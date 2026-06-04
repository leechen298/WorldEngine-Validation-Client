# v0.7 Next Chat Quickstart

Chinese mirror: `next-chat-quickstart.zh.md`.

Use this file in future chats. It provides execution order and copy-ready
prompts only. It does not replace `autonomous-validation-runbook.zh.md`,
report templates, or review evidence.

## Current State

Do not enter human validation yet.

Known blockers:

- WorldEngine currently lacks `/manifest`.
- WorldEngine currently lacks a Validation Client-discoverable world creation
  endpoint.
- Validation Client `POST /sessions/worldengine` currently fails because no
  WorldEngine public world creation endpoint is found.

Proceed in this order.

The full cross-repository gate reference is:

```text
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
```

## Step 1: WorldEngine contract implementation

Open a new chat in the WorldEngine repository:

```text
/goal Implement 0.8.9-external-validation-provider-and-handoff-manifest public handoff manifest and world creation contract.

Read first:
- AGENTS.md
- docs/project-north-star.md
- docs/product-model.md
- docs/scope-boundaries.md
- docs/roadmap.md
- docs/iterations/README.md
- docs/iterations/AGENTS.md
- docs/iterations/v0.8/README.zh.md
- docs/iterations/v0.8/CURRENT_STATE.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/README.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/technical-design.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/validation-client-contract-handoff.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-task-plan.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-handoff-prompt.zh.md

Goals:
- Implement GET /manifest.
- Implement OpenAPI-discoverable POST /worlds.
- If feasible, implement POST /worlds/{world_id}/director-guidance.
- Expose provider readiness as redacted public summary only.
- Use contract-readiness-checklist.zh.md to record WORLDENGINE_CONTRACT_READY or blocker reason.

Do not:
- Modify the Validation Client repository.
- Add concrete demo-world content.
- Expose keys, private prompts, provider raw traces, or private Agent state.
- Claim external validation PASS or human validation PASS.
```

Only proceed to Step 2 after WorldEngine reaches `WORLDENGINE_CONTRACT_READY`.

## Step 2: Validation Client v0.7 implementation

Open a new chat in the Validation Client repository:

```text
/goal Develop v0.7 Agent Autonomous Validation.

Read first:
- AGENTS.zh.md
- docs/README.zh.md
- docs/specs/validation-client-design.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
- docs/agent-guides/routing.zh.md
- docs/agent-guides/workflow.zh.md
- docs/agent-guides/validation-workflow.zh.md
- docs/agent-guides/boundaries.zh.md

Goals:
- Implement Agent operation log JSONL.
- Implement runnable browser E2E / UI smoke or equivalent autonomous validation path.
- Save screenshots, api-summary, and downloads/evidence-bundle.json.
- Associate evidence bundle with this run/session.
- Record task commands, results, and unresolved issues in review.zh.md.

Do not:
- Manage LLM keys.
- Call providers directly.
- Produce authoritative evaluator PASS.
- Record private prompts, provider raw traces, Agent private memory, private goals, self_state, or hidden_context.
```

Only proceed to Step 3 after v0.7 implementation and review evidence are done.

## Step 3: Codex autonomous validation

Open a new chat in the Validation Client repository:

```text
/goal Autonomously validate v0.7.

Read first:
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
- docs/agent-guides/validation-workflow.zh.md
- /Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md

Follow autonomous-validation-runbook.zh.md:
- Start WorldEngine, Validation Client API, and Validation Client Web.
- Run public contract preflight.
- Run tests and builds.
- Complete the full UI flow in a browser.
- Produce validation-runs/YYYY-MM-DD-codex/agent-run.jsonl.
- Produce validation-runs/YYYY-MM-DD-codex/codex.zh.md.
- Produce screenshots/, api-summary.json, and downloads/evidence-bundle.json.

Conclusion may only be:
- PASS_READY_FOR_HUMAN_VALIDATION
- PARTIAL
- BLOCKED
- FAIL

Do not claim human validation passed.
```

Only proceed to Step 4 after Codex concludes `PASS_READY_FOR_HUMAN_VALIDATION`.

## Step 4: Second Agent read-only review

Open a new chat or use another Agent:

```text
/goal Review v0.7 Codex autonomous validation evidence.

Read-only inputs:
- latest validation-runs/YYYY-MM-DD-codex/codex.zh.md
- latest validation-runs/YYYY-MM-DD-codex/agent-run.jsonl
- latest validation-runs/YYYY-MM-DD-codex/api-summary.json
- latest validation-runs/YYYY-MM-DD-codex/screenshots/
- latest validation-runs/YYYY-MM-DD-codex/downloads/evidence-bundle.json
- docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md

Read-only review:
- Did Codex follow the runbook?
- Does operation log cover key steps?
- Do screenshots cover key screens?
- Does evidence bundle match run/session?
- Is redaction scan clean?
- Did Codex avoid claiming human pass?

Output:
- validation-runs/YYYY-MM-DD-agent-review.zh.md

Conclusion may only be:
- READY_FOR_HUMAN_VALIDATION
- PARTIAL
- BLOCKED
- FAIL
```

Only proceed to Step 5 after second Agent concludes `READY_FOR_HUMAN_VALIDATION`.

## Step 5: Human validation

For human validation:

```text
/goal Human-validate v0.7.

Read first:
- latest Codex autonomous validation run.
- latest second Agent review report.
- screenshots/
- downloads/evidence-bundle.json
- docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md

Do not repeat command tests.
Judge only:
- Is the world observable?
- Do pixel canvas, event logs, and public state explain each other?
- Does Agent public state feel like natural life?
- Does director guidance remain high-level direction?
- Do replay and branch feel like world lines?
- Is the evidence bundle sufficient for replay?

Output:
- validation-runs/YYYY-MM-DD-human.zh.md

Conclusion may only be:
- HUMAN_PASS
- HUMAN_PARTIAL
- HUMAN_FAIL
```

Only a human `HUMAN_PASS` means human validation passed.
