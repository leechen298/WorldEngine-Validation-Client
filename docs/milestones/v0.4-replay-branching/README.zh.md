# v0.4 Replay And Branching

状态：实现完成 / 验证通过

## 目标

在 v0.3 的 Runtime Visualization 基础上，支持基于本地公开 evidence 的回放和
世界线分支操作。v0.4 的核心是让用户可以浏览 commit point，选择目标 tick 重建
公开运行视图，并从某个 commit point 创建和切换本地 branch。

v0.4 不改变 WorldEngine 权威运行状态，也不实现实时 tick streaming 或导演引导
提交闭环。回放和分支都是客户端侧的观察、证据和后续运行记录功能。

## 范围

允许实现：

- 后端基于公开 snapshot 和正向 state diff 重建指定 branch / tick 的 replay view。
- 后端暴露 commit point 浏览、branch 切换上下文和从 commit point 创建 branch 的
  本地 API。
- 前端 runtime store 和 typed client 支持 replay target、branch 列表、commit point
  列表和 replay view。
- 运行控制台展示时间线 scrubber、commit point 浏览、branch 切换和从当前 commit
  point 创建 branch 的基础 UI。
- replay / branch UI 只展示后端过滤后的公开 visualization、Agent public state、
  world log 和 Agent life log。

禁止实现：

- 客户端 LLM API key 管理。
- 客户端直接调用 LLM provider。
- 客户端生成权威世界事实。
- WorldEngine 私有源码、私有路径或内部 helper 依赖。
- 展示或保存私有 Agent 内部状态、记忆、目标、身份推理、自我状态或隐藏思考。
- 直接修改 Agent 内部状态、记忆、目标、身份或行为决定。
- 实时 tick streaming。
- 导演引导提交闭环。
- 完整 evidence bundle 导出。
- 玩家角色控制。

## 入口

当用户说 `开发 v0.4`、`实现 v0.4`、`继续 v0.4` 或 `/goal 开发 v0.4`，
先读取：

```text
docs/specs/validation-client-design.zh.md
docs/milestones/v0.4-replay-branching/README.zh.md
docs/milestones/v0.4-replay-branching/plan.zh.md
docs/milestones/v0.4-replay-branching/review.zh.md
docs/adr/0001-tech-stack.zh.md
docs/agent-guides/routing.md
docs/agent-guides/workflow.md
docs/agent-guides/boundaries.md
```

然后严格按 `plan.zh.md` 的 numbered task 顺序执行。每个 numbered task
必须实现、验证、记录到 `review.zh.md` 并提交后，才能进入下一 task。

## 当前结论

v0.4 已完成基础 Replay And Branching：后端提供 `replay-view` read model，
从公开 snapshot + state diff 重建指定 branch / tick 的公开运行视图；timeline API
返回 branch context 和 commit point 公开摘要；前端运行控制台支持时间线 scrubber、
commit point 浏览、branch 切换，以及从当前 commit point 创建新 branch。

后续范围仍是实时 tick streaming、运行推进 API、导演引导提交闭环和完整 evidence
bundle 导出。
