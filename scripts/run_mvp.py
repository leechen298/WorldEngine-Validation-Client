from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import List, Optional


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_health(base_url: str, timeout_seconds: float = 20.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("WorldEngine did not become healthy")


def _run(command: List[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        check=True,
        capture_output=True,
    )


def _default_worldengine_root(repo_root: Path) -> Path:
    return (repo_root.parent / "WorldEnginProjects" / "WorldEngine").resolve()


def run(args: argparse.Namespace) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    worldengine_root = (
        args.worldengine_root.resolve()
        if args.worldengine_root
        else _default_worldengine_root(repo_root)
    )
    backend_root = worldengine_root / "backend"
    backend_python = backend_root / ".venv" / "bin" / "python"
    if not backend_python.is_file():
        raise RuntimeError(f"Missing WorldEngine Python environment: {backend_python}")
    godot = shutil.which(args.godot)
    if not godot:
        raise RuntimeError(f"Godot command is unavailable: {args.godot}")

    port = args.port or _free_port()
    base_url = f"http://127.0.0.1:{port}"
    output_root = (repo_root / "validation-runs").resolve()
    registry = (repo_root / ".validation-state" / "consumed-run-ids.json").resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    registry.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        prefix="worldengine-mvp-",
        suffix=".log",
        delete=False,
    ) as log:
        log_path = Path(log.name)
    with log_path.open("wb") as log_stream:
        server = subprocess.Popen(
            [
                str(backend_python),
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=backend_root,
            stdout=log_stream,
            stderr=subprocess.STDOUT,
        )
    run_dir: Optional[Path] = None
    try:
        _wait_for_health(base_url)
        prepared = _run(
            [
                "uv",
                "run",
                "--project",
                "checkers/mvp",
                "worldengine-mvp-checker",
                "prepare",
                "--output-root",
                str(output_root),
                "--base-url",
                base_url,
                "--registry",
                str(registry),
            ],
            repo_root,
        )
        run_dir = Path(prepared.stdout.strip()).resolve()
        shutil.copy2(log_path, run_dir / "worldengine-server.log")

        try:
            godot_result = subprocess.run(
                [
                    godot,
                    "--windowed",
                    "--resolution",
                    "960x540",
                    "--path",
                    str(repo_root / "executors/godot"),
                    "--",
                    "--challenge",
                    str(run_dir / "challenge.json"),
                    "--auto-run",
                ],
                cwd=repo_root,
                text=True,
                capture_output=True,
                timeout=args.godot_timeout,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr
            (run_dir / "godot-console.log").write_text(
                (stdout or "") + (stderr or ""),
                encoding="utf-8",
            )
            raise RuntimeError(
                f"Godot executor timed out after {args.godot_timeout}s; "
                f"see {run_dir / 'godot-console.log'}"
            ) from exc
        (run_dir / "godot-console.log").write_text(
            godot_result.stdout + godot_result.stderr,
            encoding="utf-8",
        )
        if godot_result.returncode != 0:
            raise RuntimeError(
                f"Godot executor failed with {godot_result.returncode}; "
                f"see {run_dir / 'godot-console.log'}"
            )

        checker_result = subprocess.run(
            [
                "uv",
                "run",
                "--project",
                "checkers/mvp",
                "worldengine-mvp-checker",
                "verify",
                "--run-dir",
                str(run_dir),
                "--registry",
                str(registry),
            ],
            cwd=repo_root,
            text=True,
            capture_output=True,
        )
        (run_dir / "checker-console.log").write_text(
            checker_result.stdout + checker_result.stderr,
            encoding="utf-8",
        )
        if checker_result.returncode != 0:
            raise RuntimeError(
                f"Independent checker failed; see {run_dir / 'checker-console.log'}"
            )
        verdict = json.loads((run_dir / "checker/verdict.json").read_text())
        print(
            json.dumps(
                {
                    "status": verdict["status"],
                    "run_id": verdict["run_id"],
                    "session_id": verdict["session_id"],
                    "run_dir": str(run_dir),
                    "input_seal_sha256": verdict["input_seal_sha256"],
                },
                sort_keys=True,
            )
        )
        return run_dir
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
        if run_dir is not None:
            shutil.copy2(log_path, run_dir / "worldengine-server.log")
        log_path.unlink(missing_ok=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the WorldEngine Godot MVP")
    parser.add_argument("--worldengine-root", type=Path)
    parser.add_argument("--godot", default="godot")
    parser.add_argument("--godot-timeout", type=float, default=90.0)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        run(args)
        return 0
    except Exception as exc:
        print(f"MVP run failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
