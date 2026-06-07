# Autonomous Validation Runbook

Chinese mirror: `autonomous-validation-runbook.zh.md`.

Run preflight, start WorldEngine, Validation Client API, and web UI, execute the
selected bounded scenario flow, export the evidence bundle, optionally export a
checker-compatible saved-result directory, run the WorldEngine checker when
supported, run second-Agent review, and write the validation run report.

Allowed conclusions are `PASS_READY_FOR_HUMAN_VALIDATION`, `PARTIAL`, `BLOCKED`,
and `FAIL`.
