# Milestone 执行工作流

英文镜像：`workflow.md`。

这个工作流是强约束。它用于防止 agent 把整个 milestone 一次性做成不可审查的
大批量改动。

## 强执行规则

1. 严格按 `plan.zh.md` 的 task 顺序执行 milestone 工作。
2. 一次只处理一个编号 task。
3. 当前 task 未实现、未验证、未记录、未提交前，不得开始下一个 task。
4. 每个编号 task 必须有独立提交，除非用户在实现前明确批准合并 task。
5. 每个 task 提交只能包含该 task 必需文件。
6. 相关实现文件仍有未暂存或未提交改动时，不得把 milestone 标记为已实现、
   完成或等价状态。
7. 对应实现和验证未实际发生前，不得在 `review.zh.md` 写通过或完成结论。
8. 不得跳过计划中的验证命令。命令无法运行时，必须记录为 blocked，并写明精
   确原因。
9. 必需检查失败后，不得继续推进；下一步只能是针对失败的窄修复。
10. 实现 active milestone 时不得扩大到未来 milestone 范围。

## 必需 Task 循环

对 `plan.zh.md` 中每个编号 task，必须执行：

1. 读取 task 范围和文件列表。
2. 用 `git status --short --branch` 检查工作树。
3. 只实现该 task。
4. 运行 `plan.zh.md` 中该 task 的验证命令。
5. 运行 `git diff --check`。
6. 在 `review.zh.md` 更新该 task 记录。
7. 只暂存该 task 文件。
8. 用 task 级提交信息提交。
9. 确认该 task 没有未提交改动。
10. 提交成功后才进入下一个 task。

任一步失败都必须停止并报告 blocker。不得静默继续。

## Review 记录要求

`review.zh.md` 必须追踪 task 级证据。使用如下结构：

```markdown
## Task Records

### Task 1: <name>

- Commit: `<hash>`
- Files:
  - `<path>`
- Commands:
  - `<command>`: `<result>`
- Scope review:
  - `<brief result>`
- Notes:
  - `<remaining issue or none>`
```

只有所有 planned task 记录齐全、所有必需检查通过、工作树无未提交 milestone
改动后，才能写最终完成评估。

## 提交纪律

使用小提交。一个良好的 v0.1 实现应自然产生类似提交：

```text
chore: scaffold validation client workspace
feat: add FastAPI backend foundation
feat: add session and timeline storage models
feat: add WorldEngine connection check
feat: add session and branch APIs
feat: add evidence bundle metadata endpoint
feat: add React frontend foundation
feat: add session library UI
feat: add runtime console shell
docs: complete v0.1 foundation review
```

除非用户明确要求，不得用一个大提交完成整个 milestone。

## 分支发布纪律

以 `-local` 结尾的分支只作为本地工作分支。

不得 push 任何 `*-local` 分支。如果本地工作需要共享，必须先把 patch 等价提
交合入或重放到对应的非 local 目标分支，再用 `git cherry`、`git
range-diff` 和双向空 diff 验证等价性。

只有用户明确要求 push 时，才可以推送非 local 目标分支。

## 测试纪律

只有当前工作会话实际运行过的命令，才可以声明通过。

v0.1 预期命令包括：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
git diff --check
```

先运行 task 级聚焦检查，再运行更广的 milestone 检查。

如果沙箱导致命令无法运行，按权限规则请求批准后重试。如果仍无法运行，记录
为 blocked，不得写 passed。

## Dirty Worktree 安全

工作树可能包含用户或其他 agent 的改动。

编辑前必须检查 `git status --short --branch`。

除非用户明确要求，绝不 revert 或覆盖不是你做的改动。无关改动忽略；影响当
前任务的改动要协同处理，必要时停下来询问。

提交时只暂存当前 task 所属文件。

## Milestone 完成门禁

只有同时满足以下条件，milestone 才算完成：

- 每个 planned task 已实现，或有明确 deferred 理由
- 每个 task 在 `review.zh.md` 有 task record
- 每个 task 有 task-scoped commit
- 必需 focused checks 通过
- 必需 broad checks 通过
- `git diff --check` 通过
- `review.zh.md` 记录变更文件、命令、结果、范围审核和遗留问题
- 无相关 milestone 改动未提交

任何条件缺失，都只能报告为 partial 或 in progress，不能报告 complete。
