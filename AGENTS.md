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
6. the active milestone `review.zh.md`
7. relevant ADRs under `docs/adr/`
8. `docs/agent-guides/routing.md`
9. `docs/agent-guides/workflow.md`
10. `docs/agent-guides/boundaries.md`

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
world lines and must not imply parent-child ownership.
