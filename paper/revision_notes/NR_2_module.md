# NR-2 无回流核验模块与测试（2026-10-15）

- 依据：NR 计划第 3、5.2 节；`AGENTS.md` 覆盖条款 N5、N8、N10、N11；`NR_0_scope.md` 第 5、6 节（复用登记）；`NR_1_theory.md`（G-N1 已确认，第 8 节裁决：命题 5.4 推广到一般正权重）；稿件第 2–6 章、附录 B、补充 S6；`reproducibility/manuscript_audit_notes.md`。
- 交付：`nr_audit/` 中的 `params.py`、`model.py`、`allocation.py`、`state_integrals.py`、`simulate.py`、`sources.py`、`run_tests.py`、`pytest.ini`、`tests/`（5 个测试文件）、`README.md`，`results/source_manifest.json` 与测试报告 `results/nr2_test_report{,_smoke}.{json,md}`。
- 未改 tex 与图表，未编译；`check_tex.py`、`statement_diff.py`、`rewrite_metrics.py` 不适用。未实现 $\omega>0$ 与立即返回对照模型。未运行 `r7_return/`、`reproducibility/` 中的任何脚本，未写入这些目录。NR-3 的正式数值（N1–N6）不在本步。

## 1 原代码的只读检查（路径与副作用）

| 代码 | 实际读取 | 写入（副作用） | 本步处理 |
|---|---|---|---|
| `r7_return/check_references.py`、`theory_checks.py`、`r7_3_numerics.py`（回流分支） | `reproducibility/.../joint_extra/compare_*.csv` 等 | `r7_return/results/`（及 `paper/generated/r7_numbers.tex` 的生成器 `make_numbers.py`） | 不运行；只复制需要的函数 |
| `r7_return/tests/` | 经 `conftest.py` 导入 `r7_return/` | 无（`-p no:cacheprovider`），但会在 `r7_return/` 生成 `__pycache__` | 不运行 |
| `r7_return/simulate.py` 的事件法 | — | — | 阈值弧上用代数令 $I\equiv\eta$、控制按状态反馈 $c=c_0x(S/S_c)$；不满足“开环、不重置 $I$”，未复用（NR-0 第 6 节第 7 行） |
| `reproducibility/joint_extra/run.py`、`core.py` | `joint_control/.../baseline_parameters.json`、`xian/reference.json` | `--out` 指定的新目录（须为空目录）；`verify` 另写时间戳记录 | 不运行；`core.py` 只参照写法（缩放坐标、$t_1$ 换元、名义时钟分段） |
| `reproducibility/xian.py` | 原始数据与拟合 | `results/` 下的运行目录 | 本步不需要（拟合重建在 NR-3） |

## 2 复用登记（按具体提交）

回流分支 `research/return-effects` 的提交 `bb52b96`（R7-3，G2 通过）。下列 blob 与本分支 `91123ea` 中的同名文件逐字节相同（`simulate.py` 的 $\omega=0$ 部分相同）；`tests/test_sources.py::test_code_reuse_blobs` 用 `git rev-parse` 逐个核对。

| `nr_audit/` | 来源 | blob | 复用方式 |
|---|---|---|---|
| `params.py` | `r7_return/params.py` | `b5467aae` | 数值不变；删去回流专用量，增加常规轨迹派生量与能力代表点 |
| `model.py` | `r7_return/model.py` | `810bf85c` | 只留 $\omega=0$；成本被积函数改为式 (2.13) 的 $(\cdot)_+$ |
| `allocation.py` | `r7_return/alloc.py` | `034e6207` | 根法与结构扫描的框架；扩展见第 3 节 |
| `state_integrals.py` | `r7_return/endpoints.py` | `345eb9f1` | 启动状态与分段求积的框架；扩展见第 3 节 |
| `simulate.py` | `r7_return/simulate.py` | `c088330c` | 只复用 $\omega=0$ 的 `analytic_tail`；开环完整方程为新写 |

模型开关：只有无回流模型 (2.1)；参数与初值见 `source_manifest.json`（与 `bb52b96` 的 `params.py` 数值相同）；控制律与终点见 `nr_audit/README.md` 第 3 节。

## 3 实现要点

- **参数与来源**：两组参数逐位取自来源字段（基准：`baseline_parameters.json`；西安：`reference.json` 的 `parameters` 与未取整 `I0_abs` = 0.00100659188867187，$S_0=N-I_0$ 与 `fit.json` 逐位相等）；能力代表点取自 `capacity.json` 的 `point` 字段与图 6 图注。来源文件的 SHA-256、字段、单位与归一化写入 `source_manifest.json`。
- **两条路径**：(1) 闭式与对 $S$ 的一维积分（Lambert $W$＋brentq；分段 Simpson＋quad 互核；Simpson 逐片以 Richardson 估计控制误差）；(2) 完整五仓室方程，三个流量积分（进入 $I$、进入 $I_q$、$\int I$）与 $J$、$J_c$、$J_q$ 作为独立状态；阈值弧上输入按名义时钟预先生成的时间控制，$I$ 自由演化，不重置、不纠偏。
- **事件与终点**：启动＝完整方程中 $I$ 首次向上到达 $\eta$；退出＝名义 $t_2$（另记录实际 $S=S_c$ 的穿越）；清零＝退出后 $I$ 向下穿过 1；$t\to\infty$ 按定理 3.5 的首次积分解析补尾，与计至清零的值分开输出。各阶段仓室连续衔接，不重置 $S_q,I_q,R$。
- **逐状态最优选择**：端点与五次驻点多项式的全部近似实根比较（一般正权重、乘子 $\kappa$、能力约束区间；退出附近用缩放坐标）；登记实根个数、近重根、牛顿修正后的残差、近并列个数；并列取 $x$ 较大者并只作诊断记录。$N_x$ 网格（含局部极小处加密）只作交叉核对。结构扫描定位类型改变（brentq 或二分）、间断与陡峭点，退出附近另用对数网格。

## 4 测试结果（实际运行）

`conda run --no-capture-output -n thesis python nr_audit/run_tests.py`：**235 项全部通过，0 项未通过，0 项跳过**（本机多次运行 1–2.5 分钟，最后一次 65 s）；小型入口 `--level smoke`：95 项全部通过（最后一次 17 s）。逐项结果与实测量见 `nr_audit/results/nr2_test_report.md`（报告在提交前的工作区生成，记录了被测源码的 SHA-256，与本提交中的文件一致）。

| 类别（文件） | 项数 | 内容 | 关键实测量（全部项中的最大值） |
|---|---:|---|---|
| 数字来源（`test_sources.py`） | 11 | 清单是否最新、只读来源文件 SHA-256、参数与来源字段逐位相等、派生规则、审计记录与稿件表 1、默认权重、能力代表点、参照列与 `input_manifest`、复用 blob | 全部逐位相等 |
| 模型（`test_model.py`） | 5 | 守恒、$d(S+S_q)/dt=-F$、无回流结构、平衡式 (2.8)、$(\cdot)_+$ 强度 | — |
| 逐状态选择（`test_allocation.py`） | 96 | 驻点多项式＝$\varphi'$ 的分子（SymPy，含 $\kappa$）、与式 (5.4) 差 $c_0^3$、缩放坐标多项式；60 组（两组参数×5 个权重×3 个 $\kappa$×有无能力约束）×25 个状态×$N_x$=2001/4001/8001 的网格核对；三重根、重根鞍点、并列；能力区间公式、空类与等号情形；$S_{\rm sw}$；表 S5 三类结构；与 `phase.json` 的跳变位置回归；不选仅减少接触；默认权重下的类型；退出附近分担比例 $\to w_q/(w_c+w_q)$；能力代表点的结构 | 网格低于根法的相对量 $1.9\times10^{-13}$；连续切换与式 (5.6) 相差 $\le10^{-12}$；跳变位置与原结果相对差 $4.5\times10^{-12}$ |
| 状态路径（`test_state_integrals.py`） | 40 | Lambert $W$ 与 brentq；单控制闭式（定理 3.2、3.6，式 4.11、4.14，附录 B）；Simpson 与 quad；式 (4.15)(4.16)；时长排序；与 `compare_*.csv`、`capacity.json` 回归；$N_z$=1001/2001/4001；15 个乘子点；命题 4.9、5.2 的数值一致性 | 闭式 $3.8\times10^{-13}$；Simpson–quad $3.8\times10^{-13}$；回归 $1.8\times10^{-12}$（能力点 $1.5\times10^{-12}$）；$N_z$ 收敛 $3.4\times10^{-13}$；乘子曲线 $1.35\times10^{-7}$ |
| 完整方程（`test_simulate.py`） | 83 | 质量守恒、正性、控制可行性与平衡式、触发/退出/清零事件、三条独立流量恒等式与控制期恒等式、平台偏离（不为零且 $\le10^{-8}\eta$）、开环敏感性（接触率乘 $1+10^{-6}$ 后 $I$ 离开 $\eta$）、与状态路径对照、与原结果回归（含 $\max(I+I_q)/\eta$）、仅隔离控制的闭式轨迹、推论 4.7、退出后单调、$t\to\infty$ 补尾、能力代表点 | 质量残差 $7.3\times10^{-8}$ 人（西安，$N=1.3\times10^7$）；仓室下限 0；恒等式残差/初始易感者 $8.0\times10^{-15}$；平台偏离 $1.5\times10^{-9}$ 人（相对 $\le5.5\times10^{-13}$）；扰动后 $4.1\times10^{-7}$；退出时 $S-S_c$ $3.9\times10^{-7}$ 人；与状态路径 $1.1\times10^{-12}$；与原结果 $1.4\times10^{-11}$ |

这些是本次复核的判据与结果，不是对数值真值的证明；所有“全局”“结构”判断只指所检验的状态与网格。判据见 `nr_audit/README.md` 第 7 节与 `tests/conftest.py` 的 `TOL`。

## 5 开发中发现并在本模块内修正的问题

均为本模块自身的实现或测试设计问题，没有修改任何参照值或旧结果：

1. **陡峭区的求积精度**：$\kappa\approx-0.242$ 时成本最优控制律在 $z\approx2.82$ 有只跨几个网格格子的陡峭区，不分段的 $N_z=4001$ Simpson 与 quad 相差约 $10^{-6}$（开发中对乘子点的抽查发现；第一次完整运行时乘子曲线回归测试记录的最大相对差为 $9.4\times10^{-7}$，虽在其判据 $10^{-6}$ 以内，但与 quad 不一致）。修正：结构扫描增加同类型异常括区与陡峭点；Simpson 增加逐片 Richardson 误差控制与对半细分。此后 Simpson 与 quad 互差 $\le4\times10^{-13}$，该测试通过。
2. **粗网格上的假陡峭点**：$N_z=1001$、$2001$ 时，以绝对量 $|\Delta x|>10^{-3}$ 判异常会把整段内部解标为陡峭（$N_z$ 收敛测试据此未通过）。修正：改为与邻域中位数比较。
3. **段内收缩造成的界限越界**：为避开间断两侧的并列而收缩求值点，使控制越界约 $4\times10^{-12}$。修正：只对成本最优控制律收缩，收缩后投影回该状态的允许区间；退出状态取 $x=1$。
4. **测试设计**：解析上为零的分项（仅隔离控制的 $J_c$、仅减少接触的 $J_q$）原用相对差比较，改为绝对判据；开环敏感性测试原以 $\gamma\varepsilon\Delta t$ 为预期偏离，未计入 $S$ 随之加快下降，改为定性判据（偏离 $\ge0.1\varepsilon$ 且 $\ge10^4$ 倍未扰动值）。

## 6 与旧结果的差异（均在验收目标以内，供 NR-3）

- 两组参数四种控制、两个能力代表点：两条路径与 `compare_*.csv`、`capacity.json` 的全部核对字段相对差 $\le1.4\times10^{-11}$（含表 2 尚未核过的 $\max(I+I_q)/\eta$）。这只是本模块的回归测试，正式的 N1 表与 JSON 由 NR-3 产出。
- 乘子曲线（图 8 的数据）：15 个抽检点最大相对差 $1.35\times10^{-7}$，出现在 $\kappa\approx-0.244$（跳变正在消失处）；$\kappa$ 接近 0 的点约 $10^{-8}$（开发中另查）。本模块在这些点上 Simpson 与 quad 互差 $\sim10^{-13}$；差异可能来自原实现在该处的插值（PCHIP），未定位，不影响图上显示。是否逐点复核由 NR-3 决定。

## 7 本步未做（转 NR-3）

N1 正式回归表与全精度 JSON；N2 六条固定人口初值轨迹；N3 权重转折加密；N4 控制网格与状态网格的收敛表、积分容差三档（rtol、各分量 atol、max_step 同时收紧）与事件残差表；N5 拟合误差重建；N6 按需。`make_numbers.py` 与 `paper/generated/nr_numbers.tex` 未建立（本步没有入稿数字）。

## 8 待作者决定

无。NR-3 开始前无须作者对本步作裁决；若要求先看模块再进入 NR-3，按作者安排。
