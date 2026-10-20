# Reviewer 2

## 审阅设置

本报告于 2026-10-20 独立形成，按 BMB 类生物数学期刊的理论论文标准评估。预设重心为模型与流行病学解释、容量阈值及文献支持边界。未读取其他审阅报告，未交换问题清单，未修改稿件源文件，未提交，未运行优化、扫描、拟合或数值复现。

输入为 `paper/tmp/literature_review_20261020/review_packet.md`、`manifest.json` 所列主稿九章、两份主文件、附录、补充材料、数字宏、参考文献和 19 份本地 PDF，以及审阅中共同补发的原始文献。已实际逐一核对 manifest 所列稿件与文献的 SHA-256，全部匹配。下列页码均指输入 PDF 的物理页码，另有印刷页码时同时标明。

中心问题是在预先规定的阈值策略下，如何组合减少接触与追踪隔离。现稿没有把这一问题冒称为一般的双控制容量状态约束最优控制问题。审阅不构成全部证明的形式验证，也不构成数值结果的独立复现。

## 总体评价

在本审阅重心内，现稿的中心论证已经成立到可作理论论文讨论的程度，建议小修。未找到有充分依据的 Major Concern 或 Blocking Yes 问题。主要改进是清除少量尚未完全服从现稿模型定义的机制句，以及把文献中的目标、检测能力和观测指标写得更准确。

论文的价值主要在于把固定感染阈值下剩余的一维控制自由度明确化，进而得到控制时长、感染与未感染者隔离之间的计数关系和成本最优结构。把隔离易感者的持续退出单独拿出来分析，使“更快、感染更少”的来源可以被解释，而非仅比较若干数值轨迹。对于研究接触追踪、约束最优控制和疫情退出条件的读者，这一结构比西安情景的具体数字更有普遍参考价值。

## 读者与长处

1. 模型来源交代清楚。[02_model.tex 第 7、19 行](E:/work/draft-submission-ready/paper/sections/02_model.tex:7) 与 Zhou 等的式 (2.1)、(3.1) 一致。合并住院与恢复仓室后，取总移出率 `gamma = delta_I + gamma_I` 是正确的聚合解释。现稿也明确说明 `I+I_q` 不包括已经移出但仍住院者。来源为 [Zhou et al. 2024](https://doi.org/10.1007/s00285-024-02083-y)，PDF 第 4、6 页。
2. `q` 与检测率已经作了必要区分。[02_model.tex 第 28 行](E:/work/draft-submission-ready/paper/sections/02_model.tex:28) 把 `q` 定义为被追踪接触者的比例。Charpentier 的感染检测是 `I^- -> I^+`，Grundel 的检测使感染者进入待检仓室，而不把未感染接触者送入独立的 `S_q`。因此现稿在 [引言第 16 行](E:/work/draft-submission-ready/paper/sections/01_introduction.tex:16) 所作的机制区分有原文依据。来源为 [Charpentier et al.](https://doi.org/10.1051/mmnp/2020045)，PDF 第 5 页式 (2.1) 与第 8 页，以及 [Grundel et al. 作者稿](https://arxiv.org/abs/2011.01282)，PDF 第 6–7 页式 (2a)–(2k)。
3. 容量解释已经有实质补强。[S3_xian.tex 第 180–205 行](E:/work/draft-submission-ready/paper/supplement_sections/S3_xian.tex:180) 用共同需求函数、初始病例未来负担和可用容量导出平均 ICU 需求的充分条件。它没有把 `I=eta`、`I+I_q=eta` 和 ICU 占床相等混为一个公式。第 209–223 行也已把全国资源预测量、Angulo 名义系数和本地临床校准区分开。本报告不要求为所有理论结论补做临床标定。
4. 无回流是明确的解析假设，不是未被发现的模型遗漏。He 等确实在 PDF 第 6 页式 (1) 前说明忽略 `S_q -> S`，理由是其短期暴发研究；Tang 等的模型则保留回流，见 PDF 第 4 页式 (1) 和第 5 页表 1。现稿没有把这些来源对无限时间的适用性直接搬过来，而在 [02_model.tex 第 30 行](E:/work/draft-submission-ready/paper/sections/02_model.tex:30) 明说无限时刻指标仍延续无回流假设，并在讨论和补充中分析正回流。来源为 [He et al. 2023](https://doi.org/10.1371/journal.pcbi.1011535) 和 [Tang et al. 2020](https://doi.org/10.3390/jcm9020462)。
5. 正回流结果的终点与量词处理适当。[S7_return.tex 第 44–65 行](E:/work/draft-submission-ready/paper/supplement_sections/S7_return.tex:44) 给出的是有限时刻后永久恢复常规控制、`I(0)>0`、`omega>0` 下的共同渐近下界，没有声称所有控制最终感染相同。第 106–158 行明确区分首次下降到 `I=1` 的截断值、无限时刻值、尾界和积分误差，并把迁移律与正回流重新优化区分。这些是现稿已经处理的事项。
6. 西安参照的边界充分。[07_xian.tex 第 14–16、26、74 行](E:/work/draft-submission-ready/paper/sections/07_xian.tex:14) 说明极小初值只是连续模型初值，拟合不验证预测，TDINN 与阈值策略任务不同，长期结果只是固定参数外推。He 原文 PDF 第 7 页表 1、第 13 页式 (4)、(5)、第 14 页表 3 能核对现稿采用的参数与 `c_2,q_2`。本报告没有据此要求重新拟合西安或增加新的临床实验。

## Major Concerns

在实际核读的模型、解释和文献范围内未识别到有证据支持的 Major Concern。没有 Blocking Yes 项。此结论不应扩大为所有新成本结构证明与全部计算文件均已通过独立认证。

## Minor Comments

### R2-m1 固定感染阈值不能直接称为医疗资源接近饱和

| 字段 | 内容 |
|---|---|
| Severity | Minor |
| Blocking | No |
| Axis | claim-moderation |
| Claim pointer | [02_model.tex 第 102 行](E:/work/draft-submission-ready/paper/sections/02_model.tex:102) 将强化干预阶段说成“医疗资源接近饱和的时段” |
| Evidence pointer | 同文件第 4、19 行；[S3_xian.tex 第 180–205 行](E:/work/draft-submission-ready/paper/supplement_sections/S3_xian.tex:180)；[Charpentier 原文](https://doi.org/10.1051/mmnp/2020045) PDF 第 5 页式 (2.1)、第 12 页式 (2.12) |

问题是命题只证明在 `I=eta` 上启动与退出的性质。补充中的容量条件给出 `D(t)<=C`，并不推出 `D(t)` 接近 `C`；同一 `I` 下，不同 `c` 的全部新感染流量还可不同。Charpentier 直接约束的则是独立 ICU 仓室。现稿其他位置已经把这些对象分开，这一句却重新给出未经推导的等同。

影响局限在解释层面，不改变阈值类内的定理。可验收的修正是改为“强化干预集中于非隔离感染者达到阈值后的阶段”，并把与已有容量边界弧的关系说成研究动机或数学结构上的对应。无需增加 ICU 仓室或新校准。

### R2-m2 回流补充仍说默认成本控制的连续性未证

| 字段 | 内容 |
|---|---|
| Severity | Minor |
| Blocking | No |
| Axis | writing-clarity |
| Claim pointer | [S7_return.tex 第 83 行](E:/work/draft-submission-ready/paper/supplement_sections/S7_return.tex:83) 称默认权重下成本最优律的正回流平台解只有数值实现，理由是其状态函数连续性未证 |
| Evidence pointer | [05_quadratic_cost.tex 第 105–110 行](E:/work/draft-submission-ready/paper/sections/05_quadratic_cost.tex:105)，定理 `thm:joint:cost-structure`；[A_proofs_sensitivity.tex 第 300 行](E:/work/draft-submission-ready/paper/appendices/A_proofs_sensitivity.tex:300)；S7 第 20、68、107 行 |

现稿已证明默认 `r=2` 对全部允许参数满足 `r<=r_cont`，并且成本最优状态函数在整个 `(S_c,infinity)` 连续。因此“连续性未证”已经与正文不一致。正回流解的唯一性、可行性和正回流最优性仍是不同问题，不能由这一连续性顺带全部宣称解决。

可验收的修正是删除该过时理由，准确说明哪些平台存在性结论可由连续控制律与本节有限退出论证取得，哪些结论仍仅有数值实现；维持迁移律未重新优化的表述。若作者暂不补写存在性推论，至少不应保留已经被正文反证的“未证”说法。

### R2-m3 Angulo 的有效持续期应与本文控制时长区别

| 字段 | 内容 |
|---|---|
| Severity | Minor |
| Blocking | No |
| Axis | novelty-significance |
| Claim pointer | [01_introduction.tex 第 8 行](E:/work/draft-submission-ready/paper/sections/01_introduction.tex:8) 与 [08_discussion.tex 第 14 行](E:/work/draft-submission-ready/paper/sections/08_discussion.tex:14) 将 Angulo 的目标简称为干预持续时间 |
| Evidence pointer | [Angulo et al. 2021](https://doi.org/10.1098/rsif.2020.0803)，PDF 第 2 页图 1(d) 图注、第 3 页 Box 1、第 5–6 页末段最大强度干预说明；本文 [02_model.tex 第 132 行](E:/work/draft-submission-ready/paper/sections/02_model.tex:132) |

Angulo 的 effective duration 从疫情初始时刻计到最后一次非零干预，相当于尽快到达安全区，包含启动前的等待时间。本文的 `Delta t=t_2-t_1` 则只计阈值控制期。现稿已经正确区分两者退出方式，建议也在首次介绍其目标时写清这一时间定义。本文内部比较时 `t_1` 相同，因此这不推翻现稿的时长排序。

可验收的修正是一处写为“以从初始时刻到进入安全区的有效持续期最短为目标”，讨论中用这一短名，避免读者误以为两篇文章优化的是同一个时间泛函。

### R2-m4 Grundel 的检测不足结论依赖现实检测能力

| 字段 | 内容 |
|---|---|
| Severity | Minor |
| Blocking | No |
| Axis | claim-moderation |
| Claim pointer | [01_introduction.tex 第 16 行](E:/work/draft-submission-ready/paper/sections/01_introduction.tex:16) 称 Grundel 发现仅靠检测难以维持 ICU 上限 |
| Evidence pointer | [Grundel et al. 作者稿](https://arxiv.org/abs/2011.01282)，PDF 第 12 页式 (6a)–(6e) 与结尾，第 13 页检测数量说明，第 14 页式 (7e)；正式出版信息 [SIAM JCO 2022](https://doi.org/10.1137/20M1377783) |

作者稿先展示无检测数量上限时纯检测策略可行，随后指出所需日检测量超过 1200 万，而当时德国能力约 17 万，才引入检测容量上限及社交距离。现句省略这一条件，容易被读成检测机制本身无法满足 ICU 约束。

可验收的修正是在该句补入“在其采用的现实检测能力下”。本报告的内容核对依据明确是本地 2020 年 arXiv v1，不冒称已经逐页比对 2022 年正式排版版。

### R2-m5 机制句应保持新感染流入与现存感染者转移的区别

| 字段 | 内容 |
|---|---|
| Severity | Minor |
| Blocking | No |
| Axis | mechanism-evidence |
| Claim pointer | [06_numerics.tex 第 71 行](E:/work/draft-submission-ready/paper/sections/06_numerics.tex:71) 的“追踪隔离把一部分感染者从社区转入隔离” |
| Evidence pointer | [02_model.tex 第 10–14 行](E:/work/draft-submission-ready/paper/sections/02_model.tex:10)；[He et al. 2023](https://doi.org/10.1371/journal.pcbi.1011535)，PDF 第 6 页式 (1)；[Zhou et al. 2024](https://doi.org/10.1007/s00285-024-02083-y)，PDF 第 4 页式 (2.1) |

在现稿方程中，`q` 对新感染流量作即时分流，使被追踪的新感染直接进入 `I_q`；它不是把已经处于 `I` 的存量以某个检测率转到 `I_q`。后者在 Charpentier 等模型中是另一条控制通道。本句可被理解为现稿没有的 `I -> I_q` 转移。

可验收的修正是写成“被追踪的新感染直接进入隔离感染仓室，减少进入社区感染仓室的新增感染”，保留其后隔离点负荷增加的解释。无需改变模型或任何数字。

### R2-m6 Duque 的启动信号是新增入院量而非占床存量

| 字段 | 内容 |
|---|---|
| Severity | Minor |
| Blocking | No |
| Axis | writing-clarity |
| Claim pointer | [01_introduction.tex 第 6 行](E:/work/draft-submission-ready/paper/sections/01_introduction.tex:6) 的“按住院人数触发短期封控，在不超出医院容量的同时使封控时间尽量短” |
| Evidence pointer | [Duque et al. 2020](https://doi.org/10.1073/pnas.2009033117)，PDF 第 2 页（印刷页 19874）右栏触发规则、第 3 页图 1 图注 |

原文启动信号为每日新增入院人数的七日移动平均；解除还要求占床人数低于容量的 60%。其优化以高概率避免超载，而非对全部随机轨迹给出确定性保证。笼统“住院人数”会把流量与存量合并，也让其随机阈值机制与本文固定 `I` 阈值过于接近。

可验收的修正是用一句准确概括，例如“按新增入院量的七日均值触发短期封控，以尽量减少封控天数并以高概率避免医院超载”。不需要在引言展开完整的 Austin 算法。

## 证据不足处与技术边界

- 新成本定理的证明已阅读，但未逐项独立重算高次多项式恒等式、所有不等式和 Aumann 定理的原文编号。本报告不把“未独立认证”写成证明有误。
- 数值方法与表格在稿中可以追溯到独立求积、完整仓室积分和容差检查，但本轮没有运行代码，不能确认实际结果文件、缓存身份与报告文字完全对应。稿中已有说明不等于本审阅者完成复现。
- 本地没有 Pollinger、Hellewell、Kucharski、Ferretti、Fraser、Baas、Pung 等全部所引论文的全文。本轮没有据书目信息猜测其模型或宣称已核实相关排他性结论。也未把新增流量与确诊报告之间的关系当成真实病例监测过程已经得到外部验证。
- 未把无回流的长期情景当成实际隔离期限预测，未要求新增正回流重新优化、临床仓室或西安重新拟合来弥补本稿已明确界定的理论范围。

## 推荐修改顺序

先修正 R2-m2 的内部状态冲突和 R2-m1 的容量饱和表述。随后处理 R2-m3、R2-m4、R2-m6 的文献定义，最后校正 R2-m5 的流量机制句。这些修改均可不改变方程、参数、初值和现有计算完成。

文献更新方面，可在讨论未来推广时加一处对 Freddi 与 Goreac 后续工作的简短定位。[2024 年无限时域论文](https://journalofconvexanalysis.com/articles/jca31028/jca31028.pdf) 的印刷页 526–527 明确讨论，当目标加入感染状态成本时，原有 greedy 控制未必继续最优。[2022 年作者稿](https://arxiv.org/abs/2110.11625v2) 第 2 页与第 3 节则给出状态相关成本下验证 greedy 策略所需的额外条件。它们支持现稿 [讨论第 28 行](E:/work/draft-submission-ready/paper/sections/08_discussion.tex:28) 已有的研究边界，即更一般的双控制状态约束问题中是否沿阈值运行仍需证明。这是让研究定位更新、更准确的建议，不是把未引用每篇相关论文作为拒稿理由。

## 评估轴与适用性

| 技术轴 | 本轮判定 |
|---|---|
| novelty-significance | applicable。模型与首次积分已归属先行工作，组合自由度及计数关系是应强调的推进 |
| mechanism-evidence | applicable。模型机制可由方程直接核对，R2-m5 为局部文字偏差 |
| experimental-design | not applicable。本文主要是理论与情景计算，未提出新临床实验效果结论 |
| statistical-rigor | applicable，范围限于拟合定义及其解释。无重新估计或置信推断审核 |
| reproducibility | not assessable for execution。方法已读，数值执行与缓存未重验 |
| clinical-validity | applicable to claimed interpretation。现稿已收窄为设计阈值和附加需求假设下的平均容量条件，不评为临床政策验证 |
| ethical-governance | not applicable to the supplied theoretical analysis。未发现新增个体数据或干预试验主张 |
| data-resource-quality | not assessable for raw data。本轮核对输入身份与来源文字，没有独立重建病例数据 |
| figures-and-tables | applicable。核对了表中指标定义与模型解释，没有完成全稿逐图渲染验收 |
| writing-clarity | applicable。剩余问题主要是少量对象与文献目标的表述 |
| claim-moderation | applicable。已区分阈值类内最优与一般状态约束最优、共同下界与相同终值 |
| causal-vs-correlative | applicable。把 TDINN 视为数据重构与外部参照，不把拟合视为政策因果效果识别 |

## 实际阅读覆盖与未核内容

主稿两份主文件、九章、两份附录和六份补充分节均已通读源文本；数字宏与参考文献表已检查来源和相关定义。模型正性、触发退出、状态参数化、比较恒等式、回流总易感者恒等式及渐近下界、尾界和 ICU 卷积充分条件作了逐式核读。成本结构证明阅读不等于形式认证。没有把编译或数值复现列为本轮实际完成的工作。

| 输入 | 本轮实际覆盖 |
|---|---|
| REF-01 2025.09 讲稿 | 36 页的提取文本逐页浏览。公式缺字较多，未作全份图像核读。它是 Angulo 论文的中文讲解材料，不是 REF-16 的论文稿，也不作为优先学术来源 |
| REF-02 Angulo 正文 | PDF 第 1–6 页核读，重点图 1(d)、Box 1、图 3 和退出方式；第 7–10 页未逐段精读 |
| REF-03 Liberzon 教材 | 目录，以及第 4.4.4–4.5 节相关内容，PDF 第 164–171 页（印刷页 145–152）。不是全书精读 |
| REF-04 Charpentier | 摘要，PDF 第 4–13 页模型、目标、容量约束及数值方法，第 15 页结果说明；关键式 (2.1) 回看当前 PDF 渲染。其余敏感性与附录未逐段核读 |
| REF-05 Tang 2020 | PDF 第 1 页摘要、第 4–5 页模型与参数、第 10–11 页讨论结论；其他数值结果未全文精读 |
| REF-06 He 2023 | 摘要，PDF 第 6–7 页模型与参数、第 13–15 页函数拟合和表 3、第 18–19 页多波及讨论。第 6 页模型已回看当前 PDF 渲染。其余网络训练细节与附录未逐项验证 |
| REF-07 Grundel | PDF 第 1 页摘要、第 3–20 页按模型、检测数量约束、目标和 MPC 章节核读；第 2 页及第 21–25 页未完整精读。依据本地 arXiv v1，不声称核读正式排版版 |
| REF-08 Balderrama | PDF 第 1–8 页的模型、目标、边界弧、最优结构与代表数值核读；第 12–14 页证明作了浏览，未独立验证全部附录；第 9–11、15 页未逐段精读 |
| REF-09 Avram | PDF 第 1–5 页模型与目标、第 14–15 页反馈律和比较核读，第 24–25 页勘误已读。勘误涉及漏印数值图，不是推翻现稿引用的策略结构 |
| REF-10 Ketcheson | PDF 第 1–3 页模型、终点和有限期干预后的最终易感者界；其他 HJB 与数值章节未全文精读 |
| REF-11 Soner I | PDF 第 1–2 页摘要、引言、值函数及状态边界解释；未精读全部证明 |
| REF-12 Soner II | 摘要与引言浏览，不作为本文具体定理有效性的核验来源 |
| REF-13 Miclo 正式论文 | 摘要与模型、主定理相关页核读。仅按与现稿有关的阶段结构阅读，没有声称验证全部 HJB 附录 |
| REF-14 Miclo 2020 作者稿 | PDF 第 1–3 页摘要、研究问题及 filling-the-box 解释，未用作者稿取代正式版结果 |
| REF-15 Angulo 补充 | 原直接提取为空；使用共同补发且身份对应的 OCR，只核读第 16–17 页相关内容，并回看当前渲染第 17 页 S4.1，确认 `0.60*0.15*0.28=0.0252`。不声称通读全部 20 页 |
| REF-16 Zhang 2026 | PDF 第 1–8 页、10–12 页、24–25 页，核读 SIHS 行为反馈模型、行为阈值和双控制状态约束情景。该文研究地方病共存与行为响应，没有据其标题当作本文无回流 SIQR 的同一问题；其余章节未全文精读 |
| REF-17 Zhou 2024 | PDF 第 1、3–10 页重点核读模型、首次积分、清零定义和分段常数控制；第 4 页模型回看当前 PDF 渲染。后续参数拟合与全部峰值分类证明未逐项复核 |
| REF-18 Duque | PDF 第 1–3 页模型任务、入院触发及图 1，余下讨论和补充未全文核读 |
| REF-19 Balakrishnan | PDF 第 2–3 页摘要、资源目标、检测机制与模型，未复算控制算法或数值效果 |
| Freddi–Goreac 2024 增补 | 正式原文印刷页 525–527，核读问题定义和加入状态成本后 greedy 策略的适用边界；未读完整证明 |
| Freddi–Goreac–Li–Xu 增补 | arXiv:2110.11625v2 的摘要、引言和模型，主要是第 1–3 页；正式出版社信息由共同补件提供，未把作者稿说成逐页核读的正式排版版 |

上述覆盖包含按相关章节核读、提取文本浏览和仅摘要阅读，不等于 19 份 PDF 全部完成逐页精读。尤其不能据本报告宣称本地所有参考文献的每个定理、图表和证明均已核验。

本报告至此冻结。任何后续比较、编辑汇总或新来源核查，应另写记录，不回改本独立报告。
