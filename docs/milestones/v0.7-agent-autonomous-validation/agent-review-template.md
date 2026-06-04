# Second Agent Read-Only Review Template

Chinese mirror: `agent-review-template.zh.md`.

Use this template to create
`validation-runs/YYYY-MM-DD-agent-review.zh.md` after a second Agent reads the
previous Codex autonomous validation evidence.

The review Agent must not operate the browser, invent unrecorded facts, or
claim human validation passed.

## 0. Conclusion

Choose exactly one:

```text
READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

Current conclusion:

```text
<one allowed conclusion>
```

Short reason:

```text
<short public reason>
```

## 1. Read-Only Inputs

```text
Codex report:
operation log:
screenshots directory:
evidence bundle:
api summary:
WorldEngine manifest summary:
WorldEngine OpenAPI summary:
test/build output:
git status output:
```

Confirm:

- [ ] all inputs exist.
- [ ] inputs use the same run_id.
- [ ] inputs use the same session_id.
- [ ] browser was not operated again.
- [ ] no facts missing from Codex records were invented.

## 2. Codex Plan Compliance

Check that Codex completed:

- [ ] preflight.
- [ ] backend tests.
- [ ] frontend tests.
- [ ] build.
- [ ] browser flow.
- [ ] operation log.
- [ ] screenshots.
- [ ] evidence bundle download.
- [ ] evidence bundle parse.
- [ ] redaction scan.
- [ ] conclusion boundary.

Gaps:

```text
<missing plan item or none>
```

## 3. Operation Log Review

```text
line count:
parse result:
run_id:
session_id:
worldengine_world_id:
first action:
last action:
```

Coverage:

- [ ] page open.
- [ ] create session.
- [ ] enter runtime console.
- [ ] inspect pixel canvas.
- [ ] inspect public state.
- [ ] inspect Agent public state.
- [ ] submit director guidance.
- [ ] replay.
- [ ] branch.
- [ ] evidence bundle download.

Not acceptable:

- [ ] key step has screenshot but no log.
- [ ] key step has log but no visible result.
- [ ] API response summary contradicts visible UI state.
- [ ] log contains private prompt, provider raw trace, or Agent private state.

## 4. Screenshot Review

```text
session library screenshot:
create world screenshot:
runtime console screenshot:
director guidance screenshot:
replay/branch screenshot:
evidence panel screenshot:
```

Check:

- [ ] screenshots cover key screens.
- [ ] screenshots match operation log order.
- [ ] screenshots do not leak keys, private prompts, provider raw traces, or
      private state.

## 5. Evidence Bundle Review

```text
parse result:
manifest.session_id:
operation log session_id:
event count:
diff count:
snapshot count:
api summary count:
redaction flags:
warnings:
```

Check:

- [ ] evidence bundle matches run/session.
- [ ] bundle counts match records.
- [ ] replay/branch references exist.
- [ ] public evaluator output is not faked as pass.
- [ ] private data scan is clean.

## 6. Boundary Review

Confirm:

- [ ] client did not manage LLM keys.
- [ ] client did not directly call LLM providers.
- [ ] client did not read WorldEngine private paths or helpers.
- [ ] client did not record private prompts.
- [ ] client did not record provider raw traces.
- [ ] client did not record Agent private memory, private goals, identity,
      relationship, self_state, or hidden_context.
- [ ] Codex did not claim human validation pass.

## 7. Findings

```text
Finding ID:
Severity:
Evidence:
Impact:
Required follow-up:
Blocks human validation: yes/no
```

## 8. Handoff Decision

If conclusion is `READY_FOR_HUMAN_VALIDATION`:

- [ ] human validation judges experience only and does not repeat command tests.
- [ ] hand Codex report, Agent review, operation log, screenshots, and evidence
      bundle to the human reviewer.

If conclusion is not `READY_FOR_HUMAN_VALIDATION`:

- [ ] do not enter human validation.
- [ ] name the WorldEngine package, Validation Client task, or validation-run
      gap that must be fixed.
