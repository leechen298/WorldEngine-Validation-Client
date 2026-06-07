# 第二 Agent 复核模板

英文镜像：`second-agent-review-template.md`。

## 输入

- `result.json`
- `operation-log.jsonl`
- `api-log.jsonl`
- `api-summary.json`
- `manifest.json`
- scenario required artifacts
- `redaction-scan.json`
- `scorecard-summary.json`
- screenshots / transcript

## 检查项

- 操作日志是否覆盖计划步骤。
- direct API harvest 是否与 operation log 分离。
- required artifacts 是否存在或诚实记录 `blocked` / `not_run` / `fail`。
- status 是否被保真保存。
- redaction flags 是否无 blocking leak。
- scorecard/checker 结果来源是否清楚。
- 是否存在客户端自行声明 PASS。

## 结论

```text
review_status: pass | fail | blocked
blocking_findings: []
non_blocking_findings: []
evidence_paths: []
recommendation: enter_human_validation | fix_before_human_validation | blocked
```
