# v0.5 Director Guidance Review

状态：计划已创建 / 待实现

日期：2026-06-03

## 结论

v0.5 目标是基础 Director Guidance：运行控制台提交高层自然语言方向，后端记录
director intent，并在可用时通过 WorldEngine public API 提交和记录公开状态。

当前仅完成 milestone 文档创建。产品代码尚未开始实现，不能声明 v0.5 已完成。

## Task Records

### Task 1: v0.5 里程碑文档

- Commit: `7fcf84b`
- Files:
  - `docs/README.zh.md`
  - `docs/milestones/v0.5-director-guidance/README.zh.md`
  - `docs/milestones/v0.5-director-guidance/plan.zh.md`
  - `docs/milestones/v0.5-director-guidance/review.zh.md`
- Commands:
  - `git diff --check`: 通过
- Scope review:
  - 已创建 v0.5 milestone 文档，明确 Director Guidance 目标、范围、非目标、
    task 顺序、验证命令和逐 task commit 要求。
  - 计划明确导演引导只表达高层外部世界方向，不直接修改 Agent 内部状态、记忆、
    目标、身份、关系、自我状态或行为决定。
  - 计划要求 WorldEngine 连接只能通过 public API、manifest 或 OpenAPI 发现路径，
    不依赖私有源码、私有 helper、私有 prompt、LLM key 或 provider secret。
- Notes:
  - Task 1 仅创建 v0.5 milestone 文档，不包含产品代码实现。
  - Task 1 commit hash 已在后续 docs-only 记录提交中补充。

## 范围审核

- 是否只通过 public API / manifest / OpenAPI 连接 WorldEngine：待实现。
- 是否未引入客户端 LLM key 管理：待实现。
- 是否未直接调用 LLM provider：待实现。
- 是否未生成权威世界事实：待实现。
- 是否未直接修改 Agent 内部状态、记忆、目标、身份、关系、自我状态或行为决定：
  待实现。
- 是否未展示私有 Agent 内部状态、隐藏推理或私有 prompt：待实现。
- 是否未引入玩家角色控制、物品放置或手动事件注入：待实现。

## 遗留问题

- 后端 director intent 本地 API 尚未实现。
- WorldEngine public director guidance 提交适配尚未实现。
- 前端 typed client / store 尚未实现。
- 运行控制台导演引导 UI 尚未接入真实 API。
- 完整 evidence bundle 导出仍属于后续 milestone。
