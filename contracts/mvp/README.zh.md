# MVP 公开合同

`scenario.json` 是 executor 和 checker 共享的唯一声明式合同。它只包含公开
`operation_id`、固定步骤和视觉证据名称，不包含 WorldEngine 内部路径或 verdict 逻辑。

Godot executor 必须严格按 `required_operations` 记录响应。独立 checker 自己实现断言，
不会导入 Godot 代码，也不会信任 executor 提供的 PASS/FAIL。
