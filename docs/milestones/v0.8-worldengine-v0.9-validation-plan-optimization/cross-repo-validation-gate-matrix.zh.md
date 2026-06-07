# 跨仓库门禁矩阵

英文镜像：`cross-repo-validation-gate-matrix.md`。

| Gate | 名称 | Owner | 输入 | 必须产出 | 允许结论 | 下一关条件 |
| --- | --- | --- | --- | --- | --- | --- |
| Gate 0 | v0.8 plan readiness | Validation Client | v0.8 文档包 | 自审通过、review 记录 | `PLAN_READY` / `PARTIAL` / `BLOCKED` | `PLAN_READY` 且用户已授权实现 |
| Gate 1 | WorldEngine v0.9 public contract readiness | WorldEngine | v0.9 docs/testing/contracts | public surfaces、scenario/artifact/scorecard contracts | `WORLDENGINE_CONTRACT_READY` / `PARTIAL` / `BLOCKED` / `FAIL` | 缺口可由客户端诚实表示，或 WorldEngine 先修复 |
| Gate 2 | Validation Client v0.8 implementation readiness | Validation Client | 实现和测试 | bundle/export/UI/E2E 支撑 | `READY_FOR_CODEX_AUTONOMOUS_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | 当前仓库检查通过或阻塞被记录 |
| Gate 3 | Codex autonomous validation | Codex | 运行客户端和 WorldEngine | validation run、bundle、checker result | `PASS_READY_FOR_HUMAN_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | checker/scorecard/证据支持进入第二 Agent |
| Gate 4 | 第二 Agent 只读复核 | Second Agent | run artifacts | 复核报告 | `READY_FOR_HUMAN_VALIDATION` / `PARTIAL` / `BLOCKED` / `FAIL` | 无 blocking P1/P2 |
| Gate 5 | 人工验证 | Human | 复核后的证据 | 人工体验判断 | `HUMAN_PASS` / `HUMAN_PARTIAL` / `HUMAN_FAIL` | 人工结论 |

UI smoke、API tests 或客户端导出成功不等于 WorldEngine validation PASS。
