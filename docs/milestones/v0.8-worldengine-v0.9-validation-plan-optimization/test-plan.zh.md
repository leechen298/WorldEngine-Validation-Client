# 测试计划

英文镜像：`test-plan.md`。

## 文档阶段

```bash
git diff --check
rg -n "TBD|TODO|implement later|fill in details" docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization docs/README.zh.md docs/roadmap.zh.md docs/agent-guides/routing.md
```

## API

```bash
cd apps/api && uv run pytest -q
```

API tests 必须覆盖：

- v0.9 public surface discovery。
- manifest schema 和 artifact index。
- path traversal rejection。
- status enum preservation。
- unsupported items。
- missing required artifacts 不得变成 PASS。
- provider-blocked saved-result export。
- redaction flags 和 forbidden value scanning。

## Web

```bash
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
```

Web tests 必须覆盖：

- v0.9 artifact display。
- scorecard / second-Agent review display。
- redaction warning display。
- UI 不声明 evaluator 或 human PASS。
- bounded run/pause/resume controls 的可见操作日志。

## E2E / checker handoff

如果实现 v0.8 E2E，运行：

```bash
pnpm --dir apps/web test:e2e
```

如果导出 checker-compatible result directory，使用 WorldEngine checker：

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine
make validate-agent-autonomous-result RESULT_DIR=<result-dir>
```
