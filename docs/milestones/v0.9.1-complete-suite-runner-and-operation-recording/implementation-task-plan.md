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

## Recording Completeness Requirements

After implementation, any full suite result directory must prove:

- every executed `step_id` exists in `operation-log.jsonl`;
- every API request exists in `api-log.jsonl` or has an explicit no-API reason;
- `api-summary.json` aggregates requests, failures, blocked capability calls,
  and redaction by phase;
- `console.log` exists;
- `transcript.md` exists and covers Phase 1-4;
- every phase has screenshots or blocked screenshot status.

## Pre-Implementation Audit Requirement

Before implementation, read:

```text
implementation-readiness-audit.md
```

Then follow the audit conclusions:

- the first runner treats Playwright result-directory rich artifacts as the
  evidence authority;
- the older backend operation-log endpoint is supplemental evidence only;
- direct API harvest must be written to `api-log.jsonl`, never disguised as a
  user operation;
- when a WorldEngine capability is missing, continue closeout and output a
  structured `BLOCKED` result directory instead of failing mid-run and losing
  evidence.
