# NEW-4f 文献定位与主线聚焦修订记录

## 1 基准与范围（F0）

- 作者2026-10-20明确要求按 `ai/NEW_4f_focused_revision_plan_20261020.md` 执行；不使用 nature 系列技能。根规则新增N16，保留其他冻结要求。
- `NEW_4F_BASE_COMMIT=7743c3809026fe96d118234ea4d05fb5bad6c226`。本地分支 `paper/submission-ready` 与远端同名分支于本轮只读核对一致，无需拉取或回退；历史 `NEW_BASE_COMMIT` 不变。
- 初始已跟踪文件无差异；计划文件及12份 `NEW_literature*20261020*` 记录为既有未跟踪文件，原样保留，不自动暂存。初始清单、SHA-256、既有文件副本和两份基准PDF存于忽略目录 `paper/tmp/NEW_4f_baseline/`，不入库。
- 本轮按F1、F2、F3、F3b、F4分别登记和本地提交。稿件源文件提交均附本步源文件编译的两份PDF。文献原文核对、静态检查和实际构建属于本轮工作；历史科学复现仅沿用已有结果，不重跑、不称为本轮复算。
- 九章结构、模型方程、既有定理数学含义和证明逻辑、参数、初值、表值、图及计算来源冻结。新增数学说明仅为一条综合人数代价注记。

## 2 文献定位与来源证据（F1）

段落蓝图：首段传染病背景逐字保留；第二段保留社会经济代价与缓解/压制动机，连接优化问题；文献部分按容量阶段、退出要求、追踪隔离机制、已有模型与联合控制组织。研究问题和贡献列表保持，贡献(4)弱单调作必要一致性修复（F3b-X22）。讨论8.2只重定位共同阈值阶段内的自由度及精确关系。

页码均指所列 PDF 的从 1 开始页码，表中明确给刊页处除外。复用全文不等于本轮重新下载或通读全篇。

| 文献 | 本轮实际核对的原文及位置 | 模型、控制、目标与终点 | 入稿用途 |
| --- | --- | --- | --- |
| Miclo, Spiro, Weibull (2022) | 本地正式发表版 `paper/tmp/literature_review_20261020/ref_13.txt`；PDF p.1 摘要、p.5 成本与问题、pp.22–23 控制结构。对应原 PDF `refs/Optimal epidemic suppression under an ICU constraint An analytical.pdf` 的文件身份以既有 manifest 为准；[DOI](https://doi.org/10.1016/j.jmateco.2022.102669) | 单一传播抑制控制、ICU 感染上界、线性抑制代价；恢复常规传播与达到群体免疫阈值相连。本轮使用正式 2022 版，未把早期经济成本版本混入。 | 引言容量阶段、退出方式；讨论 8.2 容量阶段的对应。 |
| Angulo et al. (2021) | 本地正式刊稿 `ref_02.txt`，PDF p.3 Box 1（SIR 模型、安全区定义式(2.1)、最短到达时间目标）；pp.3–5 §2.1–2.3（可行区域与最优反馈）。[DOI](https://doi.org/10.1098/rsif.2020.0803) | 安全区是恢复零额外干预后对全部未来时刻满足感染上界的最大集合，允许安全区内感染先上升但不越界。目标是最短时间到达安全区，不是本文模型之外的控制时长。 | 引言两处改成原始目标；讨论 8.2 保留阈值策略内对应。 |
| Avram, Freddi, Goreac (2022) | 本地正式刊稿及附带更正 `ref_09.txt`；PDF pp.1–2 式(1.1)、(1.2)与严格目标，相关最优反馈段。原 PDF 共25页，最后附更正；本轮没有把本稿退出时刻说成其固定终点。[DOI](https://doi.org/10.1016/j.amc.2021.126816) | 有界单传播率控制；固定监测时域；努力代价；末状态要求易感比例严格低于群体免疫阈值。结束容量阶段/恢复常规传播与整个优化问题的固定终点须区别。 | 引言容量段和退出段明确这一区别；讨论只说恢复常规传播时刻的对应。 |
| Balderrama et al. (2024) | 本地正式刊稿 `ref_08.txt`，PDF pp.2–3 式(1)–(5)、p.7 定理4.1/式(39)；对照 `source_completion_C.md` 的定位后回查相关原文。[DOI](https://doi.org/10.1016/j.mbs.2024.109317) | 单一时变再生数；有限干预时段、感染上界与累计预算；最大化最终易感比例。容量弧之后可接严格措施，不能把其开始点写成已经达到群体免疫。 | 保留最终感染规模目标，退出句改成“离开容量边界后接续一段部分封控”。 |
| Freddi, Goreac, Li, Xu (2022) | 复用 `freddi_statecost_arxiv_pdf.txt`（作者稿 arXiv:2110.11625v2，2022-05-18），PDF pp.7–10 §3、式(6)–(11)、定理2/式(15)；核对 p.12 具体成本例子；正式元数据本轮重新查询 Crossref。[作者稿](https://arxiv.org/pdf/2110.11625v2)、[DOI](https://doi.org/10.1007/s00245-022-09884-x) | 在感染上界下到达安全区前的状态依赖运行成本；贪心最优性要求相应成本比较条件与验证条件。没有说任意状态成本都成立。 | 一句说明最优容量阶段依赖成本，Hamilton–Jacobi 验证有条件。 |
| Freddi, Goreac (2024) | 复用出版社正式 PDF 提取 `freddi_goreac_infinite_2024.txt`；PDF p.2/刊页526 式(2)，pp.31–32/刊页555–556 注9.8、定理9.9，p.35/刊页559 例10.3；本轮打开出版社网页并重新查 Crossref。[期刊页](https://journalofconvexanalysis.com/articles/jca31028/)、[正式 PDF](https://journalofconvexanalysis.com/articles/jca31028/jca31028.pdf) | 无限时域 SIR，成本为控制强度与感染存量的加权积分；定理9.9允许容量弧之后再用最大干预，各段可退化。 | 引言一句说明状态成本可改变容量弧之外的最优阶段，不据此要求本文解决一般状态约束双控制问题。 |
| Molina, Rapaport (2022) | 本轮联网打开并核读 [arXiv:2203.05800v1 PDF](https://arxiv.org/pdf/2203.05800)，11页作者稿，封面日期2022-03-14，arXiv标记2022-03-11。实际相关范围为 pp.1–5：§2 式(1)–(4)、§3 定义1/式(6)、§4 命题2；正式发表信息由本轮 Crossref 与[出版社摘要页](https://www.sciencedirect.com/science/article/abs/pii/S0005109822004587)交叉确认。 | SIR 的传播衰减控制；控制的 L1 预算；最小化全时域感染峰值。维持感染至免疫阈值、阶段之外不干预的 NSN 反馈。 | 引言维持阶段的不同目标背景；没有称与本文优化问题相同。 |
| Pollinger (2023) | 复用 `paper/tmp/literature_followup_20261020/tracing/pollinger_working.txt`：首页标明 Final Working Paper Version, 2022-12-08，含正式2023卷页。实际核读 pp.5–7 式(1)–(3)、一般追踪成本说明，pp.9–12 命题1、Assumption 1、式(4)、命题2；不是声称本轮取得出版社排版80页全文。[作者 Research 页](https://www.stefanpollinger.com/research)、[DOI](https://doi.org/10.1093/ej/uead024) | 社交距离改变传播；追踪用感染者检测移出率表示；成本包含病例和接触者的隔离/隐私损失。闭式约化利用小规模暴发压制下易感者近似固定、感染者严格下降，以感染者代替时间。 | 引言2句介绍已有联合选择和近似约化，再与本文固定 I、下降 S 的精确约化及人数关系比较；讨论8.2不重复成本细节。 |
| Tang et al. (2020) | 本地 `ref_05.txt`，PDF p.4 式(1)及模型分流，p.5–6 参数与回流说明；对照既有 `source_completion_B.md` 定位。原文保留隔离易感者回流，未据此声称其模型也是无回流。[DOI](https://doi.org/10.3390/jcm9020462) | SEIR型模型把追踪接触者按感染状态分流，不是本文的阈值组合最优控制。 | 追踪隔离机制和模型来源。 |
| He, Tang, Xiao (2023) | 本地正式刊稿 `ref_06.txt`，PDF pp.6–9 模型式(1)、参数表、TDINN数据/方程损失；pp.13–14 率函数式(4)、(5)与表3；未重跑网络或拟合。[DOI](https://doi.org/10.1371/journal.pcbi.1011535) | 短期模型忽略隔离易感者回流；重构时变 c、q；西安率函数及参数提供情景和外部参照，训练优化不等于本稿干预成本优化。 | 引言明确五仓室模型与数据重构来源。 |
| Zhou, Sha, Cheke, Tang (2024) | 本地正式刊稿 `ref_17.txt`，PDF pp.4–7 模型式(2.1)、分段干预式(2.2)、闭合子系统/首次积分式(3.1)、(3.2)；pp.21–22 §6 式(6.1)、(6.2)与双目标解释。检索后核读这些相关式段，未复算图或拟合。[DOI](https://doi.org/10.1007/s00285-024-02083-y) | 分段常数 c、q，联合选择干预启停时刻和强度，双目标为非隔离峰值与隔离区外清零时间；首次积分是既有方法。 | 引言与讨论都准确承认先行联合选择，本文差别落在全部阈值组合、精确人数排序和成本结构。 |
| Arnouss, Hayel, Allali (2026) | 本轮出版社网页搜索返回实际公开 §2 “Model dynamics” 与式(1)，并读到正式摘要；不是只从检索摘要推断模型。公开式(1)为 S'=-βSI，I'=βSI-γI-uI，Q'=uI-γqQ；§2文字明确 u 是感染者隔离率。预算峰值目标由摘要明确陈述。本轮 Crossref 核元数据。[出版社原页](https://www.sciencedirect.com/science/article/abs/pii/S2468601826000076)、[DOI](https://doi.org/10.1016/j.ifacsc.2026.100367) | 隔离仓室的流入只来自感染者；预算约束下峰值最小化。未通读全部证明，不援引其“相同预算”比较或数值感染结论验证本稿。 | 引言仅一句对照隔离对象与本稿未感染者移出机制。 |
| Duque et al. (2020) | 本地正式刊稿 `ref_18.txt`，PDF p.2 Results、p.3 图1图注、p.6 概率约束/目标；新增入院的7日移动平均与住院存量明确分开。[DOI](https://doi.org/10.1073/pnas.2009033117) | 随机优化以新增入院移动平均触发封控；超容量事件的概率约束；最小预期封控天数。没有把概率约束改说成每条随机轨迹的保证。 | 引言背景结尾的精准替换；正文只新增原文的7日平滑窗口，不加入其城市阈值和概率数值。 |
| Charpentier et al. (2020) | 本地 `ref_04.txt`，模型/成本 pp.5–12，p.32 图B.8对应原文段；对照已有来源补读A。 | 检测与封控的联合数值优化；仅封控时出现ICU饱和平台，联合检测时该平台在所列情景可消失。 | 修正把仅封控平台推广到联合方案的旧表述，仅按情景说。 |
| Grundel et al. (2022) | 本地 `ref_07.txt` 为 arXiv:2011.01282v1，PDF pp.11–14相关检测能力与联合控制段、结论；正式2022条目沿用现有 bibliography。没有把作者稿编号冒称刊稿编号。 | 年龄分组、检测与社交距离；“仅检测不足”绑定其现实检测能力限制，非任意能力下的不可能性定理。 | 引言联合干预段补足能力条件。 |

已有开头背景及其引用保持现有证据，不另发起一轮背景检索。Ferguson、Ji、Flaxman、Nicola等没有被本轮列作重新通读或重新验证的来源。

Angulo三处已统一为原始安全区时间目标。讨论中保留其与本文时长目标的对应：`prop:model:threshold-rationale`(iii)保证沿 `I=eta` 的轨迹首次到达 `S_c` 是此后恢复常规且不再越界的最早时刻；各控制共享 `t_1`，故该时刻最小等价于控制时长最短。再由 `cor:joint:whole-epidemic` 得无回流最终感染规模的相同最优控制。未将两篇文章的整个优化问题等同。

四条新增文献均实际引用，正式作者、题名、卷期/文章号/页码与DOI已核。Freddi–Goreac(2024)采用出版社正式DOI `10.68381/jca31028`。四份本轮Crossref响应存于 `paper/tmp/NEW_4f_*_crossref.json`；复用全文与本轮新取得的作者PDF/出版社片段已在上表区分。Arnouss仅核公开模型节式(1)与摘要，没有取得排版全文PDF，不援引其未核证明或数值结论。

### 删除、合并与数字登记

- 第一段（SARS/H1N1/COVID-19、医疗负担与死亡、非药物措施及欧洲11国结果）逐字保留，既有证据与数字均保留。
- 第二段保留干预难以长期维持、社会经济负担、Ferguson的两类策略及组合需要；删去“传统设计把再生数压到1以下”的旁枝与重复Angulo判据，把优化动机改为医疗容量和代价共同决定启停与强度。Angulo本身并未删除，移到专门目标比较处准确介绍。
- 原 He 段“中国2022年10月以前几乎所有疫情约40天清零”的历史背景句不再进入引言。原数字 `2022年10月`、`约40天`保存在本记录，出处为He2023 PDF p.2；删除理由是该细节与本文阈值组合的研究缺口无直接关系，且现有第7章继续完整说明外部参照及其终点。未删改本文任何实验结果数字。
- He 的地区差异细节合并为模型/数据重构来源，保留其为西安参数情景与外部参照的作用。
- 删去 Balakrishnan 的设施利用不足与检测资源调节两处旁例，避免把文献定位扩成逐篇清单；原 bibliography 条目仍保留，不为“全部条目被引”强行安排位置。
- Balderrama 与 Ketcheson 的前作关系从引言删去，保留本轮真正需要的有限时段、预算、感染上界及最终感染规模目标；未改Ketcheson条目或其研究结论。
- 去掉对所有模型统一采用“充分利用容量又不施加多余干预”的解释，改为目标与约束决定容量阶段的进入和离开。
- 去掉“这些工作都没有研究……”的全称空白断言，以本文已证明的可行组合、精确人数关系与成本结构正面界定问题。

F1实际验证：Windows标准入口在沙箱内的biber启动时报 `Illegal System DLL Relocation`；随后同一入口在授权环境完成，主稿39页/补充20页，undefined=0、multiply defined=0、超过10pt的Overfull=0。已目视主稿第2、29页的文献段落和引用。check_tex标签缺失/悬空/重复/缺bib均为0；数字字面量减少的10、2022、40来自上列He历史背景，未改参数、初值或表值。构建日志留 `paper/tmp/NEW_4f_QA/F1/`。

## 3 综合人数代价推导（F2）

第5.4节末仅新增 `remarkn` 注记 `rem:joint:headcount-cost`，不新增小节、定理、图表或全局记号。固定无回流模型、阈值和同一非空允许类，局部记

\[
D=S^*-S_c,\quad C=I_{t_{\rm cum}}(t_2)-I_{t_{\rm cum}}(t_1),\quad Q=S_q(t_2)-S_q(t_1).
\]

由已有 `eq:joint:cumulative`、`eq:joint:quarantine`，

\[
C=\beta D+(1-\beta)\gamma\eta\Delta t,\qquad Q=(1-\beta)D-(1-\beta)\gamma\eta\Delta t.
\]

因此 `C+Q=D`，对非负人数权重有

\[
J+a_IC+a_QQ=[\beta a_I+(1-\beta)a_Q]D+J+\kappa\Delta t,\qquad
\kappa=(1-\beta)\gamma\eta(a_I-a_Q).
\]

`C`为进入两个感染仓室的总新增感染，不是仅社区累计；`Q`为同一阈值控制期的新增人数，不是存量或人天。J单位为天，a_I、a_Q为时间/人数，kappa无量纲，未作货币化。a_I>a_Q惩罚较长控制期，a_I<a_Q偏重减少隔离人数，二者相等时人数项为常数。原J的定义、权重、数值均不变。

已独立检查符号展开，人数代价恒等式与C+Q=D的残差均为0，无数值求解。任意有限正负kappa均可调用现有存在性和逐状态最小化论证；原允许时长有有限上下界，不会因负kappa使目标无界。时长前沿只在内点T保证有限匹配乘子，不扩大到端点。未将原J的驻点方程系数、连续结构、切换位置、能力截断或阈值单调性外推到kappa非零。

F2实际验证：标准入口构建主稿40页/补充20页；两份undefined=0、multiply defined=0、Overfull=0、缺字0。statement_diff：既有40条带标签陈述与24条配对证明均未变，仅新增 `rem:joint:headcount-cost`。已对短注记加局部 `Needspace`，避免注记开头与公式分处两页；该排版指令不改变内容。已目视主稿第19页注记、公式与后续标题，排版正常。最终本步日志与阶段报告留 `paper/tmp/NEW_4f_QA/F2/`。

## 4 生物学解释与一致性（F3）

| 文献 | 拟支持的正文句 | 模型、控制、目标或终点 | 核对的原文位置与版本 | 使用限度与入稿位置 |
| --- | --- | --- | --- | --- |
| Britton, Ball & Trapman (2020), Science 369(6505), 846–849; DOI 10.1126/science.abc6810 | 接触活动度等人群异质性会改变解除干预所需的免疫积累条件 | 年龄与活动度结构的 SEIR，结构化接触矩阵；比例干预后恢复原传播水平，比较能否再起疫情 | [期刊 DOI](https://doi.org/10.1126/science.abc6810)；[PubMed 正式元数据](https://pubmed.ncbi.nlm.nih.gov/32576668/)；[期刊全文 JATS](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7331793/fullTextXML)。已核正文关于 next-generation matrix 的段落及恢复干预的设定；本地 `NEW_4f_F3_sources/Britton2020.txt` 段 010、013、015–020、040–041 | 只作讨论局限一句；年龄/活动度会改变结构化临界条件，不得据该文示例降低本文标量 S_c 或校正西安数值；本文退出下界在结构化模型中须另推 |
| Ashcroft et al. (2021), eLife 10, e63704; DOI 10.7554/eLife.63704 | 隔离时长与检测释放规则影响传播；7 d 量级在已有研究中出现，指数停留与固定期限不同 | 感染后传染性分布，暴露时刻 t_E、进入 t_Q、释放 t_R；固定期限与阴性检测后释放 | [期刊页面](https://elifesciences.org/articles/63704)；[期刊 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7963476/fullTextXML)。正文 Results / Model description 与 Quarantining traced contacts、Materials and methods / Traced contacts，式 (1)–(4)、图 2；现有本地 `literature_followup_20261020/root/Ashcroft2021_fulltext.txt` 行 21、38、69–72、190。正式期刊文，eLife 页面区分 2021-02-05 accepted manuscript 与 2021-03-16 version of record | 其主要直接比较为 10 d 与 7 d（以及检测方案），全文正文不直接给出 14 d 的采用说明。不能单独用它支持明确的“7、14 d”；也不能把从末次暴露起计算的期限作为进入 S_q 后指数均值的经验校准 |
| Wells et al. (2021), Nature Communications 12, 356; DOI 10.1038/s41467-020-20742-8 | 7、14 d 是已有隔离及检测研究涉及的时间尺度 | 根据感染时间信息区分旅行隔离、追踪接触者与已知暴露时刻，比较检测时间与隔离后传播概率；终点为隔离结束后的传播事件概率 | [出版社正式全文](https://www.nature.com/articles/s41467-020-20742-8)，Version of Record 2021-01-07；Introduction 第 1–3 段及 Results / Accounting for the prevalence of the disease and contact tracing，图 3 明确画 1–14 d，相关正文明确比较 7 d 检测释放与 14 d 无检测；作者表、About this article 已核 | 计划允许“按需 Wells”，此处 Ashcroft 对 14 d 的直接支撑不足，加入它有具体用途。只援引时间尺度与不同释放机制，不引入其百分比、最优天数或临床结论。用于补充 S5 数值段 |
| Allen (2017), Infectious Disease Modelling 2(2), 128–142; DOI 10.1016/j.idm.2017.03.001 | I=1 是确定性模型的操作性终点，低人数阶段的随机灭绝另需随机模型描述 | SIR 的 ODE、CTMC、SDE；分枝过程近似灭绝概率，CTMC 在 I=0 吸收 | [期刊 DOI](https://doi.org/10.1016/j.idm.2017.03.001)；[正式元数据](https://pubmed.ncbi.nlm.nih.gov/29928733/)；[期刊全文 JATS](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6002090/fullTextXML)。Introduction 第二段；3.3 Branching process approximation；3.4 Numerical simulation 的 I=0 吸收句。本地 `NEW_4f_F3_sources/Allen2017.txt` 段 009、066–068、077 | 支持低感染数下随机性与灭绝的解释；不支持把 I=1 解释为灭绝已发生，也不据初期分枝近似给本文尾部估计概率。入稿讨论既有局限句 |
| Hellewell et al. (2020), 已有 Hellewell2020 | 从出现症状到隔离的延迟会降低控制效果 | 分枝过程，病例出现症状后隔离，延迟改变隔离前可发生的继发感染；Methods 明言只隔离症状者、no quarantine | [期刊全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7097845/)；[JATS](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7097845/fullTextXML)，Methods / Model structure，第 2 段与最后数段；图 1、图 4 及 Results 对长短延迟的比较 | 可以支持病例隔离及时性，单独用它支持本文未感染接触者进入 S_q 的追踪过程不够准确；与 Ferretti 现有引文合用即可 |
| Ferretti et al. (2020), 已有 Ferretti2020 | 病例发现及接触者追踪隔离的延迟会削弱及时隔离效果 | 传染性核与传播路径，病例隔离和接触者追踪隔离；图 3 比较从出现症状至隔离/接触者隔离的延迟 | [期刊 DOI](https://doi.org/10.1126/science.abb6936)；[JATS](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7164555/fullTextXML)，Modeling case isolation and contract tracing with quarantine 及图 3；本地 `NEW_4f_F3_sources/Ferretti2020.txt` 段 066–071 | 足以和 Hellewell 支持一条定性的延迟局限，不需新增 Kretzschmar。不得移植其特定 3 d 场景作本文通用临界值 |

上述 JATS 下载收据及 SHA-256 位于 `paper/tmp/NEW_4f_F3_sources/receipts.json`。Ashcroft 的现有 XML 在本轮重新逐段核对，没有仅采信旧补读记录。Wells 本轮直接读取出版社 HTML 并核对所需段落；未声称完整通读独立补充材料。

本步修改映射：

- 模型章命题后恢复“启动前保持常规控制”的条件，去掉医疗资源已接近饱和的推断，用达到所选I阈值及S降到S_c的阶段解释（兼F3b-1）。
- 讨论8.1用“易感水平较高的控制前段”替换“疫情压力最大/一举两得”，保留追踪同时维持阈值并较快减少社区易感者的机制（兼F3b-10）；退出解释仅加一处尾部感染说明。
- 讨论局限补异质性一句、在已有延迟和低人数终点句后给依据；展望将笼统“反馈控制”改为观测、状态估计和执行误差下的阈值跟踪与纠偏。解析c_c^*(S)本来就是状态反馈，没有把它说成不存在。
- 补充S5保留7/14/30d和18条原数值；7/14d为文献涉及的时间尺度，30d为较长停留情景，指数停留与固定期限或检测释放区分。Ashcroft直接涉及7/10d，单独不足以准确支持14d，故按计划“按需Wells”补足。
- 补充S5旧“连续性未证”改成默认无回流反馈连续性已有定理，正回流中只作迁移、不重新优化；条件性右不连续推论的有解假设原样保留，不由连续性推唯一性。

无回流且退出后永久采用常规控制时，

\[
F=\frac{\beta c_0SI}{N},\qquad -\dot S=\frac{c_0[\beta+(1-\beta)q_0]SI}{N},\qquad
C_{\rm post}=\frac{\beta}{\beta+(1-\beta)q_0}(S_c-S_\infty).
\]

该分解即 `thm:s1:Itcum` / `eq:s1:cumulative` 常规阶段第一项的退出后贡献，不新增编号公式或命题。q_0=0时比例为1；q_0>0时比例小于1，其余S减少进入未感染S_q。因此不能把全部S_c-S_infty称为感染，也不把此比例式用于正回流模型。

本步没有新增隔离人天说明公式、医疗新仓室或优化结果；已有Hellewell/Ferretti足够支持采用的定性延迟句，未新增Kretzschmar。四篇新来源均实际被引用。F3实际验证：标准入口构建主稿40页/补充20页；两份undefined=0、multiply defined=0、Overfull=0、缺字0。已目视主稿第31页和补充第16页，文献引用、连续性说明、回流场景与原表排版正常。check_tex标签缺失/悬空/重复/缺bib均为0；新增数字字面量14、30是原场景在解释句中再次出现。范围核对：既有40条定理类环境与全部34段证明未变、编号公式未变、初始13份未跟踪文件未变；日志留 `paper/tmp/NEW_4f_QA/F3/`。

## 5 NEW-4e解释句复核（F3b）

待逐条核对计划表内15项及表外句。

## 6 暂缓与搁置事项

### 6.1 每日处理能力仅留记录

进入两个隔离仓室的总接触者流量为

\[
B_q=\frac{cqSI}{N}=\dot S_q+\left(\text{进入 }I_q\text{ 的流量}\right),
\]

这里S_q等式指无回流时的新增流入；正回流时应把S_q的净变化加回回流量，仍以进入隔离仓室的流入定义B_q。在阈值期I=eta、平衡关系成立时，

\[
B_q=\frac{\gamma\eta q}{\beta(1-q)},\qquad
B_q\le K_{\rm d}\iff q\le\frac{\beta K_{\rm d}}{\beta K_{\rm d}+\gamma\eta}.
\]

两隔离流量分别是(1-beta)cqSI/N和beta cqSI/N，相加才得B_q（人/天）；它不是全部电话联系、排查或检测量，也不是隔离床位存量。对K_d非负、q<1，比例上限不低于q_0的必要条件为

\[
K_{\rm d}\ge\frac{\gamma\eta q_0}{\beta(1-q_0)}.
\]

若另有c_min，仍须检查原完整可行性条件，不能把上述必要条件当充分条件。该代换已符号核验，无数值模拟。固定K_d时比例上限随eta变化，会引出新的跨阈值可行性与成本问题；原固定能力参数的阈值单调性不能直接沿用，也不能只凭比例上限下降就断言可行性对所有参数变差。全过程限制须另查启动前轨迹。本轮正文与补充仍采用原固定c_min、q_cap，不加入上述公式或额外限定。有限能力背景仅留[Contreras等DOI指针](https://doi.org/10.1038/s41467-020-20699-8)，未据该文作本文已复现的动力学临界点判断。

### 6.2 有效人口整体搁置

- 已有结果位置：`reproducibility/results/20261003_release_final/population/critical.json`、`representative_summary.csv` 等；原S4文本在 `paper/revision_notes/archive/NR_6_removed/S4_population.tex`。
- 不恢复原S4，不重新引用 `fig_dom_combined.pdf`、`population_threshold_levers.pdf`、`fig_panel_B_trajectory_decomposition.pdf`、`critical_population_cases.pdf`；不运行 `xian_dom/`、`reproducibility/population.py` 或新的有效人口计算。第7.4节、补充S3.1与 `prop:dom:floor` 保持原样。
- 后续讨论方向仅留指针：将TDINN拟合结果作为固定实际结局参照，只比较可观测或人口无关指标（总累计感染、清零时间、社区日新增峰值；阈值期社区日新增为gamma eta），约束N_eff>=N_floor，考察数据允许的全部有效人口上的界；J^T与非隔离感染者峰值不宜作固定参照。
- 已知相容性风险：沿用全市人口下重构的c(t)、q(t)，N_eff在10^4量级时不能重现观测曲线。严格比较须在N_eff下重新估计参数，属于冻结的西安重新拟合。
- F3b核读中另记录补充S3.1的一处证据界限：其“0.1倍与10倍初值并不与观测相符”不能仅由六条阈值轨迹证明；现有表本身没有这些初值下TDINN观测残差。本轮按冻结要求原样保留，不重算、不判为已发现模型错误，随未来初值/有效人口任务再核。

隔离人天核算、线性成本、其他退出目标与综合成本扫描均不扩展；没有把新增人数乘外加停留天数当作人天结果。

## 7 验证与交付（F4）

待实际构建、静态检查和受影响页面检查完成后填写；本记录不代表作者验收。
