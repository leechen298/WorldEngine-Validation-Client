# v0.2 WorldEngine Integration

状态：实现完成 / 总体验证通过 / review 修复已收口

## 目标

通过 WorldEngine 公开 API 创建世界，并读取公开能力、初始运行状态和
visualization payload。v0.2 只建立外部集成闭环，不实现实时 tick streaming、
像素渲染或完整回放。

## 范围

允许实现：

- public manifest / OpenAPI 能力发现。
- WorldEngine world creation public API 代理。
- 创建世界后保存本地 session、main branch、初始 snapshot 和 commit point。
- 接入公开初始状态和 visualization payload。
- 记录基础、脱敏 API trace。
- 前端会话库创建世界入口。
- 前端运行控制台展示初始公开状态摘要和 visualization payload 摘要。

禁止实现：

- 客户端 LLM API key 管理。
- 客户端直接调用 LLM provider。
- 客户端生成权威世界事实。
- WorldEngine 私有源码、私有路径或内部 helper 依赖。
- 直接修改 Agent 内部状态、记忆、目标、身份或行为决定。
- 实时 tick streaming。
- 完整 PixiJS 像素模拟。
- 完整 evidence bundle 导出。
- 玩家角色控制。

## 入口

当用户说 `开发 v0.2`、`实现 v0.2`、`继续 v0.2` 或 `/goal 开发 v0.2`，
先读取：

```text
docs/specs/validation-client-design.zh.md
docs/milestones/v0.2-worldengine-integration/README.zh.md
docs/milestones/v0.2-worldengine-integration/plan.zh.md
docs/milestones/v0.2-worldengine-integration/review.zh.md
docs/agent-guides/routing.md
docs/agent-guides/workflow.md
docs/agent-guides/boundaries.md
```

然后严格按 `plan.zh.md` 的 numbered task 顺序执行。每个 numbered task
必须实现、验证、记录到 `review.zh.md` 并提交后，才能进入下一 task。

## 当前结论

v0.2 已完成 WorldEngine public API 集成闭环。能力发现、public world creation
代理、本地公开状态/visualization 摘要落库、脱敏 API trace、前端创建世界入口
和运行控制台公开状态摘要均已实现并通过当前会话验证。

后续仍不属于 v0.2 的范围：实时 tick streaming、完整 PixiJS 像素渲染、完整回放
和分支操作深化、完整 evidence bundle 导出、玩家角色控制。
