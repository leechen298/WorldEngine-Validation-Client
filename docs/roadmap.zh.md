# Roadmap

状态：规划草案

## v0.1 Foundation

目标：建立可运行的本地验证客户端骨架。

范围：

- React/Vite/TypeScript 前端。
- FastAPI/Python 后端。
- SQLite 本地存储。
- 会话库第一屏。
- WorldEngine public API 连接检查。
- commit point / branch 存储模型。
- 运行控制台骨架。
- evidence bundle metadata endpoint。

非目标：

- 完整像素模拟。
- 实时 tick streaming。
- 完整回放渲染。
- 完整 evidence bundle 导出。
- 玩家角色控制。

## v0.2 WorldEngine Integration

目标：通过 WorldEngine 公开 API 创建世界并读取公开运行状态。

范围：

- world creation API 对接。
- public manifest / OpenAPI 能力发现。
- 公开初始状态和 visualization payload 接入。
- 基础错误和脱敏 API trace。

## v0.3 Runtime Visualization

目标：把 WorldEngine 公开状态转成可观察的像素世界画面。

范围：

- PixiJS 地图画面。
- Agent 公开状态面板。
- 事件气泡。
- 世界事件 / Agent life log。
- 基础 tick 显示。

## v0.4 Replay And Branching

目标：支持基于 commit point、snapshot 和 diff 的回放与分支世界线。

范围：

- snapshot + diff 重建。
- 时间线 scrubber。
- commit point 浏览。
- 从 commit point 创建 branch。
- branch 切换和运行记录。

## v0.5 Director Guidance

目标：支持高层自然语言导演引导。

范围：

- 导演输入 UI。
- 提交给 WorldEngine。
- pending / accepted / applied 状态展示。
- 确保引导只影响外部环境和事件趋势，不直接修改 Agent 内心。

## v0.6 Evidence Bundle

目标：导出本地会话证据包，供 Codex、人类或 WorldEngine 后续评审使用。

范围：

- session metadata。
- event log。
- state diffs。
- snapshots。
- replay index。
- 脱敏 API trace。
- WorldEngine 公开 evaluator 输出。
