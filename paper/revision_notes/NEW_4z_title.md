# NEW-4z：论文题目

作者 2026-11-04 对话决定（基准 `46d5595`）：题目由“阈值策略下接触控制与追踪隔离的最优控制”改为

> 基于医疗容量的阈值策略下接触与追踪隔离的最优控制

## 1 改动

| 位置 | 改动 |
|---|---|
| 主稿 `\title` | 改为新题目，一行排完 |
| 补充材料 `\title` | 新题目换行后接“补充材料”。题目变长后，原来的“：补充材料”会在“补”字后折行，所以改用换行、去掉冒号 |
| `AGENTS.md` 第 7 节 | D3 处注明作者 2026-11-04 改题 |

## 2 未改动

- 摘要、引言、讨论、结论中的“接触控制”（共 6 处）是句中用语，不随题目改。
- 正文仍用“医疗资源承载能力”。“医疗容量”只在题目中使用，作为它的简称。
- 主稿的英文题目注释 `Optimal control of contact reduction and contact tracing under a capacity-based threshold strategy` 已含 capacity-based，保留，英文稿阶段再定。
- `R1_framing.md`、`R1_storyline.md` 等历史记录中的旧题目不覆写。

## 3 选词依据

- 不写“ICU 约束”：模型没有 ICU 仓室，也不直接约束 ICU 占用，阈值约束的是 $I$；第 8.4 节把带容量状态约束时最优控制是否仍沿阈值运行列为未解决的问题。“基于医疗容量”只说明阈值的选取依据。
- 不写“保证医疗资源不被超出”一类的说法（`AGENTS.md` 4.2 节）。

## 4 检查

- 编译：主稿 39 页、补充 18 页，undefined 0、multiply defined 0、超过 10pt 的 overfull 0。与上一提交逐页比较页首，无变动；看过两份 PDF 的第 1 页。
- `check_tex.py`（`NEW_4z_check.md`）：标签缺失 0，悬空引用 0，数字无增减。
- `statement_diff.py --proofs`（`NEW_4z_statements.md`）：主稿陈述 0 条、证明 0 条变化；补充材料同样为 0。
- `nr_audit` 全量测试 411 项通过（`NEW_4z_pytest_full.xml`）。未新增计算、图件、文献与标签。

## 5 待作者决定

无。
