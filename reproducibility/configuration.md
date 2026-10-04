# 科研配置与派生结果索引

本文件和 `configuration_index.json` 是集中检索说明，不是新的运行配置入口。当前程序仍从原 MATLAB/Python 参数模块及冻结的联合控制参数文件读取设置；修改本索引不会改变计算。以下源码路径相对于项目根目录，`<RUN>` 指一次独立运行目录，例如总入口创建的 `run_1`，不是历史归档目录。

## 哪些是输入，哪些必须重新计算

固定输入包括原始日报 Excel、模型参数、TDINN 函数的已给定系数、成本权重、设计阈值和扫描规则。拟合的 `I0`、`S0=N-I0`、TDINN 峰值/成本/累计/清零时间、人口临界值、扫描极值和控制切换时刻均是派生结果。后者必须从同一次运行的未取整输出读取，不能把旧稿中的小数、图例数字或旧 `full_city_I0_reference` 常数改作正式计算输入。

| 计算部分 | 实际权威来源 | 本轮参数及未取整结果 |
|---|---|---|
| 小人口基准、MATLAB 图谱 | `scenario1_threshold_landscape/common/scenario1_params.m`、`common/compute_metrics.m`；单次完整轨迹另见 `code/scenario1_q_control_with_quarantine_panels.m` | `<RUN>/workspace/scenario1_threshold_landscape/current_run/output_csv/landscape_summary.csv`、`main_c0_summary.csv`、`main_eta_summary.csv`；运行源码及输入哈希见 `source_manifest.json` |
| 拐点诊断图 | `scenario1_inflection/fig_lambda_sensitivity.py`、`fig_scan_t.py`、`inflection_analysis.py` | `<RUN>/validation/baseline_science.json`、`logs/inflection_checks.log`；完整曲线依据运行区中的同源脚本重建，不声称全部扫描都另存 CSV |
| 西安拟合、三策略、阈值图谱 | `reproducibility/xian.py:Params/controls/fit_initial/integrate/run_xian`；Excel 读取沿用 `xian_control_comparison/xian_control_comparison.py:load_observed_data` | `<RUN>/xian/fit.json`、`reference.json`、`summary.csv`、`timeseries.csv`、`eta_scan.csv`、`heatmap.csv` |
| 有效人口比较 | `reproducibility/population.py:run_population/main_critical/theta_root/population_arc` | `<RUN>/population/critical.json`、`metadata.json`、`representative_summary.csv`、`arcs.csv`、`beta_scan.csv`、`supplementary_anchors.json` |
| 接触率敏感性 | `reproducibility/c0.py:run_c0/boundaries`；原绘图函数仍在 `c0_sensitivity/run_c0_sensitivity.py` | `<RUN>/c0/parameters.json`、`extrema.json`、`scan.csv`、`representative_summary.csv`、`phase.npz`、`beta_existence.npz` |
| 联合控制 | 冻结包 `joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json` 的 `parameters`；原核心 `numerics/joint_comparison.py`；实际数值设置见 `reproducibility/joint.py` | `<RUN>/joint/results.json`、`results.csv`、`openloop_check.json`、`root_diagnostics.json`、`trajectories.csv` |

## 初值和 TDINN 函数

西安固定 `N=13163000, beta=0.1498, gamma=0.2953, delta_q=0.3531, c0=12.8872, q0=0.3230`，只拟合绝对 `I0`，其余初始仓室为零，`S0=N-I0`。四个等权 MSE 序列分别是社区/隔离日新增和社区/隔离累计；日新增由整数日累计之差计算。当前数据为40个日区间；拟合函数按实际读取行数建网格，固定40日 S2诊断另外明确写在 `run_xian` 中。

TDINN 的两条控制函数是固定输入，不在本轮重新训练：

```text
c(t) = (12.8872 - 3.4625) exp[-(0.0463 t)^2] + 3.4625
q(t) = (0.3230 - 0.9844) exp[-(0.0452 t)^2] + 0.9844
```

西安、人口及接触率主实验统一读取本轮 `xian/reference.json` 的 `I0_abs`。人口改变时该绝对数保持不变，归一化 `i0=I0/N` 随之改变。固定归一化初值的规模不变性/清零弧是另存的诊断，不能与主实验混用。接触率实验的 `N=20000, theta=0.002`；20k下再次拟合只记录在 `c0/parameters.json` 的 `fit_at_20k_diagnostic`，不会替换主实验的全市拟合初值。S2固定 `I0=1` 是另一诊断设置。

## 数值设置及扫描

精确数值见 JSON 索引。主西安 ODE 使用归一化10状态 `DOP853` 和分量绝对容差；TDINN/常规轨迹连续积分，情景一阈值控制按三阶段连接，平台隔离控制函数预先由理论时间轨迹构造。下降 `I=1` 是清零事件，不是最初从小初值上升穿越1的事件。

MATLAB 指标积分、MATLAB 单图 `ode45`、Python 拐点启动时间、联合控制候选积分和时间开环核对各有其原设置，不能将它们概括为“所有实验共用同一容差”。联合控制冻结 JSON 的 `quadrature`、`full_ode` 等描述字段目前不被新入口读取；新入口只从其 `parameters` 构造模型。实际精细/粗糙档、1025/4097控制采样及分支插值由 `joint.py` 定义。

主要扫描覆盖：MATLAB 241×118图谱，西安11个阈值及98×47网格，人口16点弧/17个代表案例/六档传播概率/时长约束，接触率625个连续扫描点、70点边界、120×140相图和220×220拐点存在域。网格中的不可行点保留状态或 `NaN`，不当成有效结果。扫描数量是当前规则的结果，不是额外的模型参数。

## 从源码到论文的追溯

`run_all.py` → `bootstrap.prepare_workspace`（只克隆源码、原始输入及视觉参考）→ 各科学阶段的新输出 → `figures.py` 绑定同轮未取整数值 → `paper_sync.prepare_manuscript` 生成 `manuscript/staged.tex` 和 `staged_supplement.tex` → `build.py` 编译。`configuration_index.json` 列出路径与函数定位；本轮实际源码哈希由 `source_manifest.json`、`validation/source_integrity_initial.json`、`validation/source_integrity.json` 记录，运行环境及字体由 `environment.json` 记录。

`paper_anchor_updates.json` 的历史旧值对照是可选 provenance。旧输入缺失时仍保留新字段，旧值标记为未知，不影响科学阶段通过判据；不能把这份对照的历史文件哈希误称为全部科学输入。`manuscript_changes.json` 记录有来源绑定的取整与替换，论文表格/图注的取整数不是下游计算输入。

修改研究设定需先定位并更新对应权威源码，保持同一组模型参数在调用链和独立核查中一致，再从新的空目录重新运行。冻结包和原始数据不修改；另设情景时应另建明确的参数入口及版本，不直接改冻结 JSON。当前索引仅做静态追溯，本次编写未重算、未新增数学或临床验证，也不代表完整双跑及人工版面验收已完成。
