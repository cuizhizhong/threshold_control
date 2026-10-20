# 参考文献对照与稿件审阅

审阅日期为 2026-10-20。对象为分支 `paper/submission-ready`、提交 `7743c3809026fe96d118234ea4d05fb5bad6c226` 的中文主稿与补充材料，现有 PDF 分别为 39 页与 20 页。本轮只做阅读、来源检索和确定性核对，没有修改 TeX、图件、参数、表值或数字宏，没有运行新优化、ODE 复现、权重扫描、西安拟合，也没有编译或提交。

## 审阅设置

- 输入为主稿九章、附录 A/B、补充全部六个分节、参考文献和数字宏，以及 `refs/` 的 19 份 PDF。19 份文件包括 Miclo 同文的两个版本、Angulo 补充材料、一份 Angulo 讲稿及 Liberzon 教材，不能当作 19 篇彼此独立的研究论文。
- 目标是 BMB 类生物数学理论论文。评价原创性、技术正确性、流行病学解释、可复现性和可读性，不以 Nature 的跨学科广泛性作为门槛。
- 三个预设重心分别为先行工作与数学定位、模型与流行病学解释、成本数值与可复现性。三份报告在隔离上下文中形成，未互看意见，完成后冻结。后续来源补读和本报告的一致性核对不回写原报告。
- 本轮在线检索通过 Crossref 与 PubMed 公开 API 完成。内置网页检索连接失败，改用允许联网环境中的只读公开 API。取得了 Freddi–Goreac 2024 的期刊公开全文，以及 Freddi–Goreac–Li–Xu 2022 的作者稿 v2，后者的正式出版信息经出版社页面核对。
- 原文提取、输入 SHA-256、在线原始响应和下载收据位于 `paper/tmp/literature_review_20261020/`。Angulo 扫描补充采用与当前 PDF 字节完全一致的既有 OCR，另对当前 PDF 重新渲染全部 20 页；OCR 用于检索，重要公式回看图像。

## 三份独立报告

1. [R1 先行工作与数学定位](NEW_literature_review_20261020_R1.md)。无 Major，4 项 Minor。
2. [R2 模型与流行病学解释](NEW_literature_review_20261020_R2.md)。无 Major，6 项 Minor。
3. [R3 成本数值与可复现性](NEW_literature_review_20261020_R3.md)。1 项 Major，Blocking No，另有 2 项 Minor。

报告中的重复意见属于独立形成的重合，未为增加差异而重写。三个报告均未提出 Blocking Yes 问题。R3 的 Major 指向投稿读者能否定位数值实现的同一版本，不是指本地没有代码、现有结果失效或需要本轮重新计算。

## 综合评价

现稿有明确、可继续推进的理论主线。本轮未发现足以推翻主要论证的证据，但这不是全部证明的形式认证或穷尽式原创性证明。

最应突出的贡献是以下关系。维持非隔离感染者 `I=eta` 只固定 `c(1-q)S`，并未固定 `c`、`q`；追踪隔离还把未感染接触者移出社区，因此剩余自由度改变易感者下降速度。无回流时，控制期新增感染与新增隔离易感者之和等于固定的 `S*-S_c`，二者由控制时长联系。二次成本的逐状态全局比较、连续唯一结构的充分条件、能力约束截断和权重单调性，构成进一步的数学结果。固定时长前沿则说明这些目标怎样取舍。

现稿已经交代阈值策略内最优、无回流假设、`I` 与临床感染或 ICU 占用的区别、TDINN 的不同任务、低于一人的拟合初值以及西安长时外推。不能再把这些事项一概当作尚未披露的缺陷。也没有依据要求本稿现在新增 ICU 仓室、正回流重新优化、一般状态约束全局最优证明或一套新的稳健性扫描。

### 与重点来源的关系

| 来源 | 原文问题与结论边界 | 本文应强调的承接与区别 |
|---|---|---|
| [Angulo 等 2021](https://doi.org/10.1098/rsif.2020.0803) | 单一传播控制、感染上限和干预强度上限，尽快进入无需后续干预的安全区。有效持续期从初始时刻起算，等待和末端最大强度推进都属于其最优轨迹的一部分。正文 Box 1、第 2.4 节及补充 S1 给出几何与反馈结构 | 现稿已写提前启动和末端推进。需把有效持续期与本稿 `Delta t=t_2-t_1` 的起算点分开。本文固定到 `(S_c,eta)` 的阈值控制类，没有重新求解 Angulo 的可变目标到达问题 |
| [Avram、Freddi、Goreac 2022](https://doi.org/10.1016/j.amc.2021.126816) | 固定监测时域、仿射抑制成本、ICU 状态约束及严格的终端资格，结合 viability 与 Pontryagin 分析得到显式反馈。原文式 (1.2)、Problems 3.1/3.2、定理 5.6 | 本文整段可行条件是已到达阈值后的双控制条件，不是一般初始状态的完整 viability kernel。现稿已经限定这一范围。所附勘误仅补漏印的 Scenario 2 图，不推翻这里引用的结构 |
| [Miclo、Spiro、Weibull 2022](https://doi.org/10.1016/j.jmateco.2022.102669) | 无限时域的单传播率控制和线性抑制代价，解析给出沿容量运行及退出结构，正式版使用 Hamilton–Jacobi 验证。加入感染代价另有条件 | 本文的易感者还因未感染接触者隔离而减少，双控制能改变容量弧上的速度。该差别支持本文计数关系与二次成本问题，但不支持把沿容量运行本身作为新结构 |
| [Miclo 等 2020 v1](https://arxiv.org/abs/2005.01327v1) | 第 5.1 节已用单调易感者代替时间，并把轨迹成本改写为状态积分，随后处理轨迹与测度空间优化 | 建议给出这一方法承接。本文进一步固定 `I=eta` 并消去 `q`，只留下逐状态强度约束，才得到各状态独立的有限候选充分比较。一般换元与这种特殊可分结构应分开表述 |
| [Freddi、Goreac、Li、Xu 2022](https://doi.org/10.1007/s00245-022-09884-x)；本次正文依据 [作者稿 v2](https://arxiv.org/abs/2110.11625v2) | 对状态依赖成本给出 greedy 策略的 Hamilton–Jacobi 验证条件，作者稿 Theorem 2 与式 (15) 明确要求相应不等式。另讨论占用测度与 LP | 值得增补到相关工作。它说明成本形式决定既有 greedy 策略是否仍最优；并未给出本文含 `S_q` 流量的双措施二次成本结构。无需为引用它而把本稿改写成 HJB 论文 |
| [Freddi、Goreac 2024](https://doi.org/10.68381/jca31028) | 无限时域中最小化 `integral(lambda_1 u+lambda_2 i)dt`，以 Gamma 收敛联系有限时域，刻画可能含最大抑制段、容量弧及后续最大抑制段的结构。引言与第 9 节说明纯干预成本下的 greedy 结论不能不加条件地推广 | 另一篇值得补入的对话文献。可用一句说明沿容量运行的结构依赖目标、允许控制和终端要求，再转入本文明确固定的控制类。不是要求当前增加新的研究任务 |

上述两篇增补 Freddi 文献在本轮按相关章节核读，不声称对全部 Gamma 收敛或 LP 证明作了独立验证。正文论文是否存在同类结果，仍不能由有限检索作绝对否定。

### 共识问题

| 综合项 | 独立来源 | 已核实的问题 | 建议动作 |
|---|---|---|---|
| S1 补充材料未同步 | R1-m3、R2-m2 | `S7_return.tex:83` 仍称默认成本最优状态函数“连续性未证”，而正文定理 `thm:joint:cost-structure` 已覆盖默认 `r=2` | 删除过时理由，引用现有连续性定理。把无回流状态函数连续、含回流平台解存在唯一性、能力可行性、正回流最优性分开，不从连续性跳到这些结论 |
| S2 正则性用词过强 | R1-m4、R3-m1 | `05_quadratic_cost.tex:110` 将只保证连续的结果称为“平滑调整”。临界权重处现有公式还允许不可微的退化 | 改为“连续调整”。不新增正则性定理 |
| S3 Angulo 的目标时间 | R1-m2、R2-m3 | 引言第 8 行、讨论第 14 行把 effective duration 简称为干预持续时间，容易与本稿 `Delta t` 混淆 | 首次写明从初始时刻到安全区的时间。本文内部时长排序不受影响，因为启动前阶段相同 |
| S4 Duque 的触发与容量约束 | R2-m6、R3-m2 | 引言第 6 行的“住院人数”未区分新增入院流量与占床存量，且原文是随机情景下以高概率避免超载 | 写明新增入院人数的 7 日移动平均；如介绍解除条件，再写占床量条件。避免改述为对每条随机轨迹的确定性保证 |

这些共识均为 Minor，没有共识阻断项。它们集中在两三处术语和解释，不要求重做中心数学。

### 单个审阅者提出的其他问题

| 综合项 | 来源与位置 | 判断与修正 |
|---|---|---|
| S5 状态参数化的方法归属 | R1-m1；引言第 20 行、第 4 章入口、讨论 8.2 | Minor。补引 Miclo 早期稿第 5.1 节，再点出本文特殊的逐状态可分结构。现稿没有声称首次换元，问题是承接尚不够明确 |
| S6 医疗资源接近饱和 | R2-m1；`02_model.tex:102` | Minor。固定 `I=eta` 和补充的需求充分条件 `D(t)<=C` 都不能推出真实医疗占用接近 `C`。改为非隔离感染者达到阈值后的强化阶段，保留容量控制的研究动机 |
| S7 纯检测结论的条件 | R2-m4；`01_introduction.tex:16` | Minor。Grundel 作者稿先给出不限制检测数量时的纯检测策略，再因现实检测能力不足加入距离控制。补上“在其采用的现实检测能力下”。本次具体内容依据为本地 arXiv v1 |
| S8 新感染分流的机制 | R2-m5；`06_numerics.tex:71` | Minor。方程让被追踪的新感染直接进入 `I_q`，并不存在将既有 `I` 按检测率转入 `I_q` 的项。将“把一部分感染者从社区转入隔离”改成准确的新感染分流解释 |
| S9 投稿复现出口 | R3-M1；正文方法与补充 S6 | Major，Blocking No。稿件应能指向同一版本的代码、输入和输出，包括实际绝对容差、检查点、候选根与并列判据、积分分段及图表映射。整理现有材料即可，本轮无需重算，也无需立即公开 |

S9 是投稿交付事项。`NEW_author_inputs.md` 已将病例输入的可分发范围和代码归档链接留待后续决定，因此本报告保留其重要性，但不把作者已经安排后补的事项当成当前中文理论稿的中心缺陷。

### 来源补读新增的定位问题

三份报告冻结后，为完成全部本地参考论文的阅读，又补读了此前只按相关章节核读的七份来源。以下是补读新增的证据，不计作三位审阅者共识，不回改原报告。

**最近先行工作的联合优化应明确承认。** [Zhou 等 2024](https://doi.org/10.1007/s00285-024-02083-y) 不仅给出模型、首次积分和分段常数干预，也在原 PDF 第 21–23 页第 6 节、式 (6.1)–(6.2) 中提出联合选择 `T_on,T_off,c_c,q_c` 的双目标问题，目标是非隔离峰值与清零时间，并分析若干简化数值情景；第 18–20 页和附录 B 也比较两种措施的作用。现稿引言第 16 行没有概括这部分，讨论第 14 行的“推进在于区分两种干预”因而还可以更准确。建议补一句其已有的联合优化问题和情景分析，再把本文的推进落在维持 `I=eta` 的全部可测组合、精确排序和逐状态成本结构上。源文尚未覆盖本文这些定理，本轮没有发现中心结论被其直接覆盖的证据。

**Charpentier 的容量平台应绑定情景。** [Charpentier 等 2020](https://doi.org/10.1051/mmnp/2020045) 第 13–16 页的长期 ICU 饱和平台属于不使用检测的仅封控基准；第 19 页及第 32 页图 B.8 的检测与封控联合优化情景，ICU 峰值约为上限四分之一，没有同一长期饱和平台。现稿引言第 16 行先介绍联合优化，随后接“其最优封控也有一段 ICU 满负荷的长时期”，容易把两个情景接成一个结论。建议明确“仅封控情景出现长期容量平台，加入足够强的检测后最优轨迹也可离开容量边界”。这同样支持把沿容量运行的最优性绑定具体控制与成本，而不是推广到一切多措施优化。

补读还核实了 He 原文使用的西安窗口延续至 2022-01-20，本稿已明写采用至 01-17 的 40 个区间。补数据包时可说明这是截取窗口；该差别本身不证明现有病例数或拟合结果错误，本轮没有重建逐日原始数据。

另外，Balderrama 的退出描述可将“在其后再施加部分封控”明确为“离开容量边界后再施加部分封控”，避免误读为先达到常规传播临界值才再次加强。其原文定理 4.1 的活动边界弧退出条件并非本稿退出条件。Zhang2026 的行为收益阈值、另设的流行率上限与本稿 `eta` 也不同；现稿没有引用它作具体结论的依据，不需仅为覆盖本地文件而机械加入引用。

### 编辑补充建议

以下建议来自主代理在报告冻结后的来源与主张检查，不标为三位审阅者共识，也不作为新 Major。

1. 摘要首次介绍模型时，直接写明“隔离易感者不返回社区”。正文和结论已有该条件，但摘要的时长、感染与隔离排序没有就地提示，而补充已表明正回流的长期结果会不同。这是一个应前置的模型假设，不需增加整段防御性解释。
2. 摘要末句可落在“给定非隔离感染阈值下的组合”上。医疗容量是选取阈值的依据，补充的附加需求核给平均需求的充分条件；本文没有完成当地临床容量标定。
3. 介绍 Angulo 的“低于 1 不是必要条件”时，准确区分其最大干预对应的受控再生数 `R_c=(1-u_max)R_0` 与状态依赖的有效再生数。原文 Box 1 和式 (2.3) 讨论的是干预能力与允许峰值的关系，不能让读者误以为所有再生数的定义可互换。现稿未抄用其不等式，不涉及更改本稿模型。
4. 将上表两篇 Freddi 后续论文加入相关工作对话，使用它们已经核实的目标与条件，不增加泛泛背景段落。Soner I/II 不是当前降维证明所必需的引用，控制函数跳变也不能与 Soner II 的随机状态跳过程混同。

可以局部采用的草句如下，尚未写入 TeX。

> 本文在隔离易感者不返回社区的 SIQR 模型中，研究阈值策略下接触控制与追踪隔离的组合。

> 以单调易感者代替时间的参数化已有先例；本文固定非隔离感染者处于阈值，并由平衡条件消去隔离比例，使只含逐状态强度约束的双控制问题化为有限候选的全局比较。

> 被追踪的新感染直接进入隔离感染仓室，减少进入社区感染仓室的新增感染；维持社区感染者阈值的同时，隔离点负荷随之增加。

## 报告冻结后的确定性核对

完整机器记录见 [确定性核对 JSON](NEW_literature_review_20261020_audit.json)。该检查在三份独立报告全部冻结后运行，未把结果回送给审阅者。

| 项目 | 状态 | 实际检查与结果 |
|---|---|---|
| 输入与冻结身份 | passed | 21 个稿件输入、19 个原文 PDF 的 SHA-256 与本轮清单一致；三份报告与冻结哈希一致 |
| 表 2 时间关系 | passed | 基准四行的 `t_end-Delta t` 都为 27.87 d；西安为 173.03–173.04 d，与显示舍入相容 |
| 表 2 计数相消 | passed | 总累计新增感染加控制期新增隔离易感者，基准为 669.5–669.6 人，西安四行均为 `10.3570*10^6` 人，与共同前后阶段和显示舍入相容 |
| 两组闭式权重 | passed | 直接代入已冻结参数，`r_cont` 舍入为 3.1358、2.5477，`r_hat` 舍入为 3.2051、2.7090，与数字宏一致；默认 2 均严格小于连续界 |
| 连续性旧表述 | confirmed_internal_error | 默认 2 满足新定理条件，“连续性未证”已过时。与 R1-m3、R2-m2 重合 |
| 平滑性解释 | confirmed_internal_error | 在临界点，稿内公式给 `E=E_p=0`、`E_zeta<0`；不能用有限一阶导数的光滑分支概括整个定理范围。连续结构定理本身不受影响。与 R1-m4、R3-m1 重合 |
| 投稿公开定位 | provenance_gap | 拟投稿文件尚无稳定出口，本地材料与后续待办存在。与 R3-M1 重合 |
| 本轮数值重现 | not_assessable | 未运行求解器、ODE、分类矩阵或重新拟合；不把历史测试数或历史复算精度称为本轮结果 |

## 推荐处理顺序

1. 先同步 S1，修正 S2、S6、S8，并在摘要模型句中前置无回流条件。这组修改直接关系读者怎样理解现有定理，均可局部处理。
2. 再处理 S3、S4、S5、S7，以及补读发现的 Zhou 联合优化与 Charpentier 情景归属，补充两篇 Freddi 文献的准确对话。重点是目标、起算点、控制机制与方法承接，不扩写文献综述。
3. 在正式英译与投稿材料整理阶段处理 S9。沿用已有核验材料和明确版本，不以增加新算例替代复现定位。

## 风险与未支持的断言

本轮没有发现需要推翻主线的证据，但没有证明所有模型参数下的全部证明均无缺口，也没有完成全球文献中的穷尽式新颖性检索。新文献不能自动扩张本文结论。无回流模型的感染排序、给定阈值设计、临床容量保证、有限截断与无限时刻、迁移控制律与正回流最优律仍应保持现有区分。

完整文献覆盖与补读记录见下节。全文阅读表示读取全部页面的可提取文本并按需要回看公式，不等于逐符号认证全部证明或逐数据点复核全部图表。教材按与本题有关的章节阅读。

## 文献覆盖登记

所有本地研究论文文件的完整逐页文本覆盖现已补足，关键模型与目标公式按需要回看原 PDF。三份原报告在补读前冻结，不能据此改称三位审阅者在各自报告形成时均已全文阅读所有来源。补读的页码、公式、版本与限制详见 [来源补读附录](NEW_literature_review_20261020_sources.md)。

下表逐份登记最终覆盖。教材按相关章节核读，讲稿不作为独立学术证据；Angulo 扫描补充的复杂公式与表格也没有全部逐符号验证。

| 输入 | 页数 | 本轮实际阅读 |
|---|---:|---|
| [REF-01 Angulo 中文讲稿](<E:/work/draft-submission-ready/refs/2025.09_zhangyangyang.pdf>) | 36 | 36 页提取文本已通读/浏览，公式缺字多；不作独立原始学术证据 |
| [REF-02 Angulo 2021 正文](<E:/work/draft-submission-ready/refs/angulo-et-al-a-simple-criterion-to-design-optimal-non-pharmaceutical-interventions-for-mitigating-ep.pdf>) | 10 | 10 页全文，R1；重要 Box 1 及反馈结构回看原 PDF |
| [REF-03 Liberzon 教材](<E:/work/draft-submission-ready/refs/Calculus of Variations and Optimal Control Theory A Concise Introduction (Daniel Liberzon) (Z-Library).pdf>) | 254 | 按本题相关章节核读；PDF 103–107、164–171 页，未通读全书 |
| [REF-04 Charpentier 等 2020](<E:/work/draft-submission-ready/refs/COVID-19 pandemic control balancing detection policy and lockdown intervention under ICU sustainability.pdf>) | 42 | 42 页全文，含附录 A/B/C；补读 A |
| [REF-05 Tang 等 2020](<E:/work/draft-submission-ready/refs/Estimation of the Transmission Risk of the 2019-nCoV and Its Implication for Public Health Interventions.pdf>) | 13 | 13 页全文；补读 B |
| [REF-06 He、Tang、Xiao 2023](<E:/work/draft-submission-ready/refs/He_Tang2023PCB.pdf>) | 23 | 23 页全文；补读 B |
| [REF-07 Grundel 等作者稿](<E:/work/draft-submission-ready/refs/How Much Testing and Social Distancing is Required to Control COVID-19 Some Insight Based on an Age-Differentiated Compartmental Model.pdf>) | 25 | 25 页全文；补读 A；版本为 arXiv v1，未冒称逐页核对正式排版版 |
| [REF-08 Balderrama 等 2024](<E:/work/draft-submission-ready/refs/Optimal control for an SIR model with limited hospitalised patients.pdf>) | 15 | 15 页全文，含附录；补读 C |
| [REF-09 Avram、Freddi、Goreac 2022](<E:/work/draft-submission-ready/refs/Optimal control of a SIR epidemic with ICU constraints and target objectives.pdf>) | 25 | 25 页全文，R1；含 PDF 24–25 页所附勘误 |
| [REF-10 Ketcheson 2021](<E:/work/draft-submission-ready/refs/Optimal control of an SIR epidemic through finite-time non-pharmaceutical intervention.pdf>) | 21 | 21 页全文，R3 |
| [REF-11 Soner I](<E:/work/draft-submission-ready/refs/Optimal Control with State-Space Constraint I_soner.pdf>) | 10 | 10 页全文，R3；不认为本稿必须泛加此引文 |
| [REF-12 Soner II](<E:/work/draft-submission-ready/refs/Optimal Control with State-Space Constraint. II.pdf>) | 13 | 13 页全文，R3；与控制函数的跳变不是同一对象 |
| [REF-13 Miclo 等 2022 正式版](<E:/work/draft-submission-ready/refs/Optimal epidemic suppression under an ICU constraint An analytical.pdf>) | 17 | 17 页全文，R1，含 HJ 附录 |
| [REF-14 Miclo 等 2020 v1](<E:/work/draft-submission-ready/refs/Optimal epidemic suppression under an ICU constraint.pdf>) | 46 | 46 页全文，R1；第 5.1 节状态参数化为重点 |
| [REF-15 Angulo 扫描补充](<E:/work/draft-submission-ready/refs/supplementary material.pdf>) | 20 | 主代理通读 20 页 OCR 文字，当前 PDF 全部渲染总览并回看关键反馈/切换页；部分图表只浏览，不作全式校勘 |
| [REF-16 Zhang 等 2026](<E:/work/draft-submission-ready/refs/Tang_Zhang_2026_BMB.pdf>) | 38 | 38 页全文，含附录 A–E；补读 C |
| [REF-17 Zhou 等 2024](<E:/work/draft-submission-ready/refs/Tang_Zhou_2024_JMB.pdf>) | 34 | 34 页全文，含附录 A/B；补读 B |
| [REF-18 Duque 等 2020](<E:/work/draft-submission-ready/refs/Timing social distancing to avert unmanageableCOVID-19 hospital surges.pdf>) | 6 | 6 页全文，R3 |
| [REF-19 Balakrishnan、Palathingal](<E:/work/draft-submission-ready/refs/一种自适应测试策略，有助于在疫情期间有效利用医疗资源.pdf>) | 10 | 10 页全文，R3；含原文件资源中心说明页 |


两篇新增 Freddi 文献仅按与本题有关的摘要、模型、验证或结构章节核读，未将其全部证明列为已核验。仅取得摘要的 Freddi transmission 和 delayed SIR 文献不用于否定本稿定理。
