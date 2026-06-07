# Redaction Matrix

Chinese mirror: `redaction-matrix.zh.md`.

All displayable and exportable artifacts must declare redaction status. Blocking
flags include API keys, authorization headers, raw prompts, raw provider
requests/responses, provider traces, private Agent memory/goals, raw thought,
hidden context, private evaluator data, and seed/oracle data.

Forbidden markers in redaction field names are metadata. Forbidden values in
artifact content are leaks and force `fail`.
