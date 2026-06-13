# Plan

Chinese mirror: `plan.zh.md`.

## Task 1: Routing And Product Framing

Candidate files:

```text
AGENTS.md
AGENTS.zh.md
docs/README.zh.md
docs/roadmap.zh.md
docs/agent-guides/routing.md
docs/agent-guides/routing.zh.md
```

Requirements:

- Point the active milestone to `v0.9-complete-worldengine-validation-suite`.
- Stop implying that the client mirrors every WorldEngine iteration.
- Make v0.9 one complete suite with deeper internal layers.

## Task 2: Phased Validation Documents

Candidate files:

```text
docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-plan.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-runbook.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/agent-autonomous-operation-script.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/operation-recording-contract.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/scenario-matrix.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/artifact-contract.zh.md
```

Requirements:

- Define the `complete-worldengine-validation-suite` main scenario.
- Define Phase 1-4 validation.
- Define L0-L8 layers and phase mapping.
- Define required artifacts, compatibility artifacts, and redaction rules.
- Define concrete Agent autonomous UI steps, including buttons, inputs,
  downloads, and screenshots.
- Define the per-operation recording contract for `operation-log.jsonl`,
  `api-log.jsonl`, `console.log`, `transcript.md`, and screenshots.

## Task 3: Future Implementation Constraints

Candidate files:

```text
docs/milestones/v0.9-complete-worldengine-validation-suite/implementation-task-plan.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/validation.zh.md
```

Requirements:

- State that current v0.9 is a documentation iteration.
- Defer API adapter, UI controls, evidence exporter, and E2E changes to future
  implementation.
- Keep direct API harvest in `api-log.jsonl` / `api-summary.json`, not in the
  user operation log.

## Task 4: Documentation Verification And Review

Requirements:

- Routing can find this milestone.
- Documents no longer imply following every WorldEngine iteration.
- Status remains `implementation_authorized: no`.
- Review records this pass as documentation-only.

## Verification Commands

Documentation phase:

```bash
git diff --check
rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs
```

## Stop Rules

- If only UI smoke proves a result, do not mark PASS.
- If a WorldEngine public capability is missing, record
  `blocked/capability_gap`.
- If the client needs provider keys or raw prompts/raw responses, stop and FAIL.
- If redaction is blocked, fix redaction first.
