# v0.1 Foundation

状态：计划完成 / 待实现

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
