import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    return datetime.now(UTC)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="created")
    worldengine_world_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    public_world_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    initial_state_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visualization_payload_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now, onupdate=_now)

    commit_points: Mapped[list["CommitPoint"]] = relationship("CommitPoint", back_populates="session")
    branches: Mapped[list["TimelineBranch"]] = relationship("TimelineBranch", back_populates="session")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="session")
    state_diffs: Mapped[list["StateDiff"]] = relationship("StateDiff", back_populates="session")
    snapshots: Mapped[list["Snapshot"]] = relationship("Snapshot", back_populates="session")
    director_intents: Mapped[list["DirectorIntent"]] = relationship("DirectorIntent", back_populates="session")
    api_traces: Mapped[list["ApiTrace"]] = relationship("ApiTrace", back_populates="session")
    validation_runs: Mapped[list["ValidationRun"]] = relationship("ValidationRun", back_populates="session")


class CommitPoint(Base):
    __tablename__ = "commit_points"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    tick: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    event_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    snapshot_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="commit_points")
    branches: Mapped[list["TimelineBranch"]] = relationship("TimelineBranch", back_populates="commit_point")


class TimelineBranch(Base):
    __tablename__ = "timeline_branches"
    __table_args__ = (UniqueConstraint("session_id", "branch_name", name="uq_timeline_branch_session_name"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    branch_name: Mapped[str] = mapped_column(String, nullable=False)
    commit_point_id: Mapped[str] = mapped_column(String, ForeignKey("commit_points.id"), nullable=False)
    tick: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_reference: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_main: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="branches")
    commit_point: Mapped["CommitPoint"] = relationship("CommitPoint", back_populates="branches")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="branch")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    branch_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("timeline_branches.id"), nullable=True)
    tick: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    event_kind: Mapped[str] = mapped_column(String, nullable=False, default="world_event")
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="events")
    branch: Mapped[Optional["TimelineBranch"]] = relationship("TimelineBranch", back_populates="events")


class StateDiff(Base):
    __tablename__ = "state_diffs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    branch_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("timeline_branches.id"), nullable=True)
    tick: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    diff_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="state_diffs")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    branch_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("timeline_branches.id"), nullable=True)
    tick: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="snapshots")


class DirectorIntent(Base):
    __tablename__ = "director_intents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    branch_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("timeline_branches.id"), nullable=True)
    tick: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    instruction_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    public_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    applied_event_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="director_intents")


class ApiTrace(Base):
    __tablename__ = "api_traces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    method: Mapped[str] = mapped_column(String, nullable=False)
    url_path: Mapped[str] = mapped_column(String, nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    request_summary_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    response_summary_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_keys_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    private_worldengine_internals_included: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="api_traces")


class ValidationRun(Base):
    __tablename__ = "validation_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    actor: Mapped[str] = mapped_column(String, nullable=False, default="codex")
    status: Mapped[str] = mapped_column(String, nullable=False, default="running")
    web_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    api_base_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    worldengine_api_base: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    evidence_bundle_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now, onupdate=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="validation_runs")
    operation_logs: Mapped[list["OperationLogEntry"]] = relationship("OperationLogEntry", back_populates="validation_run")


class OperationLogEntry(Base):
    __tablename__ = "operation_log_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String, ForeignKey("validation_runs.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    actor: Mapped[str] = mapped_column(String, nullable=False, default="codex")
    phase: Mapped[str] = mapped_column(String, nullable=False, default="browser")
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    target_label: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    input_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_method: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    request_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visible_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    downloaded_file: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_now)

    validation_run: Mapped["ValidationRun"] = relationship("ValidationRun", back_populates="operation_logs")
