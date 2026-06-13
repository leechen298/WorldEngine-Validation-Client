# Agent Execution Handoff

英文镜像：`agent-execution-handoff.md`。

## 实现聊天 Prompt

```text
开发 Validation Client v0.9.1 complete-suite-runner-and-operation-recording。

目标：
- 实现 complete-worldengine-validation-suite E2E runner。
- Agent 按 docs/milestones/v0.9-complete-worldengine-validation-suite/agent-autonomous-operation-script.zh.md 操作 UI。
- 每个 UI 操作都写入 operation-log.jsonl。
- 每个 API 请求/响应摘要都写入 api-log.jsonl。
- 输出 api-summary.json、console.log、transcript.md、screenshots/ 和完整 result directory。
- WorldEngine 不可达或 capability 缺失时输出 structured BLOCKED，不能伪造 PASS。
- 不调用 LLM provider，不管理 provider key，不生成权威世界事实，不写 Agent private memory/goal/thought。

执行顺序：
1. 读取 AGENTS.md。
2. 读取 docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/README.zh.md。
3. 读取 plan.zh.md、test-plan.zh.md、scenario-assertion-matrix.zh.md、result-directory-contract.zh.md。
4. 按 plan.zh.md Task 1-4 执行，每个 task 独立 RED/GREEN、验证、commit。
5. 最后运行 test-plan.zh.md 的 Required Commands。

报告：
- 只能根据 E2E result directory、redaction、checker/scorecard/second-Agent review 报 PASS/PARTIAL/BLOCKED/FAIL。
- 不要把 UI smoke 当完整 WorldEngine 验证通过。
```

## 自主验证聊天 Prompt

```text
执行 Validation Client complete-worldengine-validation-suite。

要求：
- 使用 WorldEngine-Validation-Client 作为客户端和 evidence 承载面。
- 按 agent-autonomous-operation-script.zh.md 执行 Phase 1-4。
- 保存 operation-log.jsonl、api-log.jsonl、api-summary.json、console.log、transcript.md、screenshots/。
- 导出 result directory。
- 如果 WorldEngine checker 可用，运行 checker；否则记录 blocked/checker_gap。
- 第二 Agent 只读复核 result directory。
- 最终只报告 PASS/PARTIAL/BLOCKED/FAIL。
```

