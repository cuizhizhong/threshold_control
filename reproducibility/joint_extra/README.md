# 联合阈值控制新增核查（A–D）

活动模块从当前模型重算共同感染平台控制类，冻结来源和历史探索仅只读。
`ai/` 的候选代码是来源，不是运行依赖。本文最优性限于共同启动状态、
固定感染平台及 `S=Sc` 退出目标，不是一般状态约束最优控制。

## 输入和运行

基准读取 `joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json`
的完整参数及 `other_initial_states`。西安读取指定已验收 `xian/reference.json`
中的完整 `I0_abs`、`delta_q`，取 `S0=N-I0` 和设计情景 `eta=0.002N`。
本轮继承既有拟合，不重新拟合或重新积分 TDINN；参考缺项留空。

```powershell
python -B reproducibility\joint_extra\test_joint_extra.py
python -B reproducibility\joint_extra\run.py --out reproducibility\results\joint_extra_v4_NEW --mode compute --tasks A,B,C,D
python -B reproducibility\joint_extra\run.py --out reproducibility\results\joint_extra_v4_NEW --mode plot --textwidth-bp 451.275616438
python -B reproducibility\joint_extra\run.py --out reproducibility\results\joint_extra_v4_NEW --mode verify
```

`--baseline`、`--xian-reference`、`--root` 可显式指定来源；`--out`/`--output-dir`
必须指向全新或空目录。`all` 先计算再绘图，均不覆盖正式论文。
`plot/all` 还须传入本轮同版本主稿实测 `--textwidth-bp`；示例数值是
2026-10-04 模板测量，不是以后任意模板的固定宽度。
`verify` 核查本轮既有验收与计算代码哈希，另写时间戳记录，不冒充新的科学复算。
公开 `run(output_dir, root, baseline_path=None, xian_reference=None, tasks=None, mode='compute')`
供整稿复现入口调用；不得把旧输出复制到第二轮以替代重新计算。

## 算法及证据边界

- 两端点和全部数值实驻点比较；κ驻点五次式包含 `-κ*x^3`。退出邻域
  采用缩放 `y=(1-x)/(1-Sc/S)`，含κ时重建缩放多项式。受限区间直接参加
  候选比较，不以截断无约束控制代替受限最小值。
- 用原坐标/缩放坐标、独立网格和各局部极小区间加密交叉核查；浮点实根
  筛选不等于严格区间根隔离。近并列记录，不为画面平滑选取较贵候选。
- 候选目标交叉或端点导数零点定位切换，按左右极限分段名义轨迹。
  内部段插值允许区间份额 `(x-lo)/(hi-lo)`，由名义S的边界重构可行x，
  不裁剪无约束最优控制；纯端点段保留解析边界。Sc退化份额只作参数化
  延拓，近退出验收使用实际非退化状态的缩放求根。
  完整 SIQR 只使用已生成的固定名义时间函数，不使用实际实时 S 反馈。
- 状态积分显式拆分所有PCHIP多项式区间及能力几何折点，向量化比较
  Gauss-Legendre 4、8、16阶结果。阶数差是数值诊断，不是严格误差界；
  同时检查其经人数计数系数放大后的误差。名义时钟在能力折点分段，
  单控制及纯能力端点采用线性或指数解析解，其余采用局部时间DOP853。
- 完整仓室及累计计数使用归一化 DOP853 分量容差，保留真实入口 Sq/Iq；
  名义退出后检查实际 S/I 偏差，恢复常规至 I=1 的下降事件。
- `I+Iq` 与 I 的峰值在 `[0,t_end]` 的连续阶段稠密解、导数零点及切换候选
  上比较并加密检查；现存感染峰值不是 ICU/住院占用，也非无限时域峰值。
- 成本—时长表是有限乘子支持点；连线不代表所有时长均被乘子覆盖。
  κ正负含义分开，显式α族不通过插值宣称同时间严格成本改进。

验收门槛固定在对应版本首次运行前的 `acceptance.json`，包括人数、天、控制比例、
根残差、独立算法、退出份额、分支定位及峰搜索等不同量纲。状态非负下限
沿用原 joint 的较严格 `-1e-8` 人；概率端点 `beta=1` 可计算，但新增Sq上限
与时长下限的反向换算仅适用于 `0<beta<1`。

2026-10-04 首批 `run_1/2` 均真实失败，保留在
`reproducibility/runs/joint_integration_20261004/`，不改写为通过。西安仅接触
名义事件时间偏差3.09e-9天放大成约1.00e-4人的出口偏差；受限最低成本的
全局QUAD漏估局部插值区间，时长偏差约7.13e-8天放大成约4.7e-4人，
其误差估计不足以预警，状态网格一致也不能替代独立积分核查。独立诊断
脚本和结果位于同目录 `diagnostics/`。v3修复显式分段积分和名义时钟，
将完整ODE容差收紧一档；所有人数、天、控制、根验收阈值保持原值，
`precision_revision`保留旧/新设置。D在κ=-0.006700187503509591的失败是
把邻近S的单侧x直接放到精确切换S导致轻微越界；现改为同一切换S的
候选左右极限，不放宽边界容差。上述v3冻结说明仅针对该版本，不掩盖这些修订。

随后 `run_3/4` 的A/C通过，B/D仍失败。显式求积检出了真实λ插值网格误差：
λ构造跨能力几何折角，8k/16k累计差 `3.54398e-4` 人。v4在构造λ之前纳入
几何折点，并以该S实际候选确定端点；8k/16k独立探针差 `2.52388e-7` 人。
D在既定κ `-0.24620924014946255` 的粗单元中第二驻点分支尚未出现，
两个最近候选映到同一根产生假目标零点；v4仅在两个不同候选时求目标交叉，
缺分支时用实际选中分支二分。原4k/8k探针累计差降至 `4.70536e-6` 人。
v4不改变v3的网格、求积阶数、ODE精度档或任何验收门槛，新增完整状态网格
回归；这些修复探针不是全任务通过记录，最终状态以对应运行validation为准。

## 输出

2026-10-05 的第7节 v2 核查在原310个乘子值之外，加密
`[-0.6,-0.2]`（步长0.002）。原浮点值优先保留，新点按绝对差
`1e-12` 去除近重复，共470点；完整两套网格及构造规则写入
`input_manifest.json.settings.kappa_grid_construction`。这不改变求解器或验收门槛。
新的受控稿源可按 `generated_figure_labels` 只生成图12，其余23幅图按批准哈希
继承，不把继承图称为本轮重新绘制。科学双跑、原310点回归、文案测试、编译和
页面检查的实际状态分别记录于
`reproducibility/release_reports/20261005_sec7_v2_refinement/`，不能由网格点数推断通过。

`input_manifest.json` 保存完整输入、派生量、软件和计算源码哈希；
`compare_*.csv` 保留 state/time 独立字段及四策略未取整指标，
`trajectories_*.csv` 保存分段实际状态及固定时间控制；
`capacity.json`、`capacity_*.npz`、代表轨迹绑定同一能力配置；
`phase_*.npz` 保存选择份额及候选分类，Sc的0/0首列遮罩，非理论填充值；
`frontier_baseline.csv`、`alpha_family_baseline.csv` 保存实际支持点和状态跳变/连线标识。
`candidate_checks_*.json` 保留完整候选、开环、收敛和峰值诊断，
`validation.json` 对每个任务分别记录通过、失败或未执行；D失败不撤销A–C。
`derived_summary.json` 是正文百分比的单一未取整来源；CSV以17位有效数字
往返保存，不表示17位认证。JSON缺失为null，不输出NaN。

B等号代表点也运行独立受限开环轨迹。C对全部非退化相图单元汇总原
导数残差、允许区间及候选比较，并对实际显示切换做原单元17点加密
定位核查；这仍是有限网格证据。D每40点及每个失败点保存检查点，
失败点不剔除、其前后不连线，任何失败均令D不通过。

计算源码与绘图/文案层分别记录版本；图件只从当前结果读取。
数学证明、数值复算、排版检查分别验收，不将开发回归或旧验收冒充本轮完成。
