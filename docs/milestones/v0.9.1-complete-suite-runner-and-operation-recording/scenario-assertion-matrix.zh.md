# Scenario Assertion Matrix

英文镜像：`scenario-assertion-matrix.md`。

## 主场景

```text
complete-worldengine-validation-suite
```

## Phase 1：基础功能

| Step | UI 操作 | API evidence | 必需 artifact | PASS / BLOCKED 断言 |
| --- | --- | --- | --- | --- |
| P1-01 | 打开根页面 | none | screenshot | 页面可见，否则 blocked/client_unreachable |
| P1-02 | 读取 WorldEngine 状态 | `GET /health/worldengine` | capability-discovery.json | reachable=false -> BLOCKED |
| P1-03 | 填 Session 名称 | none | operation-log.jsonl | 输入被记录 |
| P1-04 | 填世界观 | none | operation-log.jsonl | 输入长度和公开摘要被记录 |
| P1-05 | 点击创建世界 | `POST /sessions/worldengine` | world-creation-summary.json | 201 或 blocked/world_creation |
| P1-06 | 等待运行控制 | none | screenshot | heading 可见 |
| P1-07 | 查看公开状态 | session/runtime API | session-summary.json | world id/tick 可见 |
| P1-08 | 设置 tick 数 | none | operation-log.jsonl | value=`5` |
| P1-09 | 点击 run | runtime API | runtime-control-summary.json | tick 前后可比较 |
| P1-10 | 下载基础 evidence | evidence API | result artifacts | 下载记录存在 |
| P1-11 | 截图 | none | screenshots/phase-1-final.png | 文件存在 |
| P1-12 | 阶段结论 | none | result.json | phase verdict 存在 |

## Phase 2：生命周期

| Step | UI 操作 | API evidence | 必需 artifact | PASS / BLOCKED 断言 |
| --- | --- | --- | --- | --- |
| P2-01 | 设置 20 tick | none | operation-log.jsonl | value=`20` |
| P2-02 | 点击 run | runtime API | runtime-control-summary.json | bounded run evidence |
| P2-03 | 点击 pause | runtime API | runtime-control-summary.json | status paused |
| P2-04 | 点击 resume | runtime API | runtime-control-summary.json | status running |
| P2-05 | 点击 single tick | runtime API | runtime-control-summary.json | tick +1 |
| P2-06 | 查看事件 | events API | timeline-evidence.json | events 或 blocked |
| P2-07 | 查看快照 | snapshots/replay API | timeline-evidence.json | snapshots 或 blocked |
| P2-08 | 设置 replay tick | none | operation-log.jsonl | value=`0` |
| P2-09 | 创建 branch | branch API | timeline-evidence.json | branch id/name |
| P2-10 | 提交方向 1 | direction API | direction-boundary-summary.json | 不直接写 Agent 内部 |
| P2-11 | 提交方向 2 | direction API | direction-boundary-summary.json | 不直接指定 Agent 死亡 |
| P2-12 | 下载 lifecycle evidence | evidence API | coverage-matrix.json | artifact index 完整 |
| P2-13 | 截图 | none | screenshots/phase-2-final.png | 文件存在 |
| P2-14 | 阶段结论 | none | result.json | phase verdict 存在 |

## Phase 3：Agent 深度

| Step | UI 操作 | API evidence | 必需 artifact | PASS / BLOCKED 断言 |
| --- | --- | --- | --- | --- |
| P3-01 | 打开 Agent 面板 | Agent public API | agent-evidence.json | 面板可见或 blocked |
| P3-02 | 读取 public state | Agent public API | agent-evidence.json | public state，不含 private |
| P3-03 | Agent step/observe | Agent step API | agent-evidence.json | action/wait/rest/observe |
| P3-04 | 运行观察 tick | runtime API | agent-evidence.json | 多轮公开状态 |
| P3-05 | 记录无意图状态 | none | agent-evidence.json | no-intent 合法 |
| P3-06 | 查看 memory summary | memory public API | memory-continuity-summary.json | public summary |
| P3-07 | consolidation | continuity API | memory-continuity-summary.json | pass 或 blocked |
| P3-08 | narrative projection | inspection API | inspection-evidence.json | 不写 canonical state |
| P3-09 | diagnostic dialogue | inspection API | inspection-evidence.json | 不写 Agent memory |
| P3-10 | 下载 Agent evidence | evidence API | agent/memory artifacts | 下载记录存在 |
| P3-11 | 截图 | none | screenshots/phase-3-final.png | 文件存在 |
| P3-12 | 阶段结论 | none | result.json | phase verdict 存在 |

## Phase 4：Closeout

| Step | 操作 | API/CLI evidence | 必需 artifact | PASS / BLOCKED 断言 |
| --- | --- | --- | --- | --- |
| P4-01 | 导出 result directory | evidence API | required files | 文件齐全 |
| P4-02 | 保存 console log | browser console | console.log | 文件存在 |
| P4-03 | 保存 transcript | Agent notes | transcript.md | Phase 1-4 覆盖 |
| P4-04 | redaction scan | scan command | redaction-report.json | pass 或 fail |
| P4-05 | WorldEngine checker | checker command | scorecard-input/summary | pass 或 blocked/checker_gap |
| P4-06 | 第二 Agent 复核 | review transcript | second-agent-review.md | pass 或 blocked |
| P4-07 | 最终结论 | none | result.json | PASS/PARTIAL/BLOCKED/FAIL |

## 全局断言

- 每个 executed step 必须存在 `operation-log.jsonl` entry。
- 每个 API 请求必须存在 `api-log.jsonl` entry。
- 每个 artifact 下载必须有 operation record 和 artifact ref。
- direct API harvest 不得出现在 `operation-log.jsonl`。
- 任何 redaction blocking marker 命中都必须 FAIL。

