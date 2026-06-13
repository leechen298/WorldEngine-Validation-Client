# 自然语言路由

英文镜像：`routing.md`。

自然语言请求只负责把工作路由到 milestone、spec 或 ADR 文档。路由永远不授权
跳过文档、验证、review 记录或 task 级提交。

| 用户请求 | 路由 | 必读文档 |
| --- | --- | --- |
| `开发 v0.1`、`实现 v0.1`、`继续 v0.1`、`/goal 开发 v0.1` | `docs/milestones/v0.1-foundation/` | `README.zh.md`、`plan.zh.md`、`review.zh.md` |
| `规划 v0.2`、`生成 v0.2 文档`、`准备 v0.2` | 创建或更新 `docs/milestones/v0.2-*/` | `README.zh.md`、`plan.zh.md`、`review.zh.md` |
| `开发 v0.8`、`实现 v0.8`、`继续 v0.8`、`/goal 开发 v0.8`、`/goal 开发 v0.8-worldengine-v0.9-validation-plan-optimization` | `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/` | `README.zh.md`、`plan.zh.md`、`implementation-task-plan.zh.md`、`cross-repo-validation-gate-matrix.zh.md`、`planning-readiness-checklist.zh.md`、`review.zh.md` |
| `自主验证 v0.8`、`Codex 验证 v0.8`、`Agent 验证 v0.8` | `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/` | `README.zh.md`、`plan.zh.md`、`review.zh.md`、`validation.zh.md`、`autonomous-validation-runbook.zh.md`、`codex-run-report-template.zh.md`、`second-agent-review-template.zh.md`、`agent-review-template.zh.md` |
| `开发 v0.9`、`实现 v0.9`、`继续 v0.9`、`/goal 开发 v0.9`、`/goal 开发完整验证套件` | `docs/milestones/v0.9-complete-worldengine-validation-suite/` | `README.zh.md`、`gap-analysis.zh.md`、`phased-validation-plan.zh.md`、`phased-validation-runbook.zh.md`、`agent-autonomous-operation-script.zh.md`、`operation-recording-contract.zh.md`、`scenario-matrix.zh.md`、`artifact-contract.zh.md`、`plan.zh.md`、`implementation-task-plan.zh.md`、`validation.zh.md`、`review.zh.md` |
| `自主验证 v0.9`、`Codex 验证 v0.9`、`Agent 验证 v0.9`、`运行完整验证套件` | `docs/milestones/v0.9-complete-worldengine-validation-suite/` | `README.zh.md`、`phased-validation-plan.zh.md`、`phased-validation-runbook.zh.md`、`agent-autonomous-operation-script.zh.md`、`operation-recording-contract.zh.md`、`scenario-matrix.zh.md`、`artifact-contract.zh.md`、`plan.zh.md`、`implementation-task-plan.zh.md`、`validation.zh.md`、`review.zh.md` |
| `开发 v0.9.1`、`实现 v0.9.1`、`补全完整验证 runner`、`实现完整操作记录` | `docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/` | `README.zh.md`、`plan.zh.md`、`implementation-task-plan.zh.md`、`test-plan.zh.md`、`scenario-assertion-matrix.zh.md`、`result-directory-contract.zh.md`、`validation.zh.md`、`agent-execution-handoff.zh.md`、`review.zh.md` |
| `开发 vX.Y`、`实现 vX.Y`、`继续 vX.Y`、`/goal 开发 vX.Y` | 匹配 `docs/milestones/vX.Y-*/` | `README.zh.md`、`plan.zh.md`、存在时的 `implementation-task-plan.zh.md`、`cross-repo-validation-gate-matrix.zh.md`、`planning-readiness-checklist.zh.md`、`review.zh.md` |
| `审核 vX.Y`、`review vX.Y`、`检查 vX.Y` | 匹配 `docs/milestones/vX.Y-*/` | `README.zh.md`、`plan.zh.md`、`review.zh.md`、当前 git diff |
| `自主验证 vX.Y`、`Codex 验证 vX.Y`、`Agent 验证 vX.Y` | 匹配 `docs/milestones/vX.Y-*/` | `README.zh.md`、`plan.zh.md`、`review.zh.md`、`validation.zh.md`、`validation-workflow.zh.md`、存在时的 `cross-repo-validation-gate-matrix.zh.md`、`autonomous-validation-runbook.zh.md` 和报告模板 |
| `人工验证 vX.Y`、`人工复核 vX.Y` | 匹配 `docs/milestones/vX.Y-*/` | `validation.zh.md`、最近的 `validation-runs/*-codex.zh.md`、`validation-workflow.zh.md`、存在时的 `agent-review-template.zh.md` 和 `human-validation-template.zh.md` |
| `下一步 vX.Y`、`怎么开工 vX.Y`、`handoff vX.Y`、`quickstart vX.Y`、`复制 prompt vX.Y` | 匹配 `docs/milestones/vX.Y-*/` | 存在时优先读取 `planning-readiness-checklist.zh.md` 和 `next-chat-quickstart.zh.md`，再读取 `README.zh.md`、`plan.zh.md`、`review.zh.md` |
| `修改技术栈`、`为什么选 <technology>`、`架构决策` | `docs/adr/` | 相关 ADR；如需改变架构，先创建新 ADR |
| `更新总体设计`、`修改产品边界`、`改验证客户端设计` | `docs/specs/validation-client-design.zh.md` | 总体设计 spec 和受影响 milestone 文档 |

其他版本路由到 `docs/milestones/` 下匹配目录。

如果目录或计划不存在，必须停止并创建或请求 milestone 文档，不能直接实现。

## Milestone 文档标准

每个 milestone 实现前必须有详细文档：

- `README.zh.md`：状态、目标、范围、非目标和入口规则。
- `plan.zh.md`：编号任务、文件、验证命令和预期提交边界。
- `implementation-task-plan.zh.md`：当 milestone 需要更细执行约束时，记录
  task-by-task 的候选文件、测试重点、验证命令、完成标准和 stop rules。
- `review.zh.md`：task 记录、命令结果、范围审核和最终评估。
- `validation.zh.md`：当 milestone 包含验证行为或验证结论时，记录自主验证清
  单、Agent 复核清单和人工交接清单。
- `autonomous-validation-runbook.zh.md`：当 milestone 包含真实 Codex 自主验证时，
  记录服务启动、preflight、命令、浏览器 flow、证据和 stop rules。
- `cross-repo-validation-gate-matrix.zh.md`：当 milestone 依赖 WorldEngine、
  Validation Client、Codex、第二 Agent 和人工验证跨阶段推进时，记录不可跳关
  门禁、证据、结论枚举和 stop rules。
- `planning-readiness-checklist.zh.md`：当 milestone 需要交给后续聊天执行时，记录
  当前计划结论、唯一允许的下一步、未完成项和 stop rules。
- `next-chat-quickstart.zh.md`：当 milestone 需要跨聊天推进时，记录后续聊天可
  复制的分阶段 `/goal` prompts。

实现前，`review.zh.md` 可以记录为待实现。完成门禁满足前，不能写已实现、完
成或等价状态。

如果实现过程中发现 `plan.zh.md` 错误或不完整，必须停下来更新 milestone 文
档，并在范围清楚后再恢复。不得绕开计划静默发挥。
