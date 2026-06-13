# Agent Autonomous Operation Script

Chinese mirror: `agent-autonomous-operation-script.zh.md`.

## Goal

This document defines the concrete operation script for Agent autonomous
testing in `complete-worldengine-validation-suite`.

The autonomous Agent must operate the Validation Client Web UI from a normal
validator perspective. It must persist every operation, input, visible result,
API result, screenshot, and exported artifact.

## Execution Rules

- Prefer Web UI operations.
- Direct API harvest is allowed only as supplemental evidence and must never be
  disguised as a user click.
- Every UI operation must be written to `operation-log.jsonl`.
- Every API request/response summary must be written to `api-log.jsonl` and
  `api-summary.json`.
- Every phase must save a screenshot under `screenshots/`.
- Every phase must append a natural-language record to `transcript.md`.
- Missing controls, pages, or APIs must be recorded as blocked evidence, not
  skipped.

## Fixed Inputs

| Field | Value |
| --- | --- |
| Session name | `complete-suite-autonomous-<timestamp>` |
| World premise | `A publicly observable harbor pixel world with residents, roads, markets, weather, resource flow, and day-night changes. Residents should live, wait, rest, interact, and respond to external events under world rules.` |
| Direction 1 | `Make the market area more likely to show cooperation, queues, or resource-flow changes over the next period, but do not directly create items or directly change any Agent internal memory or goal.` |
| Direction 2 | `Make weather gradually capable of worsening, and let the world decide external risk from location, weather, and rules. Do not directly specify any Agent death.` |
| Branch name | `autonomous-branch-<timestamp>` |
| Initial run ticks | `5` |
| Lifecycle run ticks | `20` |
| Agent depth observation ticks | `30` |
| Replay target tick | `0` |

## Phase 1: Basic Functionality

| Step | Operation | Target | Input | Required Record |
| --- | --- | --- | --- | --- |
| P1-01 | Open page | Validation Client root URL | none | URL, title, screenshot |
| P1-02 | Read connection status | WorldEngine status area | none | visible status, health summary |
| P1-03 | Fill session name | `Session name` input | fixed session name | before/after value, control label |
| P1-04 | Fill world premise | `World premise` input | fixed premise | text length, redacted summary |
| P1-05 | Create world | `Create world` button | click | click event, request path, response status |
| P1-06 | Wait for runtime page | runtime-control heading | none | visible sections |
| P1-07 | Verify public world state | public state/map/log panels | none | world id, tick, summary |
| P1-08 | Set tick count | run-tick input | `5` | input value |
| P1-09 | Run ticks | run button | click | runtime API summary |
| P1-10 | Download basic evidence | evidence download button | click | filename, artifact index |
| P1-11 | Save screenshot | current page | none | `screenshots/phase-1.png` |
| P1-12 | Record phase verdict | result phase entry | verdict | pass source or blocked taxonomy |

## Phase 2: Lifecycle

| Step | Operation | Target | Input | Required Record |
| --- | --- | --- | --- | --- |
| P2-01 | Set run ticks | run-tick input | `20` | input value |
| P2-02 | Run world | run button | click | before/after tick, response status |
| P2-03 | Pause | pause button | click | runtime state change |
| P2-04 | Resume | resume button | click | runtime state change |
| P2-05 | Single tick | single-tick button | click | tick +1 evidence |
| P2-06 | Inspect events | world log/events panel | none | event count, summaries |
| P2-07 | Inspect snapshots | snapshots/replay panel | none | snapshot count, tick |
| P2-08 | Set replay tick | target tick input | `0` | input value |
| P2-09 | Create branch | branch input/button | fixed branch name | branch id/name, source tick |
| P2-10 | Submit direction 1 | direction input/button | direction 1 | classification, status |
| P2-11 | Submit direction 2 | direction input/button | direction 2 | no direct Agent internal write |
| P2-12 | Download lifecycle evidence | lifecycle/handoff download | click | artifact index, coverage |
| P2-13 | Save screenshot | current page | none | `screenshots/phase-2.png` |
| P2-14 | Record phase verdict | result phase entry | verdict | pass source or blocked taxonomy |

## Phase 3: Agent Depth

| Step | Operation | Target | Input | Required Record |
| --- | --- | --- | --- | --- |
| P3-01 | Open Agent panel | Agent life/public state panel | none | Agent list, public summary |
| P3-02 | Read Agent public state | Agent detail area | none | agent id, tick, public state |
| P3-03 | Trigger Agent step | Agent step/observe control | click | observe/action/wait/rest result |
| P3-04 | Run observation ticks | run-tick input/button | `30` | multi-tick state changes |
| P3-05 | Record legal no-intent state | intent/status area | none | intent/action/wait/rest |
| P3-06 | Inspect memory summary | memory/continuity panel | none | public summary only |
| P3-07 | Run consolidation | consolidation control | click or blocked | consolidation id/status |
| P3-08 | Run narrative projection | narrative control | click | projection summary, no canonical write |
| P3-09 | Run diagnostic dialogue | diagnostic control | diagnostic prompt | diagnostic summary, no Agent memory write |
| P3-10 | Download Agent evidence | Agent evidence download | click | Agent/memory artifacts |
| P3-11 | Save screenshot | current page | none | `screenshots/phase-3.png` |
| P3-12 | Record phase verdict | result phase entry | verdict | pass source or blocked taxonomy |

## Phase 4: Autonomous Closeout

| Step | Operation | Target | Input | Required Record |
| --- | --- | --- | --- | --- |
| P4-01 | Export result directory | complete result export | click | result dir path, file list |
| P4-02 | Save console log | browser/app logs | none | `console.log` |
| P4-03 | Save transcript | Agent execution notes | none | `transcript.md` |
| P4-04 | Run redaction scan | client or WorldEngine checker | result dir | command, result |
| P4-05 | Run WorldEngine checker | checker/scorecard | result dir | command, stdout, exit code |
| P4-06 | Run second-Agent review | read-only Agent | result dir | `second-agent-review.md` |
| P4-07 | Summarize verdict | result/scorecard | none | PASS/PARTIAL/BLOCKED/FAIL |

## Stop Rules

- Missing UI controls must be recorded as blocked. Do not replace them with
  direct API calls that appear as UI success.
- API success without visible UI state is an evidence gap.
- Missing UI operation records prevent final PASS.
- Missing API summaries prevent final PASS.
- Missing screenshots, console log, or transcript prevent Phase 4 PASS.
- Any secret/raw/private marker leak is final FAIL.

