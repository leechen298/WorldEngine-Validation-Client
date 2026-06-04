# 第二 Agent 只读复核模板

英文镜像：`agent-review-template.md`。

用途：第二 Agent 读取上一轮 Codex 自主验证证据后，用本文模板生成
`validation-runs/YYYY-MM-DD-agent-review.zh.md`。

本文不允许重新操作浏览器，不允许补写未记录事实，不允许把复核结论写成人工
验证通过。

## 0. 结论

结论只能选择一个：

```text
READY_FOR_HUMAN_VALIDATION
PARTIAL
BLOCKED
FAIL
```

当前结论：

```text
<one allowed conclusion>
```

一句话原因：

```text
<short public reason>
```

## 1. Read-Only Inputs

```text
Codex report:
operation log:
screenshots directory:
evidence bundle:
api summary:
WorldEngine manifest summary:
WorldEngine OpenAPI summary:
test/build output:
git status output:
```

必须确认：

- [ ] 所有输入存在。
- [ ] 输入来自同一个 run_id。
- [ ] 输入来自同一个 session_id。
- [ ] 未重新操作浏览器。
- [ ] 未补写 Codex 未记录的事实。

## 2. Codex Plan Compliance

检查 Codex 是否完成：

- [ ] preflight。
- [ ] backend tests。
- [ ] frontend tests。
- [ ] build。
- [ ] browser flow。
- [ ] operation log。
- [ ] screenshots。
- [ ] evidence bundle download。
- [ ] evidence bundle parse。
- [ ] redaction scan。
- [ ] conclusion boundary。

缺口：

```text
<missing plan item or none>
```

## 3. Operation Log Review

```text
line count:
parse result:
run_id:
session_id:
worldengine_world_id:
first action:
last action:
```

覆盖检查：

- [ ] page open。
- [ ] create session。
- [ ] enter runtime console。
- [ ] inspect pixel canvas。
- [ ] inspect public state。
- [ ] inspect Agent public state。
- [ ] submit director guidance。
- [ ] replay。
- [ ] branch。
- [ ] evidence bundle download。

不可接受：

- [ ] 关键步骤只有截图没有日志。
- [ ] 关键步骤只有日志没有可见结果。
- [ ] API response summary 与 UI 可见状态矛盾。
- [ ] 日志包含 private prompt、provider raw trace 或 Agent private state。

## 4. Screenshot Review

```text
session library screenshot:
create world screenshot:
runtime console screenshot:
director guidance screenshot:
replay/branch screenshot:
evidence panel screenshot:
```

检查：

- [ ] 截图覆盖关键页面。
- [ ] 截图与 operation log 时间顺序一致。
- [ ] 截图不泄漏 key、private prompt、provider raw trace 或 private state。

## 5. Evidence Bundle Review

```text
parse result:
manifest.session_id:
operation log session_id:
event count:
diff count:
snapshot count:
api summary count:
redaction flags:
warnings:
```

检查：

- [ ] evidence bundle 与 run/session 匹配。
- [ ] bundle counts 与 records 一致。
- [ ] replay/branch 所需引用存在。
- [ ] public evaluator output 没有被伪造成 pass。
- [ ] private data scan clean。

## 6. Boundary Review

必须确认：

- [ ] 客户端没有管理 LLM key。
- [ ] 客户端没有直接调用 LLM provider。
- [ ] 客户端没有读取 WorldEngine 私有路径或 helper。
- [ ] 客户端没有记录 private prompt。
- [ ] 客户端没有记录 provider raw trace。
- [ ] 客户端没有记录 Agent private memory、private goal、identity、
      relationship、self_state 或 hidden_context。
- [ ] Codex 没有声明 human validation pass。

## 7. Findings

```text
Finding ID:
Severity:
Evidence:
Impact:
Required follow-up:
Blocks human validation: yes/no
```

## 8. Handoff Decision

如果结论是 `READY_FOR_HUMAN_VALIDATION`：

- [ ] 人工验证只判断体验，不重复命令测试。
- [ ] 将 Codex report、Agent review、operation log、screenshots、evidence
      bundle 交给人类。

如果结论不是 `READY_FOR_HUMAN_VALIDATION`：

- [ ] 不进入人工验证。
- [ ] 明确需要修复的 WorldEngine package、Validation Client task 或验证运行缺口。
