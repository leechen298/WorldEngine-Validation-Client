# v0.8 实现计划

英文镜像：`plan.md`。

状态：文档阶段进行中 / 用户已授权继续实现

## 任务

### 1. v0.8 文档、路由和自审

创建 v0.8 文档包，更新 `docs/README.zh.md`、`docs/roadmap.zh.md`、`docs/agent-guides/routing.md` 和镜像文件中的路由。

验证：

```bash
git diff --check
rg -n "TBD|TODO|implement later|fill in details" docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization docs/README.zh.md docs/roadmap.zh.md docs/agent-guides/routing.md
```

### 2. WorldEngine v0.9 public surface discovery

扩展 backend discovery，识别 v0.9 public surfaces，并把缺失 surface 显示为
`blocked` 或 `not_run`。

候选文件：

```text
apps/api/app/worldengine_client.py
apps/api/app/routes/health.py
apps/api/app/schemas.py
apps/api/tests/test_health.py
apps/api/tests/test_sessions.py
```

验证：

```bash
cd apps/api && uv run pytest tests/test_health.py tests/test_sessions.py -q
git diff --check
```

### 3. Scenario-aware evidence manifest 和 artifact index

实现 v0.9 manifest、artifact index、status preservation、unsupported items 和 bundle-relative path validation。

候选文件：

```text
apps/api/app/routes/evidence.py
apps/api/app/schemas.py
apps/api/tests/test_evidence.py
```

验证：

```bash
cd apps/api && uv run pytest tests/test_evidence.py -q
git diff --check
```

### 4. Named artifact builders 和 redaction scan

导出 v0.9 named artifacts，并对 displayable/exportable artifacts 做 redaction scan。

候选文件：

```text
apps/api/app/routes/evidence.py
apps/api/app/routes/validation_runs.py
apps/api/tests/test_evidence.py
apps/api/tests/test_validation_runs.py
```

验证：

```bash
cd apps/api && uv run pytest tests/test_evidence.py tests/test_validation_runs.py -q
git diff --check
```

### 5. Bounded runtime controls 和 frontend artifact display

在 Runtime Console 中展示 bounded run、pause、resume、additional run、artifact status、scorecard、second-Agent review 和 redaction warning。

候选文件：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/store/sessionStore.ts
apps/web/src/__tests__/RuntimeConsole.test.tsx
```

验证：

```bash
pnpm --dir apps/web test
pnpm --dir apps/web build
git diff --check
```

### 6. v0.8 E2E / checker handoff readiness

新增或升级 v0.8 E2E flow，导出 checker-handoff result directory 或明确记录
`BLOCKED`。

候选文件：

```text
apps/web/e2e/
apps/web/playwright.config.ts
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/autonomous-validation-runbook.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/review.zh.md
```

验证：

```bash
pnpm --dir apps/web test:e2e
git diff --check
```

如已导出 result directory：

```bash
cd /Users/leechen/projects/WorldEnginProjects/WorldEngine
make validate-agent-autonomous-result RESULT_DIR=<result-dir>
```

### 7. 总体验证和 review 收口

运行 broad checks，更新 review，确保没有相关 milestone 改动未提交。

验证：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```

## Stop Rules

- WorldEngine public surface 不存在时，记录 `blocked` 或 `not_run`，不伪造证据。
- provider key 或 provider call 只能由 WorldEngine 拥有。
- redaction blocking leak 必须 FAIL。
- checker 不支持的 PASS 不得写 PASS。
- 第二 Agent 未复核时，不能声明 full lifecycle PASS。
