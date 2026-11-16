# NEW-4at 删去显式控制族（N48）

基准 fa7787a（NEW-4as），执行前标签 `pre-explicit-cut-20261116`。作者 2026-11-16 听取“留对照、删理论”与“全部删去”两种方案后决定全删，回复“按计划开始删去”。

## 1 理由（作者认可的判断）

- 理论部分：显式族的轨迹与时长闭式、定理 4.2(ii) 都是定理 4.1、4.2(i) 的直接推论，删去时长约束与能力约束后，后文没有结果用到它们。
- 对照部分：$\alpha=0.5$ 的时长、感染与隔离人数居于两种单控制之间由定理 4.2 直接得到，成本高于成本最优控制是定义；“节省全部来自 $S<S_{\rm sw}$ 一段”第 6.2 节已写明。

## 2 改动

| 位置 | 改动 |
|---|---|
| 第 4 章 | 删 4.2 节“显式控制族”（式 `eq:joint:explicit-c`、`eq:joint:explicit-q`）；定理 `thm:joint:comparison` 删 (ii)，原 (iii)(iv) 顺延为 (ii)(iii)，证明同步；4.2 节（原 4.3 节）末句改为“取两种单控制的凸组合，控制时长随组合系数连续变化”。第 4 章现为两节 |
| 第 6 章 | 导语、6.2 节标题与正文“四种控制”改“三种控制”；排序句删 $\alpha=0.5$；定理引用 (iv) 改 (iii)；表 1 删 $\alpha=0.5$ 一行、表注改“三种”；图 4 换新图、图注改“三种” |
| 第 7 章 | 表 3 删 $\alpha=0.5$ 一行，表题与表注改“三种” |
| 补充材料 | 删“显式控制族”一节（定理 `thm:joint:explicit` 及证明、式 `eq:joint:explicit-S`、`eq:joint:explicit-duration`、`eq:joint:explicit-zero`、标签 `sec:sup:explicit`）与导言中的指引；各节顺次重新编号为 S1–S6。源文件 `S4_explicit_control.tex` 原样留作存档，不再 `\input` |
| 补充数值一节 | 收敛表“四种控制”改“三种控制”；`nrConvTolMaxRel` 由 $3\times10^{-12}$ 变为 $2\times10^{-12}$（不再计入 $\alpha=0.5$，结果文件不改） |

## 3 删除清单与去向

| 内容 | 类别 | 去向 |
|---|---|---|
| 定理 `thm:joint:explicit`（补充）与定理 4.2(ii) | 删去（作者同意） | 恢复见第 6 节 |
| 表 1 行：9.24、37.11、323.4、346.2、2.55、1.64 | 删去 | `reproducibility/.../joint_extra/compare_baseline.csv`（strategy=alpha_0.5）；`new4s_figures.json` |
| 表 3 行：250.01、468.70、2.556、7.776、89.88、3.32 | 删去 | `nr_audit/results/new4w/xian_theta001.json` 的 `laws.alpha` |
| 图 4 中 $\alpha=0.5$ 的品红虚线 | 删去 | 旧图 `paper/figures/new4s/joint_compare_baseline.pdf` 保留 |

删除存疑：无。因篇幅删去的机制句：无。

## 4 陈述、数字与检查

- statement_diff：第 4 章 1 条陈述有变化（定理 4.2 删 (ii)），证明 1 处随之删去并重编条号；第 6、7 章与补充数值一节陈述、证明零变化（`NEW_4at_statements_*.md`）。其余陈述的数学含义与证明逻辑不变。
- check_tex（`NEW_4at_check.md`）：标签缺失 7 个，均为上表经授权删去的标签；悬空引用 0；数字缺 16、增 0，全部出自两表的 $\alpha=0.5$ 行与正文的 $\alpha=0.5$。
- 图 4：新入口 `nr_audit/plot_new4at_fig4.py` 复用 NEW-4s 的绘图函数，输入按 NEW-4s 收据核对 SHA-256，其余三条轨迹的记录与 NEW-4s 逐项相同，横轴上限不变。收据 `nr_audit/results/new4at_fig4.json`；范围收据 `nr_audit/results/new4at_scope.json`。不解 ODE、不优化。
- 编译：正文 34 页、补充 14 页（页数均不变），0 个未定义引用，无超过 10pt 的 Overfull hbox；看过正文第 11–13、16–17、20 页与补充第 1 页。
- 测试：新测试 `test_new4at.py`（5 项）；`test_new4s_figures.py`、`test_new4w.py`、`test_new4ao.py`、`test_new4ap.py` 增加被 NEW-4at 取代的分支，参照数值不变。全量 450 项通过（原 445 项加新增 5 项），见 `NEW_4at_pytest_full.xml`。

## 5 待作者决定

无。

## 6 恢复方法

`git show pre-explicit-cut-20261116:<路径>` 取回第 4、6、7 章与补充主文件；补充主文件加回 `\input{supplement_sections/S4_explicit_control}` 与导言指引句，图 4 改回 `figures/new4s/joint_compare_baseline.pdf`。
