# Codex Autonomous Validation to Human Validation Master Plan

Chinese mirror: `codex-autonomous-validation-master-plan.zh.md`.

> **For agentic workers:** Future implementation must use
> subagent-driven development or an equivalent task-by-task workflow. Each
> phase must write evidence before the next phase starts.

**Goal:** Let Codex operate the validation client from a human-like browser
perspective, produce replayable evidence, have a second Agent review that
evidence in read-only mode, and then hand the result to a human for experience
validation.

**Architecture:** WorldEngine owns world generation, LLM provider management,
Agent behavior, runtime progression, evaluator output, and public contracts.
Validation Client consumes only WorldEngine public APIs, stores client-side
operation evidence, and presents visible state. Codex performs browser
operation and evidence collection. A second Agent reviews the evidence. Humans
judge experience quality.

**Tech Stack:** WorldEngine FastAPI public API, Validation Client FastAPI API,
React/Vite Web UI, JSONL operation logs, Playwright or Browser automation, and
JSON evidence bundles.

---

## 0. Current Measured State

As of 2026-06-04:

- Validation Client local branch is `v0.7`.
- Local `v0.7` commit is still
  `833063b8656149b1f8163d0affd12a7ba185e81a`, the same as local `v0.6`.
- Remote heads observed only up to `origin/v0.5`; no `origin/v0.6` or
  `origin/v0.7` was found.
- `pnpm run test` passed: Web 24 tests and API 48 tests.
- `pnpm run build` passed.
- WorldEngine can start locally. `GET /health` and `GET /openapi.json` return
  200.
- Validation Client `GET /health/worldengine` can reach WorldEngine.
- Validation Client `POST /sessions/worldengine` currently fails with
  `WorldEngine public world creation endpoint not found`.

Current conclusion:

- Do not enter human validation.
- Do not record Codex autonomous validation PASS.
- First fix the WorldEngine public world creation contract, or adapt Validation
  Client to a reviewed public WorldEngine generation API.

## 1. Validation Layers

### 1.1 What Codex autonomous validation proves

Codex autonomous validation proves only:

- the client can be operated from a human-like browser perspective.
- baseline tests and builds pass.
- WorldEngine public APIs can be consumed by the client.
- the UI flow can complete.
- operation logs are replayable.
- evidence bundles can be downloaded and parsed.
- keys, private prompts, provider raw traces, and private Agent state are not
  leaked.
- evidence is sufficient to enter human validation.

It does not prove:

- world experience quality.
- natural or credible Agent behavior.
- authoritative WorldEngine evaluator pass.
- final provider cost, speed, or quality.
- that human experience judgment can be automated.

### 1.2 What the second Agent review proves

The second Agent review proves only:

- whether Codex followed the validation plan.
- whether operation logs and artifacts are complete.
- whether the evidence bundle supports the previous operation record.
- whether boundary, redaction, or evidence gaps exist.
- whether the run is ready for human validation.

The second Agent does not operate the browser, invent missing facts, or replace
human experience judgment.

### 1.3 What human validation judges

Human validation judges:

- whether the world is observable.
- whether pixel UI, event logs, and public state explain each other.
- whether Agents appear to react naturally to public state and events.
- whether director guidance only affects external events and world-environment
  trends.
- whether replay and branch behavior can be understood as world lines.
- whether the evidence bundle is clear enough to replay.

## 2. File Responsibilities

### 2.1 Validation Client

Planning and evidence:

```text
docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
docs/milestones/v0.7-agent-autonomous-validation/review.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/
```

Backend candidates:

```text
apps/api/app/routes/
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/app/worldengine_client.py
apps/api/tests/
```

Frontend candidates:

```text
apps/web/src/pages/SessionLibrary.tsx
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/store/sessionStore.ts
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/__tests__/
```

Browser automation candidates:

```text
apps/web/e2e/
apps/web/playwright.config.ts
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/
```

### 2.2 WorldEngine

WorldEngine-side prerequisite contract package:

```text
docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/
```

Future implementation candidates:

```text
backend/app/api/routes/
backend/app/schemas/
backend/app/core/
backend/app/tests/
docs/contracts/
```

## 3. End-to-End Phase Plan

### Phase 1: WorldEngine public contract ready

Goal: let Validation Client create worlds, observe public state, and submit
high-level director guidance through public APIs.

Required:

- `GET /health` is available.
- `GET /openapi.json` is available.
- `GET /manifest` or an equivalent handoff manifest is available.
- OpenAPI exposes a client-discoverable world creation endpoint.
- world creation response includes public `world_id`, `status`,
  `public_initial_state` or `initial_state`, and `visualization` or
  `visualization_payload`.
- if director guidance is in scope, OpenAPI exposes a public director guidance
  endpoint.
- provider readiness is public and redacted; credentials are never exposed.

Recommended contract:

```text
GET /manifest
POST /worlds
POST /worlds/{world_id}/director-guidance
```

Minimum `GET /manifest` response:

```json
{
  "schema_version": "0.8.x",
  "worldengine_version": "v0.8",
  "provider": {
    "provider_class": "mock|kimi_platform_api|deepseek_api|unknown",
    "provider_readiness": "ready|limited|blocked|unknown",
    "credential_source_class": "environment|not_configured|unknown",
    "model_label": "public-or-redacted-label"
  },
  "public_surfaces": [
    "/health",
    "/openapi.json",
    "/worlds",
    "/worlds/{world_id}/director-guidance"
  ],
  "redaction": {
    "secrets_included": false,
    "private_prompts_included": false,
    "provider_raw_traces_included": false
  },
  "blockers": [],
  "warnings": []
}
```

Minimum `POST /worlds` request:

```json
{
  "world_prompt": "a small observable pixel world"
}
```

Minimum `POST /worlds` response:

```json
{
  "world_id": "world-001",
  "status": "created",
  "public_initial_state": {
    "summary": "public summary",
    "public_agents": [
      {
        "agent_id": "agent-1",
        "display_name": "Ada",
        "location": "market",
        "public_status": "observing",
        "visible_action": "opens a stall"
      }
    ]
  },
  "visualization": {
    "tiles": [],
    "entities": []
  }
}
```

Verification:

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine/backend
.venv/bin/python -m pytest app/tests -q
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine
git diff --check
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/manifest
curl -i http://127.0.0.1:8000/openapi.json
curl -i -H 'Content-Type: application/json' \
  -d '{"world_prompt":"a small observable pixel world"}' \
  http://127.0.0.1:8000/worlds
```

Stop rules:

- no world creation endpoint: do not enter Phase 2.
- manifest leaks keys, private prompts, or provider raw traces: FAIL.
- endpoint exists but cannot be discovered by the client: PARTIAL; do not enter
  browser autonomous validation.

### Phase 2: Validation Client operation log ready

Goal: record Codex's human-like browser actions in reviewable logs.

Required:

- operation log run id.
- JSONL records for UI actions.
- key API request / response summaries.
- screenshot paths.
- downloaded evidence bundle filenames.
- redaction check result.
- validation run report template.

Recommended JSONL shape:

```json
{
  "timestamp": "2026-06-04T00:00:00Z",
  "run_id": "2026-06-04-codex-v0.7",
  "actor": "codex",
  "phase": "ui_smoke",
  "url": "http://127.0.0.1:5173/",
  "action_type": "click|fill|submit|api_request|api_response|screenshot|download|assertion",
  "target_label": "Create world",
  "input_text": "a small observable pixel world",
  "request_method": "POST",
  "request_path": "/sessions/worldengine",
  "response_status": 201,
  "response_summary": {
    "session_id": "session-public-id",
    "worldengine_world_id": "world-public-id"
  },
  "visible_result": "Runtime console opened",
  "screenshot_path": "screenshots/04-runtime-console.png",
  "downloaded_file": null,
  "notes": "public summary only"
}
```

Forbidden in logs and bundles:

```text
api_key
authorization
credential
password
provider secret
private prompt
provider raw trace
Agent private memory
Agent private goal
Agent self_state
hidden_context
private WorldEngine path
```

Verification:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
pnpm run test
pnpm run build
git diff --check
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_prompt|raw_response|hidden_context|self_state" \
  apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

Stop rules:

- no operation log: do not enter Agent review.
- missing UI action, API summary, screenshot, or download records: PARTIAL.
- real secret in logs or bundle: FAIL.

### Phase 3: Codex browser autonomous run

Goal: Codex operates the client like a human.

Formal execution must use:

```text
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
```

Start services:

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine/backend
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

cd /Users/leechen/projects/WorldEngine-Validation-Client
uv run --project apps/api uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir apps/api
pnpm --dir apps/web dev
```

Browser flow:

1. Open the Web URL.
2. Capture the session library screenshot.
3. Check WorldEngine connection status.
4. Enter session name.
5. Enter base world premise.
6. Create the world.
7. Wait for runtime console.
8. Capture runtime screenshot.
9. Inspect public state summary.
10. Inspect pixel canvas.
11. Inspect Agent public state.
12. Inspect World Log.
13. Inspect Agent Life Log.
14. Enter high-level director guidance.
15. Submit guidance.
16. Capture guidance status.
17. Use replay slider.
18. Select a commit point.
19. Enter branch name.
20. Create a branch from that commit point.
21. Switch branch.
22. Open evidence panel.
23. Download evidence bundle.
24. Parse evidence bundle.
25. Generate `agent-run.jsonl`.
26. Generate `codex.zh.md`.

Artifact directory:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/2026-06-04-codex/
```

Suggested contents:

```text
agent-run.jsonl
codex.zh.md
screenshots/01-session-library.png
screenshots/02-create-world.png
screenshots/03-runtime-console.png
screenshots/04-director-guidance.png
screenshots/05-replay-branch.png
screenshots/06-evidence-panel.png
downloads/evidence-bundle.json
api-summary.json
```

`codex.zh.md` must include:

```text
run_id
branch
commit
WorldEngine API base
Validation Client API base
Web URL
commands run
test results
browser flow summary
operation log path
screenshots path
evidence bundle path
redaction scan result
known gaps
conclusion
```

Use this template when generating `codex.zh.md`:

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
```

Allowed Codex conclusions:

```text
PASS_READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

Stop rules:

- WorldEngine session creation fails: BLOCKED or FAIL, depending on cause.
- UI cannot create a world: BLOCKED.
- evidence bundle cannot download: PARTIAL or FAIL.
- logs cannot be replayed: FAIL.
- conclusion claims world experience passed: FAIL.

### Phase 4: second Agent read-only review

Goal: another Agent reviews Phase 3 evidence without operating the browser.

Inputs:

```text
agent-run.jsonl
codex.zh.md
screenshots/
downloads/evidence-bundle.json
api-summary.json
git status output
test/build output
WorldEngine manifest/openapi summaries
```

Checklist:

- Codex ran required commands.
- Codex started WorldEngine, API, and Web.
- operation log covers each key UI action.
- API summaries correspond to visible UI state.
- screenshots cover session library, runtime console, director guidance,
  replay, branch, and evidence.
- evidence bundle `session_id` matches the run.
- evidence bundle counts match records.
- redaction flags are clean.
- private-data scan has no real leakage.
- Codex conclusion is limited to ready-for-human-validation.

Output:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/2026-06-04-agent-review.zh.md
```

Use this template when generating the review output:

```text
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
```

Allowed review conclusions:

```text
READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

Stop rules:

- incomplete operation log: do not enter human validation.
- evidence does not match the session: do not enter human validation.
- leakage found: FAIL.

### Phase 5: human validation handoff

Goal: hand automated evidence to a human and let the human judge experience.

Human reads:

```text
codex.zh.md
agent-review.zh.md
agent-run.jsonl
screenshots/
evidence-bundle.json
```

Human checks:

- session library is understandable.
- world creation feels clear.
- world is observable.
- map, Agents, and event logs explain each other.
- Agent public state has life-like value.
- director guidance feels high level, not direct player control.
- replay can revisit state.
- branch behavior feels like world lines.
- evidence bundle is sufficient for replay.
- experience issues are clear enough to drive the next iteration.

Output:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/2026-06-04-human.zh.md
```

Use this template when generating the human report:

```text
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
```

Allowed human conclusions:

```text
HUMAN_PASS
HUMAN_PARTIAL
HUMAN_FAIL
```

## 4. Future Chat Sequence

```text
WorldEngine contract -> Validation Client v0.7 operation log/E2E -> Codex autonomous run -> second Agent review -> human validation
```

## 5. Final Completion Standard

Only when all conditions are true may the project say "Codex autonomous
validation is complete and ready for human validation":

- WorldEngine public contract ready.
- Validation Client tests and build pass.
- browser UI flow completes.
- operation log JSONL is complete.
- screenshots cover key screens.
- evidence bundle downloads and parses.
- evidence bundle matches session/run.
- redaction scan is clean.
- second Agent read-only review passes.
- Codex conclusion is exactly limited to `PASS_READY_FOR_HUMAN_VALIDATION`.

Only a human `HUMAN_PASS` means human validation passed.
