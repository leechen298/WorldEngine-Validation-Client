# Godot 外部验证 MVP

状态：`已验证`

## 目标

通过公开 Engine V1 API 驱动一个可见的 Godot 像素世界，并由独立 checker 证明执行结果
来自 WorldEngine 的权威历史，而不是客户端自报。

## 边界

- `executors/godot/`：Godot 客户端，只渲染投影、发送输入并保存 raw evidence。
- `contracts/mvp/`：固定场景、操作目录和证据格式，executor/checker 均可读取。
- `checkers/mvp/`：独立 Python checker，只读 run directory 并直接向 WorldEngine 获取
  evidence，独占最终 verdict。
- `apps/web/` 和 `apps/api/`：legacy compatibility surface，不参与本次 PASS。

## 固定流程

1. checker 创建带 run id、nonce、时间和 API 地址的 challenge。
2. Godot 动态读取 capability manifest。
3. Godot 创建世界包和 Session，推进 tick，显示 Agent 和世界信号。
4. Godot提交合法方向、非法直接事实、客户端 action 和 typed feedback。
5. Godot保存每个公开 HTTP response、hash、操作日志、summary 和 PNG frame。
6. checker 拒绝 executor 预写 verdict，重新抓取 evidence，验证场景和证据后写 verdict。

## 完成条件

- [x] Godot 交互模式可以显示并操作像素世界。
- [x] Godot 自动执行模式可以跑完整固定场景并保存真实渲染帧。
- [x] executor 输出不包含最终 PASS/FAIL。
- [x] checker 正常场景 PASS。
- [x] hash 篡改、缺文件、旧 nonce、未签发/伪造 challenge、重复 run id、跨 Session、事件倒序、敏感字段和预写
  verdict 都会 FAIL。
- [x] 正常与负向测试、视觉非空检查和真实跨仓 HTTP 运行全部通过。

## 已验证证据

- Godot 版本：`4.7.1.stable.official.a13da4feb`。
- 合同测试：`GODOT_MVP_CONTRACT_TEST_PASS`。
- checker 正反向测试：`15 passed`，包含跨 run request/package 拼装攻击。
- legacy compatibility：Web `36 passed`，API `61 passed`，Web production build 通过。
- 正式运行：`run-20260718T152937Z-2f79d9c5`。
- WorldEngine Session：`session-d7c3736991604445`。
- 独立 verdict：`PASS`，17 项 checks 全部为 `true`。
- input seal：`1c01a7d1b0de8e8d2870aea098fc5ee32b810a1fc9b325eee6ba62e89525659c`。
- executor 记录 13 个公开 HTTP 操作、13 份带 SHA-256 的原始响应和三张 `960x540`
  渲染帧；checker 自行重新抓取 capabilities 与 evidence 后才写 verdict。

自动闭环默认启动短暂的 macOS Godot 渲染窗口，以取得真实 viewport 帧。Godot headless display
只提供 dummy renderer，因此 headless 用于合同和 GDScript 检查，不用于伪造视觉通过。runner 对
Godot 设置 90 秒硬超时，异常时会退出并清理 WorldEngine 服务。

## 本地复现

前提：已安装 `uv`、`pnpm`、Godot，且相邻 WorldEngine 仓库的 `backend/.venv` 可用。

```bash
make test-checker
make test-godot
make run-mvp
```

`make run-mvp` 会选择空闲端口、启动 WorldEngine、签发 challenge、运行 Godot、调用独立
checker，并在成功或失败后关闭服务。成功时标准输出只返回 run id、Session、证据目录和 input
seal；完整原始证据位于被 Git 忽略的 `validation-runs/<run-id>/`。
