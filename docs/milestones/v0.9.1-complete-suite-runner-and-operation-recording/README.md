# v0.9.1 Complete Suite Runner And Operation Recording

Chinese mirror: `README.zh.md`.

Status: implementation package drafted / ready for user approval
implementation_authorized: no
external_validation_authorized: no
provider_live_call_authorized: no

## Goal

Turn the v0.9 phased validation documents into executable client behavior:

```text
Agent runs complete-worldengine-validation-suite through concrete UI steps and
persists detailed records for every operation.
```

## Scope

- Add a `complete-worldengine-validation-suite` E2E runner.
- Execute Phase 1-4 following the v0.9 operation script.
- Write every Playwright UI action to `operation-log.jsonl`.
- Write every Validation Client / WorldEngine API request summary to
  `api-log.jsonl`.
- Generate `api-summary.json`.
- Save phase screenshots and key before/after screenshots.
- Save `console.log`.
- Save `transcript.md`.
- Export or assemble a suite-level result directory.
- Emit structured `BLOCKED` evidence when WorldEngine capabilities are missing.

## Complete Test Plan Files

```text
test-plan.zh.md
scenario-assertion-matrix.zh.md
result-directory-contract.zh.md
validation.zh.md
agent-execution-handoff.zh.md
```

Together these files define test layers, per-step assertions, result-directory
schema, verdict rules, and copy-ready implementation/validation prompts.

## Non-Goals

- No direct LLM provider calls.
- No provider key management.
- No authoritative WorldEngine fact generation.
- No direct Agent memory/goal/thought/identity/hidden-context writes.
- No UI-smoke-as-PASS behavior.
- No implementation of missing WorldEngine public capabilities.
