# Intent

Chinese mirror: `intent.zh.md`.

v0.8 makes the Validation Client evolve with WorldEngine validation contracts.
It is a repeatable external-client optimization pattern rather than a one-off
compatibility patch.

For WorldEngine v0.9:

- LLM-backed lifecycle validation cannot rely on UI smoke alone.
- `BLOCKED`, `not_run`, and checker-valid blocked results are real outcomes and
  must not be rewritten.
- Artifact names, manifest fields, scorecard items, and redaction flags must be
  reviewable by a second Agent or WorldEngine checker.
- Direct API harvest must be recorded separately from user-visible operations.

The output should let Codex, a second Agent, and humans distinguish client
availability, public evidence completeness, checker acceptance, and exact
provider/runner/schema/artifact/redaction gaps.
