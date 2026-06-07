# Contract

Chinese mirror: `contract.zh.md`.

## Client Role

- `client_role`: `display_export_only`
- `provider_owner`: `worldengine`
- `evaluator_role`: `worldengine_checker_or_second_agent_review`

The Validation Client may display, record, and export public evidence. It does
not own provider calls, evaluator authority, PASS decisions, or canonical world
state.

## Status Values

Exported data must preserve:

- `pass`
- `fail`
- `blocked`
- `not_run`
- `out_of_scope`, only when the scenario contract allows it

Missing, malformed, blocked, or not-run required artifacts must never be mapped
to PASS.

## Public Surfaces

v0.8 discovery should recognize WorldEngine public surfaces listed in
`contract.zh.md`. Missing surfaces are recorded as `blocked` or `not_run`.

## Boundary

The client must not expose raw prompts, raw provider requests/responses,
provider traces, authorization headers, API keys, Agent private memory/goals,
raw thought, hidden context, private evaluator data, seed, or oracle data.
