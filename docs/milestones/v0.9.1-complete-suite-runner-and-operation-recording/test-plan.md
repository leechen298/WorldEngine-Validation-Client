# Test Plan

Chinese mirror: `test-plan.zh.md`.

## Goal

Validate that v0.9.1 implements:

```text
E2E + Agent autonomous testing + complete per-operation records + reviewable result directory
```

This is not UI smoke. The Agent must operate the Validation Client as a user
and persist UI operations, API summaries, screenshots, console logs,
transcript, and result-directory artifacts.

## Layers

| Layer | Name | Purpose | Minimum conclusion |
| --- | --- | --- | --- |
| T0 | unit recorder tests | operation/API/transcript/screenshot helpers | required pass |
| T1 | blocked exporter tests | structured BLOCKED when WorldEngine is unavailable | required pass |
| T2 | E2E blocked path | runner does not fake PASS | required pass |
| T3 | E2E connected path | Phase 1-2 via real UI operations | pass or blocked with evidence |
| T4 | Agent depth path | Phase 3 Agent/memory/inspection evidence | pass or blocked with taxonomy |
| T5 | closeout path | Phase 4 result directory/redaction/checker handoff | pass or blocked with evidence |

## Required Commands

```bash
pnpm --dir apps/web test src/__tests__/operationRecorder.test.ts
pnpm --dir apps/web test src/__tests__/completeSuiteResult.test.ts
pnpm --dir apps/web test:e2e -- --grep "complete-worldengine-validation-suite"
pnpm --dir apps/web test
pnpm --dir apps/web build
git diff --check
```

If E2E emits a complete `BLOCKED` result directory because WorldEngine is
unreachable, the E2E process may pass, but the validation conclusion remains
`BLOCKED`, not `PASS`.

