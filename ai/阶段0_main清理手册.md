# 阶段 0 手册：在 main 上清理仓库（论文是论文，代码是代码）

- 适用：本机仓库 `E:\work\draft`（GitHub：`cuizhizhong/threshold_control`），起点提交 `8537652`，在 `main` 上直接进行。
- 预计用时：约 1 小时。
- 分工：打标签、放入新规则文件由你自己做；移动和删除交给 Codex，分两个任务；每步之后你按清单检查。
- 演练结果：我在仓库副本上按本手册完整执行过一遍（编译除外，那台机器没有 biber）。受版本控制的文件从 2461 个减到约 410 个，工作区从约 810 MB 减到约 216 MB；论文 tex 与原稿逐项比对为 0 差异；保留的计算代码没有引用被删的模块。

> 若你已按上一版手册建了 `journal-revision` 分支或解压了 `paper_初始文件.zip`：先 `git switch main`，`git branch -D journal-revision`（推送过的话再 `git push origin --delete journal-revision`），并删掉仓库里未提交的 `paper` 文件夹，然后从第 1 步开始。上一版手册和那个压缩包作废。

---

## 清理后的仓库

```text
E:\work\draft\                       （main）
├─ AGENTS.md          ← 整份重写，唯一的现行规则（约 16 KB）
├─ CLAUDE.md          ← 一行 @AGENTS.md，供 Claude Code 读取
├─ README.md          ← 重写
├─ paper\             ← 正式稿，直接编辑
│  ├─ flatten_curve_analysis_cn.tex  flatten_curve_supplement_cn.tex
│  ├─ references.bib  elegantpaper.cls  figures\（24 幅图）
│  ├─ build.ps1  build.sh  style_examples.md  tools\check_tex.py
│  └─ revision_notes\  baseline_main.tex  baseline_supplement.tex  00_baseline.md  00_check.md
├─ reproducibility\   ← 只剩计算代码与 results\（README 重写）
├─ code\  c0_sensitivity\  scenario1_inflection\  scenario1_threshold_landscape\
├─ xian_control_comparison\  xian_dom\  joint_control\     ← 计算模块，暂不动
├─ 真实数据\  refs\
└─ （已删除）ai\  archive_unused\  latex\  以及 reproducibility\ 中的稿件控制管线
```

标签 `pipeline-final-20261006` 保存清理前的一切，删掉的东西随时可以单个取回。

提交顺序：

1. `docs: 新的 AGENTS.md、README 与 paper/ 初始文件`（你）
2. `refactor: 论文移至 paper/，删除 latex/ 旧稿与修订目录`（Codex 任务 A）
3. `chore: 删除稿件控制管线与历史目录`（Codex 任务 B）

---

## 第 1 步　开始前检查并打标签（你自己，约 5 分钟）

```powershell
cd E:\work\draft
git status                 # 应显示 nothing to commit, working tree clean
git switch main
git pull
git log -1 --oneline       # 应为 8537652 或更新的提交
xelatex --version
biber --version
```

- [ ] **工作区干净。** 有未提交的改动就先提交或 `git stash`。
- [ ] **没有还要合入正式稿的补丁。** 清理后 `latex/` 不复存在，正式稿只在 `paper/`。
- [ ] **没有正在运行的复现任务。**

然后打标签并推送到 GitHub：

```powershell
git tag pipeline-final-20261006
git push origin pipeline-final-20261006
git ls-remote --tags origin            # 应能看到 refs/tags/pipeline-final-20261006
```

这个标签是删除前唯一需要的保险，一定要确认远端已有。

---

## 第 2 步　放入新规则文件（你自己，约 5 分钟）

先放新规则、再让 Codex 动手，是因为 Codex 每次开会话都会先读 `AGENTS.md`。旧文件里有“冻结包、历史输出不得覆盖”“保持修改范围小”“结论不要写满”等规定，会和清理、和后面的去防御化改写打架。

`main清理文件包.zip` 的内容（均已写好并测试）：

| 文件 | 说明 |
|---|---|
| `AGENTS.md` | 新的根目录规则：仓库结构与历史、投稿修改的边界、不可改动的内容、论文主线与贡献、写作规范与术语表、编译与检查命令、待作者决定的事项、计算约定 |
| `CLAUDE.md` | 一行 `@AGENTS.md` |
| `README.md` | 新的项目说明 |
| `reproducibility/README.md` | 说明该目录保留了哪些计算代码和结果、为什么暂时不能直接运行 |
| `paper/build.ps1`、`paper/build.sh` | 编译脚本（先补充材料后主稿，结束时报告页数和警告数） |
| `paper/tools/check_tex.py` | 只读检查：标签、悬空引用、文献、数字的增减 |
| `paper/style_examples.md` | 改写示例 1–9 |

```powershell
Expand-Archive .\main清理文件包.zip -DestinationPath E:\work\draft -Force   # zip 路径按你的下载位置改
git status --short
```

应看到：`M AGENTS.md`、`M README.md`、`M reproducibility/README.md`，以及未跟踪的 `CLAUDE.md` 和 `paper/`。确认后提交：

```powershell
git add AGENTS.md CLAUDE.md README.md reproducibility/README.md paper
git commit -m "docs: 新的 AGENTS.md、README 与 paper/ 初始文件"
```

---

## 第 3 步　论文独立（Codex 任务 A）

在仓库根目录启动 Codex，粘贴：

```text
本任务是作者要求的阶段 0 清理第一部分，属于 AGENTS.md 第 1 节边界的明确例外：可以移动和删除 latex/ 下的文件。不修改论文内容。

0. 先运行 git branch --show-current（应为 main）和 git tag -l pipeline-final-20261006（应能看到该标签）。任一不符就停下来告诉我。

1. 用 git mv 把正式稿移到 paper/（paper/ 中已有 build.ps1 等初始文件，不要改动它们）：
   git mv latex/flatten_curve_analysis_cn.tex latex/flatten_curve_supplement_cn.tex latex/references.bib latex/elegantpaper.cls paper/
   git mv latex/figures paper/figures

2. 新建 paper/revision_notes/，用文件复制（不要用 git show 重定向，以免改变编码）保存原稿快照：
   Copy-Item paper\flatten_curve_analysis_cn.tex paper\revision_notes\baseline_main.tex
   Copy-Item paper\flatten_curve_supplement_cn.tex paper\revision_notes\baseline_supplement.tex

3. 删除 latex/ 中剩下的全部受版本控制的内容：git rm -r -q latex
   之后若磁盘上仍有 latex 文件夹，先列出其中的文件：如果全是 LaTeX 编译中间文件（.aux .log .bbl .blg .out .bcf .run.xml .synctex.gz .xdv .fls .fdb_latexmk），删除整个文件夹；如果有别的文件，列给我看，不要删除。

4. 根目录 .gitignore 末尾追加两行：
   # 论文编译产物（PDF 不入库）
   paper/*.pdf

5. 根目录 .gitattributes：删除注释行“# 已验收讨论来源包由逐字节SHA追溯，克隆时不得转换换行。”及其下面三行 /ai/ 开头的规则；删除注释行“# 正式论文与已验收来源保持相同字节；不会影响 PDF 的二进制识别。”及其下面五行 /latex/ 开头的规则。其余行不动。

6. 编译：powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1
   不要用 Git Bash。失败时把对应 .log 中的第一个错误给我看，不要修改 tex。

7. 自检（仓库根目录）：
   python paper/tools/check_tex.py --old paper/revision_notes/baseline_main.tex paper/revision_notes/baseline_supplement.tex --new paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex --bib paper/references.bib --hedge --stats --out paper/revision_notes/00_check.md

8. 写 paper/revision_notes/00_baseline.md，内容：基线标签 pipeline-final-20261006；当前提交号（git rev-parse --short HEAD）；build.ps1 最后输出的两行；check_tex.py 输出的一行结论；一句“各节汉字数与限定性词语计数见 00_check.md”。

9. 提交（latex/ 的删除已由 git rm 暂存，不要再对 latex 运行 git add，否则会报 pathspec 错误）：
   git add -A paper .gitignore .gitattributes
   git status
   确认暂存区中没有 .aux .log .bbl .pdf 文件后：
   git commit -m "refactor: 论文移至 paper/，删除 latex/ 旧稿与修订目录"
```

**你检查：**

- [ ] `paper\flatten_curve_analysis_cn.pdf` 51 页、`paper\flatten_curve_supplement_cn.pdf` 3 页；随手翻几页，外观与原稿一致。
- [ ] `00_baseline.md` 中 undefined、multiply defined 均为 0。
- [ ] `00_check.md` 结论为：标签缺失 0、悬空引用 0、数字缺 0、增 0（两份稿件共 756 个数值字面量）；bib 中未被引用的条目为 `ShaanxiHealth2022`、`Zhang2026Behavior`。
- [ ] `git show --stat HEAD`：`latex/` 的 tex、bib、cls、figures 显示为重命名到 `paper/`，其余 `latex/` 文件为删除，另有 `.gitignore`、`.gitattributes` 和 `paper/revision_notes/` 的改动。

不满意：`git reset --hard HEAD~1` 回到第 2 步结束时的状态，重新执行本步。

---

## 第 4 步　删除稿件控制管线与历史目录（Codex 任务 B）

在仓库根目录新开一个 Codex 会话，粘贴：

```text
本任务是作者要求的阶段 0 清理第二部分，属于 AGENTS.md 第 1 节边界的明确例外：按下面的清单删除文件。不修改清单以外的任何文件。先运行 git branch --show-current（应为 main）和 git tag -l pipeline-final-20261006（应能看到该标签），任一不符就停下。

1. 删除历史目录：
   git rm -r -q ai archive_unused

2. 删除 reproducibility/ 中的稿件控制管线、审计与运行记录（在 reproducibility 目录下执行，清单之外的文件一律不动）：
   git rm -r -q manuscript_versions publication tests release_reports runs deliverables
   git rm -q manuscript_version.py paper_sync.py document_revision.py icu_revision_text.py threshold_revision.py threshold_revision_text.py publish_verified.py registry.py run_all.py run_all.ps1 run_selection.py compare_runs.py build.py theory_trace.py integrity.py sec7_v2_refinement_audit.py joint_integration_audit.py package_joint_release.py postprocess_joint_extra.py check_export_probe.py prepare_export_probe.py probe_lossless_heatmap.py prepare_matlab_regression.py verify_matlab_regression.py validation_report.md future_plan.md joint_extra/manuscript.py joint_extra/test_manuscript.py
   若清单中某个文件不存在，记下来告诉我，继续删其余的。

3. 确认保留下来的 reproducibility 文件为：README.md、assets/、bootstrap.py、c0.py、checks.py、configuration.md、configuration_index.json、environment.json、figures.py、finalize_matlab_figures.py、joint.py、joint_extra/（core.py、run.py、figures.py、validation.py、test_joint_extra.py、test_kappa_refinement.py、README.md、acceptance.json）、manuscript_audit_notes.md、matlab_*.m（9 个）、plotting_checks.py、population.py、registry.json、registry.md、requirements.txt、results/、xian.py。与此不符就告诉我。

4. 检查保留的 reproducibility 下各 .py 文件（含 joint_extra/）中，没有 import 下列已删除的模块：manuscript_version、paper_sync、document_revision、icu_revision_text、threshold_revision、threshold_revision_text、publish_verified、registry、run_all、run_selection、compare_runs、build、theory_trace、integrity、postprocess_joint_extra、joint_extra.manuscript。只报告结果，不修改代码。

5. 磁盘上的残留：
   - 若 ai、archive_unused 文件夹或 reproducibility 下被删的目录在磁盘上仍存在（里面是未跟踪的文件），列出其路径和大小，不要删除，交给我决定；
   - 同样列出 reproducibility 下其他未跟踪的本地目录（如 backups、dev_*、integration_failure_probe_*、historical_optional_probe_*），不要删除；
   - 不要碰 reproducibility/.venv。

6. 编译一次 paper\build.ps1，确认论文仍正常（页数不变）。

7. 提交（删除已由 git rm 暂存，不需要再 git add；不要对已删除的目录运行 git add，否则会报 pathspec 错误）：
   git status
   确认暂存区只有删除、没有新增或修改的文件后：
   git commit -m "chore: 删除稿件控制管线与历史目录"
```

**你检查：**

- [ ] `git ls-files | Measure-Object` 约 410 行（原来 2461）。
- [ ] 第 4 项检查结果为“没有引用被删模块”。
- [ ] Codex 列出的磁盘残留（若有）：确认都不需要后，你自己删除对应文件夹；`reproducibility\.venv` 保留。
- [ ] `git ls-tree -r --name-only pipeline-final-20261006 | Select-String paper_sync` 能显示 `reproducibility/paper_sync.py`，说明标签里确实保存着被删的管线。

---

## 第 5 步　推送与最终检查

```powershell
git log --oneline -4          # 三次新提交，最下面是 8537652
git push                      # 推送 main
```

- [ ] 根目录只剩：`AGENTS.md`、`CLAUDE.md`、`README.md`、`.gitignore`、`.gitattributes`、`.vscode\`，以及 `paper`、`reproducibility`、`code`、`c0_sensitivity`、`joint_control`、`refs`、`scenario1_inflection`、`scenario1_threshold_landscape`、`xian_control_comparison`、`xian_dom`、`真实数据` 这些目录。
- [ ] GitHub 上 main 分支的首页显示新的 README；Tags 中有 `pipeline-final-20261006`。

---

## 出问题怎么办

| 问题 | 处理 |
|---|---|
| 推送前发现任何一步不对 | `git reset --hard pipeline-final-20261006` 回到起点（丢弃这几次提交；标签不受影响），从第 2 步重来 |
| 推送后才发现问题 | 不要强推；用 `git revert <提交号>` 撤销某次提交，或从标签取回需要的文件 |
| 需要某个已删除的文件 | `git restore --source pipeline-final-20261006 -- <路径>`，例如取回某个绘图脚本 |
| PowerShell 拒绝运行 build.ps1 | `powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1` |
| build.ps1 中文乱码或语法错误 | 文件须为带 BOM 的 UTF-8（压缩包里的已是）；若被编辑器另存成无 BOM，重新解压 |
| 编译报找不到图片 | 确认 `paper\figures\` 共 24 个 PDF。`xian_eta_sensitivity.pdf` 等几幅图在 tex 中不带 `figures/` 前缀，靠 `\graphicspath` 在 `figures\` 中找到 |
| 引用显示 `[?]` | biber 没跑或失败，看 `.blg` |
| `check_tex.py` 报告有差异 | 说明快照或稿件被改动过（例如换行或编码转换）；让 Codex 重新复制，不要修改 tex 去“对齐” |

---

## 两点提醒

1. **重画图件时需要从标签取回绘图脚本。** 当前论文图的绘图脚本有一部分在被删的 `latex/revision_layout_v5/`、`latex/revision_style_restore/`、`latex/revision_v4/` 中（如 `layout_python.py`、`layout_matlab.m`、`restore_figures.py`），部分输入数据在 `archive_unused/generated_snapshots/`。改写文字用不到它们；以后若要改图（换记号、统一风格）或做代码整理，用 `git restore --source pipeline-final-20261006 -- <路径>` 取回。新的 AGENTS.md 和 `reproducibility/README.md` 里都写了这一点。
2. **`refs/` 的版权问题（可选处理）。** 仓库是公开的，`refs/` 里有出版社的论文 PDF 和一本 Z-Library 来源的书。删除只影响最新版本，历史提交和标签里仍然公开可见，所以最彻底的办法是在 GitHub 上把仓库设为私有；投稿时若要公开代码，再单独建一个只含代码和数据的公开仓库。

---

## 之后每个阶段怎么开始

- 每个阶段在仓库根目录新开一个 Codex 会话，粘贴《修改计划与分阶段提示词》中对应阶段的提示词；提示词第一句都是“先阅读 AGENTS.md……”。
- 每个阶段结束后运行 `git show --stat HEAD`：改动应全部在 `paper/` 下。
- 下一步：阶段 1（诊断，只读，不改稿）。
