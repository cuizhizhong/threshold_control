# 第六轮修订：术语、导数记号和表格格式

本版以上一轮 `flatten_curve_analysis_cn_connected.tex` 为基础，不改章节顺序、模型、定理结论或数值结果。

## 文件

- `flatten_curve_analysis_cn_notation.pdf`：完整阅读版，49页。
- `flatten_curve_analysis_cn_notation.tex`：原 ElegantPaper 工程的主稿。
- `拐点分析两表预览.pdf`：从完整阅读版第18页提取的两表所在页，含少量上下文。
- `拐点分析两表替换稿.tex`：两表的 LaTeX 代码，保留原表格标签。
- `修改说明.md`：本轮修改说明。
- `changes_v5_to_v6.diff`：与上一版主稿的逐行差异。
- `修改记录.json`：替换记录、结构和编译检查。
- `此前待确认的数学问题.md`：沿用此前独立列出的数学问题；本轮没有补证。
- `原工程表格补丁/`：沿用上一版的外部表格文件，内容未改。
- `standalone/`：独立编译的阅读版源文件、原图和参考文献。

## 放回原工程

将主稿与 `theory_context_references.bib` 放入原主文件目录，沿用原 `elegantpaper.cls`、`references.bib`、图和表。此前已应用过表格补丁的，无需再次更改；未应用的，将 `原工程表格补丁/` 的文件放入原 `table/` 目录。

按原环境运行：

```text
xelatex flatten_curve_analysis_cn_notation.tex
biber flatten_curve_analysis_cn_notation
xelatex flatten_curve_analysis_cn_notation.tex
xelatex flatten_curve_analysis_cn_notation.tex
```

## 独立编译阅读版

进入 `standalone/` 后运行：

```text
xelatex paper_preview.tex
biber paper_preview
xelatex paper_preview.tex
xelatex paper_preview.tex
```

完整PDF由此独立排版文件生成，而非在原 ElegantPaper 模板中编译。正文与主稿相同，差别仅为版式、图表资源路径和参考文献文件名。未附字体文件。

## 核查范围

已检查源代码中的标签、引用和环境配对，并检查编译后的版面。偏导数记号展开后，所有编号公式环境均与原式逐一比对；统一记号并忽略排版空白后，表达式一致。两张表只转置、统一参数次序和符号表示；固定N时，原表2关于theta的符号换列为关于eta的符号。

本次没有重新运行拟合或数值实验，也没有完成对原稿全部数学结论的证明审查。摘要和引言仍为原稿占位内容。
