# 技术设计

英文镜像：`technical-design.md`。

## 设计形态

v0.8 复用 v0.7 的 session、validation run、operation log、evidence bundle 和 E2E
基础，新增 v0.9 scenario-aware packaging layer。

主要模块：

- `worldengine_client.py`：发现 v0.9 public surfaces，输出 capability model。
- `routes/evidence.py`：导出 v0.9 manifest、artifact index 和 named artifacts。
- `routes/validation_runs.py`：保存 operation log 与 direct API harvest log。
- `RuntimeConsole.tsx`：展示 bounded controls、artifact status、checker/scorecard/second-Agent review。
- `api/types.ts` 与 `api/client.ts`：承载 v0.9 evidence bundle types。

## 数据流

1. 通过 `/health`、`/manifest`、`/openapi.json` 建立 public surface map。
2. 用户或 Agent 在 UI 中执行 visible operations。
3. 客户端把 visible operations 写入 `operation-log.jsonl`。
4. 客户端把 direct public API harvest 写入 `api-log.jsonl`。
5. evidence exporter 根据 scenario contract 生成 required/optional artifacts。
6. redaction scanner 扫描 displayable/exportable artifacts。
7. manifest 保留 status、unsupported items 和 checker contract。

## 风险控制

- 客户端只展示 checker/scorecard，不生成 PASS。
- bounded runtime controls 避免无限运行。
- status preservation 避免把 `blocked` 或 `not_run` 隐藏在成功 UI 后。
- bundle-relative paths 避免本地路径泄漏。
