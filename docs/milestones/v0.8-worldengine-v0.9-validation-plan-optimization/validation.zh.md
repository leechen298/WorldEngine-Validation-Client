# v0.8 验证计划

英文镜像：`validation.md`。

## Codex 自主验证

Codex 验证只能证明客户端、证据、redaction 和 checker handoff 足够进入下一关。
它不能自动声明世界体验、Agent 自然性或 LLM-backed full lifecycle PASS。

## 必查项

- 当前会话运行 API/Web/build/E2E 相关命令。
- operation log 和 api log 分离。
- evidence bundle JSON 可解析。
- required artifacts 存在或诚实记录 blocked/not_run/fail。
- redaction scan clean 或明确 FAIL。
- checker/scorecard 结论来源清楚。
- 第二 Agent review 未运行时不能写 full lifecycle PASS。

## 输出

```text
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/validation-runs/YYYY-MM-DD-codex.zh.md
```

结论：`PASS_READY_FOR_HUMAN_VALIDATION`、`PARTIAL`、`BLOCKED`、`FAIL`。
