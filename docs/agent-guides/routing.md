# Natural Language Routing

Chinese mirror: `routing.zh.md`.

Natural-language requests route work to milestone, spec, or ADR documents.
Routing never authorizes skipping documentation, verification, review records,
or task-level commits.

| User request | Route | Required documents |
| --- | --- | --- |
| develop v0.1, implement v0.1, continue v0.1, `/goal develop v0.1` | `docs/milestones/v0.1-foundation/` | `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| plan v0.2, create v0.2 docs, prepare v0.2 | create or update `docs/milestones/v0.2-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| develop v0.8, implement v0.8, continue v0.8, `/goal develop v0.8`, `/goal develop v0.8-worldengine-v0.9-validation-plan-optimization` | `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/` | `README.zh.md`, `plan.zh.md`, `implementation-task-plan.zh.md`, `cross-repo-validation-gate-matrix.zh.md`, `planning-readiness-checklist.zh.md`, `review.zh.md` |
| autonomous validation v0.8, Codex validation v0.8, Agent validation v0.8 | `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/` | `README.zh.md`, `plan.zh.md`, `review.zh.md`, `validation.zh.md`, `autonomous-validation-runbook.zh.md`, `codex-run-report-template.zh.md`, `second-agent-review-template.zh.md`, `agent-review-template.zh.md` |
| develop v0.9, implement v0.9, continue v0.9, `/goal develop v0.9`, `/goal develop complete validation suite` | `docs/milestones/v0.9-complete-worldengine-validation-suite/` | `README.zh.md`, `gap-analysis.zh.md`, `phased-validation-plan.zh.md`, `phased-validation-runbook.zh.md`, `agent-autonomous-operation-script.zh.md`, `operation-recording-contract.zh.md`, `scenario-matrix.zh.md`, `artifact-contract.zh.md`, `plan.zh.md`, `implementation-task-plan.zh.md`, `validation.zh.md`, `review.zh.md` |
| autonomous validation v0.9, Codex validation v0.9, Agent validation v0.9, run complete validation suite | `docs/milestones/v0.9-complete-worldengine-validation-suite/` | `README.zh.md`, `phased-validation-plan.zh.md`, `phased-validation-runbook.zh.md`, `agent-autonomous-operation-script.zh.md`, `operation-recording-contract.zh.md`, `scenario-matrix.zh.md`, `artifact-contract.zh.md`, `plan.zh.md`, `implementation-task-plan.zh.md`, `validation.zh.md`, `review.zh.md` |
| develop v0.9.1, implement v0.9.1, complete validation runner, implement complete operation recording | `docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/` | `README.zh.md`, `plan.zh.md`, `implementation-task-plan.zh.md`, `test-plan.zh.md`, `scenario-assertion-matrix.zh.md`, `result-directory-contract.zh.md`, `validation.zh.md`, `agent-execution-handoff.zh.md`, `review.zh.md` |
| develop vX.Y, implement vX.Y, continue vX.Y, `/goal develop vX.Y` | matching `docs/milestones/vX.Y-*/` | `README.zh.md`, `plan.zh.md`, `implementation-task-plan.zh.md` if present, plus `cross-repo-validation-gate-matrix.zh.md`, `planning-readiness-checklist.zh.md`, and `review.zh.md` if present |
| review vX.Y, inspect vX.Y, audit vX.Y | matching `docs/milestones/vX.Y-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md`, current git diff |
| autonomous validation vX.Y, Codex validation vX.Y, Agent validation vX.Y | matching `docs/milestones/vX.Y-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md`, `validation.zh.md`, `validation-workflow.md`, plus `cross-repo-validation-gate-matrix.zh.md`, `autonomous-validation-runbook.zh.md`, and report templates if present |
| human validation vX.Y, human review vX.Y | matching `docs/milestones/vX.Y-*/` | `validation.zh.md`, latest `validation-runs/*-codex.zh.md`, `validation-workflow.md`, plus `agent-review-template.zh.md` and `human-validation-template.zh.md` if present |
| next step vX.Y, how to start vX.Y, handoff vX.Y, quickstart vX.Y, copy prompt vX.Y | matching `docs/milestones/vX.Y-*/` | read `planning-readiness-checklist.zh.md` and `next-chat-quickstart.zh.md` first if present, then `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| change tech stack, explain a technology choice, architecture decision | `docs/adr/` | relevant ADR, or create a new ADR before changing architecture |
| update overall design, change product boundary, revise validation-client design | `docs/specs/validation-client-design.zh.md` | design spec plus affected milestone docs |

For versions not listed above, route to the matching directory under
`docs/milestones/`.

If the directory or plan does not exist, stop and create or request milestone
documentation before implementation.

## Milestone Documentation Standard

Every milestone must have detailed documents before implementation starts:

- `README.zh.md`: status, goal, scope, non-goals, and entry rules.
- `plan.zh.md`: numbered tasks, files, verification commands, and expected
  commit boundaries.
- `implementation-task-plan.zh.md`: when a milestone needs stronger execution
  constraints, records task-by-task candidate files, test focus, verification
  commands, done criteria, and stop rules.
- `review.zh.md`: task records, command results, scope review, and final
  assessment.
- `validation.zh.md`: validation plan, autonomous validation checklist, Agent
  review checklist, and human handoff checklist when the milestone includes
  validation behavior or validation claims.
- `autonomous-validation-runbook.zh.md`: when the milestone includes real Codex
  autonomous validation, records service startup, preflight, commands, browser
  flow, evidence, and stop rules.
- `cross-repo-validation-gate-matrix.zh.md`: when the milestone depends on
  WorldEngine, Validation Client, Codex, second-Agent review, and human
  validation across phases, records non-skippable gates, evidence, conclusion
  enums, and stop rules.
- `planning-readiness-checklist.zh.md`: when the milestone needs handoff to
  future chats, records current planning conclusion, only allowed next step,
  incomplete work, and stop rules.
- `next-chat-quickstart.zh.md`: when the milestone needs cross-chat handoff,
  records copy-ready staged `/goal` prompts.

Before implementation, `review.zh.md` may record that implementation is
pending. It must not claim implemented, complete, or equivalent status until
the completion gate in `workflow.md` is satisfied.

If implementation reveals that `plan.zh.md` is wrong or incomplete, stop,
update milestone documents, and resume only after the updated scope is clear.
Do not silently improvise around the plan.
