# Review

英文镜像：`review.md`。

状态：documentation drafted / ready for review

## 本轮调整

上一版文档把 Validation Client 路线拆成 v0.9/v0.10/v0.11，并绑定
WorldEngine v0.12。这不符合产品目标。

本轮已改为：

```text
v0.9-complete-worldengine-validation-suite
```

它是一套完整验证用例，内部按 L0-L8 分层。WorldEngine 版本只作为当前被测对象
的 capability 状态，不作为客户端验证路线。

随后根据用户反馈，本 milestone 进一步收敛为文档迭代：目标是交付一套完整的
分阶段验证文档。后续 Validation Client 按这份文档去跑用例。

新增：

```text
phased-validation-plan.zh.md
phased-validation-plan.md
phased-validation-runbook.zh.md
phased-validation-runbook.md
```

并将 `plan.zh.md` / `implementation-task-plan.zh.md` 调整为 docs-only 口径。

索引和路由已同步更新：

```text
AGENTS.md
AGENTS.zh.md
docs/README.zh.md
docs/roadmap.zh.md
docs/agent-guides/routing.md
docs/agent-guides/routing.zh.md
```

后续 `开发 v0.9`、`/goal 开发完整验证套件`、`运行完整验证套件` 都应先读取
本 milestone 的分阶段计划和 runbook。

## 文档一致性验证

已运行：

```text
required v0.9 files check -> missing=[] empty=[]
stale v0.10/v0.11 route scan -> no active hits
false completion / false PASS scan -> only routing rule text hit
git diff --check -> passed
```

说明：`false completion / false PASS scan` 唯一命中是
`docs/agent-guides/routing.zh.md` 里的规则文本：
“完成门禁满足前，不能写已实现”，不是错误状态声明。

## 未运行

- 未运行代码测试。
- 未启动服务。
- 未运行 external validation。

原因：本轮是文档口径修正。

## 当前 Findings

- P1：无。
- P2：当前客户端实现仍未完成完整 suite，需要后续实现。
- P3：旧 v0.8 文档保留为历史，后续实现时要避免把它当 active flow。

## Task Records

### Task 1：路由和产品口径修正

- Commit: `afac751`
- Files:
  - `AGENTS.md`
  - `AGENTS.zh.md`
  - `docs/README.zh.md`
  - `docs/roadmap.zh.md`
  - `docs/agent-guides/routing.md`
  - `docs/agent-guides/routing.zh.md`
- Commands:
  - `git diff --check`: `passed`
  - `rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs`: `passed; hits are expected route/suite references and historical/stop-rule text`
- Scope review:
  - Active milestone and route text now point to the complete validation suite instead of v0.8 or per-WorldEngine-iteration validation.
- Notes:
  - Documentation-only; no code tests, services, external validation, or provider live calls run.

### Task 2：分阶段验证文档

- Commit: `2ff0c5a`
- Files:
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-plan.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/phased-validation-runbook.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/scenario-matrix.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/artifact-contract.zh.md`
  - English mirror files for the same documents.
- Commands:
  - `git diff --check`: `passed`
  - `rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs`: `passed; hits are expected route/suite references and historical/stop-rule text`
- Scope review:
  - Documents define one suite with Phase 1-4, L0-L8, required artifacts, compatibility outputs, and redaction rules.
- Notes:
  - Documentation-only; runtime/API/UI/E2E implementation remains future work.

### Task 3：后续实现约束文档

- Commit: `b7cb77b`
- Files:
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/implementation-task-plan.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/validation.zh.md`
  - English mirror files for the same documents.
- Commands:
  - `git diff --check`: `passed`
  - `rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs`: `passed; hits are expected route/suite references and historical/stop-rule text`
- Scope review:
  - Current v0.9 remains documentation-only with `implementation_authorized: no`; future implementation owns API adapter, runtime controls, exporter, and E2E changes.
- Notes:
  - Direct API harvest must remain in API logs, not user operation logs.

### Task 4：文档验证和 review

- Commit: `pending`
- Files:
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/README.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/README.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/gap-analysis.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/gap-analysis.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/plan.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/plan.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/review.zh.md`
  - `docs/milestones/v0.9-complete-worldengine-validation-suite/review.md`
- Commands:
  - `git diff --check`: `passed`
  - `find docs/milestones/v0.9-complete-worldengine-validation-suite -maxdepth 1 -type f | sort`: `passed; required v0.9 files present`
  - `rg -n "complete-worldengine-validation-suite|v0\\.9-complete-worldengine-validation-suite|WorldEngine iteration" AGENTS.md AGENTS.zh.md docs`: `passed; hits are expected route/suite references and historical/stop-rule text`
- Scope review:
  - Review records documentation-only scope, no implementation authorization, no external validation authorization, and no provider live-call authorization.
- Notes:
  - No milestone completion claim for runtime suite execution.
