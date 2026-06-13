# Phased Validation Plan

Chinese mirror: `phased-validation-plan.zh.md`.

## Goal

This is the stable Validation Client validation case. It does not mirror
WorldEngine iterations.

The question is:

```text
Does the currently connected WorldEngine work?
```

## Phases

| Phase | Scope | Minimum evidence |
| --- | --- | --- |
| Phase 1 | Basic functionality | preflight, world creation, short runtime, basic evidence export |
| Phase 2 | Lifecycle | runtime controls, events, snapshots, replay, direction boundary |
| Phase 3 | Agent depth | Agent public life, memory/rest continuity, inspection surfaces |
| Phase 4 | Autonomous validation | full result directory, checker/scorecard, second-Agent review |

Each phase can be `pass`, `fail`, `blocked`, or `not_run`.

## Summary Rules

- Phase 1 only PASS is `PARTIAL`.
- Phase 1-2 PASS with Phase 3 blocked is `PARTIAL / BLOCKED`.
- Phase 1-3 PASS with Phase 4 checker blocked is `PARTIAL / BLOCKED`.
- Phase 1-4 PASS is `PASS`.
- Any redaction failure is `FAIL`.
- Any blocking product behavior failure is `FAIL`.

## Stability Rule

WorldEngine versions are observed through capability mapping. They do not create
new Validation Client validation case names.
