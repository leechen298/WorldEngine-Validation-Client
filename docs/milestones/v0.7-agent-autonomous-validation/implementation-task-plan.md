# v0.7 Detailed Implementation Plan

Chinese mirror: `implementation-task-plan.zh.md`.

Status: planned / pending implementation

This document decomposes `codex-autonomous-validation-master-plan.zh.md` into
execution tasks for a future development chat. It does not authorize runtime,
API, UI, E2E, or test implementation in the current documentation stage.

## 0. Preconditions

Before a future chat starts `develop v0.7`, confirm:

- WorldEngine has implemented the 0.8.9 public contract.
- WorldEngine `GET /manifest` is available and does not include secrets,
  private prompts, or provider raw traces.
- WorldEngine OpenAPI exposes a Validation Client-discoverable world creation
  endpoint, preferably `POST /worlds`.
- Validation Client `GET /health/worldengine` reports reachable, OpenAPI
  available, and `world_creation: available`.
- Validation Client `POST /sessions/worldengine` can create a
  WorldEngine-backed session.

If any condition is missing, v0.7 implementation may only record BLOCKED or
PARTIAL. It must not proceed to browser autonomous validation or human handoff.

## 1. File Responsibilities

Primary implementation candidates:

```text
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/app/routes/sessions.py
apps/api/app/routes/evidence.py
apps/api/app/worldengine_client.py
apps/api/tests/test_sessions.py
apps/api/tests/test_evidence.py
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/pages/SessionLibrary.tsx
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/SessionLibrary.test.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

If E2E is added, create:

```text
apps/web/e2e/
apps/web/playwright.config.ts
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/
```

Do not modify:

```text
WorldEngine source code
LLM provider key management
WorldEngine private prompts, oracle, or evaluator internals
Agent private memory, private goal, or self_state
```

## 2. Task Sequence

Each task should be committed separately. If a task fails, update
`review.zh.md` with the failure before moving on.

### Task 1: WorldEngine preflight gate

Goal: let the client decide whether WorldEngine satisfies the v0.7 prerequisite
contract before creating a session.

Implement:

- Fetch manifest and summarize OpenAPI discovery in
  `apps/api/app/worldengine_client.py`.
- Expose a redacted preflight result through health or an existing status
  response.
- Keep keys, authorization headers, and provider raw traces out of responses.

Minimum tests:

- Unreachable WorldEngine returns `reachable: false`.
- OpenAPI without a world creation endpoint returns `world_creation: unknown`
  or `unavailable`.
- OpenAPI with `POST /worlds` returns `world_creation: available`.
- Manifest private fields are not returned as public payload.

Run:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest tests/test_health.py tests/test_sessions.py -q
git diff --check
```

Done when health/preflight output clearly says whether a WorldEngine session can
be created, with no secret or private trace leakage.

### Task 2: Agent operation log data model

Goal: generate reviewable JSONL logs for Codex browser operations.

Implement a validation run / operation log model or equivalent evidence export
structure with:

```text
timestamp
run_id
actor
phase
url
action_type
target_label
input_text
request_method
request_path
response_status
response_summary
visible_result
screenshot_path
downloaded_file
notes
```

Redact or reject:

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
private filesystem path
```

Run:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest tests/test_evidence.py -q
git diff --check
```

Done when JSONL lines parse, each record has `run_id` and `timestamp`, and
forbidden private fields cannot be written.

### Task 2.5: Event/diff and snapshot storage

Goal: use lightweight event/diff records plus periodic snapshots to support
replay jumps, commit-point review, and branch timelines.

Implement:

- commit point, event/diff, and snapshot records in backend models, schemas, or
  evidence export structures.
- append-only diffs for each tick/event.
- snapshots on a fixed tick interval, fixed event interval, or explicit
  checkpoint.
- target commit-point reconstruction by applying later diffs forward from the
  nearest snapshot.
- no event 1 inference by reversing event 2.
- branch handling only as branch id / branch name / current branch view.
- these fields in the evidence bundle:

```text
commit_point_count
branch_count
event_diff_count
snapshot_count
latest_commit_point_id
active_branch_id
```

Candidate files:

```text
apps/api/app/models.py
apps/api/app/schemas.py
apps/api/app/routes/evidence.py
apps/api/tests/test_evidence.py
apps/web/src/api/types.ts
apps/web/src/pages/RuntimeConsole.tsx
```

Run:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest tests/test_evidence.py -q
pnpm --dir apps/web test
git diff --check
```

Done when applying diffs forward from the nearest snapshot reconstructs the
target commit-point public state, the evidence bundle can explain where each
commit point and branch public state lives, branch switching relies only on
branch id, commit point, and current view state, and stored data excludes
private prompts, provider raw traces, LLM keys, and Agent private state.

### Task 3: API summary and evidence bundle association

Goal: associate every autonomous run with API summaries, screenshots, and the
downloaded evidence bundle.

Implement:

- validation run metadata in the evidence bundle.
- redacted API traces containing method, path, status, public summary, and error
  class only.
- consistent references among session id, WorldEngine world id, timeline branch
  id, and evidence bundle filename.

Run:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest tests/test_evidence.py tests/test_sessions.py -q
pnpm run test
git diff --check
```

Done when the evidence bundle `session_id` matches the validation run, the API
summary contains no raw provider response, and tests parse the bundle.

### Task 4: Web UI operation-log hooks

Goal: have human-visible UI actions produce operation-log records.

Implement:

- session library logging for page open, WorldEngine status check, session input,
  and create submit.
- runtime console logging for page open, public state inspection, director
  guidance, replay, branch, and evidence download.
- logging driven by UI actions or API responses, not hidden private state.

Run:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

Done when Web tests cover key logging behavior, local and WorldEngine sessions
still work, and the UI does not imply authoritative evaluator PASS.

### Task 5: Browser E2E / UI smoke runner

Goal: provide a Codex-runnable browser autonomous validation path.

The flow must cover:

- open session library.
- check WorldEngine connection status.
- create a WorldEngine session.
- enter runtime console.
- inspect pixel canvas, public state, World Log, and Agent Life Log.
- submit high-level director guidance.
- use replay slider.
- create a branch from a commit point.
- download evidence bundle.

If Playwright is selected, run:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
pnpm --dir apps/web exec playwright test
git diff --check
```

Done when artifacts are saved, failures include screenshots, and success
produces `agent-run.jsonl` and `api-summary.json`.

### Task 6: Codex run report template

Goal: give autonomous validation a fixed report shape.

Create or update:

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.md
```

The report must contain:

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
api summary path
redaction scan result
known gaps
conclusion
```

Allowed conclusions:

```text
PASS_READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

### Task 7: Second Agent read-only review template

Goal: let another Agent review the previous Codex run without operating the
browser.

Create or update:

```text
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.md
```

The template must check:

- operation log coverage.
- screenshot coverage.
- whether API summaries support UI results.
- whether evidence bundle matches session and run.
- whether redaction scan is clean.
- whether Codex avoided claiming human pass.

Allowed conclusions:

```text
READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

### Task 8: Human validation handoff template

Goal: hand automated evidence to a human experience reviewer.

Create or update:

```text
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.md
```

The template must ask only:

- whether the world is observable.
- whether canvas, public state, and event logs explain each other.
- whether public Agent behavior feels natural.
- whether director guidance remains high level.
- whether replay and branch feel like world lines.
- whether evidence can be replayed.

Allowed conclusions:

```text
HUMAN_PASS
HUMAN_PARTIAL
HUMAN_FAIL
```

### Task 9: Full v0.7 closeout check

Goal: decide whether v0.7 can enter Codex autonomous validation or must stop as
BLOCKED/PARTIAL.

Run:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

If E2E is added, run the E2E command too.

Done when `review.zh.md` records every task commit, changed files, commands,
results, and remaining issues. Do not enter human validation before the second
Agent review. Do not claim product pass before `HUMAN_PASS`.

## 3. Validation Path

```text
WorldEngine 0.8.9 contract ready
-> Validation Client v0.7 implementation complete
-> Codex browser autonomous run
-> second Agent read-only review
-> human validation
```

## 4. Stop Rules

- Stop if WorldEngine public contract is insufficient.
- If provider is missing, record only the WorldEngine public warning; do not
  fake generation output.
- Stop if operation logs are incomplete.
- Stop if evidence bundle cannot be matched to session/run.
- FAIL on secret or private state leakage.
- Do not hand off to humans before second Agent review.
- Do not claim product pass before human validation is complete.
