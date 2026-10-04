# 固定阈值比例下的 c0 数值实验

运行 `run_c0_sensitivity.py` 后，过程数据和图片写入 `outputs/`。该目录不纳入版本控制；
清理前的输出快照保存在 `../archive_unused/generated_snapshots/c0_sensitivity_outputs/`。

## 当前正式稿中的定位与口径

正式主稿为 `../latex/flatten_curve_analysis_cn.tex`。当前关联为第 9.6 节及附录：
图 15（`fig:c0-panel`）、图 16（`fig:c0-phase`）、附录图 19（`fig:c0-scan`）
和图 20（`fig:c0-beta-existence`），来源与入稿适配见 `../reproducibility/registry.json`。
正式复现由 `../reproducibility/c0.py` 使用统一积分设置重建结果，再由现用绘图层保留原样式；
全文入口为 `../reproducibility/run_all.ps1`，输出必须是新建空目录。

主实验固定 `N_eff=20000`、`theta=0.002`（`eta=40`），沿用全市人口下一次拟合的同一个
未取整绝对 `I0`，正文显示为 `1.00659e-3`，并取 `S0=N-I0`，不随 `c0` 重新拟合。
在 `N_eff=20000` 下重拟合仅作为敏感性诊断，不替换主实验初值。原模块 `main()` 已采用固定
全市初值的约定，但其历史常量和旧文案不等于当前正式复现输入；当前输入来自本轮输出
`xian/reference.json`，诊断和完整精度结果见 `c0/parameters.json`、`c0/diagnostics.json`。

本轮只整理文档，未执行这些脚本、未改算法或正式图件，也未生成新的数值验收。
下文旧拟合记录、表格和误差保留为历史对照，不能当作当前稿逐项复跑结果。

## 历史实验与初值诊断记录

- 固定参数：`N_eff=20000`、`beta=0.1498`、`gamma=0.2953`、`q0=0.323`。
- 固定阈值比例：`theta=eta/N=0.002`，所以共同平台为 `eta=40.00` 人。
- 早期记录在 `N_eff=20000` 下按当时的四序列最小二乘口径拟合一次初值，得到
  `I0=0.00100662823352`；所有 c0 情景共同使用该初值，不随 c0 重新拟合。当前主实验已采用
  上文的全市绝对初值约定，该旧记录不再定义当前输入。
- 作为当时的拟合对照，同一程序在全市人口下得到 `I0=0.00100659186644`、
  目标函数 `1036.761462098`，附件记录值分别为
  `0.00100662823352`、`1036.76140515`。
- 不画 TDINN，也不画公共常规控制轨迹；图中只比较阈值控制自身。

## 三个结构位置（历史数值锚点）

- 阈值首次可达边界：`c0_trigger=3.33372463`。低于该值时无需启动阈值控制。
- 内部拐点出现边界：`c0_inf=3.54308966`。在触发边界与此边界之间，
  q_c(t) 可构造但全程凸，不存在内部拐点。
- 控制时长极大点：`c0_duration_max=6.60699438`，
  `Delta_t_max=103.18101642` 天。

隔离率拐点高度在所有存在内部拐点的情景中均为
`q_inf=0.411903081628`，与 c0 无关。

## 五个代表情景（历史指标记录）

| c0 | t1 (d) | Delta t (d) | t2 (d) | q_max | t_inf / lambda | clear time (d) | total cumulative |
|---:|---:|---:|---:|---:|:---:|---:|---:|
| 3.4337 | 209.99 | 30.22 | 240.21 | 0.3834 | 无（全程凸） | 366.52 | 1831.71 |
| 3.5931 | 157.38 | 47.53 | 204.91 | 0.4227 | 162.52 / 0.108 | 328.49 | 2020.73 |
| 6.607 | 28.33 | 103.18 | 131.51 | 0.6971 | 108.46 / 0.777 | 223.82 | 3333.91 |
| 9 | 17.18 | 98.00 | 115.19 | 0.7782 | 98.26 / 0.827 | 194.92 | 3536.62 |
| 12.887 | 10.48 | 85.07 | 95.55 | 0.8454 | 83.73 / 0.861 | 162.95 | 3608.57 |

## 历史算例的读图说明

1. c0 增大时，阈值平台高度始终等于 eta，变化的是到达平台的速度、平台长度和所需隔离强度。
2. t1 严格提前，q_max 严格增大；c0=3.43、3.59
   分居拐点出现边界两侧，展示触发边界到控制时长极大点之间的近临界过渡。
3. Delta t 不是全域单调量：从触发边界的 0 上升，历史扫描在 c0≈6.61 得到约 103.18 天的数值极大值，
   随后在所考察范围内下降；基准情景展示这一回落阶段。不据该扫描宣称一般参数下极大值唯一。
4. c0=3.43 虽能触发阈值控制，但 q_max<q_inf，因此 q_c(t) 全程凸、无内部拐点。
   c0=3.59、6.61、9.00、12.89 均超过约 3.5431，存在唯一内部拐点。
5. 内部拐点存在时，q_inf 不变，但 lambda 随 c0 增大而增大：
   拐点在归一化平台时间中向 t2 端移动；绝对 t_inf 则因整条轨迹提前而提前。
6. I(t) 平台上的实心圆只是 q_c(t) 拐点时刻的投影，不是 I(t) 自身的拐点。
7. 总累计感染按各情景自身的清零时刻 I(t)=1 截止，定义为
   I_tcum=I_cum+Iq_cum；累计仓室从 0 开始，不重复计入共同的初始感染 I0。

## 历史数值校验（本轮未复跑）

- 五个开环平台的最大绝对平台误差（换算为人数）为 `0.000e+00`。
- 表内实际有四条曲线存在内部拐点，旧文案的“三条”计数不正确；原生成器中的对应文字
  尚未在本轮修改。旧记录采用均匀时间网格二阶差分定位，报告最大时刻误差
  `3.973e-03` 天、最大高度误差 `3.011e-05`，此处保留数值而不新增误差认证。

原脚本确实对理论时间开环控制另作 ODE 积分以检查平台误差，不是仅从解析平台常数读出零误差；
但上述旧记录不自动认证当前所有输出。正式验收应读取已有 `c0/diagnostics.json` 中的
`trajectory_checks` 和基准加严容差记录，并注明后者检查的具体情景，不推广为全扫描收敛证明。

## 文件

下列图、CSV 和 JSON 生成文件均位于 `outputs/`；源码 `run_c0_sensitivity.py`
和输入 `inputs/xian_observed_data_processed.csv` 仍位于模块根目录：

- `c0_sensitivity_main.png/.pdf`：I(t) 与 q(t) 的两面板主图。
- `c0_sensitivity_main_linear.png/.pdf`：仅将主图 I(t) 纵轴改为线性坐标的对照版。
- `c0_sensitivity_main_linear_cumulative.png/.pdf`：线性主图；用清零时总累计感染柱状图替代相对时间 inset。

## 当前正式图的原图来源与适配

主图有三个变体，**当前正文图 15（旧稿图 23）的原图来源是 `main_linear_cumulative`**（线性纵轴 + 总累计感染柱图 inset），
不是 `main`（对数纵轴 + 相对时间 inset）。三者版式相近，容易复制错。

| 原模块输出 | 正式图件名称（位于 `../latex/figures/`） | 当前主稿 |
|---|---|---|
| `outputs/c0_sensitivity_main_linear_cumulative.pdf` | `layout_v5/c0_sensitivity_panel.pdf` | 图 15（`fig:c0-panel`） |
| `outputs/c0_sensitivity_phase.pdf` | `layout_v5/c0_phase_stationary.pdf` | 图 16（`fig:c0-phase`） |
| `outputs/c0_sensitivity_scan.pdf` | `c0_sensitivity_scan.pdf` | 附录图 19（`fig:c0-scan`） |
| `outputs/c0_beta_existence.pdf` | `c0_beta_existence.pdf` | 附录图 20（`fig:c0-beta-existence`） |

表格列出来源关系，不是建议把旧输出直接复制入稿。旧根 `../figures/` 已不存在，
当前正式绘图层会绑定新数据并沿用已认可的样式与布局；仅复制原模块图不能保证实现该适配。
原脚本还会生成 `outputs/README.md`，其中仍可能含旧初值说明和图号；它不覆盖本文件，
也不能当作正式稿的最新导航。生成器文案同步留为后续维护事项，本轮不改科学计算代码。

`c0_sensitivity_main.pdf` 与 `c0_sensitivity_main_linear.pdf` 仅作对照，不进论文。
- `c0_sensitivity_scan.png/.pdf`：c0 连续扫描的八指标图，上排 t1、Δt、tail、t_end
  （三者相加即 t_end），下排 q_max、λ、J、I_tcum。
- `c0_sensitivity_phase.png/.pdf`：(θ,c0) 结构相图（三条结构边界叠 Δt 等值线）。
- `c0_beta_existence.png/.pdf`：(c0,β) 平面内部拐点存在域（β 为病原情景变量，θ、q0 固定）。
- `c0_representative_summary.csv`：五个代表情景的指标表。
- `c0_representative_timeseries.csv`：五条轨迹的逐时点数据。
- `c0_continuous_scan.csv`：连续 c0 扫描数据。
- `experiment_parameters.json`：参数、边界与一次性初值标定结果。
- `run_c0_sensitivity.py`：可复现实验脚本。
- `inputs/xian_observed_data_processed.csv`：脚本的一次性初值标定输入。
