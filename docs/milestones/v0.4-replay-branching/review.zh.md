# v0.4 Replay And Branching Review

状态：计划已创建 / 实现待开始

日期：2026-06-03

## 结论

v0.4 目标是基础 Replay And Branching：后端从公开 snapshot + state diff 重建
replay view，前端运行控制台展示时间线 scrubber、commit point 浏览、branch 切换
和从 commit point 创建 branch 的基础体验。

当前仅完成 milestone 文档创建。实现尚未开始。

## Task Records

### Task 1: v0.4 里程碑文档

- Commit: `待提交`
- Files:
  - `docs/README.zh.md`
  - `docs/milestones/v0.4-replay-branching/README.zh.md`
  - `docs/milestones/v0.4-replay-branching/plan.zh.md`
  - `docs/milestones/v0.4-replay-branching/review.zh.md`
- Commands:
  - `git diff --check`: 通过
- Scope review:
  - 已创建 v0.4 milestone 文档，明确 Replay And Branching 目标、范围、非目标、
    task 顺序、验证命令和逐 task commit 要求。
- Notes:
  - Task 1 仅创建 v0.4 milestone 文档，不包含产品代码实现。
  - Git commit hash 无法在同一个提交内自引用后保持不变，因此本记录将在后续
    docs-only review 更新中补充可见 hash。

## 范围审核

- 是否只通过 public API / 本地公开 evidence 数据连接 WorldEngine：待实现后验证。
- 是否未引入客户端 LLM key 管理：待实现后验证。
- 是否未直接调用 LLM provider：待实现后验证。
- 是否未生成权威世界事实：待实现后验证。
- 是否未引入玩家角色控制：待实现后验证。
- 是否未引入 WorldEngine 私有源码、私有路径或内部 helper：待实现后验证。
- 是否未展示私有 Agent 内部状态、记忆、目标、隐藏推理或自我状态：待实现后验证。

## 遗留问题

- 后端 replay read model API 尚未实现。
- commit point / branch 上下文深化尚未实现。
- 前端 replay / branch typed client 和状态尚未实现。
- 时间线 scrubber、commit point 浏览、branch 切换和创建 UI 尚未实现。
