# v0.9 Complete WorldEngine Validation Suite

Chinese mirror: `README.zh.md`.

Status: documentation iteration / ready for review
implementation_authorized: no
external_validation_authorized: no
provider_live_call_authorized: no

## Positioning

The Validation Client should not create a new validation milestone for every
WorldEngine version or iteration.

This documentation milestone defines one stable phased validation suite:

```text
Use WorldEngine-Validation-Client to validate, end to end, whether WorldEngine works.
```

WorldEngine versions are compatibility targets observed by capability
discovery, not the organizing structure of the client validation suite.

## Phased Validation Chain

| Phase | Depth | Scope |
| --- | --- | --- |
| Phase 1 | basic | preflight, world creation, short ticks, basic evidence |
| Phase 2 | lifecycle | runtime controls, events, snapshots, replay, direction |
| Phase 3 | Agent depth | Agent life, memory/rest continuity, inspection surfaces |
| Phase 4 | autonomous closeout | result directory, checker/scorecard, second-Agent review |

Each phase can be `pass`, `fail`, `blocked`, or `not_run`. Earlier blockers
must not be converted into later PASS claims. Detailed L0-L8 layer rules live
in `phased-validation-plan.md`.
