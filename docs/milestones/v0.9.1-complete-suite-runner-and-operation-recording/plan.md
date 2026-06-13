# Plan

Chinese mirror: `plan.zh.md`.

## Task 1: E2E Operation Recorder

Candidate files:

```text
apps/web/e2e/support/operationRecorder.ts
apps/web/e2e/support/operationRecorder.test.ts
```

Requirements:

- Provide helpers such as `recordOperation`, `recordApiCall`,
  `recordScreenshot`, and `writeTranscript`.
- Generate `operation-log.jsonl` and `api-log.jsonl` matching the v0.9
  operation recording contract.
- Support blocked operation records.
- Never record secrets, authorization headers, raw prompts, raw provider
  responses, private memory, or raw thought.

## Task 2: Complete Suite Blocked Result Exporter

Candidate files:

```text
apps/web/e2e/support/completeSuiteResult.ts
apps/web/e2e/support/completeSuiteResult.test.ts
```

Requirements:

- Assemble required result-directory artifacts.
- Emit structured `BLOCKED` when WorldEngine is unreachable or capability is
  missing.
- Include operation log, API log, API summary, console log, transcript, and
  screenshot placeholders/status even on blocked paths.

## Task 3: Complete Suite E2E Runner

Candidate file:

```text
apps/web/e2e/complete-worldengine-validation-suite.spec.ts
```

Requirements:

- Execute Phase 1-4 following the v0.9 operation script.
- Record concrete clicks, inputs, waits, downloads, and screenshots.
- Keep direct API harvest in `api-log.jsonl`, not user operation logs.
- Support PASS / PARTIAL / BLOCKED / FAIL outputs.

## Task 4: Docs/Review Closeout

Update review and routing docs. Do not claim WorldEngine PASS unless a real
checker/scorecard run passed. The test plan must cover E2E, Agent autonomous
operations, per-step records, result directory, second-Agent review, and
FAIL/BLOCKED taxonomy.
