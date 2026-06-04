# Validation Workflow: Agent Autonomous Validation -> Human Validation

Chinese mirror: `validation-workflow.zh.md`.

## Scope

This workflow validates implemented validation-client milestones, especially
v0.7 and later Agent autonomous validation, Agent review, and human-validation
handoff work.

It is not an implementation workflow. Implementation still follows the task
loop in `workflow.md`.

## Triggers

Use this workflow when the user asks for:

- autonomous validation for vX.Y
- Codex validation for vX.Y
- Agent autonomous testing for vX.Y
- Agent validation for vX.Y
- human validation for vX.Y
- human review for vX.Y

## Required Reading

Before validation, read:

1. `docs/README.zh.md`
2. `docs/roadmap.zh.md`
3. `docs/specs/validation-client-design.zh.md`
4. the active milestone `README.zh.md`
5. the active milestone `plan.zh.md`
6. the active milestone `implementation-task-plan.zh.md`, if it exists
7. the active milestone `review.zh.md`
8. the active milestone `validation.zh.md`
9. `docs/agent-guides/routing.md`
10. `docs/agent-guides/workflow.md`
11. `docs/agent-guides/boundaries.md`

Human validation must also read the latest Codex / Agent autonomous validation
run record.

## Validation Roles

### Codex Autonomous Validation

Codex autonomous validation proves that the client is reliable, boundary-safe,
and reviewable enough to enter human validation.

Codex may judge:

- whether tests and builds pass.
- whether basic E2E / UI smoke flows complete.
- whether API endpoints return expected structures.
- whether evidence bundles download, parse, and keep count consistency.
- whether redaction flags and sensitive-content scans are consistent.
- whether the client still works only through the local backend and
  WorldEngine public APIs.

Codex must not automatically claim:

- that the world experience passed.
- that Agent behavior is natural and credible.
- that director guidance semantics satisfy human product expectations.
- that WorldEngine evaluator output gives an authoritative pass.

### Agent Autonomous Testing

Agent autonomous testing is performed by an operation Agent using the client
from a human-like perspective. The current operation Agent may be Codex; future
Agents may include OpenClaw or other agents.

The operation Agent must record detailed logs:

- visited URLs.
- clicked buttons.
- entered text.
- selected branch / tick / commit point.
- API request and response summaries.
- server statuses, errors, and evidence bundle manifests.
- screenshots, downloaded filenames, and key visible UI states.

The log must be detailed enough for another Agent or a human to replay the
operation.

### Agent Validation

Agent validation is performed by a second Agent that reads the operation log,
screenshots, API records, and evidence bundle from the previous run.

The review Agent must not invent unrecorded behavior. It may only judge:

- whether the planned steps were executed.
- whether evidence is complete.
- whether the result supports entering human validation.
- whether any gaps must be fixed first.

### Human Validation

Human validation should not repeat Codex command checks. It judges:

- whether the world is observable.
- whether worldview, scenes, Agents, and events are coherent.
- whether Agents appear to react naturally to public state and events.
- whether director guidance only affects external environment and event
  trends.
- whether replay and branches feel like world lines / saves.
- whether the evidence bundle is clear enough for another human to review.

## Codex Autonomous Validation Stages

1. Preflight:

```bash
git status --short --branch
git diff --check
```

2. Backend validation:

```bash
cd apps/api && uv run pytest -q
cd apps/api && uv run pytest tests/test_evidence.py -q
```

3. Frontend validation:

```bash
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
```

4. Basic E2E / UI smoke:

- open the session library.
- check WorldEngine connection status.
- create a local or WorldEngine session.
- open the runtime console.
- inspect pixel canvas, public state, logs, and Agent public state.
- submit high-level director guidance.
- use replay / branch controls.
- inspect the evidence panel.
- download the evidence bundle.

5. Operation log:

The UI smoke must produce a structured operation log with timestamps, actor,
URL, action type, target, input text, request method, request path, response
status, response summary, visible result, screenshot path, and notes.

6. Evidence bundle check:

- JSON parses.
- `manifest.session_id` matches the validation session.
- counts match records.
- warnings are readable.
- redaction flags match records.
- the bundle does not claim evaluator pass unless public WorldEngine evaluator
  output exists.

7. Boundary scan:

```bash
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones
```

Allowed hits include redaction constants, negative tests, and boundary
documents. UI private-content display, bundle private-content output, real
secrets, and WorldEngine private path/helper coupling are forbidden.

## Conclusion Standard

### PASS

Codex autonomous validation may write PASS only when all required commands pass
in the current session, E2E / UI smoke completes, operation logs are complete,
the evidence bundle downloads and parses, redaction/boundary checks pass, no
related implementation changes remain uncommitted, and the conclusion is
limited to "ready for human validation".

### PARTIAL

Use PARTIAL when core commands pass but E2E, live WorldEngine integration,
evidence download, or human handoff material has gaps.

### BLOCKED

Use BLOCKED when dependencies, WorldEngine, LLM provider configuration, ports,
sandbox permissions, or browser availability prevent progress.

### FAIL

Use FAIL when tests/builds fail, evidence leaks private content, boundaries are
violated, UI claims authoritative evaluator pass incorrectly, or operation logs
miss key steps.

## Output Locations

Codex autonomous validation run:

```text
docs/milestones/vX.Y-*/validation-runs/YYYY-MM-DD-codex.zh.md
```

If the active milestone provides `codex-run-report-template.zh.md`, use that
template for output.

Agent operation log:

```text
docs/milestones/vX.Y-*/validation-runs/YYYY-MM-DD-agent-run.jsonl
```

If the active milestone provides `agent-review-template.zh.md`, use that
template for second Agent review output.

Human validation run:

```text
docs/milestones/vX.Y-*/validation-runs/YYYY-MM-DD-human.zh.md
```

If the active milestone provides `human-validation-template.zh.md`, use that
template for human validation output.

## Stop Rules

- If WorldEngine public APIs are insufficient, stop and record a WorldEngine
  prerequisite gap.
- If LLM provider access is needed, WorldEngine must own provider and key
  management; the validation client must not take over.
- If the evidence bundle contains private content, stop and record FAIL.
- If the operation Agent cannot produce replayable logs, do not enter Agent
  validation.
- If Codex autonomous validation is incomplete, do not ask the human validator
  to judge full product pass.
