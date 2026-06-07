# v0.8 WorldEngine v0.9 Validation Plan Optimization Review

英文镜像：`review.md`。

状态：文档自审通过 / 实现已授权
implementation_authorized: yes
provider_live_call_authorized: no
checker_execution_authorized: conditional
external_validation_authorized: no

## 授权

用户已授权：创建 v0.8 文档并完成自审后，继续进入实现；中间除非遇到无法自行决策的门禁，否则推进到待验证状态。

## Task Records

### Task 1: v0.8 文档、路由和自审

- Commit: pending
- Files:
  - `AGENTS.md`
  - `AGENTS.zh.md`
  - `docs/README.zh.md`
  - `docs/roadmap.zh.md`
  - `docs/agent-guides/routing.md`
  - `docs/agent-guides/routing.zh.md`
  - `docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization/`
- Commands:
  - `git diff --check`: 通过，exit 0，无输出。
  - `python3 -c "from pathlib import Path; root=Path('docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization'); required=['README','intent','contract','technical-design','test-plan','plan','implementation-task-plan','scenario-operation-matrix','artifact-contract','redaction-matrix','autonomous-validation-runbook','second-agent-review-template','cross-repo-validation-gate-matrix','planning-readiness-checklist','handoff-status','next-chat-quickstart','handoff-prompts','validation','codex-run-report-template','agent-review-template','human-validation-template','review']; missing=[]; [missing.append(f'{base}.md') for base in required if not (root/f'{base}.md').exists()]; [missing.append(f'{base}.zh.md') for base in required if not (root/f'{base}.zh.md').exists()]; print({'files': len(list(root.glob('*.md'))), 'missing': missing, 'gitkeep': (root/'validation-runs/.gitkeep').exists()}); raise SystemExit(1 if missing or not (root/'validation-runs/.gitkeep').exists() else 0)"`: 通过，`{'files': 44, 'missing': [], 'gitkeep': True}`。
  - `rg -n "TBD|TODO|implement later|fill in details" docs/milestones/v0.8-worldengine-v0.9-validation-plan-optimization docs/README.zh.md docs/roadmap.zh.md docs/agent-guides/routing.md docs/agent-guides/routing.zh.md AGENTS.md AGENTS.zh.md --glob '!plan.zh.md' --glob '!test-plan.zh.md' --glob '!review.zh.md'`: 无命中，exit 1，按 `rg` 语义表示未发现占位符。
- Scope review:
  - v0.8 被定义为可重复的 WorldEngine v0.9 验证计划优化迭代。
  - 文档包覆盖 scenario matrix、artifact contract、redaction matrix、gate matrix、runbook、Codex/Agent/human 模板和 handoff。
  - 路由和 AGENTS active milestone 已指向 v0.8。
  - 客户端边界仍是 `display_export_only`；不拥有 provider、evaluator、PASS 判定或权威世界状态。
  - UI smoke、API tests、bundle export 成功不得写成 WorldEngine validation PASS。
- Notes:
  - WorldEngine 侧 `0.9.11` handoff 当前是文档草案，本仓库只读消费，不修改 WorldEngine。
  - 当前工作树存在 v0.7 validation artifacts 既有脏文件；本任务不纳入这些文件。
  - 原始占位符扫描不排除文件时只命中文档中记录的扫描命令文本；review 采用排除 `plan.zh.md`、`test-plan.zh.md`、`review.zh.md` 后的实际内容扫描。

## 当前结论

Task 1 文档自审通过。按用户授权，下一步进入 Task 2：WorldEngine v0.9 public surface discovery。
