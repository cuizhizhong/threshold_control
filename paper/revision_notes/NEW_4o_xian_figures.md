# NEW-4o 图 8 与图 S11 改为图 2 风格

作者 2026-10-27 指示（根 `AGENTS.md` N25）：图 4 的局部放大暂不做；先把正文图 8（`fig:xian:strategy-process`）与补充图 S11（`fig:xian_eta_sens`）的字体、字号、配色与线型改为正文图 2（`fig:scenario1:single-sim`）的风格。分支 `paper/submission-ready`，基准 `4a396df`。

## 图 2 的风格（取自 `code/scenario1_q_control_with_quarantine_panels.m`）

| 项目 | 图 2 | 新图 8、S11 |
|---|---|---|
| 字体 | MATLAB LaTeX 解释器（Computer Modern） | matplotlib `cmr10` 与 `mathtext.fontset=cm`，嵌入 Cmr10/Cmmi10 |
| 印刷字号 | MATLAB 刻度 11、轴标签 13、标题 14、图例 10，导出后缩至 0.7 倍版心宽，约为原值的 0.50 倍 | 按印刷尺寸直接设定：刻度 5.5 pt、轴标签 6.5 pt、标题 7 pt、图例 5 pt、$t_1,t_2$ 标注 5.5 pt |
| 坐标轴 | 四边封闭，刻度朝内 | 同 |
| 面板标题 | 面板上方居中的数学符号 | 同，前加 (a)–(e) 以对应图注 |
| 图例 | 带黑框 | 同 |
| 线型与颜色 | 仅隔离阈值控制：蓝色实线；常规控制：黑色点划线；阈值参照：红色虚线（透明度 0.7）；$t_1,t_2$：黑色点线；另用绿、紫、品红 | 图 8 中三种策略依次为蓝色实线、黑色点划线、绿色实线；观测数据为黑色空心圆；$\eta$ 与 $R_e=1$ 为红色虚线；$t_1,t_2$ 为黑色点线并标注；观测窗口结束为灰色点线。图 S11 中扫描值为带圆点的蓝色实线，$t_{\rm end}$ 为品红，TDINN 参照为绿色虚线 |
| 线宽（印刷） | 主曲线约 1.5 pt、对照线约 1.0 pt、竖线约 0.6 pt | 同 |

## 修改

- **新绘图入口** `nr_audit/plot_xian_fig2_style.py`：只读 `reproducibility/results/20261003_release_final/xian/` 下的 `timeseries.csv`、`observed.csv`、`summary.csv`、`eta_scan.csv`、`reference.json`。原字节 SHA-256 记入 `results/new4o_xian_figures.json`。
- **画法**：面板布局、坐标尺度（对数、对称对数）、坐标范围与原图相同，原图出自 `restore_figures.xian` 与 `xian_control_comparison.plot_eta_sensitivity`。只改字体、字号、配色、线型与图例。重跑输出逐字节相同。
- **新图件**：`paper/figures/new4o/xian_strategy_process.pdf`（135×125 mm）、`xian_eta_sensitivity.pdf`（111.86×84 mm，即 0.7 倍版心宽）。按印刷尺寸生成，稿件中的宽度不变，因而不再缩放。旧图件 `figures/layout_v5/xian_strategy_process.pdf`、`figures/xian_eta_sensitivity.pdf` 保留不动。
- **图注**：
  - 图 8：(a) 补“水平虚线为 $\eta$”；“浅红色竖虚线标记仅隔离控制的启动与退出”改为“黑色竖点线标记仅隔离控制的启动 $t_1$ 与退出 $t_2$”。
  - 图 S11：“水平线为 TDINN 参照值”改为“水平虚线为 TDINN 参照值”。
- **新测试** `nr_audit/tests/test_new4o_xian_figures.py`（5 项）：核对输入原字节未变、入库图件即收据登记的输出、字体为 Computer Modern、宽度与稿件一致，以及 $t_1,t_2,\eta$、观测点数、扫描点数与 TDINN 参照值。

## 数据核对

- **时间与参照值**：$t_1=16.8967$、$t_2=101.9678$、$\eta=26326$ 取自 `summary.csv`；观测 40 天；扫描 11 个 $\eta/N$ 值；TDINN 参照值 $J=49.389$ 取自 `reference.json`。均与原图相同。
- **峰值**：时间序列最大值与汇总表峰值的相对差在 $10^{-5}$ 以内（离散采样所致）。

## 陈述、数字与验证

- **检查**：`check_tex`（相对 `4a396df`）标签缺失 0，数字 682→682；`statement_diff` 42 条陈述全部未变。
- **构建**：两轮，主稿 36 页、补充 24 页，undefined、Overfull 均 0；渲染比对了正文第 18 页（图 2）、第 24 页（图 8）与补充第 18 页（图 S11）。
- **测试**：`text_identity.py --refresh-current` 刷新现稿内容哈希后，全量测试 368 passed（既有 363 项＋新增 5 项，0 跳过；`NEW_4o_pytest_full.xml`）。

## 作者改动（一并提交）

- 摘要：“但退出时的累计感染存在与控制组合无关的下界”改为“但控制结束时的累计感染存在与控制组合无关的下界”。由作者于 2026-10-27 直接修改，作者确认一并提交。
- 本轮两份 PDF 的编译、`check_tex`、`statement_diff` 与内容哈希刷新都在这处改动之后进行，已包含它。

## 待作者决定

- 正文图 7（西安拟合）、图 3–6 与其余补充图仍是原来的 Times 风格或各自的风格；第 7 章中图 7 与图 8 现在风格不同。是否把其余图也改为图 2 风格，由作者决定。
- 推迟事项中的图 4 局部放大按作者指示暂不做；表 2 精度、补充图精简、期刊声明仍待决定。
