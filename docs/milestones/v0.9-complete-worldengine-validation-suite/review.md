# Review

Chinese mirror: `review.zh.md`.

Status: documentation drafted / ready for review

## Adjustment

The previous draft incorrectly split the Validation Client path into
WorldEngine-version-following milestones. This revision defines a single
complete validation suite:

```text
v0.9-complete-worldengine-validation-suite
```

WorldEngine versions are observed through capability discovery; they do not
define the client validation structure.

After user feedback, this milestone was further narrowed to a documentation
iteration. Its goal is to deliver a complete phased validation document that
the Validation Client can later execute.

Added:

```text
phased-validation-plan.zh.md
phased-validation-plan.md
phased-validation-runbook.zh.md
phased-validation-runbook.md
```

`plan.zh.md` / `plan.md` and `implementation-task-plan.zh.md` /
`implementation-task-plan.md` now use a docs-only scope for this milestone.

The active indexes and routing documents were also updated:

```text
AGENTS.md
AGENTS.zh.md
docs/README.zh.md
docs/roadmap.zh.md
docs/agent-guides/routing.md
docs/agent-guides/routing.zh.md
```

Future requests such as `develop v0.9`, `/goal develop complete validation
suite`, or `run complete validation suite` should read this milestone's phased
plan and runbook first.

## Consistency Checks

Ran:

```text
required v0.9 files check -> missing=[] empty=[]
stale v0.10/v0.11 route scan -> no active hits
false completion / false PASS scan -> only routing rule text hit
git diff --check -> passed
```

The only false-completion scan hit is the rule text in
`docs/agent-guides/routing.zh.md` that says completion must not be claimed
before the gate is satisfied.

## Not Run

- Code tests.
- Services.
- External validation.

Reason: this pass only updates documentation scope and routing.

## Findings

- P1: none.
- P2: the client implementation still does not execute the full suite; that is
  future implementation work.
- P3: old v0.8 docs remain historical and must not be treated as the active
  flow during later implementation.

## Task Records

### Task 1: Routing And Product Framing

- Commit: `afac751`
- Files:
  - `AGENTS.md`
  - `AGENTS.zh.md`
  - `docs/README.zh.md`
  - `docs/roadmap.zh.md`
  - `docs/agent-guides/routing.md`
  - `docs/agent-guides/routing.zh.md`
- Commands:
  - `git diff --check`: `passed`
  - `rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs`: `passed; hits are expected route/suite references and historical/stop-rule text`
- Scope review:
  - Active milestone and route text now point to the complete validation suite instead of v0.8 or per-WorldEngine-iteration validation.
- Notes:
  - Documentation-only; no code tests, services, external validation, or provider live calls run.

### Task 2: Phased Validation Documents

- Commit: `2ff0c5a`
- Files:
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-plan.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-runbook.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/scenario-matrix.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/artifact-contract.zh.md`
  - English mirror files for the same documents.
- Commands:
  - `git diff --check`: `passed`
  - `rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs`: `passed; hits are expected route/suite references and historical/stop-rule text`
- Scope review:
  - Documents define one suite with Phase 1-4, L0-L8, required artifacts, compatibility outputs, and redaction rules.
- Notes:
  - Documentation-only; runtime/API/UI/E2E implementation remains future work.

### Task 3: Future Implementation Constraints

- Commit: `b7cb77b`
- Files:
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/implementation-task-plan.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/validation.zh.md`
  - English mirror files for the same documents.
- Commands:
  - `git diff --check`: `passed`
  - `rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs`: `passed; hits are expected route/suite references and historical/stop-rule text`
- Scope review:
  - Current v0.9 remains documentation-only with `implementation_authorized: no`; future implementation owns API adapter, runtime controls, exporter, and E2E changes.
- Notes:
  - Direct API harvest must remain in API logs, not user operation logs.

### Task 4: Documentation Verification And Review

- Commit: `pending`
- Files:
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/README.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/README.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/gap-analysis.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/gap-analysis.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/plan.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/plan.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/review.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/review.md`
- Commands:
  - `git diff --check`: `passed`
  - `find docs/milestones/v0.9-complete-worldengine-validation-suite -maxdepth 1 -type f | sort`: `passed; required v0.9 files present`
  - `rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs`: `passed; hits are expected route/suite references and historical/stop-rule text`
- Scope review:
  - Review records documentation-only scope, no implementation authorization, no external validation authorization, and no provider live-call authorization.
- Notes:
  - No milestone completion claim for runtime suite execution.
