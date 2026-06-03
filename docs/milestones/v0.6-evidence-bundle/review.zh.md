# v0.6 Evidence Bundle Review

状态：文档创建完成 / 实现待开始

日期：2026-06-04

## 结论

v0.6 目标是完整 Evidence Bundle：在不越过 WorldEngine public API 和本地客户端
证据边界的前提下，导出可下载、可审计、可脱敏检查的本地 session 证据包。

当前仅完成 milestone 文档创建和计划边界确认。产品代码实现尚未开始，后续必须
从 `plan.zh.md` Task 2 开始，按 numbered task 顺序实现、验证、记录并逐 task
提交。

## Task Records

### Task 1: v0.6 里程碑文档

- Commit: `pending`
- Files:
  - `docs/README.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/README.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/plan.zh.md`
  - `docs/milestones/v0.6-evidence-bundle/review.zh.md`
- Commands:
  - `git diff --check`: 通过
- Scope review:
  - 已创建 v0.6 milestone 文档，明确 Evidence Bundle 目标、范围、非目标、task
    顺序、验证命令和逐 task commit 要求。
  - 计划明确 evidence bundle 是本地会话证据包，不是权威 evaluator 报告。
  - 计划要求 bundle 仅导出 public API 和本地客户端允许保存的公开/脱敏记录。
  - 计划禁止保存或展示 LLM key、provider secret、private prompt、WorldEngine
    私有 internals、Agent 私有内部状态、hidden context 或 evaluator oracle
    internals。
- Notes:
  - Task 1 仅创建 v0.6 milestone 文档，不包含产品代码实现。

## 范围审核

- 是否只通过 public API / manifest / OpenAPI 连接 WorldEngine：待后续实现确认。
- 是否未引入客户端 LLM key 管理：Task 1 是。
- 是否未直接调用 LLM provider：Task 1 是。
- 是否未生成权威世界事实或 evaluator 结论：Task 1 是。
- 是否未直接修改 Agent 内部状态、记忆、目标、身份、关系、自我状态或行为决定：
  Task 1 是。
- 是否未展示私有 Agent 内部状态、hidden context、私有 prompt 或 evaluator oracle：
  Task 1 是。
- 是否所有 planned numbered tasks 均已记录并有 task-scoped commit：否，仅 Task 1
  进行中。
- 是否 broad checks 已通过：否，尚未进入总体验证。

## 遗留问题

- 后端完整 evidence bundle schema / manifest 尚未实现。
- 后端 bundle 内容组装、排序、脱敏检查和下载 endpoint 尚未实现。
- 前端 typed client / store / evidence panel / 下载入口尚未实现。
- v0.6 尚未完成总体验证和 review 收口。
