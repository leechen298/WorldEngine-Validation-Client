# 意图

英文镜像：`intent.md`。

v0.8 的意图是让 Validation Client 随 WorldEngine 验证合同变化而持续优化。它不是
一次性的兼容补丁，而是一种后续可重复使用的外部验证客户端迭代模式。

本次优化针对 WorldEngine v0.9：

- LLM-backed lifecycle 不再只看 UI smoke。
- `BLOCKED`、`not_run` 和 checker-valid blocked result 是真实结论，不能被改写。
- artifact 名称、manifest 字段、scorecard items 和 redaction flags 必须可被第二
  Agent 或 WorldEngine checker 复核。
- direct API harvest 必须独立记录，不能伪装成用户或 Agent 可见操作。

最终产物应让后续 Codex、第二 Agent 和人类清楚区分：

- 客户端运行是否可用。
- WorldEngine public evidence 是否齐全。
- checker 或 scorecard 是否接受 result。
- provider、runner、schema、artifact 或 redaction 缺口具体在哪里。
