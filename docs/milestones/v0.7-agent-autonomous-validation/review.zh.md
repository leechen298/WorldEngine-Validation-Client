# v0.7 Agent Autonomous Validation Review

状态：计划完成 / WAITING_FOR_WORLDENGINE_GATE_1

## 实现授权

当前状态：仅完成 v0.7 文档规划。尚未授权 runtime、API、UI、E2E、Agent runner
或日志实现。

当前跨仓库门禁停在 WorldEngine Gate 1。WorldEngine 未写出
`WORLDENGINE_CONTRACT_READY` 前，本仓库不得进入 Validation Client v0.7 runtime
implementation、Codex 浏览器自主验证、第二 Agent 复核或人工验证。

## Task Records

### Task 1: v0.7 里程碑文档和路由

- Commit: `1652793`
- Files:
  - `AGENTS.md`
  - `AGENTS.zh.md`
  - `docs/README.zh.md`
  - `docs/roadmap.zh.md`
  - `docs/agent-guides/routing.md`
  - `docs/agent-guides/routing.zh.md`
  - `docs/agent-guides/workflow.md`
  - `docs/agent-guides/workflow.zh.md`
  - `docs/agent-guides/boundaries.md`
  - `docs/agent-guides/boundaries.zh.md`
  - `docs/agent-guides/validation-workflow.md`
  - `docs/agent-guides/validation-workflow.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/README.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/handoff-status.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/review.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md`
  - `docs/milestones/v0.7-agent-autonomous-validation/validation-runs/.gitkeep`
- Commands:
  - `git diff --check`: 通过。
  - `rg -n "TBD|TODO|implement later|fill in details" docs/milestones/v0.7-agent-autonomous-validation docs/agent-guides AGENTS.md AGENTS.zh.md --glob '!review.zh.md'`: 无命中，通过。
  - `LC_ALL=C rg -n "[^[:ascii:]]" AGENTS.md docs/agent-guides/routing.md docs/agent-guides/workflow.md docs/agent-guides/boundaries.md docs/agent-guides/validation-workflow.md docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.md docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.md docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.md docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.md docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.md docs/milestones/v0.7-agent-autonomous-validation/handoff-status.md docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.md docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.md docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.md docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.md docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.md`: 无命中，通过。
  - `rg -n "parent timeline|child timeline|parent-child ownership|父子|父级|子级|层级" AGENTS.md AGENTS.zh.md docs/agent-guides docs/milestones/v0.7-agent-autonomous-validation --glob '!review.zh.md'`: 无命中，通过。
- Scope review:
  - 文档限定 v0.7 为 Agent 自主验证、第二 Agent 复核和人工验证交接 milestone。
  - 新增跨仓库 Gate 0 到 Gate 5 的不可跳关矩阵。
  - 明确当前唯一允许的下一步是 WorldEngine Gate 1：实现 public handoff
    manifest 和 world creation contract，并写出 `WORLDENGINE_CONTRACT_READY`。
  - 不授权客户端管理 LLM key，不直接调用 provider，不生成权威 evaluator PASS。
  - 不授权 Validation Client runtime / API / UI / E2E / Agent runner / operation
    log 实现。
  - branch 相关说明统一为命名、切换、回放和继续推进，不使用 parent/child
    timeline 语义。
- Notes:
  - `docs/milestones/v0.7-agent-autonomous-validation/validation-runs/2026-06-04-codex-preflight.zh.md`
    是单独预检记录，不纳入 Task 1 文档规划提交。

## 结论

当前 v0.7 仅达到文档计划就绪。Validation Client v0.7 runtime implementation 仍
等待 WorldEngine Gate 1 contract readiness。

## Gate 1 Preflight Records

### 2026-06-04 Codex 自主验证预检

- Commit: `b38df21`
- File:
  - `docs/milestones/v0.7-agent-autonomous-validation/validation-runs/2026-06-04-codex-preflight.zh.md`
- Commands:
  - `git diff --check`: 通过。
  - `pnpm run test`: Web 测试通过，API 阶段被沙箱阻止访问 `~/.cache/uv`，命令以
    exit code 2 结束。
  - `uv run --project apps/api pytest -q`: 提升权限后通过，48 passed, 1 warning。
  - `pnpm run build`: 通过。
- Conclusion:
  - `BLOCKED / WAITING_FOR_WORLDENGINE_GATE_1`
  - 基础 Web/API 测试和 Web build 通过。
  - 完整 v0.7 Codex 自主验证仍被 WorldEngine Gate 1 阻塞。

### 2026-06-04 WorldEngine Gate 1 解除记录

- WorldEngine Commit: `b10061c`
- Gate result: `WORLDENGINE_CONTRACT_READY`
- Public contract evidence:
  - WorldEngine `GET /manifest` 可用。
  - WorldEngine OpenAPI 暴露 `POST /worlds`。
  - WorldEngine `POST /worlds` 返回 public `world_id`、`status`、
    `public_initial_state` 和 `visualization`。
  - WorldEngine public director guidance endpoint 可用。
  - Validation Client `/health/worldengine` 可识别 `world_creation: available`。
  - Validation Client `POST /sessions/worldengine` 已通过兼容性探针创建
    WorldEngine-backed session。
- Commands:
  - WorldEngine focused tests:
    `PYTHONPATH=backend uv run --with-requirements backend/requirements.txt --no-project pytest backend/app/tests/test_world_generation_schema.py backend/app/tests/test_public_handoff_contract_api.py backend/app/tests/test_generation_core_readiness_api.py -q`：
    20 passed, 1 warning。
  - Validation Client compatibility probe:
    `GET /health/worldengine`：200。
  - Validation Client compatibility probe:
    `POST /sessions/worldengine`：201。
- Decision:
  - Gate 1 no longer blocks Validation Client v0.7 implementation.
  - Current user authorization allows proceeding through implementation gates
    until the repository reaches the Codex autonomous validation handoff state.

## Implementation Records

### Task 2 / 2.5 / 3: validation run, operation log, and evidence association

- Commit: pending in current step.
- Files:
  - `apps/api/app/main.py`
  - `apps/api/app/models.py`
  - `apps/api/app/routes/evidence.py`
  - `apps/api/app/routes/validation_runs.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_evidence.py`
  - `apps/api/tests/test_validation_runs.py`
- Implementation:
  - Added `ValidationRun` records for Codex / Agent browser validation runs.
  - Added `OperationLogEntry` records with timestamp, run id, actor, phase, URL,
    action, target, input text, request method/path, response status/summary,
    visible result, screenshot path, downloaded file, and notes.
  - Added `/validation-runs`, `/validation-runs/{run_id}/operation-log`,
    `/validation-runs/{run_id}/operation-log.jsonl`,
    `/validation-runs/{run_id}/api-summary`, and
    `/validation-runs/{run_id}/api-summary/download`.
  - Upgraded evidence bundle schema to `0.7.0`.
  - Added latest validation run id, evidence bundle filename, validation run
    counts, operation-log counts, validation run records, and operation-log
    records to evidence bundle output.
  - Reused existing event/diff/snapshot/commit-point/branch storage; no reverse
    event inference was introduced.
- Boundary review:
  - The client still does not manage LLM keys.
  - The client still does not call LLM providers directly.
  - The client still does not import WorldEngine source code.
  - Operation logs reject private prompt, provider secret, raw provider trace,
    API key, token, password, Agent private memory, private goal, self_state,
    hidden context, and private source-path markers.
  - API summary uses public trace summaries only and does not export request
    prompt content.
- Commands:
  - `cd apps/api && uv run pytest tests/test_evidence.py tests/test_validation_runs.py tests/test_sessions.py tests/test_health.py -q`:
    46 passed, 1 warning.
  - `git diff --check`: passed.
- Result:
  - Task 2 complete.
  - Task 2.5 remains satisfied by the existing event/diff/snapshot/commit-point
    storage plus the new v0.7 evidence association fields.
  - Task 3 complete for backend evidence/API summary association.

### Task 4: Web UI operation-log hooks

- Commit: pending in current step.
- Files:
  - `apps/web/src/api/client.ts`
  - `apps/web/src/api/types.ts`
  - `apps/web/src/pages/RuntimeConsole.tsx`
  - `apps/web/src/pages/SessionLibrary.tsx`
  - `apps/web/src/store/sessionStore.ts`
  - `apps/web/src/__tests__/RuntimeConsole.test.tsx`
  - `apps/web/src/__tests__/SessionLibrary.test.tsx`
- Implementation:
  - Added frontend types and API client methods for validation runs,
    operation-log entries, and API summaries.
  - Added `ensureValidationRun(sessionId)` and `logOperation(sessionId, payload)`
    to the session store.
  - Automatically creates a validation run for newly created WorldEngine
    sessions and existing sessions opened from the session library.
  - Records session creation, health status display, runtime view load, replay
    view load, branch list load, commit-point load, director intent load,
    director guidance submit, branch creation, evidence manifest load, and
    evidence bundle download.
  - Records UI-only actions for runtime console open, Run, Pause, Single Tick,
    replay slider change, commit-point selection, branch selection, and opening
    an existing session.
  - Operation-log write failures are intentionally non-blocking and do not
    interrupt the client workflow.
- Boundary review:
  - Frontend does not manage LLM keys.
  - Frontend does not call LLM providers.
  - Frontend operation logs use public user input, public API paths, public
    response summaries, visible UI result text, screenshot path placeholders,
    and downloaded evidence filenames.
  - Logs do not claim evaluator PASS or human PASS.
- Commands:
  - `pnpm --dir apps/web test`: 25 passed.
  - `pnpm --dir apps/web build`: passed.
- Notes:
  - Vitest emits existing React `act(...)` warnings from async store updates in
    `RuntimeConsole` tests. The warnings did not fail the test run.
- Result:
  - Task 4 complete.
