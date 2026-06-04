# 范围边界

英文镜像：`boundaries.md`。

`WorldEngine-Validation-Client` 是外部验证与观察客户端，必须和 WorldEngine
core 保持硬边界。

## 允许的通信方式

客户端只能通过公开接口与 WorldEngine 通信：

- `WORLDENGINE_API_BASE`
- 公开 HTTP API
- 公开 schema、manifest 和 OpenAPI 描述
- 公开 event、state、timeline 和 evaluator 输出

## 禁止的耦合

客户端不得：

- import WorldEngine 源码
- 依赖 WorldEngine 私有本地路径
- 调用 WorldEngine 内部 helper
- 管理 LLM API key
- 直接调用 LLM provider
- 生成权威世界事实
- 直接修改 Agent 记忆、目标、身份、自我状态、关系或行动

## 允许的本地证据

验证客户端允许存储本地客户端证据：

- sessions
- timeline branches
- commit points
- public events
- state diffs
- snapshots
- director intents
- redacted API traces
- evidence bundle metadata

## 禁止存储的数据

验证客户端不得存储或暴露：

- LLM API keys
- provider secrets
- private prompts
- private evaluator oracle internals
- private WorldEngine internals
- private WorldEngine file paths
- non-public event payloads

## Timeline 和 Branch 语义

Timeline branches 按代码分支建模。

- 可重建 tick 或 event point 是 `commit point`。
- branch 是命名世界线。
- branch 可以从选定 commit point 继续推进。
- branch 语义只包含命名、切换、回放和继续推进。
- 数据模型和文档保持这种直接语义。
