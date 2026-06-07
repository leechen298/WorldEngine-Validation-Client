# 合同

英文镜像：`contract.md`。

## 客户端角色

- `client_role`: `display_export_only`
- `provider_owner`: `worldengine`
- `evaluator_role`: `worldengine_checker_or_second_agent_review`

Validation Client 可以展示、记录和导出公开证据。它不得拥有 provider、evaluator、
PASS 判定或权威世界状态。

## 状态枚举

导出数据必须原样保留：

- `pass`
- `fail`
- `blocked`
- `not_run`
- `out_of_scope`，仅当 scenario contract 明确允许时使用

任何 required artifact 缺失、malformed、blocked 或 not run 都不得被改写为 PASS。

## 公开接口

v0.8 discovery 应识别这些 WorldEngine public surfaces，缺失时记录 `blocked` 或
`not_run`：

```text
GET /health
GET /manifest
GET /openapi.json
POST /provider/live-smoke
POST /world/generation/worldview
POST /worlds
GET /runtime/state
POST /runtime/step
POST /runtime/run
POST /runtime/pause
POST /runtime/resume
GET /world/events
GET /world/event-steps
GET /archive/snapshots
GET /world/params
POST /worlds/{world_id}/direction
POST /worlds/{world_id}/director-guidance
POST /worlds/{world_id}/evolution/evaluate-event
POST /worlds/{world_id}/agents/{agent_id}/continuity/evaluate
POST /worlds/{world_id}/narrative/project
POST /worlds/{world_id}/agents/{agent_id}/diagnostics/dialogue/evaluate
```

## 边界

客户端不得暴露 raw prompts、raw provider request/response、provider trace、
authorization header、API key、Agent private memory、Agent private goal、raw thought、
hidden context、private evaluator data、seed 或 oracle data。
