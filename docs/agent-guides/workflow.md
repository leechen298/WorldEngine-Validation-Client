# Milestone Execution Workflow

Chinese mirror: `workflow.zh.md`.

This workflow is strict. It exists to prevent agents from completing an entire
milestone as one unreviewable batch.

Validation requests are routed through `validation-workflow.md`. Do not use the
implementation task loop as a substitute for autonomous validation, Agent
review, or human validation handoff.

## Hard Execution Rules

1. Execute milestone work strictly in `plan.zh.md` task order.
2. Work on only one numbered task at a time.
3. Do not start the next task until the current task is implemented, verified,
   recorded, and committed.
4. Every numbered task must have its own commit, unless the user explicitly
   approves combining tasks before implementation.
5. Each task commit must include only files required for that task.
6. Do not mark a milestone as implemented, complete, or equivalent while
   related implementation files remain unstaged or uncommitted.
7. Do not update `review.zh.md` with a pass or completion claim before the
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
task records are present, all required checks pass, and the working tree has no
uncommitted milestone changes.

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

Do not make one large commit for an entire milestone unless the user explicitly
requests it.

## Branch Publishing Discipline

Branches ending in `-local` are local-only working branches.

Never push a `*-local` branch. If local-only work must be shared, first merge or
replay its patch-equivalent commits onto the matching non-local target branch,
then verify equivalence with `git cherry`, `git range-diff`, and an empty
bidirectional diff.

Push only the non-local target branch, and only when the user explicitly asks
for a push.

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
