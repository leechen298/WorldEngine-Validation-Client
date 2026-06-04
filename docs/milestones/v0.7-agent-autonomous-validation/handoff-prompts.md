# v0.7 Handoff Prompts

Chinese mirror: `handoff-prompts.zh.md`.

This file contains `/goal` prompts that future chats can use directly. Before
using them, the new chat must still read this milestone's `README.zh.md`,
`validation.zh.md`, `implementation-task-plan.zh.md`, and
`codex-autonomous-validation-master-plan.zh.md`, plus
`planning-readiness-checklist.zh.md`.

For a shorter copy-ready entry, use:

```text
docs/milestones/v0.7-agent-autonomous-validation/next-chat-quickstart.zh.md
```

Full cross-repository gates:

```text
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
```

## 0. Current Short Conclusion

Do not enter human validation yet.

Measured blockers:

- WorldEngine can start. `/health` and `/openapi.json` are reachable.
- WorldEngine currently lacks `/manifest`.
- WorldEngine OpenAPI currently lacks a Validation Client-discoverable world
  creation endpoint.
- Validation Client `POST /sessions/worldengine` currently returns 502:
  `WorldEngine public world creation endpoint not found`.

Required sequence:

1. Fix WorldEngine public contract first.
2. Develop Validation Client v0.7 operation log / autonomous validation.
3. Run Codex autonomous validation.
4. Run second Agent read-only review.
5. Enter human validation.

## 1. WorldEngine Development Chat Prompt

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
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/external-validation-gate-matrix.zh.md
- docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/implementation-handoff-prompt.zh.md

Goals:
- Add or implement GET /manifest returning a redacted public readiness document.
- Add an OpenAPI-discoverable public world creation endpoint, preferably POST /worlds.
- world creation response must include public world_id, status, public state, and visualization.
- If feasible, add POST /worlds/{world_id}/director-guidance.
- Provider readiness may expose only provider class, readiness, credential source class, and public model label. Do not expose keys, private prompts, or provider raw traces.

Boundaries:
- Do not implement Validation Client.
- Do not add concrete demo-world content.
- Do not put external validator behavior into WorldEngine.
- Do not expose keys, private prompts, provider raw traces, or private Agent state.
- Do not reopen v0.8 final closeout. 0.8.9 is a post-closeout addendum.

Verification:
- cd backend && .venv/bin/python -m pytest app/tests -q
- git diff --check
- Start WorldEngine and curl /health, /manifest, /openapi.json, and POST /worlds.
- Start Validation Client API and confirm /health/worldengine reports world_creation: available.
- Confirm Validation Client POST /sessions/worldengine succeeds.

Completion:
- Record review.zh.md.
- Conclusion may only say WorldEngine contract is ready for Validation Client autonomous validation.
- Do not claim external validation PASS or human validation PASS.
```

## 2. Validation Client Development Chat Prompt

```text
/goal Develop v0.7 Agent Autonomous Validation.

Read first:
- AGENTS.zh.md
- docs/README.zh.md
- docs/specs/validation-client-design.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
- docs/agent-guides/routing.zh.md
- docs/agent-guides/workflow.zh.md
- docs/agent-guides/validation-workflow.zh.md
- docs/agent-guides/boundaries.zh.md

Goals:
- Implement Agent operation log JSONL.
- Implement browser E2E / UI smoke or an equivalent runnable autonomous validation path.
- Save screenshots, API summaries, and downloaded artifacts.
- Associate the evidence bundle with the current run/session.
- Provide Codex run report, second Agent review report, and human validation handoff templates.

Boundaries:
- The client does not manage LLM keys.
- The client does not directly call providers.
- The client does not produce authoritative evaluator PASS.
- Do not record private prompts, provider raw traces, Agent private memory, private goals, self_state, or hidden_context.

Verification:
- pnpm run test
- pnpm run build
- git diff --check
- Sensitive-term scan must be classified and recorded.
- If Playwright is added, run E2E and save artifacts.

Completion:
- review.zh.md records each task, command, result, and unresolved issue.
- Do not claim human validation passed.
```

## 3. Codex Autonomous Validation Chat Prompt

```text
/goal Autonomously validate v0.7.

Read first:
- docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
- docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
- docs/agent-guides/validation-workflow.zh.md

Follow autonomous-validation-runbook.zh.md. Preflight:
- Confirm WorldEngine /manifest is reachable.
- Confirm WorldEngine OpenAPI exposes a discoverable world creation endpoint.
- Confirm Validation Client /health/worldengine reports world_creation: available.
- Confirm Validation Client POST /sessions/worldengine succeeds.

Then start:
- WorldEngine backend.
- Validation Client API.
- Validation Client Web.

Use the browser to run the full flow:
- Open session library.
- Create WorldEngine session.
- Enter runtime console.
- Inspect pixel canvas, public state, Agent public state, World Log, and Agent Life Log.
- Submit high-level director guidance.
- Use replay slider.
- Create branch from a commit point.
- Download evidence bundle.

Must produce:
- validation-runs/YYYY-MM-DD-codex/agent-run.jsonl
- validation-runs/YYYY-MM-DD-codex/codex.zh.md
- screenshots/
- downloads/evidence-bundle.json
- api-summary.json

Conclusion may only be:
- PASS_READY_FOR_HUMAN_VALIDATION
- PARTIAL
- BLOCKED
- FAIL

Do not claim world experience pass or human validation pass.
```

## 4. Second Agent Review Chat Prompt

```text
/goal Review v0.7 Codex autonomous validation evidence.

Read-only inputs:
- Latest validation-runs/YYYY-MM-DD-codex/codex.zh.md
- Latest validation-runs/YYYY-MM-DD-codex/agent-run.jsonl
- screenshots/
- downloads/evidence-bundle.json
- api-summary.json
- docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md

Check:
- Did Codex follow the plan?
- Does the operation log cover key steps?
- Do API summaries correspond to visible UI state?
- Does the evidence bundle match the session/run?
- Are redaction flags and sensitive scans clean?
- Is the Codex conclusion limited to ready for human validation?

Output:
- validation-runs/YYYY-MM-DD-agent-review.zh.md

Conclusion may only be:
- READY_FOR_HUMAN_VALIDATION
- PARTIAL
- BLOCKED
- FAIL

Do not operate the browser, do not invent unrecorded facts, and do not replace human experience judgment.
```

## 5. Human Validation Chat Prompt

```text
/goal Human-validate v0.7.

Read first:
- Latest Codex autonomous validation run.
- Latest second Agent review report.
- screenshots/
- evidence-bundle.json.
- docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md.

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

## 6. One-Line Sequence

```text
WorldEngine contract -> Validation Client v0.7 operation log/E2E -> Codex autonomous run -> second Agent review -> human validation
```
