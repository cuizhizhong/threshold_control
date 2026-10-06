# AGENTS.md

本文件是本仓库唯一的现行规则。子目录中的 AGENTS.md（`xian_control_comparison/`、`scenario1_threshold_landscape/` 等）是各计算模块的历史说明，其中涉及论文、图号和正式稿位置的内容一律以本文件为准。`paper/revision_notes/01_decisions.md` 存在时，其中的作者决定优先于本文件第 7、9 节的建议。

## 0 仓库结构与历史

| 目录 | 内容 | 现状 |
|---|---|---|
| `paper/` | 正式稿（中文）、参考文献、模板、图、编译脚本；`revision_notes/` 存放各阶段修改记录 | 唯一正式稿，直接编辑 |
| `reproducibility/` | 计算代码（`xian.py`、`population.py`、`c0.py`、`joint.py`、`figures.py`、`joint_extra/` 等）、`results/` 中的数值结果、`manuscript_audit_notes.md`（求解器设置与未取整数值） | 暂按原样保留；脚本中的路径仍指向旧结构，不能直接运行，在代码整理阶段修复 |
| `code/`、`scenario1_inflection/`、`scenario1_threshold_landscape/`、`c0_sensitivity/`、`xian_control_comparison/`、`xian_dom/`、`joint_control/` | 各计算模块，以及冻结的 20261002 交付包 | 同上 |
| `真实数据/` | 西安原始数据 | 只读 |
| `refs/` | 参考文献 PDF | 只读 |

- **论文**：SIQR 阈值控制论文，目标期刊为 Bulletin of Mathematical Biology 类英文生物数学期刊。先在 `paper/` 完成中文稿，再译成英文（`paper_en/`）。
- **历史**：2026-10-06 清理前的完整状态保存在标签 `pipeline-final-20261006`，包括已删除的稿件控制管线（受控稿源、文字同步、发布与审计脚本及测试）、`ai/` 讨论记录、`archive_unused/` 和 `latex/` 下的旧稿与 `revision_*` 目录。需要时用 `git show pipeline-final-20261006:<路径>` 查看，或用 `git restore --source pipeline-final-20261006 -- <路径>` 取回单个文件；不要整体恢复。
- **重画图件**：当前论文图的绘图脚本有一部分在已删除的 `latex/revision_layout_v5/`、`latex/revision_style_restore/`、`latex/revision_v4/` 中，部分输入数据在 `archive_unused/generated_snapshots/` 中。需要重画这些图时，先从上述标签取回。

## 1 当前任务与边界（投稿修改）

- 任务：把论文修改为可投稿的期刊论文——结构、行文、篇幅、前置部分与参考文献。不做新的数学研究，不做新的数值计算。
- 只修改 `paper/` 内的文件（翻译阶段为 `paper_en/`）。不修改计算代码、`results/`、`真实数据/` 和 `refs/`；不运行计算脚本。查数字时可以只读 `reproducibility/results/` 和 `reproducibility/manuscript_audit_notes.md`。
- 每次只完成当前提示词指定的阶段或章节，不顺手修改其他章节；发现其他地方需要配合修改，写进修改记录。

## 2 不可改变的内容

发现疑似错误时，写进修改记录的“待作者确认”，不要自行修正。

1. 定理、命题、引理、推论、注记的数学内容、假设和证明逻辑。允许：精简证明行文；把证明移到附录；合并重复的陈述——合并后的陈述必须蕴含原有各条。
2. 数值。只能删减或调整显示位数（正文 3–4 位有效数字，表格保持原精度）；不能改值、不能新算；正文数字必须与表格一致。保留的每个数字都要能在 `paper/revision_notes/baseline_*.tex` 或 `reproducibility/results/` 中找到。
3. 数据、参数取值和图像文件。图中文字需要修改时，只在修改记录中列出。
4. 参考文献。不得凭记忆新增或补全 bib 条目；候选文献写进修改记录，经作者确认后才能加入，且只能依据 `refs/` 中 PDF 本身的信息。
5. 原有引用所支持的论断：可以改写措辞，不能把引用挪去支持别的论断。

## 3 论文主线与贡献

**主线**：在同一社区非隔离感染人数上限 $I\le\eta$ 下，接触减少与追踪隔离可以有不同分配。控制时长、累计感染和成本需要分别评价。在固定起止状态且 $0<\beta<1$ 时，最快与累计感染最少同序；最低二次成本则有另一取舍。规定在 $S=S_c$ 退出还给累计感染设定下界。ICU 容量是选取 $\eta$ 的动机，$\eta$ 在文中是外生参数。

**贡献**（标签为原稿标签；阶段 1 后按 `01_decisions.md` 更新）：

- C1 仅隔离阈值控制的完整解析解：启动状态（Lambert $W$）、隔离控制函数、控制时长、退出后的动态与累计新增感染；提高阈值降低最大隔离比例、控制时长和成本，但增加累计感染。（`thm:s1:start`、`thm:s1:platform`、`thm:s1:tend`、`thm:s1:Itcum`、`prop:threshold-tradeoff`）
- C2 联合阈值控制的状态参数化：全部控制与接触率状态函数 $c_c(S)$ 对应；能力限制下整段可行的充要条件。（`thm:joint:representation`、`cor:joint:feasibility`）
- C3 固定起止状态下，控制时长、累计新增感染与新增隔离易感者人数之间的恒等式：$0<\beta<1$ 时，最快的分配累计感染最少，但进入隔离的未感染者最多。（`thm:joint:comparison`、`cor:joint:capped-comparison`、`cor:joint:whole-epidemic`）
- C4 二次成本最小分配：存在性与逐状态有限候选判据；最小成本随阈值严格下降；退出前两种措施必须共同使用，成本严格低于两种单控制，代价是控制时长和累计感染增加。（`thm:joint:cost-minimum`、`prop:joint:minimum-threshold`、`prop:joint:terminal-allocation`、`prop:joint:global-structure`、`rem:joint:duration-constraint`）
- C5 在 $S=S_c$ 退出导致累计感染下界 $\beta(S_0-S_c)$；西安全市参数下约 $1.53\times10^6$，与低累计感染目标不相容。（`prop:exit-infection-lower-bound`）

## 4 写作规范

### 4.1 限定性表述分五类处理

| 类别 | 判别 | 处理 |
|---|---|---|
| A 定理假设 | 去掉后结论不成立，如 $0<\beta<1$、$\eta>1$、触发条件、“无额外能力限制” | 保留在定理陈述里；摘要、引言、结论转述时也要带上 |
| B 作用域 | “类内”“固定起止状态”“规定控制类” | 在模型章定义控制类 $\mathcal A(\eta)$，删去重复的解释性作用域声明；具体比较所需的固定起止二维状态、完整初值、能力限制、终点、单位、假设和严格性仍留在定义、结果或比较附近 |
| C 方法局限 | 无回流假设、观测误差与执行延迟、$J$ 不计隔离人天、有效人口未知、阈值未经临床标定、长期外推 | 模型无回流假设、目标函数不含隔离人天、设计阈值身份及必要表注保留在对象附近；讨论集中解释这些条件的影响，重复讨论内容追加到 `revision_notes/limitations_pool.md` |
| D 冗余与元评论 | “无需再引入”“不必另设”“这里没有据此断言”“并不意味着”等 | 仅删除纯元评论；否定句若承载边界，改成等义的正面说明或保留 |
| E 未完成的工作 | 按实质判断“尚待核查”“未进一步确定”等；有限候选最小化判据、驻点候选不属于未完成研究 | 真正未解决的连续集合、唯一性或匹配性登记并保持原文，未经批准不认证、不靠改写消除；按已批准的处理方案执行，仅暂停依赖该问题的结论或任务，独立部分可继续；迁移到补充不视为已经解决 |

### 4.2 改写示例

见 `paper/style_examples.md`（示例 1–9）。改写任何章节前先读一遍；提示词中的“示例 N”指该文件中的编号。

### 4.3 句式、段落与数值

- 每节开头 1–3 句：本节回答什么问题、主要结论是什么。不写“本节先……再……最后……”式路线图（引言末段除外）。
- 定理之后最多 1–2 句说明含义或机制；不复述证明；不写“该结论只刻画……不证明……”。
- 证明保留逻辑完整，删除“在本证明中记”“下面说明”之类的过渡；长证明移附录，正文写“证明见附录 A”。
- 一句话一个论断；不用分号串起三四个从句。论证主线连续行文，不用 `\paragraph` 或加粗小标题把论证切成清单。
- 数值段落按“现象 → 机制 → 对应的理论结果”写。正文一段不超过 3–4 个数字，保留 3–4 位有效数字；精确值留在表中。同一结果只在一处给出完整数字。
- 用“本文”，不用“本稿”；用“数值计算/数值验证”，不用“核查”。预先生成并输入完整方程的时间函数称“开环控制”；名义模型、参数、容量和退出时刻按原有含义处理，不批量替换“名义”。状态表达用于参数化，不把 ODE 实时状态反馈写成原有开环实现；解析公式回代不改称独立 ODE 验证。
- 不加空泛评价词（“深刻”“系统性”“重要意义”），也不为了“保险”新增限定语。

### 4.4 术语表（推荐值，以 01_decisions.md 为准）

| 统一为 | 英文译法 | 替换掉的写法 |
|---|---|---|
| 阈值控制期 $[t_1,t_2]$ | threshold-control phase | 平台期、感染平台、平台控制 |
| 控制时长 $\Delta t$ | control duration | 控制持续时间 |
| 隔离比例 $q$ | quarantine fraction | 隔离率（首次定义时说明 $q$ 的含义） |
| 接触率 $c$ | contact rate | — |
| 清零时间 $t_{\rm end}$ | clearance time | 动态清零时间、社区动态清零时间、清零时刻 |
| 仅隔离控制 | quarantine-only control | 仅加强隔离、隔离率阈值控制、仅隔离阈值策略 |
| 仅减少接触 | contact-reduction-only control | — |
| 联合阈值控制 | joint threshold control | — |
| 阈值控制类 $\mathcal A(\eta)$ | admissible threshold-control class | 规定控制类 |
| 最小成本分配 | minimum-cost allocation | 类内最小成本、最低成本分配、成本最小分配等 |
| 常规控制 | baseline control | “无控制”（禁用） |
| 累计新增感染 | cumulative new infections | — |
| 新增隔离易感者人数 | newly quarantined susceptibles | — |

注意：$I_{\rm cum}$（社区累计）、$I_{q_{\rm cum}}$（隔离累计）、$I_{t_{\rm cum}}$（总累计，宏 `\Itcum`）是三个不同的量，不得合并。

## 5 LaTeX 与编译

- 保留全部 `\label`；新增标签用 `sec:`、`thm:`、`prop:`、`lem:`、`cor:`、`rem:`、`eq:`、`fig:`、`tab:` 前缀。被引用的标签不得删除。
- elegantpaper 的 `corollary`、`remark` 不编号，原稿因此定义了 `corollaryn`、`remarkn`；继续使用这两个环境。
- 图内文字保持英文（最终投英文期刊），中文稿阶段不改图。
- 可删除确认无用的生成器注释和未被调用的宏；仍被调用且承载公式、图注、表注意义的宏及兼容 label 保留。图10的 `jointcapacitypostexitdays` 目前有效，迁移时携带定义及作用域。若将其等价写为已有1天，须在获批的图注/版式任务记录，不改变图意。
- 参考文献按首次引用顺序编号（`\ExecuteBibliographyOptions{sorting=none}` 或目标期刊样式）。
- 编译：Windows 下用 PowerShell 运行 `paper/build.ps1`（不要用 Git Bash），Linux 下运行 `paper/build.sh`。顺序是先补充材料、后主稿，各自 xelatex → biber → xelatex → xelatex；跳过 biber 会使引用显示为 `[?]`。
- 纯说明或只读诊断阶段复用有效检查，不强制重新编译或交付修改后 TeX。报告明确区分本轮执行、阶段0复用与未测试；数字字面量计数不代替参数组、策略、指标、终点和单位检查。
- 修改 TeX、引用或文档资源的阶段结束：按实际入口构建主文与补充，编译通过、0 个未定义引用，并检查受影响 PDF；运行 `paper/tools/check_tex.py` 比较本阶段前后（在仓库根目录运行）：
  `python paper/tools/check_tex.py --old <上一阶段的主稿与补充材料> --new <当前主稿与补充材料> --bib paper/references.bib --out paper/revision_notes/<阶段号>_check.md`
  与原稿比较时，`--old` 用 `paper/revision_notes/baseline_main.tex paper/revision_notes/baseline_supplement.tex`。脚本会展开 `\input`，报告丢失的标签、悬空引用、文献问题，以及消失和新增的数字。

## 6 每阶段交付

1. 修改后的 tex 文件（仅实际修改论文的阶段；纯说明或只读诊断阶段不要求修改 TeX）。
2. `paper/revision_notes/<阶段号>_<名称>.md`，包括：改动摘要；删除内容清单（原文 + 类别或依据）；移动清单；移入 `limitations_pool.md` 的内容；数字变动；待作者确认；改写前后字数；编译页数与警告。
3. 一次 git commit，信息写明阶段与内容。

## 7 待作者决定的事项与暂停条件

阶段 1 前列出的事项（现行批准状态与处理范围以 `01_decisions.md` 为准）：

- D1 目标期刊与语言：**已定**——Bulletin of Mathematical Biology 类英文生物数学期刊。先在 `paper/` 完成中文稿，再译成英文（`paper_en/`）。中文阶段重点是结构、删减、论证逻辑和术语。
- D2 原第 9 节（有效人口比较）的去留：已按 D-02、D-03 批准，正文保留命题 `prop:dom:floor` 及必要条件的短解释；完整表5、人口扫描及案例移入补充材料。
- D3 数学记号：已按 D-04 批准，暂不更换整套数学记号，不改图内文字。
- D4 未完成事项：已按 D-05 批准保留有限证据及原未解决说明，不补算；不将处理方案获批视为数学问题已经解决。
- D5／D-XIAN-LINEAR：**作者已决定；deferred / non-blocking**。暂不研究、追溯、补算或验证西安线性成本反转，不新增反转断言；仅作者另行明确授权后恢复，不作为其他写作的前置条件。保留 $J_c$、$J_q$ 定义、已有二次成本分析、两组四策略比较及西安章节与外部参照。原反转说法不因规则记载而视为已核实。
- D6 拐点分析：已按 D-01、D-02 批准正文保留短小节，完整辅助敏感性及数值迁入补充材料。
- D7 正文图的数量：已按 D-03 批准正文保留10幅，另外14幅完整迁入补充材料；保护安排按实际 label 执行。

遇到以下情况，暂停受影响的内容或任务，把问题写进修改记录并询问作者；不依赖该问题的独立部分可继续：

- `01_decisions.md` 没有覆盖的结构决定；
- 需要删除定理、命题，或改变其陈述；
- 需要新算数值、重新出图或新增文献；
- 遇到已批准处理范围未覆盖的 E 类事项，或拟写结论依赖其未解决问题；已批准保留有限证据及未解决说明的处理不重复请求确认；
- 发现推导或数值的疑似错误。

## 8 已知事实（供查证，不要改动）

- 基准参数：$N=763$，$S_0=762$，$I_0=1$，$\beta=0.155$，$c_0=10$，$q_0=0.01526$，$\gamma=\delta_q=0.3504$，$\eta=0.05N$。
- 西安参数：$N=13\,163\,000$，$\beta=0.1498$，$\gamma=0.2953$，$\delta_q=0.3531$，$c_0=12.8872$，$q_0=0.3230$，$I_0\approx1.00659\times10^{-3}$（未取整值见 `reproducibility/manuscript_audit_notes.md`），$\eta=0.002N=26\,326$（设计情景）。
- TDINN 参照：峰值 152.55，总累计 2105.63，清零时间 45.29 d，$J=49.39$（$w_c=1,w_q=2$）。
- 成本默认权重 $w_c=1,w_q=2$。
- 计算约定（代码整理和补算时遵守）：仅隔离控制的 $q_c(t)$ 是由理论启动点和解析轨迹 $S_{\rm th}(t)$ 得到的**时间开环**控制，不能写成依赖积分器实时 $S(t)$ 的反馈；数值验证检查阈值控制期内 $I(t)$ 是否沿 $\eta$ 运行。联合控制的数值验证同样输入预先生成的开环控制。$J$ 用二次加权形式，$J_c$、$J_q$ 只作分项参考，不相加作综合成本。
- 策略名称：仅隔离控制、仅减少接触、联合阈值控制、TDINN 控制（He–Tang–Xiao 2023 学到的控制函数）、常规控制（$c=c_0,q=q_0$ 的反事实基准）。不用“无控制”“现实控制”。

## 9 已批准的结构与内容分配

当前批准目录与内容分配以 `paper/revision_notes/01_decisions.md` 中明确批准的条目为准。新第5章专述二次成本；两组四策略统一第6章；TDINN 外部参照和必要人口解释在第7章；第8章为讨论与结论。表5完整下沉到补充材料，正文保留人口必要条件和短解释。未列入作者批准范围的建议继续待确认；具体任务仍须由作者另行点名，不自动开始阶段2a或2b。

## 10 常用命令

- 编译（Windows，用 PowerShell，不要用 Git Bash）：`powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1`
- 检查（仓库根目录）：`python paper/tools/check_tex.py --old <比较基准> --new <当前稿件> --bib paper/references.bib --out paper/revision_notes/<阶段号>_check.md`；加 `--hedge` 统计限定性词语，加 `--stats` 统计各节汉字数。
- 提交前：`git status` 确认只改了 `paper/` 下的文件，没有加入 `.aux`、`.log`、`.bbl`、`.pdf`。
