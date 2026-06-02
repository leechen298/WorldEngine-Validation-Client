from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .models import Base


_engine = None
_SessionLocal: Optional[sessionmaker[Session]] = None


def _create_database_url(database_path: str) -> str:
    db_path = Path(database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


def init_db(database_path: Optional[str] = None) -> None:
    global _engine, _SessionLocal
    target_path = database_path or get_settings().database_path
    _engine = create_engine(_create_database_url(target_path), connect_args={"check_same_thread": False})
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    Base.metadata.create_all(bind=_engine)


def reset_db_state() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def get_sessionmaker() -> sessionmaker[Session]:
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
