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

## v0.7 Agent Autonomous Validation

目标：建立 Codex / Agent 自主验证、Agent 复核和人工验证交接流程。

范围：

- 基础 E2E / UI smoke 验证。
- Agent 以人的视角操作客户端。
- 细粒度操作日志，记录点击、输入、API 请求、响应摘要、截图和下载文件。
- 另一个 Agent 对上一轮操作日志、截图和 evidence bundle 做只读复核。
- 人工验证交接清单。
- WorldEngine LLM provider 前置评估边界。

非目标：

- 客户端管理 LLM key。
- 客户端直接调用 LLM provider。
- 客户端生成权威 evaluator 结论。
- 人工体验判断自动化。

v0.7 的 Codex / Agent PASS 只表示“可以进入人工验证”，不表示世界体验或 Agent
自然性已经通过。

## v0.8 WorldEngine v0.9 Validation Plan Optimization

目标：把客户端的测试计划、scenario 矩阵、artifact 合同、redaction 矩阵和
checker handoff 对齐 WorldEngine v0.9。

范围：

- WorldEngine v0.9 public surface discovery。
- scenario-aware evidence bundle manifest 和 artifact index。
- provider/world/rule/event/Agent/replay/narrative/diagnostic named artifacts。
- status preservation：`pass`、`fail`、`blocked`、`not_run`。
- operation log 与 direct API harvest log 分离。
- bounded runtime controls。
- scorecard、checker 和第二 Agent review 展示。

非目标：

- 客户端直接调用 LLM provider。
- 客户端管理 provider key。
- 客户端生成权威世界事实、event legality、Agent autonomy 或 PASS 结论。

v0.8 的客户端 PASS 只表示客户端证据承载和 handoff 能力满足当前门禁；WorldEngine
validation PASS 仍由 WorldEngine checker/scorecard 和第二 Agent 复核决定。

## v0.9 Complete WorldEngine Validation Suite

目标：建立一套稳定的完整验证用例，用 Validation Client 一次性、端到端验证
WorldEngine 是否能正常工作。

v0.9 不跟随 WorldEngine 的每个迭代拆分验证。WorldEngine 版本、manifest 和
capability 只是本次运行的被测对象状态；客户端验证结构保持稳定。

范围：

- `complete-worldengine-validation-suite` 主场景。
- L0-L8 分层验证：preflight、world creation、runtime、timeline、direction、
  Agent life、memory continuity、inspection surfaces、evidence handoff。
- runtime controls 必须真实驱动 WorldEngine public APIs。
- 完整 result directory、coverage matrix、command matrix、operation log、API log、
  redaction report、scorecard input 和 second-Agent review。
- 兼容 WorldEngine 当前 checker/scorecard，但不把 checker 版本作为客户端 milestone。

非目标：

- 客户端不管理 provider key。
- 客户端不直接调用 LLM provider。
- 客户端不生成权威世界事实。
- 客户端不把 UI smoke 当 WorldEngine PASS。

v0.9 的完整验证 suite 可以逐层 `pass`、`fail`、`blocked` 或 `not_run`。最终 PASS
仍由 WorldEngine checker/scorecard、redaction PASS 和 second-Agent review 支持。

## v0.9.1 Complete Suite Runner And Operation Recording

目标：把 v0.9 的完整验证方案变成可执行 runner，并确保 Agent 自主测试保存每一步
完整操作记录。

范围：

- `complete-worldengine-validation-suite` E2E runner。
- 按 v0.9 operation script 执行 Phase 1-4。
- `operation-log.jsonl` 记录每个 UI 操作。
- `api-log.jsonl` / `api-summary.json` 记录每个 API 摘要。
- `console.log`、`transcript.md`、`screenshots/` 和完整 result directory。
- WorldEngine 不可达或 capability 缺失时输出 structured `BLOCKED`，不伪造 PASS。
- 第二 Agent 只读复核输入和 result directory schema。

非目标：

- 不调用 LLM provider。
- 不管理 provider key。
- 不生成 WorldEngine 权威事实。
- 不修补 WorldEngine 缺失 capability。

v0.9.1 的测试通过只证明 Validation Client 的完整验证执行和证据承载能力。WorldEngine
是否 PASS 仍由 WorldEngine checker/scorecard 和第二 Agent review 决定。
