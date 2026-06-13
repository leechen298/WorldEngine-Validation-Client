# Operation Recording Contract

Chinese mirror: `operation-recording-contract.zh.md`.

## Goal

Agent autonomous testing must persist detailed, reviewable raw operation
records. This document defines the minimum requirements for
`operation-log.jsonl`, `api-log.jsonl`, `console.log`, `transcript.md`, and
screenshots.

## Record Boundaries

| Type | File | Meaning |
| --- | --- | --- |
| User/Agent UI operations | `operation-log.jsonl` | Clicks, fills, waits, selects, downloads, screenshots. |
| HTTP/API interactions | `api-log.jsonl`, `api-summary.json` | Validation Client and WorldEngine request/response summaries. |
| Agent execution narrative | `transcript.md` | Human-readable observations, decisions, and phase verdicts. |

Direct API harvest must not be written as a user click. It belongs in
`api-log.jsonl` and must be called out in `transcript.md`.

## `operation-log.jsonl` Schema

Each line is a JSON object with at least:

```json
{
  "schema_version": "0.9.0",
  "run_id": "uuid-or-stable-id",
  "step_id": "P1-05",
  "phase": "phase-1",
  "actor": "codex-agent",
  "operation_kind": "click",
  "target": {
    "page": "Runtime Console",
    "role": "button",
    "label": "Create world",
    "test_id": null,
    "selector": null
  },
  "input": {
    "text_redacted": null,
    "value_redacted": null,
    "value_length": null
  },
  "before": {
    "url": "http://127.0.0.1:5173/",
    "visible_text_summary": "Session library visible",
    "screenshot": "screenshots/phase-1-before-create-world.png"
  },
  "after": {
    "url": "http://127.0.0.1:5173/",
    "visible_text_summary": "Runtime controls visible",
    "screenshot": "screenshots/phase-1-after-create-world.png"
  },
  "api_refs": ["api-log:0004"],
  "artifact_refs": ["world-creation-summary.json"],
  "result": {
    "status": "executed",
    "blocked_reason": null,
    "error_message": null
  },
  "timestamp": "ISO-8601"
}
```

## Allowed `operation_kind`

```text
page_open
click
fill
select
keyboard
wait_for_visible
wait_for_response
download
screenshot
observe
phase_verdict
blocked
```

## Input Rules

- Public world premises and public directions may be recorded, with text length
  and summary.
- Never record provider API keys, authorization headers, raw prompts, raw
  provider responses, private memory, or raw thought.
- Potentially sensitive input must be redacted before entering the evidence
  bundle.
- Public user input may be stored verbatim only when marked as
  `source: user_public_input`.

## `api-log.jsonl` Schema

Each line is a JSON object with at least:

```json
{
  "schema_version": "0.9.0",
  "run_id": "uuid-or-stable-id",
  "api_ref": "api-log:0004",
  "phase": "phase-1",
  "source_step_id": "P1-05",
  "method": "POST",
  "url_origin": "validation-client-api",
  "path_template": "/sessions/worldengine",
  "path_redacted": "/sessions/worldengine",
  "request_summary": {
    "body_shape": ["session_name", "worldview"],
    "public_input_lengths": {"worldview": 58},
    "secrets_included": false,
    "raw_prompt_included": false
  },
  "response_summary": {
    "status_code": 201,
    "body_shape": ["session", "world"],
    "world_id": "world-...",
    "error_class": null
  },
  "duration_ms": 123,
  "timestamp": "ISO-8601"
}
```

## `api-summary.json`

Must aggregate request counts by phase, method/path template, non-2xx
responses, blocked capability calls, redaction status, direct API harvest
entries, and step-to-API refs.

## Screenshots

Minimum screenshots:

```text
screenshots/phase-1-before-create-world.png
screenshots/phase-1-after-create-world.png
screenshots/phase-1-final.png
screenshots/phase-2-final.png
screenshots/phase-3-final.png
screenshots/phase-4-final.png
```

Blocked phases must still save a screenshot.

## `console.log`

Must include browser console warnings/errors, frontend runtime errors, and
failed network request summaries. It must not include secrets, authorization
headers, or raw provider payloads.

## `transcript.md`

Must include run metadata, per-phase observations, operations performed,
evidence downloaded, blockers or pass sources, and final classification.

`transcript.md` is human-readable context. It cannot replace
`operation-log.jsonl` or `api-log.jsonl`.

## PASS Gate

Final PASS requires:

- every executed step has an `operation-log.jsonl` record;
- every request has an `api-log.jsonl` record or a documented no-API reason;
- every phase has screenshots;
- every downloaded artifact has `artifact_refs`;
- `transcript.md` covers every phase;
- `redaction-report.json` is pass.

Any missing item limits the final result to `PARTIAL` or `BLOCKED`.

