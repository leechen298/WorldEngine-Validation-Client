# v0.7 Planning Readiness Checklist

Chinese mirror: `planning-readiness-checklist.zh.md`.

Status: PLAN_READY

Purpose: prove that v0.7 Codex autonomous validation to human validation
planning documents are ready for future execution chats. This document does
not prove v0.7 implementation, Codex autonomous validation pass, or human
validation pass.

## 0. Conclusion

```text
PLAN_READY
```

Reason:

```text
Validation Client v0.7 and WorldEngine 0.8.9 now have cross-repository gates,
implementation tasks, execution runbook, report templates, and future-chat
prompts. The next step is WorldEngine Gate 1 contract implementation.
```

## 1. Allowed Next Step

Only allowed next step:

```text
Implement the WorldEngine 0.8.9 public handoff manifest and world creation contract.
```

Not allowed:

- Start Validation Client v0.7 implementation.
- Start Codex browser autonomous validation.
- Start second-Agent review.
- Start human validation.
- Claim v0.7 validation passed.

Reason:

- WorldEngine currently lacks `/manifest`.
- WorldEngine currently lacks a Validation Client-discoverable world creation
  endpoint.
- Validation Client currently cannot create a WorldEngine-backed session.

## 2. Required Documents

Validation Client documents:

```text
README.zh.md
plan.zh.md
implementation-task-plan.zh.md
codex-autonomous-validation-master-plan.zh.md
cross-repo-validation-gate-matrix.zh.md
autonomous-validation-runbook.zh.md
next-chat-quickstart.zh.md
handoff-prompts.zh.md
codex-run-report-template.zh.md
agent-review-template.zh.md
human-validation-template.zh.md
validation.zh.md
review.zh.md
planning-readiness-checklist.zh.md
```

WorldEngine documents:

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/README.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/technical-design.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/test-plan.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-task-plan.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/validation-client-contract-handoff.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/external-validation-gate-matrix.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-handoff-prompt.zh.md
```

## 3. Coverage

The plan covers:

- WorldEngine public contract readiness.
- LLM provider and API key ownership by WorldEngine.
- no direct provider calls from Validation Client.
- evaluator conclusions owned by WorldEngine.
- Codex operating the Web client from a human viewpoint.
- operation logs for user actions, API summaries, screenshots, downloads, and
  evidence bundles.
- lightweight event/diff for each tick/event.
- periodic snapshots.
- forward diff application from nearest snapshot to a commit point.
- branches as named world lines, switchable views, and progression entry
  points.
- second-Agent read-only review.
- human validation for experience and world observability.
- automated conclusions never replacing `HUMAN_PASS`.

## 4. Incomplete Work

Not complete:

- WorldEngine 0.8.9 implementation.
- Validation Client v0.7 implementation.
- Codex autonomous validation run.
- second-Agent read-only review.
- human validation.
- commit / push.

## 5. Stop Rules

Future chats must stop and record a non-ready conclusion if:

- WorldEngine still lacks `/manifest`.
- WorldEngine OpenAPI still lacks a discoverable world creation endpoint.
- Validation Client `POST /sessions/worldengine` still fails.
- Validation Client needs to manage LLM keys.
- Validation Client needs to call an LLM provider directly.
- evidence leaks keys, private prompts, provider raw traces, or Agent private
  state.
- operation logs cannot support human-viewpoint review.
- Codex or the second Agent claims human validation passed.

## 6. Recommended Future Chat

Copy from:

```text
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
```

Current handoff status:

```text
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
```

The first future chat must run in the WorldEngine repository:

```text
/goal Implement 0.8.9-external-validation-provider-and-handoff-manifest public handoff manifest and world creation contract.
```

Only proceed to Validation Client v0.7 implementation after WorldEngine writes
`WORLDENGINE_CONTRACT_READY`.
