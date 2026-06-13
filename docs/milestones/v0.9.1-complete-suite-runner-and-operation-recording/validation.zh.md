# Validation

英文镜像：`validation.md`。

## 结论枚举

| 结论 | 条件 |
| --- | --- |
| `PASS` | Phase 1-4 required evidence 齐全，redaction pass，checker/scorecard 或 second-Agent review 支持 PASS。 |
| `PARTIAL` | 核心 UI 操作和记录链路可运行，但某些非阻塞能力缺 evidence，且没有 redaction fail。 |
| `BLOCKED` | WorldEngine capability、checker、环境、权限或客户端控制缺失导致无法完成。 |
| `FAIL` | 产品行为失败、证据不完整却声明 PASS、redaction 泄露、越权 provider/private 操作。 |

## v0.9.1 自身可以证明什么

v0.9.1 的实现和测试可以证明：

- Validation Client 能按具体 Agent 操作脚本执行。
- 每个 UI 操作能保存到 `operation-log.jsonl`。
- 每个 API 摘要能保存到 `api-log.jsonl` 和 `api-summary.json`。
- blocked path 也能生成完整 result directory。
- redaction boundary 没有明显泄露。

v0.9.1 不能单独证明：

- WorldEngine 世界质量已经达到游戏体验。
- Agent 自主性质量已经满足最终产品。
- LLM provider live behavior 已经正确，除非 WorldEngine checker/scorecard 提供证据。

## PASS 来源

最终 PASS 只能来自：

- 完整 result directory。
- redaction pass。
- WorldEngine checker/scorecard PASS。
- second-Agent read-only review PASS。

不允许的 PASS 来源：

- UI smoke。
- E2E 进程退出码为 0，但 result status 是 `BLOCKED`。
- 只存在 `operation-log.jsonl`，但缺少 API/evidence/checker。
- 人工主观觉得“看起来可以”。

## Review Checklist

第二 Agent 只读复核必须检查：

- `operation-log.jsonl` 是否覆盖全部 executed step。
- `api-log.jsonl` 是否覆盖全部请求。
- `api-summary.json` 是否聚合 phase、path、non-2xx、blocked capability。
- `coverage-matrix.json` 是否和 operation/API logs 一致。
- `transcript.md` 是否覆盖 Phase 1-4。
- screenshots 是否存在。
- redaction 是否 pass。
- direct API harvest 是否没有伪装成用户点击。

