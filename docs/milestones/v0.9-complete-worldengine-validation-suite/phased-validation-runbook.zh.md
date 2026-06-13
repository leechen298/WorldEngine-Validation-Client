# Phased Validation Runbook

英文镜像：`phased-validation-runbook.md`。

## 使用方式

Codex Agent 或人工验证者按阶段执行。每个阶段结束后都可以停下来输出结论。

不要跳过前置阶段。如果前置阶段 blocked，后续阶段只能 `not_run` 或 `blocked`。

本文件只描述阶段顺序。Agent 自主测试必须按
`agent-autonomous-operation-script.zh.md` 执行具体按钮点击、输入、下载、截图和
closeout 步骤，并按 `operation-recording-contract.zh.md` 保存逐操作记录。

## Phase 1 Runbook

1. 启动或连接 WorldEngine。
2. 启动 Validation Client API 和 Web。
3. 打开会话库。
4. 确认 WorldEngine 连接状态。
5. 输入基础世界观并创建世界。
6. 执行最小 tick。
7. 下载基础 evidence。
8. 输出 Phase 1 结果。

## Phase 2 Runbook

1. 在 Phase 1 session 上继续。
2. 运行 N ticks。
3. single tick。
4. pause / resume。
5. 查看 events / snapshots / replay。
6. 创建 branch。
7. 输入高层方向。
8. 下载 lifecycle evidence。
9. 输出 Phase 2 结果。

## Phase 3 Runbook

1. 读取 Agent public state。
2. 观察或触发 Agent step。
3. 记录 action / wait / rest。
4. 读取 memory summary。
5. 执行 consolidation，如果支持。
6. 运行 narrative projection。
7. 运行 diagnostic inspection。
8. 下载 Agent / inspection evidence。
9. 输出 Phase 3 结果。

## Phase 4 Runbook

1. 导出完整 result directory。
2. 运行可用 WorldEngine checker / scorecard。
3. 第二 Agent 只读复核。
4. 扫描 redaction。
5. 输出最终 PASS / PARTIAL / BLOCKED / FAIL。

## 记录要求

每阶段都必须记录：

- 每个具体操作是否执行，且必须能回溯到 operation script 的 `step_id`。
- artifact 是否生成。
- forbidden operation 是否触犯。
- redaction 是否通过。
- PASS 来源。
- blocked/fail taxonomy。

完整记录最低包括：

- `operation-log.jsonl`：逐 UI 操作记录。
- `api-log.jsonl`：逐 API 请求/响应摘要。
- `api-summary.json`：按阶段聚合 API 状态。
- `console.log`：浏览器和前端公开错误摘要。
- `transcript.md`：Agent 自主执行叙事记录。
- `screenshots/`：每阶段截图和关键 before/after 截图。

## Stop Rules

- 任何 secret/raw/private marker 泄露：立即 FAIL。
- UI smoke 不能作为完整 PASS。
- 客户端不能直接调用 provider。
- 客户端不能生成权威世界事实。
- 缺少任一已执行操作的 `operation-log.jsonl` 记录时，最终不能 PASS。
- direct API harvest 不能写成用户点击，必须进入 `api-log.jsonl`。
