# NEW-4b 中文审阅版小修（2026-10-19）

工作树 E:/work/draft-submission-ready，分支 paper/submission-ready；基准505cbf5（NEW-4a）。本轮按作者点名六项小修，保留数学含义、方程、参数、初值和原表值。

## 逐项修改

1. 引言相关工作段末句改为“平台上的平衡关系只约束接触率与未隔离比例的乘积，留下的一个自由度决定两种干预的组合”。
2. 摘要第二句按原话改为“容量约束下的多项最优控制研究表明，最优策略含有沿容量运行的阶段：……”，冒号后原文保留。
3. 模型式(2.1)后新段的首次δ_I、γ_I处加入括注“分别为该文非隔离感染者的诊断率与自然恢复率”。
4. 图7采用Times New Roman，数学STIX；独立放置色标，图区与色标间距为画幅宽度的0.03（5.22 mm），图幅仍为174×145 mm。实际运行plot_figure7.py --reuse-data，更新正式PDF/SVG及NEW_4b_figure7_before.png、NEW_4b_figure7_after.png。PDF实际嵌入TimesNewRomanPSMT和STIXGeneral，和图5、6、8一致；没有重新分类或计算背景。
5. vendor/README.md登记helper的固定上游提交473e8d7b、源路径、Git blob及SHA。固定源根LICENSE实际为Apache-2.0，全文逐字节保存为LICENSE.nature-skills（blob 261eeb9e，SHA256 c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4）。该提交README的MIT字样与LICENSE不符，按实际LICENSE登记；helper除既有行尾差异外内容相同。许可证已核清，故保留必需导入，不触发“许可证不明时”的可选导入分支。本轮未制作或发布公开快照；今后携带helper时同时携带来源说明和许可证。
6. 图7.py/.json输入仅把CRLF替换为LF后计算SHA，不去尾空白或重写JSON；二进制按原字节。原phase.json虽同时登记文本内容SHA，仍额外强制核验原始字节；原NPZ和本地缓存NPZ亦保持raw SHA校验。new_figure7.json重新登记source_hashes、frozen_source_hashes及新策略，identity_history追加NEW-4a来源全集和旧记录SHA；历史compute_script与background身份不改。迁移见new4b_identity_migration.json。

## 实际核验

- 51项受影响测试通过，0失败、错误或跳过。范围为test_new4a_identity、test_release_inputs、test_return_endpoint、test_numbers、test_sources；新增LF/CRLF两种复用测试，并验证冻结phase即使仅改变行尾也必须失败。换行属性测试读取仓库真实.gitattributes及真实相对路径。
- 在两个新目录分别将点名可变文本及图7元数据写为LF、CRLF，真实运行--reuse-data均exit 0，source_hashes匹配，NPZ字节相同。该验收在Windows完成，未声称Linux实测。结果见new4b_reproducibility.json。
- 图7cases、背景数组、本地NPZ和108个宏与NEW-4a完全相同；原冻结来源原字节未变。新权重分类、背景计算、回流ODE求解均为0。本轮未重跑完整261项测试或回流矩阵。
- 按build.ps1先补充后主稿完成构建：主35页、补19页；两份最终日志均无未定义引用/文献、重复标签、缺字、Overfull或重跑提示。已看主稿35页联系表及第1、2、3、4、23页高分辨率渲染，三处文字与图7显示正常；补充19页与NEW-4a逐页像素相同。图7对齐和碰撞检查均PASS，0失败/警告。PDF核验摘要见new4b_pdf_qa.json。
- 相对NEW-4a，数字字面量669→669，增减均0；标签缺失、悬空、重复均0；35条带标签陈述及23条对应证明变化均0。原有84个显示公式环境、35个结果环境、32个证明及13个表的数值序列通过既有保护检查，108宏未变。原main、无回流、回流分支及作者未提交资产均保留。

## 文字统计与作者事项

段落安排不变，只改指定的两句与一个括注。正文汉字15338→15394（+56），陈述2170→2170、证明2819→2819；沿用率接近100%符合局部小修范围，不据此扩改。删除清单、删除存疑、移出清单、因篇幅删除的机制句均为无；没有新增实质数学修改或待作者裁决项，NEW-4既有待审清单继续保留。本轮独立提交；不更新main，不英译，不打zh-final。
