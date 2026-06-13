# Validation Plan

英文镜像：`validation.md`。

## 结论枚举

- `PASS`：完整 suite required layers 均有 evidence，redaction 通过，WorldEngine
  checker/scorecard 或 second-Agent review 支持结论。
- `PARTIAL`：核心 flow 可执行，但部分非阻塞层级缺证据或 checker 不完整。
- `BLOCKED`：capability、环境、checker、result directory、权限或客户端 evidence 缺失。
- `FAIL`：产品行为、redaction、边界或证据完整性失败。

## PASS 来源

PASS 只能来自：

- WorldEngine checker / scorecard。
- second-Agent read-only review。
- 完整 result directory 的 redaction PASS。

## 不允许的 PASS 来源

- UI smoke 通过。
- Validation Client 自己判断“看起来正常”。
- WorldEngine API key 或 provider readiness 存在。
- 历史 result directory。
- 只跑了 L0-L2。

## Agent 自主验证

Agent 应按完整 suite 操作客户端，而不是按 WorldEngine 某个迭代文档逐项调度。
WorldEngine 文档只作为被测能力契约和 checker/scorecard 来源。
