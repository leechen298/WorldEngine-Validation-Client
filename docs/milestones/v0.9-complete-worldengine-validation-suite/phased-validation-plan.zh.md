# Phased Validation Plan

英文镜像：`phased-validation-plan.md`。

## 目标

这份文档是 Validation Client 的稳定验证用例。它不跟随 WorldEngine 的迭代拆分。

验证问题只有一个：

```text
当前连接的 WorldEngine 是否能正常工作？
```

验证可以分阶段逐步深入。每个阶段都必须输出 evidence，不能用人工感觉或 UI smoke
替代。

## Phase 1：基础功能验证

目的：确认 WorldEngine 可连接、可创建世界、可短时间运行，并且客户端能导出基础证据。

包含层级：

- L0 `preflight-capability-discovery`
- L1 `world-creation`
- L2-min `short-runtime-smoke`
- L8-min `basic-evidence-export`

必需操作：

1. 读取 WorldEngine health / manifest / OpenAPI。
2. 输入基础世界观。
3. 创建世界或 session。
4. 运行最小 tick，例如 1 到 3 tick。
5. 导出基础 evidence bundle。

PASS 条件：

- WorldEngine public API 可达。
- 创建世界成功。
- 至少一个 runtime/tick 相关 public response 成功。
- evidence bundle 包含 operation log、API summary、redaction report。

BLOCKED 示例：

- WorldEngine 不可达。
- public world creation capability 缺失。
- 客户端无法导出 evidence。

## Phase 2：生命周期验证

目的：确认世界不是只创建成功，而是能持续推进、产生事件、留下可回放证据。

包含层级：

- L2 `runtime-control`
- L3 `timeline-evidence`
- L4 `direction-boundary`

必需操作：

1. bounded run N ticks。
2. single tick。
3. pause / resume。
4. 读取 events、snapshots、diff 或 replay view。
5. 创建或切换 branch。
6. 输入高层自然语言方向。
7. 记录方向 queued / accepted / rejected / applied public status。

PASS 条件：

- runtime controls 真实调用 WorldEngine public API。
- tick、event 或 snapshot evidence 可以互相对应。
- replay 或 branch evidence 可用。
- 用户方向不会直接写 Agent internal memory / goal / thought。

FAIL 示例：

- Run 按钮只改本地 UI 状态，没有 WorldEngine API trace。
- 用户方向被直接当成最终事实写入世界。
- direct API harvest 被写成用户操作日志。

## Phase 3：Agent 深度验证

目的：确认 Agent 不只是一次 action，而是有公开可观察的生活、等待、休息、记忆和连续性证据。

包含层级：

- L5 `agent-life`
- L6 `memory-continuity`
- L7 `inspection-surfaces`

必需操作：

1. 读取 Agent public state。
2. 触发或观察 Agent observe。
3. 记录 Agent intent / action / wait / rest 中至少一种合法状态。
4. 读取 memory summary。
5. 执行 rest / sleep-like consolidation，如果 WorldEngine 支持。
6. 运行 narrative projection。
7. 运行 diagnostic dialogue / inspection。

PASS 条件：

- Agent 行为证据来自 WorldEngine public evidence。
- 允许没有每 tick 意图，但必须有观察、等待、行动或休息的公开状态。
- memory / continuity 只导出 public summary，不泄露 private memory。
- narrative / diagnostic 是外部 inspection，不写入 canonical world state 或 Agent memory。

BLOCKED 示例：

- 当前 WorldEngine 没有 Agent public state endpoint。
- 当前 WorldEngine 没有 memory/consolidation endpoint。
- inspection surface 不存在。

## Phase 4：完整自主验证

目的：由 Codex Agent 按普通用户视角完整操作 Validation Client，导出 result directory，
再交给 WorldEngine checker/scorecard 或第二 Agent 复核。

包含层级：

- L8 `evidence-handoff`
- `second-agent-review`
- `checker-or-scorecard`

必需操作：

1. Agent 操作 Web UI，而不是只直接 curl API。
2. 记录点击、输入、下载、可见 UI 结果。
3. public API harvest 单独进入 API log。
4. 导出完整 result directory。
5. 运行可用 checker / scorecard。
6. 第二 Agent 只读复核。

PASS 条件：

- required artifacts 完整。
- redaction PASS。
- checker/scorecard 或 second-Agent review 支持 PASS。
- 没有 UI smoke 冒充完整验证 PASS。

## 总结论规则

| 阶段结果 | 总结论影响 |
| --- | --- |
| Phase 1 PASS，后续未跑 | `PARTIAL` |
| Phase 1-2 PASS，Phase 3 blocked | `PARTIAL / BLOCKED` |
| Phase 1-3 PASS，Phase 4 checker blocked | `PARTIAL / BLOCKED` |
| Phase 1-4 全部 PASS | `PASS` |
| 任一阶段 redaction fail | `FAIL` |
| 任一阶段发现产品行为阻塞缺陷 | `FAIL` |

## 稳定性规则

- WorldEngine 新增能力时，添加 capability mapping，不新增一套按 WorldEngine 版本命名的用例。
- WorldEngine 缺能力时，记录 blocked taxonomy，不改写用例结构。
- Validation Client 的验证用例名称保持稳定。
