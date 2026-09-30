# 图表改排（v4 优先）

本轮以用户调整后的 v4 为准，v3 用于补充图表安排、数据保留和核查细则。没有改动模型、拟合目标、控制律或理论证明。

## 成品与重新编译

- 主稿：../flatten_curve_analysis_cn.tex、同名 PDF（41 页）。
- 补充表：../flatten_curve_supplement_cn.tex、同名 PDF（3 页，S1–S3）。
- 在 latex 目录运行：powershell -ExecutionPolicy Bypass -File .\build_paper.ps1
- 请先生成补充材料的 aux，再编译主稿。构建脚本已包含此顺序，以及主稿的 xelatex → biber → xelatex → xelatex。
- 主稿仍使用本目录原 elegantpaper.cls 和 references.bib。不要单独复制 tex 而遗漏 figures、模板或参考文献。

## 改排与复核

- old_to_new_figures.md、old_to_new_tables.md：原编号对应关系。
- validation_report.md：实际检查、保留条件与未解决的既有数值精度问题。
- changed_files.txt：交付文件范围。
- before/：本轮开始时的原稿、PDF、参考文献与完整表格源文件，不是另一份待用主稿。
- data/：本轮绘图缓存、原实验完整表格输出。
- qa/final_render/：最终 PDF 的全页渲染图；上级其他渲染目录为过程检查记录。
- ../figures/revision_v4/：六份新图的 PDF、SVG、PNG。
- plot_revisions.py：Python 绘图入口，不调用初值拟合。旧图缺少轨迹缓存时，使用原研究模块函数及原参数恢复轨迹，并将缓存写入本目录。
- verify_revision.py：源文、数值表、PDF 渲染与图稿审计。依赖 PyMuPDF、Pillow 和本机 nature-figure 审计脚本；绘图另需 numpy、pandas、scipy、matplotlib 与项目原研究模块。实际运行使用 E:\anaconda\python.exe；临时 QA 依赖位于 E:\work\draft\tmp\figure_qa_deps。

主稿图文件 2、8、9、10（按修改前编号）的 SHA-256 与 includegraphics 尺寸选项均未改变；作者此前调整的图 8、9 图注也保留。旧的 latex_theory 删除状态未触碰。

