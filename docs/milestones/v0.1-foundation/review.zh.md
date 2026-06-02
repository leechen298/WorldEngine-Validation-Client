# v0.1 Foundation Review

状态：已完成（v0.1 细项收口）

## 实现授权

当前状态：允许按 `plan.zh.md` 开始实现。

## 变更文件

2026-06-02 更新：

- `package.json`
- `pnpm-workspace.yaml`
- `.gitignore`
- `apps/api/README.md`
- `apps/api/pyproject.toml`
- `apps/api/app/__init__.py`
- `apps/api/app/main.py`
- `apps/api/app/config.py`
- `apps/api/app/db.py`
- `apps/api/app/models.py`
- `apps/api/app/schemas.py`
- `apps/api/app/worldengine_client.py`
- `apps/api/app/routes/health.py`
- `apps/api/app/routes/sessions.py`
- `apps/api/app/routes/timelines.py`
- `apps/api/app/routes/evidence.py`
- `apps/api/tests/conftest.py`
- `apps/api/tests/test_health.py`
- `apps/api/tests/test_sessions.py`
- `apps/api/tests/test_timelines.py`
- `apps/api/tests/test_evidence.py`
- `apps/web/package.json`
- `apps/web/index.html`
- `apps/web/vite.config.ts`
- `apps/web/tsconfig.json`
- `apps/web/src/main.tsx`
- `apps/web/src/App.tsx`
- `apps/web/src/styles.css`
- `apps/web/src/api/client.ts`
- `apps/web/src/api/types.ts`
- `apps/web/src/store/sessionStore.ts`
- `apps/web/src/components/ConnectionStatus.tsx`
- `apps/web/src/components/PixelWorldCanvas.tsx`
- `apps/web/src/components/TimelineBranchList.tsx`
- `apps/web/src/pages/SessionLibrary.tsx`
- `apps/web/src/pages/RuntimeConsole.tsx`
- `apps/web/src/test/setup.ts`
- `apps/web/src/__tests__/SessionLibrary.test.tsx`
- `apps/web/src/__tests__/RuntimeConsole.test.tsx`

2026-06-02 追加补齐：

- `apps/api/app/main.py`
- `apps/api/app/config.py`
- `apps/api/app/worldengine_client.py`
- `apps/api/app/models.py`
- `apps/web/src/pages/SessionLibrary.tsx`
- `.gitignore`
- `package.json`
- `docs/milestones/v0.1-foundation/review.zh.md`

## 验证命令

执行结果：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
git diff --check
```

- `cd apps/api && uv run pytest -q`：`7 passed, 0 failed`（含 `app` 依赖相关告警，仅 warning）
- `pnpm --dir apps/web test`：2 passed（无 act 警告）
- `pnpm --dir apps/web build`：构建成功
- `git diff --check`：无 whitespace/冲突问题

## 范围审核

执行结果确认：

- 是否只通过 public API 连接 WorldEngine：是，`/health/worldengine` 仅调用 `WORLDENGINE_API_BASE/health` 与 `/manifest`。
- 是否未引入客户端 LLM key 管理：是，未读取或创建 LLM key。
- 是否未直接调用 LLM provider：是。
- 是否未生成权威世界事实：是，本版本仅记录会话与分支元数据。
- 是否未引入玩家角色控制：是，前端为观测/控制台骨架。

## 遗留问题

- `SessionLibrary` 与 `RuntimeConsole` 使用本地 API 的基础功能已就绪，下一步 v0.2 进入 WorldEngine 公开 API 深度对接。
- 后端 endpoint 未实现 world create/run/tick 的业务动作（v0.1 非目标）。

## v0.1 收口补丁回执（本轮）

- 已修复高优先级项：`apps/api/app/main.py` 增加 `CORSMiddleware`，并通过 `get_settings().allowed_origins` 统一来源。
- 已修复中优先级项：`apps/api/app/config.py` 与 `main.py` 的数据库路径统一为 `get_settings().database_path`，避免路径解析分叉。
- 已修复低优先级项：`apps/web/src/pages/SessionLibrary.tsx` 对创建会话异常增加 `try/catch` 兜底，结合 store 错误态展示。
- 收尾：`.gitignore` 增加 `.superpowers/`、`package.json` 补齐后端与整体脚本、`apps/api/app/models.py` 去掉 `datetime.utcnow()` 告警用法。

待执行项（建议）

- 如需严谨复核可执行：`pnpm run test`、`pnpm run build`（当前代码结构已对齐目标，不需要功能性变更）。
