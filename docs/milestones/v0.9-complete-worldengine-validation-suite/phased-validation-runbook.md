# Phased Validation Runbook

Chinese mirror: `phased-validation-runbook.zh.md`.

## Usage

Run validation by phase. Each phase may stop with a verdict. Do not skip a
blocked prerequisite phase.

## Phases

1. Phase 1: connect, create world, run a minimal tick, export basic evidence.
2. Phase 2: run bounded lifecycle, replay/branch, submit direction, export
   lifecycle evidence.
3. Phase 3: collect Agent public life, memory/rest continuity, narrative and
   diagnostic inspection evidence.
4. Phase 4: export complete result directory, run checker/scorecard when
   available, run second-Agent review, report final verdict.

## Stop Rules

- Secret/raw/private marker leak: FAIL.
- UI smoke is not full PASS.
- The client must not call providers directly.
- The client must not generate authoritative world facts.
