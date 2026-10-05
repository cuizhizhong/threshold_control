# 全文来源与复现清单

覆盖：24 幅图、5 张正文表、3 张补充表。
另定位 92 组编号公式、28 个理论陈述、694 行含数字陈述。

结构清单通过不代表所有数字对账完成。静态/供应方/本机执行/本机复现分开记录；未实算锚点保持待核对。

| 项目 | 标签 | 部分 | 状态 | 本机数值/图件证据 |
|---|---|---|---|---|
| 图1 含接触追踪与隔离的 SIQR 型模型。$S,S_q,I,I_q,R$ 分别表示社区易感者、隔离易感者、非隔离感染者、隔离感染者和康 | `fig:model_schematic` | schematic | inherited | figures/Fig1.pdf |
| 图2 仅隔离阈值控制与常规控制的时间轨迹。参数为 $N=763$、$S_0=762$、$I_0=1$、$S_q(0)=I_q(0)=R( | `fig:scenario1:single-sim` | baseline | inherited | figures/optimal_control_with_quarantine_panels.pdf |
| 图3 不同常规接触率和感染阈值下的隔离率轨迹。固定 $N=763,S_0=762,I_0=1,\beta=0.155,\gamma=0. | `fig:baseline:q-joint` | baseline | inherited | figures/layout_v5/baseline_q_joint.pdf |
| 图4 $(\eta/N,c_0)$ 平面上的启动时间、控制持续时间、清零时间和累计感染。固定 $N=763,S_0=762,I_0=1, | `fig:scenario1_heatmaps_c0_eta` | baseline | inherited | figures/scenario1_heatmaps_c0_eta.pdf |
| 图5 拐点相对位置 $\lambda$ 随 $\eta/N,c_0,\beta,q_0$ 的变化。基准取 $N=763,S_0=762, | `fig:s1:lambda-sensitivity` | inflection | inherited | figures/layout_v5/scenario1_inflection_lambda_sensitivity.pdf |
| 图6 不同 $q_0,\beta,c_0,\eta/N$ 下的隔离率时间轨迹。其余参数同图\ref{fig:s1:lambda-sens | `fig:s1:inflection-scan` | inflection | inherited | figures/layout_v5/scenario1_inflection_scan_t.pdf |
| 图7 不同阈值比例下各指标随 $c_0$ 的变化。固定 $N=763,S_0=762,I_0=1,\beta=0.155,\gamma= | `fig:scenario1_summary_c0` | baseline | inherited | figures/layout_v5/c0_sensitivity_selected_eta.pdf |
| 图8 不同常规接触率下各指标随 $\eta/N$ 的变化。固定 $N=763,S_0=762,I_0=1,\beta=0.155,\ga | `fig:scenario1_summary_eta` | baseline | inherited | figures/layout_v5/eta_sensitivity_selected_c0.pdf |
| 图9 基准参数下相同启动与退出要求的四种分配（$N=763$，$\eta=0.05N$，$w_c=1,w_q=2$）。(a) 接触率；( | `fig:joint:compare` | joint_extra | inherited | figures/joint_v2/joint_compare_baseline.pdf |
| 图10 能力限制下的可行区域与代表轨迹。(a) 基准参数；(b) 西安参数。横轴为最大接触减少比例 $1-c_{\min}/c_0$，纵轴 | `fig:joint:capacity` | joint_extra | inherited | figures/joint_v2/joint_capacity.pdf |
| 图11 固定 $w_c=1$、改变 $r=w_q/w_c$ 时的类内最低二次成本分配。(a) 基准参数；(b) 西安参数。颜色为 $y=( | `fig:joint:phase` | joint_extra | inherited | figures/joint_v2/joint_phase_weights.pdf |
| 图12 基准参数下二次成本与控制持续时间的关系。红色曲线连接已核查的 $J+\kappa\Delta t$ 最小化解，实线与短虚线分别对应 | `fig:joint:frontier` | joint_extra | reproduced | figures/joint_v2/joint_frontier_baseline.pdf |
| 图13 西安疫情观测窗口内的日新增病例与 TDINN 重构。(a) 社区发现病例；(b) 隔离发现病例。点为观测值，实线取自三策略比较所用 | `fig:xian:observed-fit` | xian | inherited | figures/layout_v5/xian_observed_fit.pdf |
| 图14 $\eta=0.002N$ 时三策略的全过程比较。(a) 社区感染者人数 $I(t)$；(b) 接触率 $c(t)$；(c) 隔离 | `fig:xian:strategy-process` | xian | inherited | figures/layout_v5/xian_strategy_process.pdf |
| 图15 西安参数下控制指标随 $\eta/N$ 的变化。(a) 启动隔离率；(b) 加权成本；(c) 累计感染；(d) 控制持续时间与动态 | `fig:xian_eta_sens` | xian | inherited | figures/xian_eta_sensitivity.pdf |
| 图16 西安参数下 $(\eta,c_0)$ 平面上的控制指标。(a) 控制持续时间；(b) 动态清零时间；(c) 累计感染；(d) 加权 | `fig:xian_heatmaps` | xian | inherited | figures/xian_heatmaps.pdf |
| 图17 西安参数下 $(N_{\rm eff},\eta)$ 平面比较区域的近似展示。(a) 峰值条件及成本、时长和触发参考直线；后三者采 | `fig:dom` | population | inherited | figures/fig_dom_combined.pdf |
| 图18 阈值与有效人口对轨迹的不同影响。左列固定 $N_{\rm eff}=20000$，$\eta=22.7,33.1,75.2$ 分别 | `fig:dom:levers` | population | inherited | figures/layout_v5/population_threshold_levers.pdf |
| 图19 固定 $N_{\rm eff}=2\times10^4$、$\theta=0.002$，不同 $c_0$ 下的 (a) 感染人数和 | `fig:c0-panel` | c0 | inherited | figures/layout_v5/c0_sensitivity_panel.pdf |
| 图20 $(\theta,c_0)$ 平面上的触发边界、内部拐点边界 $s^*=2\bar s$ 和控制持续时间驻点曲线 $\partia | `fig:c0-phase` | c0 | inherited | figures/layout_v5/c0_phase_stationary.pdf |
| 图21 固定 $\eta=100$ 时不同有效人口下的感染轨迹。(a)--(d) 分别对应 $N_{\rm eff}=3973,10151 | `fig:panel_N_decomp` | population | inherited | figures/layout_v5/fig_panel_B_trajectory_decomposition.pdf |
| 图22 三类临界有效人口下的阈值比较。三行依次为 $N_{\rm eff}=11813,40553,92174$；左列为社区感染者人数（对 | `fig:dom:critical-cases` | population | inherited | figures/layout_v5/critical_population_cases.pdf |
| 图23 固定 $N_{\rm eff}=2\times10^4$、$\theta=0.002$ 时各指标随 $c_0$ 的变化。(a)-- | `fig:c0-scan` | c0 | inherited | figures/c0_sensitivity_scan.pdf |
| 图24 固定 $\theta=0.002$、$q_0=0.3230$ 时，$(c_0,\beta)$ 平面上的内部拐点存在范围。边界为 $ | `fig:c0-beta-existence` | c0 | inherited | figures/c0_beta_existence.pdf |
| 表1 仅隔离控制中主要量的参数敏感性 | `tab:sensitivity` | theory | static |  |
| 表2 相同阈值与启动、退出要求下四种分配的结果（$w_c=1,w_q=2$） | `tab:joint:compare` | joint_extra | reproduced | joint_extra/compare_baseline.csv, joint_extra/compare_xian.csv, joint_extra/validation.json, manuscript_changes.json |
| 表3 西安算例的参数与初始条件 | `tab:xian_initial_fit` | xian | inherited | xian/fit.json, xian/reference.json |
| 表4 西安参数下三种策略的感染结局与干预指标 | `tab:xian_summary` | xian | inherited | xian/summary.csv, xian/diagnostics.json |
| 表5 不同指标限制对应的有效人口界值 | `tab:dom:thresholds` | population | inherited | population/critical.json, population/arcs.csv |
| 表S1 基准参数下代表性控制结果 | `tab:sup:baseline` | baseline | inherited | workspace/scenario1_threshold_landscape/current_run/output_csv/landscape_summary.csv |
| 表S2 不同初值设定下的观测窗口比较 | `tab:sup:initial` | xian | inherited | xian/S2_difference.json, xian/fit.json |
| 表S3 西安参数下不同阈值的控制结果 | `tab:sup:eta` | xian | inherited | xian/eta_scan.csv |

## 已明确核对的联合数值

| 数字 | 本机结果 | 论文取整 | 状态 |
|---|---:|---:|---|

## 仍需逐项核对

每个图注、表格数值单元及含数字正文行都保留位置和来源；详细项目见 JSON。
供应方历史锚点不是本机证据；理论/证明不因数值一致性而标通过。
SI S2 固定 I0=1 的40天窗口只依据其对应配置的单元核对记录，不能被拟合基准结果替代。
