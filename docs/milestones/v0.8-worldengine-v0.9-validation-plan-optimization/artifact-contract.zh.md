# Artifact Contract

英文镜像：`artifact-contract.md`。

## Bundle 结构

```text
evidence-bundle/
  manifest.json
  result.json
  operation-log.jsonl
  api-log.jsonl
  api-summary.json
  provider-live-summary.json
  world-creation-summary.json
  world-rule-summary.json
  rule-parameter-summary.json
  event-legality-summary.json
  agent-autonomy-summary.json
  diff-replay-summary.json
  world-lifecycle-summary.json
  narrative-projection-summary.json
  diagnostic-conversation-summary.json
  redaction-scan.json
  scorecard-summary.json
  second-agent-review.md
  transcript.md
  console.log
  screenshots/
```

只有 active scenario 要求的 artifact 必须存在。缺失 required artifact 必须显示为
`blocked`、`not_run` 或 `fail`。

## Manifest 字段

`manifest.json` 必须包含：

- `schema_version`
- `bundle_id`
- `scenario`
- `result_status`
- `client_role`
- `provider_owner`
- `evaluator_role`
- `created_at`
- `artifact_index`
- `redaction_status`
- `checker_contract`
- `unsupported_items`

每个 `artifact_index` entry 必须包含：

- `name`
- `path`
- `required`
- `displayable`
- `exportable`
- `producer`
- `schema_version`
- `status`
- `redaction_status`

`path` 必须是 bundle-relative path，不能包含绝对路径或跳出 bundle 的 `..`。
