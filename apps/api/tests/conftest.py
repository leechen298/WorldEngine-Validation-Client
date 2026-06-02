import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app import db
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "client.sqlite3"
    monkeypatch.setenv("WORLDENGINE_VALIDATION_DATABASE_PATH", str(db_path))
    os.environ["WORLDENGINE_API_BASE"] = os.environ.get("WORLDENGINE_API_BASE", "http://127.0.0.1:8000")

    db.reset_db_state()
    db.init_db(str(db_path))
    with TestClient(app) as c:
        yield c
