# NEW-1 来源导入与发布适配（2026-10-19）

## 改动与来源身份

- 先逐路径比较，再从9887340091911eda76753c1d2cc2afa23430cc62选择性导入r7_return和R7_2/R7_3两份历史记录。未导入回流主tex、正文章、附录C、AGENTS或r7_numbers.tex；原r7算法与JSON只读。
- 核心JSON实测blob=582def57c4a957e242d884dff50d6c8937e9137a、SHA-256=3ca0a3d245314230df83c0717e07ed73ab67129803c284ea46eab8921cdfb05f，bb52b96与归档版原始字节一致。LF、无末尾换行。
- xian_loader已证实只存在CRLF/LF差别，按101b3e0原blob字节恢复，SHA-256=c029a604c8f7147a24d59e6c0d39a927ff360f0dbb1b7338f23bd86573ff15a2。两个精确路径用-text保护，未全仓库renormalize。
- source_manifest中pinned来源只有xian_loader的身份改动，其余不变；未修改参数、初值或回归参照。身份收据见nr_audit/results/new_source_identity.json。
- import_return_numbers默认读固定本地JSON；强制校验SHA/blob、模型、终点、权重和18行。Git历史可用时额外对照历史原字节；无历史只跳过这一项。缺输入或字节变化失败，不补默认值。

## 实际验证

1. thesis环境Python3.10.20，numpy2.2.5、scipy1.15.3、sympy1.14.0、mpmath1.3.0、pandas2.3.3、openpyxl3.1.5、pytest9.1.1、matplotlib3.10.9。已逐包读取，精简安装清单和精确版本分别保存。
2. 实际执行pytest nr_audit/tests：255 passed、0 failed、0 skipped，190.53s。152条提示是record_property与JUnit xunit2的报告兼容提示，不是数值失败；未放宽任何阈值。摘要与源码SHA在new1_test_summary.json。
3. 七项新增发布输入测试覆盖无历史导入、缺文件、CRLF变化、末尾换行、损坏字节、冻结loader及core.autocrlf=true/false实际检出。属于Windows配置模拟。
4. 在无.git临时快照中，并以GIT_CEILING_DIRECTORIES阻断向父仓库发现Git，实际执行导入与make_numbers。18行旧值完全相同，101个宏与工作树逐字节相同；收据new_no_git_snapshot.json。没有运行r7_return/make_numbers。
5. WSL探测退出1并提示未安装，未做Linux实测，未声称跨系统运行通过。
6. 正式图表映射覆盖20幅图、13张表。18幅PDF与历史生成报告SHA匹配；capacity/phase在R7-a改图，不能沿用旧身份。历史报告不等于本轮视觉验收或全曲线重算；旧绘图层需要从标签恢复隔离路径，清单明确列出。

## 稿件与后续

本步未改tex、方程、数学陈述、参数、初值、图件或原表值；101个宏未改变显示值。段落蓝图、删除/移出、机制句删除均无。README区分历史来源、当前核验、完整回归、长时复算与PDF验收。NEW-2继续处理派生终点尾界与图7；已有36条回流复现仅作为旧报告，不冒称本轮复算。
