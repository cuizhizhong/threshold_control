# 当前论文的全文复现工程

唯一正式稿为 `../latex/flatten_curve_analysis_cn.tex`，补充材料为同目录
`flatten_curve_supplement_cn.tex`。`../ai/threshold_control_reproducible_release_20261002/`
保持原样；导入前的主稿、PDF、文献、模板和图件保存于 `backups/before_import_20261002/`。

本工程不使用任何 Nature skills，不修改历史实验和原始 Excel。原绘图语句、字体、配色、
线型、布局、内嵌图和标记继续使用。数值修正必须有计算来源，不能为匹配旧数字而调整模型。

版本控制完整保留冻结包及已汇集的结果/验收日志；`.gitattributes` 禁止这些文件自动换行转换，确保克隆后的字节校验不受 `core.autocrlf` 影响。本机环境、完整运行目录和备份不提交、不删除。验收记录中的 `git_writes=false` 描述计算/发布入口本身，后续用户单独授权的 Git 提交不改写这些历史记录。

## 环境与运行

以下命令均从项目根目录执行。本轮实际验收 Python 3.12.8，其他 Python 版本尚未验收。
图件导出实际验收 MATLAB R2025b / Symbolic Math Toolbox 25.2；旧 MATLAB 导出接口不在本轮兼容性保证内。
Windows PowerShell，需 MATLAB（含 Symbolic Math Toolbox）、XeLaTeX、Biber、
PowerPoint（导出可编辑模型图）和论文原有 Windows 字体。Python依赖锁定于 `requirements.txt`。
软件入口从 PATH 发现，也可以显式传 `-Python`、`-Matlab`；不依赖私人技能目录。
图 1 的 COM 导出只关闭本次打开的图源；不退出先前已运行的 PowerPoint，也不关闭其他文档。
实际 Python/TeX/字体记录见 `environment.json`；MATLAB、Symbolic 和 PowerPoint 的本轮版本来源汇总见 `release_reports/software_versions.json`。

```powershell
python -m venv --system-site-packages reproducibility/.venv
reproducibility/.venv/Scripts/python.exe -m pip install -r reproducibility/requirements.txt
powershell -ExecutionPolicy Bypass -File reproducibility/run_all.ps1
```

总入口默认运行两次，各使用从零创建的隔离工作区。数值链条是：
原始Excel → 同一拟合/积分设置 → 未取整TDINN参照 → 西安和人口扫描 → 原样式出图。
小人口 MATLAB 图谱、拐点及联合控制另有独立入口。旧生成CSV/NPZ/pickle不复制到新工作区，
新运行内部缓存可以供绘图使用。正式结果中的输入、来源代码、适配、环境和字体均有哈希记录。

当前总入口不会自动覆盖正式稿；编译产物和新图在运行目录中，必须完成数值对账和人工页面
审查后才发布。失败返回非零，失败状态与部分输出保留，不生成虚假的“完成”报告。

正文同步以冻结交付包为底稿，而不是反读正式稿后猜测替换。发布后可以再次复跑同一研究版本；
若以后直接修改正式 TeX 的实质内容，需要同时版本化底稿与同步规则，否则这些新编辑不会
自动进入下一次复现输出。入口不自动覆盖正式文件，因此不会默默丢失手工修改。

## 文件分工

- `bootstrap.py`：源码/原始输入隔离，环境与来源记录。
- `configuration.md`、`configuration_index.json`：集中列出固定参数、拟合/派生结果和实际容差的权威来源；索引本身不是新的可编辑运行配置。
- `xian.py`、`population.py`、`c0.py`：统一数值口径和下游比较。
- `joint.py`：完整候选比较、积分误差、真实时间开环的完整三阶段核查。
- `matlab_stage.m`、`figures.py`：原科学模块与最终图件适配，不调用旧清理/覆盖入口。
- `plotting_checks.py`：项目自包含的几何、科学对象与PDF检查。
- `registry.py`：20图、4正文表、3补充表和理论/数字陈述对应清单。
- `paper_sync.py`：有明确计算来源的正文/表格同步及旧新值记录。
- `build.py`、`compare_runs.py`：完整编译、PDF渲染和两次独立复现比较。
- `matlab_fixed_graphics.m`、`matlab_export_deterministic.m`、`finalize_matlab_figures.py`：独立场景导出、机械锚点锁定与新鲜输出封装，不改科学计算；图 2 保持原感染人数刻度，图 4 按原虚线节距用 600 dpi 无损图像型 PDF 输出。原脚本/历史图件不覆盖，具体边界见验收报告。
- `publication/publish_artifacts.py`：人工页面核查后回核实际 PDF/TeX/20图件和来源哈希、重新严格对比，再调用 `publish_verified.py`；正式目录重编译和48页渲染对照通过后记录发布。发布工具单独留源码摘要，不改变科学运行版本。
- `publication/collect_results.py`：正式发布通过后，将本轮未取整 CSV/JSON/NPZ、两轮环境和检查报告集中复制到 `results/<运行版本>/` 和 `release_reports/<运行版本>/`，并保存根索引。汇集副本不是下一轮计算输入，不覆盖既有汇集目录。

## 验收边界

`source_manifest.json` 证明输入及源码版本，不能证明数学命题或临床解释。
`registry.json` 区分静态追溯、供应方记录、本机计算和正文实际对账。
两次运行的数值和图件比较不代替人工PDF审查；PDF元数据不同不算数值差异。
17位CSV用于浮点往返，不表示全部尾数均已认证。

理论部分保留公式、定理和证明来源；数值测试不能代替独立数学证明审查。
能力受限、权重变化、真实ICU占用、回流、延迟和效率前沿仍是后续研究，不在此处伪装成已完成。

最终验收状态见 `validation_report.md`；后续扩展见 `future_plan.md`。若验收报告尚未生成
或存在未通过项，不能称全文复现完成。

2026-10-03 本机正式验收版本为 `runs/20261003_release_final`：两个空目录完整运行、84 份数值文件严格比较、20 幅图在 120 dpi 下逐像素一致，正式正文 45 页及补充材料 3 页重编译和实际页面审阅完成。当前研究版本的未取整结果在 `results/20261003_release_final/`，证据在 `release_reports/20261003_release_final/`；总索引为 `release_reports/final_acceptance.json`。理论证明与临床阈值认证不在此项数值验收结论内。

显式发布须已有真实 `manual_review_root.json`，不能由自动编译日志伪造人工记录。
使用 `publication/publish_artifacts.py --run-directory <双跑总目录>`；同一运行为一次性发布，
再次发布会拒绝已变化的正式稿。若发布阶段失败，可能留下已复制文件，须查看失败记录
的 `partial_publication`、`changed_targets` 和 `recoverable_backups`，不要把失败理解为正式稿未变。

发布完成后才运行 `publication/collect_results.py --run-directory <同一双跑总目录>`。
失败的计算、比较及检查记录保留在各自运行目录，不因随后成功而改成通过。
