# SIQR 模型下的情景一阈值控制研究

本项目研究带接触追踪与隔离机制的 SIQR 型传染病动力学模型，重点分析医疗容量约束
\(I(t)\leq \eta\) 下的**情景一阈值控制**。当前工作包括控制律的解析推导、参数敏感性、
数值验证、西安真实疫情数据应用，以及情景一阈值控制与 TDINN控制、常规控制之间的条件性比较。

项目仍处于理论分析、数值实验和论文草稿整理阶段。现有结果用于说明控制策略的成立条件、
参数依赖和行为边界，不应解读为已经证明某一种策略在所有情形下优于其他策略。

## 1. 模型与控制问题

模型包含以下状态变量：

- \(S(t)\)：社区易感者；
- \(I(t)\)：社区感染者；
- \(S_q(t)\)：隔离易感者；
- \(I_q(t)\)：隔离感染者；
- \(R(t)\)：移出者。

接触率 \(c(t)\) 和隔离率 \(q(t)\) 是控制变量。当前主线只讨论情景一：固定
\(c(t)=c_0\)，在系统首次达到医疗容量阈值 \(I(t)=\eta\) 后提高隔离率，使平台期满足
\(I(t)\equiv\eta\)。控制律为

\[
q_c(t)=1-\frac{\gamma N}{\beta c_0 S_{\mathrm{th}}(t)},
\]

其中 \(S_{\mathrm{th}}(t)\) 是根据理论启动点 \(S^*\) 和启动时间 \(t_1\) 得到的时间轨迹。
数值实现保持该控制为关于时间的开环函数，而不是依赖积分器当前状态 \(S(t)\) 的反馈控制。

控制过程分为三个阶段：

1. 在常规控制 \((c_0,q_0)\) 下运行，直到 \(I(t)\) 首次达到 \(\eta\)；
2. 在 \([t_1,t_2]\) 内施加 \(q_c(t)\)，使社区感染者维持在阈值平台；
3. 当 \(S(t)\) 到达常规控制下的临界值 \(S_c\) 后恢复 \((c_0,q_0)\)，继续模拟到动态清零 \(I(t)\leq1\)。

主要比较指标包括控制启动时间、解除时间、控制时长、清零时间、感染峰值、总累计感染和二次加权成本

\[
J=\int_0^T\left[
w_c\left(\frac{(c_0-c(t))_+}{c_0}\right)^2+
w_q\left(\frac{(q(t)-q_0)_+}{1-q_0}\right)^2
\right]\,dt,
\qquad w_c=1,\quad w_q=2.
\]

## 2. 项目结构

```text
.
├── paper_elegantpaper_relayout/   # ElegantPaper 中文主论文工程与编译后 PDF
├── code/                          # 情景一基准模拟和 MATLAB 参数分析
├── scenario1_inflection/          # q_c(t) 拐点、曲率与相对位置分析（Python）
├── scenario1_threshold_landscape/ # N=763 下的二维阈值响应图谱（MATLAB）
├── xian_control_comparison/       # 西安三种控制策略的拟合、比较与敏感性分析
├── xian_dom/                      # 有效人口占优区域及图 20--23 的求解和绘图
├── c0_sensitivity/                # 固定阈值比例下的 c0 敏感性实验
├── 真实数据/                       # 六个地区的原始 Excel 数据，请勿直接修改
├── figures/                       # 主论文采用的成品图
├── table/                         # 主论文采用的 CSV 与 LaTeX 表格
├── refs/                          # 参考论文、文本摘录和模型示意图
├── archive_unused/                # 已归档的旧实验与非当前主线内容
├── ai_markdown/                   # 分析记录与阶段性材料
├── AGENTS.md                      # 项目研究口径和协作约定
└── PROGRESS.md                    # 论文整合过程记录
```

主要入口如下：

- 主论文源文件：[`paper_elegantpaper_relayout/flatten_curve_analysis_cn.tex`](paper_elegantpaper_relayout/flatten_curve_analysis_cn.tex)
- 主论文 PDF：[`paper_elegantpaper_relayout/flatten_curve_analysis_cn.pdf`](paper_elegantpaper_relayout/flatten_curve_analysis_cn.pdf)
- 西安比较主程序：[`xian_control_comparison/xian_control_comparison.py`](xian_control_comparison/xian_control_comparison.py)
- 情景一完整图谱入口：[`scenario1_threshold_landscape/run_all.m`](scenario1_threshold_landscape/run_all.m)
- 拐点数值校验：[`scenario1_inflection/verify_anchors.py`](scenario1_inflection/verify_anchors.py)
- 有效人口占优分析说明：[`xian_dom/README.md`](xian_dom/README.md)

进入带有独立 `AGENTS.md` 的子目录工作时，应同时遵守根目录与子目录规范；若细节冲突，以子目录规范为准。

## 3. 环境与依赖

项目主要在 Windows PowerShell 下运行。

### Python

建议使用 Python 3.10 或更高版本。主要第三方依赖为：

```powershell
python -m pip install numpy pandas scipy matplotlib openpyxl
```

代码使用 `numpy`、`pandas`、`scipy` 和 `matplotlib` 完成数值积分、求根、参数拟合和绘图，
使用 `openpyxl` 读取 Excel 数据。目前仓库未锁定统一的 Python 环境文件，复现时应记录实际包版本。

### MATLAB

MATLAB 模块使用常微分方程求解、数值积分、表格读写和绘图功能；涉及 `lambertw` 的脚本需要
Symbolic Math Toolbox。建议从 PowerShell 使用 `matlab -batch`，避免 Git Bash 下的输出异常。

### LaTeX

主论文需要支持中文的 XeLaTeX 环境和 Biber。仓库已包含 `elegantpaper.cls`，但仍需安装模板依赖的
LaTeX 宏包和相应中英文字体。主稿使用 `biblatex` 管理参考文献，完整编译必须包含 Biber 步骤。

## 4. 主要运行方式

以下命令均从项目根目录执行。

### 西安控制策略比较

```powershell
python -B xian_control_comparison\xian_control_comparison.py
```

该程序拟合西安初值并比较 TDINN控制、情景一阈值控制和常规控制，输出时间序列、汇总表和论文图。

### 情景一拐点分析

```powershell
conda run --no-capture-output -n thesis python -B scenario1_inflection\verify_anchors.py
conda run --no-capture-output -n thesis python -B scenario1_inflection\fig_lambda_sensitivity.py
conda run --no-capture-output -n thesis python -B scenario1_inflection\fig_landscape4.py
conda run --no-capture-output -n thesis python -B scenario1_inflection\fig_scan_t.py
conda run --no-capture-output -n thesis python -B scenario1_inflection\fig_diagnose.py
```

若未使用名为 `thesis` 的 Conda 环境，可将命令中的 Python 解释器替换为已安装上述依赖的环境。

### 情景一阈值响应图谱

```powershell
matlab -batch "run('E:\work\draft\scenario1_threshold_landscape\run_all.m')"
```

该入口会重建 `scenario1_threshold_landscape/current_run/` 下的数据、图、表和日志。
如需保留某次探索性结果，应在重新运行前另行复制，避免覆盖当前输出。

### 有效人口占优分析

```powershell
powershell -ExecutionPolicy Bypass -File xian_dom\run_all.ps1
```

该模块生成 \((N_{\mathrm{eff}},\eta)\) 平面上的占优边界，以及固定 \(N_{\mathrm{eff}}\)
或固定 \(\eta\) 的轨迹比较图。详细口径、模块依赖和输出文件见
[`xian_dom/README.md`](xian_dom/README.md)。

### 编译主论文

```powershell
Set-Location paper_elegantpaper_relayout
xelatex -interaction=nonstopmode flatten_curve_analysis_cn.tex
biber flatten_curve_analysis_cn
xelatex -interaction=nonstopmode flatten_curve_analysis_cn.tex
xelatex -interaction=nonstopmode flatten_curve_analysis_cn.tex
```

只运行 XeLaTeX 而跳过 Biber 会使正文引文显示为 `[?]`。改动图、表、交叉引用或公式编号后，
应执行完整四步编译并检查 PDF 页面渲染。

## 5. 研究主线与结果边界

当前论文依次处理模型设定、常规阶段首次积分、情景一闭式控制律、拐点结构、成本和参数敏感性、
数值验证、西安真实疫情应用、规模不变性与有效人口占优分析。比较 TDINN控制、情景一阈值控制和
常规控制时，结论均依赖于参数范围、有效人口、医疗容量阈值、成本权重和采用的效果指标。

在当前设定下，数值结果可用于识别峰值、成本、控制时长和累计感染之间的权衡；纳入总累计感染或
清零时间后，占优区域可能明显收缩。因此，本项目保留探索性结果和失败边界，不用低阈值或特定参数下的
单次结果替代主基准，也不作无条件的策略优劣判断。

## 6. 数据、产物与版本管理

- `真实数据/` 保存原始输入，分析代码不应直接覆写这些文件。
- 主论文使用的成品图和表集中复制到 `figures/` 与 `table/`。
- 各实验模块的过程输出保留在各自目录，正式输出与探索性输出应使用不同目录或后缀。
- LaTeX 中间文件、Python 缓存、本机编辑器设置和本机 AI 助手权限配置不纳入版本控制。
- 提交前应检查 `git status` 与 `git diff`，避免把无关或含本机信息的文件加入提交。

## 7. 许可说明

本仓库是正在整理的研究项目，目前**未提供开源许可证**。仓库公开可见仅用于版本存档、研究交流和
结果核查，不表示作者授予复制、修改、再发布或商业使用许可。`refs/` 中的论文和其他第三方材料仍归
原权利人所有；引用或使用相关内容时应遵守原出版方和数据来源的许可条件。
