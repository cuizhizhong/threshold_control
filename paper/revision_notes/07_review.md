# 任务7：全文一致性检查

日期：2026-10-07。状态：**待作者验收**。

起点：`main`，`6f207f0199d5fb5e75ecdfd627173feefbda90c1`（6a、6b验收登记）。本轮只执行任务7；依据实际 `AGENTS.md`、`STATUS.md`、`01_decisions.md`、本地执行手册的通用约定及任务7，按当前文件和label检查。未启动独立审稿或英文阶段。

## 实际改动

- `paper/flatten_curve_supplement_cn.tex`：补充入口原按默认顺序排列文献，与项目的首次引用编号要求不一致。新增一行 `\ExecuteBibliographyOptions{sorting=none}`；主文已有该设置。补充实际BBL顺序现为 Baas、XianStat、Chen、Angulo、Pung，与首次引用一致。
- 新增本记录及 `07_check.md`，更新 `STATUS.md`。没有删除、移动正文内容，没有移入 `limitations_pool.md` 的内容；没有修改bib、引用键、模型、数学、数值或图件。
- 17份正式TeX逐文件对照本轮起点，仅补充入口新增上述一行，其余16份字节相同。展开后的去注释汉字数：主文22952→22952、补充8145→8145；检查器计数字面量692→692，无新增或消失。

## 已通过：去向、完整性及论断范围

当前组织为八章、附录A/B、补充S1—S5，正文10图、补充14图，主文4张编号表、补充4张编号表，另有S2未编号数值小表。逐项对照D-01—D-03，未发现批准对象丢失或去向不符。

| 对象 | 当前实际位置与证据 |
|---|---|
| 模型及指标 | `sections/02_model.tex`；`prop:model:positive`、`prop:model:threshold-rationale`，控制类及三个累计量分别定义 |
| 仅隔离解析结果 | `sections/03_single_control.tex`；10个结果环境，包含启动、轨迹、退出、累计量、敏感性、规模关系及拐点 |
| 联合可行性与指标比较 | `sections/04_joint_control.tex`；8个结果环境，包含状态表示、能力条件、显式族、比较及退出感染下界 |
| 二次成本 | `sections/05_quadratic_cost.tex`；5个结果环境，包含存在性、有限候选、阈值、退出附近及乘子充分条件 |
| 西安人口必要条件 | `sections/07_xian.tex` 的 `prop:dom:floor`；完整人口表与扫描在 `supplement_sections/S4_population.tex` |
| 指定长证明与成本公式 | `appendices/A_proofs_sensitivity.tex` 的九个指定证明及敏感性汇总；`appendices/B_control_cost.tex` 的成本积分与闭式表达 |
| 辅助材料 | S1基准扫描与低阈值极限，S2拐点敏感性及正负导数构造，S3西安初值/阈值/医疗关系，S4人口条件与案例，S5接触率与传播概率扩展 |

共有28个定理类环境、33个结果label（含5组兼容别名），与baseline结果逐项对应。27个显式 `proof` 环境全部保留；乘子注记另保留逐状态不等式论证。对baseline的证明文本比较中，21个在去空白和既定术语统一后相同；其余6个逐段查看，仅为术语、迁移指向和过渡语调整，其68个数学片段相同。正文“证明见附录”的对象与实际证明位置对应。该检查确认保存与衔接，不等于独立认证全部数学结论。

已通读摘要、第1—8章、附录及补充并对照结果条件：

- 主线仍以非隔离感染人数 `I≤η` 为约束；`I+I_q` 未混作约束，`η` 是外生设计参数。无回流假设、启动/退出规则及完整初值在相应对象附近保留。
- 最快与累计感染排序保留固定起止二维状态及 `0<β<1`；全过程比较另保留共同完整初值、`η>1` 与共同退出后规则。累计新增感染、新增隔离易感者及二次成本的统计范围分别保留。
- 最小成本结论限定于已定义阈值控制类；一般正权重与固定默认权重闭式公式未混用。阈值的严格下降、能力扩大时的不增、退出附近混合及单控制严格成本比较的条件保留；端点局部判据未改作一般全局切换定理。
- E-WEIGHT的161点权重网格、E-MULTIPLIER的470个离散乘子点、E-POP的固定绝对初值人口扫描、E-INTERSECTION的16点及插值仍是有限证据；连续转折、全时长匹配、连续人口集合及一般交点唯一性未被摘要或结论认证。
- 西安40日重构、各策略清零终点、同条件四分配与外部TDINN参照有明确区分。医疗需求关系保留共同滞留核、平均需求及初始占用等条件；0.002N情景未写成当地临床容量标定。
- 当前正文没有把未核实的西安线性成本反转写成已验证论断。`J_c,J_q` 定义及已有二次成本、两组四策略、西安外部参照保留；D-XIAN-LINEAR继续 **deferred / non-blocking**，未追溯或补算。

## 已通过：数字对应及保护图

除字面量检查外，按参数组、策略、指标、统计终点与单位只读对照已保存结果。6张数值表的194个单元格按原显示精度逐项一致；没有运行研究计算。

| 当前表label（实际页） | 已保存来源及检查口径 |
|---|---|
| `tab:joint:compare`（主文22页） | `20261005_sec7_v2_refinement/joint_extra/compare_baseline.csv`、`compare_xian.csv`；两组四分配的时长、清零、总累计、新增隔离易感者、J；基准人数为人，西安为10^6人 |
| `tab:xian_summary`（主文27页） | `20261003_release_final/xian/summary.csv`；三策略的全过程峰值、各自清零的总累计、终点及J；TDINN与阈值策略的成本区间按表注区分 |
| `tab:sup:baseline`（补充2页） | 同批 `baseline/main_c0_summary.csv`、`main_eta_summary.csv`；固定5%改变c0及固定c0=10改变阈值两组，共10行 |
| `tab:sup:initial`（补充6页） | 同批 `xian/S2_window.csv`；观测、拟合、固定I0=1三行的40日累计与日新增峰值；不混入清零累计 |
| `tab:sup:eta`（补充6页） | 同批 `xian/eta_scan.csv`；11个阈值比例、隔离比例、时长、清零、J及至清零的总累计 |
| `tab:dom:thresholds`（补充11页） | 同批 `population/critical.json`；5项分别对应必要人口下界、参考条件界值及扫描最大值，不混作已证全局边界 |

上述结果目录均在 `reproducibility/results/` 下。另核对表1及正文参数、`manuscript_audit_notes.md` 的未取整西安初值 `0.00100659188867187`、40日与45.2874日的不同累计量，以及代表能力组合和默认权重。当前数字来源与终点说明一致；历史结果中的误差与网格判定没有冒充本轮重算结果。

24个图源均存在，哈希与本轮起点提交相同。四保护图的哈希还与批准记录逐一一致，实际正文引用有效；放大查看图内变量、图例和图注后，未发现含义冲突。

| 保护label | 当前文件、图源与实际页 |
|---|---|
| `fig:scenario1:single-sim` | `sections/06_numerics.tex`；`figures/optimal_control_with_quarantine_panels.pdf`；现图2、19页 |
| `fig:scenario1_summary_eta` | 同节；`figures/layout_v5/eta_sensitivity_selected_c0.pdf`；现图4、20页 |
| `fig:joint:compare` | 同节；`figures/joint_v2/joint_compare_baseline.pdf`；现图5、22页，(c)是 `(I+I_q)/η` 的参照 |
| `fig:joint:capacity` | 同节；`figures/joint_v2/joint_capacity.pdf`；现图6、23页，(c)绘至名义退出后1天；有效宏 `jointcapacitypostexitdays` 保留 |

## 已通过：实际构建与PDF检查

- 在仓库根目录运行 `python paper/tools/check_tex.py --old paper/tmp/07_review_6f207f0/flatten_curve_analysis_cn.tex paper/tmp/07_review_6f207f0/flatten_curve_supplement_cn.tex --new paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex --bib paper/references.bib --out paper/revision_notes/07_check.md --stats`。退出0，递归展开15个输入；220个label全保留，缺失、悬空、重复标签及bib缺键均0。另逐输入检查文件存在性，缺失0。两个既有未引用bib条目不动。
- 最小修复后实际运行 `powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1`，先补充后主文，各XeLaTeX→Biber→XeLaTeX→XeLaTeX，退出0。主文36页、补充21页；最终日志中未定义引用、重复标签、Overfull/Underfull、LaTeX/Package Warning、Biber WARN/ERROR均0。主文17条、补充5条BBL顺序分别与首次引用一致。
- 初次沙箱内Biber曾因 `{Illegal System DLL Relocation}` 启动失败；同一构建入口经自动审查允许后在沙箱外成功，修复后又完整重跑成功。Perl的 `C.UTF-8` locale回退启动提示仍存在，单列为环境提示，不计为文献或LaTeX通过项。
- 本轮重新渲染并逐页查看全部57页，另放大四保护图页；未见截断公式、重叠、缺字或不可读表格。已知6.2断句仍存在，见下。主文36页提取文本与起点PDF全部相同；补充只有8、9、21页文本变化，对应引用编号与文献顺序。
- 主文15个、补充23个跨文档PDF链接的文件和命名目标均有效，共38个，未发现未解引用标记。此为PDF目标解析检查，未逐链接操作特定阅读器。

## 待修／待作者决定

1. **6.2局部版式**：主文18页末句在“无需启动”后断开，末尾“仅隔离控制。”位于20页图后，与6a记录一致。建议后续单独处理该句与浮动图的相对位置，保留图源和显示尺寸。本轮任务7只允许纯错字或确定引用错误的最小修复，未改第6章版式。
2. **作者与题目**：两入口仍有 `\author{XXX \and XXX}`（主文第6行、补充第5行）；没有形式为TODO/FIXME/TBD的剩余占位。作者信息须提供真实内容，当前题目及6b的候选选择保持待定；未猜测替换。
3. **投稿的数据/代码入口**：补充所写本地审计说明和结果路径真实存在且已跟踪；现稿尚无单独的数据/代码可用性声明或正式发布链接。根目录及复现README明确旧路径未修复、原一键入口已删除，不能据此声称可直接完整复现。整理入口、验证研究复现、确定实际发布地址及相应声明须另行授权；本轮未修改计算代码或补写未经证实的公开可用性承诺。

## 未测试及覆盖边界

- 未进行独立数学认证、研究程序重跑、容差/网格再收敛、重新拟合、重绘、Linux构建、英文投稿格式核实或任务8独立审稿。既有文献定位沿用6a已验收核对，本轮检查引用与论断关系，未重新逐篇核验全部文献元数据或外部网址当前可达性。
- `check_tex.py` 会展开当前输入，但缺失输入可能静默保留原命令；重复label、缺bib键虽列入报告，却不一定触发非零退出。它排除单个整数等部分字面量，也不检查证明逻辑、数字语义、图内文字、PDF布局或跨文档实际目标。本轮分别用文件存在性、报告明细、语义/表格对照及PDF检查补充上述当前稿覆盖，未修改或扩建检查器。
- E-POP、E-WEIGHT、E-MULTIPLIER、E-INTERSECTION继续保留已批准的未解决说明，未标记为数学通过；D-XIAN-LINEAR继续独立暂缓。

提交仅纳入补充入口、`07_review.md`、`07_check.md`、`STATUS.md`。临时快照和检查证据位于忽略目录 `paper/tmp/07_review_6f207f0/`；PDF、编译产物、执行手册及既有未跟踪材料不纳入。保存本轮一次本地提交后停止，不push，等待作者决定验收后进入独立审稿或先做局部返修。
