# Technical Design

Chinese mirror: `technical-design.zh.md`.

v0.8 reuses the v0.7 session, validation-run, operation-log, evidence-bundle,
and E2E foundation. It adds a v0.9 scenario-aware packaging layer.

Main modules:

- `worldengine_client.py`: discover v0.9 public surfaces and produce a
  capability model.
- `routes/evidence.py`: export v0.9 manifest, artifact index, and named
  artifacts.
- `routes/validation_runs.py`: persist operation logs and direct API harvest
  logs.
- `RuntimeConsole.tsx`: display bounded controls, artifact status,
  checker/scorecard, and second-Agent review.
- `api/types.ts` and `api/client.ts`: carry v0.9 evidence bundle types.

The core data flow separates visible operations, direct API harvest, scenario
artifact generation, redaction scanning, and checker/second-Agent verdict
display.
