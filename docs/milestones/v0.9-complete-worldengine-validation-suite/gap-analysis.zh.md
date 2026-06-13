# Gap Analysis

英文镜像：`gap-analysis.md`。

## 结论

当前 Validation Client 的产品方向和最终目标一致，但当前功能和用例还没有形成
“一次性完整验证 WorldEngine”的稳定 suite。

它现在更接近：

```text
v0.7 自主验证留证框架 + v0.8 checker handoff / blocked export 基础
```

而不是完整 suite。

## 已满足

- 独立仓库。
- Web 客户端承载验证体验。
- 只通过 WorldEngine public API / manifest / OpenAPI 连接。
- 不保存 provider key，不直接调用 LLM。
- 支持创建世界的基础 public API flow。
- 支持 director guidance 基础 flow。
- 支持 operation log、API summary、evidence bundle、redaction scan。
- 支持 blocked handoff，不把不可达或缺 artifact 伪装成 PASS。

## 主要缺口

| 缺口 | 为什么重要 |
| --- | --- |
| 用例结构仍绑定 WorldEngine v0.9/v0.12 | 客户端应验证“WorldEngine 是否工作”，不是验证某个 WorldEngine 迭代文档。 |
| Runtime controls 没有真实驱动 WorldEngine | Run/Pause/Single Tick 如果只是本地 UI 状态，不能证明世界运行。 |
| 缺少完整 suite result directory | 没有统一承载 L0-L8 结果、coverage、command、redaction、review。 |
| Agent memory / rest / continuity 未纳入客户端主流程 | 无法证明 Agent 能持续生活。 |
| 小说式投影和诊断对话未纳入主流程 | 无法验证外部观察面是否可用于判断运行情况且不写入世界。 |
| artifact 命名和 checker handoff 不稳定 | 需要一个 suite-level artifact contract，兼容 WorldEngine checker。 |
| second-Agent review 仍是占位 | 不能支撑完整验证 closeout。 |

## 正确修复方向

不要继续创建：

```text
WorldEngine v0.13 validation
WorldEngine v0.14 validation
WorldEngine v0.15 validation
```

应创建并维护：

```text
complete-worldengine-validation-suite
```

然后通过 capability discovery 判断当前 WorldEngine 支持哪些层级：

- endpoint 不存在：`blocked / capability_gap`
- endpoint 存在但返回失败：`fail / product_behavior`
- evidence 不完整：`blocked / client_evidence`
- checker 不支持：`blocked / checker_gap`
- redaction 命中：`fail / redaction`

这样客户端用例稳定，WorldEngine 版本变化只影响本次 run 的覆盖结果。
