# v0.1 Foundation

状态：代码骨架已实现 / v0.1-review-fix 验证通过 / 历史流程偏离已记录

## 目标

建立 `WorldEngine-Validation-Client` 的第一版可运行骨架：Web 前端、本地
FastAPI 后端、SQLite 存储、会话库、WorldEngine 连接检查、commit
point/branch 数据模型和运行控制台骨架。

## 范围

允许实现：

- React/Vite/TypeScript 前端骨架。
- Python/FastAPI 后端骨架。
- SQLite 数据库。
- session 创建和列表。
- commit point / branch 存储模型。
- WorldEngine public health / manifest 连接检查。
- evidence bundle metadata endpoint。
- 简单运行控制台 UI。

禁止实现：

- 客户端 LLM API key 管理。
- 客户端直接调用 LLM。
- 客户端生成权威世界事实。
- 私有 WorldEngine 集成。
- 玩家角色控制。
- 完整像素模拟。
- 实时 tick streaming。
- 完整 evidence bundle 导出。

## 入口

当用户说 `开发 v0.1` 或 `实现 v0.1`，先读取：

```text
docs/specs/validation-client-design.zh.md
docs/milestones/v0.1-foundation/plan.zh.md
docs/milestones/v0.1-foundation/review.zh.md
```

然后按 `plan.zh.md` 实现，并在完成后更新 `review.zh.md`。

## 当前结论

截至 2026-06-02，本 milestone 的代码骨架可以运行，并已完成一次
`v0.1-review-fix`：

- 前端会话库现在展示真实 `/health/worldengine` 结果，而不是把本地 FastAPI
  `/health` 误报为 WorldEngine 连接状态。
- 默认 SQLite 路径固定解析到 `apps/api/.worldengine-validation-client/client.sqlite3`。
- branch 创建的 `snapshot_reference` 来自 commit point，不接受客户端任意覆盖。
- branch 加载和创建失败会收尾 loading 状态，并在运行控制台展示错误。
- `review.zh.md` 已补充历史流程偏离说明和本轮验证证据。

限制：v0.1 主体实现历史没有按当前 `workflow.md` 做逐 task 独立提交，因此不把
原始 v0.1 历史声明为“按强流程 clean pass”。该事实只能记录，不能通过补丁伪造。
