# Result Directory Contract

英文镜像：`result-directory-contract.md`。

## 目录格式

```text
validation-runs/<timestamp>-complete-worldengine-validation-suite/
```

如果导出给 WorldEngine checker，可以复制到 WorldEngine 接受的 result path，但
Validation Client 原始目录必须保留。

## Required Tree

```text
result.json
coverage-matrix.json
command-matrix.md
operation-log.jsonl
api-log.jsonl
api-summary.json
capability-discovery.json
world-creation-summary.json
session-summary.json
runtime-control-summary.json
timeline-evidence.json
direction-boundary-summary.json
agent-evidence.json
memory-continuity-summary.json
inspection-evidence.json
scorecard-input.json
redaction-report.json
console.log
transcript.md
second-agent-review.md
screenshots/
  phase-1-before-create-world.png
  phase-1-after-create-world.png
  phase-1-final.png
  phase-2-final.png
  phase-3-final.png
  phase-4-final.png
compat/
  world-lifecycle-summary.json
  diff-replay-summary.json
  scorecard-summary.json
  redaction-scan.json
```

## `result.json`

最低字段：

```json
{
  "schema_version": "0.9.1",
  "scenario": "complete-worldengine-validation-suite",
  "status": "pass|partial|blocked|fail",
  "status_reason": "string",
  "worldengine": {
    "reachable": true,
    "manifest_seen": true,
    "capabilities": {}
  },
  "phases": [
    {
      "phase": "phase-1",
      "status": "pass|partial|blocked|fail|not_run",
      "executed_steps": ["P1-01"],
      "blocked_reason": null,
      "pass_source": "worldengine_public_response|checker|second_agent|none"
    }
  ],
  "redaction": {
    "status": "pass|fail",
    "blocking_findings": []
  },
  "artifacts": []
}
```

## `coverage-matrix.json`

必须说明每个 step：

- `planned`
- `executed`
- `not_run`
- `blocked`
- `operation_log_ref`
- `api_refs`
- `artifact_refs`

## `command-matrix.md`

必须记录：

- 启动命令。
- E2E 命令。
- checker 命令。
- redaction scan 命令。
- 未运行命令及原因。

## BLOCKED Result 要求

即使 WorldEngine 不可达，也必须生成：

- `result.json`
- `coverage-matrix.json`
- `operation-log.jsonl`
- `api-log.jsonl`
- `api-summary.json`
- `capability-discovery.json`
- `redaction-report.json`
- `console.log`
- `transcript.md`
- 至少一个 blocked screenshot 或 screenshot status。

blocked result 不能缺少 operation/API evidence。

