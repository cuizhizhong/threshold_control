# 新会话接续指引

**更新于 2026-10-27。** 每结束一轮修改，更新本文件第 1、3 节。

## 1. 当前状态

- 工作树 `E:\work\draft-submission-ready`，分支 `paper/submission-ready`。最近五轮为 NEW-4m（跳变结构入稿，N23，`0c8512d`、`332091f`）、NEW-4n（删去时长约束、整理第 5 章与补充 S5，N24，`705c20e`、`4a396df`）、NEW-4o（图 8、图 S11 改为图 2 风格，N25，`697d2bc`）、NEW-4p（数值部分与图表重排，N26，`50edb4e`、`5ab02f4`、`dd0e888` 及记录提交）、NEW-4q（第 5 章陈述与证明的整理润色，N27，记录见 `paper/revision_notes/NEW_4q_section5_polish.md`）、NEW-4r（图 3 改为阈值取舍图，N28，记录见 `paper/revision_notes/NEW_4r_threshold_tradeoff.md`）与 NEW-4s（图 3 标题与图 4 风格，N29，记录见 `paper/revision_notes/NEW_4s_figures.md`），均为本地提交、**未推送**；NEW-4l 及此前各轮已推送。
- NEW-4p 后的结构（记录见 `paper/revision_notes/NEW_4p_numerics_layout.md`）：
  - 基准参数演示机制，西安参数做应用。图 2、图 3 在第 3 章（3.1 节末、3.4 节），基准参数写在图 2 图注；第 6 章“联合控制的数值结果”只用基准参数；西安参数的全部内容在第 7 章（7.1 参数表与拟合、7.2 控制组合、7.3 TDINN 参照、7.4 低阈值与退出、7.5 有效人口），策略过程图与对照表含成本最优控制。
  - 正文 9 幅图、5 张表：图 1 模型，图 2–3 第 3 章，图 4–6 第 6 章，图 7 拟合、图 8 西安控制组合、图 9 策略过程；表 1 四种控制（基准）、表 2 西安参数、表 3 西安控制组合、表 4 策略对照、表 5 附录敏感性。
  - 补充 8 幅图、5 张表：删去原表 S1、S2.3 节（原图 S4–S7）、原图 S9、原表 S3–S5。补充 S6.1 现为“人口缩放”。
  - 图 3、图 5–9 为图 2 风格（`nr_audit/plot_new4r_tradeoff.py`、`plot_new4p_figures.py` 与 `plot_xian_fig2_style.py`）。
  - NEW-4r：正文图 3 现为阈值取舍图（控制时长与成本对总累计新增感染）；原六面板图移为补充图 S2（`fig:sup:eta-summary`），与图 S1 配对，补充图原 S2–S7 顺延为 S3–S8。补充参考文献前的 `\enlargethispage` 已去掉（参考文献现完整在第 20 页）。
- 编号变化（与外部审阅或旧记录对照时注意换算）：
  - NEW-4l 后，连续结构定理为定理 5.2（原 5.5），阈值单调性为命题 5.5（原 5.2）。
  - NEW-4n 删去 5.4 节（原注记 5.8、命题 5.9、注记 5.10）和 6.6 节、原图 7，原图 8、9 现为图 7、8。
  - 附录现为 A.11 连续结构（含引理 A.1）、A.12 权重单调性、A.13 阈值证明。
  - 补充 S5 现为引理 S5.1（上集性）、命题 S5.2（$\hat r$）、引理 S5.3（内部并列）、命题 S5.4（跳变次数）。
  - NEW-4p 后：原图 8（策略过程）现为图 9，新增图 8（西安控制组合）；原表 1 拆为图 2 图注与表 2（西安参数），原表 2 拆为表 1（基准）与表 3（西安），原表 3 现为表 4；第 6 章原 6.3–6.5 节现为 6.2–6.4 节；补充图原 S8、S10、S11、S12 现为 S4、S5、S6、S7，补充表原 S2、S6–S9 现为 S1–S5。
- NEW-4m 在补充 S5.3 新增引理与命题（现为 S5.3、S5.4）：任意权重下成本最优状态反馈至多跳变一次，$(r_{\rm cont},\hat r)$ 内跳变状态为 $2[\bar S+(S_c-\bar S)\sqrt r]$；正文只加引用句。$r>\hat r$ 时仅隔离段结束的位置（相切方程）与 $r_C$ 仍不入稿。来源推导在 `ai/成本最优/补充推导_20261026/`。
- 2026-10-26 清理了 `paper/tmp/` 与 `tmp/` 中的测试临时目录、截图和编译日志（均未入库）；文献核实证据、测试 XML、基准快照仍保留在原处。
- 中文稿：主稿 `paper/flatten_curve_analysis_cn.pdf` 36 页，补充材料 `paper/flatten_curve_supplement_cn.pdf` 20 页；`nr_audit` 全量测试 384 项通过。
- 近几轮：NEW-4l（第 5 章重排）、NEW-4m（跳变结构入稿）、NEW-4n（删去时长约束）、NEW-4o（图 8、S11 风格）、NEW-4p（数值部分与图表重排）、NEW-4q（第 5 章润色）、NEW-4r（图 3 取舍图）。中文稿进入定稿阶段。
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
- **图表与声明（作者 2026-10-27 决定不再推迟到英文稿，在中文稿阶段处理）**：
  - 图 4 早期差异的局部放大：作者 2026-10-27 决定暂不做；
  - 字体配色：正文图 3–9 与补充图 S7（西安阈值扫描）已为图 2 风格（图 4 为 NEW-4s，`nr_audit/plot_new4s_figures.py`）；补充图 S1–S6、S8 是否跟进待作者决定（NEW-4p 计划 D10）；
  - 表格显示精度：表 1、表 3 已在 NEW-4p 统一（$J$ 两位小数、西安人数三位小数）；
  - 补充图精简：NEW-4p 已删原 S4–S7、S9；补充图 S8（西安热图）低增量面板的精简待定；
  - 审计脚本 `audit_baseline.py`、`audit_fit.py` 读取的稿件表格结构已变，需要重跑时须先按新表格调整（NEW-4p 记录“未改与遗留”）；
  - 期刊声明（基金、利益冲突、数据与代码链接、作者与单位），需作者提供信息。
  - 附录 A.11 的分段已在 NEW-4n 完成。
- 外部审阅中**不采纳**的建议及理由见 NEW-4k 计划第 7 节、`NEW_4j_review_closeout.md` 末节，新会话不必重新讨论。

## 4. 工作约定与易踩的坑

- **授权**：每轮改稿前，由作者授权并在 `AGENTS.md` 末尾加一条 N 条款（下一条为 N30），计划写在 `ai/NEW_<轮次>_*_plan_<日期>.md`。推送只在作者明确要求时进行。
- **Python**：用 `E:/anaconda/envs/thesis/python.exe`，并设 `PYTHONIOENCODING=utf-8`；`conda run` 遇中文输出会报 gbk 编码错误。
- **编译**：`powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1`（用 PowerShell，不用 Git Bash）。Acrobat 打开 PDF 时会锁文件。
- **检查**（`--old` 用上一轮提交，如 `fd5fdaf:paper/flatten_curve_analysis_cn.tex`）：
  - `paper/tools/check_tex.py`：标签缺失必须为 0（经授权删除的除外，此时该工具返回非零，后续命令要分开运行），消失的数字要登记去向；
  - `paper/tools/statement_diff.py --proofs`：附录中的证明不会被自动配对，改动要人工登记；
  - `paper/tools/rewrite_metrics.py`：只报告字数变化。
- **改了稿件 tex 之后**：先运行 `nr_audit/text_identity.py --refresh-current`（只刷新现稿内容哈希），再运行 `-m pytest nr_audit/tests -q -p no:cacheprovider --basetemp=paper/tmp/<轮次>/pytest_full`；`--basetemp` 的父目录要先建好，否则全部报错。
- **记录与提交**：写 `paper/revision_notes/NEW_<轮次>_*.md`（不超过两页），在 STATUS 表格首行加一行；提交时显式列出路径，附重新编译的两份 PDF，提交信息末尾加 Co-Authored-By 行。
- **文献**：新增文献须在线核对元数据（Crossref），并对照摘要或全文核对所支持的论断。
- **版面**：补充 S6 末有 `\FloatBarrier`（防止西安热图跑进 S7）；补充参考文献前原有的 `\enlargethispage` 已在 NEW-4r 去掉（版面变化后它使文献压到页码上）。改动后要检查补充材料末页的参考文献、S6 末的浮动体，以及正文第 6 章标题前的 `\Needspace`。
- **写作**：局限保持两段（AGENTS 4.3）；不出现“审稿人”“应要求”等字样；解释句只写定理或算例已支持的内容；操作性清零（$I$ 降到 1）是全文统一约定。

## 5. 新会话开场提示词（可直接复制）

> 先读 `ai/SESSION_HANDOFF.md`，再按其中第 2 节的顺序读文件，了解论文当前状态、待处理事项和工作约定。读完用几句话告诉我你理解的当前状态和待处理事项，然后等我下一步指示，先不要改任何文件。
