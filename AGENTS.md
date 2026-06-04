# AGENTS.md

Guidance for Codex and other AI coding agents working in this repository.

Chinese mirror: `AGENTS.zh.md`.

## Project Role

`WorldEngine-Validation-Client` is an external validation and observation
client for WorldEngine. It is a separate repository from WorldEngine and must
not become a WorldEngine submodule, private test fixture, or implementation
backdoor.

The client may communicate with WorldEngine only through public interfaces:

- `WORLDENGINE_API_BASE`
- public HTTP APIs
- public schemas, manifests, and OpenAPI descriptions
- public event, state, timeline, and evaluator outputs

## Required Reading

Before planning, implementing, reviewing, or completing milestone work, read:

1. `docs/README.zh.md`
2. `docs/roadmap.zh.md`
3. `docs/specs/validation-client-design.zh.md`
4. the active milestone `README.zh.md`
5. the active milestone `plan.zh.md`
6. the active milestone `implementation-task-plan.zh.md`, if that file exists
7. the active milestone `cross-repo-validation-gate-matrix.zh.md`, if that file exists
8. the active milestone `planning-readiness-checklist.zh.md`, if that file exists
9. the active milestone `review.zh.md`
10. relevant ADRs under `docs/adr/`
11. `docs/agent-guides/routing.md`
12. `docs/agent-guides/workflow.md`
13. `docs/agent-guides/boundaries.md`

For validation requests such as autonomous validation, Agent validation, or
human validation, also read:

14. the active milestone `validation.zh.md`
15. `docs/agent-guides/validation-workflow.md`
16. the active milestone `autonomous-validation-runbook.zh.md`, if it exists
17. the active milestone `codex-run-report-template.zh.md`, if it exists
18. the active milestone `agent-review-template.zh.md`, if it exists
19. the active milestone `human-validation-template.zh.md`, if it exists

For next-chat handoff, next-step, handoff, quickstart, or copy-ready `/goal`
prompt requests, also read:

20. the active milestone `planning-readiness-checklist.zh.md`, if it exists
21. the active milestone `next-chat-quickstart.zh.md`, if it exists

For v0.1, the active milestone is:

```text
docs/milestones/v0.1-foundation/
```

## Short Router

| User request | Route | Primary guide |
| --- | --- | --- |
| develop / implement / continue vX.Y | `docs/milestones/vX.Y-*/` | `docs/agent-guides/routing.md` |
| plan / create docs / prepare vX.Y | create or update `docs/milestones/vX.Y-*/` | `docs/agent-guides/routing.md` |
| review / audit / inspect vX.Y | matching milestone plus current git diff | `docs/agent-guides/workflow.md` |
| change tech stack or architecture decision | `docs/adr/` | `docs/agent-guides/workflow.md` |
| change product boundary or overall design | `docs/specs/validation-client-design.zh.md` | `docs/agent-guides/boundaries.md` |
| autonomous / Agent validation vX.Y | matching milestone plus `validation.zh.md` | `docs/agent-guides/validation-workflow.md` |
| human validation vX.Y | matching milestone, latest Codex run, and `validation.zh.md` | `docs/agent-guides/validation-workflow.md` |

A trigger phrase is routing only. It does not authorize skipping milestone
documents, task order, verification, review records, or task-level commits.

## Non-Negotiable Execution Rules

Detailed rules live in `docs/agent-guides/workflow.md`. The short version:

- Execute milestone work strictly in `plan.zh.md` task order.
- Work on only one numbered task at a time.
- Do not start the next task until the current task is implemented, verified,
  recorded in `review.zh.md`, and committed.
- Every numbered task needs its own commit unless the user explicitly approves
  combining tasks before implementation.
- Do not mark a milestone complete while related implementation files remain
  unstaged or uncommitted.
- Do not claim a check passed unless it ran in the current work session.
- Branches ending in `-local` are local-only working branches. Never push a
  `*-local` branch; when sharing work, merge or replay its patch-equivalent
  commits onto the matching non-local branch first, then push only that target
  branch when the user explicitly requests a push.

## Boundary Rules

Detailed boundaries live in `docs/agent-guides/boundaries.md`.

The validation client must not manage LLM keys, call LLM providers directly,
generate authoritative world facts, import WorldEngine source code, or mutate
Agent internal state. Timeline branches are modeled like code branches:
reconstructable ticks or event points are commit points; branches are named
world lines for naming, switching, replay, and continued progression.
