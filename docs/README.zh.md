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
  adr/
    0001-tech-stack.zh.md
```

## 工作方式

大版本用 `docs/milestones/vX.Y-*/` 组织。每个 milestone 至少包含：

- `README.zh.md`：目标、范围、状态和入口。
- `plan.zh.md`：实现计划、步骤和验证方式。
- `review.zh.md`：实现后记录变更、命令、结果和遗留问题。

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
