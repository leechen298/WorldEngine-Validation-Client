# Codex 自主验证报告模板

英文镜像：`codex-run-report-template.md`。

用途：Codex 完成一次浏览器自主验证后，用本文模板生成
`validation-runs/YYYY-MM-DD-codex/codex.zh.md`。

本文是模板，不是验证结果。未实际运行命令、浏览器 flow、日志解析或 evidence
bundle 检查时，不得填写为通过。

## 0. 结论

结论只能选择一个：

```text
PASS_READY_FOR_HUMAN_VALIDATION
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

## 1. Run Metadata

```text
run_id:
date:
operator:
branch:
commit:
working_tree_status:
WorldEngine repo:
WorldEngine branch:
WorldEngine commit:
Validation Client repo:
Validation Client branch:
Validation Client commit:
WorldEngine API base:
Validation Client API base:
Web URL:
```

## 2. Preflight Evidence

记录实际命令和结果：

```text
git status --short --branch:
git diff --check:
WorldEngine GET /health:
WorldEngine GET /manifest:
WorldEngine GET /openapi.json:
Validation Client GET /health:
Validation Client GET /health/worldengine:
Validation Client POST /sessions/worldengine:
```

必须确认：

- [ ] WorldEngine `/manifest` 可访问。
- [ ] WorldEngine OpenAPI 有可发现 world creation endpoint。
- [ ] Validation Client 报告 `world_creation: available`。
- [ ] Validation Client 可以创建 WorldEngine-backed session。
- [ ] 没有 key、private prompt、provider raw trace 或 Agent private state 出现
      在 public response 中。

如果任一项未满足，结论不得为 `PASS_READY_FOR_HUMAN_VALIDATION`。

## 3. Commands Run

只记录当前会话实际运行过的命令。

```text
cd apps/api && uv run pytest -q:
pnpm --dir apps/web test:
pnpm --dir apps/web build:
pnpm run test:
pnpm run build:
E2E command:
redaction scan:
```

## 4. Service Startup

```text
WorldEngine command:
WorldEngine PID/session:
WorldEngine port:
Validation Client API command:
Validation Client API PID/session:
Validation Client API port:
Validation Client Web command:
Validation Client Web PID/session:
Validation Client Web port:
```

必须记录端口冲突、重启、失败和 fallback。

## 5. Browser Flow Checklist

- [ ] 打开会话库。
- [ ] 截图 `screenshots/01-session-library.png`。
- [ ] 检查 WorldEngine 连接状态。
- [ ] 输入 session name。
- [ ] 输入基础世界观。
- [ ] 创建 WorldEngine session。
- [ ] 进入运行控制台。
- [ ] 截图 `screenshots/03-runtime-console.png`。
- [ ] 检查像素画布。
- [ ] 检查公开状态摘要。
- [ ] 检查 Agent 公开状态。
- [ ] 检查 World Log。
- [ ] 检查 Agent Life Log。
- [ ] 提交高层导演引导。
- [ ] 截图 `screenshots/04-director-guidance.png`。
- [ ] 使用 replay slider。
- [ ] 从 commit point 创建 branch。
- [ ] 切换 branch。
- [ ] 截图 `screenshots/05-replay-branch.png`。
- [ ] 打开 evidence panel。
- [ ] 下载 evidence bundle。
- [ ] 截图 `screenshots/06-evidence-panel.png`。

未完成项：

```text
<list missing steps or none>
```

## 6. Operation Log Evidence

```text
operation log path:
line count:
run_id matched:
session_id matched:
worldengine_world_id matched:
first timestamp:
last timestamp:
```

必须检查日志覆盖：

- [ ] page open。
- [ ] click。
- [ ] fill。
- [ ] submit。
- [ ] API request summary。
- [ ] API response summary。
- [ ] screenshot。
- [ ] download。
- [ ] assertion。
- [ ] visible result。

## 7. Evidence Bundle Evidence

```text
evidence bundle path:
JSON parse result:
manifest.session_id:
operation log session_id:
timeline branch ids:
event count:
diff count:
snapshot count:
api summary count:
redaction flags:
warnings:
```

必须检查：

- [ ] evidence bundle 可以 parse。
- [ ] evidence bundle 与本次 run/session 匹配。
- [ ] evidence bundle 与 operation log 互相引用。
- [ ] counts 与 records 一致。
- [ ] public evaluator output 未被伪造成 PASS。
- [ ] private data scan clean。

## 8. Screenshots

```text
screenshots/01-session-library.png:
screenshots/02-create-world.png:
screenshots/03-runtime-console.png:
screenshots/04-director-guidance.png:
screenshots/05-replay-branch.png:
screenshots/06-evidence-panel.png:
```

缺失截图：

```text
<list missing screenshots or none>
```

## 9. Redaction / Boundary Scan

命令：

```bash
rg -n "api_key|apikey|secret|token|password|credential|authorization|private_path|source_path|private_prompt|oracle|internal|helper|provider|memory|thought|goal|self_state|relationship|identity|hidden_context|raw_response" apps/api/app apps/api/tests apps/web/src docs/milestones/v0.7-agent-autonomous-validation
```

分类：

```text
allowed documentation hits:
allowed test redaction hits:
forbidden UI hits:
forbidden bundle hits:
forbidden real secret hits:
```

任何真实 key、private prompt、provider raw trace 或 Agent private state 泄漏，结
论必须为 `FAIL`。

## 10. Known Gaps

```text
<gap id>:
severity:
evidence:
required follow-up:
```

## 11. Next Gate

如果结论是 `PASS_READY_FOR_HUMAN_VALIDATION`：

- [ ] 第二 Agent 只读复核尚未开始。
- [ ] 不声明人工验证通过。
- [ ] 将本报告、operation log、screenshots、evidence bundle 和 api summary 交给
      第二 Agent。

如果结论不是 `PASS_READY_FOR_HUMAN_VALIDATION`：

- [ ] 不进入第二 Agent 复核，除非复核目标是确认 blocker。
- [ ] 不进入人工验证。
- [ ] 记录修复所需 package 或 task。
