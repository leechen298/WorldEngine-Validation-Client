# v0.7 Cross-Repository Validation Gate Matrix

Chinese mirror: `cross-repo-validation-gate-matrix.zh.md`.

Status: plan complete / pending execution

Purpose: connect WorldEngine, Validation Client, Codex autonomous validation,
second-Agent review, and human validation into a non-skippable execution
sequence. This document is not validation evidence and does not authorize
runtime, API, UI, E2E, or test implementation.

## 0. Principles

- WorldEngine owns the engine runtime and LLM provider.
- Validation Client owns the client surface, logs, and evidence.
- Codex autonomous validation only proves readiness for human validation.
- The second Agent performs read-only evidence review. It does not operate the
  browser again and does not add missing facts.
- Only a human can write `HUMAN_PASS`.
- Each gate may conclude only from commands and evidence observed in the
  current execution session.
- If a gate is not satisfied, the next gate must not start.

## 1. Current State

The current state is blocked at Gate 1.

Known facts:

- WorldEngine `/health` is reachable.
- WorldEngine `/openapi.json` is reachable.
- WorldEngine currently lacks `/manifest`.
- WorldEngine currently lacks a Validation Client-discoverable world creation
  endpoint.
- Validation Client `/health/worldengine` can detect WorldEngine as reachable.
- Validation Client `POST /sessions/worldengine` currently fails with:
  `WorldEngine public world creation endpoint not found`.

Allowed next step:

```text
Implement the WorldEngine 0.8.9 public contract first.
```

Not allowed now:

- Start Codex browser autonomous validation.
- Start second-Agent review.
- Start human validation.
- Claim that v0.7 validation passed.

## 2. Gate Matrix

| Gate | Name | Owner | Input | Required output | Allowed conclusions | Next gate condition |
| --- | --- | --- | --- | --- | --- | --- |
| Gate 0 | Documentation planning gate | Current planning chat | Existing discussion and docs in both repositories | v0.7 docs, 0.8.9 docs, this matrix | `PLAN_READY` / `PARTIAL` / `BLOCKED` | Both repositories have executable docs |
| Gate 1 | WorldEngine public contract readiness | WorldEngine | 0.8.9 package | `/manifest`, discoverable `POST /worlds`, provider readiness redaction, contract readiness checklist | `WORLDENGINE_CONTRACT_READY` / `PARTIAL` / `BLOCKED` / `FAIL` | Checklist says `WORLDENGINE_CONTRACT_READY` |
| Gate 2 | Validation Client v0.7 implementation readiness | Validation Client | Gate 1 conclusion and v0.7 plan | operation log, event/diff plus snapshot storage, E2E/UI smoke, evidence bundle, review | `READY_FOR_CODEX_AUTONOMOUS_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | tests/build/E2E/log/evidence review all pass |
| Gate 3 | Codex autonomous validation | Codex | Gate 2 review and runbook | `validation-runs/YYYY-MM-DD-codex/` evidence | `PASS_READY_FOR_HUMAN_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | Codex says `PASS_READY_FOR_HUMAN_VALIDATION` |
| Gate 4 | Second-Agent read-only review | Another Agent | Gate 3 run directory | `validation-runs/YYYY-MM-DD-agent-review.zh.md` | `READY_FOR_HUMAN_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | Agent says `READY_FOR_HUMAN_VALIDATION` |
| Gate 5 | Human validation | Human | Gate 3 and Gate 4 evidence | `validation-runs/YYYY-MM-DD-human.zh.md` | `HUMAN_PASS` / `HUMAN_PARTIAL` / `HUMAN_FAIL` | Human writes `HUMAN_PASS` |

## 3. Gate 0: Documentation Planning

Goal: make future chats stop guessing the workflow.

Required Validation Client documents:

```text
docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
```

Required WorldEngine package:

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/
```

Completion criteria:

- Docs say the next allowed step is WorldEngine contract implementation.
- Docs separate Codex, Agent, and human conclusions.
- Docs say Validation Client does not manage LLM keys or call providers.
- Docs say WorldEngine does not implement Validation Client behavior.
- Docs treat a branch as a branch and a commit point as a replayable time
  point. Branch semantics are limited to naming, switching, replay, and
  continued progression.

## 4. Gate 1: WorldEngine Public Contract Readiness

Goal: allow Validation Client to create and observe a WorldEngine-backed
session through public APIs only.

The WorldEngine implementation chat must first read:

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/AGENTS.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/project-north-star.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/product-model.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/scope-boundaries.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/roadmap.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/README.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/AGENTS.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/README.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/technical-design.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/validation-client-contract-handoff.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-task-plan.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
```

Required proof:

- `GET /health` returns 200.
- `GET /manifest` returns a public handoff manifest.
- `GET /openapi.json` exposes a client-discoverable world creation endpoint.
- Prefer `POST /worlds`.
- `POST /worlds` returns public `world_id`, `status`, public state, and a
  visualization payload.
- For full director validation, expose `POST /worlds/{world_id}/director-guidance`,
  or record a public unavailable reason in the manifest.
- Provider readiness is public summary only.
- No key, authorization header, private prompt, provider raw trace, Agent
  private memory, private goal, self_state, or hidden_context appears in public
  output.

Validation Client compatibility probe must succeed:

```bash
curl -i http://127.0.0.1:8765/health/worldengine
curl -i -H 'Content-Type: application/json' \
  -d '{"session_name":"Codex contract check","world_prompt":"observable small pixel world"}' \
  http://127.0.0.1:8765/sessions/worldengine
```

Evidence path:

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/review.zh.md
```

Only next gate condition:

```text
WorldEngine contract-readiness-checklist.zh.md concludes WORLDENGINE_CONTRACT_READY.
```

## 5. Gate 2: Validation Client v0.7 Implementation Readiness

Goal: make the client operable by Codex as a human-like browser user, with
complete evidence.

Future implementation must follow `implementation-task-plan.zh.md` task order.

Required implementation:

- WorldEngine preflight gate.
- Agent operation log JSONL.
- Lightweight event/diff persistence for each tick/event.
- Periodic snapshot persistence.
- Reconstruct any commit point by applying diffs forward from the nearest
  snapshot.
- Branches are independent timeline labels and switchable views.
- Evidence bundle aligns session id, WorldEngine world id, run id, commit
  point, and branch.
- Web UI operation-log hooks.
- Browser E2E / UI smoke or equivalent automated flow.
- Codex run report, second-Agent review template, and human validation
  template.

Storage requirements:

- Event/diff records are append-only.
- Snapshots are saved on a fixed interval or explicit checkpoint.
- Replay jumps use nearest snapshot plus later diffs.
- Do not infer event 1 by reversing event 2.
- Evidence bundle records diff count, snapshot count, commit point count, and
  branch count.
- Client logs and evidence must not include private prompts, provider raw
  traces, LLM keys, or Agent private state.

Required commands:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

If Playwright or an equivalent E2E runner is added, run it and retain artifacts.

Evidence path:

```text
docs/milestones/v0.7-agent-autonomous-validation/review.zh.md
```

Gate 3 conditions:

- v0.7 review records every implemented task.
- tests/build/E2E pass, or any omission is explicitly non-blocking.
- operation log parses.
- evidence bundle downloads and parses.
- redaction scan has no unexplained leak.
- conclusion is `READY_FOR_CODEX_AUTONOMOUS_VALIDATION`.

## 6. Gate 3: Codex Autonomous Validation

Goal: Codex operates the complete Web client from a human viewpoint and
produces replayable evidence.

Required documents:

```text
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
```

Required output directory:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/
  agent-run.jsonl
  codex.zh.md
  api-summary.json
  screenshots/
  downloads/evidence-bundle.json
```

Browser flow must cover:

- Open session library.
- Check WorldEngine connection status.
- Enter base world premise.
- Create WorldEngine session.
- Enter runtime console.
- Inspect pixel canvas.
- Inspect public world state.
- Inspect public Agent state.
- Inspect World Log.
- Inspect Agent Life Log.
- Enter high-level director guidance.
- Submit director guidance.
- Use replay slider.
- Create branch from a commit point.
- Switch branch view.
- Download evidence bundle.

Only Gate 4 condition:

```text
codex.zh.md concludes PASS_READY_FOR_HUMAN_VALIDATION.
```

## 7. Gate 4: Second-Agent Read-Only Review

Goal: another Agent checks whether Codex evidence supports moving to human
validation.

Read-only inputs:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/codex.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/agent-run.jsonl
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/api-summary.json
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/screenshots/
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/downloads/evidence-bundle.json
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
```

Required checks:

- Codex followed the runbook.
- operation log covers key UI actions.
- API summary supports visible UI results.
- screenshots cover key pages.
- evidence bundle matches session/run/commit point/branch.
- redaction scan is clean.
- Codex did not claim human pass.

Only Gate 5 condition:

```text
agent-review concludes READY_FOR_HUMAN_VALIDATION.
```

## 8. Gate 5: Human Validation

Goal: a human judges the game-like client experience and whether world runtime
behavior is credible.

Human validation judges only:

- The world is observable.
- Pixel UI, public state, and event logs explain each other.
- Public Agent state and behavior look like natural living behavior.
- Director guidance remains high-level direction, not item placement or player
  commands.
- Replay and branches read as timelines.
- Evidence bundle is enough for replay and audit.

Human output:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-human.zh.md
```

Only this conclusion means human validation passed:

```text
HUMAN_PASS
```

## 9. Global Stop Rules

Stop immediately and record `BLOCKED`, `PARTIAL`, or `FAIL` when:

- WorldEngine lacks `/manifest`.
- WorldEngine OpenAPI lacks a discoverable world creation endpoint.
- Validation Client cannot create a WorldEngine-backed session.
- provider readiness pretends to be ready.
- API key, authorization header, private prompt, provider raw trace, or Agent
  private state leaks.
- operation log cannot parse.
- evidence bundle cannot be matched to run/session/commit point/branch.
- E2E lacks key screenshots or failure context.
- second-Agent review has not run.
- Codex or Agent states automated validation as human experience pass.

## 10. Future Chat Order

Open future chats in this exact order:

1. WorldEngine: `/goal implement 0.8.9-external-validation-provider-and-handoff-manifest`
2. Validation Client: `/goal develop v0.7 Agent Autonomous Validation`
3. Validation Client: `/goal autonomously validate v0.7`
4. Validation Client or another Agent: `/goal review v0.7 Codex autonomous validation evidence`
5. Human: `/goal human validate v0.7`

Copy-ready prompts:

```text
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
```
