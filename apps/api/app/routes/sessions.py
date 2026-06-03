import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ApiTrace, CommitPoint, DirectorIntent, Event, Session as DbSession, Snapshot, StateDiff, TimelineBranch
from ..schemas import (
    BranchResponse,
    BranchCreatePayload,
    DirectorIntentCreatePayload,
    DirectorIntentListResponse,
    DirectorIntentResponse,
    EventResponse,
    PublicAgentState,
    ReplayViewResponse,
    RuntimeLogItem,
    RuntimeViewResponse,
    SessionCreatePayload,
    SessionListResponse,
    SessionSummary,
    WorldEngineSessionCreatePayload,
)
from ..worldengine_client import create_world_via_public_api

router = APIRouter(prefix="/sessions")

PRIVATE_PAYLOAD_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "file_path",
    "goal",
    "helper",
    "internal",
    "key",
    "memory",
    "oracle",
    "password",
    "path",
    "private",
    "prompt",
    "provider",
    "secret",
    "source_path",
    "thought",
    "token",
)

PUBLIC_AGENT_FIELDS = {"agent_id", "id", "display_name", "name", "location", "public_status", "visible_action"}
VISUALIZATION_TILE_FIELDS = {"x", "y", "terrain", "sprite", "variant", "color"}
VISUALIZATION_ENTITY_FIELDS = {"id", "x", "y", "sprite", "label", "kind", "public_status"}
LOG_PAYLOAD_FIELDS = {"text", "summary", "description", "agent_id", "x", "y", "severity"}


def _session_summary(db_session: DbSession, branch_count: int, main_branch: TimelineBranch | None) -> SessionSummary:
    return SessionSummary(
        id=db_session.id,
        session_name=db_session.session_name,
        status=db_session.status,
        worldengine_world_id=db_session.worldengine_world_id,
        public_world_status=db_session.public_world_status,
        initial_state_summary=db_session.initial_state_summary,
        visualization_payload_summary=db_session.visualization_payload_summary,
        branch_count=branch_count,
        main_branch_id=main_branch.id if main_branch else None,
        main_commit_point_id=main_branch.commit_point_id if main_branch else None,
        created_at=db_session.created_at,
        updated_at=db_session.updated_at,
    )


def _director_intent_response(intent: DirectorIntent) -> DirectorIntentResponse:
    return DirectorIntentResponse(
        id=intent.id,
        session_id=intent.session_id,
        branch_id=intent.branch_id,
        tick=intent.tick,
        instruction_text=intent.instruction_text,
        status=intent.status,
        public_explanation=intent.public_explanation,
        applied_event_id=intent.applied_event_id,
        error_message=intent.error_message,
        created_at=intent.created_at,
    )


def _load_json_object(raw_value: str | None) -> dict[str, Any]:
    if not raw_value:
        return {}
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _public_payload(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            lowered_key = str(key).lower()
            if any(part in lowered_key for part in PRIVATE_PAYLOAD_KEY_PARTS):
                continue
            result[key] = _public_payload(item)
        return result
    if isinstance(value, list):
        return [_public_payload(item) for item in value]
    return value


def _allowlisted_dict(raw_value: Any, allowed_fields: set[str]) -> dict[str, Any]:
    if not isinstance(raw_value, dict):
        return {}
    return {
        key: _public_payload(value)
        for key, value in raw_value.items()
        if key in allowed_fields and not any(part in key.lower() for part in PRIVATE_PAYLOAD_KEY_PARTS)
    }


def _public_visualization(snapshot_payload: dict[str, Any]) -> dict[str, Any]:
    raw_visualization = snapshot_payload.get("visualization")
    if not isinstance(raw_visualization, dict):
        return {}
    result: dict[str, Any] = {}
    raw_tiles = raw_visualization.get("tiles")
    if isinstance(raw_tiles, list):
        result["tiles"] = [_allowlisted_dict(item, VISUALIZATION_TILE_FIELDS) for item in raw_tiles if isinstance(item, dict)]
    raw_entities = raw_visualization.get("entities")
    if isinstance(raw_entities, list):
        result["entities"] = [
            _allowlisted_dict(item, VISUALIZATION_ENTITY_FIELDS) for item in raw_entities if isinstance(item, dict)
        ]
    return result


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


def _public_agents(snapshot_payload: dict[str, Any]) -> list[PublicAgentState]:
    initial_state = snapshot_payload.get("initial_state") if isinstance(snapshot_payload.get("initial_state"), dict) else {}
    raw_agents = snapshot_payload.get("public_agents") or initial_state.get("public_agents") or initial_state.get("agents") or []
    if not isinstance(raw_agents, list):
        return []

    agents = []
    for raw_agent in raw_agents:
        if not isinstance(raw_agent, dict):
            continue
        safe_agent = _allowlisted_dict(raw_agent, PUBLIC_AGENT_FIELDS)
        agent_id = safe_agent.get("agent_id") or safe_agent.get("id")
        if not agent_id:
            continue
        extra_payload = {key: value for key, value in safe_agent.items() if key not in PUBLIC_AGENT_FIELDS}
        agents.append(
            PublicAgentState(
                agent_id=str(agent_id),
                display_name=_string_or_none(safe_agent.get("display_name") or safe_agent.get("name")),
                location=_string_or_none(safe_agent.get("location")),
                public_status=_string_or_none(safe_agent.get("public_status")),
                visible_action=_string_or_none(safe_agent.get("visible_action")),
                payload=extra_payload,
            )
        )
    return agents


def _runtime_log_item(event: Event) -> RuntimeLogItem:
    payload = _allowlisted_dict(_load_json_object(event.payload_json), LOG_PAYLOAD_FIELDS)
    text = payload.get("text") or payload.get("summary") or payload.get("description") or event.event_kind
    agent_id = payload.get("agent_id")
    return RuntimeLogItem(
        id=event.id,
        tick=event.tick,
        event_kind=event.event_kind,
        text=str(text),
        agent_id=str(agent_id) if agent_id is not None else None,
        payload=payload,
        created_at=event.created_at,
    )


def _merge_public_patch(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    public_patch = _public_payload(patch)
    for key, value in public_patch.items():
        if any(part in key.lower() for part in PRIVATE_PAYLOAD_KEY_PARTS):
            continue
        if isinstance(base.get(key), dict) and isinstance(value, dict):
            base[key] = _merge_public_patch(dict(base[key]), value)
        else:
            base[key] = value
    return base


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SessionSummary)
def create_session(payload: SessionCreatePayload, db: Session = Depends(get_db)):
    db_session = DbSession(session_name=payload.session_name)
    db.add(db_session)
    db.flush()

    first_commit = CommitPoint(session_id=db_session.id, tick=0, payload_json="{}")
    db.add(first_commit)
    db.flush()

    main_branch = TimelineBranch(
        session_id=db_session.id,
        branch_name="main",
        commit_point_id=first_commit.id,
        tick=0,
        snapshot_reference=None,
        is_main=True,
    )
    db.add(main_branch)
    db.commit()
    db.refresh(db_session)
    db.refresh(main_branch)

    return _session_summary(db_session, 1, main_branch)


@router.post("/worldengine", status_code=status.HTTP_201_CREATED, response_model=SessionSummary)
async def create_worldengine_session(payload: WorldEngineSessionCreatePayload, db: Session = Depends(get_db)):
    try:
        world_data = await create_world_via_public_api(payload.world_prompt)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    db_session = DbSession(
        session_name=payload.session_name,
        worldengine_world_id=world_data["world_id"],
        public_world_status=world_data["status"],
        initial_state_summary=world_data["initial_state_summary"],
        visualization_payload_summary=world_data["visualization_payload_summary"],
    )
    db.add(db_session)
    db.flush()

    snapshot = Snapshot(session_id=db_session.id, tick=0, snapshot_json=world_data["snapshot_json"])
    db.add(snapshot)
    db.flush()

    first_commit = CommitPoint(
        session_id=db_session.id,
        tick=0,
        snapshot_id=snapshot.id,
        payload_json=world_data["event_payload_json"],
    )
    db.add(first_commit)
    db.flush()

    main_branch = TimelineBranch(
        session_id=db_session.id,
        branch_name="main",
        commit_point_id=first_commit.id,
        tick=0,
        snapshot_reference=snapshot.id,
        is_main=True,
    )
    db.add(main_branch)
    db.flush()
    snapshot.branch_id = main_branch.id

    event = Event(
        session_id=db_session.id,
        branch_id=main_branch.id,
        tick=0,
        event_kind="world_created",
        payload_json=world_data["event_payload_json"],
    )
    db.add(event)
    db.flush()
    first_commit.event_id = event.id

    trace_payload = world_data["api_trace"]
    trace = ApiTrace(
        session_id=db_session.id,
        method=trace_payload["method"],
        url_path=trace_payload["url_path"],
        status_code=trace_payload["status_code"],
        request_summary_json=trace_payload["request_summary_json"],
        response_summary_json=trace_payload["response_summary_json"],
        error_message=trace_payload["error_message"],
        llm_keys_included=False,
        private_worldengine_internals_included=False,
    )
    db.add(trace)
    db.commit()
    db.refresh(db_session)
    db.refresh(main_branch)

    return _session_summary(db_session, 1, main_branch)


@router.get("", response_model=SessionListResponse)
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.execute(select(DbSession).order_by(DbSession.created_at.desc())).scalars().all()
    result = []
    for item in sessions:
        main_branch = (
            db.execute(
                select(TimelineBranch)
                .where(TimelineBranch.session_id == item.id, TimelineBranch.is_main.is_(True))
                .order_by(TimelineBranch.created_at.asc())
                .limit(1)
            )
            .scalars()
            .first()
        )
        branch_count = (
            db.execute(select(func.count(TimelineBranch.id)).where(TimelineBranch.session_id == item.id)).scalar() or 0
        )

        result.append(
            _session_summary(item, int(branch_count), main_branch)
        )

    return SessionListResponse(sessions=result)


@router.post("/{session_id}/director-intents", response_model=DirectorIntentResponse, status_code=status.HTTP_201_CREATED)
def create_director_intent(
    session_id: str,
    payload: DirectorIntentCreatePayload,
    db: Session = Depends(get_db),
):
    db_session = db.get(DbSession, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if payload.branch_id:
        branch = (
            db.execute(
                select(TimelineBranch).where(
                    TimelineBranch.id == payload.branch_id,
                    TimelineBranch.session_id == session_id,
                )
            )
            .scalars()
            .first()
        )
        if not branch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

    intent = DirectorIntent(
        session_id=session_id,
        branch_id=payload.branch_id,
        tick=payload.tick,
        instruction_text=payload.instruction_text,
        status="pending",
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)

    return _director_intent_response(intent)


@router.get("/{session_id}/director-intents", response_model=DirectorIntentListResponse)
def list_director_intents(session_id: str, db: Session = Depends(get_db)):
    db_session = db.get(DbSession, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    intents = (
        db.execute(
            select(DirectorIntent)
            .where(DirectorIntent.session_id == session_id)
            .order_by(DirectorIntent.created_at.desc(), DirectorIntent.id.desc())
        )
        .scalars()
        .all()
    )

    return DirectorIntentListResponse(
        session_id=session_id,
        director_intents=[_director_intent_response(intent) for intent in intents],
    )


@router.post("/{session_id}/branches", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(session_id: str, payload: BranchCreatePayload, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    commit_point = db.get(CommitPoint, payload.commit_point_id)
    if not commit_point or commit_point.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commit point not found")

    existing_branch = (
        db.execute(
            select(TimelineBranch).where(
                TimelineBranch.session_id == session_id,
                TimelineBranch.branch_name == payload.branch_name,
            )
        )
        .scalars()
        .first()
    )
    if existing_branch:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Branch name already exists")

    branch = TimelineBranch(
        session_id=session_id,
        branch_name=payload.branch_name,
        commit_point_id=payload.commit_point_id,
        tick=commit_point.tick,
        snapshot_reference=commit_point.snapshot_id,
        is_main=False,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return BranchResponse(
        id=branch.id,
        branch_name=branch.branch_name,
        commit_point_id=branch.commit_point_id,
        tick=branch.tick,
        current_tick=branch.tick,
        snapshot_reference=branch.snapshot_reference,
        is_main=branch.is_main,
        created_at=branch.created_at,
    )


@router.get("/{session_id}/runtime-view", response_model=RuntimeViewResponse)
def get_runtime_view(session_id: str, db: Session = Depends(get_db)):
    db_session = db.get(DbSession, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    main_branch = (
        db.execute(
            select(TimelineBranch)
            .where(TimelineBranch.session_id == session_id, TimelineBranch.is_main.is_(True))
            .order_by(TimelineBranch.created_at.asc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    branch_id = main_branch.id if main_branch else None
    snapshot_query = select(Snapshot).where(Snapshot.session_id == session_id)
    if branch_id:
        snapshot_query = snapshot_query.where(Snapshot.branch_id == branch_id)
    else:
        snapshot_query = snapshot_query.where(Snapshot.id.is_(None))
    snapshot = (
        db.execute(
            snapshot_query.order_by(Snapshot.tick.desc(), Snapshot.created_at.desc()).limit(1)
        )
        .scalars()
        .first()
    )
    event_query = select(Event).where(Event.session_id == session_id)
    if branch_id:
        event_query = event_query.where(Event.branch_id == branch_id)
    else:
        event_query = event_query.where(Event.id.is_(None))
    events = (
        db.execute(
            event_query.order_by(Event.tick.asc(), Event.created_at.asc())
        )
        .scalars()
        .all()
    )
    snapshot_payload = _load_json_object(snapshot.snapshot_json if snapshot else None)
    visualization = _public_visualization(snapshot_payload)
    log_items = [_runtime_log_item(event) for event in events]
    agent_life_log = [
        item for item in log_items if item.agent_id is not None or item.event_kind.lower().startswith("agent_")
    ]
    world_log = [item for item in log_items if item not in agent_life_log]
    event_ticks = [event.tick for event in events]
    tick = max([snapshot.tick if snapshot else 0, *event_ticks])

    return RuntimeViewResponse(
        session_id=db_session.id,
        worldengine_world_id=db_session.worldengine_world_id,
        world_status=db_session.public_world_status or db_session.status,
        tick=tick,
        visualization=visualization if isinstance(visualization, dict) else {},
        public_agents=_public_agents(snapshot_payload),
        world_log=world_log,
        agent_life_log=agent_life_log,
        latest_event=log_items[-1] if log_items else None,
    )


@router.get("/{session_id}/replay-view", response_model=ReplayViewResponse)
def get_replay_view(
    session_id: str,
    branch_id: str | None = Query(default=None),
    tick: int | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
):
    db_session = db.get(DbSession, session_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    branch_query = select(TimelineBranch).where(TimelineBranch.session_id == session_id)
    if branch_id:
        branch_query = branch_query.where(TimelineBranch.id == branch_id)
    else:
        branch_query = branch_query.where(TimelineBranch.is_main.is_(True)).order_by(TimelineBranch.created_at.asc())
    branch = db.execute(branch_query.limit(1)).scalars().first()
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")

    target_tick = tick if tick is not None else branch.tick
    snapshot = (
        db.execute(
            select(Snapshot)
            .where(Snapshot.session_id == session_id, Snapshot.branch_id == branch.id, Snapshot.tick <= target_tick)
            .order_by(Snapshot.tick.desc(), Snapshot.created_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    if not snapshot:
        referenced_snapshot_id = branch.snapshot_reference
        if not referenced_snapshot_id:
            branch_commit_point = db.get(CommitPoint, branch.commit_point_id)
            referenced_snapshot_id = branch_commit_point.snapshot_id if branch_commit_point else None
        if referenced_snapshot_id:
            snapshot = (
                db.execute(
                    select(Snapshot).where(
                        Snapshot.session_id == session_id,
                        Snapshot.id == referenced_snapshot_id,
                        Snapshot.tick <= target_tick,
                    )
                )
                .scalars()
                .first()
            )
    if not snapshot:
        raise HTTPException(
            status_code=422,
            detail="No replay snapshot is available at or before the requested tick",
        )

    replay_payload = _load_json_object(snapshot.snapshot_json)
    diffs = (
        db.execute(
            select(StateDiff)
            .where(
                StateDiff.session_id == session_id,
                StateDiff.branch_id == branch.id,
                StateDiff.tick > snapshot.tick,
                StateDiff.tick <= target_tick,
            )
            .order_by(StateDiff.tick.asc(), StateDiff.created_at.asc())
        )
        .scalars()
        .all()
    )
    for diff in diffs:
        replay_payload = _merge_public_patch(replay_payload, _load_json_object(diff.diff_json))

    events = (
        db.execute(
            select(Event)
            .where(Event.session_id == session_id, Event.branch_id == branch.id, Event.tick <= target_tick)
            .order_by(Event.tick.asc(), Event.created_at.asc())
        )
        .scalars()
        .all()
    )
    log_items = [_runtime_log_item(event) for event in events]
    agent_life_log = [
        item for item in log_items if item.agent_id is not None or item.event_kind.lower().startswith("agent_")
    ]
    world_log = [item for item in log_items if item not in agent_life_log]

    return ReplayViewResponse(
        session_id=db_session.id,
        branch_id=branch.id,
        snapshot_id=snapshot.id,
        worldengine_world_id=db_session.worldengine_world_id,
        world_status=db_session.public_world_status or db_session.status,
        tick=target_tick,
        visualization=_public_visualization(replay_payload),
        public_agents=_public_agents(replay_payload),
        world_log=world_log,
        agent_life_log=agent_life_log,
        latest_event=log_items[-1] if log_items else None,
    )


@router.get("/{session_id}/events", response_model=list[EventResponse])
def list_session_events(session_id: str, db: Session = Depends(get_db)):
    session = db.get(DbSession, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    events = db.execute(
        select(Event).where(Event.session_id == session_id).order_by(Event.created_at.asc())
    ).scalars().all()
    return events
