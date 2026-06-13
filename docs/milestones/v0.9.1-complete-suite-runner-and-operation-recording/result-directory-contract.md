# Result Directory Contract

Chinese mirror: `result-directory-contract.zh.md`.

The result directory must be:

```text
validation-runs/<timestamp>-complete-worldengine-validation-suite/
```

The Chinese mirror defines the authoritative required tree and JSON field
contracts.

Even when WorldEngine is unreachable, the runner must generate a structured
`BLOCKED` directory containing at least `result.json`, `coverage-matrix.json`,
`operation-log.jsonl`, `api-log.jsonl`, `api-summary.json`,
`capability-discovery.json`, `redaction-report.json`, `console.log`,
`transcript.md`, and blocked screenshot evidence/status.

