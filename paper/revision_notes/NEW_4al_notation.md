# NEW-4al 隔离比例两个记号的调换（N40）

基准 0e86fa7。作者 2026-11-12 在对话中决定：隔离比例的能力上限由 $q_{\rm cap}$ 改记 $q_{\max}$，与接触率下限 $c_{\min}$ 对称；仅隔离控制在 $t_1$ 跳升到的隔离比例（原 $q_{\max}$，式 (3.10)，标签 `eq:s1:qmax` 不变）改记 $q_1$，与 $t_1$ 对应。此前 Claude 建议推迟到英文稿阶段（同一符号改换含义易错，且 4 幅图的图内文字要重绘），作者决定在中文稿阶段就改。

## 1 稿件

| 文件 | $q_{\max}\to q_1$ | $q_{\rm cap}\to q_{\max}$ |
|---|---:|---:|
| 第 3 章 | 9 | 0 |
| 第 4 章 | 10 | 25 |
| 第 5 章 | 0 | 7 |
| 第 6 章 | 2 | 5 |
| 第 7 章 | 0 | 1 |
| 附录 A | 1 | 5 |
| 补充 S2 | 5 | 0 |
| 补充 S4 | 0 | 5 |
| 补充 S6 | 5 | 0 |
| 合计 | 32 | 48 |

先把全部 $q_{\max}$ 改为 $q_1$，再把全部 $q_{\rm cap}$ 改为 $q_{\max}$，两步不交叉。逐文件核对：把同样的替换施于 HEAD 版本，再换四个图件路径，结果与新稿逐字相同，即没有其他改动。全文原无 $q_1$，无冲突。摘要、引言、第 2 章不含这两个记号。

陈述变化（`NEW_4al_statements.md`）共 16 条，全部只是记号：推论 3.3、定理 3.4 的拐点条件 $q_0<\qinf<q_1$、命题 3.8 的 $\partial q_1/\partial\eta<0$；推论 4.2(ii) 的 $c_{\min}(1-q_{\max})\le c_0(1-q_1)$、推论 4.4、4.5 与 4.6(i) 的 $q_{\max}\ge q_1$；第 5 章含能力约束的 6 条（`thm:joint:cost-minimum`、`prop:joint:global-structure`、`prop:joint:terminal-allocation`、`prop:joint:minimum-threshold`、`cor:joint:capacity-clip`、`prop:joint:weight-monotone`）；补充 S2（`prop:contact-effects`）、S4（`cor:joint:allocation-range`）、S6（`prop:scaling`）各 1 条。数学含义不变。

## 2 图件

图内含这两个记号的 4 幅图只改坐标轴文字，新入口 `nr_audit/plot_new4al_notation.py` 调用原绘图函数，输出到 `paper/figures/new4al/`，收据 `nr_audit/results/new4al_notation.json`：

| 图 | 原图件 | 改动 | 生成环境 |
|---|---|---|---|
| 正文图 5（`fig:joint:capacity`） | `figures/new4p/joint_capacity_baseline.pdf` | (a) 纵轴 $q_{\rm cap}\to q_{\max}$ | Python 3.10.20 / Matplotlib 3.10.9 |
| 正文图 8（`fig:xian:joint`） | `figures/new4w/Main8.pdf` | (a) 纵轴 $q_{\rm cap}\to q_{\max}$ | 同上 |
| 补充图 S1（`fig:scenario1_summary_c0`） | `figures/new4t/S1.pdf` | (d) 纵轴 $q_{\max}\to q_1$ | Python 3.12.8 / Matplotlib 3.9.2 |
| 补充图 S2（`fig:sup:eta-summary`） | `figures/new4t/S2.pdf` | (d) 纵轴 $q_{\max}\to q_1$ | 同上 |

每幅图先在原 rc 设置下按原参数保存未改字的重画，核对与现入稿图件逐字节相同，再只替换该文字另存；图中其余文字逐项相同。S1、S2 原图由 base 环境生成，在 thesis 环境下重画字节不同，改用 base 环境后逐字节相同。不求解模型、不重算任何数据；原图件与 NEW-4p、NEW-4t、NEW-4w 的收据只读保留。

## 3 测试与来源映射

- `test_new4p_figures.py`、`test_new4t_figures.py`、`test_new4r_tradeoff.py`、`test_new4w.py`：增加被 NEW-4al 取代的分支，核对被取代图件的原字节、重画与原图相同、新图件即收据登记的输出，以及稿件引用 `figures/new4al/`。
- `test_sources.py`：图注断言中的 $q_{\rm cap}=0.6$、$0.75$ 改为 $q_{\max}$，数值不变。
- `figure_table_sources.py`：四个图的绘图入口后补 `nr_audit/plot_new4al_notation.py`。

## 4 检查

标签缺失 0，悬空引用 0，数字缺 0、增 0（`NEW_4al_check.md`）；主 38/补 18 页，0 个未定义引用；四幅新图已看过；已刷新稿件文本身份哈希；424 项测试通过（`NEW_4al_pytest_full.xml`）。

## 5 待作者决定

无。
