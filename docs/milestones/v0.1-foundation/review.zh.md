# v0.1 Foundation Review

状态：待实现

## 实现授权

当前状态：允许按 `plan.zh.md` 开始实现。

## 变更文件

待实现后填写。

## 验证命令

计划运行：

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
git diff --check
```

## 范围审核

待实现后确认：

- 是否只通过 public API 连接 WorldEngine。
- 是否未引入客户端 LLM key 管理。
- 是否未直接调用 LLM provider。
- 是否未生成权威世界事实。
- 是否未引入玩家角色控制。

## 遗留问题

待实现后填写。
