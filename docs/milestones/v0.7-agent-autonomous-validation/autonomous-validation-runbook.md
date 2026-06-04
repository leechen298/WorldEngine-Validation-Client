# Codex Autonomous Validation Runbook

Chinese mirror: `autonomous-validation-runbook.zh.md`.

Use this runbook after v0.7 implementation is complete and WorldEngine 0.8.9
public contract is ready. Codex follows it to run one real browser autonomous
validation and produce evidence for second Agent review and human validation.

This is not a validation result. Do not write
`PASS_READY_FOR_HUMAN_VALIDATION` before the commands and browser flow in this
runbook actually run.

## 0. Preconditions

Before starting, confirm:

- [ ] WorldEngine implemented the 0.8.9 public contract.
- [ ] WorldEngine completed or equivalently satisfied
      `contract-readiness-checklist.zh.md`.
- [ ] WorldEngine conclusion is `WORLDENGINE_CONTRACT_READY`.
- [ ] Validation Client v0.7 implementation is complete.
- [ ] Validation Client `review.zh.md` records v0.7 implementation and command
      results.
- [ ] the current goal is Codex autonomous validation, not human validation.

If any item is missing, stop and write BLOCKED or PARTIAL. Do not enter the
browser flow.

## 1. Required Reading

```text
AGENTS.zh.md
docs/README.zh.md
docs/specs/validation-client-design.zh.md
docs/milestones/v0.7-agent-autonomous-validation/README.zh.md
docs/milestones/v0.7-agent-autonomous-validation/validation.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/autonomous-validation-runbook.zh.md
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
docs/agent-guides/validation-workflow.zh.md
```

WorldEngine-side reading:

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/contract-readiness-checklist.zh.md
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.8/0.8.9-external-validation-provider-and-handoff-manifest/review.zh.md
```

## 2. Create Run Directory

Directory name:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/
```

Required outputs:

```text
agent-run.jsonl
codex.zh.md
api-summary.json
screenshots/
downloads/evidence-bundle.json
```

Recommended screenshots:

```text
screenshots/01-session-library.png
screenshots/02-create-world.png
screenshots/03-runtime-console.png
screenshots/04-director-guidance.png
screenshots/05-replay-branch.png
screenshots/06-evidence-panel.png
```

## 3. Record Git and Environment Metadata

In Validation Client:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
git status --short --branch
git rev-parse HEAD
git diff --check
```

In WorldEngine:

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine
git status --short --branch
git rev-parse HEAD
git diff --check
```

Record in `codex.zh.md`:

- branch.
- commit.
- dirty files.
- unrelated dirty files.
- whether this run may continue with the current dirty worktree.

If dirty files affect this validation and cannot be explained, stop.

## 4. Start Services

### 4.1 WorldEngine

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine/backend
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Record:

```text
command:
port:
PID or session id:
startup result:
```

### 4.2 Validation Client API

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
uv run --project apps/api uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir apps/api
```

Record:

```text
command:
port:
PID or session id:
startup result:
```

### 4.3 Validation Client Web

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
pnpm --dir apps/web dev
```

Record the actual Web URL from dev server output. Do not assume a fixed port.

## 5. Public Contract Preflight

Run:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/manifest
curl -i http://127.0.0.1:8000/openapi.json
curl -i http://127.0.0.1:8765/health
curl -i http://127.0.0.1:8765/health/worldengine
curl -i -H 'Content-Type: application/json' \
  -d '{"session_name":"Codex autonomous validation preflight","world_prompt":"a small observable pixel world"}' \
  http://127.0.0.1:8765/sessions/worldengine
```

Required:

- [ ] `/manifest` returns 200.
- [ ] `/openapi.json` is reachable.
- [ ] Validation Client reports `world_creation: available`.
- [ ] `POST /sessions/worldengine` succeeds.
- [ ] public responses contain no keys, private prompts, provider raw traces, or
      Agent private state.

If any item is missing, stop and use `codex-run-report-template.zh.md` to write
BLOCKED, PARTIAL, or FAIL.

## 6. Command Tests

Run:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

If v0.7 implementation adds Playwright or equivalent E2E, run that command and
record artifact paths.

On command failure:

- do not enter human validation.
- stop browser flow if the failure blocks UI flow.
- record the command, error, and reproduction path in `codex.zh.md`.

## 7. Browser Autonomous Flow

Use a browser from a human perspective:

1. Open Web URL.
2. Screenshot session library.
3. Check WorldEngine connection status.
4. Enter session name.
5. Enter base worldview.
6. Create WorldEngine session.
7. Enter runtime console.
8. Screenshot runtime console.
9. Inspect pixel canvas.
10. Inspect public state summary.
11. Inspect Agent public state.
12. Inspect World Log.
13. Inspect Agent Life Log.
14. Enter high-level director guidance.
15. Submit director guidance.
16. Screenshot guidance status.
17. Use replay slider.
18. Select commit point.
19. Create branch.
20. Switch branch.
21. Screenshot replay / branch state.
22. Open evidence panel.
23. Download evidence bundle.
24. Screenshot evidence panel.

Every step must be recorded in `agent-run.jsonl`. Screenshots without log
records are not enough for a complete pass.

## 8. Operation Log Requirements

Each JSONL record needs:

```text
timestamp
run_id
actor
phase
url
action_type
target_label
input_text
request_method
request_path
response_status
response_summary
visible_result
screenshot_path
downloaded_file
notes
```

Check:

- [ ] every JSONL line parses.
- [ ] run_id is consistent.
- [ ] session_id is consistent.
- [ ] worldengine_world_id is consistent.
- [ ] all key UI actions are covered.
- [ ] no private prompt, provider raw trace, Agent private memory, private goal,
      self_state, or hidden_context is recorded.

## 9. Evidence Bundle Check

Check downloaded file:

```text
downloads/evidence-bundle.json
```

Confirm:

- [ ] JSON parses.
- [ ] bundle session_id matches this run.
- [ ] bundle and operation log explain each other.
- [ ] event, diff, snapshot, and API summary counts match records.
- [ ] redaction flags are clean.
- [ ] evaluator PASS is not faked.
- [ ] private content is not leaked.

## 10. Redaction Scan

Run and classify:

```bash
cd /Users/leechen/projects/WorldEngine-Validation-Client
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

Classification:

```text
allowed documentation hits:
allowed test redaction hits:
forbidden UI hits:
forbidden bundle hits:
forbidden real secret hits:
```

Real secret, private prompt, provider raw trace, or Agent private state leakage
requires `FAIL`.

## 11. Write Codex Report

Use:

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-run-report-template.zh.md
```

Output:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-codex/codex.zh.md
```

Allowed conclusions:

```text
PASS_READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

## 12. Second Agent Handoff

Only enter second Agent review when `codex.zh.md` concludes
`PASS_READY_FOR_HUMAN_VALIDATION`.

Inputs:

```text
codex.zh.md
agent-run.jsonl
api-summary.json
screenshots/
downloads/evidence-bundle.json
```

Second Agent uses:

```text
docs/milestones/v0.7-agent-autonomous-validation/agent-review-template.zh.md
```

Output:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-agent-review.zh.md
```

## 13. Human Validation Entry

Only hand off to a human when second Agent conclusion is
`READY_FOR_HUMAN_VALIDATION`.

Human validation uses:

```text
docs/milestones/v0.7-agent-autonomous-validation/human-validation-template.zh.md
```

Human validation output:

```text
docs/milestones/v0.7-agent-autonomous-validation/validation-runs/YYYY-MM-DD-human.zh.md
```

Allowed human conclusions:

```text
HUMAN_PASS
HUMAN_PARTIAL
HUMAN_FAIL
```

## 14. Stop Rules

- Stop if WorldEngine contract is not ready.
- Stop if Validation Client cannot create a WorldEngine session.
- Stop or write PARTIAL/FAIL if command tests or builds fail.
- Do not enter second Agent READY if browser flow cannot complete.
- Do not enter human validation if operation logs are incomplete.
- Do not enter human validation if evidence bundle cannot parse or does not
  match this run.
- FAIL on real secret or private state leakage.
- Codex must not claim human validation pass.
- Second Agent must not replace human experience judgment.
