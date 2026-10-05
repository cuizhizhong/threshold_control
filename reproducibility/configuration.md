# 科研配置与派生结果索引

本文件和 `configuration_index.json` 是集中检索说明，不是新的运行配置入口。当前程序仍从原 MATLAB/Python 参数模块及冻结的联合控制参数文件读取设置；修改本索引不会改变计算。以下源码路径相对于项目根目录，`<RUN>` 指一次独立运行目录，例如总入口创建的 `run_1`，不是历史归档目录。

## 哪些是输入，哪些必须重新计算

固定输入包括原始日报 Excel、模型参数、TDINN 函数的已给定系数、成本权重、设计阈值和扫描规则。拟合的 `I0`、`S0=N-I0`、TDINN 峰值/成本/累计/清零时间、人口临界值、扫描极值和控制切换时刻均是派生结果。整稿从头复现时，后者必须从同一次运行的未取整输出读取，不能把旧稿中的小数、图例数字或旧 `full_city_I0_reference` 常数改作正式计算输入。新增联合模块的局部模式例外：按本轮明确任务约定读取锁定的 `results/20261003_release_final/xian/reference.json`，记录其 SHA-256 并注明科学证据继承；这不构成新的西安拟合或整稿复跑。

| 计算部分 | 实际权威来源 | 本轮参数及未取整结果 |
|---|---|---|
| 小人口基准、MATLAB 图谱 | `scenario1_threshold_landscape/common/scenario1_params.m`、`common/compute_metrics.m`；单次完整轨迹另见 `code/scenario1_q_control_with_quarantine_panels.m` | `<RUN>/workspace/scenario1_threshold_landscape/current_run/output_csv/landscape_summary.csv`、`main_c0_summary.csv`、`main_eta_summary.csv`；运行源码及输入哈希见 `source_manifest.json` |
| 拐点诊断图 | `scenario1_inflection/fig_lambda_sensitivity.py`、`fig_scan_t.py`、`inflection_analysis.py` | `<RUN>/validation/baseline_science.json`、`logs/inflection_checks.log`；完整曲线依据运行区中的同源脚本重建，不声称全部扫描都另存 CSV |
| 西安拟合、三策略、阈值图谱 | `reproducibility/xian.py:Params/controls/fit_initial/integrate/run_xian`；Excel 读取沿用 `xian_control_comparison/xian_control_comparison.py:load_observed_data` | `<RUN>/xian/fit.json`、`reference.json`、`summary.csv`、`timeseries.csv`、`eta_scan.csv`、`heatmap.csv` |
| 有效人口比较 | `reproducibility/population.py:run_population/main_critical/theta_root/population_arc` | `<RUN>/population/critical.json`、`metadata.json`、`representative_summary.csv`、`arcs.csv`、`beta_scan.csv`、`supplementary_anchors.json` |
| 接触率敏感性 | `reproducibility/c0.py:run_c0/boundaries`；原绘图函数仍在 `c0_sensitivity/run_c0_sensitivity.py` | `<RUN>/c0/parameters.json`、`extrema.json`、`scan.csv`、`representative_summary.csv`、`phase.npz`、`beta_existence.npz` |
| 联合控制 | 冻结包 `joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json` 的 `parameters`；原核心 `numerics/joint_comparison.py`；实际数值设置见 `reproducibility/joint.py` | `<RUN>/joint/results.json`、`results.csv`、`openloop_check.json`、`root_diagnostics.json`、`trajectories.csv` |
| 新增联合分配、能力、权重及成本—时长 | `reproducibility/joint_extra/core.py`、`run.py`；基准参数仍读取冻结JSON，西安局部模式明确继承已验收reference，完整模式读取同轮reference | `<RUN>/joint_extra/input_manifest.json`、`compare_*.csv`、`capacity.json`、`phase_*.npz`、`frontier_baseline.csv`、`validation.json`、`convergence.json`；失败项保留状态 |

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

修改研究设定需先定位并更新对应权威源码，保持同一组模型参数在调用链和独立核查中一致，再从新的空目录重新运行。冻结包和原始数据不修改；另设情景时应另建明确的参数入口及版本，不直接改冻结 JSON。当前索引仅做来源追溯，不是计算程序。2026-10-04 新增联合模块第三批 `run_5/run_6` 已分别完成 A–D 科学计算并通过逐任务门槛；该事实来自实际输出，不能由索引本身推得。整稿旧科学结果继承、重复性比较、文案编译与人工页面核查分别记录，数值通过不代表一般数学证明或临床验证。

## 新增联合模块与受控稿源

新增模块采用相同二次成本、共同触发/退出条件和完整候选判据，不新增线性综合成本或回流模型。其锁定配置、分支比较、独立预定时间开环及加严结果分别写入本轮输出，不以旧候选CSV替代计算。旧单项 `J_c`、`J_q` 仍是线性强度参考量。

本轮通过版本为 `joint-extra-20261004-v4-geometry-branch-repair`，实际权威设置是 `joint_extra/acceptance.json`，不是冻结包中描述性容差。名义时钟在能力几何折点处分段，积分在 PCHIP 区间及能力折点上按 Gauss 4/8/16 阶比较；根残差、独立网格、完整时间开环仓室 ODE、守恒/恒等式及加严差异均有逐项结果。前两批失败保留原算法、输入身份和诊断，不能用通过版本重标旧运行。有限网格与浮点候选检查不认证驻点完备性或一般最优解唯一性。

能力图的代表点为基准 `(c_min/c0,q_cap)=(0.5,0.6)` 与西安 `(0.5,0.75)`；控制轨迹视窗延长退出后1日仅为绘图配置，实际累计和清零指标仍使用各自的终点。任务C是有限权重/状态网格，任务D是有限310个乘子支持点及代表约束时长，不宣称已经刻画所有允许时长的完整前沿。理论上允许时长的可行性与某个时长在有限乘子扫描中未匹配，属于不同判断。

`run_all.ps1 -Scope joint-extra` 只计算本轮新增联合内容，旧图按批准哈希继承，既有西安拟合/人口结果继承 `20261003_release_final` 并明确记录身份。默认 `-Scope all` 仍计算同轮上游；新版稿源要求上游数值与所继承科学版本一致，若改变不能静默保留旧正文。两个模式的证据边界不可混用。

活动稿源由 `manuscript_versions/current.json` 及版本目录的 `manifest.json` 锁定，内容来自本轮本地整合稿；原冻结包不改。`paper_sync` 仅在唯一的 `JOINT_EXTRA` 标识块生成新增出版文案，标签/图路径/表结构与批准清单一致，证明与版本源逐块比对。实际打印宽度记录在版本清单，不写死旧图宽度。文案回归、实际编译和科学双跑分别记录。

分阶段执行时，科学计算期的 `joint_extra/input_manifest.json` 先记录 `core.py/run.py/validation.py/acceptance.json` 及指定输入的 SHA-256。`postprocess_joint_extra.py` 首次承接同一运行后，才生成完整出版源码快照及 `postprocessing_manifest.json`；快照的 `snapshot_phase=after_completed_joint_extra` 不代表科学运行前已记录全工程哈希。后处理不改变科学文件，不读取别轮新结果，也不执行新的科学计算。公开 `run_all` 的空目录模式仍在计算前记录完整工作副本，两种时序需明确区分。

两个通过机器验收的实际运行由 `run_selection.py` 明确写入一次性的 `accepted_runs.json`。检查共同源码哈希、批准稿源、模型完整输入及验收配置均相同，再按实际所选目录完成重复性比较、发布与汇集；不假定最早的两个编号已经通过。选择记录本身不证明数值重复性或人工页面审阅通过，失败运行的编号、输出和诊断保留不动。
