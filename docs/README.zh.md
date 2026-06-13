# WorldEngine Validation Client 文档

本仓库采用轻量 milestone 文档流程，而不是照搬 WorldEngine 核心仓库的强迭代
治理。

## 文档结构

```text
docs/
  README.zh.md
  roadmap.zh.md
  specs/
    validation-client-design.zh.md
    validation-client-design.md
  milestones/
    v0.1-foundation/
      README.zh.md
      plan.zh.md
      review.zh.md
    v0.2-worldengine-integration/
      README.zh.md
      plan.zh.md
      review.zh.md
    v0.3-runtime-visualization/
      README.zh.md
      plan.zh.md
      review.zh.md
    v0.4-replay-branching/
      README.zh.md
      plan.zh.md
      review.zh.md
    v0.5-director-guidance/
      README.zh.md
      plan.zh.md
      review.zh.md
    v0.6-evidence-bundle/
      README.zh.md
      plan.zh.md
      review.zh.md
    v0.7-agent-autonomous-validation/
      README.zh.md
      plan.zh.md
      implementation-task-plan.zh.md
      implementation-task-plan.md
      codex-autonomous-validation-master-plan.zh.md
      codex-autonomous-validation-master-plan.md
      handoff-prompts.zh.md
      handoff-prompts.md
      codex-run-report-template.zh.md
      codex-run-report-template.md
      agent-review-template.zh.md
      agent-review-template.md
      human-validation-template.zh.md
      human-validation-template.md
      autonomous-validation-runbook.zh.md
      autonomous-validation-runbook.md
      cross-repo-validation-gate-matrix.zh.md
      cross-repo-validation-gate-matrix.md
      planning-readiness-checklist.zh.md
      planning-readiness-checklist.md
      handoff-status.zh.md
      handoff-status.md
      next-chat-quickstart.zh.md
      next-chat-quickstart.md
      review.zh.md
      validation.zh.md
      validation-runs/
    v0.8-worldengine-v0.9-validation-plan-optimization/
      README.zh.md
      README.md
      intent.zh.md
      intent.md
      contract.zh.md
      contract.md
      technical-design.zh.md
      technical-design.md
      test-plan.zh.md
      test-plan.md
      plan.zh.md
      plan.md
      implementation-task-plan.zh.md
      implementation-task-plan.md
      scenario-operation-matrix.zh.md
      scenario-operation-matrix.md
      artifact-contract.zh.md
      artifact-contract.md
      redaction-matrix.zh.md
      redaction-matrix.md
      autonomous-validation-runbook.zh.md
      autonomous-validation-runbook.md
      second-agent-review-template.zh.md
      second-agent-review-template.md
      cross-repo-validation-gate-matrix.zh.md
      cross-repo-validation-gate-matrix.md
      planning-readiness-checklist.zh.md
      planning-readiness-checklist.md
      handoff-status.zh.md
      handoff-status.md
      next-chat-quickstart.zh.md
      next-chat-quickstart.md
      handoff-prompts.zh.md
      handoff-prompts.md
      validation.zh.md
      validation.md
      codex-run-report-template.zh.md
      codex-run-report-template.md
      agent-review-template.zh.md
      agent-review-template.md
      human-validation-template.zh.md
      human-validation-template.md
      review.zh.md
      review.md
      validation-runs/
    v0.9-complete-worldengine-validation-suite/
      README.zh.md
      README.md
      gap-analysis.zh.md
      gap-analysis.md
      phased-validation-plan.zh.md
      phased-validation-plan.md
      phased-validation-runbook.zh.md
      phased-validation-runbook.md
      scenario-matrix.zh.md
      scenario-matrix.md
      artifact-contract.zh.md
      artifact-contract.md
      plan.zh.md
      plan.md
      implementation-task-plan.zh.md
      implementation-task-plan.md
      validation.zh.md
      validation.md
      review.zh.md
      review.md
  agent-guides/
    routing.zh.md
    workflow.zh.md
    boundaries.zh.md
    validation-workflow.zh.md
  adr/
    0001-tech-stack.zh.md
```

## 工作方式

大版本用 `docs/milestones/vX.Y-*/` 组织。每个 milestone 至少包含：

- `README.zh.md`：目标、范围、状态和入口。
- `plan.zh.md`：实现计划、步骤和验证方式。
- `implementation-task-plan.zh.md`：当 milestone 需要交给后续开发聊天时，记录
  更细的 task-by-task 实施计划、文件责任、验证命令和 stop rules。
- `review.zh.md`：实现后记录变更、命令、结果和遗留问题。
- `validation.zh.md`：当 milestone 涉及验证行为或验证结论时，记录 Codex 自主
  验证、Agent 复核和人工验证交接方案。
- `codex-autonomous-validation-master-plan.zh.md`：当 milestone 要交接到 Codex
  自主验证和人工验证时，记录跨 WorldEngine / Validation Client / Agent / 人类
  的完整阶段计划。
- `handoff-prompts.zh.md`：记录后续 WorldEngine 开发、Validation Client 开发、
  Codex 自主验证、第二 Agent 复核和人工验证聊天可直接使用的 `/goal` prompts。
- `codex-run-report-template.zh.md`、`agent-review-template.zh.md`、
  `human-validation-template.zh.md`：固定三类验证报告的输入、检查项和结论枚举。
- `autonomous-validation-runbook.zh.md`：记录真实 Codex 自主验证运行当天的执行
  顺序、命令、浏览器 flow、证据落盘和 stop rules。
- `cross-repo-validation-gate-matrix.zh.md`：记录 WorldEngine、Validation
  Client、Codex、第二 Agent 和人工验证之间的不可跳关门禁、证据和结论枚举。
- `planning-readiness-checklist.zh.md`：记录当前计划是否已经可交给后续聊天执行、
  当前唯一允许的下一步和未完成项。
- `handoff-status.zh.md`：记录单页当前状态、blocker、当前 gate 和唯一允许的下一步。
- `next-chat-quickstart.zh.md`：记录后续聊天可直接复制使用的分阶段 `/goal`
  prompts。

高风险设计或长期技术选择使用 `docs/adr/` 记录。

## 自然语言入口

当用户说：

```text
开发 v0.1
实现 v0.1
继续 v0.1
审核 v0.1
开发 v0.2
开发 v0.3
开发 v0.4
开发 v0.5
开发 v0.6
开发 v0.7
自主验证 v0.7
人工验证 v0.7
开发 v0.8
自主验证 v0.8
开发 v0.9
自主验证 v0.9
```

Agent 应先读取对应 milestone：

```text
docs/milestones/v0.1-foundation/README.zh.md
docs/milestones/v0.1-foundation/plan.zh.md
docs/milestones/v0.1-foundation/review.zh.md
```

如果目标 milestone 目录或计划尚不存在，应先创建或补齐 milestone 文档，再按
`docs/agent-guides/workflow.md` 的逐 task 流程进入实现。

然后按计划实现、验证并更新 `review.zh.md`。

验证请求走 `docs/agent-guides/validation-workflow.zh.md`。Codex / Agent 自主验证
只能证明客户端、证据和边界足以进入人工验证；人工验证负责判断世界可观察性、
Agent 自然性、导演边界和体验可信度。

v0.7 之后的完整自主验证计划入口：

```text
docs/milestones/v0.7-agent-autonomous-validation/codex-autonomous-validation-master-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.7-agent-autonomous-validation/planning-readiness-checklist.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-status.zh.md
docs/milestones/v0.7-agent-autonomous-validation/implementation-task-plan.zh.md
docs/milestones/v0.7-agent-autonomous-validation/handoff-prompts.zh.md
```

v0.8 WorldEngine v0.9 验证计划优化入口：

```text
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/README.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/plan.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/implementation-task-plan.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/cross-repo-validation-gate-matrix.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/artifact-contract.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/scenario-operation-matrix.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/redaction-matrix.zh.md
docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/review.zh.md
```

完整 WorldEngine 验证套件入口：

```text
docs/milestones/v0.9-complete-worldengine-validation-suite/README.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/gap-analysis.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-plan.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-runbook.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/scenario-matrix.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/artifact-contract.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/plan.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/implementation-task-plan.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/validation.zh.md
docs/milestones/v0.9-complete-worldengine-validation-suite/review.zh.md
```

## 流程原则

本仓库采用轻量但可审计的工程流程：

1. 先写或确认 spec / milestone 文档。
2. 审核范围和边界。
3. 按 `plan.zh.md` 实现。
4. 运行自测。
5. 更新 `review.zh.md`。
6. 再进入下一个 milestone。

这类似业内常见的 RFC / milestone / PR review / test report 流程，但比
WorldEngine 核心仓库更轻。
