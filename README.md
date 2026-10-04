# SIQR 模型下接触减少与追踪隔离的阈值控制

当前唯一正式稿件为 `latex/flatten_curve_analysis_cn.tex`，补充表格为同目录
`flatten_curve_supplement_cn.tex`。2026-10-02 新稿来自 `joint_control/threshold_control_reproducible_release_20261002`；
该交付包保持冻结，2026-10-04 从 `ai/` 原样迁移。正式稿包含仅隔离基准和联合控制理论，不再只有情景一。

整稿复现说明和本机验收状态见 [reproducibility/README.md](reproducibility/README.md)。
复现入口采用独立空输出目录，不调用 Nature skills，不直接清空旧实验目录或覆盖正式图件。
“有源代码”“供应方运行记录”“本机实际复跑通过”是不同状态；以最新运行报告为准。
旧版本与导入前备份保留，不作为并行维护的正式主稿。
2026-10-03 已完成本研究版本的双空目录复现和正式工程重编译：20 幅图、4 张正文表、3 张补充表及已列明关键数值通过；正文 45 页、补充材料 3 页。结果与证据边界见 [验收报告](reproducibility/validation_report.md)，未取整结果集中在 `reproducibility/results/20261003_release_final/`。这不是一般证明或真实医疗阈值认证。

本项目研究带接触追踪与隔离机制的 SIQR 型传染病动力学模型，分析社区感染阈值约束
$I(t)\leq \eta$ 下的仅隔离基准及接触率—隔离率联合分配。当前工作包括控制律推导、
参数敏感性、数值验证、西安数据重构和与 TDINN控制、常规控制的条件性比较。
该阈值并非由西安实际 ICU 占用独立标定；无回流模型中的固定退出目标也不等于所有可行防控策略。

项目仍处于理论分析、数值实验和论文草稿整理阶段。现有结果用于说明控制策略的成立条件、
参数依赖和行为边界，不应解读为已经证明某一种策略在所有情形下优于其他策略。

## 1. 模型与控制问题

模型包含以下状态变量：

- $S(t)$：社区易感者；
- $I(t)$：社区感染者；
- $S_q(t)$：隔离易感者；
- $I_q(t)$：隔离感染者；
- $R(t)$：移出者。

接触率 $c(t)$ 和隔离率 $q(t)$ 是控制变量。仅隔离解析基准采用情景一：固定
$c(t)=c_0$，在系统首次达到医疗容量阈值 $I(t)=\eta$ 后提高隔离率，使平台期满足
$I(t)\equiv\eta$。控制律为

$$
q_c(t)=1-\frac{\gamma N}{\beta c_0 S_{\mathrm{th}}(t)},
$$

其中 $S_{\mathrm{th}}(t)$ 是根据理论启动点 $S^*$ 和启动时间 $t_1$ 得到的时间轨迹。
数值实现保持该控制为关于时间的开环函数，而不是依赖积分器当前状态 $S(t)$ 的反馈控制。

控制过程分为三个阶段：

1. 在常规控制 $(c_0,q_0)$ 下运行，直到 $I(t)$ 首次达到 $\eta$；
2. 在 $[t_1,t_2]$ 内施加 $q_c(t)$，使社区感染者维持在阈值平台；
3. 当 $S(t)$ 到达常规控制下的临界值 $S_c$ 后恢复 $(c_0,q_0)$，继续模拟到动态清零 $I(t)\leq1$。

主要比较指标包括控制启动时间、解除时间、控制时长、清零时间、感染峰值、总累计感染和二次加权成本

$$
J=\int_0^T\left[
w_c\left(\frac{(c_0-c(t))_+}{c_0}\right)^2+
w_q\left(\frac{(q(t)-q_0)_+}{1-q_0}\right)^2
\right]\,dt,
\qquad w_c=1,\quad w_q=2.
$$

## 2. 项目结构

```text
.
├── latex/                         # 唯一正式主论文工程、补充材料与 PDF
├── reproducibility/               # 隔离复现入口、配置、对应清单与验收记录
├── code/                          # 情景一基准模拟和 MATLAB 参数分析
├── scenario1_inflection/          # q_c(t) 拐点、曲率与相对位置分析（Python）
├── scenario1_threshold_landscape/ # N=763 下的二维阈值响应图谱（MATLAB）
├── xian_control_comparison/       # 西安三种控制策略的拟合、比较与敏感性分析
├── xian_dom/                      # 有效人口条件比较的求解与原绘图逻辑
├── c0_sensitivity/                # 固定阈值比例下的 c0 敏感性实验
├── 真实数据/                       # 当前主线使用的西安原始 Excel 数据，请勿直接修改
├── joint_control/                 # 联合控制核心、参数及完整冻结来源（内容不改）
├── ai/                            # AI 讨论、计划与尚未纳入正式链条的外部材料
├── refs/                          # 参考论文、文本摘录和模型示意图
├── archive_unused/                # 旧实验、非当前主线数据与可复现输出快照
└── AGENTS.md                      # 项目研究口径和协作约定
```

主要入口如下：

- 主论文源文件：[`latex/flatten_curve_analysis_cn.tex`](latex/flatten_curve_analysis_cn.tex)
- 主论文 PDF：[`latex/flatten_curve_analysis_cn.pdf`](latex/flatten_curve_analysis_cn.pdf)
- 正式复现入口：[`reproducibility/run_all.ps1`](reproducibility/run_all.ps1)
- 联合控制来源与运行说明：[`joint_control/README.md`](joint_control/README.md)
- 西安比较主程序：[`xian_control_comparison/xian_control_comparison.py`](xian_control_comparison/xian_control_comparison.py)
- 情景一完整图谱入口：[`scenario1_threshold_landscape/run_all.m`](scenario1_threshold_landscape/run_all.m)
- 拐点数值校验：[`scenario1_inflection/verify_anchors.py`](scenario1_inflection/verify_anchors.py)
- 有效人口占优分析说明：[`xian_dom/README.md`](xian_dom/README.md)

以下原模块入口保留供历史实验核对，并非当前整稿复现入口；部分会覆盖自身旧输出，
不要用它们替代独立输出目录中的正式流程。
进入带有独立 `AGENTS.md` 的子目录工作时，应同时遵守根目录与子目录规范；若细节冲突，以子目录规范为准。

## 3. 环境与依赖

项目主要在 Windows PowerShell 下运行。

### Python

本轮整稿实际验收环境为 Python 3.12.8；其他 Python 版本尚未验收。正式复现请使用
`reproducibility/requirements.txt` 中锁定的依赖。以下通用依赖命令仅供历史模块使用：

```powershell
python -m pip install numpy pandas scipy matplotlib openpyxl
```

代码使用 `numpy`、`pandas`、`scipy` 和 `matplotlib` 完成数值积分、求根、参数拟合和绘图，
使用 `openpyxl` 读取 Excel 数据。整稿复现锁定环境见 `reproducibility/requirements.txt`，实际工具和字体见运行报告。

### MATLAB

MATLAB 模块使用常微分方程求解、数值积分、表格读写和绘图功能；涉及 `lambertw` 的脚本需要
Symbolic Math Toolbox。建议从 PowerShell 使用 `matlab -batch`，避免 Git Bash 下的输出异常。

### LaTeX

主论文需要支持中文的 XeLaTeX 环境和 Biber。仓库已包含 `elegantpaper.cls`，但仍需安装模板依赖的
LaTeX 宏包和相应中英文字体。主稿使用 `biblatex` 管理参考文献，完整编译必须包含 Biber 步骤。

## 4. 主要运行方式

以下命令均从项目根目录执行。

### 历史西安控制策略比较（可能覆盖旧输出）

```powershell
python -B xian_control_comparison\xian_control_comparison.py
```

该程序拟合西安初值并比较 TDINN控制、情景一阈值控制和常规控制，输出时间序列、汇总表和论文图。

### 历史情景一拐点分析（可能覆盖旧输出）

```powershell
conda run --no-capture-output -n thesis python -B scenario1_inflection\verify_anchors.py
conda run --no-capture-output -n thesis python -B scenario1_inflection\fig_lambda_sensitivity.py
conda run --no-capture-output -n thesis python -B scenario1_inflection\fig_landscape4.py
conda run --no-capture-output -n thesis python -B scenario1_inflection\fig_scan_t.py
conda run --no-capture-output -n thesis python -B scenario1_inflection\fig_diagnose.py
```

若未使用名为 `thesis` 的 Conda 环境，可将命令中的 Python 解释器替换为已安装上述依赖的环境。

### 历史情景一阈值响应图谱（可能覆盖旧输出）

```powershell
matlab -batch "run(fullfile(pwd,'scenario1_threshold_landscape','run_all.m'))"
```

该入口会重建 `scenario1_threshold_landscape/current_run/` 下的数据、图、表和日志。
如需保留某次探索性结果，应在重新运行前另行复制，避免覆盖当前输出。

### 历史有效人口占优分析（可能覆盖旧输出）

```powershell
powershell -ExecutionPolicy Bypass -File xian_dom\run_all.ps1
```

该模块生成 $(N_{\mathrm{eff}},\eta)$ 平面上的占优边界，以及固定 $N_{\mathrm{eff}}$
或固定 $\eta$ 的轨迹比较图。详细口径、模块依赖和输出文件见
[`xian_dom/README.md`](xian_dom/README.md)。

### 编译正式主论文及补充材料

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File latex\build_paper.ps1
```

该入口先为补充材料运行两遍 XeLaTeX，再执行主稿 `xelatex → biber → xelatex → xelatex`，
使干净目录也能解析跨文档标签。跳过 Biber 会使正文引文显示为 `[?]`。改动图、表、
交叉引用或公式编号后，应执行此完整入口并检查 PDF 页面渲染。

## 5. 研究主线与结果边界

当前论文处理模型设定、常规阶段首次积分、仅隔离闭式控制律、拐点结构、成本和参数敏感性、
联合控制表示及候选比较、数值验证、西安数据应用、规模不变性与有效人口条件比较。比较 TDINN控制、情景一阈值控制和
常规控制时，结论均依赖于参数范围、有效人口、医疗容量阈值、成本权重和采用的效果指标。

在当前设定下，数值结果可用于识别峰值、成本、控制时长和累计感染之间的权衡；纳入总累计感染或
清零时间后，占优区域可能明显收缩。因此，本项目保留探索性结果和失败边界，不用低阈值或特定参数下的
单次结果替代主基准，也不作无条件的策略优劣判断。

## 6. 数据、产物与版本管理

- `真实数据/` 只保留当前主线使用的西安原始输入；其余五个地区的数据已移至
  `archive_unused/inactive_scope/multicity_raw_data/`，分析代码不应直接覆写原始文件。
- 正式稿只读取 `latex/figures/` 中的 20 幅图；4 张正文表和 3 张补充表直接保存在各自 TeX 中。
  未引用的图件副本、根目录旧图表及 `latex/table/` 已移入回收站，不再作为并行编辑入口。
  `latex/revision_*` 仍含现用绘图源码及历史核查材料，不能当作无用目录删除。
- 验收通过后，完整精度派生结果汇集到 `reproducibility/results/<运行版本>/`，对应清单、
  环境和验收报告汇集到 `reproducibility/`；这些结果副本不是下一轮计算输入。
- 各实验模块的过程输出由运行命令重新生成并已加入 `.gitignore`；清理前的输出快照保存在
  `archive_unused/generated_snapshots/`，不再与活动源码混放。
- 当前不参与论文主线但仍有追溯价值的代码、数据和图片统一放在 `archive_unused/`；
  归档清单和恢复方式见 [`archive_unused/README.md`](archive_unused/README.md)。
- LaTeX 中间文件、Python 缓存、本机编辑器设置和本机 AI 助手权限配置不纳入版本控制。
- 本轮保守清理的完整清单、可恢复记录与编译/哈希验收见
  [`reproducibility/release_reports/cleanup_20261003/`](reproducibility/release_reports/cleanup_20261003/)。
  原始数据、冻结包、所有复现运行、历史备份和归档材料均保留；本轮不自动提交或推送 Git。
- 提交前应检查 `git status` 与 `git diff`，避免把无关或含本机信息的文件加入提交。

## 7. 许可说明

本仓库是正在整理的研究项目，目前**未提供开源许可证**。仓库公开可见仅用于版本存档、研究交流和
结果核查，不表示作者授予复制、修改、再发布或商业使用许可。`refs/` 中的论文和其他第三方材料仍归
原权利人所有；引用或使用相关内容时应遵守原出版方和数据来源的许可条件。
