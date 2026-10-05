# 联合控制 A–D：本轮复算、正式稿整合与交付核查

## 结论与范围

本轮批准的 A–D 均完成：四策略比较、能力限制、二次权重敏感性、成本与时长的有限乘子支持点核查。正式工程已更新并执行完整编译；正文51页、补充材料3页，24幅图、5张正文表和3张补充表。新增4幅图与1张六列分组表；原有20幅图文件、7张表体、第9节订正及旧编号公式/证明均保留。

这里的“完成”限定于计划批准的参数、代表点和有限扫描，以及对应求根、求积、开环 ODE 和收敛检查。它不表示一般状态约束最优控制、严格区间根隔离、全部参数解析分类、完整成本—时长前沿或真实 ICU 标定已经完成。

本轮没有使用 Nature 技能，没有重新拟合或积分 TDINN，没有重跑无关历史 MATLAB 实验，没有提交或推送 Git。科学计算、继承验收、文案回归、编译、人工页面审阅分别记录。

## 1. 基准、输入和保护

- 开始时 `HEAD` 为 `accb1e65f50aaca7ca1aaea7f5e7b6c19bcdc691`；结束时仍为该版本。
- 修改前工作稿、PDF、文献、模板及相关程序保存于 `../../backups/joint_integration_20261004_212826/`。正式发布前另保存 `../../backups/before_verified_publication_20261004_233700/`。
- 基准参数来自冻结包 `joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json`，SHA-256为 `5aeafe3fe2ba5809eda90a9fbfd9c722dd9161e9d026e5740dd74f94e183f9d6`。
- 西安来源为 `reproducibility/results/20261003_release_final/xian/reference.json`，SHA-256为 `b920deaf55f771958433ab27f32ca1606393c9ae7b96d3361aee053af097bc45`。沿用未取整 `I0_abs=0.00100659188867187`、`delta_q=0.3531` 和全部仓室参数，不使用候选代码的省略参数或人口倍乘统一容差。
- [最终保护核查](protection_final.json)实际通过：595个受保护旧文件哈希不变，20幅旧图不变，7张旧表体不变，第9节内容不变；90个旧 equation、7个旧 align、26个旧 proof 全部保留。新增内容使 equation/proof 各增加1个。章节、图表与定理编号按现有计数器自然顺移。
- 冻结目录87文件完整保留：发布检查核对86个清单条目及清单文件自身，不能将86个条目误称为整个目录只有86文件。原始输入和既有验收没有被覆盖。
- 开始时已有的未跟踪计划、文献PDF和清理日志未纳入删除操作；本轮没有清理历史文件。

## 2. 实际科学计算与两次独立运行

正式科学依据为 `../../runs/joint_integration_20261004/run_5/joint_extra/` 与 `run_6/joint_extra/`，两次均在新空目录从相同输入独立计算，没有用第一轮输出充当第二轮输入。

计算期锁定四份科学源码、输入、软件和验收门槛。最终四源码哈希为：

| 文件 | SHA-256 |
| --- | --- |
| `joint_extra/core.py` | `62df75cd98542dd7c8f2401ce63c01a0140a0546ce8a4c56fe7fc0fee258d2bc` |
| `joint_extra/run.py` | `a1156e16408ec471444bc5b11fab714a21e4b1c6991821d5d8207011e8b3e3cb` |
| `joint_extra/validation.py` | `2bd9ff3b9a7235adb2d430e8a8dbac29d3e02da8b84fece8abcd6fb5ffed05a8` |
| `joint_extra/acceptance.json` | `45146c8aab1f41b6249b3db427ee8f08b6612a81325d557ab5cbaf787f36613a` |

实际验收包括允许端点与全部数值实驻点、原坐标/退出缩放坐标交叉检查、近并列候选记录、分支及切换加密、求积和状态网格收敛、固定名义时间开环的完整仓室独立积分、非负性、质量守恒、控制边界、平台和退出误差、清零方向、两项平台计数恒等式，以及稠密解导数零点/阶段端点/切换两侧的峰值核查。控制不依赖实际积分的实时状态，实际事件也不纠正名义退出时间。

任务摘要如下；完整精度结果在本轮 CSV/JSON/NPZ 中，17位 CSV 仅用于浮点往返，不认证全部尾数。

- A：基准与西安四策略均使用共同启动状态和退出目标、相同累计定义及清零统计终点。最低二次成本相对仅隔离降低，但控制时长及累计感染增加，正文保留这一不利结果。西安成本从40.7686降至38.0209，时长从85.07增至108.81天，累计新增感染从约237.79万增至253.48万；不据此声称支配固定外部 TDINN 参照。
- B：两组600×600能力分类及两代表点、能力等号点、退化/轻微不可行测试通过；等号归可行侧。受限成本基准2.3611264994、西安41.6165963179，均不低于对应无额外能力限制成本。完整能力边界控制及其独立轨迹保留。
- C：固定 `wc=1`，`r` 在0.1至20的有限网格上扫描并加密显示切换。默认 `r=2` 与 A 完全一致；退出端点遮罩，不以理论填充值验证极限。局部端点判据与数值全局选择边界有区别，正文和图注均予以限定。
- D：310个有限κ点全部通过，κ=0回归 A；乘子驻点方程重新含κ，不用网格最小值替代完整候选比较。实际连接组保留9处较大相邻时长间距，图上断线不证明中间时长不可达，也不宣称获得完整前沿。四个κ代表点另做完整 ODE 核查。

[独立静态复核](independent_science_audit.md)核对计数、默认权重、能力成本、分支、未取整结果及正文片段，但不冒充第三次科学复跑。

### 失败历史没有抹除

`run_1/2`、`run_3/4` 保留实际 `partial` 和原失败点；不改编号、不填回新结果。[首轮记录](first_round_notes.md)与[第二批记录](second_round_notes.md)说明名义时钟放大误差、全局求积漏估、能力几何折点插值及缺失分支伪零点。两份失败版本源码另存并匹配其各自输入清单。

修复收紧计算精度并纠正分段/分支实现，没有调松预先锁定的验收门槛。独立诊断探针不是最终通过记录；正式依据是随后重新计算的 `run_5/6`。

实际通过的开发检查包括20项求解器测试（[日志](unit_tests_v4.log)）、26项发布/选择守卫测试（[日志](publication_guard_tests_final.log)），以及保留的旧 `joint.py` 基准回归。旧基准最低成本约2.1182745585，与新模块一致。

## 3. 受控稿源、出版回归与结果汇集

受控稿源为 `../../manuscript_versions/20261004_joint_integration/`，源于本轮本地正式稿及批准修改，不来自候选整稿覆盖；原冻结包不变。其清单 SHA-256为 `a8a49821a1c793edfeec1deca3eee4563c702b38a4afb8ffd144e32ae66dab87`。

科学计算完成后另做出版快照和后处理，记录明确区分这两个阶段，不能说全部出版源码在计算开始前已经锁定。两轮后处理前后科学结果哈希不变；纯文案片段按唯一锚点同步，缺失或重复匹配即失败，不回退冻结旧稿。

[出版生成检查](publication_generation_checks.json)实际通过：能力限制补充、审计分流、第9节和已有数学块均保留。两份工作稿均完整编译为51+3页。

显式选择的 `accepted_runs.json` SHA-256为 `58fda5b8f878aa558f9560df64913c903291f3f70f6a07ea5101d1e94904afee`。实际严格双跑比较及发布前重复比较均通过：31份结果及验收文件、5,404,561个数值项，在 `rtol=1e-10, atol=1e-9` 下无差异；24幅图在120 dpi下逐像素一致。原20图继承已验收文件，不声称本轮重新生成其科学数据。

新增结果已经汇集到 `../../results/joint_integration_20261004/joint_extra/`；[汇集清单](publication/collection_manifest.json)记录65次文件复制及哈希。汇集副本不是下一次计算输入。旧根索引的快照位于 `collection/previous_active_index/`；历史验收目录不改写。

## 4. 正式编译、人工审阅与发布

[正式发布清单](publication/publication_manifest.json)为实际成功记录。正式目录调用 `latex/build_paper.ps1`：补充材料 XeLaTeX 两遍，正文 XeLaTeX→Biber→XeLaTeX→XeLaTeX。正式重编译的全部51+3页与已人工审阅工作副本逐页文本相同、120 dpi逐像素相同；PDF字节因元数据变化而不同，不将其当作科学差异。

主代理实际查看全部51页正文概览、19页重点独立渲染，补充3页逐页查看；独立代理另审摘要、引言、理论、新图表、西安、第9节、附录和文献重点页。两份实际人工记录位于 `run_5/validation/manual_review_root.json` 与 `manual_review_agent.json`，绑定对应实际 PDF 哈希。

正文仅打印一次参考文献，20个已引用条目在第50至51页完整显示，无未解析引用、缺失文献、Biber警告、Overfull、浮动体过大或缺字。仅保留第9节既有 Underfull hbox（badness2376），所涉页面实际检查没有出框；作者XXX仍为既有草稿占位，不宣称已修复。

正式输出 SHA-256：

- 正文PDF：`e4dce872903de9b86582b7c5f106511bc6cd76d1d457de226534226dca0f107f`。
- 补充PDF：`fd26d7bbc369fd470717d7b47934ead39846615a6284f681e158f885e17ab925`。

首次发布命令因独立人工记录的字段位置不同，在复制前被守卫拒绝；仅补齐记录 schema 后重试，未改守卫或容差。见[格式检查记录](publication_schema_check.md)。

## 5. 交付和重新运行

完整包预计保存于 `../../deliverables/joint_integration_20261004.zip`，同名目录为可直接查看的工程副本。实际打包状态、文件数和ZIP哈希以旁边 `joint_integration_20261004_archive_manifest.json` 为准；不存在成功收据时不能称打包完成。

包内包含正式论文工程、活动源码、原始输入、全部87份冻结来源、旧验收参照、本轮两次通过与四次失败运行证据、未取整结果、受控稿源、修改前备份和本核查资料。包装层另补入 `reproducibility/assets/` 的9项可编辑模型图与图件适配资产，原已冻结打包程序不改写；不包含环境和字体。

软件与字体须按 `reproducibility/requirements.txt`、`environment.json` 及说明安装；本轮实际 Python3.12.8、NumPy1.26.4、SciPy1.13.1、XeTeX/TeX Live2026、Biber2.21，MATLAB旧验收环境另列，不冒充本轮新MATLAB验收。

解压换路径后，先配置环境，再从包根目录编译：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File latex/build_paper.ps1
```

新增模块可在两个全新空目录独立运行，显式指定同一参数来源；以下只是一轮的命令示例，不复制旧结果：

```powershell
python -B reproducibility/joint_extra/run.py --root . --baseline joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/baseline_parameters.json --xian-reference reproducibility/results/20261003_release_final/xian/reference.json --out reproducibility/runs/NEW_joint_A/joint_extra --mode compute --tasks A,B,C,D
```

或使用 `reproducibility/run_all.ps1 -Scope joint-extra` 创建两次独立运行、生成图文、编译及比较。`-Scope all` 会重建旧上游并向新增模块传同次西安参照，本轮未再执行该全历史流程。换路径后的旧审计记录仍保留原绝对路径，不能直接送旧运行到发布守卫重新认证；应在新空目录生成新的记录。旧记录不改写。

## 6. 仍未解决的事项

- `fig:dom`（整合前图13，当前自然顺移为图17）的案例标记与后续轨迹逐点绑定仍待核查；本文保留原图及既有暂存说明，不声称本轮修复。
- 第9节候选求根值对应的连续允许人口区间尚未一般认证；实际指标、严格触发与参考直线的区别保留。
- 有限权重网格及有限κ支持点不是全参数/全时长的完备证明；近并列不认证唯一解，所有时长上的最小成本仍未覆盖。
- 真实ICU占用、回流、响应延迟、新受限算例的进一步系统扫描不混入本轮结论。

交付后若修改受控稿、计算源码或输入，应另立版本并重新验收，不能复用本轮锁定报告冒充新版本通过。
