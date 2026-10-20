# 2026-10-20 追踪延迟、隔离效果与隔离时长：补读证据

本备忘录服务于现稿局部修改建议。没有修改 TeX、参考文献、参数、图或计算结果。公开来源的下载收据和 SHA-256 位于 `paper/tmp/literature_followup_20261020/root/fetch_receipts.json`。以下区分实际阅读、模型结论和对本文的推论；不把其他模型的数值阈值移植为本文结论。

## 1. Kretzschmar 等：覆盖比例不能代替追踪时间

Mirjam E. Kretzschmar, Ganna Rozhnova, Martin C. J. Bootsma, Michiel van Boven, Janneke H. H. M. van de Wijgert, Marc J. M. Bonten. *Impact of delays on effectiveness of contact tracing strategies for COVID-19: a modelling study*. The Lancet Public Health **5**(8), e452–e459 (2020). [DOI](https://doi.org/10.1016/S2468-2667(20)30157-2)；[公开原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7365652/)。

- **版本与阅读**：本轮新取得 Europe PMC 的期刊全文 JATS；读摘要、完整正文的 Introduction、Methods、Results、Discussion，以及图1–4和表1–2的说明。未取得并完整阅读其独立补充附件，不据附件公式作新判断。Crossref请求遇429，作者、卷页和DOI由期刊全文头部核实；下载失败没有记为成功。
- **原文对象**：分枝过程区分感染、症状、确诊和追踪时点；检测延迟为症状至确诊，追踪延迟为确诊至接触者被追踪。覆盖率与这些时间分别进入模型。Methods同时假设隔离阻断后续传播。
- **可支持的结论**：在该文设定中，缩短检测和追踪延迟可以改变相同覆盖比例下的传播效果。其特定疫情参数下的若干天数界限不能作为本文SIQR模型的通用界限。
- **现稿位置**：`02_model.tex:7,28,30` 已准确说明 `q` 是接触者比例、隔离者不传播；`08_discussion.tex:24` 已说明执行延迟。但尚可更明确地区分“追踪进入隔离的延迟”与“控制指令执行延迟”。前者改变传播过程，后者是输入实施问题。
- **建议句（只需一处）**：

  > 模型把被追踪的接触者直接分入隔离仓室，并假设隔离后不再传播；现实中的追踪延迟和隔离期间的残余传播会改变同一覆盖比例的效果。

这句话适合并入讨论现有局限段，不另开一段。无需加入潜伏仓室或求解时滞模型。

## 2. James 等：覆盖率与隔离效果是不同对象

A. James, M. J. Plank, S. Hendy, R. Binny, A. Lustig, N. Steyn, A. Nesdale, A. Verrall. *Successful contact tracing systems for COVID-19 rely on effective quarantine and isolation*. PLoS ONE **16**(6), e0252499 (2021). [DOI及期刊全文](https://doi.org/10.1371/journal.pone.0252499)。

- **版本与阅读**：本轮下载14页期刊PDF，另读取期刊HTML全文正文。重点核读 Methods/Model、Results and discussion 的两个小节及图2–4；PDF第12–14页为参考文献，未将引文列表算成研究结果。未执行代码或重新分析新西兰病例。
- **原文对象**：年龄结构分枝过程分别设置追踪概率、追踪时间、接触者隔离与确诊病例隔离的有效性；未被追踪的有症状者仍可能在稍后检测并隔离。因此“覆盖一部分接触者并完全隔离”与“覆盖全部但部分阻断传播”通常不是同一过程。
- **原文支持**：图2及相关讨论展示上述两种场景可以有不同的有效再生数；这建立在该文病例发现与症状过程等假设下。不能据此给本文设一个经验证的隔离残余传播比例。
- **修改用途**：支撑上一节建议句，并限制 `q` 的现实解释。现稿已经说明 `q` 不是检出速率，无须反复重复定义；也不宜在新增文字中把 `q` 改称已经吸收所有延迟、依从性与残余传播的“综合有效比例”，因为本文没有推导这种约化的等价性。

## 3. Ashcroft 等：人数、人天与释放规则

Peter Ashcroft, Sonja Lehtinen, Daniel C. Angst, Nicola Low, Sebastian Bonhoeffer. *Quantifying the impact of quarantine duration on COVID-19 transmission*. eLife **10**, e63704 (2021). [DOI](https://doi.org/10.7554/eLife.63704)；[公开原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7963476/)。

- **版本与阅读**：本轮取得期刊JATS全文，核读模型说明、被追踪接触者的结果与图1–3、Materials and methods 式(1)–(6)、Discussion；旅行者部分仅作背景浏览，未把全部附录与同行评议材料计为通读。
- **公式对象**：式(1)用隔离进入和退出之间的传染性核积分表示阻断比例；式(2)加入随感染后时间变化的假阴性；式(3)计不同检测结果下的平均隔离时长；式(4)以感染比例、阻断比例及平均隔离天数构造效用。效用定义本身是一项选择，并非货币化福利。
- **可支持的修改**：隔离人数与隔离人天不能互换；检测后释放、固定时长隔离与指数停留也不等同。因此本文现有计数结论和指数回流情景应按各自的明确模型解释，不称已经评估一般的隔离社会成本或真实释放政策。
- **已解决事项**：`02_model.tex:161`、`08_discussion.tex:26` 已说明成本不计人天；`S7_return.tex:18,107` 已定义指数停留与7–30 d情景。这里不应再次批评“没有说明”。
- **建议句（可选，压缩替换现有限定）**：

  > 本文比较未感染接触者的新增隔离人数；实际隔离负担还取决于停留时长与检测释放规则，二者不由该人数单独决定。

有限释放的文献可以解释补充S5的动机，不能证明本文正指数回流的共同下界，也不为平均停留7、14、30 d提供当地临床标定。本文回流下界仍应引用自己的命题及其条件。

## 4. 对能力约束的一个解释性建议

现稿 `04_joint_control.tex:37` 将 `q≤q_cap` 明确设为比例上限。它不等同于每日可处理人数或同时可容纳的隔离人数上限。直接由模型两条流入相加，被追踪进入 `S_q` 与 `I_q` 的总流量为 `cqSI/N`；因此相同 `q` 在不同 `S,I,c` 下对应不同流量。这个式子只说明现稿参数的量纲，不是对实际追踪工作人员负荷的校准，也不是新运行的数值结果。

Kretzschmar与James的过程模型为区分覆盖、时效和隔离效果提供依据；由此建议在能力约束首次定义处将已有末句扩成：

> 这里的能力约束限制干预强度，未另设每日追踪人数、隔离场所占用或调整速度的上限。

这是可选的概念澄清。若作者要施加流量或存量约束，允许控制区间和成本问题须重新推导；本轮没有把该研究列作投稿前必做任务。

## 5. 检索到但未进入主要依据的来源

Freya M. Shearer等. *Estimating the impact of test–trace–isolate–quarantine systems on SARS-CoV-2 transmission in Australia*. Epidemics **47**, 100764 (2024). [DOI](https://doi.org/10.1016/j.epidem.2024.100764)；[机构元数据与摘要](https://research.monash.edu/en/publications/estimating-the-impact-of-testtraceisolatequarantine-systems-on-sa/)。本轮核实Crossref与机构摘要，公开PDF终端返回403、网页读取502，未完成全文阅读；不据此给现稿规定追踪超负荷函数，也不引用摘要中的百分比作为主要修改证据。

## 6. 本轮判断

最值得采用的是把 `q` 的理想化过程解释清楚，并用一小句区分比例能力与实际处理人数。人数/人天与指数回流边界已有说明，最多补引文、合并措辞。以上文献没有否定本文在给定无回流模型和阈值策略下的计数恒等式、排序或成本结构。
