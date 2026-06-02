# apps/api

FastAPI backend for WorldEngine Validation Client v0.1 foundation.

开发/运行方式：

```bash
cd apps/api
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

### 本地数据库

- 默认数据库路径：`apps/api/.worldengine-validation-client/client.sqlite3`
- 可通过环境变量 `WORLDENGINE_VALIDATION_DATABASE_PATH` 覆盖。

### 环境变量

- `WORLDENGINE_API_BASE`：WorldEngine public API 地址（默认 `http://127.0.0.1:8000`）
- `WORLDENGINE_VALIDATION_ALLOWED_ORIGINS`：后端允许的跨域来源，支持多个来源使用英文逗号分隔；默认 `*`。
