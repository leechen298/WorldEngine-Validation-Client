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

Field-level requirements for `operation-log.jsonl` and `api-log.jsonl` live in
`operation-recording-contract.md`. Concrete step ids, buttons, inputs, and
screenshots live in `agent-autonomous-operation-script.md`.

## Operation Recording Requirements

`operation-log.jsonl` must cover every UI operation executed by the Agent:

- page opens;
- text fills;
- button clicks;
- selections;
- waits for visible elements or API responses;
- artifact downloads;
- screenshots;
- phase verdict records;
- blocked operations.

`api-log.jsonl` must cover every Validation Client API or WorldEngine public API
request summary. Direct API harvest must be recorded as API evidence, not as a
user click.

If any executed operation is missing a record, the complete suite cannot PASS.

Compatibility artifacts such as `world-lifecycle-summary.json`,
`diff-replay-summary.json`, `scorecard-summary.json`, and
`redaction-scan.json` may be generated for current WorldEngine checkers, but
they do not replace the suite-level required files.
