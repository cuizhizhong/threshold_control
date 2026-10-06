# 阶段 0：正式稿迁移基线

- 执行日期：2026-10-06。
- 基线标签：`pipeline-final-20261006`，已推送并核对远端。
- 清理前提交：`8537652db6d71ee145a0012d586b23fc195fae85`。
- 当前提交：`8470044`（新规则、README 与 `paper/` 初始文件提交；本记录在迁移提交前生成）。
- 本阶段不修改论文内容，不运行科学计算。

完整运行 `powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1` 后的最后两行：

```text
flatten_curve_supplement_cn: 5 页；undefined 0 处；multiply defined 0 处；超过 10pt 的 Overfull hbox 0 处
flatten_curve_analysis_cn: 51 页；undefined 0 处；multiply defined 0 处；超过 10pt 的 Overfull hbox 0 处
```

`check_tex.py` 的输出结论：

```text
标签缺失 0，悬空引用 0，数字缺 0、增 0；报告：paper\revision_notes\00_check.md
```

各节汉字数与限定性词语计数见 `00_check.md`。两份稿件均为 756 个数值字面量；重复标签和缺失文献键均为 0。bib 中未被两份稿件引用的条目为 `ShaanxiHealth2022`、`Zhang2026Behavior`。

## 原字节与页面核对

主稿、补充材料、参考文献、模板和 24 幅图直接迁移；两份 tex 快照用文件复制保存。主稿与补充材料的源文件、快照 SHA256 分别完全一致：

| 文件 | 迁移前后 SHA256 |
|---|---|
| `flatten_curve_analysis_cn.tex` | `cfd174f05f7a0f3a92a12097eadee50b7712e066f34c8e15d6102f85f299343c` |
| `flatten_curve_supplement_cn.tex` | `b048368f95155b5cea425e3acdeed75f0a110bb11ac0fea12709c29e15216ab5` |
| `references.bib` | `def94793ffc84d460932ac6eb5965bfe0d90c2d1102a6d5410e4f921e778ca33` |
| `elegantpaper.cls` | `bf80b5bb9061f11010b4595cd1bc443defe54fb093283ecf864c800371ad4b51` |

迁移前后两个 PDF 的全部 56 页以 Poppler 在 96 dpi 下渲染，逐页像素和文本比较均无差异。另实际查看正文第 1、28、37 页及补充材料第 1、5 页，未发现迁移引入的排版问题。渲染和机器检查的临时记录在本地 `tmp/cleanup_20261006/`，不纳入版本控制。

## 与手册的差异及后续清理边界

手册写“正文 51 页、补充材料 3 页”；当前基线提交的补充材料已经是 5 页。本轮迁移前后均为 51＋5 页，以实际文件和本轮编译为准，不为匹配旧页数修改 tex。

`latex/` 迁移后剩余 459 个受版本控制文件按清单删除。磁盘上留下的 19 个文件均为手册明确列出的编译中间产物，检查路径后删除该目录。

下一步仅删除手册任务 B 的受版本控制路径。清理前已对拟保留的 15 个 Python 文件实际执行 AST 导入检查，未发现对待删模块的导入；清理后再次核对。未跟踪文件、本地忽略目录及 `reproducibility/.venv` 按手册保留。24 幅图的 PDF 属于迁移的源图件；两个编译生成的整稿 PDF 由 `paper/*.pdf` 忽略，不提交。
