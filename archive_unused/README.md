# 非当前主线材料归档

本目录保存当前论文主线不再直接使用、但仍有复核或恢复价值的代码、数据、图表和运行快照。
归档实验不是正式计算入口；部分快照仍供复现程序作历史差异对账，不能删除，也不能用它们代替从原始输入计算。正式主稿为 [flatten_curve_analysis_cn.tex](../latex/flatten_curve_analysis_cn.tex)，20幅正式图件位于 `../latex/figures/`；4张正文表直接维护于主稿，3张补充表在 [补充材料](../latex/flatten_curve_supplement_cn.tex)中。根目录旧 `figures/`、`table/` 已不再是正式输出位置。

当前实验、图号及计算来源见[复现说明](../reproducibility/README.md)和[逐项登记](../reproducibility/registry.json)。本目录内部的 `AGENTS.md`、README及数值记录只说明对应历史实验，不能覆盖当前正式稿的初值、成本、阈值定义和验收规则。

## 目录说明

- `generated_snapshots/`：清理前各实验模块的可复现输出，包括情景一 MATLAB 图谱、
  西安主比较、有效人口敏感性、二维阈值图谱和 `c0` 敏感性结果。
- `inactive_scope/scenario2/`：当前暂不研究的情景二、情景三论文草稿、代码和表格。
- `inactive_scope/multicity_raw_data/`：广州、海南、辽宁、乌鲁木齐和扬州原始数据。
  当前活动数据目录只保留西安数据。
- `superseded/`：已由现行模块替代的占优区域实现、论文不再引用的图片、早期扫描数据和旧表格。
- `fit_method_comparison/`、`low_eta_analysis/`、`tdinn_q_only_comparison/`：此前已经归档的探索实验。

`generated_snapshots/duplicates/` 中的文件只是旧位置留下的重复成品，不应作为论文引用源。

## 历史模块独立运行入口

以下命令均从项目根目录运行，供需要恢复或探索对应旧模块时查阅，并非更新正式论文的推荐入口。生成目录已加入 `.gitignore`，但部分脚本会清空或覆盖模块输出；执行前应检查源码、依赖、参数和现有文件，先保护旧结果。本轮没有执行这些命令，也不保证历史入口与当前正式结果一致。

```powershell
python -B xian_control_comparison\xian_control_comparison.py
python -B c0_sensitivity\run_c0_sensitivity.py
python -B xian_control_comparison\effective_population_sensitivity\effective_population_sensitivity.py
python -B xian_control_comparison\threshold_landscape_analysis\threshold_landscape_analysis.py
matlab -batch "run('E:\work\draft\scenario1_threshold_landscape\run_all.m')"
```

正式全文复现应从 `reproducibility/run_all.ps1` 进入独立空输出目录。历史入口的旧复制位置不代表当前正式文件映射；不得据此将旧图或表直接复制入正式工程。更新正式稿须先按当前参数、实际指标、绘图适配关系和完整验收流程核查，再使用受控发布步骤；生成文件不等于已通过科学或视觉验收。

## 恢复原则

- 需要恢复某个归档模块时，先检查其是否仍被现行代码或论文引用，再移回原位置。
- 归档材料仍受 Git 管理，可使用 `git log --follow -- <path>` 查看移动前历史。
- 已删除的 AI 讨论稿和独立 `q_c` 凸性审查文件不在本目录中，但仍可从清理前的 Git 提交恢复。
- 本次整理不改写 Git 历史，因此归档前路径和已删除内容仍存在于旧提交中。
