# v0.8 详细实施计划

英文镜像：`implementation-task-plan.md`。

## 文件责任

主要后端文件：

```text
apps/api/app/worldengine_client.py
apps/api/app/routes/health.py
apps/api/app/routes/evidence.py
apps/api/app/routes/validation_runs.py
apps/api/app/schemas.py
apps/api/tests/test_health.py
apps/api/tests/test_evidence.py
apps/api/tests/test_validation_runs.py
```

主要前端文件：

```text
apps/web/src/api/client.ts
apps/web/src/api/types.ts
apps/web/src/store/sessionStore.ts
apps/web/src/pages/RuntimeConsole.tsx
apps/web/src/__tests__/RuntimeConsole.test.tsx
apps/web/e2e/
apps/web/playwright.config.ts
```

禁止修改 WorldEngine 仓库、provider key 管理、WorldEngine 私有 prompt/oracle、Agent private state。

## Task 1: 文档和路由

交付 v0.8 文档包、路由更新和文档自审。

## Task 2: v0.9 public surface discovery

以测试先行扩展 discovery response，至少覆盖可用、缺失、blocked 三类 surface 状态。

## Task 3: evidence manifest 和 artifact index

以测试先行实现 bundle-relative path、required artifact、unsupported items 和 status preservation。

## Task 4: named artifacts 和 redaction scan

以测试先行生成 scenario artifacts，并扫描 displayable/exportable artifact 内容。

## Task 5: bounded runtime UI 和 artifact display

以前端测试先行实现 bounded controls、scorecard/second-Agent/redaction display。

## Task 6: E2E / checker handoff

升级 E2E artifact 路径和 v0.8 flow，导出 result 或诚实记录 `BLOCKED`。

## Task 7: 总体验证

运行 broad checks，更新 review，保留待验证状态和真实阻塞项。
