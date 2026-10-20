# NEW-4h 跨平台文本身份与编辑收尾

作者2026-10-21授权实际修改。分支 `paper/submission-ready`，基准 `f1f334db30e564b06629d40b198f020c031690f7`；规则见根 `AGENTS.md` N18，范围见 `ai/NEW_4h_portability_followup_plan_20261021.md`。本轮沿用 nature-polishing 和 PDF 检查流程，仅本地提交。

## 实际修改

- 正文3.4的接触率机制并入阈值取舍段；6.2删除独立的重复机制段，只在阈值分析末尾保留补充材料指引。S2.2.1删去重复机制，完整解释保留在S2.1证明之后。未删除新的数学内容或流行病学机制。
- S2.1命题后直接接证明，取消紧邻的“证明见下一节”及独立标题；用 `\phantomsection` 保留 `sec:proof:contact-effects` 的跳转目标。此标签当前无正文引用，不再表示独立编号小节；今后需要引用证明时用有说明文字的 `\hyperref`。S2.2.1等后续编号不变，低阈值极限保持原位置。
- 附录敏感性表的两处依据明确写为“补充命题”，避免S2.2命题号与小节号混淆。S5图注“西安两处纠错点”改为“西安两处补充计算点”。
- 新增 `nr_audit/text_identity.py`：只对点名文本作字节级CRLF→LF后取SHA；空格、BOM、孤立CR和数值变化仍会报错。数字宏须同时匹配基准Git文本、现稿文本和独立基线内容SHA；历史manifest及8项现稿定位、11项片段采用相同内容规则。
- 迁移收据与 `NEW_4g_baseline.json` 只新增内容身份字段，全部既有字段原值保留，包括旧raw SHA和16项历史测试记录。现稿文本的后续授权编辑可用 `python nr_audit/text_identity.py --refresh-current` 刷新新增内容字段；此命令不更新历史raw身份、冻结来源或宏基线。
- `sources.py` 的raw SHA逻辑不改；PDF、NPZ、冻结科学JSON及全部受保护来源继续按原始字节核验。没有改动科学数据、图文件、算法容差或历史结果。

## 实际验证

- 两稿联合 `check_tex` 相对本轮基准：标签缺失、悬空、重复、缺bib均0；数字687→687，缺0、增0。三条既有未引用bib保持。
- `statement_diff`：41条陈述全部相同，配对证明0变化；相对本轮基准170个独立陈列公式块逐块相同。独立迁移审计相对NEW-4g前基准 `83ddcdb` 复核34段proof逐块相同，图件使用21次及原图字节不变，数字宏身份通过。
- 13张表中12张按原去空白判据完全相同；敏感性表仅新增两处“补充命题”引用前缀。审计保留1旧/1新表块的实际差异，只对这两个指定标签的前缀作登记等价处理；符号、数值、标签和其他文字的变化仍被拒绝，另有5项正反测试覆盖。
- 迁移收据与宏基线相对本轮基准的全部既有字段逐叶未变；76个受保护文件原字节SHA全部一致。历史manifest原raw为 `bd5ed07bf8ae18b433be8e7d01055bd03bd0936d85c3ace137bccdfcb54e2ad0`，新增内容SHA为 `ad8ee09b88cd1219db66641a97bfdbb66ccaeab77a458c4edcddedb5ee50135d`；数字宏原raw为 `49e5b256aafe1eb8cd776efae8a400bacf8d740a8ef4a21f075aad11b85cc719`，内容SHA为 `3f926bb7caa3f961b3c53a013ab0c0fe18a5693c93863e7580e0fa0605a2b827`。
- 实际全量命令：

  ```powershell
  E:/anaconda/envs/thesis/python.exe -m pytest nr_audit/tests -q -p no:cacheprovider --basetemp=paper/tmp/NEW_4h/pytest_full --junitxml=paper/revision_notes/NEW_4h_pytest_full.xml
  ```

  **353 passed，0 failed，0 error，0 skipped，191.78 s**；原289项加本轮64项。152条warning均为既有 `record_property` 与默认JUnit `xunit2` 格式的兼容提示，没有数值断言失败。不使用会覆盖历史报告的 `run_tests.py`。新增测试先用默认临时目录时遇Windows沙箱目录权限错误，改用独立工作区 `--basetemp` 后通过，未改判据或阈值。
- 本次实际环境是Windows；LF/CRLF组合、内容损坏、空格/BOM/孤立CR、宏两边同时损坏和冻结输入原始字节等在临时检出夹具中验证。没有本机Linux运行，不将Claude报告的Linux结果记为本轮结果。
- 全量测试包含既有闭式、逐状态根法、无回流ODE、抽样乘子及固定初值下的误差重建回归；没有开展新的研究性优化、重新拟合、参数扫描或历史回流长矩阵计算。
- 仓库标准构建 `paper/build.ps1` 完整执行两轮；沿用正常环境运行，以避开已知沙箱Biber DLL问题。主稿37页、补充23页；两轮aux的164/69行标签逐行相同。两份最终日志undefined、multiply defined、Overfull hbox、缺字均0。
- 两份共60页均已渲染；52页与已目视的NEW-4g版逐像素相同，其余主稿10、19、20、35页与补充2、3、4、13页重新目视检查，公式、图表、引用和页脚正常，主35及补2、3页另作高分辨率检查。页数不作为跨平台一致性的判据。

逐项证据见 `NEW_4h_check.md`、`NEW_4h_statements.md`、`NEW_4h_metrics.md`、`NEW_4h_migration_audit.json`、`NEW_4h_validation.json` 与 `NEW_4h_pytest_full.xml`。历史NEW-4g报告保持原样；本轮没有新增作者待决事项，不宣称作者验收或中文定稿。
