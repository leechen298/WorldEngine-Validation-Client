# AGENTS.zh.md

本仓库是 WorldEngine 的外部客户端和独立验证器。当前目标只由
`docs/current/MVP.zh.md` 指导。

`docs/milestones/` 下的旧文件是历史参考，不再要求开发前创建 milestone package、
逐 task 提交或填写 review 记录。

## 必须保留的边界

1. 只能通过公开 HTTP、OpenAPI、manifest 和公开 evidence 与 WorldEngine 通信，不得导入
   WorldEngine 源码或读取其存储。
2. Godot executor 负责渲染公开投影并记录原始执行证据，不得写 PASS/FAIL verdict。
3. checker 是独立进程，不得导入 executor 代码，并且独占最终 verdict。
4. 本仓库不管理 LLM key、权威世界事实、Agent 私有状态或 provider trace。
5. 除非当前 MVP 需要有边界的兼容修复，否则保留旧 Web/API；旧 E2E 绿色不能作为 MVP
   PASS。
6. 只有当前工作会话真实运行的命令才能作为完成证据。
7. 保留无关用户改动，不执行破坏性 Git 操作。

直接实现完整纵向闭环。当前决策和证据写入 `docs/current/MVP.zh.md`；详细 milestone
文档和常规 evaluator 不再是前置门禁。
