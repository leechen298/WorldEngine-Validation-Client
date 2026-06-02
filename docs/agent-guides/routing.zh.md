# 自然语言路由

英文镜像：`routing.md`。

自然语言请求只负责把工作路由到 milestone、spec 或 ADR 文档。路由永远不授权
跳过文档、验证、review 记录或 task 级提交。

| 用户请求 | 路由 | 必读文档 |
| --- | --- | --- |
| `开发 v0.1`、`实现 v0.1`、`继续 v0.1`、`/goal 开发 v0.1` | `docs/milestones/v0.1-foundation/` | `README.zh.md`、`plan.zh.md`、`review.zh.md` |
| `规划 v0.2`、`生成 v0.2 文档`、`准备 v0.2` | 创建或更新 `docs/milestones/v0.2-*/` | `README.zh.md`、`plan.zh.md`、`review.zh.md` |
| `开发 vX.Y`、`实现 vX.Y`、`继续 vX.Y`、`/goal 开发 vX.Y` | 匹配 `docs/milestones/vX.Y-*/` | `README.zh.md`、`plan.zh.md`、`review.zh.md` |
| `审核 vX.Y`、`review vX.Y`、`检查 vX.Y` | 匹配 `docs/milestones/vX.Y-*/` | `README.zh.md`、`plan.zh.md`、`review.zh.md`、当前 git diff |
| `修改技术栈`、`为什么选 <technology>`、`架构决策` | `docs/adr/` | 相关 ADR；如需改变架构，先创建新 ADR |
| `更新总体设计`、`修改产品边界`、`改验证客户端设计` | `docs/specs/validation-client-design.zh.md` | 总体设计 spec 和受影响 milestone 文档 |

其他版本路由到 `docs/milestones/` 下匹配目录。

如果目录或计划不存在，必须停止并创建或请求 milestone 文档，不能直接实现。

## Milestone 文档标准

每个 milestone 实现前必须有详细文档：

- `README.zh.md`：状态、目标、范围、非目标和入口规则。
- `plan.zh.md`：编号任务、文件、验证命令和预期提交边界。
- `review.zh.md`：task 记录、命令结果、范围审核和最终评估。

实现前，`review.zh.md` 可以记录为待实现。完成门禁满足前，不能写已实现、完
成或等价状态。

如果实现过程中发现 `plan.zh.md` 错误或不完整，必须停下来更新 milestone 文
档，并在范围清楚后再恢复。不得绕开计划静默发挥。
