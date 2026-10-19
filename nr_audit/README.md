# nr_audit：无回流模型的核验模块（NR-2）

## NEW中文审阅版的复现入口

以下命令在仓库根目录运行。建议使用隔离环境；精简依赖在requirements.txt，实际验证版本在requirements-validated.txt。

~~~powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r nr_audit/requirements.txt
python -m pytest nr_audit/tests -q -m "not slow"
python -m pytest nr_audit/tests -q
python nr_audit/import_return_numbers.py
python nr_audit/make_numbers.py
powershell -NoProfile -ExecutionPolicy Bypass -File paper/build.ps1
~~~

实际运行时使用同一环境的python。完整测试含无回流闭式/状态积分/完整方程比较，轻量命令跳过slow项；二者都不是重新求解36条回流矩阵。回流数字默认读取固定本地JSON，可显式指定 `--source-json`，SHA-256必须一致；无Git历史只跳过额外历史blob核对。缺文件、字节变化、缺行明确失败。`new_no_git_snapshot.json`记录了真实无Git发现环境中的导入和宏生成。

`r7_return/` 仅作为已归档来源，结果JSON不修改、不解析重写；核心JSON和冻结xian_loader由精确gitattributes保护字节。LF/CRLF配置测试是同一Windows主机上的检出模拟，不是Linux实测。论文的历史来源核对、数值复现、终点适用性和最终PDF视觉验收分别记录。

完整图表来源清单为results/figure_table_sources.csv。旧绘图历史代码如不在当前目录，清单指向历史Git对象；这不等同于可分发快照中已有独立入口。本轮只针对已知图7错误做局部重绘。

本目录是无回流主稿分支 `paper/no-return-focus` 的计算核验模块（NR 计划第 5.2 节）。NR-2 只建立代码与测试；正式回归表、固定人口初值诊断、权重转折加密、收敛表与拟合误差重建由 NR-3 用本模块完成（`NR_3_numbers.md`）。`theory_checks.py` 是 NR-1 的代数核对（G-N1 已确认），与本模块的数值路径无关。

**范围**：只实现稿件式 (2.1) 的无回流 SIQR 模型（隔离易感者不返回 $S$），阈值策略 $\mathcal A(\eta)$ 及其能力约束子类。不实现回流（$\omega>0$）与立即返回对照模型，不实现退出时的释放（释放注记只有公式，不模拟）。

## 1 运行入口与环境

环境：conda 环境 `thesis`（Windows 11）；实际测试所用版本为 Python 3.10.20、numpy 2.2.5、scipy 1.15.3、sympy 1.14.0、mpmath 1.3.0、pytest 9.1.1（每次运行的版本写入测试报告）。在仓库根目录运行；`conda run` 在 GBK 控制台转发中文输出会报编码错误，所以加 `--no-capture-output`。

```bash
conda run --no-capture-output -n thesis python nr_audit/run_tests.py --level smoke
```

```bash
conda run --no-capture-output -n thesis python nr_audit/run_tests.py
```

```bash
conda run --no-capture-output -n thesis python -m pytest nr_audit/tests -q -m "not slow"
```

```bash
conda run --no-capture-output -n thesis python nr_audit/sources.py
```

| 入口 | 内容 | 输出 | 时间（本机） |
|---|---|---|---|
| `run_tests.py --level smoke` | 小型入口：基准参数下的全部类别（来源、模型、根法与多项式、闭式、状态路径、开环完整方程、能力约束），不含 N_x 网格扫描、西安与乘子曲线 | `results/nr2_test_report_smoke.{json,md}` | 约 20–45 s |
| `run_tests.py --level quick` | 跳过标为 `slow` 的项 | `results/nr2_test_report_quick.{json,md}` | 约 1–2 min |
| `run_tests.py` | 全部 235 项 | `results/nr2_test_report.{json,md}` | 约 1–2.5 min |
| `pytest nr_audit/tests …` | 同上，只在终端显示 | — | — |
| `sources.py` | 重新生成来源清单（来源文件或参数改变时） | `results/source_manifest.json` | 1 s |

报告逐项记录结果、耗时和测试中记录的实测量（如最大相对差、平台偏差、残差），并记录运行时 `HEAD`、`nr_audit` 是否有未提交改动与被测源码的 SHA-256。通过与否以报告为准，README 不预填结果。

## 2 文件

| 文件 | 内容 |
|---|---|
| `params.py` | 两组参数与初值（未取整；西安 $I_0=0.00100659188867187$，$S_0=N-I_0$），能力约束 `Capacity` 与两个代表点（图 6：基准 $c_{\min}/c_0=0.5$、$q_{\rm cap}=0.6$；西安 $0.5$、$0.75$） |
| `model.py` | 式 (2.1) 的右端、四类流量、阈值弧上的控制 $c=c_0x$、$q=1-(1-q_0)/(xz)$、归一化强度与二次干预强度成本的被积函数 |
| `allocation.py` | 允许区间（式 4.6–4.8）、显式控制律、驻点多项式、逐状态最小化（根法）、$N_x$ 网格核对、结构变化点与陡峭点的扫描 |
| `state_integrals.py` | 第一条路径：启动状态（Lambert $W$）、$t_1$、阈值弧的 S 坐标求积、退出后（$S_{\rm end}$、$S_\infty$、清零时间）、全过程指标、单控制闭式；`Policy`（控制律及其分段点） |
| `simulate.py` | 第二条路径：完整五仓室方程与累计流量的独立积分，开环时间控制，事件与终点，诊断 |
| `sources.py` | 来源清单的生成（来源文件、字段、SHA-256、复用代码的 blob） |
| `run_tests.py` | 运行测试并写报告 |
| `tests/` | `test_sources.py`（数字来源）、`test_model.py`、`test_allocation.py`、`test_state_integrals.py`、`test_simulate.py`；`conftest.py` 集中容差 `TOL` 与缓存 |
| `results/` | `source_manifest.json`、`nr2_test_report*.{json,md}`；NR-1 的 `theory_checks.{json,md}` |

## 3 模型、控制与终点

- **模型**：式 (2.1)，$0<\beta<1$，$0\le q_0<1$；隔离者不参与传播，隔离易感者不返回 $S$。两组算例 $S_q(0)=I_q(0)=R(0)=0$。
- **阈值策略**（定义 2.1）：常规轨迹首次由下方到达 $I=\eta$（$t_1$）时启动；阈值弧上 $I=\eta$、$c\le c_0$、$q\ge q_0$，平衡式 (2.8) 成立；$S$ 首次降到常规传播临界值 $S_c$（$t_2$）时恢复 $(c_0,q_0)$，此后一直保持，不释放隔离易感者。
- **控制律**（`Policy` 的 `name`）：`q_only` 仅隔离控制（$x\equiv1$）；`c_only` 仅减少接触（$x=1/z$）；`alpha` 显式族 $x=\alpha+(1-\alpha)/z$（默认 $\alpha=0.5$）；`opt` 成本最优控制（逐状态最小化 $J+\kappa\Delta t$ 的被积函数，$\kappa=0$ 即定理 5.1；权重 `wc`、`wq` 可设）；`cap_upper`、`cap_lower` 能力约束下最快、最慢的控制 $c^{\pm}$（推论 4.6）。`cap` 给出能力约束；式 (4.7) 不成立时抛出 `allocation.Infeasible`。
- **终点**（第 2.4 节）：$\Delta t=t_2-t_1$；清零时间 $t_{\rm end}$ 是退出后 $I$ 由上方降到 1 的时刻（事件只在退出后、方向向下检测；基准 $I_0=1$ 的初始状态不算）；“计至清零”的累计新增感染统计到各控制自身的 $t_{\rm end}$；“$t\to\infty$”由 $t_{\rm end}$ 处的 $(S,I)$ 按定理 3.5 的首次积分解析补尾，与计至清零的值不同，二者分别输出。累计新增感染不含初始感染者；新增隔离易感者人数、$J$、$J_c$、$J_q$ 只计阈值控制期。$J$ 为式 (2.13) 的二次加权积分（天），$J_c$、$J_q$ 为式 (2.12) 的分项线性强度积分，$J\ne J_c+2J_q$。
- **两显式感染仓室之和的峰值** $\max(I+I_q)/\eta$：在 $[0,t_{\rm end}]$ 上对完整方程的稠密解取样并在导数变号处加密，是模型输出，不是 ICU 占用。

## 4 归一化

| 用途 | 变量 | 写法 |
|---|---|---|
| 完整方程 | $s=S/N$、$i=I/N$、$s_q$、$i_q$、$r$，$\theta=\eta/N$ | `simulate.py` 的状态；`params` 中后缀 `_N` |
| 控制律与 S 坐标求积 | $z=S/S_c$、$x=c/c_0$、$\bar z=\bar S/S_c=(1-\beta)(1-q_0)$ | `allocation.py`、`state_integrals.py`；以 `z` 开头 |

二者只在一处换算：$z=s/s_c$。人数以人计，时间以天计。

## 5 两条计算路径

**第一条（闭式与对 $S$ 的一维积分）**：$S^*$ 由 Lambert $W$ 的 $k=-1$ 分支给出、brentq 交叉核对；$t_1$ 为式 (3.2) 的 quad（换元 $S_0-S=\text{scale}\cdot(e^w-1)$，消去 $I_0$ 很小时的对数型近奇性）；阈值弧上 $\Delta t$、$J$、$J_c$、$J_q$、控制期感染与新增隔离易感者的流量都化为对 $z$ 的积分（式 4.5、5.1），主结果为分段复合 Simpson（初始 $N_z=4001$ 点，分段点为结构变化点、陡峭点与能力折点；间断点与陡峭点两侧用 $z=\text{端点}\pm Lu^3$ 的分级网格；每片以隔点 Simpson 的 Richardson 估计 $|S_n-S_{n/2}|/15$ 控制误差，时长或成本分量超过 $10^{-12}$ 相对时对半细分，至多 10 层，细分次数与误差估计随结果输出），另用分段 quad（epsrel $10^{-12}$）交叉核对；退出后 $S_{\rm end}$、$S_\infty$ 由 Lambert $W$ 的 $k=0$ 分支给出、brentq 交叉核对，清零时间为式 (3.15) 的 quad；全过程累计为定理 3.6 的三段写法。单控制与显式族另有闭式（`closed_forms`）。

**第二条（完整方程，开环）**：`simulate.run` 积分完整五仓室方程，另把 $\int\beta c(1-q)si\,dt$（进入 $I$）、$\int\beta cq\,si\,dt$（进入 $I_q$）、$\int i\,dt$、$J$、$J_c$、$J_q$ 作为独立状态积分；累计新增感染不由 $S_0+S_q(0)-S-S_q$ 定义，二者之差作为恒等式残差报告。阈值弧上的控制是按名义模型预先生成的时间函数：名义时钟 $dz/d\tau=-(c_0\eta/N)(x(z)z-\bar z)$ 从 $z^*$ 出发、按分段点逐段求解（显式律用闭式，成本最优控制用 DOP853 稠密解），控制 $c(t)=c_0x(z_{\rm nom}(t-t_1))$、$q(t)=1-(1-q_0)/(xz_{\rm nom})$ 只依赖时间。完整方程中 $I$ 自由演化，不重置到 $\eta$，不按实时状态纠偏；$t_1$ 取完整方程触发事件的时刻，名义退出时刻 $t_2=t_1+\sum$段时长，此后恢复常规。`run(…, c_scale)` 只用于检验开环性（扰动接触率后 $I$ 必须离开 $\eta$）。

## 6 逐状态最优选择

定理 5.1 把成本最优控制化为每个状态上的有限比较。`allocation.argmin_state` 在允许区间 $[x_{\rm lo},x_{\rm hi}]$ 上比较两个端点与五次驻点多项式的全部近似实根：

- 驻点多项式（$x$ 坐标）：$[w_c,\,-2bw_c,\,w_c(2b-1)-w_q-\kappa,\,4rw_q,\,-r(3r+2b)w_q,\,2br^2w_q]$，$r=1/z$、$b=\bar z/z$；$\kappa=0$ 时与稿件式 (5.4) 只差正因子 $c_0^3$（`test_allocation.py` 用 SymPy 核对）。$\zeta=1-1/z<10^{-4}$ 时改用缩放坐标 $x=1-\zeta y$ 的五次式，避免 $1-x$ 的相消。
- 候选：`numpy.roots` 中虚部 $\le10^{-4}\max(1,|\text{根}|)$ 的根取实部，落在区间外不超过 $10^{-10}$·区间宽度的截到端点，再做至多 8 步牛顿修正（只在不离开区间时采用）；候选都可行，多收只会增加候选。严格实根（虚部 $\le10^{-10}$）另计个数；区间内两根相距小于 $10^{-6}$·区间宽度记为近重根；相距小于 $10^{-12}$·区间宽度的候选合并（保留端点）。
- 选择：目标值严格最小者；完全相等时取 $x$ 较大者（更接近仅隔离；缩放坐标下对应取 $y$ 较小者）。近并列（值在最小值加 $10^{-10}\max(|\min|,\text{极差})$ 以内）只计个数作诊断，不平滑选择。
- 网格只作交叉核对：`grid_check` 在 $N_x$ 个等距点上取值，并在每个网格局部极小的相邻两格内用有界一维搜索加密，网格值低于根法值即判为根法漏解。
- 结构扫描（`scan_structure`，$N_z$ 网格）：类型（端点 'hi'/'lo'、内部 'int'）改变的括区，连续的用“驻点多项式在端点的值”的 brentq（xtol $10^{-15}$）定位，否则二分到 $|\Delta z|\le10^{-14}z$；类型相同但二阶差分远大于邻域（$10^3$ 倍邻域中位数 $+10^{-10}$）或 $|\Delta x|>10^{-3}$ 且超过邻域中位数 5 倍的括区，二分后两侧 $x$ 差 $>10^{-6}$ 记为间断，否则记为陡峭点（十等分收敛到斜率最大处），只作求积分段点；退出附近第一个格子内另用对数网格查类型改变（如 $\kappa>0$ 时 $\zeta=O(\kappa)$ 处的切换）。结构变化点与陡峭点都只是数值定位，“全局”只指所检验的状态与网格。

## 7 容差

| 位置 | 设置 |
|---|---|
| `allocation.py` | IMAG_TOL_CANDIDATE $10^{-4}$，IMAG_TOL_STRICT $10^{-10}$，EDGE_TOL $10^{-10}$，DUP_TOL $10^{-12}$，DOUBLE_ROOT_GAP $10^{-6}$（均相对区间宽度或根的模），NEAR_TIE_REL $10^{-10}$，DEG_TOL $10^{-14}$，FEAS_TOL $10^{-12}$，ZETA_SCALED $10^{-4}$，牛顿步数 8；JUMP_CLASSIFY_TOL $10^{-6}$，ANOMALY_FACTOR $10^3$，ANOMALY_FLOOR $10^{-10}$ |
| `state_integrals.py` | 初始 $N_z=4001$（每片至少 101 点、$4m+1$ 个）；自适应细分 ADAPT_TOL $10^{-12}$、至多 10 层；quad epsrel $10^{-12}$（$t_1$、清零时间 $10^{-13}$）；段内收缩 $10^{-12}\cdot z_{\rm hi}$ 后投影回允许区间 |
| `simulate.py` | DOP853，rtol $10^{-12}$，max_step 0.5 d；atol（按 $N$ 归一）：$s$ $10^{-15}$，$\ln i$ $10^{-12}$（即 $I$ 的相对误差），$s_q,i_q,r$ 与三个流量积分 $10^{-13}\min(i_0,1/N)$（西安约 $7.7\times10^{-24}$，远小于 $i_0\approx7.65\times10^{-11}$；基准约 $1.7\times10^{-16}$），$J,J_c,J_q$ $10^{-13}$ d；`Config.atol_scale` 整体缩放。名义时钟 DOP853 rtol $10^{-13}$、atol $10^{-15}$。事件时刻由 `solve_ivp` 在连续解上用 brentq 定位，求根容差由 scipy 内部设定，没有单独的事件容差参数；收敛检查须同时收紧 rtol、atol 与 max_step（NR-3）。诊断取样：每个积分步 8 等分 |
| 测试判据（`conftest.TOL`） | 与旧全精度结果回归 $10^{-4}$（相对，NR 计划的验收目标）；闭式与 Simpson $10^{-9}$；Simpson 与 quad $10^{-10}$；开环完整方程与状态路径 $10^{-8}$；累计量恒等式残差/初始易感者 $10^{-8}$；质量残差/$N$ $10^{-12}$；仓室下限 $-10^{-8}$ 人；平台 $\max|I-\eta|/\eta\le10^{-8}$ 且 $>0$；控制界限越界 $10^{-12}$；平衡式 $10^{-12}$；触发、退出事件相对残差与 $t_1$ 对照 $10^{-9}$；$|I(t_{\rm end})-1|\le10^{-8}$ 人；网格低于根法 $10^{-12}$（相对）；Lambert $W$ 与 brentq $10^{-12}$。另有各测试内写明的专项判据（如 $N_z$ 收敛 $10^{-8}$、乘子曲线回归 $10^{-6}$、切换位置 $10^{-8}$） |

这些是本次复核的判据，不是对数值真值的证明。

## 8 输入、输出与副作用

- **输入**：只有 `params.py` 中的参数与初值。参照数据（`reproducibility/results/20261005_sec7_v2_refinement/joint_extra/` 的 `compare_*.csv`、`capacity.json`、`phase.json`、`frontier_baseline.csv`、`input_manifest.json`，`reproducibility/results/20261003_release_final/xian/` 的 `reference.json`、`fit.json`，基准参数 JSON）只由测试与 `sources.py` 读取，用于来源核对与回归，不作为计算输入。
- **输出**：只写 `nr_audit/results/`。不写入 `reproducibility/`、`r7_return/`、`joint_control/`、`paper/` 与其他目录；pytest 缓存已关闭（`-p no:cacheprovider`），`__pycache__/` 由 `.gitignore` 忽略。
- **来源清单**：`results/source_manifest.json` 记录每个参数的来源文件、字段、来源值与单位，只读目录中来源文件的 SHA-256（`pinned`；稿件文件会在后续步骤修改，只记录生成时的值），能力代表点，以及复用代码的来源 blob。

## 9 复用与来源

复制并改写自回流分支 `research/return-effects` 的提交 `bb52b96`（R7-3，G2 通过）的 `r7_return/`；这几个文件与本分支中的 `91123ea` 版本逐字节相同（`simulate.py` 的 $\omega=0$ 部分相同），原文件未改动、未运行：

| 本目录 | 来源 | blob | 改动 |
|---|---|---|---|
| `params.py` | `r7_return/params.py` | `b5467aae` | 删去回流专用量；增加常规轨迹派生量与能力代表点；数值未改 |
| `model.py` | `r7_return/model.py` | `810bf85c` | 只保留 $\omega=0$；成本被积函数改为 $(\cdot)_+$ 形式；增加线性强度 |
| `allocation.py` | `r7_return/alloc.py` | `034e6207` | 只保留无回流；扩展为一般权重、$\kappa$、能力约束、缩放坐标、牛顿修正与重根诊断、网格加密核对、异常括区与退出附近对数网格 |
| `state_integrals.py` | `r7_return/endpoints.py` | `345eb9f1` | 只保留无回流部分；增加 $J_c$、$J_q$、$t_1$、退出后、闭式、分级网格与 `Policy` |
| `simulate.py` | `r7_return/simulate.py` | `c088330c` | 只复用 $\omega=0$ 的 `analytic_tail`；r7 的事件法在阈值弧上用代数令 $I\equiv\eta$ 并按状态反馈求控制，不满足开环、不重置 $I$ 的要求，未复用 |

参照但未复制、未运行：`reproducibility/joint_extra/core.py`（缩放坐标的驻点多项式、$t_1$ 的换元、名义时钟分段的思路）。

## 10 已知事项

- 开发中发现：乘子曲线（注记 5.5）在 $\kappa\approx-0.24$ 附近，成本最优控制律 $x(z)$ 在 $z\approx2.82$ 处有只跨几个网格格子的陡峭区（接近跳变消失的临界 $\kappa$）。不分段、不细分时 $N_z=4001$ 的 Simpson 只准到约 $10^{-6}$。为此结构扫描增加了陡峭点，Simpson 增加了逐片误差控制；此后在所抽检的乘子点上 Simpson 与 quad 互差 $\le4\times10^{-13}$（开发中的检查）。`test_frontier_regression` 所抽检的 15 个乘子点与原 `frontier_baseline.csv` 的最大相对差见测试报告（集中在 $\kappa\approx-0.244$ 附近，原结果在该处的分段与插值方式不同）；NR-3 决定是否需要逐点复核。
- 网格扫描只能定位网格分辨得出的结构；宽度远小于网格且 $x$ 变化很小的特征可能漏检，其对积分的影响由 $N_z$ 收敛与 quad 互核反映。
- 西安归一化初始感染极小（$i_0\approx7.65\times10^{-11}$），完整方程用 $\ln i$ 作状态，并把小量分量的 atol 设得远小于 $i_0$。

## 11 NR-3 的审计脚本

在仓库根目录依次运行（每条前加 `conda run --no-capture-output -n thesis`）：

| 脚本 | 任务 | 输出（`results/`） | 时间（本机） |
|---|---|---|---|
| `python nr_audit/audit_baseline.py` | N1：表 2 两条路径与旧值、能力代表点、稿件保留数字的复算与显示核对（第 6、7 章，补充 S1、S2、S3、S5、S6），文中定性陈述的数值核对，旧实现数值与本模块对应值 | `regression.{json,md}` | 约 20 s |
| `python nr_audit/audit_initial_condition.py` | N2：西安固定人口，$I_0$ 为拟合值的 0.1/1/10 倍，仅隔离与成本最优控制 | `initial_condition.{json,md}` | 约 10 s |
| `python nr_audit/audit_weights.py` | N3：表 S5 的结构转折复核与加密（不假定单调） | `weight_brackets.{json,md}` | 约 10–20 min |
| `python nr_audit/audit_convergence.py` | N4：控制网格、状态网格、积分容差三档 | `convergence.{json,md}` | 约 5 min |
| `python nr_audit/audit_fit.py` | N5：在给定 $I_0$ 下按原定义重算四项拟合误差与补充表 S2 | `fit_reconstruction.{json,md}` | 约 3 s |
| `python nr_audit/audit_population_scale.py` | NR-6：人口缩放情景（原补充 S4“规模的作用”，移入补充 S3.1）的数字复核：θ=0.002 的六个人口、η=100 的两个人口与对数因子，并与原 `fixed_absolute_scale.csv`（只读）对照 | `population_scale.{json,md}` | 约 10 s |
| `python nr_audit/audit_noreturn_inf.py` | NR-7：无回流 t→∞ 累计感染 $C_\pi(0)$（四种控制、两组参数）与 $L=U(0)-S_c$ 的独立复核，对照回流分支 bb52b96 记录值（手抄，只读来源），并核对条件性推论的前提 $C_\pi(0)<L$ | `noreturn_inf_crosscheck.{json,md}` | 约 5 s |
| `python nr_audit/import_return_numbers.py` | NR-7：自回流分支固定提交 bb52b96 导入指数回流的 18 条轨迹（$1/\omega=7,14,30$ d）的终止时累计感染等，记录来源 blob 与 SHA-256，不重算，不导入其宏文件 | `return_import.json` | 1 s |
| `python nr_audit/make_numbers.py` | 新增数字的宏（NR-3 的 31 个；NR-5 追加 12 个：权重括区的两位小数取整值 `...Apx` 共 6 个、收敛检查的上界 5 个、TDINN 收紧容差的变化 1 个，上界一律向上取整） | `paper/generated/nr_numbers.tex`、`nr_numbers_map.json` | 1 s |

`tdinn.py` 实现 TDINN 控制与常规控制下的完整方程（时间开环，控制函数为稿件式 (7.1)），供 N1 的第 7 章数字与 N5 使用；`audit_common.py` 是写出、读表与显示核对的公共部分。N6（无回流 $t\to\infty$ 汇总）本步未做。
