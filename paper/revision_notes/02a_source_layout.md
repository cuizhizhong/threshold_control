# 任务2a：源码模块化（待作者验收）

日期：2026-10-06。起点：`main`，`dba6f349981ff94a5e6c080b9bd17919df93af4f`。

作者已验收“1确认”，本轮仅执行另行授权的2a。依据实际根 `AGENTS.md`、`STATUS.md`、已批准 `01_decisions.md`、`CODEX_EXECUTION.md` 的通用约定与任务2a，以及两份正式源码的实际章节和label。执行手册实际位于 `paper/revision_notes/CODEX_EXECUTION.md`，为本轮开始前已有未跟踪文件，不纳入提交。

## 实际改动与文件映射

两份入口继续使用原名、文档类、参考文献后台、外部引用和图目录。主文前言、摘要、全局宏、`\appendix`、参考文献留在入口；补充前言、说明、编号设置和参考文献留在入口。20个完整内容块改用 `\input`，不新增分组或强制分页。各表仍在所属内容文件内直接编辑。

下表行号是本轮拆分前源码锚点；今后按实际子文件和label定位。这里只沿用旧顺序，未执行已批准的新八章目录和内容迁移。

| 实际子文件（相对 `paper/`） | 拆分前行号 | 主要label |
|---|---:|---|
| `sections/01_introduction.tex` | 主文31–63 | `sec:introduction` |
| `sections/02_model.tex` | 主文64–208 | `sec:model`、`sec:model:strategy` |
| `sections/03_single_control.tex` | 主文209–416 | `sec:s1` |
| `sections/04_sensitivity.tex` | 主文417–694 | `sec:cost`、`sec:scaling-theory` |
| `sections/05_inflection.tex` | 主文695–861 | `sec:s1:shape`、`sec:s1:inflection-position` |
| `sections/06_joint_control.tex` | 主文862–1323 | `sec:joint`、`sec:joint:cost` |
| `sections/07_numerics.tex` | 主文1324–1478 | `sec:num`、`sec:numerics`及联合数值小节label |
| `sections/08_xian.tex` | 主文1479–1643 | `sec:xian`、`sec:xian:threshold-scale` |
| `sections/09_population.tex` | 主文1644–1919 | `sec:dominance`及人口比较小节label |
| `sections/10_discussion.tex` | 主文1920–1956 | `sec:discussion` |
| `appendices/A_population_cases.tex` | 主文1959–1990 | `app:panel_eta_N` |
| `appendices/B_beta_comparison.tex` | 主文1991–2011 | `app:dom:numerics` |
| `appendices/C_contact_scan.tex` | 主文2012–2024 | `app:c0_scan` |
| `appendices/D_inflection_existence.tex` | 主文2025–2043 | `app:c0_beta` |
| `appendices/E_quarantine_cost.tex` | 主文2044–2081 | `app:cost` |
| `appendices/F_inflection_direction.tex` | 主文2082–2103 | `app:lambda` |
| `appendices/G_reference_conditions.tex` | 主文2104–2160 | `app:reference-comparison` |
| `supplement_sections/numerical_tables.tex` | 补充15–101 | `tab:sup:baseline`、`tab:sup:initial`、`tab:sup:eta` |
| `supplement_sections/medical_link.tex` | 补充103–146 | `sec:sup:medical-link` |
| `supplement_sections/threshold_scale.tex` | 补充147–164 | `sec:sup:threshold-scale` |

补充原行102的 `\renewcommand{\thesection}{S\arabic{section}}` 留在入口首次补充节之前。原有空行、注释、`\clearpage` 和 `\FloatBarrier` 均随原位置保留。主文旧6.4仍在联合控制子文件，全部24幅图仍在主文原位置；这些结构分配留待2b执行。

## 内容与保护核对

- 删除清单：无；未删原文、公式、证明、标题、图表、label或注释。入口中移出的内容均完整进入上表子文件。
- 移动清单：仅上表20个源码块的存储位置变化，文档内容顺序与显示位置不变。
- `limitations_pool.md`：无内容移入，未创建或修改。
- 数字变动：无；模型、初值、参数、策略、指标、终点、单位、数学陈述及证明原样保留。
- 四张保护图按 `fig:scenario1:single-sim`、`fig:scenario1_summary_eta`、`fig:joint:compare`、`fig:joint:capacity` 定位；原图源SHA256均与 `01_decisions.md` 记录一致，图8未合并。图10的 `jointcapacitypostexitdays` 定义及图注调用均留在 `sections/07_numerics.tex`，作用域和先后顺序不变，图注未改。
- 待作者确认：无新增数学或结构疑问。E-POP、E-WEIGHT、E-MULTIPLIER、E-INTERSECTION保留原未解决说明；D-XIAN-LINEAR继续暂缓、非阻塞，未进行研究、追溯、补算或验证。

## 本轮实际检查

1. 拆分前两份正式TeX与既有baseline逐字节相同。严格展开本轮完整 `\input` 行后，主文162670字节、补充9625字节与拆分前逐字节一致。SHA256分别为 `cfd174f05f7a0f3a92a12097eadee50b7712e066f34c8e15d6102f85f299343c`、`b048368f95155b5cea425e3acdeed75f0a110bb11ac0fea12709c29e15216ab5`。这也核对了数字对应的上下文、顺序和单位，未仅凭数字计数判断内容不变。
2. 20条输入路径均存在、唯一，并覆盖全部20个子文件。章节和全部label序列不变；主文196个label、24个图label、28个定理类环境，补充5个label。有效宏定义先于图注调用。
3. 在仓库根目录实际运行：

   ```powershell
   python paper/tools/check_tex.py --old paper/revision_notes/baseline_main.tex paper/revision_notes/baseline_supplement.tex --new paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex --bib paper/references.bib --out paper/revision_notes/02a_check.md --stats
   powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1
   ```

   检查报告：标签缺失、悬空引用、重复标签、bib缺键均为0；合并口径的数值字面量756→756，缺0、增0。未引用bib条目仍为 `ShaanxiHealth2022`、`Zhang2026Behavior`。
4. 主文与补充各按XeLaTeX → Biber → XeLaTeX → XeLaTeX完成，先补充后主文。主文51页、补充5页；未定义项、重复定义、Overfull hbox均为0。主文已有1处Underfull hbox（badness 2376）仍在，补充无此项；两份最终TeX日志均无 `Warning:`，Biber日志无WARN/ERROR。Biber终端出现Perl locale回退到 `C` 的环境提示，两次均正常完成。
5. 与本轮编译前PDF对照：Poppler在96 dpi下渲染全部56页，逐页像素完全一致；两份PDF的全文文本及顺序完全一致。主文196条、补充5条AUX `\newlabel` 记录逐行一致，显示编号和标签页码不变。实际查看主文第8、26、27、28、51页及补充第4、5页，未发现本轮引入的排版变化。
6. 展开正文去注释后的汉字数：主文28110→28110，补充1241→1241；每节统计见 `02a_check.md`。本轮改写字数为0。

检查器的实际边界：仅支持字面量 `\input{...}` / `\include{...}`，本轮为入口的一层、每文件一次输入，全部覆盖。它合并两文档标签判断跨文档引用；AUX导入另由实际编译验证。检查器不主动报缺失输入，且退出码不涵盖重复标签、bib缺键或数字变化，故另查输入存在性并读取报告。未扩展检查器或创建回写器。

本轮前PDF、源码副本、渲染、文本、逐页哈希与检查脚本保存在被忽略的 `paper/tmp/02a/`，不纳入提交，也未覆盖既有baseline。源码原有CRLF和块末空行保留；默认 `git diff --check` 将新增输入行的CR及新子文件末尾原有空行报为空白，按 `cr-at-eol,-blank-at-eof` 复核；原块内空白由完整字节等价核验。

## 交付与停止点

实际修改两份入口，新增20个源码子文件、`02a_check.md`及本记录，更新 `STATUS.md`。仅这些25个文件进入本地提交；已有未跟踪材料和编译产物排除。未修改构建入口、图源、参考文献、计算代码、数据或历史结果；未运行研究计算。

本轮状态：**待作者验收**。提交号由Git及回复给出，不回填自身hash。未push；停在2a，不自动执行2b。下一任务为另行授权的2b。
