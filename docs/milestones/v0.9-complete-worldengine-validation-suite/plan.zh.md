# Plan

英文镜像：`plan.md`。

## Task 1：路由和产品口径修正

候选文件：

```text
AGENTS.md
AGENTS.zh.md
docs/README.zh.md
docs/roadmap.zh.md
docs/agent-guides/routing.md
docs/agent-guides/routing.zh.md
```

要求：

- active milestone 指向 `v0.9-complete-worldengine-validation-suite`。
- 不再暗示客户端要跟随 WorldEngine 每个迭代拆验证。
- 明确 v0.9 是一个完整 suite，内部按层级深入。

## Task 2：分阶段验证文档

候选文件：

```text
docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-plan.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-runbook.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/agent-autonomous-operation-script.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/operation-recording-contract.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/scenario-matrix.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/artifact-contract.zh.md
```

要求：

- 定义 `complete-worldengine-validation-suite` 主场景。
- 定义 Phase 1-4 分阶段验证。
- 定义 L0-L8 分层和阶段映射。
- 定义 required artifacts、compatibility artifacts 和 redaction rules。
- 定义 Agent 自主测试的具体 UI 操作步骤，包括按钮、输入、下载和截图。
- 定义逐操作记录契约，包括 `operation-log.jsonl`、`api-log.jsonl`、`console.log`、
  `transcript.md` 和 screenshots。

## Task 3：后续实现约束文档

候选文件：

```text
docs/milestones/v0.9-complete-worldengine-validation-suite/implementation-task-plan.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/validation.zh.md
```

要求：

- 明确当前 v0.9 是文档迭代。
- 后续实现才修改 API adapter、UI controls、evidence exporter、E2E。
- direct API harvest 必须进入 `api-log.jsonl` / `api-summary.json`，不进入用户操作日志。

## Task 4：文档验证和 review

要求：

- 路由能找到本 milestone。
- 文档不再暗示跟随 WorldEngine 每个迭代验证。
- 状态保持 `implementation_authorized: no`。
- review 记录本轮只改文档。

## 验证命令

文档阶段：

```bash
git diff --check
rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs
```

## Stop Rules

- 如果只能靠 UI smoke 证明结果，不能 PASS。
- 如果 WorldEngine public capability 缺失，记录 `blocked/capability_gap`。
- 如果客户端需要 provider key 或 raw prompt/raw response，停止并 FAIL。
- 如果 redaction 阻塞，优先修 redaction。
