# Human Validation Template

Chinese mirror: `human-validation-template.zh.md`.

Use this template to create
`validation-runs/YYYY-MM-DD-human.zh.md` after Codex autonomous validation and
second Agent review are complete.

Human validation does not repeat command tests and does not judge internal
implementation correctness. It judges visual experience, world observability,
public Agent behavior credibility, director boundary, replay/world-line
behavior, and evidence reviewability.

## 0. Conclusion

Choose exactly one:

```text
HUMAN_PASS
HUMAN_PARTIAL
HUMAN_FAIL
```

Current conclusion:

```text
<one allowed conclusion>
```

Short reason:

```text
<short human-facing reason>
```

## 1. Inputs Reviewed

```text
Codex report:
Agent review report:
operation log:
screenshots directory:
evidence bundle:
Web URL if reopened:
session_id:
worldengine_world_id:
branch_id:
```

Confirm:

- [ ] Codex conclusion is `PASS_READY_FOR_HUMAN_VALIDATION`.
- [ ] second Agent conclusion is `READY_FOR_HUMAN_VALIDATION`.
- [ ] human validation is not running before automated gaps are fixed.

If these are not true, this report may only conclude `HUMAN_PARTIAL` or
`HUMAN_FAIL`.

## 2. Session Library Experience

Scores:

```text
understanding cost: 1-5
save/world-line entry clarity: 1-5
WorldEngine connection status clarity: 1-5
```

Notes:

```text
what worked:
what confused me:
must fix:
```

## 3. World Creation Experience

Scores:

```text
base worldview input clarity: 1-5
creation feedback: 1-5
runtime console transition: 1-5
```

Notes:

```text
world prompt used:
visible creation result:
must fix:
```

## 4. World Observability

Scores:

```text
pixel canvas readability: 1-5
public state summary readability: 1-5
event log explanatory power: 1-5
canvas/state/log consistency: 1-5
```

Judgment:

```text
Can I tell what is happening?
Can I connect visual state to events?
Can I explain the current world state to another person?
must fix:
```

## 5. Agent Public Life

Scores:

```text
Agent public state readability: 1-5
Agent behavior naturalness: 1-5
Agent event reaction relationship: 1-5
Agent life-like quality: 1-5
```

Judgment:

```text
What did the Agent appear to want or do?
Did the Agent react to public events naturally?
What felt mechanical or unclear?
must fix:
```

Human validation judges only public behavior, not Agent private memory, private
goal, or self_state.

## 6. Director Guidance Boundary

Scores:

```text
high-level direction input clarity: 1-5
pending / accepted / applied status clarity: 1-5
external event and environment boundary: 1-5
not direct player control: 1-5
```

Judgment:

```text
guidance text:
visible effect:
Did it feel high-level?
Did it seem to force Agent internal state?
must fix:
```

## 7. Replay and World Lines

Scores:

```text
replay slider understandability: 1-5
commit point understandability: 1-5
branch creation understandability: 1-5
branch switching understandability: 1-5
```

Judgment:

```text
Can I revisit a prior visible state?
Does branch feel like a named world line?
Did the UI keep branch semantics limited to naming, switching, replay, and continued progression?
must fix:
```

## 8. Evidence Reviewability

Scores:

```text
evidence bundle understandability: 1-5
screenshots to operation record match: 1-5
log replayability: 1-5
issue localization: 1-5
```

Judgment:

```text
Can another human replay the validation story from evidence?
What evidence was missing?
must fix:
```

## 9. Human Findings

```text
Finding ID:
Severity: P1/P2/P3
Area:
Evidence:
Human impact:
Required follow-up:
Blocks next iteration: yes/no
```

## 10. Final Decision

`HUMAN_PASS` requires:

- [ ] world is observable.
- [ ] Agent public behavior has basic naturalness.
- [ ] director guidance keeps high-level boundary.
- [ ] replay and branch are understandable as world lines.
- [ ] evidence bundle is sufficient for replay.
- [ ] no P1 blocker exists.

If any item is missing, the conclusion must not be `HUMAN_PASS`.
