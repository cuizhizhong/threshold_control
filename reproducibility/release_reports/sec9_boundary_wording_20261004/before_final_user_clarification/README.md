# 第9节精确边界与参考直线：本轮核查记录

日期：2026-10-04。结论：批准范围内的局部订正、纯文案回归、正式编译和页面检查均已完成。未进行新的科学计算、渐近证明或图件重画。

## 1. 正式修改与保护

正式源码只修改 `latex/flatten_curve_analysis_cn.tex` 与 `reproducibility/paper_sync.py`。主稿有14项局部出版文案锚点，涉及第9.1、9.2、9.5节、图13图注及两处比较条件附录衔接：

- 应用情景沿用全市人口下拟合的同一个绝对初值，并取 `S0=N-I0`，不声称拟合初值天然独立于人口。
- 固定归一化初值时的精确规模不变性与人口上界商式保留；固定绝对初值的应用集合按实际成本、时长、峰值与严格触发条件定义。
- 保留四行边界公式的编号；其中成本、时长、触发三行改用实际指标。峰值水平线仍精确，图13中的三条参考直线按参考人口下的未取整比例解释。
- 无限时长应用上界由实际成本求根定义；有限时长上界取成本与时长允许上界的较小者，不解释为同时解两个等式，不增加一般唯一性结论。
- 原人口区间的显示数值保持，符号区间与取整区间间改用近似号；累计比较段及附录B的相关交点也明确为实际条件的数值交点。
- 约103天、102.91天及常规峰值比例约0.1047明确限定为全市参考人口下的计算值。

本轮备份：`reproducibility/backups/before_sec9_boundary_wording_20261004/`。其中12份文件保留修改前主稿/PDF、补充材料/PDF、辅助标签、模板、文献库、编译入口及相关文案源。`baseline.json` 记录8175项已有文件的大小、SHA-256及修改前Git状态。

实际检查确认：

- 4张正文表、3张补充表的完整源码（含表注）逐字不变；20幅正式图PDF的哈希不变。
- 所有已有证明、编号命题、能力限制补充及前轮8项审计分流文案不变。
- 97个编号数学环境的数量不变；只改批准的三行边界及人口区间的等号。
- 正文184个、补充材料3个标签的实际编号不变；引用键、文献库与唯一一份正文参考文献不变。
- 补充材料TEX逐字不变，其PDF仅由完整编译入口重新生成。
- 8175项保护检查无非白名单变化；原始输入、冻结包、外部核查包、历史结果及此前未提交改动保留。

完整逐项证据见 `verification_static.json`、`verification.json`；最终人工闭合与文件绑定见 `final_acceptance.json`。

## 2. 文案生成回归，而非科学复跑

`paper_sync.py` 增加纯函数 `population_comparison_prose(reference, fit, critical)` 和14项局部同步。计算接口、参数、验收阈值及既有科学调用不变，完整精度的输入字典与审计锚点保留。

回归输入仅来自已验收的 `reproducibility/results/20261003_release_final/`：`xian/reference.json`、`xian/fit.json`、`population/critical.json` 等已有文件。实际回归在本轮报告目录执行，禁止文件IO、子进程、科学模块导入及 `prepare_manuscript`；以本轮备份构造内存编辑器，14项局部替换与当前正式主稿逐字符一致。输入未改，输出可重复，旧8项审计分流文案及既有辅助函数保持。

实际命令（项目根目录）：

```powershell
reproducibility\.venv\Scripts\python.exe -B reproducibility\release_reports\sec9_boundary_wording_20261004\verify.py --phase static
reproducibility\.venv\Scripts\python.exe -B reproducibility\release_reports\sec9_boundary_wording_20261004\verify.py --phase complete
```

这里没有重新拟合、积分、求根或运行冻结底稿的完整生成入口。回归通过只认证上述局部出版文案；不认证整稿生成器能够从冻结版本恢复当前所有人工修订，不据此覆盖正式稿。

## 3. 实际编译与页面核查

实际运行正式入口三次，最终一次退出码为0，完整顺序为补充材料XeLaTeX两遍，再执行正文XeLaTeX → Biber → XeLaTeX → XeLaTeX：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File latex\build_paper.ps1
```

最终正文47页（备份46页），补充材料3页。文字增加导致自然分页，章节与公式编号未变。正文参考文献20条，在第46–47页完整显示。最终日志保存在 `build_stdout.log`、`build_stderr.log`；前两次日志亦保留。

没有未定义引用、缺字、Overfull溢出、浮动体错误或Biber告警。保留以下非阻断提示，不称为“零警告”：

- 正文1725–1726行累计比较段的一条 `Underfull \\hbox (badness 2376)`。已实际查看最终第35页，文字可读，无越界、遮挡或异常大块空白。
- Perl不支持环境中的 `C.UTF-8`，回退到 `C`；编译流程仍成功，原始stderr保留。

用Poppler以120dpi渲染全部50页，保存在 `qa/`。主代理实际查看全部7张总览，以及正文31–36、42–47页和补充材料1–3页的单页图（15张）；独立核查者查看全部总览，以及正文30–40、42–47页和补充材料1–3页的单页图（20张）。修改页、相邻页、图13及参考文献均完整，无新增裁切或编号碰撞。正文第34页表4引用已经并入完整句，不再形成下一页孤立短尾。

独立记录见 `manual_review_agent.json` 和 `independent_verification_notes.md`。`verification.json` 中的主代理人工状态是核查脚本生成时的待完成快照；最终人工状态以 `final_acceptance.json` 为准。此前第二次编译的报告和渲染以 `*_before_short_tail_fix.json`、`qa_before_short_tail_fix/` 留存，未改写历史记录。

## 4. 未修复事项：图13标记的数据绑定

状态：待后续核查，不标记为已修复。本轮没有重画图13，未修改其绘图代码、数据或正式图文件。

`xian_dom/dom_pretty.py` 第150–155行的圆点、方点由参考比例或弧线插值构造；清零方点仍包含旧硬编码人口 `3969.7`。`reproducibility/population.py` 的绘图适配替换参数和弧数据块，但未替换该后续标记定义。既有正式结果 `population/representative_summary.csv` 的 `dominance_fixed_eta0` 使用人口 `3973.3552578867098`、阈值100。因此，图13标记不能被声称为图14各案例参数的逐点精确绑定。

本輪仅将图注改为两类比较的示意，并把具体轨迹参数指向图14，撤回原精确对应表述。上述数字只摘录已有源码/结果，未产生新计算。未来如要修复，应统一标记与代表案例的实际指标来源，再单独核查导出图；不由本轮文案回归冒充完成。

## 5. 范围结论

本轮接受状态为局部订正完成，不是新一轮全文科学复现或数学证明审查。没有加入云端截距、渐近展开、新数值、新文献、算例或附录证明；没有使用Nature系列技能，没有提交或推送Git。Git HEAD保持 `436dedd733a30cc033c51c8362ef2ca80c532b82`。
