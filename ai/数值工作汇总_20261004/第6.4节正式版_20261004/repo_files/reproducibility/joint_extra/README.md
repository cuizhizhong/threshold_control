# joint_extra：第 6.4 节新增图表的计算与绘图

本模块为第 6.4 节新增的命题、注记、4 幅图和 1 张表提供数据与图件。它只读取冻结包与正式复现输出，不修改它们。

## 输入

- 基准参数：`ai/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json`（N=763，η=0.05N，w_c=1，w_q=2）。
- 西安参数：`reproducibility/results/20261003_release_final/xian/reference.json` 的 `I0_abs`；S0=N−I0，η=0.002N，w_c=1，w_q=2。TDINN 参照量直接取该文件。

## 运行（项目根目录）

```powershell
python -B reproducibility\joint_extra\run.py        # 约 3 分钟，写 reproducibility/results/joint_extra_v1/
python -B reproducibility\joint_extra\figures.py    # 只读结果文件，写 latex/figures/joint_v1/
```

`run.py` 可用 `--out`、`--baseline`、`--xian-reference` 改路径；`figures.py` 可用 `--res`、`--out`。

## 方法

- 平台类内逐状态全局最小：s=S/S_c，x=c/c0，在允许区间 x∈[max(1/s, c_min/c0), min(1, (1−q0)/((1−q_cap)s))] 的 4001 点网格上找全局最小格点，再作抛物线加密；状态网格 8001 点。
- 时间轨迹：三阶段时间开环。常规控制至 I=η（上升）；平台期按名义 S(t) 预先构造 c(t)、q(t) 的时间函数输入完整 SIQR（DOP853，rtol=1e-11，atol=1e-13·N）；名义退出后恢复常规控制，至 I=1（下降）。
- 成本—时长曲线：对 J+κΔt 逐状态最小化，扫描 310 个 κ。
- 权重相图：r=w_q/w_c 取 [0.1, 20] 上 161 个对数等距值，s 取 1201 点。

## 输出（`reproducibility/results/joint_extra_v1/`，均为未取整结果）

| 文件 | 内容 | 用于 |
|---|---|---|
| `compare_baseline.csv`、`compare_xian.csv` | 四种分配（西安另含 TDINN 参照）的 t1、t2、Δt、清零时间、总累计感染、控制期新增 S_q 与 I_q、(I+I_q) 峰值、J、J_c、J_q、q 峰值、c 最小值、平台期漂移、守恒律核对值 | 表 tab:joint:compare，正文数值 |
| `trajectories_baseline.csv` | 基准四种分配的 S、I、S_q、I_q、c、q 时间序列 | 图 fig:joint:compare |
| `frontier_baseline.csv`、`alpha_family_baseline.csv` | κ 扫描的 (Δt, J, 感染, S_q) 与显式族 | 图 fig:joint:frontier |
| `capacity.json`、`capacity_traj_*.csv` | 三区域边界参数、代表能力点结果与轨迹 | 图 fig:joint:capacity |
| `phase_*.npz`、`phase.json` | (s, r) 网格上的接触份额、跳变位置、临界 r | 图 fig:joint:phase |
| `structure_checks.json` | 命题 prop:joint:global-structure 的数值核对（r∈{0.1,0.5,1,2,5,20}） | 核对 |
| `convergence.json` | 网格 (4001,2001)/(8001,4001)/(16001,8001) 下的 J_min 与 Δt | 正文收敛说明 |
| `manifest.json` | 输入与源码 SHA-256、软件版本、设置 | 追溯 |

对账：基准类内最小成本 J=2.1182745585、Δt=7.7535977 与 `20261003_release_final/joint/results.csv` 一致；西安仅隔离 85.0711 d、J=40.7686、清零 258.1044 d、累计 2377943 与正式结果一致。网格加密一倍后 J_min 相对变化 < 1e-12，Δt < 2e-8。

## 图件（`latex/figures/joint_v1/`）

样式沿用 `xian_dom/` 的设置：Times New Roman / STIX，9 / 10 / 8.5 pt，pdf.fonttype=42。全宽图的宽度为 451.28 bp（= \textwidth），成本—时长图为 0.6\textwidth；插图时缩放为 1.0，已用 pdfinfo 复量。`figure_manifest.json` 记录各 PDF 与 `figures.py` 的哈希。

| 文件 | 图号标签 | 宽度 |
|---|---|---|
| `joint_compare_baseline.pdf` | fig:joint:compare | \textwidth |
| `joint_frontier_baseline.pdf` | fig:joint:frontier | 0.6\textwidth |
| `joint_capacity.pdf` | fig:joint:capacity | \textwidth |
| `joint_phase_weights.pdf` | fig:joint:phase | \textwidth |

## 对主稿的影响（受影响图表清单）

- 第 6.4 节末尾新增：式 eq:joint:ssw、命题 prop:joint:global-structure（含证明）、注记 rem:joint:duration-constraint、4 幅图、1 张表及相应正文段落。
- 改动 1 句：第 6.4 节"上述逐状态分配利用了成本中……"一段，把"总时长、累计隔离预算"改为"控制调整速度或隔离人天等跨状态预算"，并说明时长上限与新增隔离易感者上限可用乘子处理。
- 不修改任何已有图件、表格数值或公式；其后的图、表、命题编号因插入而顺移（正文全部用 \ref，无需手改）。
- 本模块的数值为联合控制的补充结果；仅隔离、TDINN、常规控制的正式数值仍以 `20261003_release_final` 为准。
