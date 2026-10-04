# 联合控制来源与运行说明

本目录存放当前论文复现所需的联合控制核心、参数和完整冻结交付来源。2026-10-04 从 `ai/threshold_control_reproducible_release_20261002/` 整体移入，内部 87 个文件的内容及相对目录保持不变。`ai/` 用于 AI 讨论、计划和尚未纳入正式链条的外部材料，不再是正式复现入口的依赖目录。

## 文件分工

- `threshold_control_reproducible_release_20261002/numerics/joint_comparison.py`：原联合控制核心。
- `threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json`：基准参数的原始来源。
- 同包 `numerics/results/`、`validation/`、`provenance/`、`review/`：供应方结果、来源和审查记录，不作为从头计算的替代。
- 同包 `latex/`：导入时的冻结论文、补充材料与图件来源，不是需要并行修改的正式稿。文案同步、理论来源及 S2 历史对账仍需读取它们，因此保留完整包，不能只留下数值程序。
- 同包 `plans/`：冻结来源携带的后续研究计划，包含尚未完成的内容，保持原样。

当前唯一正式稿仍为 `../latex/flatten_curve_analysis_cn.tex`，实际复现与开环核查入口在 `../reproducibility/`。目录迁移没有重新拟合或修改模型、已认可图表；正常全文复现仍从原始 Excel 重建拟合结果，不受这次迁移范围限制。`ai/` 中的探索性结果不自动并入正式稿。

正文已包含 `c_min`、`q_cap` 的能力约束理论，当前正式数值链条只验收了无额外能力限制的联合控制基准。有限能力新增算例、权重扫描及西安联合控制的系统数值计算尚未纳入正式验收。`ai/` 中第6.4节材料包虽有“正式版”名称、补丁和预览 PDF，仍是待审材料，不是本目录核心或已发布论文的一部分。

## 运行

从项目根目录执行。输出使用新建空目录；以下命令只是使用说明，本次目录整理没有重跑科学计算。

```powershell
# 联合控制基准：完整候选比较、收敛诊断与独立时间开环 ODE 核查。
python -B reproducibility/joint.py --output-dir reproducibility/runs/<新的运行目录>

# 全文复现：仍由统一入口协调原始输入和各研究模块。
powershell -NoProfile -ExecutionPolicy Bypass -File reproducibility/run_all.ps1

# 冻结来源的只读锁定文件检查，不重算。
python -B joint_control/threshold_control_reproducible_release_20261002/scripts/verify_release.py
```

不要直接使用冻结数值脚本的默认输出位置，部分入口会写入包内 `numerics/results/`。需要使用供应方脚本时先核对参数，并显式指定独立输出目录。

本次迁移清单、计划保留理由及实际核查范围见 [来源整理核查](../reproducibility/release_reports/source_relocation_20261004/README.md)。旧验收报告保持历史路径和哈希，不改写为迁移后的新验收。
