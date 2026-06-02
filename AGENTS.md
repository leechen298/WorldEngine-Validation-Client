# AGENTS.md

Guidance for Codex and other AI coding agents working in this repository.

This repository uses a lightweight industry-style workflow built around
specs, milestones, ADRs, tests, reviews, and small commits. It is intentionally
lighter than the WorldEngine core repository, but the execution discipline is
strict.

Chinese is the preferred language for user-facing planning, review, and
status reports unless the user asks otherwise.

## Project Role

`WorldEngine-Validation-Client` is an external validation and observation
client for WorldEngine.

It is a separate repository from WorldEngine. It must not become a
WorldEngine submodule, private test fixture, or implementation backdoor.

The client may communicate with WorldEngine only through public interfaces:

- `WORLDENGINE_API_BASE`
- public HTTP APIs
- public schemas, manifests, and OpenAPI descriptions
- public event, state, timeline, and evaluator outputs

The client must not:

- import WorldEngine source code
- depend on private WorldEngine local paths
- call WorldEngine internal helpers
- manage LLM API keys
- call LLM providers directly
- generate authoritative world facts
- directly mutate Agent memory, goals, identity, self-state, relationships, or
  actions

## Documentation Sources

Before planning or implementing milestone work, read:

1. `docs/README.zh.md`
2. `docs/roadmap.zh.md`
3. `docs/specs/validation-client-design.zh.md`
4. the active milestone `README.zh.md`
5. the active milestone `plan.zh.md`
6. the active milestone `review.zh.md`
7. relevant ADRs under `docs/adr/`

For v0.1, the active milestone documents are:

- `docs/milestones/v0.1-foundation/README.zh.md`
- `docs/milestones/v0.1-foundation/plan.zh.md`
- `docs/milestones/v0.1-foundation/review.zh.md`

## Natural Language Routing

A trigger phrase is routing only. It does not authorize skipping milestone
documents, task order, verification, review records, or task-level commits.

| User request | Route | Required documents |
| --- | --- | --- |
| `开发 v0.1`, `实现 v0.1`, `继续 v0.1`, `/goal 开发 v0.1`, `/goal 实现 v0.1` | `docs/milestones/v0.1-foundation/` | `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| `规划 v0.2`, `生成 v0.2 文档`, `准备 v0.2` | create or update `docs/milestones/v0.2-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| `开发 vX.Y`, `实现 vX.Y`, `继续 vX.Y`, `/goal 开发 vX.Y` | matching `docs/milestones/vX.Y-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| `审核 vX.Y`, `review vX.Y`, `检查 vX.Y` | matching `docs/milestones/vX.Y-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md`, current git diff |
| `修改技术栈`, `为什么选 <technology>`, `架构决策` | `docs/adr/` | relevant ADR, or create a new ADR before changing architecture |
| `更新总体设计`, `修改产品边界`, `改验证客户端设计` | `docs/specs/validation-client-design.zh.md` | design spec plus affected milestone docs |

For versions not listed above, route to the matching directory under
`docs/milestones/`. If the directory or plan does not exist, stop and create or
request milestone documentation before implementation.

## Milestone Documentation Standard

Every milestone must have detailed but lightweight documents before
implementation starts:

- `README.zh.md`: status, goal, scope, non-goals, and entry rules.
- `plan.zh.md`: numbered tasks, files, verification commands, and expected
  commit boundaries.
- `review.zh.md`: task records, command results, scope review, and final
  assessment.

Before implementation, `review.zh.md` may say `待实现` or `计划完成 / 待实现`.
It must not say `已实现`, `完成`, or `complete` until the completion gate is
satisfied.

If implementation reveals that `plan.zh.md` is wrong or incomplete, stop,
update the milestone documents, and resume only after the updated scope is
clear. Do not silently improvise around the plan.

## Hard Execution Rules

These rules are mandatory. Do not treat them as suggestions.

1. Execute milestone work strictly in `plan.zh.md` task order.
2. Work on only one numbered task at a time.
3. Do not start the next task until the current task is implemented, verified,
   recorded, and committed.
4. Every numbered task must have its own commit, unless the user explicitly
   approves combining tasks before implementation.
5. Each task commit must include only files required for that task.
6. Do not mark a milestone as `已实现`, `完成`, `complete`, or equivalent while
   related implementation files remain unstaged or uncommitted.
7. Do not update `review.zh.md` with a pass/completion claim before the
   corresponding implementation and verification have actually happened.
8. Do not skip a planned verification command. If a command cannot run, record
   it as blocked with the exact reason.
9. Do not continue after a failing required check unless the next work is a
   narrow fix for that failure.
10. Do not widen scope to future milestones while implementing the active
    milestone.

## Required Task Loop

For every numbered task in `plan.zh.md`, follow this loop:

1. Read the task scope and file list.
2. Check the working tree with `git status --short --branch`.
3. Implement only that task.
4. Run the task-specific verification command listed in `plan.zh.md`.
5. Run `git diff --check`.
6. Update `review.zh.md` with the task record.
7. Stage only the files for this task.
8. Commit with a task-scoped message.
9. Confirm the working tree has no uncommitted changes for that task.
10. Move to the next task only after the commit succeeds.

If any step fails, stop and report the blocker. Do not silently continue.

## Review Record Requirements

`review.zh.md` must track task-level evidence. Use this shape:

```markdown
## Task Records

### Task 1: <name>

- Commit: `<hash>`
- Files:
  - `<path>`
- Commands:
  - `<command>`: `<result>`
- Scope review:
  - `<brief result>`
- Notes:
  - `<remaining issue or none>`
```

The final milestone assessment may be set to complete only after all planned
task records are present, all required checks pass, and the working tree has
no uncommitted milestone changes.

## Commit Discipline

Use small commits. A good v0.1 implementation should naturally produce commits
like:

```text
chore: scaffold validation client workspace
feat: add FastAPI backend foundation
feat: add session and timeline storage models
feat: add WorldEngine connection check
feat: add session and branch APIs
feat: add evidence bundle metadata endpoint
feat: add React frontend foundation
feat: add session library UI
feat: add runtime console shell
docs: complete v0.1 foundation review
```

Do not make one large commit for an entire milestone unless the user
explicitly requests it.

## Testing Discipline

A task may claim pass only for commands that ran in the current work session.

For v0.1, expected commands include:

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
git diff --check
```

Focused task checks should run before broader milestone checks.

If sandboxing prevents a command from running, retry with the appropriate
approval request. If it still cannot run, record the command as blocked rather
than passed.

## Scope Boundaries

The validation client is allowed to store local client evidence:

- sessions
- timeline branches
- commit points
- public events
- state diffs
- snapshots
- director intents
- redacted API traces
- evidence bundle metadata

The validation client must not store or expose:

- LLM API keys
- provider secrets
- private prompts
- private evaluator oracle internals
- private WorldEngine internals
- private WorldEngine file paths
- non-public event payloads

## Timeline And Branch Semantics

Timeline branches are modeled like code branches.

- A reconstructable tick or event point is a `commit point`.
- A branch is a named world line.
- A branch can continue from a selected commit point.
- Branches do not imply parent-child ownership.
- Do not introduce `parent timeline`, `child timeline`, or hierarchy language
  into the data model or documentation.

## Dirty Worktree Safety

The working tree may contain user or agent changes.

Before editing, inspect `git status --short --branch`.

Never revert or overwrite changes you did not make unless the user explicitly
asks. If unrelated changes exist, ignore them. If they affect the active task,
work with them or stop and ask for direction.

When committing, stage only the files that belong to the current task.

## Milestone Completion Gate

A milestone is complete only when all are true:

- every planned task is implemented or explicitly deferred with rationale
- every task has a task record in `review.zh.md`
- every task has a task-scoped commit
- required focused checks pass
- required broad checks pass
- `git diff --check` passes
- `review.zh.md` records changed files, commands, results, scope review, and
  remaining issues
- no related milestone changes remain uncommitted

If any condition is missing, report the milestone as partial or in progress,
not complete.
