# NEW-0 工作区与基准（2026-10-19）

- 工作区 `E:\work\draft\tmp\submission-ready`，分支 `paper/submission-ready`，位于当前可写根的忽略目录tmp中；没有覆盖既有目录。
- NEW_BASE_COMMIT `101b3e044418930e7242187f15044ee290c9f9f9`；RETURN_SOURCE_COMMIT `9887340091911eda76753c1d2cc2afa23430cc62`；原数字来源 `bb52b965a8cd98dd07a5c41b9997dae433128756`。
- 抓取后 main本地 `2b5545af423c9791aee9699296405b01b94ce244`、origin/main `b4835d9aae6fe0192093da7b6353a5455b42097a`；NR与return本地/远端均等于上列来源。旧方案分支 `36de3fa0b6cb3f9ab354ec9cf4e3adb1879e8710` 仅文档增补，不作为合并对象。
- 三个原工作区均无已跟踪修改。main有原NR英文文件名计划和上轮四份评估；NR有本轮计划；return无未跟踪项。逐文件SHA见NEW_0_assets.json，保持原样，不把这些资产混入新分支。
- 已读STATUS、NR_9_final、NR_return_handoff、本计划及两份旧方案。选NR最终已验收源；不回滚main，不复制回流规则、主tex或旧宏。
- 本计划原样复制到ai目录。AGENTS替换覆盖条款N1–N11，明确当前授权、九章、已接收回流状态、仓室术语、来源保护、集中审阅、英文冻结；保留其他数学证据规则。
- 提交检查：作者原计划第3–5行的Markdown双空格换行及末尾空行原样保留，git diff --check会报告这4处；其余本步文件单独检查无空白错误，不改作者源计划以消除提示。
- 数学陈述、数字、图件与tex在本步均未修改。段落蓝图、删改/移出、机制句删除均无。
- 基线构建实际完成：首次沙箱启动Biber报 {Illegal System DLL Relocation}，保留为环境失败记录；授权环境重试后主稿34页，补充18页。首轮补充因尚无主稿aux出现64条undefined，第二轮完整build.ps1使两份均undefined=0、multiply defined=0、Overfull>10pt=0。没有运行科学求解。
