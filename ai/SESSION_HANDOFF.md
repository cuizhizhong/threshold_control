# 新会话接续指引

**更新于 2026-10-26。** 每结束一轮修改，更新本文件第 1、3 节。

## 1. 当前状态

- 工作树 `E:\work\draft-submission-ready`，分支 `paper/submission-ready`。最近一轮为 NEW-4m（成本最优控制跳变结构入稿，N23，M0 `0c8512d` 与 M1–M4 两次本地提交，**未推送**）；NEW-4l 及此前各轮已推送。
- NEW-4l 后第 5 章编号有变：连续结构定理为定理 5.2（原 5.5），阈值单调性为命题 5.5（原 5.2），其证明在附录 A.12；与外部审阅或旧记录对照时注意换算。
- NEW-4m 在补充 S5.3 新增引理 S5.2 与命题 S5.3：任意权重下成本最优状态反馈至多跳变一次，$(r_{\rm cont},\hat r)$ 内跳变状态为 $2[\bar S+(S_c-\bar S)\sqrt r]$；正文只加引用句。$r>\hat r$ 时仅隔离段结束的位置（相切方程）与 $r_C$ 仍不入稿。来源推导在 `ai/成本最优/补充推导_20261026/`。
- 2026-10-26 清理了 `paper/tmp/` 与 `tmp/` 中的测试临时目录、截图和编译日志（均未入库）；文献核实证据、测试 XML、基准快照仍保留在原处。
- 中文稿：主稿 `paper/flatten_curve_analysis_cn.pdf` 38 页，补充材料 `paper/flatten_curve_supplement_cn.pdf` 24 页；`nr_audit` 全量测试 363 项通过（既有 353 项＋NEW-4m 新增 10 项）。
- 近几轮：NEW-4j（外部审阅意见收尾）、NEW-4k（理论与数值收尾）、NEW-4l（第 5 章重排）、NEW-4m（跳变结构入稿，记录见 `paper/revision_notes/NEW_4m_jump_structure.md`）。结论：理论已闭环，数值不需新计算，正文 9 幅图全部保留；中文稿进入定稿阶段。
- 理论重开条件（NEW-4k 计划 0.2 节）：实际使用的假设未写入陈述；证明步骤不成立或有反例；正文结论超出已证明范围；公式、证明与报告数值实质矛盾。

## 2. 读取顺序

1. `AGENTS.md`：唯一现行规则，Claude Code 会自动读取。重点看 N19–N21 与第 2、4、6 节。
2. `paper/revision_notes/STATUS.md`：表格第一行（最近一轮）和“遗留事项”。
3. `ai/NEW_4k_closeout_plan_20261022.md`：第 0 节总体判断、第 6 节推迟项、第 7 节不采纳理由。
4. `paper/revision_notes/NEW_4k_closeout.md`：最近一轮的实际修改与验证。
5. `ai/NEW_4i_review_revision_plan_20261021.md` 第 2 节：X1–X7 待处理清单。
6. `paper/revision_notes/NEW_author_inputs.md`：需要作者提供的信息。
7. 动稿件时再读相应的 `paper/sections/*.tex`、`paper/supplement_sections/*.tex`、`paper/appendices/*.tex`。

更早的背景只在需要时查：`paper/revision_notes/R1_storyline.md`（章节与标题方案）、`R1_framing.md`（主线）、`01_decisions.md`，以及 `NEW_4i/4j` 的计划和记录。

## 3. 待处理

- **X1–X7**（无回流假设与医疗负担的呈现，见上面第 5 项）：作者 2026-10-22 决定继续待处理，另行安排。其中包括摘要是否给“仅隔离控制最快、感染最少”加“被隔离的未感染者不返回”的限定。
- **推迟到英文稿（NEW-5，需作者启动）**：
  - 图 4 早期差异的局部放大或切换时刻标记；全套图的字号、字体与配色统一；
  - 表 2 显示精度；
  - 补充图精简（优先 S9，其次 S7，再考虑 S3、S5、S12 的低增量面板；S12 的控制时长与累计感染面板保留）；
  - 附录 A.11 证明的进一步分段；
  - 期刊声明（基金、利益冲突、数据与代码链接、作者与单位）。
- 外部审阅中**不采纳**的建议及理由见 NEW-4k 计划第 7 节、`NEW_4j_review_closeout.md` 末节，新会话不必重新讨论。

## 4. 工作约定与易踩的坑

- **授权**：每轮改稿前，由作者授权并在 `AGENTS.md` 末尾加一条 N 条款（下一条为 N24），计划写在 `ai/NEW_<轮次>_*_plan_<日期>.md`。推送只在作者明确要求时进行。
- **Python**：用 `E:/anaconda/envs/thesis/python.exe`，并设 `PYTHONIOENCODING=utf-8`；`conda run` 遇中文输出会报 gbk 编码错误。
- **编译**：`powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1`（用 PowerShell，不用 Git Bash）。Acrobat 打开 PDF 时会锁文件。
- **检查**（`--old` 用上一轮提交，如 `fd5fdaf:paper/flatten_curve_analysis_cn.tex`）：
  - `paper/tools/check_tex.py`：标签缺失必须为 0，消失的数字要登记去向；
  - `paper/tools/statement_diff.py --proofs`：附录中的证明不会被自动配对，改动要人工登记；
  - `paper/tools/rewrite_metrics.py`：只报告字数变化。
- **改了稿件 tex 之后**：先运行 `nr_audit/text_identity.py --refresh-current`（只刷新现稿内容哈希），再运行 `-m pytest nr_audit/tests -q -p no:cacheprovider --basetemp=paper/tmp/<轮次>/pytest_full`；`--basetemp` 的父目录要先建好，否则全部报错。
- **记录与提交**：写 `paper/revision_notes/NEW_<轮次>_*.md`（不超过两页），在 STATUS 表格首行加一行；提交时显式列出路径，附重新编译的两份 PDF，提交信息末尾加 Co-Authored-By 行。
- **文献**：新增文献须在线核对元数据（Crossref），并对照摘要或全文核对所支持的论断。
- **版面**：补充 S6 末有 `\FloatBarrier`（防止图 S12 跑进 S7），补充材料 `\printbibliography` 前有 `\enlargethispage`（防止末条参考文献单独成页）。改动后要检查这两处，以及正文第 6 章标题前的 `\Needspace`。
- **写作**：局限保持两段（AGENTS 4.3）；不出现“审稿人”“应要求”等字样；解释句只写定理或算例已支持的内容；操作性清零（$I$ 降到 1）是全文统一约定。

## 5. 新会话开场提示词（可直接复制）

> 先读 `ai/SESSION_HANDOFF.md`，再按其中第 2 节的顺序读文件，了解论文当前状态、待处理事项和工作约定。读完用几句话告诉我你理解的当前状态和待处理事项，然后等我下一步指示，先不要改任何文件。
