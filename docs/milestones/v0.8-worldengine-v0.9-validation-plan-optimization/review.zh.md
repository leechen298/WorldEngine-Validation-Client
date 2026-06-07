# v0.8 WorldEngine v0.9 Validation Plan Optimization Review

英文镜像：`review.md`。

状态：文档自审通过 / 实现已授权
implementation_authorized: yes
provider_live_call_authorized: no
checker_execution_authorized: conditional
external_validation_authorized: no

## 授权

用户已授权：创建 v0.8 文档并完成自审后，继续进入实现；中间除非遇到无法自行决策的门禁，否则推进到待验证状态。

## Task Records

### Task 1: v0.8 文档、路由和自审

- Commit: pending
- Files:
  - `AGENTS.md`
  - `AGENTS.zh.md`
  - `docs/README.zh.md`
  - `docs/roadmap.zh.md`
  - `docs/agent-guides/routing.md`
  - `docs/agent-guides/routing.zh.md`
  - `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/`
- Commands:
  - `git diff --check`: 通过，exit 0，无输出。
  - `python3 -c "from pathlib import Path; root=Path('docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization'); required=['README','intent','contract','technical-design','test-plan','plan','implementation-task-plan','scenario-operation-matrix','artifact-contract','redaction-matrix','autonomous-validation-runbook','second-agent-review-template','cross-repo-validation-gate-matrix','planning-readiness-checklist','handoff-status','next-chat-quickstart','handoff-prompts','validation','codex-run-report-template','agent-review-template','human-validation-template','review']; missing=[]; [missing.append(f'{base}.md') for base in required if not (root/f'{base}.md').exists()]; [missing.append(f'{base}.zh.md') for base in required if not (root/f'{base}.zh.md').exists()]; print({'files': len(list(root.glob('*.md'))), 'missing': missing, 'gitkeep': (root/'validation-runs/.gitkeep').exists()}); raise SystemExit(1 if missing or not (root/'validation-runs/.gitkeep').exists() else 0)"`: 通过，`{'files': 44, 'missing': [], 'gitkeep': True}`。
  - `rg -n "TBD|TODO|implement later|fill in details" docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization docs/README.zh.md docs/roadmap.zh.md docs/agent-guides/routing.md docs/agent-guides/routing.zh.md AGENTS.md AGENTS.zh.md --glob '!plan.zh.md' --glob '!test-plan.zh.md' --glob '!review.zh.md'`: 无命中，exit 1，按 `rg` 语义表示未发现占位符。
- Scope review:
  - v0.8 被定义为可重复的 WorldEngine v0.9 验证计划优化迭代。
  - 文档包覆盖 scenario matrix、artifact contract、redaction matrix、gate matrix、runbook、Codex/Agent/human 模板和 handoff。
  - 路由和 AGENTS active milestone 已指向 v0.8。
  - 客户端边界仍是 `display_export_only`；不拥有 provider、evaluator、PASS 判定或权威世界状态。
  - UI smoke、API tests、bundle export 成功不得写成 WorldEngine validation PASS。
- Notes:
  - WorldEngine 侧 `0.9.11` handoff 当前是文档草案，本仓库只读消费，不修改 WorldEngine。
  - 当前工作树存在 v0.7 validation artifacts 既有脏文件；本任务不纳入这些文件。
  - 原始占位符扫描不排除文件时只命中文档中记录的扫描命令文本；review 采用排除 `plan.zh.md`、`test-plan.zh.md`、`review.zh.md` 后的实际内容扫描。

## 当前结论

Task 1 文档自审通过并已提交。按用户授权，已进入实现。

### Task 2: WorldEngine v0.9 public surface discovery

- Commit: pending
- Files:
  - `apps/api/app/schemas.py`
  - `apps/api/app/worldengine_client.py`
  - `apps/api/tests/test_health.py`
  - `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/review.zh.md`
- Implementation:
  - 在 `/health/worldengine` response model 中保留 `v0_9_validation` 和 `v0_9_public_surfaces`。
  - 在 WorldEngine OpenAPI summary 中输出 v0.9 public surface map。
  - 识别 provider live smoke、worldview generation、world creation、runtime controls、events、snapshots、params、direction、director guidance、event legality、Agent continuity、narrative projection 和 diagnostic dialogue 等 public surfaces。
  - OpenAPI 不可用时标记 `not_run`；OpenAPI 可用但 surface 缺失时标记 `blocked`；可发现时标记 `available`。
  - 过滤 `/internal`、`/private`、helper 类 endpoint，不把 provider/private 字段写入 discovery summary。
- Commands:
  - RED: `cd apps/api && uv run pytest tests/test_health.py tests/test_sessions.py -q`: 失败，2 failed，新增测试缺少 `v0_9_validation` 字段。
  - GREEN: `cd apps/api && uv run pytest tests/test_health.py tests/test_sessions.py -q`: 36 passed, 1 warning。
  - `git diff --check`: 通过，exit 0，无输出。
- Scope review:
  - 仅扩展 public discovery 和 schema，不调用 provider，不访问 WorldEngine 私有源码或 helper。
  - v0.9 readiness 只表达 public surface discovery 状态，不声明 provider live PASS 或 WorldEngine validation PASS。
  - 既有 v0.7 Playwright artifacts 仍未纳入本任务。
- Notes:
  - GREEN 测试 warning 为既有 `StarletteDeprecationWarning`。

Task 2 已通过 focused verification 并已提交。

### Task 3: Scenario-aware evidence manifest 和 artifact index

- Commit: pending
- Files:
  - `apps/api/app/routes/evidence.py`
  - `apps/api/app/schemas.py`
  - `apps/api/tests/test_evidence.py`
  - `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/review.zh.md`
- Implementation:
  - 保留旧 `bundle_schema_version=0.7.0`，新增 v0.8 `schema_version=0.8.0`、`bundle_id`、`scenario`、`result_status`、`client_role`、`provider_owner`、`evaluator_role`。
  - 增加 scenario-aware `artifact_index`，记录 artifact name、bundle-relative path、required/displayable/exportable、producer、schema version、status 和 redaction status。
  - 增加 `checker_contract`、`unsupported_items` 和 `redaction_status`。
  - 对 `provider-live-smoke-deepseek`、`worldengine-full-lifecycle-autonomous`、`llm-backed-full-lifecycle-autonomous` 建立 required artifact set。
  - 缺 required artifact 时保留 `blocked`，不映射为 PASS。
- Commands:
  - RED: `cd apps/api && uv run pytest tests/test_evidence.py -q`: 失败，2 failed，缺少 `schema_version` 和 `result_status`。
  - GREEN: `cd apps/api && uv run pytest tests/test_evidence.py -q`: 11 passed, 1 warning。
  - `git diff --check`: 通过，exit 0，无输出。
- Scope review:
  - 仅生成 manifest/index 层，不直接调用 provider，不运行 checker，不创建 WorldEngine result。
  - artifact paths 均为 bundle-relative paths，测试覆盖不以 `/` 开头且不包含 `..`。
  - status preservation 保持 `blocked` / `not_run`，未生成 required artifact 不会 PASS。
- Notes:
  - GREEN 测试 warning 为既有 `StarletteDeprecationWarning`。

## 当前实现结论

Task 3 已通过 focused verification 并已提交。

### Task 4: Named artifact builders 和 redaction scan

- Commit: pending
- Files:
  - `apps/api/app/routes/evidence.py`
  - `apps/api/tests/test_evidence.py`
  - `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/review.zh.md`
- Implementation:
  - 新增 `GET /sessions/{session_id}/evidence/bundle/artifacts`。
  - 输出 v0.9 named artifacts：`manifest.json`、`result.json`、`operation-log.jsonl`、`api-log.jsonl`、`api-summary.json`、provider/world/rule/event/Agent/replay/lifecycle/narrative/diagnostic summaries、`redaction-scan.json`、`scorecard-summary.json`、second-Agent/transcript/console/screenshots 占位状态。
  - `provider-live-summary.json` 在缺少 WorldEngine provider live evidence 时保留 `blocked`，并记录 public failure category。
  - `redaction-scan.json` 根据 bundle redaction flags 输出 `pass` 或 `fail`，blocking flags 不清空也不改写。
  - `result.json` 继承 manifest result status；redaction blocking leak 会使 result 变为 `fail`。
- Commands:
  - RED: `cd apps/api && uv run pytest tests/test_evidence.py -q`: 失败，2 failed，`/bundle/artifacts` 返回 404。
  - GREEN: `cd apps/api && uv run pytest tests/test_evidence.py tests/test_validation_runs.py -q`: 16 passed, 1 warning。
  - `git diff --check`: 通过，exit 0，无输出。
- Scope review:
  - Artifact builders 只打包当前客户端公开/脱敏证据，不调用 provider，不创建 WorldEngine 权威证据。
  - Direct API 证据输出为 `api-log.jsonl`，用户可见操作仍为 `operation-log.jsonl`。
  - `blocked`、`not_run`、`fail` 被保留，不升级为 PASS。
- Notes:
  - GREEN 测试 warning 为既有 `StarletteDeprecationWarning`。

## 当前实现结论

Task 4 已通过 focused verification，等待提交。
