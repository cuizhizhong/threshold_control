# 最终LaTeX工程与数值复现包

## 1. 唯一论文版本

本包的论文内容锁定为 `threshold_control_capacity_final_20261002.zip` 中的容量定义整合稿：主稿45页，补充表格3页。本轮不改写论文，不增加或重画图表，不合入GitHub可能后续更新的内容。

`latex/` 中主稿TEX、主稿PDF、补充TEX/PDF、references.bib、elegantpaper.cls、原编译脚本及20幅图，与原容量定义包逐文件相同。仅补入从这一版文献库生成的 `.bbl`，便于查看参考文献编译结果。

本轮在独立目录删除旧辅助文件，从最终TEX与BIB重新编译。主稿45页和补充3页全部页面的提取文字相同，120 dpi RGB渲染逐像素相同。PDF文件创建时间等元数据可能不同；交付的正式PDF仍保留原字节。报告见 `validation/pdf_comparison.json` 与 `validation/source_consistency.json`。

本包是完整编译工程和指定联合控制算例的复现包，不是原仓库全部MATLAB代码、所有扫描原始数据及临床数据库的镜像。

## 2. 文件入口

| 文件 | 用途 |
|---|---|
| `latex/flatten_curve_analysis_cn.tex` | 唯一完整主稿 |
| `latex/flatten_curve_analysis_cn.pdf` | 与前次最终版完全相同的45页PDF |
| `latex/flatten_curve_supplement_cn.tex/.pdf` | 同版本3页补充表格 |
| `latex/references.bib` | 同版本文献库 |
| `latex/elegantpaper.cls` | 实际使用的模板 |
| `latex/figures/` | 全部20幅矢量图，不重画 |
| `scripts/threshold_scale_check.py` | 原包已有的比例算术脚本，字节未改 |
| `numerics/joint_comparison.py` | 从此前交付包恢复的原联合控制计算程序，字节未改 |
| `scripts/reproduce_joint_example.py` | 本轮新增的配置读取、导出及三阶段ODE核查入口 |
| `numerics/inputs/baseline_parameters.json` | 联合控制的明确输入、终点与计数定义 |
| `numerics/results/` | 本轮实际运行的完整精度输出、ODE核查及采样轨迹 |
| `review/交付与数值溯源报告.md` | 对代码来源、可复现值和未验证事项的完整说明 |
| `plans/后续研究计划_最新版.md` | 已更新完成状态的唯一后续研究计划 |
| `provenance/` | 旧计算程序和输出的来源证据；不含旧版主稿 |

## 3. 编译

需要安装含中文支持的TeX环境：XeLaTeX、Biber、ctex/Fandol、newtx、TeX Gyre及模板依赖宏包。建议使用完整TeX Live，或按缺包提示安装所需宏包。模板在TeX Gyre字体不可用时有Liberation字体回退；不同字体或TeX版本可能改变换行。包内不分发字体文件。

本轮实际环境见 `validation/environment.json`。通过的环境为XeTeX（TeX Live 2025/dev/Debian）、Biber 2.20。

从解压后的根目录运行：

```bash
bash latex/build.sh
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\latex\build.ps1
```

脚本先编译补充材料，再编译主稿、运行Biber并解析交叉引用。普通build会更新 `latex/` 内PDF的创建时间和辅助文件；不需要重新生成图件。

需要保留交付PDF字节不变、独立核对编译时：

```bash
python -m pip install -r requirements-audit.txt
python scripts/verify_build.py
```

该命令在临时目录编译，在 `validation/build_recheck/` 输出重编PDF和逐页对照，不覆盖正式稿。

## 4. 复现阈值换算

仅需Python标准库：

```bash
python scripts/threshold_scale_check.py --population 13163000 --beds-per-100k 4.37 --coefficient 0.0252 --design-theta 0.002 --output validation/threshold_scale_calculations.json
```

这只核对比例设定的算术，不计算床位动态、不估计临床系数。参考阈值约0.001734126984126984，不等于已采用的代表性设计阈值0.002。

## 5. 复现联合控制数值

```bash
python -m pip install -r requirements-numerics.txt
python scripts/reproduce_joint_example.py
```

使用 `numerics/inputs/baseline_parameters.json` 中的参数。计算核心从历史工程恢复，不是按论文小数反向拼接结果。原包的计算程序与未取整输出都有独立SHA记录。

输出：
- `numerics/results/joint_comparison_results.json`：参数、S*、Sc、启动时刻、全部比较策略、容差检验和控制期ODE残差；
- 同名 `.csv`：17位有效数字的结果；
- `full_three_stage_ode_check.json`：本轮新增，从t=0真实初值积分的三阶段核对；
- `full_three_stage_trajectories.csv`：三阶段采样轨迹，切换时刻以phase区分左右控制值，不用于替代标量积分。

JSON/CSV不按论文四位小数取整；浮点尾数不是精确真值，可靠精度应结合容差与ODE对照判断。

原样执行恢复的历史理论数值检查（可选，需要SymPy）：

```bash
python -m pip install -r requirements-audit.txt
python scripts/rerun_historical_checks.py
```

这类数值测试不能替代数学证明的独立复核。

## 6. 版本和未验证事项

解压后可先执行：

```bash
python scripts/verify_release.py
```

它校验锁定的最终源码、PDF、图件、计算代码和配置。普通LaTeX重编后PDF元数据会变化，故若要与交付哈希比较，应先运行此检查，或使用不覆盖正式稿的 `verify_build.py`。

上一版容量定义包没有附联合控制程序。本轮从此前两份实际交付包中恢复，并再次运行；不能把“代码可恢复、现在可复现”表述为已认证过去每次回复的执行过程。来源详见 `provenance/source_inventory.json`。

当前没有重新拟合西安，没有统一重算补充表S2的累计数差异，没有复跑20幅旧图背后的全部参数扫描，没有计算真实ICU占用、回流或延迟效应。所谓4.5倍ICU峰值、503天控制不在本包已验证结果中。本轮不把未执行任务写入论文成果。

编译日志说明：`stdout.log`包含从零编译的所有轮次，初次未定义引用及提示重跑属于正常中间状态；最终验收以两个文档最后一轮的`.log`和Biber的`.blg`为准，见`validation/final_log_checks.json`。
