# 任务6a：引言与文献定位

日期：2026-10-07。状态：**作者已验收**。与6b共用起点 `6e6088bfbcd8853d0677c83e695d830aab4c6e6d`（5a、5b已验收），合并保存一次本地提交，不push，不启动任务7。

## 实际修改与结果依据

仅重写 `paper/sections/01_introduction.tex` 的 `sec:introduction`：由峰值限制进入已有容量控制研究，区分接触减少与追踪隔离的机制，再给出固定启动、阈值与退出任务中的分配问题、贡献和八章结构。保留无回流假设、外生阈值身份、原平衡公式和社区感染流量解释；不把已有联合控制研究说成不存在。

| 引言贡献 | 当前实际证据及保留条件 |
|---|---|
| 仅隔离解析基准与阈值权衡 | 第3章 `thm:s1:start`、`thm:s1:platform`、`thm:s1:tend`、`thm:s1:Itcum`、`prop:threshold-tradeoff`；保留触发区间，清零终点累计感染比较带上 `eta>1` |
| 全部联合分配的状态参数化与能力可行性 | `thm:joint:representation`、`cor:joint:feasibility`；有界可测控制、整段允许区间；显式策略族仍只是具体构造 |
| 时长、感染及未感染者隔离的排序 | `thm:joint:comparison`；固定二维起止状态、`0<beta<1`。全过程延伸对应 `cor:joint:whole-epidemic`，保留共同完整初值、`eta>1` 与前后常规控制 |
| 二次成本存在性、有限候选及退出混合分配 | `thm:joint:cost-minimum`、`prop:joint:minimum-threshold`、`prop:joint:terminal-allocation`；正权重、无额外跨状态约束，阈值变化限于触发且整段可行范围；严格单控制比较在无额外能力限制下转述 |
| 规定退出目标的感染下界 | `prop:exit-infection-lower-bound`；从初始时刻到有限时刻达到 `S=S_c` 的总累计新增感染，不改成单个仓室或控制期指标 |

两组四策略仍以共同完整初值、阈值及启动/退出要求比较。TDINN仍是任务不同的外部重构参照；有限能力代表点、权重网格和离散匹配乘子点未扩大为连续范围的认证。D-XIAN-LINEAR继续deferred / non-blocking。

## 文献定位的实际复核

引言15个引用键与上轮相同，未新增或补全bib条目。下表记录本轮实际读到的摘要、模型或直接相关段落；并非15篇全文重新审计。仅压缩原论断及重复引用，没有改作支持其他论断。

| 既有引用键 | 本轮来源与引言用途 |
|---|---|
| `Ferguson2020Report9` | [Imperial官方仓储摘要](https://spiral.imperial.ac.uk/entities/publication/ab151e2b-3acb-4bc3-a87a-7a747e8ae51a)：医疗需求高峰与多措施配合 |
| `Duque2020` | 本地 `Timing social distancing to avert unmanageableCOVID-19 hospital surges.pdf`，PDF第1页：医院容量与短期干预的启动规则 |
| `Miclo2022ICU` | 本地 `Optimal epidemic suppression under an ICU constraint An analytical.pdf`，PDF第1、3页：SIR、特定线性成本下的恒定感染结构 |
| `Avram2022` | 本地 `Optimal control of a SIR epidemic with ICU constraints and target objectives.pdf`，PDF第1页：能力、可行区域与退出任务 |
| `Angulo2021` | 本地 `angulo-et-al-a-simple-criterion-to-design-optimal-non-pharmaceutical-interventions-for-mitigating-ep.pdf`，PDF第1、2、4页：峰值约束下能力与时长、必要时提前启动 |
| `Balderrama2024` | 本地 `Optimal control for an SIR model with limited hospitalised patients.pdf`，PDF第1、2页：累计干预与感染峰值限制下的最终感染规模 |
| `Hellewell2020` | [原论文摘要及相关正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7097845/)：追踪覆盖与响应延迟 |
| `Ferretti2020` | [Science原论文摘要与图3相关内容](https://doi.org/10.1126/science.abb6936)：追踪覆盖与延迟 |
| `Kucharski2020` | [原论文摘要、方法与结果](https://pmc.ncbi.nlm.nih.gov/articles/PMC7511527/)：措施组合与需隔离接触者数量 |
| `Tang2020Transmission` | 本地 `Estimation of the Transmission Risk of the 2019-nCoV and Its Implication for Public Health Interventions.pdf`，PDF第4页：被追踪感染者和未感染者分仓；未将其回流设定等同于本文 |
| `Zhou2024SPCI` | 本地 `Tang_Zhou_2024_JMB.pdf`，PDF第1—6页：分段控制、首次积分及非隔离感染者传播 |
| `He2023TDINN` | 本地 `He_Tang2023PCB.pdf`，PDF第1页：时间控制函数的数据重构 |
| `Charpentier2020` | 本地 `COVID-19 pandemic control balancing detection policy and lockdown intervention under ICU sustainability.pdf`，PDF第1页：ICU约束下检测与封控的联合分配 |
| `Pollinger2023` | [Oxford原论文摘要](https://doi.org/10.1093/ej/uead024)：追踪与社交距离的联合抑制 |
| `Balakrishnan2023` | 本地 `一种自适应测试策略，有助于在疫情期间有效利用医疗资源.pdf`，PDF第2页：动态检测与医疗资源使用目标 |

主文入口按AGENTS.md第5节加入 `\ExecuteBibliographyOptions{sorting=none}`。Biber及原numeric体例保留，未切换模板；实际BBL中的17个主文条目顺序与首次引用一致。补充入口和bib均未改。

## 删除、移动与数字

以下是删除或替换的原文锚点；完整逐段改写可由本轮Git diff查看。

| 原文 | 类别／处理依据 |
|---|---|
| “在未提前改变的常规轨迹上，首次触及阈值之前尚未违反感染上限……” | B：删去对规定过程的重复论证，模型2.2保留完整条件；引言改为回指 `eq:model:trigger` 并明确二维起止状态 |
| “本文需要解决的问题不是首次将两种干预与容量约束放在一起……” | D：改为正面陈述具体分配问题，已有联合控制文献及原支持关系保留 |
| “这里研究的是实现这一规定过程所需的措施及其代价，而非预先假定某一种措施组合最优。” | B/D：作用域并入控制类定义及结果条件，不重复元评论 |
| “提高感染阈值虽然降低最大隔离强度、控制时长和成本，却增加累计新增感染。” | A：改写时补明触发区间，清零累计感染的 `eta>1` 条件；不是删除原结果 |
| “先采用 $N=763$ 的基准参数……” | D：删去引言中一次重复人口值，完整基准参数仍在6.2、图注和补充S1 |
| “其控制时长和累计新增感染严格介于两者之间……” | B：引言压缩同条件数值与成本说明，原完整结论及条件仍在第4—6章 |

无跨文件迁移，无内容移入 `limitations_pool.md`。数字字面量693→692，仅删除引言中重复的763，新增0；参数组、策略、指标、终点与单位未变，没有修改表格精度或新算数值。

## 实际检查与待配合项

- 17份正式TeX中仅引言和主文入口改变，其余15份逐文件字节相同；完整证明、数学块、24个图源哈希、图块尺寸、bib及有效宏 `jointcapacitypostexitdays` 保留。四保护图按实际label保留。
- 本轮 `check_tex.py` 展开15个输入，220个label全部保留；缺失、悬空、重复及bib缺键均0，两个既有未引用bib条目不变。报告见 `06ab_check.md`。
- 最终按 `paper/build.ps1` 先补充后主文，各执行XeLaTeX→Biber→XeLaTeX→XeLaTeX，主文36页、补充21页。未定义引用、重复标签、Overfull/Underfull、LaTeX/Package Warning、Biber WARN/ERROR均0，PDF无 `[?]`。沙箱内Biber发生Windows DLL启动错误，同一入口在沙箱外实际构建成功；Perl locale回退启动提示单列保留，未计作“无环境提示”。
- 前后全部36+21页渲染比较：主文10页像素相同，26个变化页均实际查看，摘要、引言、模型衔接、公式、图表及文献无裁切或重叠；补充21页逐页像素相同，复用5a、5b已验收视觉检查。38个跨文档PDF链接目标有效。
- **待配合修版：** 引言压缩后的正文重排使6.2末句“……其下方的常规感染峰值低于阈值，无需启动仅隔离控制。”在18页断开，两张图所在的19—20页之后，仅“仅隔离控制。”落在20页。内容无丢失。依AGENTS.md第1节，其他章节的配合修改登记于此，本轮不改第6章；后续可单独点名局部版式处理。
- 去注释汉字数（含章标题、不计数学和英文）：引言3038→2071；展开主文23964→22952、补充8145→8145。摘要和关键词口径见6b记录。
- 未运行研究计算、重拟合、重绘、Linux构建或独立数学认证。基线、既有未跟踪材料、执行手册、PDF、编译产物和临时证据不纳入本轮提交。

待作者确认：无新增科学或结构决定；上述版式配合项已登记。标题选择见 `06b_front_matter.md`。

## 验收登记

2026-10-07：作者明确回复“我验收了”，确认执行提交 `4b7e685303106f36b853b4c8b1a5353ff35686ca` 的实际交付。本次仅更新6a、6b记录及STATUS的验收状态，未修改论文、未重新构建；检查沿用执行轮记录及 `06ab_check.md`。当前题目保留，三个候选仍待选择，6.2局部版式配合项保持原登记，未启动任务7。
