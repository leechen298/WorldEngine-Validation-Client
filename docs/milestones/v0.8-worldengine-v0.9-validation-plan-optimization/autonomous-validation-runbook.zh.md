# 自主验证 Runbook

英文镜像：`autonomous-validation-runbook.md`。

## Preflight

```bash
git status --short --branch
git diff --check
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
```

## 执行顺序

1. 启动 WorldEngine。
2. 启动 Validation Client API。
3. 启动 Validation Client Web。
4. 打开 session library。
5. 记录 `/health`、`/manifest`、`/openapi.json` discovery。
6. 选择 scenario。
7. 执行 bounded operation flow。
8. 导出 evidence bundle。
9. 导出 v0.8 checker handoff directory：

```bash
VALIDATION_CLIENT_E2E_OUTPUT_DIR=../../docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/validation-runs/playwright-artifacts \
VALIDATION_CLIENT_API_BASE=http://127.0.0.1:8765 \
VALIDATION_CLIENT_SCENARIO=worldengine-full-lifecycle-autonomous \
pnpm --dir apps/web test:e2e
```

Playwright 输出目录内的 `checker-handoff/` 是客户端 evidence directory。
其中 `manifest.json`、`result.json`、`redaction-scan.json`、`scorecard-summary.json`
和 `operation-log.jsonl` 必须保留 `blocked`、`fail` 或 `not_run`，不能改写为 PASS。

10. 如 `checker-handoff/` 已生成且 WorldEngine checker 支持该目录，运行 WorldEngine checker。
11. 运行第二 Agent 只读复核。
12. 写入 validation run 报告。

## 结论

- `PASS_READY_FOR_HUMAN_VALIDATION`：仅在当前会话所有命令、E2E、bundle、checker/scorecard 和第二 Agent 复核均支持时使用。
- `PARTIAL`：客户端运行可用，但部分 scenario 或 artifact 缺失。
- `BLOCKED`：provider、runner、schema、checker、端口或依赖阻塞。
- `FAIL`：测试失败、证据泄漏、边界破坏或 unsupported PASS claim。
