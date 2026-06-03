# v0.3 Runtime Visualization

状态：计划已创建 / 实现待开始

## 目标

把 WorldEngine 通过公开接口返回并已由本地后端保存的公开运行状态，转换成可
观察的运行控制台画面。v0.3 交付的是基础 Runtime Visualization：像素地图、公开
Agent 状态、公开事件气泡、world / Agent log 和基础 tick 显示。

v0.3 不实现实时 tick streaming，也不实现回放、分支深化、导演引导提交闭环或完
整 evidence bundle 导出。

## 范围

允许实现：

- 后端提供本地 runtime view API，只从已保存的公开 snapshot、公开 event 和公开
  visualization payload 生成展示数据。
- 前端 typed API 和 store 状态读取 runtime view。
- PixiJS 基础地图画面，使用 public visualization payload 渲染 tiles / entities 的
  初始静态视图。
- Agent 公开状态面板，只展示 WorldEngine 公开 payload 中允许展示的字段。
- 公开事件气泡、world log、Agent life log 和基础 tick 显示。
- 缺少可视化 payload 时的 empty / degraded UI。

禁止实现：

- 客户端 LLM API key 管理。
- 客户端直接调用 LLM provider。
- 客户端生成权威世界事实。
- WorldEngine 私有源码、私有路径或内部 helper 依赖。
- 展示或保存私有 Agent 内部状态、记忆、目标、身份推理、自我状态或隐藏思考。
- 直接修改 Agent 内部状态、记忆、目标、身份或行为决定。
- 实时 tick streaming。
- 完整 replay / branch 重建。
- 完整 evidence bundle 导出。
- 玩家角色控制。

## 入口

当用户说 `开发 v0.3`、`实现 v0.3`、`继续 v0.3` 或 `/goal 开发 v0.3`，
先读取：

```text
docs/specs/validation-client-design.zh.md
docs/milestones/v0.3-runtime-visualization/README.zh.md
docs/milestones/v0.3-runtime-visualization/plan.zh.md
docs/milestones/v0.3-runtime-visualization/review.zh.md
docs/adr/0001-tech-stack.zh.md
docs/agent-guides/routing.md
docs/agent-guides/workflow.md
docs/agent-guides/boundaries.md
```

然后严格按 `plan.zh.md` 的 numbered task 顺序执行。每个 numbered task
必须实现、验证、记录到 `review.zh.md` 并提交后，才能进入下一 task。

## 当前结论

v0.3 文档已建立，产品实现尚未开始。下一步应从 Task 2 开始实现本地 runtime
view API，并保持 WorldEngine public API 边界。
