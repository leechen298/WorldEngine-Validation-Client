# 人工验证模板

英文镜像：`human-validation-template.md`。

用途：人类在 Codex 自主验证和第二 Agent 复核之后，用本文模板生成
`validation-runs/YYYY-MM-DD-human.zh.md`。

人工验证不重复命令测试，不判断内部实现正确性，只判断可视化体验、世界可观察
性、Agent 公开行为可信度、导演边界、回放/世界线和证据可复盘性。

## 0. 结论

结论只能选择一个：

```text
HUMAN_PASS
HUMAN_PARTIAL
HUMAN_FAIL
```

当前结论：

```text
<one allowed conclusion>
```

一句话原因：

```text
<short human-facing reason>
```

## 1. Inputs Reviewed

```text
Codex report:
Agent review report:
operation log:
screenshots directory:
evidence bundle:
Web URL if reopened:
session_id:
worldengine_world_id:
branch_id:
```

必须确认：

- [ ] Codex 结论是 `PASS_READY_FOR_HUMAN_VALIDATION`。
- [ ] 第二 Agent 结论是 `READY_FOR_HUMAN_VALIDATION`。
- [ ] 人工验证不是在自动验证缺口未修复时进行。

如果上述条件不满足，本记录只能写 `HUMAN_PARTIAL` 或 `HUMAN_FAIL`。

## 2. Session Library Experience

评分：

```text
理解成本: 1-5
存档/世界线入口清晰度: 1-5
WorldEngine 连接状态清晰度: 1-5
```

观察：

```text
what worked:
what confused me:
must fix:
```

## 3. World Creation Experience

评分：

```text
基础世界观输入清晰度: 1-5
创建过程反馈: 1-5
进入运行控制台连贯性: 1-5
```

观察：

```text
world prompt used:
visible creation result:
must fix:
```

## 4. World Observability

评分：

```text
像素画布可读性: 1-5
公开状态摘要可读性: 1-5
事件日志解释力: 1-5
画布/状态/日志一致性: 1-5
```

判断：

```text
Can I tell what is happening?
Can I connect visual state to events?
Can I explain the current world state to another person?
must fix:
```

## 5. Agent Public Life

评分：

```text
Agent 公开状态可读性: 1-5
Agent 行为自然性: 1-5
Agent 与事件反应关系: 1-5
Agent 生活感: 1-5
```

判断：

```text
What did the Agent appear to want or do?
Did the Agent react to public events naturally?
What felt mechanical or unclear?
must fix:
```

注意：人工验证只能评价公开表现，不评价 Agent private memory、private goal 或
self_state。

## 6. Director Guidance Boundary

评分：

```text
高层方向输入清晰度: 1-5
pending / accepted / applied 状态清晰度: 1-5
是否保持外部事件和环境趋势边界: 1-5
是否没有变成玩家直接操作: 1-5
```

判断：

```text
guidance text:
visible effect:
Did it feel high-level?
Did it seem to force Agent internal state?
must fix:
```

## 7. Replay and World Lines

评分：

```text
replay slider 可理解性: 1-5
commit point 可理解性: 1-5
branch 创建可理解性: 1-5
branch 切换可理解性: 1-5
```

判断：

```text
Can I revisit a prior visible state?
Does branch feel like a named world line?
Did the UI keep branch semantics limited to naming, switching, replay, and continued progression?
must fix:
```

## 8. Evidence Reviewability

评分：

```text
evidence bundle 可理解性: 1-5
screenshots 与操作记录对应性: 1-5
日志复盘能力: 1-5
问题定位能力: 1-5
```

判断：

```text
Can another human replay the validation story from evidence?
What evidence was missing?
must fix:
```

## 9. Human Findings

```text
Finding ID:
Severity: P1/P2/P3
Area:
Evidence:
Human impact:
Required follow-up:
Blocks next iteration: yes/no
```

## 10. Final Decision

如果结论为 `HUMAN_PASS`，必须同时满足：

- [ ] 世界可观察。
- [ ] Agent 公开行为有基本自然性。
- [ ] 导演引导保持高层边界。
- [ ] replay 和 branch 可理解为世界线。
- [ ] evidence bundle 足够复盘。
- [ ] 没有 P1 blocker。

如果任一项不满足，结论不能是 `HUMAN_PASS`。
