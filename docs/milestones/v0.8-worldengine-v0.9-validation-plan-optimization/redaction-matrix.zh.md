# Redaction Matrix

英文镜像：`redaction-matrix.md`。

## Blocking flags

PASS 要求所有 blocking flags 为 `false`：

- `api_keys_included`
- `authorization_headers_included`
- `raw_prompts_included`
- `raw_provider_requests_included`
- `raw_provider_responses_included`
- `provider_traces_included`
- `private_agent_memory_included`
- `private_agent_goals_included`
- `raw_thought_included`
- `hidden_context_included`
- `private_evaluator_data_included`
- `seed_or_oracle_data_included`

## Scanner 规则

- marker 只出现在 redaction 字段名中时，分类为 metadata。
- marker 出现在 displayable/exportable artifact 内容中时，bundle 必须 `fail`。
- path 必须为相对路径；绝对路径或 `..` path traversal 必须 `fail`。
- blocked/not_run 不等于 redaction clean；二者应分别记录。
