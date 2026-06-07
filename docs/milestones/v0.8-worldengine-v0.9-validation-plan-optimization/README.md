# v0.8 WorldEngine v0.9 Validation Plan Optimization

Chinese mirror: `README.zh.md`.

Status: documentation self-review in progress / implementation authorized after documentation

## Goal

v0.8 upgrades the Validation Client from the v0.7 autonomous-validation carrier
into a repeatable WorldEngine validation-plan optimization surface. It aligns
the client with WorldEngine v0.9 public scenarios, artifacts, scorecards,
checkers, and second-Agent review contracts.

The client remains an external evidence carrier. PASS authority remains with
WorldEngine checker/scorecard output and second-Agent review.

## Scope

- Create the v0.8 milestone package, scenario operation matrix, artifact
  contract, redaction matrix, runbook, and second-Agent template.
- Refresh v0.8 routing and stale v0.7 / WorldEngine 0.8.9 references.
- Extend WorldEngine v0.9 public surface discovery.
- Add scenario-aware evidence bundle manifest, artifact index, and named
  artifacts.
- Preserve `pass`, `fail`, `blocked`, and `not_run` without mapping blockers to
  PASS.
- Separate user-visible operation logs from direct API harvest logs.
- Add bounded runtime control support in UI and logs.
- Display checker, scorecard, second-Agent review, and redaction status without
  client-owned PASS decisions.

## Non-goals

- No direct DeepSeek or provider calls.
- No provider key storage, display, or forwarding.
- No client-generated LLM-backed world content.
- No authoritative world-rule, parameter-change, event-legality, or Agent
  autonomy evaluation in the client.
- No UI smoke result may be represented as WorldEngine validation PASS.
- Narrative projection and diagnostic dialogue remain external inspection
  surfaces, not canonical world state or Agent memory.

## Authority

WorldEngine v0.9 is the authority for validation contracts. v0.8 consumes the
current WorldEngine handoff draft:

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.9/0.9.11-validation-client-evidence-handoff-contract/validation-client-v0.8-validation-plan-optimization-handoff.md
```

That handoff is currently a WorldEngine documentation draft. This repository
only consumes the public contract and does not modify WorldEngine.

## Current Authorization

The user authorized creating v0.8 docs, completing self-review, then continuing
implementation until a validation-ready state unless a hard gate blocks.
