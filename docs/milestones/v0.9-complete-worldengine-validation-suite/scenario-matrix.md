# Scenario Matrix

Chinese mirror: `scenario-matrix.zh.md`.

## Main Scenario

```text
complete-worldengine-validation-suite
```

Other scenarios are layers or sub-scenarios of this one complete validation
suite.

## Phases And Layers

| Phase | Layers | Goal |
| --- | --- | --- |
| Phase 1 | L0, L1, L2-min, L8-min | basic functionality |
| Phase 2 | L2, L3, L4 | lifecycle validation |
| Phase 3 | L5, L6, L7 | Agent depth |
| Phase 4 | L8, checker/review | autonomous closeout |

## Layer Details

| ID | Sub-scenario | Required artifact |
| --- | --- | --- |
| L0 | `preflight-capability-discovery` | `capability-discovery.json` |
| L1 | `world-creation` | `world-creation-summary.json`, `session-summary.json` |
| L2 | `runtime-control` | `runtime-control-summary.json`, `api-log.jsonl` |
| L3 | `timeline-evidence` | `timeline-evidence.json` |
| L4 | `direction-boundary` | `direction-boundary-summary.json` |
| L5 | `agent-life` | `agent-evidence.json` |
| L6 | `memory-continuity` | `memory-continuity-summary.json` |
| L7 | `inspection-surfaces` | `inspection-evidence.json` |
| L8 | `evidence-handoff` | `result.json`, `scorecard-input.json`, `redaction-report.json` |
