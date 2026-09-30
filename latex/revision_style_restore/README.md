# 原图内容与样式恢复记录

完成日期：2026-09-29。范围仅为当前 `latex` 工程中的图 9、10、14、16、18，以及表 2 的“含义”列单位。

## 交付与备份

- 主稿：`../flatten_curve_analysis_cn.tex`、同名 PDF，41 页。
- 新图：`../figures/style_restored/`，每幅有 PDF、SVG 和 300 dpi PNG；主稿引用这些新文件。
- 独立合图入口：`restore_figures.py`。没有覆盖原始研究模块的代码、原始图或 `revision_v4` 图像。
- 修改前主稿、PDF、参考文献、补充表源码及上一版合图：`before/`。
- 自动验证：`verify_revision.py`；碰撞误报复核：`review_collision_geometry.py`。
- 实际编译记录、字号/对齐/碰撞检查、原图与相关论文页渲染：`qa/`。

## 逐图处理及内容核对

本轮只恢复既有结果的呈现，不增加研究结论。图 10 展示控制函数与状态轨迹的对应；图 14 展示阈值与有效人口的两种改变方式；图 18 展示三个临界人口案例。均为确定性模型轨迹，原常规控制包络是参数范围，不是统计置信区间。

| 项目 | 修改 | 最终 PDF 页 |
|---|---|---|
| 图 9 | 保留原来的坐标区、线、散点和 a/b；只删顶部图例及两处英文标题，含义由原图注说明 | 23 |
| 表 2 | 仅删除含义列的“人”和日的负一次方单位；其余单元格、来源不动 | 23 |
| 图 10 | a：I；b：c；c：q；d：总累计；e：有效再生数。恢复原深浅蓝/灰色及 Times/STIX 样式和参考线；不恢复任何已删内嵌图 | 25 |
| 图 14 | 原图 20/21 左右组合，I 在上、q 在下。恢复两幅累计柱图、8 个平台投影点、8 个隔离率拐点、清零标记、峰值线、全部五个人口规模及八成员常规包络 | 33 |
| 图 16 | 原三条边界样式、三个切片交点、水平切片、等值线全部保留；图例右上角，保留 Stationary curve，等值线数字避开边界 | 35 |
| 图 18 | 原图 25/26/27 按三行排列，每行 I 左、q 右；恢复三幅累计柱图、9 个平台投影点、9 个隔离率拐点、清零标记与峰值线 | 38 |

图 14、18 的图注明确区分“隔离率拐点”与“拐点时刻在感染平台上的投影”，不把平台实心点称为感染曲线拐点。

为使窄列中的文字可读，图 14、18 的完整图例放入上方留白，固定阈值图例文字适当换行，累计内嵌图仍位于隔离率面板右上方并适当加宽。只调整画布、轴位置、文字尺寸和标注间距，没有对 PDF 非等比例拉伸，也没有替换字体家族、曲线配色、线型或删减标记。

### 累计柱图与原 PDF 逐项比对

| 来源 | 原 PDF 与新 PDF 均保留的柱值 |
|---|---|
| 原图 20 | 3,500；3,569；3,773 |
| 原图 21 | 945；2,097；5,016；10,784；15,410 |
| 原图 25 | 2,056；2,097；2,218 |
| 原图 26 | 7,072；7,211；7,620 |
| 原图 27 | 16,072；16,385；17,312 |

原图及新图 PDF 的文本检查已实际执行，结果保存在 `qa/verification.json`。

## 原代码与数据来源

- 图 10 继承 `xian_control_comparison/paper_plot_style.py`，根据 `xian_control_comparison.py::plot_results` 中相应五个坐标轴的原画法组合。轨迹和观测数据读取 `archive_unused/generated_snapshots/xian_control_comparison_main/`，启动/解除时间读取原 `xian_flat_control_details.csv`，不重新拟合。
- 图 14/18 直接读取并执行 `xian_dom/panels.py::panel_A` 和 `xian_dom/plot_B.py` 的原绘图语句，注入目标坐标轴，跳过原文件输出入口；使用原 `build_plot_series`、`compute_inflection` 和累计计算函数。
- 17 条阈值轨迹使用 `../revision_v4/data/` 的现存 CSV。由已保存的拐点恒等式恢复解析启动状态，不用稀疏采样近似替代控制律。
- 固定阈值图缺失的常规控制包络按 `compute_B.py` 原来的 8 个几何间隔人口、原函数与默认求解设置恢复；固定绝对初值为原 `panels.py` 的 `0.00100662823352`，全市 TDINN 参照也使用原函数。没有调用任何初值拟合入口，没有修改容差或模型参数。恢复缓存只写入本目录 `data/original_reference_cache.pkl`。
- 固定阈值内嵌图使用原 `cumulative_at_cached_clearance`；其结果与直接累计 CSV 有千分之一量级的既有积分差异，图上整数标签与原 PDF 完全相同，未将两种计算方式混换。
- 图 16 使用 `../revision_v4/data/phase_curves.npz` 的原网格及边界，恢复 `c0_sensitivity/run_c0_sensitivity.py` 的样式与切片交点。

`qa/original_artist_preservation.json` 在布局调整前后逐一比较原绘图对象的数据数组、颜色、线宽、线型、透明度、散点位置与颜色；五组原图的这些对象均未改变。仅放置及文字调整不参与此项数值对象比较。

## 实际验证结果与边界

1. 运行 `../build_paper.ps1`：补充材料两遍 XeLaTeX，主稿 XeLaTeX → Biber → XeLaTeX → XeLaTeX，成功生成 41 页主稿和原 3 页补充材料。
2. 最终日志没有未定义文献/交叉引用、Overfull、Underfull 或 Float too large。原模板仍有 Times/楷体及数学字体的替代警告，未为消除这些警告而修改模板。
3. 图号、标签和引用列表不变；参考文献文件及补充表源码与修改前 SHA-256 相同；五个 figure 块和表 2 单位以外的主稿文本逐字相同；上一版图像未覆盖。
4. 对齐检查实际执行：四幅多面板图 PASS，容差 1.5 pt；单面板图 16 不适用。内嵌轴由原绘图代码放在主坐标轴内部，不作为等宽主面板比较。
5. 五幅新图的 PDF 实际字形最小值分别为：图 9 为 8.00 pt，图 10 为 5.18 pt，图 14/18 为 5.04 pt，图 16 为 5.60 pt。图宽 451.44 bp，与论文通栏约 451.28 bp 一致；印刷缩放后仍不低于 5 pt。
6. 已检查全部指定图表所在页（23、25、33、35、38），并查看相邻页的页面缩略图；原图 20、21、25、26、27 与合图逐面板视觉对照。页 41 的 5 条参考文献完整显示。
7. 原始通用碰撞检查报告没有被隐藏或改写：图 9、16 自动 PASS；图 10、14、18 仍有几何误报，不能表述成“全部自动检查通过”。复核证据见 `qa/collision_geometry_review.json`：面板编号与曲线的提示来自未考虑 PDF 裁剪的轴外路径，已逐路径核实裁剪框不相交；峰值符号提示来自数学上下标合并框，720 dpi 裁剪已人工查看，字形未重叠；内嵌图白底边缘提示已逐页查看，数字、参考线和曲线无遮挡。
8. 通用静态检查偏好无衬线字体及另一种期刊栏宽。本轮按照用户明确要求保留原 Times/STIX、原模板栏宽，不为满足默认样式提示重做图形。没有声称符合某一特定期刊的全部投稿细则。

## 重现

在项目根目录执行（使用当前已有的 Python/TeX 环境）：

```powershell
$env:PYTHONUTF8='1'
E:\anaconda\python.exe -B latex\revision_style_restore\restore_figures.py
& latex\build_paper.ps1
$env:PYTHONPATH='E:\work\draft\tmp\figure_qa_deps'
E:\anaconda\python.exe -B latex\revision_style_restore\verify_revision.py
E:\anaconda\python.exe -B latex\revision_style_restore\review_collision_geometry.py
```

绘图入口还支持 `xian`、`dominance`、`phase` 参数。Python 重绘依赖原研究模块和当前科研绘图检查工具；仅编译 LaTeX 不需要运行 Python，所需新图 PDF 均已放在 `latex/figures/style_restored/`。
