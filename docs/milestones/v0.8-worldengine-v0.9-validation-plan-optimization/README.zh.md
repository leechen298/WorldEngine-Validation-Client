# v0.8 WorldEngine v0.9 Validation Plan Optimization

英文镜像：`README.md`。

状态：文档自审中 / 用户已授权文档后继续实现

## 目标

v0.8 把 Validation Client 从 v0.7 的自主验证载体升级为可重复的
WorldEngine 验证计划优化面。它对齐 WorldEngine v0.9 的公开 scenario、artifact、
scorecard、checker 和第二 Agent 复核合同，让客户端能够展示、记录、导出并保留
WorldEngine v0.9 验证证据。

v0.8 不让客户端成为 WorldEngine evaluator。PASS 权威仍来自 WorldEngine checker、
scorecard 和第二 Agent 复核。

## 范围

- 创建 v0.8 里程碑文档包、scenario 操作矩阵、artifact 合同、redaction 矩阵、runbook 和第二 Agent 模板。
- 刷新 v0.8 路由和过期 v0.7 / WorldEngine 0.8.9 引用。
- 扩展 WorldEngine v0.9 public surface discovery。
- 增加 scenario-aware evidence bundle manifest、artifact index 和 named artifacts。
- 保留 `pass`、`fail`、`blocked`、`not_run`，不把阻塞状态美化成 PASS。
- 区分用户可见 operation log 和 direct API harvest log。
- 增加 bounded runtime controls 的 UI/log 支撑。
- 展示 checker、scorecard、second-Agent review 和 redaction 状态，但不由客户端自行判定 PASS。

## 非目标

- 不直接调用 DeepSeek 或任何 LLM provider。
- 不保存、展示或转发 provider key。
- 不生成 LLM-backed world content。
- 不计算权威 world rules、parameter changes、event legality 或 Agent autonomy。
- 不把 UI smoke 当作 WorldEngine validation PASS。
- 不把 narrative projection 或 diagnostic dialogue 写入 canonical world state 或 Agent memory。

## 权威来源

WorldEngine v0.9 是验证合同的权威来源。v0.8 使用 WorldEngine 当前交接草案：

```text
/Users/leechen/projects/WorldEnginProjects/WorldEngine/docs/iterations/v0.9/0.9.11-validation-client-evidence-handoff-contract/validation-client-v0.8-validation-plan-optimization-handoff.zh.md
```

该交接文档当前位于 WorldEngine 工作树的文档草案中。本仓库只消费其公开合同，不修改
WorldEngine 仓库。

## 入口

开发、审核或验证 v0.8 前读取：

```text
docs/README.zh.md
docs/roadmap.zh.md
docs/specs/validation-client-design.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/README.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/plan.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/contract.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/artifact-contract.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/scenario-operation-matrix.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/redaction-matrix.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/technical-design.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/test-plan.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/review.zh.md
docs/agent-guides/routing.md
docs/agent-guides/workflow.md
docs/agent-guides/boundaries.md
docs/agent-guides/validation-workflow.md
```

## 当前授权

用户已授权：创建 v0.8 文档并完成自审后，继续进入实现，除非遇到无法自行决策的门禁，
否则推进到待验证状态。
