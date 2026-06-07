# Artifact Contract

Chinese mirror: `artifact-contract.zh.md`.

The v0.8 evidence bundle uses named, scenario-aware artifacts. Only artifacts
required by the active scenario are mandatory, but missing required artifacts
must be exported as `blocked`, `not_run`, or `fail`.

`manifest.json` must include schema, bundle id, scenario, result status,
client/provider/evaluator roles, artifact index, redaction status, checker
contract, and unsupported items.

Each artifact index entry must include name, bundle-relative path, required,
displayable, exportable, producer, schema version, status, and redaction
status. Absolute paths and path traversal are forbidden.
