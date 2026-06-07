# Scenario Operation Matrix

英文镜像：`scenario-operation-matrix.md`。

| Scenario | 客户端操作 | Required artifacts | PASS 来源 |
| --- | --- | --- | --- |
| `worldengine-full-lifecycle-autonomous` | 创建世界、bounded step/run、读取 events/snapshots、提交 direction/guidance、导出 bundle。 | `result.json`、`operation-log.jsonl`、`api-summary.json`、`world-lifecycle-summary.json`、截图、`redaction-scan.json`、`scorecard-summary.json`。 | WorldEngine checker。 |
| `provider-live-smoke-deepseek` | 发现并调用 WorldEngine-owned `/provider/live-smoke`。 | `provider-live-summary.json`、`operation-log.jsonl`、`redaction-scan.json`。 | WorldEngine 公开响应和 checker 规则。 |
| `llm-backed-world-creation` | 提交 premise，调用 WorldEngine-owned generation/creation path。 | `world-creation-summary.json`、public state refs、visualization refs。 | LLM-backed 且非 deterministic generic fallback。 |
| `world-rule-parameter-evolution` | 运行 bounded ticks，采集 params/events/diffs。 | `world-rule-summary.json`、`rule-parameter-summary.json`、`diff-replay-summary.json`。 | rule-linked changes 证据。 |
| `rule-compliant-event-generation` | 提交 legal/illegal candidate 或 direction-linked event，记录 adjudication。 | `event-legality-summary.json`、event refs、diff refs。 | legality evidence 且无 direct final-state mutation。 |
| `agent-persistent-autonomy-evidence` | 观察多轮公开 Agent continuity/autonomy evidence。 | `agent-autonomy-summary.json`、public summary refs、event refs。 | WorldEngine evidence 且非 client-scripted action。 |
| `llm-backed-full-lifecycle-autonomous` | provider smoke、world creation、rule evolution、event legality、Agent autonomy、bundle、checker、第二 Agent review。 | 完整 v0.9 evidence bundle。 | checker/scorecard 加第二 Agent clean review。 |

Direct API harvest 必须记录到 `api-log.jsonl`，不得伪装成 `operation-log.jsonl` 中的人类或
Agent 可见操作。
