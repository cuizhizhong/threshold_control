# 任务2b：结构迁移（作者已验收）

日期：2026-10-06。起点：`main`，`f09f7e2a878111148d17d43a646f68d2faf370e7`。作者已验收2a，本轮仅执行另行授权的2b。

依据实际根 `AGENTS.md`、`STATUS.md`、已批准 `01_decisions.md`、本目录中的 `CODEX_EXECUTION.md` 通用约定与2b，以及2a子文件的实际内容和label。执行手册及其他起点已有未跟踪材料排除提交。未改规则、构建脚本、图源、参考文献、计算代码、数据或历史结果。

## 实际迁移与文件映射

两份正式入口名称不变。主文采用八章、附录A/B，补充采用S1–S5；共15个内容文件由入口的字面量 `\input` 加载。表格仍在所属内容文件内直接编辑。旧子文件内容完整分配后移除旧路径；移出主文不等于整体删除。

| 当前文件（相对 `paper/`） | 去向与保留边界 |
|---|---|
| `sections/01_introduction.tex` | 第1章；只更新末段结构指向，`sec:introduction`保留 |
| `sections/02_model.tex` | 第2章四小节；控制约定和能力界前置2.3，清零/累计定义、计数恒等式、成本及原有正权重说明前置2.4；`sec:model`、`sec:model:strategy`、`sec:cost`保留 |
| `sections/03_single_control.tex` | 第3章四小节；完整启动、能力、时间控制、退出、累计及参数/尺度结果；拐点定理、相对位置和端点分类留3.4；`sec:s1`、`sec:scaling-theory`、`sec:s1:shape`保留 |
| `sections/04_joint_control.tex` | 第4章四小节；状态表示、可行性、显式族、指标恒等式、连续可达时长与感染下界；`sec:joint`保留 |
| `sections/05_quadratic_cost.tex` | 原联合成本块成为第5章四小节；成本最小定理完整留5.1，5.2调用其有限候选判据；两个末端性质命题在5.3相邻，匹配乘子条件留5.4；`sec:joint:cost`保留 |
| `sections/06_numerics.tex` | 第6章六小节；西安参数表和共用方法前置6.1；基准图与原数字段进6.2；两组完整四策略表、图及原西安四策略数字段进6.3；能力、权重、乘子数值进6.4–6.6 |
| `sections/07_xian.tex` | 第7章四小节；重构、外部参照、退出代价及人口必要条件；TDINN独有范围句留7.2；`sec:xian`、`sec:xian:threshold-scale`、`sec:dominance`、`sec:dom:region`保留 |
| `sections/08_discussion.tex` | 第8章三小节；原讨论保留，人口参数移植和初值影响迁8.2；`sec:discussion`、`sec:dom:limits`保留 |
| `appendices/A_proofs_sensitivity.tex` | 附录A：九个完整证明及敏感性汇总表的三个兼容label |
| `appendices/B_control_cost.tex` | 附录B：原成本附录完整内容，另收`eq:joint:contact-cost`及显式族比较解释；`app:cost`保留 |
| `supplement_sections/S1_baseline.tex` | 基准完整扫描、归一化低阈值扩展、`tab:sup:baseline`及两幅扫描图 |
| `supplement_sections/S2_inflection.tex` | 敏感性命题和证明、未编号极值小表、两图及原附录F严格构造 |
| `supplement_sections/S3_xian.tex` | 西安扫描两图、初值及阈值完整两表、医疗需求与阈值量级两节 |
| `supplement_sections/S4_population.tex` | 完整人口比较条件、扫描、人口表和案例；原附录A/B/G完整迁入 |
| `supplement_sections/S5_contact.tex` | 常规接触率扩展及原附录C/D，四图完整迁入 |

附录A九个证明对应：`prop:model:threshold-rationale`、`thm:s1:tend`、`lem:s1:Sstar-sensitivity`、`prop:threshold-tradeoff`、`prop:contact-effects`、`thm:joint:representation`、`thm:joint:cost-minimum`、`prop:joint:terminal-allocation`、`prop:joint:global-structure`。旧处只加入最短证明指向；最后两个证明顺次相邻。

## 删除、保留与待续事项

- 独立研究内容删除：无。原文保留；变化限于批准标题、迁移后的交叉引用、最短指向和TODO。旧源块生成器注释仍保留，未执行任务3清理。
- 旧标题按D-01/D-02替换，迁补充的原附录降为对应小节；“本附录/附录图”更新为当前“小节/图”。原模型段尾“本文规定控制期间满足”改为“控制期间的约束见第…节”，原约束方程完整迁2.3。引言路线图及迁出附录的指向作最短更新。
- 西安四策略段的数字和机制解释完整迁6.3，独有TDINN范围句留7.2。为保持2b原文，本轮未删段内重复数字；TODO留4e-3按批准范围精简。
- TODO：2.3控制类正式命名留4a；3.3旧衔接留4b；第4章旧成本路线图留4c；6.3重复段留4e-3；第7章原路线图及“后续/下一节”称呼留4f。未开始术语替换或正文重写。
- `limitations_pool.md`无内容移入、未创建；人口影响仅按批准映射迁8.2。数学、数字、参数、初值、统计终点及单位无改变，一般正权重只迁原有说明。
- E-POP、E-WEIGHT、E-MULTIPLIER、E-INTERSECTION保留原有限证据及未解决说明，未补算或认证。D-XIAN-LINEAR继续暂缓、非阻塞，未研究、追溯、补算或验证。
- 待作者确认：无新增数学或结构决定；本轮交付整体待作者验收。
- 后续配合：主文图5、图10浮动页和补充第6–7页表格留白留5b；S3标题在补充第5页末。现有参考文献仍沿用模板排序，首次引用顺序要求登记到文献阶段。本轮不扩展修改版式或文献样式。

## 本轮实际检查

1. 本轮前展开稿与baseline去注释、去空白后相同，未覆盖baseline。按旧子文件行块记录去向，非空实质行无遗漏、无重复分配；快照与辅助证据在忽略的 `paper/tmp/02b/`，不提交。
2. 实际完整块比对：28个定理类环境原文一致，27个证明均完整；唯一证明文字变化为S2末句把原附录F改称当前小节。91个`equation`、7个`align`、3个`align*`完整一致；24个图块、8个编号表块及未编号极值小表保留。图表块也保留参数组、策略、指标、统计终点、表注和单位，未只凭数字总数判断。
3. 201个既有label全部保留，新增17个结构/证明指向label，重复0；15条输入存在、唯一且覆盖全部内容文件，图路径可解析。正文10图、补充14图；编号表为正文4张、补充4张。
4. 四张保护图源SHA256与批准记录一致，完整图块和显示尺寸不变；`jointcapacitypostexitdays`定义先于调用且仍为1。当前实际定位：`fig:scenario1:single-sim`为图2/p19，`fig:scenario1_summary_eta`为图4/p20，`fig:joint:compare`为图5/p22，`fig:joint:capacity`为图6/p23。原图8对应保护对象未合并。
5. 实际运行以下命令；`02b_check.md`报告标签缺失、悬空引用、重复标签、bib缺键均0，数值字面量756→756，缺0、增0。未引用bib键仍为`ShaanxiHealth2022`、`Zhang2026Behavior`。

   ```powershell
   python paper/tools/check_tex.py --old paper/tmp/02b/before/main.tex paper/tmp/02b/before/supplement.tex --new paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex --bib paper/references.bib --out paper/revision_notes/02b_check.md --stats
   powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1
   ```

6. 补充入口补齐迁入内容所需宏、环境、图搜索路径和主文外部引用。按既有入口先补充后主文，各自XeLaTeX → Biber → XeLaTeX → XeLaTeX。首轮补充读取迁移前主文AUX出现46处重复标签；主文AUX刷新后完整重建，最终两份日志的未定义引用、重复标签、Overfull hbox和`Warning:`均0。主文36页、补充21页；原Underfull hbox（badness 2376）随原段迁S4。Biber日志无WARN/ERROR，Perl locale回退到`C`的提示未影响构建。
7. 实际检查PDF双向引用：主文12个、补充16个`GoToR`链接，目标PDF及命名目的地均存在；全文未发现`??`或`[?]`。
8. Poppler以110 dpi渲染全部57页并作逐页版式总览；另放大查看主文19、20、21、23、34页和补充1、4、6、7、12、17、18、19、20页。保护图、完整四策略表及迁入内容未见裁切、重叠或整页空白。最终仅补回原注释后重新渲染，两份PDF共57页PNG的SHA256与上述已查看版本逐页相同，差异0。
9. 去注释的展开正文汉字数：主文28110→22358，补充1241→7431。变化来自迁移、标题和指向句，未作正文压缩；各节统计见检查报告。Git空白检查按既有CRLF约定`cr-at-eol,-blank-at-eof`通过。

检查器合并两文档标签判断外部引用，不主动报缺失输入，退出码也不涵盖全部问题；本轮另查输入覆盖、完整环境块、源图哈希、实际构建和PDF外部目的地。未扩展检查器或恢复旧管线。Linux构建、研究计算、后续任务及英文阶段未执行。

## 交付与停止点

修改两份入口与上述内容文件，移除内容已完整迁出的旧子文件，新增本记录和检查报告，更新`STATUS.md`。仅本轮源码及三份记录进入本地提交；PDF、AUX、LOG、BBL、临时证据和起点已有未跟踪材料排除。提交号从Git和回复读取，不回填自身hash。

交付时状态：**待作者验收**。

验收登记（2026-10-06）：作者在本对话明确表示“我已验收”，验收交付提交为`16eb7e0d0eed0c180e7e5d152ccf72b74967eadf`。当前状态：**作者已验收**。本次仅更新本记录与`STATUS.md`，复用上述2b检查，不改论文源码，不重新编译。停在2b，等待作者另行点名，不push，不自动执行任务3或后续写作任务。
