# WorldEngine Validation Client

本仓库是 WorldEngine 的外部客户端与独立验证器。当前可运行 MVP 由三部分组成：

- `executors/godot/`：只通过公开 Engine V1 API 驱动并渲染像素世界。
- `checkers/mvp/`：重新抓取公开 evidence，独立生成最终 verdict。
- `contracts/mvp/`：Godot 与 checker 共享的固定公开场景合同。

## 运行 MVP

前提：本机已安装 `uv`、Godot，且相邻 WorldEngine 仓库的 `backend/.venv` 已准备好。

```bash
make test-checker
make test-godot
make run-mvp
```

成功运行会输出 `status: PASS`、run id、Session id 和 input seal。生成的原始响应、截图和
checker verdict 位于 `validation-runs/<run-id>/`，该目录不会提交到 Git。

当前合同、边界和已验证证据见 [`docs/current/MVP.zh.md`](docs/current/MVP.zh.md)。
`apps/web/` 与 `apps/api/` 是保留的 legacy compatibility surface，不参与当前 MVP verdict。
