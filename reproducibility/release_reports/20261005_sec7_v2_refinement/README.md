# 第7节 v2 整合与图12加密：本轮核查记录

## 结论与范围

本轮已完成正式工程更新。基准为提交 `894fd49c99cc52fbaf8e2992c08457ff456c4749` 及当前本地主稿；仅采用 `ai/第7节文字修改_20261005_v2/`，未整份覆盖为候选稿。正式主稿仍是 `latex/flatten_curve_analysis_cn.tex`，正文51页、补充材料3页。未提交或推送 Git，未使用 Nature 技能。

本轮重新计算联合控制 A–D；西安拟合、TDINN参照和其他历史研究结果继承指定验收版本，未重新拟合西安、积分TDINN或运行旧MATLAB实验。全文页面检查和编译不代表整稿科学复跑，也不替代数学证明复核。

## 修改内容

- 按唯一 `JOINT_EXTRA` 锚点局部整合7.2–7.5节及图10、11图注，保留局部判据与全局候选选择、有限权重网格、几乎处处控制约定、同一易感者状态与完整轨迹的区别。
- 第7.5节使用符号精确端点、实际二次成本夹界和动态结果文案；没有硬编码点数或时长，不将有限扫描解释为完备前沿。
- 正文及补充表的 `J` 列统一四位小数；其他列不变。第10节西安成本比较增加 `w_c=1,w_q=2` 的限定。
- 图9原PDF、通栏宽度、比例和字体不变；正式模板下图9与表2同处第28页，不需额外调整浮动顺序或缩小字体。
- 仅重新生成图12 `latex/figures/joint_v2/joint_frontier_baseline.pdf`。其余23幅正式图件逐字节不变。图12仍采用原配色、字体、尺寸、对数横轴及负乘子短虚线。
- 更新文案生成、成本精度同步、选择性绘图、源码收集和受控版本入口；错误或不完整证据拒绝生成相应结论。

## 基准、保护与受控版本

修改前备份：`reproducibility/backups/sec7_v2_refinement_20261005/`。正式发布前又备份至 `reproducibility/backups/before_verified_publication_20261005_122816/`。

`baseline.json` 固化原始输入、冻结包、旧结果、历史验收及稿件和图件哈希；`protection_final.json` 实际核查678个保护文件未变，证明、编号公式、引用键、标签、图表登记及第9节保持不变，仅批准图12变化。主稿局部差异见 `protection_final.patch`。

新受控版本：`reproducibility/manuscript_versions/20261005_sec7_v2_refinement/`。先以不激活模式创建并校验，后显式批准切换 `current.json`；旧指针及批准凭据保存在 `reproducibility/manuscript_versions/approvals/`，未删除指针或绕过覆盖保护。对应本轮记录为 `version_created_inactive.json`、`version_activation.json`。

## 本轮科学复算

两个独立空目录：

- `reproducibility/runs/20261005_sec7_v2_refinement/run_1/joint_extra/`
- `reproducibility/runs/20261005_sec7_v2_refinement/run_2/joint_extra/`

两轮均显式读取冻结基准 `joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json` 及已验收 `reproducibility/results/20261003_release_final/xian/reference.json`。第二轮未用第一轮输出作输入。每轮 `input_manifest.json` 记录完整参数路径、哈希、原310个乘子、加密候选网格和构造规则。

执行入口为 `python -B reproducibility/joint_extra/run.py --root <项目根目录> --baseline <上述冻结参数> --xian-reference <上述验收参照> --mode compute --tasks A,B,C,D --out <独立空目录>`。计算完成后用 `postprocess_joint_extra.py` 独立后处理；两阶段源码清单分别保存，不将计算后才完成的出版代码冒充计算前已锁定。

两轮A–D均通过原验收门槛。原310个binary64乘子保留原值，增加 `k/500, k=-300,...,-100` 共201个候选；仅删除与已保留值绝对差不超过 `1e-12` 的新增点，实际新增160点，最终470点。原网格内部已有的近重复浮点对不删除。

验收覆盖完整端点与驻点候选比较、根残差、求积及加严容差、权重和能力网格检查；A–C及D规定代表轨迹进行分段名义时间开环、完整仓室独立ODE、质量守恒、非负性、控制边界、平台和退出误差、清零方向、累计恒等式及独立峰值核查。D的470点全部通过候选与收敛检查；没有将全部470点声称为逐点完整仓室ODE复跑。

旧点对照见 `scientific_regression.json`（38项记录）及 `independent_scientific_audit.json`：A–C结果、原D点完整精度指标及全部候选/收敛诊断与旧验收一致；原D点指标最大绝对变化为0，`kappa=0` 与任务A一致。两轮严格比较见运行目录的 `repeatability.json`：31个数值文件、24幅图渲染及输入/源码身份均通过，容差仍为相对 `1e-10`、绝对 `1e-9`。

图12重新按既有间距规则分组，实际缺口为0。最大相邻时长差约0.371331天，所有相邻距离均小于原规则的0.5天最小阈值；不是通过放宽规则连线。保留未计算中间时长的限定。470点动态文案中的10%成本范围最大计算时长和下一点均来自本轮CSV，不是精确连续临界值。

## 文案回归、测试与编译

`inherited_prose_regression.json` 只用旧验收检查文案；`current_prose_run_1.json` 和 `prose_only_regression/` 使用本轮结果检查完整生成与批准稿源一致。旧验收回归本身不是新的科学计算。能力限制补充、审计分流、第9节、块外图注及原证明均保持。

`final_complete_tests.log` 记录本轮实际执行的100项测试，全部通过；包含错误 `c0`、能力上限0.15、分段证据缺失、默认切换或峰值关系改变、网格结构改变、失败/非有限D数据和锚点缺失/重复等负例。取整端点 `T=5.90` 与实际端点 `5.9025558511400265` 区分检查通过，实际端点等号、二次成本夹界及默认 `r=2` 独立来源通过。

`publication_guard_tests_current.json` 记录170项实际身份检查及错误PDF摘要、失败双跑、错误数值摘要的拒绝测试。未放宽生产发布门槛。

两轮隔离稿均实际完整编译；人工检查通过后，正式目录再次执行 `latex/build_paper.ps1`：补充材料XeLaTeX两遍，主稿XeLaTeX → Biber → XeLaTeX两遍。正式PDF与已审阅稿的全部页面文本及渲染完全一致；PDF元数据哈希不同不解释为科学或排版差异。

正文只有一份参考文献，20条均输出。无未定义引用、Overfull、超大浮动体或Biber警告；正文第9节保留一处非阻断 `Underfull \hbox`（badness2376），补充材料无排版警告。

根代理实际看过正文1–51页及补充1–3页概览，细看正文26–35、42–44、50–51及补充第3页；另一个代理独立细看19页。两份人工记录绑定审阅PDF哈希，见 `collection/run_1/validation/manual_review_root.json` 与 `manual_review_agent.json`。页面检查不替代数值或证明验收。

## 产物与待办

正式工程：`latex/flatten_curve_analysis_cn.tex/.pdf`、`latex/flatten_curve_supplement_cn.tex/.pdf`、图12及原有模板/文献库。未取整CSV/JSON、NPZ和470点诊断汇集在 `reproducibility/results/20261005_sec7_v2_refinement/`；65份汇集文件均有摘要绑定，输入源仍指向实际运行和冻结/验收来源，不将汇集结果充当从头计算的输入。

发布及汇集记录：`publication/publication_manifest.json`、`publication/artifact_preflight.json`、`publication/collection_manifest.json`。新版源码收集、环境、选择清单、结果登记和验收日志另存于 `collection/`；旧索引另存 `collection/previous_active_index/`。冻结包、历史报告和失败运行没有覆盖或删除。

本轮开发核查中，两项网格测试最初把原网格已有近重复值误作错误，及用过严的浮点步长测试；已订正测试而非科学设置。旧发布测试入口原绑定20图历史记录，已改为当前24图验收身份，生产守卫未放宽。独立科学报告的一处手工哈希录入错误已按实际10项文件摘要订正；科学文件未变。两份本轮静态 `verify` 报告保留在 `static_verification/`，避免不同时间戳文件名混入科学双跑文件集合；未删除原始计算输出。默认 `git diff --check` 把保留的CRLF行尾报告为尾随空白；启用 `cr-at-eol` 后，对本轮Python、Markdown、TeX和JSON的检查实际通过，未为消除提示而全文件转换行尾。

未由本轮解决的既有事项仍保留：图13案例标记绑定、允许人口连续区间的证据范围，以及作者XXX占位。没有新增渐近展开、理论命题、全域权重临界值或完整效率前沿认证。
