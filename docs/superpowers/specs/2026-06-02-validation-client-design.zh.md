# WorldEngine Validation Client 设计文档

状态：用户评审草案
日期：2026-06-02

## 目标

`WorldEngine-Validation-Client` 是一个独立的 Web 优先验证客户端，用于观察、
回放和分叉 WorldEngine 运行会话。

第一版需要让人类可以看见一个由 WorldEngine 生成并演化的世界，支持高层导
演引导，保留可回放的本地证据，并兼容未来向游戏客户端演进的方向。

本仓库独立于 WorldEngine 核心仓库。

## 产品定位

客户端既不是单薄的工程仪表盘，也不是完整游戏客户端。它是一个观察优先、
带高层导演引导能力的验证体验：

- 用户观察由 WorldEngine 创建并演化的世界。
- 用户可以引导世界演化的大方向。
- 用户不作为玩家角色进入世界。
- 用户不放置物品、不直接触发具体事件、不编辑 Agent 内部状态。
- 客户端只可视化并记录 WorldEngine 通过公开 API 暴露的内容。

未来正式游戏客户端可以使用不同的运行时或表现技术栈。但这个验证客户端仍
应采用可向游戏式存档、回放和世界线分叉演进的会话与存储模型。

## 仓库边界

WorldEngine 和 `WorldEngine-Validation-Client` 是两个独立仓库。

验证客户端不得：

- import WorldEngine 源码。
- 依赖 WorldEngine 私有本地路径。
- 调用 WorldEngine 内部 helper。
- 管理 LLM API key。
- 直接调用 LLM provider。
- 生成权威世界事实。
- 直接修改 Agent 记忆、目标、身份、自我状态或行为决定。

验证客户端只能通过公开接口与 WorldEngine 通信：

- `WORLDENGINE_API_BASE`。
- 公开 HTTP API。
- 公开 schema、manifest 和 OpenAPI 描述。
- 公开 event、state、timeline 和 evaluator 输出。

## 职责拆分

### WorldEngine

WorldEngine 拥有所有核心运行能力：

- 通过环境变量配置管理 LLM provider 和 API key。
- 根据自然语言世界观生成世界。
- 生成场景、物品、角色、规则和初始状态材料。
- 自动推动世界演化。
- 生成随机事件。
- 执行 Agent cognition、拟似自我、记忆使用、目标和行动。
- 执行 evaluator 逻辑并提供公开 evaluator 输出。
- 持有权威运行状态。

### 验证客户端后端

本地验证后端属于本仓库。它保存并提供客户端侧会话数据，但不成为
WorldEngine 子系统。

它负责：

- session 创建和本地元数据。
- timeline 和 branch 记录。
- event 和 diff 持久化。
- 周期 snapshot。
- 为 Web 前端提供 replay 和 fork API。
- 保存脱敏 API trace。
- 导出本地 evidence bundle。
- 可选代理调用 WorldEngine 公开 API。

它不生成世界内容，也不生成权威世界事实。

### Web 前端

前端负责人类体验：

- 会话库。
- 创建世界入口。
- 像素世界观察界面。
- 运行控制。
- 高层导演输入。
- 时间线 scrubber。
- 回放和分叉 UI。
- Agent 公开状态面板。
- 事件和生活日志面板。
- 本地 evidence bundle 导出。

## 技术栈

第一版技术栈：

- 前端：React、Vite、TypeScript。
- 像素场景：PixiJS。
- 前端状态：Zustand。
- 后端：Python、FastAPI、Pydantic。
- 数据库：SQLite。
- 开发形态：Web 前端加本地 FastAPI 后端。

第一版使用 SQLite，因为它能支持持久本地存储、append-only 日志、snapshot、
timeline 分叉和导出，不需要一开始引入服务端数据库。后续如需要云端或多人
场景，再考虑 Postgres。

## 主要页面

### 会话库

第一屏是 session 和世界线库。

它应展示：

- WorldEngine 连接状态。
- WorldEngine API base URL。
- 健康状态、版本和公开能力 manifest 摘要。
- 创建新世界入口。
- 已保存 session。
- 最新 tick、最新事件摘要和最后运行时间。
- timeline 分支数量。
- 导入、导出、归档和清理操作。

用户在设计评审中选择了该第一屏模式，因为它比一次性测试控制台更接近游戏
存档和世界列表。

### 运行控制台

打开 session 后进入运行控制台。

它应包含：

- 左侧控制区：run、pause、continue、single tick、导演引导、分支选择。
- 中央像素世界视图，由 WorldEngine 公开状态驱动。
- 时间线 scrubber，包含 tick、snapshot、事件标记、回放跳转和从此处分叉。
- 右侧面板：Agent 公开状态、事件/生活日志、diff、warning、error 和证据导
  出。

## 核心流程

### 创建世界

用户输入自然语言基础世界观。

WorldEngine 将该世界观转成结构化世界内容，并返回公开初始状态和可视化
payload。客户端保存世界观、请求元数据、返回的公开状态和初始 snapshot。

### 运行世界

WorldEngine 按时间或 tick 推进世界。

客户端记录：

- 公开 event envelope。
- 可视化状态 diff。
- 周期 snapshot。
- API trace。
- warning 和 error。

WorldEngine 拥有实际时间推进、状态转换、Agent 行动、记忆使用、随机事件生
成和 evaluator 行为。

### 导演引导

用户可以在运行过程中输入高层自然语言方向。

导演引导：

- 只影响外部世界环境和事件倾向。
- 进入队列或 pending 状态。
- 由 WorldEngine 在合适的演化节点插入。
- 记录原始文本、接受时机、公开结构化解释，以及可用时的公开影响结果。

导演引导不得：

- 直接改变 Agent 内部想法。
- 直接改变记忆记录。
- 直接设定目标。
- 强迫 Agent 行动。
- 强迫关系或身份变化。
- 以隐藏方式覆盖世界事实。

Agent 必须根据自身状态、记忆、目标、历史、关系和感知到的公开事件自然反应。

### 回放

用户可以回到过去某个 tick 或事件点。

回放重建流程：

1. 找到最近的前置 snapshot。
2. 依次应用后续正向 diff，直到目标 tick。
3. 渲染重建后的公开可视化状态。

回放是客户端侧的可视化和证据功能。它不改写 WorldEngine 权威运行状态。

### 分叉世界线

用户可以从历史 tick 创建分支。

一次分叉记录：

- 父 timeline id。
- fork tick。
- fork snapshot 引用。
- 可选 fork reason 或 director guidance。
- 新 timeline id。

新 timeline 之后作为独立运行线继续推进，不覆盖父 timeline。

### 导出 Evidence Bundle

客户端可以导出本地 session evidence bundle。

该 bundle 不是重型 evaluator 报告。它是给 Codex、人类或后续 WorldEngine
评审使用的证据包：

- session 元数据。
- WorldEngine 版本和能力摘要。
- director inputs。
- event log。
- state diffs。
- snapshots。
- replay index。
- 脱敏 API traces。
- WorldEngine 公开 evaluator 输出，如有。
- warning 和 error。

## 存储模型

存储模型是 event-sourced 加周期 snapshot。

主要表：

- `sessions`
- `timelines`
- `events`
- `state_diffs`
- `snapshots`
- `director_intents`
- `api_traces`
- `worldengine_runs`
- `replay_index`

存储规则：

- 将公开 event envelope 作为审计记录保存。
- 将状态变化保存为正向 diff。
- 每 N tick 或关键事件保存完整 snapshot。
- 用 snapshot 加正向 diff 重建历史可视化状态。
- 用 timeline branch 表达世界线分叉，而不是覆盖历史。
- 第一版优先使用可读 JSON。
- 基础模型稳定后，再对大 snapshot 或导出 bundle 增加 gzip 或 zstd 压缩。

客户端数据库不是 WorldEngine 的权威状态源。它是本地观察、回放、分叉和导出
存储。

## 日志

客户端应为自己的 session 保存完整本地日志。

日志类别：

- session 生命周期。
- 世界事件。
- 可视化状态 diff。
- Agent 公开生活事件。
- 导演引导。
- timeline 和 fork 操作。
- API trace 摘要。
- warning 和 error。
- WorldEngine evaluator 公开输出，如有。

日志必须脱敏。不得包含 LLM API key、provider secret、私有 prompt、私有
oracle internals 或非公开 WorldEngine 内部信息。

## API 形态

本地后端应提供客户端 API：

- 连接状态。
- session CRUD。
- 创建世界请求。
- run、pause、continue 和 tick 命令。
- director guidance 提交。
- timeline 列表和选择。
- replay 重建。
- fork 创建。
- log 查询。
- evidence bundle 导出。

WorldEngine API 细节保持外部化，应从 WorldEngine 的公开 API、manifest 或
OpenAPI 面发现。

## 第一版非目标

第一版不实现：

- 玩家角色控制。
- 直接放置物品。
- 直接手动注入事件。
- 直接编辑 Agent 记忆、目标、身份、关系或行动。
- 客户端自定义 LLM provider 调用。
- 客户端 LLM API key 管理。
- 客户端重型 evaluator 逻辑。
- 私有 WorldEngine 集成。
- 云同步。
- 多人模式。
- 正式游戏打包。

## 待在实现计划中确定的细节

以下内容应在实现计划阶段确定：

- 具体 WorldEngine 公开 API endpoints。
- 可视化 payload schema。
- diff 格式，优先考虑 JSON Patch 风格。
- snapshot 频率。
- SQLite schema 细节和索引。
- evidence bundle 文件结构。
- 前端组件拆分。
- 开发脚本和进程管理方式。
- replay 和 fork 正确性的测试策略。
