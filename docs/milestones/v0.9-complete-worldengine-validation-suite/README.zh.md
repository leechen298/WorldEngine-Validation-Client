# v0.9 Complete WorldEngine Validation Suite

英文镜像：`README.md`。

状态：documentation iteration / ready for review
implementation_authorized: no
external_validation_authorized: no
provider_live_call_authorized: no

## 定位

Validation Client 不应该跟随 WorldEngine 的每个版本或每个迭代做一套验证。

本 milestone 是一个文档迭代，目标是把客户端验证目标收敛为一套稳定的、
分阶段的完整验证用例：

```text
用 WorldEngine-Validation-Client 一次性、端到端验证 WorldEngine 是否能正常工作。
```

WorldEngine 当前实现版本只是被测对象的兼容状态。客户端可以记录它观察到的
WorldEngine version / manifest / capabilities，但不把 WorldEngine 迭代号作为自己的
验证结构。

## 核心原则

- 一个完整验证 suite，而不是按 WorldEngine 版本拆验证项目。
- 用例可以逐级深入，但最终属于同一条完整验证链路。
- 客户端负责执行、观察、记录、回放和导出 evidence。
- WorldEngine 负责世界生成、运行、Agent、LLM/provider、evaluator/checker 和最终
  PASS 依据。
- Validation Client 不拥有 provider key，不调用 LLM，不生成权威世界事实，不判定
  WorldEngine PASS。

## 分阶段验证链路

完整用例按阶段推进。每个阶段内部可以再分层执行：

| 阶段 | 验证深度 | 覆盖范围 |
| --- | --- | --- |
| Phase 1 | 基础功能验证 | preflight、创建世界、短 tick、基础 evidence |
| Phase 2 | 生命周期验证 | runtime controls、events、snapshots、replay、direction |
| Phase 3 | Agent 深度验证 | Agent life、memory/rest continuity、inspection surfaces |
| Phase 4 | 完整自主验证 | result directory、checker/scorecard、second-Agent review |

每阶段可以 `pass`、`fail`、`blocked`、`not_run`。前阶段 blocked 不允许后阶段伪造
pass。阶段内的 L0-L8 分层定义见 `phased-validation-plan.zh.md`。

Agent 自主测试必须使用 `agent-autonomous-operation-script.zh.md` 中的逐步操作脚本，
并按 `operation-recording-contract.zh.md` 保存每一步操作记录、API 摘要、截图、
console log 和 transcript。

## 当前判断

当前客户端方向正确，但现有 v0.8 flow 还不是完整验证 suite：

- Runtime 按钮不能只记录本地操作，必须真实调用 WorldEngine runtime/session API。
- Evidence 不能只导出 v0.8/v0.9 handoff artifact，应覆盖完整 suite 的结果目录。
- 用例不能只叫 `worldengine-full-lifecycle-autonomous` 或 `llm-backed-full-lifecycle`；
  它们应成为完整 suite 下的层级或子场景。
- WorldEngine 版本差异应通过 capability discovery 和 blocked taxonomy 处理。

## 范围

- 定义完整验证 suite 的 product contract。
- 输出完整分阶段验证文档。
- 更新客户端路由、roadmap 和验证入口。
- 定义 scenario matrix、artifact contract、phased runbook、Agent 自主操作脚本、
  操作记录契约和后续实现约束。

## 非目标

- 不实现 runtime/API/UI/test 代码。
- 不启动服务。
- 不运行完整验证。
- 不声明 WorldEngine PASS。
- 不提交 provider live call。

## 完成标准

- 后续 Agent 能使用本 milestone 直接实现或执行完整验证 suite。
- Validation Client 可以按 `phased-validation-plan.zh.md` 分阶段跑用例。
- Agent 自主测试有明确到按钮、输入、下载和截图的操作步骤。
- 每个操作的详细记录要求可由 `operation-recording-contract.zh.md` 验证。
- 文档不再暗示 Validation Client 要跟随 WorldEngine 每个迭代生成验证计划。
- 当前缺口清楚落到客户端 suite 能力，而不是 WorldEngine 版本命名。
