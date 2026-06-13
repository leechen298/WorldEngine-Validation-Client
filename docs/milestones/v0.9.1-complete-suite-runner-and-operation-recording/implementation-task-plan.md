# Implementation Task Plan

Chinese mirror: `implementation-task-plan.zh.md`.

## Boundary

This is an implementation package, but it is not yet authorized:

```text
implementation_authorized: no
```

After explicit approval, execute Task 1-4 from `plan.zh.md` in order. Each task
needs focused verification and a task-scoped commit.

## RED/GREEN Requirements

- Task 1: write recorder focused tests, confirm RED, then implement helpers.
- Task 2: write result exporter focused tests, confirm RED, then implement
  exporter.
- Task 3: write or adjust E2E expectation, confirm the suite runner is missing,
  then implement it.
- Task 4: docs closeout only.

