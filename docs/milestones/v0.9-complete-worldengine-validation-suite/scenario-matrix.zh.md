# Scenario Matrix

英文镜像：`scenario-matrix.md`。

## 主场景

```text
complete-worldengine-validation-suite
```

这是唯一完整验证主场景。其他场景是它的层级或子场景。

## 阶段和层级

| 阶段 | 包含层级 | 阶段目标 |
| --- | --- | --- |
| Phase 1 | L0、L1、L2-min、L8-min | 基础功能验证 |
| Phase 2 | L2、L3、L4 | 生命周期验证 |
| Phase 3 | L5、L6、L7 | Agent 深度验证 |
| Phase 4 | L8、checker/review | 完整自主验证 |

## 层级明细

| ID | 子场景 | 必需操作 | 必需 artifact | PASS 来源 |
| --- | --- | --- | --- | --- |
| L0 | `preflight-capability-discovery` | 读取 health / manifest / OpenAPI / capabilities | `capability-discovery.json` | client evidence + redaction |
| L1 | `world-creation` | 输入基础世界观，创建世界/session | `world-creation-summary.json`、`session-summary.json` | WorldEngine public response |
| L2 | `runtime-control` | run N ticks、single tick、pause、resume | `runtime-control-summary.json`、`api-log.jsonl` | WorldEngine public response |
| L3 | `timeline-evidence` | 采集 events、snapshots、diff/replay、branch | `timeline-evidence.json` | replay/diff evidence |
| L4 | `direction-boundary` | 提交高层方向，验证不直接写 Agent 内部 | `direction-boundary-summary.json` | WorldEngine classification |
| L5 | `agent-life` | Agent observe、intent/action/wait/rest | `agent-evidence.json` | WorldEngine public Agent evidence |
| L6 | `memory-continuity` | memory summary、rest/sleep consolidation | `memory-continuity-summary.json` | WorldEngine public memory evidence |
| L7 | `inspection-surfaces` | narrative projection、diagnostic dialogue | `inspection-evidence.json` | read-only inspection evidence |
| L8 | `evidence-handoff` | 导出 result directory、redaction、checker/review | `result.json`、`scorecard-input.json`、`redaction-report.json` | checker/scorecard/second-Agent |

## Forbidden Operations

- Validation Client 直接调用 LLM provider。
- Validation Client 保存或展示 provider key。
- Validation Client 生成权威世界事实。
- Validation Client 把本地 UI 状态当成 WorldEngine runtime 状态。
- Validation Client 把 direct API harvest 伪装成用户/Agent 操作日志。
- Validation Client 修改 Agent memory、goal、thought、identity、relationship 或 hidden context。

## 结果枚举

- `pass`
- `fail`
- `blocked`
- `not_run`

完整 suite 的最终结论按最严重层级汇总；任何 required layer 缺证据时不能 PASS。
