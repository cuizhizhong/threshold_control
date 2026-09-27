# 非当前主线材料归档

本目录保存当前论文主线不再直接使用、但仍有复核或恢复价值的代码、数据、图表和运行快照。
归档文件不属于活动运行路径；主论文定稿图表仍位于根目录 `figures/` 与 `table/`。

## 目录说明

- `generated_snapshots/`：清理前各实验模块的可复现输出，包括情景一 MATLAB 图谱、
  西安主比较、有效人口敏感性、二维阈值图谱和 `c0` 敏感性结果。
- `inactive_scope/scenario2/`：当前暂不研究的情景二、情景三论文草稿、代码和表格。
- `inactive_scope/multicity_raw_data/`：广州、海南、辽宁、乌鲁木齐和扬州原始数据。
  当前活动数据目录只保留西安数据。
- `superseded/`：已由现行模块替代的占优区域实现、论文不再引用的图片、早期扫描数据和旧表格。
- `fit_method_comparison/`、`low_eta_analysis/`、`tdinn_q_only_comparison/`：此前已经归档的探索实验。

`generated_snapshots/duplicates/` 中的文件只是旧位置留下的重复成品，不应作为论文引用源。

## 重新生成活动输出

以下命令均从项目根目录运行。生成目录已经加入 `.gitignore`。

```powershell
python -B xian_control_comparison\xian_control_comparison.py
python -B c0_sensitivity\run_c0_sensitivity.py
python -B xian_control_comparison\effective_population_sensitivity\effective_population_sensitivity.py
python -B xian_control_comparison\threshold_landscape_analysis\threshold_landscape_analysis.py
matlab -batch "run('E:\work\draft\scenario1_threshold_landscape\run_all.m')"
```

重新生成的过程输出不会自动覆盖根目录的论文定稿图表。若要更新论文图表，应先核对参数、
验证结果和文件映射，再明确复制到 `figures/` 或 `table/`。

## 恢复原则

- 需要恢复某个归档模块时，先检查其是否仍被现行代码或论文引用，再移回原位置。
- 归档材料仍受 Git 管理，可使用 `git log --follow -- <path>` 查看移动前历史。
- 已删除的 AI 讨论稿和独立 `q_c` 凸性审查文件不在本目录中，但仍可从清理前的 Git 提交恢复。
- 本次整理不改写 Git 历史，因此归档前路径和已删除内容仍存在于旧提交中。
