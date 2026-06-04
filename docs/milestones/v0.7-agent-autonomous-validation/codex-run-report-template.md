# Codex Autonomous Validation Report Template

Chinese mirror: `codex-run-report-template.zh.md`.

Use this template to create
`validation-runs/YYYY-MM-DD-codex/codex.zh.md` after Codex completes one browser
autonomous validation run.

This is a template, not a result. Do not fill it as passing unless the commands,
browser flow, operation log parsing, and evidence bundle checks actually ran.

## 0. Conclusion

Choose exactly one:

```text
PASS_READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

Current conclusion:

```text
<one allowed conclusion>
```

Short reason:

```text
<short public reason>
```

## 1. Run Metadata

```text
run_id:
date:
operator:
branch:
commit:
working_tree_status:
WorldEngine repo:
WorldEngine branch:
WorldEngine commit:
Validation Client repo:
Validation Client branch:
Validation Client commit:
WorldEngine API base:
Validation Client API base:
Web URL:
```

## 2. Preflight Evidence

Record actual command results:

```text
git status --short --branch:
git diff --check:
WorldEngine GET /health:
WorldEngine GET /manifest:
WorldEngine GET /openapi.json:
Validation Client GET /health:
Validation Client GET /health/worldengine:
Validation Client POST /sessions/worldengine:
```

Required checks:

- [ ] WorldEngine `/manifest` is reachable.
- [ ] WorldEngine OpenAPI exposes a discoverable world creation endpoint.
- [ ] Validation Client reports `world_creation: available`.
- [ ] Validation Client can create a WorldEngine-backed session.
- [ ] No key, private prompt, provider raw trace, or Agent private state appears
      in public responses.

If any required check is missing, the conclusion must not be
`PASS_READY_FOR_HUMAN_VALIDATION`.

## 3. Commands Run

Record only commands run in the current session.

```text
cd apps/api && uv run pytest -q:
pnpm --dir apps/web test:
pnpm --dir apps/web build:
pnpm run test:
pnpm run build:
E2E command:
redaction scan:
```

## 4. Service Startup

```text
WorldEngine command:
WorldEngine PID/session:
WorldEngine port:
Validation Client API command:
Validation Client API PID/session:
Validation Client API port:
Validation Client Web command:
Validation Client Web PID/session:
Validation Client Web port:
```

Record port conflicts, restarts, failures, and fallbacks.

## 5. Browser Flow Checklist

- [ ] Open session library.
- [ ] Capture `screenshots/01-session-library.png`.
- [ ] Check WorldEngine connection status.
- [ ] Enter session name.
- [ ] Enter base worldview prompt.
- [ ] Create WorldEngine session.
- [ ] Enter runtime console.
- [ ] Capture `screenshots/03-runtime-console.png`.
- [ ] Inspect pixel canvas.
- [ ] Inspect public state summary.
- [ ] Inspect Agent public state.
- [ ] Inspect World Log.
- [ ] Inspect Agent Life Log.
- [ ] Submit high-level director guidance.
- [ ] Capture `screenshots/04-director-guidance.png`.
- [ ] Use replay slider.
- [ ] Create branch from a commit point.
- [ ] Switch branch.
- [ ] Capture `screenshots/05-replay-branch.png`.
- [ ] Open evidence panel.
- [ ] Download evidence bundle.
- [ ] Capture `screenshots/06-evidence-panel.png`.

Missing steps:

```text
<list missing steps or none>
```

## 6. Operation Log Evidence

```text
operation log path:
line count:
run_id matched:
session_id matched:
worldengine_world_id matched:
first timestamp:
last timestamp:
```

Check log coverage:

- [ ] page open.
- [ ] click.
- [ ] fill.
- [ ] submit.
- [ ] API request summary.
- [ ] API response summary.
- [ ] screenshot.
- [ ] download.
- [ ] assertion.
- [ ] visible result.

## 7. Evidence Bundle Evidence

```text
evidence bundle path:
JSON parse result:
manifest.session_id:
operation log session_id:
timeline branch ids:
event count:
diff count:
snapshot count:
api summary count:
redaction flags:
warnings:
```

Required checks:

- [ ] evidence bundle parses.
- [ ] evidence bundle matches this run/session.
- [ ] evidence bundle and operation log reference each other.
- [ ] counts match records.
- [ ] public evaluator output is not faked as PASS.
- [ ] private data scan is clean.

## 8. Screenshots

```text
screenshots/01-session-library.png:
screenshots/02-create-world.png:
screenshots/03-runtime-console.png:
screenshots/04-director-guidance.png:
screenshots/05-replay-branch.png:
screenshots/06-evidence-panel.png:
```

Missing screenshots:

```text
<list missing screenshots or none>
```

## 9. Redaction / Boundary Scan

Command:

```bash
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

Classification:

```text
allowed documentation hits:
allowed test redaction hits:
forbidden UI hits:
forbidden bundle hits:
forbidden real secret hits:
```

Any real key, private prompt, provider raw trace, or Agent private state leak
requires `FAIL`.

## 10. Known Gaps

```text
<gap id>:
severity:
evidence:
required follow-up:
```

## 11. Next Gate

If conclusion is `PASS_READY_FOR_HUMAN_VALIDATION`:

- [ ] second Agent read-only review has not started yet.
- [ ] do not claim human validation passed.
- [ ] hand this report, operation log, screenshots, evidence bundle, and API
      summary to the second Agent.

If conclusion is not `PASS_READY_FOR_HUMAN_VALIDATION`:

- [ ] do not enter second Agent review unless the review goal is blocker
      confirmation.
- [ ] do not enter human validation.
- [ ] record the package or task needed to fix the gap.
