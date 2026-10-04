# 情景一阈值响应图谱

本目录用于独立生成 `N=763` 情景一阈值响应图谱，不修改主论文工程，也不覆盖主项目中的 `figures/`、`tables/` 或 `code/` 结果。

## 当前正式稿中的定位

正式主稿为 `../latex/flatten_curve_analysis_cn.tex`。本模块提供仅隔离基准的计算和原绘图逻辑，
当前对应图 3（`fig:baseline:q-joint`）、图 4（`fig:scenario1_heatmaps_c0_eta`）、
图 7（`fig:scenario1_summary_c0`）和图 8（`fig:scenario1_summary_eta`）。
原独立图经 `../latex/revision_layout_v5/` 等既有布局适配后入稿，不应直接复制旧输出覆盖正式图。
正式复现使用 `../reproducibility/run_all.ps1` 的新建空输出目录流程；映射和来源见
`../reproducibility/registry.json`。本文档中的 2026-07 历史统计不代表本次新增复跑。

## 目录结构

```text
scenario1_threshold_landscape/
├── README.md
├── run_all.m
├── common/
├── scripts/
└── current_run/                   # 运行时创建，不纳入版本控制
```

- `run_all.m`：推荐入口，先清空 `current_run/` 输出目录，再顺序生成数据、图和表。
- `scripts/`：数据生成、单独绘图和表格脚本。
- `common/`：共享参数、指标计算、轨迹重构、读表和保存图形函数。
- `current_run/`：运行时创建的最新一轮完整结果，不纳入版本控制。
- 清理前的完整结果快照位于
  `../archive_unused/generated_snapshots/scenario1_threshold_landscape_current_run/`。

## 独立模块运行（会清空当前输出）

从任意位置运行：

以下入口只用于模块实验，不是当前正式稿的完整复现入口。先保存所需旧运行，避免清空后丢失。

```powershell
matlab -batch "run('E:\work\draft\scenario1_threshold_landscape\run_all.m')"
```

运行 `run_all.m` 会先清空 `current_run/` 的 `output_csv/`、`figures/`、`tables/`、`logs/`（避免上一轮的过期文件残留），再重新生成本轮完整结果。`current_run/` 已加入 `.gitignore`；如需长期保留某次结果，应在重跑前复制到 `archive_unused/` 下的新目录并补充归档说明。

注意：单独重画某一类图（下面“单独运行模块”）不会清空目录，只覆盖对应输出；清空只发生在 `run_all.m`。

## 单独运行模块

已有 `current_run/output_csv/landscape_summary.csv` 后，可以单独重画某一类图，例如：

```powershell
matlab -batch "run('E:\work\draft\scenario1_threshold_landscape\scripts\plot_heatmaps.m')"
```

常用脚本：

- `scripts/generate_landscape_data.m`：只生成 CSV 和诊断。
- `scripts/validate_main_outputs.m`：检查网格行数、有效指标、诊断码、五组控制时长峰值和拐点恒等式。
- `scripts/plot_baseline_validation.m`：生成基准验证图和基准表。
- `scripts/plot_main_q_trajectories.m`：生成两个隔离率原图（旧稿图 5/6），当前适配合为图 3，含 `q_inf` 与内部拐点标记。
- `scripts/plot_sensitivity_curves.m`：生成一维敏感性图；`c0` 图的 `Delta_t`
  面板使用线性纵轴并标出离散峰值；`eta` 图使用四档 `c0` 曲线，其 `q_max`
  面板固定为 `0.45--0.85`。
- `scripts/plot_heatmaps.m`：生成六张单指标热图和主论文 2×2 合成热图。
- `scripts/plot_duration_regions.m`：生成控制时长区域图。
- `scripts/plot_representative_trajectories.m`：生成代表轨迹图。
- `scripts/plot_cumulative_decomposition.m`：生成累计感染分解图。
- `scripts/write_representative_tables.m`：生成代表组合表。
- `scripts/write_main_summary_tables.m`：生成主论文候选的 `c0`、`eta` 汇总 CSV 和 LaTeX 表。

## 当前参数域与主论文候选图

当前完整网格为：

```matlab
eta_frac_list = 0.002:0.0002:0.050;
c0_list = 2.3:0.1:14;
```

即 `241 x 118 = 28438` 个参数点。主论文候选的一维曲线使用：

- 固定 `eta/N=5%`，隔离率原图取 `c0=[4,5,8,10,12]`（当前合图 3 的一个面板）；
- 固定 `c0=10`，取 `eta/N=[0.2%,0.6%,1%,2%]`；
- `c0` 敏感性图使用上述四档阈值，其中 `Delta_t` 面板使用线性纵轴；
  `eta` 敏感性图使用 `c0=[5,8,10,12]`、完整阈值网格和对数横轴，其中
  `q_max` 面板固定纵轴范围为 `0.45--0.85`。

历史入稿记录：上述输出于 2026-07-29 完成当时的审图，正式用于当时主论文图 5--9：图 5/6 保持同名，
`c0_sensitivity_selected_eta.pdf` 和 `eta_sensitivity_selected_c0.pdf` 分别以论文既有文件名
`scenario1_summary_c0.pdf`、`scenario1_summary_eta.pdf` 入稿，四面板景观图保持
`scenario1_heatmaps_c0_eta.pdf` 文件名。模块仍独立生成结果，不在运行脚本中自动覆盖论文工程。

当时的独立图按入稿物理尺寸导出，避免 LaTeX 再次缩小图中文字。旧图 5/6 的 PDF 尺寸约为
`324.9 x 231.5 bp`，图 7/8 约为 `397.1 x 260.4 bp`，图 9 约为
`451.3 x 330.8 bp`。最终字号规范为：刻度 `8.5 pt`，坐标标签和面板标题 `10 pt`，
图例 `7.5 pt`，面板编号 `11 pt`，普通注释 `8.5 pt`，热图等值线标签 `8 pt`。
旧图 5--8 使用矢量 PDF；旧图 9 保持 600 dpi image PDF。此处保留旧独立出口规范，
不要求把当前组合图恢复为旧图号或尺寸；当前正式图件以已认可的布局适配和主稿标签为准。

## 当前结果

重新运行后，最新结果位于 `current_run/`；完整一轮应包含：

- `current_run/output_csv/`：8 个 CSV；
- `current_run/figures/`：17 张 PDF；
- `current_run/tables/`：4 个 LaTeX 表格；
- `current_run/logs/`：各脚本运行日志。

归档的最近一次完整运行（2026-07-28）得到：

- `landscape_summary.csv`：28438 行；
- `valid`：26780/28438；
- `diagnostics.csv`：1658 条，均为预期的阈值不可达记录；
- 五档 `eta/N=0.2%,0.5%,1%,2%,5%` 的离散 `Delta_t` 峰位分别为
  `c0=4.3,4.3,4.4,4.6,5.1`；
- `scenario1_u_time_c0.pdf`、`scenario1_u_time_eta.pdf`：
  当时主论文图 5/6 候选（当前合为图 3）；
- `c0_sensitivity_selected_eta.pdf`、`eta_sensitivity_selected_c0.pdf`：
  当时主论文图 7/8 候选（当前图 7/8 仍以此为来源并经适配）；
- `scenario1_heatmaps_c0_eta.pdf`：当时主论文图 9 的 2×2 候选（当前图 4）。

本模块的触发网格未另设 `q_cap<1`。正文已经给出额外能力上限下的仅隔离实施判据
`q_max<=q_cap`；该条件不应与“常规峰值低于阈值，因而无需加强隔离”混为一谈。
