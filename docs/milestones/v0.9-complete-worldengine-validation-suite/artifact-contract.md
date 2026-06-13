# Artifact Contract

Chinese mirror: `artifact-contract.zh.md`.

## Result Directory

Recommended output:

```text
validation-runs/<timestamp>-complete-worldengine-validation-suite/
```

## Required Files

```text
result.json
coverage-matrix.json
command-matrix.md
operation-log.jsonl
api-log.jsonl
api-summary.json
capability-discovery.json
world-creation-summary.json
session-summary.json
runtime-control-summary.json
timeline-evidence.json
direction-boundary-summary.json
agent-evidence.json
memory-continuity-summary.json
inspection-evidence.json
scorecard-input.json
redaction-report.json
console.log
transcript.md
second-agent-review.md
screenshots/
```

Compatibility artifacts such as `world-lifecycle-summary.json`,
`diff-replay-summary.json`, `scorecard-summary.json`, and
`redaction-scan.json` may be generated for current WorldEngine checkers, but
they do not replace the suite-level required files.
