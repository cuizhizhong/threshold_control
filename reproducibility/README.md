# 当前论文的全文复现工程

唯一正式稿为 `../latex/flatten_curve_analysis_cn.tex`，补充材料为同目录
`flatten_curve_supplement_cn.tex`。`../joint_control/threshold_control_reproducible_release_20261002/`
保持原样；导入前的主稿、PDF、文献、模板和图件保存于 `backups/before_import_20261002/`。

2026-10-04 的来源迁移只移动冻结目录并同步索引，不改其内容；旧验收中的 `ai/threshold_control_reproducible_release_20261002/` 映射到上述新目录，历史记录不改写，见 [来源整理核查](release_reports/source_relocation_20261004/README.md)。同日随后实施的联合数值整合另立活动模块、源码版本及新验收，不能与目录迁移混为一轮科学复跑。

2026-10-04 联合整合稿已实际完整编译为正文51页、补充材料3页，含24幅图、5张正文表及3张补充表；新增页面已实际预检。整合前47+3页、旧科学依据 `20261003_release_final` 及第9节局部订正记录保持原样，见 [订正核查](release_reports/sec9_boundary_wording_20261004/README.md)。新增活动模块第三批 `runs/joint_integration_20261004/run_5` 与 `run_6` 已分别实际完成 A–D 并通过逐任务科学检查；双跑比较、分阶段正式工作副本及发布状态另行记录，不倒写旧45+3页验收。前两批失败和诊断保留。只核对并局部提取AI候选材料，不以整稿、预览或“正式版”文件名证明发布。

本工程不使用任何 Nature skills，不修改历史实验和原始 Excel。原绘图语句、字体、配色、
线型、布局、内嵌图和标记继续使用。数值修正必须有计算来源，不能为匹配旧数字而调整模型。

版本控制完整保留冻结包及已汇集的结果/验收日志；`.gitattributes` 禁止这些文件自动换行转换，确保克隆后的字节校验不受 `core.autocrlf` 影响。本机环境、完整运行目录和备份不提交、不删除。验收记录中的 `git_writes=false` 描述计算/发布入口本身，后续用户单独授权的 Git 提交不改写这些历史记录。

## 环境与运行

以下命令均从项目根目录执行。本轮实际验收 Python 3.12.8，其他 Python 版本尚未验收。
旧20图导出的已验收环境为 MATLAB R2025b / Symbolic Math Toolbox 25.2；新增联合Python图不调用MATLAB。旧 MATLAB 导出接口不在兼容性保证内。
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

旧研究版本的生成以冻结交付包为底稿；新增联合整合版使用 `manuscript_versions/current.json` 所选受控稿源，来自当前本地整合稿而非AI候选整稿。冻结包本身不可改写。受控清单存在时不允许退回冻结稿；正文同步在唯一的 `JOINT_EXTRA` 标识块生成新文案，并保持能力限制、审计分流、第9节和已有证明。后续实质编辑仍须另立版本并批准，不能自动反读已变化的正式稿。是否完成完整生成回归以本轮报告为准，入口不自动覆盖正式文件。

新增联合内容的独立入口如下；它不重拟合西安、不重跑既有MATLAB图，旧图和旧科学证据均明确继承。需先有批准的受控稿源，输出目录必须全新：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File reproducibility/run_all.ps1 -Scope joint-extra
```

该入口独立运行两次新模块、生成新图与完整稿件、编译并比较两轮；自动成功仍不替代全部页面的人工审阅。原默认 `-Scope all` 使用同轮上游参照，两个范围不能统称整稿科学复跑。

本轮允许先从两个全新 `run_*/joint_extra/` 目录独立执行 `joint_extra/run.py --mode compute`，再承接同一运行进行出版后处理。后处理不重算、不复制第一轮科学结果到第二轮，不允许覆盖已经后处理过的运行；批准稿源必须先建立。

```powershell
reproducibility/.venv/Scripts/python.exe -B reproducibility/postprocess_joint_extra.py --output <本轮总目录>/<新运行A> --check-only
reproducibility/.venv/Scripts/python.exe -B reproducibility/postprocess_joint_extra.py --output <本轮总目录>/<新运行A>
reproducibility/.venv/Scripts/python.exe -B reproducibility/postprocess_joint_extra.py --output <本轮总目录>/<新运行B>
```

该入口核对计算期 `input_manifest.json` 的四份科学源码哈希、两份指定输入、锁定验收规则和软件版本，再建立工作副本、生成新图/文案、编译及登记。完整出版源码的 `source_manifest.json` 明确标为科学计算完成后的快照；不能说它在科学计算开始前已经锁定。后处理前后全部科学输出逐文件哈希必须不变。两轮数值、图件及文案比较仍需单独执行 `compare_runs.compare` 并实际审阅页面，单轮后处理成功不表示完成双跑验收。

若同一总目录保留了失败的早期运行，不更名、不覆盖，也不复制新结果填回旧编号。两个新运行分别后处理通过后，显式选择实际目录（以下名称只是示例），再比较：

```powershell
reproducibility/.venv/Scripts/python.exe -B reproducibility/run_selection.py --run-directory <本轮总目录> --runs run_5 run_6
reproducibility/.venv/Scripts/python.exe -B reproducibility/compare_runs.py --run-directory <本轮总目录>
```

`accepted_runs.json` 一次性锁定两个不同目录、验收报告哈希、共同源码/稿源/输入身份。缺失、失败或身份不一致时拒绝选择；选择后报告或输入改变则拒绝载入。发布、重新比较和结果汇集均读取实际所选名称，不暗中使用 `run_1/run_2`。从全新总目录执行公开 `run_all` 时，入口在两轮机器验收完成后自动明确建立选择清单；这仍不是人工页面验收。

## 文件分工

投稿正文与工程审计记录的分工见 [数值设置、收敛证据与历史程序对账](manuscript_audit_notes.md)。正文和补充表保留科研结果及必要的精度边界；旧容差、旧初值、历史输出及文件导航集中在该说明，原始验收材料不改写。S2 的清零累计容差差异不等于整张窗口表已逐项收敛。

- `bootstrap.py`：源码/原始输入隔离，环境与来源记录。
- `configuration.md`、`configuration_index.json`：集中列出固定参数、拟合/派生结果和实际容差的权威来源；索引本身不是新的可编辑运行配置。
- `xian.py`、`population.py`、`c0.py`：统一数值口径和下游比较。
- `joint.py`：完整候选比较、积分误差、真实时间开环的完整三阶段核查。
- `matlab_stage.m`、`figures.py`：原科学模块与最终图件适配，不调用旧清理/覆盖入口。
- `plotting_checks.py`：项目自包含的几何、科学对象与PDF检查。
- `registry.py`：按批准稿源的标签及资产路径建立图表和理论/数字清单，新增图插入后不按旧图号猜证据。
- `manuscript_version.py`、`manuscript_versions/`：活动稿源、旧科学参照与旧图哈希、批准任务和实际打印宽度；原冻结包保持原样。
- `joint_extra/`：本轮四策略、有限能力、二次权重及成本—时长计算和纯文案生成，逐任务通过后才进入对应正文图表。
- `postprocess_joint_extra.py`：首次承接同一运行的已完成科学结果；严格身份核对后执行图文、编译及索引，不重新计算。
- `run_selection.py`：显式选择两个真正通过机器验收的独立运行并锁定共同身份；失败旧运行留在原处，不改编号。
- `paper_sync.py`：有明确计算来源的正文/表格同步及旧新值记录。
- `build.py`、`compare_runs.py`：完整编译、PDF渲染和两次独立复现比较。
- `matlab_fixed_graphics.m`、`matlab_export_deterministic.m`、`finalize_matlab_figures.py`：独立场景导出、机械锚点锁定与新鲜输出封装，不改科学计算；图 2 保持原感染人数刻度，图 4 按原虚线节距用 600 dpi 无损图像型 PDF 输出。原脚本/历史图件不覆盖，具体边界见验收报告。
- `publication/publish_artifacts.py`：人工页面核查后回核实际 PDF/TeX、批准标签对应的全部图件和来源哈希、重新严格对比，再调用 `publish_verified.py`；正式目录重编译和全部页面的渲染对照通过后记录发布，按该版本实际页数核查。发布工具单独留源码摘要，不改变科学运行版本。
- `publication/collect_results.py`：正式发布通过后，将本轮未取整 CSV/JSON/NPZ、两轮环境和检查报告集中复制到 `results/<运行版本>/` 和 `release_reports/<运行版本>/`，并保存根索引。汇集副本不是下一轮计算输入，不覆盖既有汇集目录。

## 验收边界

`source_manifest.json` 证明输入及源码版本，不能证明数学命题或临床解释。
`registry.json` 区分静态追溯、供应方记录、本机计算和正文实际对账。
两次运行的数值和图件比较不代替人工PDF审查；PDF元数据不同不算数值差异。
17位CSV用于浮点往返，不表示全部尾数均已认证。

理论部分保留公式、定理和证明来源；数值测试不能代替独立数学证明审查。
正文给出仅隔离与联合能力界限的理论判据；新活动模块已经分别复跑两个参数案例的四策略、两个有限能力代表点、有限权重网格和有限κ支持点。只声称各已存验收记录支持的范围：数值实根比较不是严格根隔离，有限相图不是全参数解析分类，支持点及连线不是完整效率前沿。真实ICU占用、回流及延迟未纳入当前模型或本轮新增证据；逐任务科学通过、重复性、出版文案和页面核查分别记录。

第9节应用采用固定绝对初值 `I0`、`S0=N-I0`，集合成员按实际 `J`、`Delta t` 和严格触发条件判断；固定归一化初值的精确理论、参考人口下的近似直线及应用求根值必须区分。现有求根值仍作候选界值，连续人口允许区间及 `fig:dom`（整合前图13）案例标记绑定未认证。待办依据和已有输出范围见 [第9节订正核查](release_reports/sec9_boundary_wording_20261004/README.md) 第4–5部分，本轮文案回归不替代该科学核查。

最终验收状态见 `validation_report.md`；后续扩展见 `future_plan.md`。若验收报告尚未生成
或存在未通过项，不能称全文复现完成。

2026-10-03 本机正式验收版本为 `runs/20261003_release_final`：两个空目录完整运行、84 份数值文件严格比较、20 幅图在 120 dpi 下逐像素一致，正式正文 45 页及补充材料 3 页重编译和实际页面审阅完成。当前研究版本的未取整结果在 `results/20261003_release_final/`，证据在 `release_reports/20261003_release_final/`；总索引为 `release_reports/final_acceptance.json`。理论证明与临床阈值认证不在此项数值验收结论内。

显式发布须已有真实 `manual_review_root.json`，不能由自动编译日志伪造人工记录。
使用 `publication/publish_artifacts.py --run-directory <双跑总目录>`；新版发布/汇集记录位于 `release_reports/<运行版本>/publication/`，旧根验收清单不覆盖；同一运行为一次性发布，
再次发布会拒绝已变化的正式稿。若发布阶段失败，可能留下已复制文件，须查看失败记录
的 `partial_publication`、`changed_targets` 和 `recoverable_backups`，不要把失败理解为正式稿未变。

发布完成后才运行 `publication/collect_results.py --run-directory <同一双跑总目录>`。
失败的计算、比较及检查记录保留在各自运行目录，不因随后成功而改成通过。
