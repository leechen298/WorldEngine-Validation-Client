# Handoff Prompts

英文镜像：`handoff-prompts.md`。

## Validation Client 实现

```text
/goal 开发 v0.8-worldengine-v0.9-validation-plan-optimization
```

目标：按 `plan.zh.md` 的编号任务推进，保持外部客户端边界，完成到待验证状态。

## 第二 Agent 复核

```text
/goal 只读复核 v0.8-worldengine-v0.9-validation-plan-optimization 的最新 validation run
```

目标：读取 operation log、api log、manifest、artifacts、redaction scan 和 scorecard summary，只给证据是否支持进入人工验证的结论。
