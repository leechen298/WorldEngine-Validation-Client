# Autonomous Validation Runbook

Chinese mirror: `autonomous-validation-runbook.zh.md`.

Run preflight, start WorldEngine, Validation Client API, and web UI, execute the
selected bounded scenario flow, export the evidence bundle, export the v0.8
checker handoff directory, run the WorldEngine checker only when that directory
exists and the checker supports the contract, run second-Agent review, and write
the validation run report.

```bash
VALIDATION_CLIENT_E2E_OUTPUT_DIR=../../docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/validation-runs/playwright-artifacts \
VALIDATION_CLIENT_API_BASE=http://127.0.0.1:8765 \
VALIDATION_CLIENT_SCENARIO=worldengine-full-lifecycle-autonomous \
pnpm --dir apps/web test:e2e
```

The `checker-handoff/` directory under the Playwright output is a client
evidence directory. `manifest.json`, `result.json`, `redaction-scan.json`,
`scorecard-summary.json`, and `operation-log.jsonl` must preserve `blocked`,
`fail`, or `not_run`; the client must not rewrite them to PASS.

Allowed conclusions are `PASS_READY_FOR_HUMAN_VALIDATION`, `PARTIAL`, `BLOCKED`,
and `FAIL`.
