# SUB 投稿准备：本地分步执行计划

版本：2026-10-19。依据 `paper/revision_notes/merge_submission_plan.md`（下称合并方案）。适用于作者本机的三个 git worktree：`E:\work\draft`（`main`）、`E:\work\draft-nr`（`paper/no-return-focus`）、`E:\work\draft-return`（`research/return-effects`）。

## 0. 用途与边界

本计划把“无回流主稿修订已完成”推进到“英文稿投出”。共七步：SUB-0 由作者在 PowerShell 中手动执行（分支合并），SUB-1 至 SUB-6 交给本地 Code，一步一个会话。

本阶段不做（沿用 NR 计划 1.3 节的冻结范围）：

- 不新增研究、计算或图。SUB-3b 的图表脚本只重跑已有计算，并与现有结果对照。
- 不改定理类陈述的数学含义。
- 不把回流章并入本稿。命题 R3、36 条指数回流轨迹全表与释放数值留到返修（第 6 节）。
- 不重画正式图。图 1 的标注在英文稿阶段由作者决定。

## 1. 步骤总览

| 步骤 | 执行者 | 任务 | 主要交付 | 验收 |
|---|---|---|---|---|
| SUB-0 | 作者 | 本地合并：`main` 快进到无回流版，引入 `r7_return/` | 推送后的 `main` | G-S0：编译通过，主稿 34 页、补充 18 页 |
| SUB-1 | Code | 合并登记；`AGENTS.md`、`STATUS.md` 切换到投稿准备阶段 | `SUB_1_rules.md` | 作者读 `AGENTS.md` 的改动 |
| SUB-2 | Code | 投稿前定点修订：基准参数表注、回流收敛指向、文献段 | 稿件小改、`SUB_2_fixes.md` | G-S2：作者确认新文献与改句 |
| SUB-3 | Code | 复现包：换行符、依赖清单、README、公开范围 | `SUB_3_repro.md` | G-S3：作者确认公开范围 |
| SUB-3b | Code | 图表脚本整理（建议，可与 SUB-5 并行） | `repro/`、`SUB_3b_figures.md` | 作者看对照报告 |
| SUB-4 | Code、作者 | 中文稿冻结（原 R8） | `SUB_4_freeze.md`、标签 `zh-final` | G-S4：作者本机 PDF 验收 |
| SUB-5 | Code | 英文稿（五个会话） | `paper_en/`、`SUB_5*_en.md` | G-S5：作者通读英文稿 |
| SUB-6 | Code、作者 | 投稿材料与打包 | 投稿包、投稿信 | G-S6：作者投稿 |

依赖：SUB-1 在 SUB-0 之后；SUB-2、SUB-3 在 SUB-1 之后，先后执行；SUB-4 在 SUB-2、SUB-3 之后；SUB-5 在 SUB-4 之后；SUB-3b 可与 SUB-5 并行，但须在另一个 worktree 中进行，不写相同文件。

时间（约两周）：第 0 天 SUB-0、SUB-1；第 1–2 天 SUB-2、SUB-3；第 3 天 SUB-4；第 4–12 天 SUB-5；第 13–14 天 SUB-6。

## 2. 开始前作者要定的事项

1. 是否采用本计划。采用即批准 SUB-1 中对 `AGENTS.md` 的改法。
2. 是否补合并方案第 4.2 节第 1 项的文献段（建议补；新文献在 SUB-2 中核对后还要作者确认一次）。
3. 代码与数据的公开方式（SUB-3 前）：公开 GitHub 仓库、Zenodo 快照，或“合理请求时提供”；`真实数据/` 能否公开。
4. 英文稿是否把 3.2 节（拐点）、3.4 节（参数影响）、4.2 节（显式族）移入附录或补充材料（SUB-5 前）。
5. 另文能否在投稿前挂预印本（SUB-6 前）。

## 3. SUB-0：本地合并（作者在 PowerShell 中执行）

全部命令在 `E:\work\draft` 中运行：`main` 签出在这里，在 `draft-nr` 里不能切到 `main`。任何一步的输出与“预期”不符，就停下，把输出交给 Code 或 Claude，不要继续。

### 3.1 检查

```powershell
cd E:\work\draft
git -C E:\work\draft status --short
git -C E:\work\draft-nr status --short
git -C E:\work\draft-return status --short
```

预期：三个工作区都没有以 `M`、`A`、`D` 开头的行（以 `??` 开头的未跟踪文件可以有）。有未提交的改动时，先在对应工作区提交或处理，不要用 stash 或 reset。

```powershell
git fetch origin --tags
git branch -vv
git rev-parse --short paper/no-return-focus
git rev-parse --short research/return-effects
git merge-base --is-ancestor main paper/no-return-focus; $LASTEXITCODE
```

预期：

- `paper/no-return-focus` 为 `101b3e0`，`research/return-effects` 为 `9887340`；
- 最后一行输出 `0`，即 `main` 是无回流分支的祖先，可以快进；
- `git branch -vv` 中三个分支都没有 `behind`。`main` 显示 `ahead 1`（提交 2b5545a，10-14 起未推送）属正常。

`paper/no-return-focus` 不是 `101b3e0`（本地有更新的提交）时，走 3.3 节的路径 B。最后一行不是 `0` 时停下。

### 3.2 备份

```powershell
git branch backup/main-pre-sub0 main
```

推送之前发现问题，可以用 `git reset --hard backup/main-pre-sub0` 回到合并前的状态。

### 3.3 快进

路径 A（`paper/no-return-focus` 为 `101b3e0`，通常如此）：快进到方案分支。它就是无回流分支加上合并方案与本计划两份文件。

```powershell
git merge --ff-only origin/claude/paper-branch-merge-strategy-w4vpck
git log --oneline -4
```

预期：`101b3e0` 之上只有放入本计划与合并方案的提交（提交信息以“SUB 计划”“SUB 投稿准备”“分支合并与投稿路线”开头）。

路径 B（本地无回流分支有更新的提交）：

```powershell
git merge --ff-only paper/no-return-focus
git checkout origin/claude/paper-branch-merge-strategy-w4vpck -- paper/revision_notes/merge_submission_plan.md ai/SUB_投稿准备_分步执行计划.md
git commit -m "放入投稿准备计划与合并方案"
```

### 3.4 引入回流计算目录

```powershell
git checkout research/return-effects -- r7_return paper/revision_notes/R7_2_return_theory.md paper/revision_notes/R7_3_numerics.md
git status --short
git commit -m "SUB-0: 引入回流分支的 r7_return 计算目录与 R7-2、R7-3 记录（补充 S5 回流数字的来源，源提交 9887340）"
git rev-parse HEAD:r7_return/results/r7_3_exponential_return.json
```

预期：`git status` 只列出 `r7_return/` 下的文件和两份记录；最后一行为 `582def57c4a957e242d884dff50d6c8937e9137a`，即补充 S5 表中回流数字的源文件，与 `nr_audit/results/return_import.json` 中记录的 blob 一致。

不要在 `main` 上运行 `r7_return/make_numbers.py`：它会生成稿件不用的 `paper/generated/r7_numbers.tex`。

### 3.5 检查后推送

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1
conda run --no-capture-output -n thesis python -m pytest nr_audit/tests -q -m "not slow"
conda run --no-capture-output -n thesis python -m pytest r7_return/tests -q
git status --short
```

预期：

- 补充 18 页、主稿 34 页，undefined 0。若有 undefined，再运行一次 `build.ps1`（补充材料与主稿互相引用）。
- `nr_audit`：230 项选中，全部通过，约 1–2 分钟。在 Linux/macOS 检出中，`test_sources` 有两项会因换行符失败，这是 SUB-3 要修的问题，Windows 检出中不会出现。
- `r7_return`：89 项通过、2 项跳过，约 2 分钟；跳过的是宏测试，因为 `main` 没有 `r7_numbers.tex`。
- `git status --short` 没有输出。这里不用 `nr_audit/run_tests.py`：它会改写已跟踪的测试报告，使工作区不干净。

以上预期已在云端用同样的步骤演练过（本地 `main` 取 2b5545a），编译页数与两组测试结果一致。

```powershell
git push origin main
```

### 3.6 工作区整理（可选）

- `E:\work\draft`：此后在这里工作。
- `E:\work\draft-nr`：内容与 `main` 相同；确认干净后可以移除：`git worktree remove E:\work\draft-nr`（分支保留）。
- `E:\work\draft-return`：存档，保留。分支与标签都不能删，`nr_audit` 的来源核验要读其中的提交 bb52b96。
- `E:\work\draft` 中未跟踪的 `ai/NR_no_return_revision_plan_20261014.md` 如果还在，它与已合并的 NR 计划逐字节相同，可以删除。
- 确认一切正常后删除备份分支：`git branch -d backup/main-pre-sub0`。

G-S0：作者看编译结果与 PDF 首页，确认与无回流版一致，再进入 SUB-1。

## 4. 逐步提示词（交给本地 Code）

用法：一步一个会话，在 `E:\work\draft` 中执行。Code 不推送、不自行宣布验收通过；作者确认后自己推送。

### SUB-1：合并登记与阶段规则

```text
你在 cuizhizhong/threshold_control 的 main 工作区（E:\work\draft）执行 SUB-1。先读 AGENTS.md、paper/revision_notes/STATUS.md、paper/revision_notes/merge_submission_plan.md、ai/SUB_投稿准备_分步执行计划.md。

1. 核对 SUB-0 的结果：git status 干净；main 包含 101b3e0（git merge-base --is-ancestor 101b3e0 main）；r7_return/ 已在 main，HEAD:r7_return/results/r7_3_exponential_return.json 的 blob 为 582def57c4a957e242d884dff50d6c8937e9137a；标签 nr-base、nr-focus-complete、r7-return-draft 存在。任何一项不符就停下报告。
2. 修改 AGENTS.md（作者采用 SUB 计划即批准以下改法；只改这些位置，其余条目不动）：
   a. 开头“当前阶段”一段改为：当前阶段为 SUB 投稿准备（2026-10-19 起），按 ai/SUB_投稿准备_分步执行计划.md 执行；无回流分支已于 SUB-0 快进合并到 main，中文稿以其结果为准，SUB-4 冻结为标签 zh-final，英文稿在 paper_en/；回流分支已存档（标签 r7-return-draft），其 r7_return/ 已引入 main，作为补充 S5 回流数字的来源；分支与标签不删除。
   b. “分支说明（2026-10-14）”一段改为合并后的现状，一句话。
   c. “NR 覆盖条款”改名为“无回流主稿规则（原 NR 覆盖条款）”，首句改为在 main 上继续有效。N1–N4、N6–N8 不改。N5 的可写范围增加 paper_en/、SUB 计划点名时的根目录 .gitattributes、README.md、requirements.txt、SUB-3b 的新目录、ai/SUB_投稿准备_分步执行计划.md（只限放入与校正）；r7_return/ 改为只读存档。N9 的比较基准改为：SUB-1 至 SUB-4 用 nr-focus-complete，SUB-5 起英文稿以 zh-final 为准；记录写成 paper/revision_notes/SUB_*.md；G-S 节点由作者确认。N10 标为作废（回流分支已存档，第二篇论文从 main 另开分支）。
3. STATUS.md：增加一行 SUB（投稿准备），登记 SUB-0、SUB-1；R8 一行改为“并入 SUB-4”。
4. 写 paper/revision_notes/SUB_1_rules.md（不超过一页）：SUB-0 的提交号与核对结果、AGENTS.md 改动摘要。
5. 不改 tex，不运行研究计算。提交“SUB-1: 合并登记与投稿准备阶段规则”，停下等作者确认。
```

### SUB-2：投稿前定点修订

```text
执行 SUB-2。先读 AGENTS.md、SUB 计划第 2 节、merge_submission_plan.md 第 4.1、4.2 节。

A. 基准参数出处（表 tab:xian_initial_fit 的表注）。先对照 refs/Tang_Zhou_2024_JMB.pdf 的式 (2.1) 与数值算例：N=763、S0=762、I0=1、β=0.155、c0=10、q0=0.01526、γ_I=0.1、δ_I=0.2504；确认该算例没有给 δ_q。核对无误后，把表注第一句改为：“基准参数取自文献\cite{Zhou2024SPCI}的示例算例，其中 $\gamma$ 为该文非隔离感染者的自然恢复率 $\gamma_I=0.1$ 与诊断率 $\delta_I=0.2504$ 之和；该算例未给出隔离感染者的移出率，本文取 $\delta_q=\gamma$，它只影响隔离感染者 $I_q$。”核对结果与 PDF 页码写进记录。原文与上述不符时停下报告，不改稿。
B. 补充 S5（supplement_sections/S7_return.tex）表 tab:sup:return:term 的表注末尾加一句：“积分容差的三档检查结果随代码公开（r7_return/）。”
C. 文献段。新文献须作者确认后才入稿：
   1. 对 merge_submission_plan.md 第 4.2 节第 1 项的 4 条候选，以及你认为必要的另外至多 2 条，在线核对出版信息（Crossref 或出版社页面）并读摘要，逐条列出“拟支持的论断—摘要原文依据”。
   2. 起草引言第 3 段末的 3–4 句：阈值控制的 Filippov/滑模工作研究滑模段与伪平衡点的存在；维持 I=η 的阶段即以 I=η 为切换面的滑模运动；本文在这一滑模上优化两种干预的组合。同时起草 bib 条目。
   3. 只写进记录，不改 tex。
D. 检查：编译（build.ps1，0 undefined）；check_tex（--old nr-focus-complete:<两份主文件>）；statement_diff（陈述应 0 条变化）。
E. 写 paper/revision_notes/SUB_2_fixes.md，更新 STATUS 的 SUB 行。提交“SUB-2: 投稿前定点修订（文献段待 G-S2）”，停下等作者确认。

作者在 G-S2 确认文献与写法后，同一会话继续：写入引言与 references.bib，编译检查新引用，提交“SUB-2 补：写入文献段（G-S2 已确认）”。
```

### SUB-3：复现包

```text
执行 SUB-3。先读 AGENTS.md、SUB 计划第 2 节、nr_audit/README.md、r7_return/README.md、README.md、.gitattributes，以及作者对 SUB 计划第 2 节第 3 项的决定。

A. 换行符（必须）。nr_audit/results/source_manifest.json 中 xian_loader（xian_control_comparison/xian_control_comparison.py）的 SHA-256 是 Windows CRLF 检出时的值，Linux/macOS 检出时 test_manifest_current 与 test_pinned_files_unchanged 失败。
   1. 在 .gitattributes 加一行 /xian_control_comparison/** -text；
   2. 删除工作区中的该文件后运行 git checkout -- xian_control_comparison/xian_control_comparison.py，使工作区为仓库中的 LF 内容（git diff 应为空）；
   3. conda run --no-capture-output -n thesis python nr_audit/sources.py 重新生成清单；核对只有 xian_loader 的哈希变化，新值应为 c029a604c8f7147a24d59e6c0d39a927ff360f0dbb1b7338f23bd86573ff15a2；
   4. 运行 nr_audit 全部测试（conda run --no-capture-output -n thesis python nr_audit/run_tests.py），应全部通过；它会重写 nr_audit/results/nr2_test_report.{json,md}，随本步一起提交。
B. 依赖清单（必须）：用 conda list -n thesis 读取实际版本，写根目录 requirements.txt（Python 版本写在注释中；至少 numpy、scipy、sympy、mpmath、pandas、openpyxl、pytest）。
C. README.md：把“计算代码的现状”一节改为现状：nr_audit/ 为无回流数字核验（入口与测试），r7_return/ 为补充 S5 的回流数字，reproducibility/ 为原始结果（只读）；编译方法不变。
D. 公开范围（只提方案，不执行公开）：列出公开包应含与不应含的目录。不应公开 refs/：其中有出版社 PDF 与一本电子书，有版权问题。ai/ 中的内部讨论由作者决定。真实数据/ 须作者确认来源与许可（He 等 2023 的数据是否已公开、可否再分发）。nr_audit 依赖的只读来源文件须保持相对路径；test_sources 中依赖提交 bb52b96 的检查在没有完整 git 历史时会自动 skip，写明这一点。写出数据与代码可得性声明的中英文草稿（URL 留空）。
E. 写 paper/revision_notes/SUB_3_repro.md，更新 STATUS。提交“SUB-3: 复现包的换行符、依赖与公开范围”，停下等 G-S3。
```

### SUB-3b：图表脚本整理（建议；可与 SUB-5 并行）

```text
执行 SUB-3b。在单独的 worktree 中进行，不与 SUB-5 写同一文件。README.md 原定投稿前把计算整理为“每张图、每张表对应一个脚本”。

1. 新建目录 repro/（作者可改名）。为正文 10 幅图和补充材料中的图与表各写一个入口脚本，复用 nr_audit/ 的模块，不改旧目录；输出写到 repro/output/。
2. 每个脚本运行后，与 paper/figures/ 中的现有图和稿件中的数字做数据级对照（底层曲线数组或表中数值的相对差），写进报告。
3. 不替换 paper/figures/ 中的任何图。差异超过显示精度时停下报告。
4. 写 paper/revision_notes/SUB_3b_figures.md。提交“SUB-3b: 图表脚本整理与对照”。
```

时间不够时，SUB-3b 可以推迟到返修。此时可得性声明写明：数值结果与核验代码已公开，图件脚本随修改稿提供。

### SUB-4：中文稿冻结（原 R8）

```text
执行 SUB-4。先读 AGENTS.md、NR_9_final.md、SUB_2_fixes.md、SUB_3_repro.md。

1. 编译两份稿件：0 undefined、0 multiply defined、0 个超过 10pt 的 Overfull。
2. 相对 nr-focus-complete 运行 check_tex 与 statement_diff：陈述变化应为 0；数字变化只来自 SUB-2；被引用的标签无缺失。
3. 按 NR_9_final.md 第 2 节的搜索表重做一遍禁用表述搜索。
4. 写 paper/revision_notes/SUB_4_freeze.md：变化清单、检查结果、作者需要看的 PDF 页（表 1 所在页、引言第 3 段所在页、补充 S5 两张表所在页）。
5. 提交“SUB-4: 中文稿冻结检查（待 G-S4）”，停下。
```

作者本机验收后，在批准的提交上建标签并推送：

```powershell
git tag zh-final <提交>
git push origin main
git push origin zh-final
```

### SUB-5：英文稿（五个会话）

总则（每个会话都遵守）：

- 目录与文件：`paper_en/`，主文件与补充材料各一个 tex，文件名由作者定。模板用作者从 BMB 官网投稿指南下载的 Springer Nature LaTeX 模板，放在 `paper_en/template/`；Code 不从第三方网站下载模板。摘要字数、关键词个数、参考文献格式与声明格式以官网投稿指南为准。
- 单一来源：数字用 `\input{../paper/generated/nr_numbers}`，与中文稿同源；图用 `\graphicspath{{../paper/figures/}}`，图内文字本来就是英文。SUB-6 打包时再复制进投稿目录。
- 参考文献：从 `paper/references.bib` 复制为 `paper_en/references_en.bib`；中文文献给出英文题名并注明 (in Chinese)。
- 术语按 `AGENTS.md` 4.4 节英文栏，标题按 `R1_storyline.md` 第 8 节。
- 数学陈述与中文稿逐条对应，不改含义、条件、量词与严格性；正文句子可以按英文习惯重组。
- 在第 2 节末加一段 Scope and conventions，集中交代模型（无回流）、控制类 $\mathcal A(\eta)$ 与终点约定；正文其余位置只在条件会改变结论方向时再写（合并方案第 4.2 节第 2 项）。摘要与结论各写一次范围。
- 摘要用“一对一交换”的表述：阈值控制期内新增感染与新增隔离易感者之和恒为 $S^*-S_c$，各控制之间每少一例感染就多隔离一名未感染者（定理 4.5(iii)；合并方案第 4.2 节第 3 项）。
- 推迟到英文稿的事项：表格统一 3 位有效数字（只改显示，不改取值）；图 1 标注（作者定）；下标 $c$ 的多重含义与 $q_c(S)$ 的两种用法（只在不改变任何公式含义时调整，并记录新旧记号对照）。
- 作者在第 2 节第 4 项决定移动 3.2、3.4、4.2 节时，按决定移动；未决定时保持中文稿结构。
- 每个会话结束：编译英文稿，0 undefined；英文正文不残留中文字符（参考文献中的 (in Chinese) 除外）；在记录中列出定理、命题、推论、表、图的中英文编号对照；写 `paper/revision_notes/SUB_5x_en.md`（x 为 a–e），提交，停下。

会话划分（提示词：“执行 SUB-5x。先读 AGENTS.md、SUB 计划第 4 节 SUB-5 总则、R1_storyline.md 第 8 节与上一会话的记录。只处理本会话点名的部分。”后接下表对应一行）：

| 会话 | 内容 |
|---|---|
| SUB-5a | 目录、模板、宏与 bib；题目、摘要、关键词；第 1 节引言 |
| SUB-5b | 第 2–5 节（含 Scope and conventions 一段）；附录 A、B |
| SUB-5c | 第 6–7 节与全部表格 |
| SUB-5d | 第 8–9 节；补充材料全部 |
| SUB-5e | 全文统一：术语、时态、冠词、重复的限定语；摘要压到期刊上限；编号对照终检 |

G-S5：作者通读英文 PDF，重点看摘要、贡献列表、定理陈述与中文稿是否一致；可以另请语言润色。

### SUB-6：投稿材料与打包

```text
执行 SUB-6。先读 SUB 计划、merge_submission_plan.md 第 4.2、5 节、SUB_3_repro.md 与 SUB-5e 的记录。

1. 声明：按期刊模板写 Funding、Competing interests、Data availability、Code availability、Author contributions 的草稿；作者信息、基金号与 URL 留空，由作者填写。
2. 投稿信草稿（英文，约一页）：研究问题；三项主要结果（状态参数化与可行性；一对一交换与不同目标的最优控制；成本最优控制的结构）；主动交代无回流模型是可解析的基准、补充材料给出回流下所有控制共享的下界；“最优”指阈值策略内的最优；另文若已公开，说明两文问题不同。
3. 推荐审稿人：只从本文参考文献的作者中提出候选名单与理由，不编写邮箱，由作者核实与取舍。
4. 打包：把 nr_numbers.tex、所用的图与 bib 复制进 paper_en/submission/，在该目录单独编译，确认不依赖 ../paper；生成最终 PDF（主稿与补充材料各一份）。
5. 投稿前检查表：摘要字数、关键词个数、图表文件格式、补充材料单独成文件、声明齐全、作者信息、可得性 URL。
6. 写 paper/revision_notes/SUB_6_package.md，提交“SUB-6: 投稿材料与打包（待 G-S6）”，停下。由作者投稿。
```

## 5. 作者怎样验收

- G-S0：编译页数与 PDF 首页；`git log` 顶部是 SUB-0 的提交。
- SUB-1：读 `AGENTS.md` 的 diff，确认只改了点名的位置。
- G-S2：逐条看新文献的摘要依据；看表 1 注的新写法。
- G-S3：确认公开范围（特别是 `refs/`、`真实数据/`）与可得性声明。
- G-S4：本机看 PDF 改动页，然后建标签 `zh-final`。
- G-S5：通读英文稿；摘要、贡献列表与定理陈述要与中文稿一致。
- G-S6：投稿。

## 6. 返修时可用的材料（不进初投稿）

| 材料 | 位置 | 用途 |
|---|---|---|
| 命题 R3（立即返回对照模型）与端点表 | 标签 `r7-return-draft`：`paper/sections/07b_return.tex`、`paper/appendices/C_return_proofs.tex` | 回答“哪些结论不依赖无回流”：时长排序与追踪人次排序仍成立，控制期累计感染对所有控制相同 |
| 36 条指数回流轨迹全表与收敛表 | `main`：`r7_return/results/r7_3_exponential_return.json`、`r7_3_convergence.json` | 同上；控制时长排序在 36 组中都保持 |
| 退出时全部释放的 $R_e(t_2^+)$：基准约 3.22、西安约 3.71 | `main`：`r7_return/results/r7_3_release.json` | 回答退出时释放隔离者的追问 |
| 西安线性成本下 TDINN 与仅隔离控制的成本排序反转 | 作者自验，材料不在仓库 | 回答成本形式的追问；届时把验证材料放进 `nr_audit/` |

取回存档文件到工作区：`git restore --source r7-return-draft -- <路径>`。在 PowerShell 中不要用 `git show … > 文件` 另存，会写成 UTF-16。

## 7. 完成标准

- `main` 为投稿版，GitHub 已同步；回流分支与标签保留。
- 中文稿打了标签 `zh-final`；英文稿编译通过、0 undefined，编号与中文稿一一对应。
- 代码包在 Windows 与 Linux 上测试全部通过，公开范围不含受版权保护的文件。
- 投稿材料齐全，作者已投稿。

---

**执行起点：先 SUB-0（作者手动），再 SUB-1。不要把 SUB-1 至 SUB-6 一次连续执行。**
