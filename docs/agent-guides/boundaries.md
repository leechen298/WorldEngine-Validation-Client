# Scope Boundaries

Chinese mirror: `boundaries.zh.md`.

`WorldEngine-Validation-Client` is an external validation and observation
client. It must preserve a hard boundary from WorldEngine core.

## Allowed Communication

The client may communicate with WorldEngine only through public interfaces:

- `WORLDENGINE_API_BASE`
- public HTTP APIs
- public schemas, manifests, and OpenAPI descriptions
- public event, state, timeline, and evaluator outputs

## Forbidden Coupling

The client must not:

- import WorldEngine source code
- depend on private WorldEngine local paths
- call WorldEngine internal helpers
- manage LLM API keys
- call LLM providers directly
- generate authoritative world facts
- directly mutate Agent memory, goals, identity, self-state, relationships, or
  actions

## Allowed Local Evidence

The validation client may store local client evidence:

- sessions
- timeline branches
- commit points
- public events
- state diffs
- snapshots
- director intents
- redacted API traces
- evidence bundle metadata

## Forbidden Stored Data

The validation client must not store or expose:

- LLM API keys
- provider secrets
- private prompts
- private evaluator oracle internals
- private WorldEngine internals
- private WorldEngine file paths
- non-public event payloads

## Timeline And Branch Semantics

Timeline branches are modeled like code branches.

- A reconstructable tick or event point is a `commit point`.
- A branch is a named world line.
- A branch can continue from a selected commit point.
- Branches do not imply parent-child ownership.
- Do not introduce `parent timeline`, `child timeline`, or hierarchy language
  into the data model or documentation.
