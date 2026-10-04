# AI 材料整理与冻结来源迁移核查

## 处理结果

2026-10-04 将 `ai/threshold_control_reproducible_release_20261002/` 原样迁至 `joint_control/threshold_control_reproducible_release_20261002/`。完整保留 87 个文件：联合控制核心、输入、结果、冻结论文、图件、出处和历史验收记录。冻结包内部文件不改，正式主稿仍位于 `latex/`。

活动复现入口的 9 份 Python 文件只改来源路径；当前配置/来源索引、项目说明和 Git 字节属性同步新目录。历史报告、原始输入、已汇集结果不改写，旧路径通过 [relocation_manifest.json](relocation_manifest.json) 逐文件对应新路径。迁移前入口及文档备份在 `reproducibility/backups/before_source_relocation_20261004/`。

本次没有提交或推送 Git。工作区中旧路径显示的 87 项删除与新 `joint_control/` 中的 87 项文件是一一对应的移动，不是删除复现材料；以后提交时应将新旧路径同时纳入，不能只提交旧路径删除。

## 计划清理判定

本轮未找到整份已经执行完、且没有独有待办或来源信息的独立计划，因此本轮实际删除 0 个文件。成功执行迁移验证时，原 `ai/` 中除冻结包以外的 16 个文件均保留原字节：

- `CODEX_后续阈值数据与数值计划.md`：初值/积分统一及无额外能力限制联合基准的部分工作已完成；新阈值情景、受限能力数值和资源校准仍未全部完成。旧文档末尾“尚未执行”是当时状态，不据此否认已有验收，也不把整份计划视为已完成。
- `总览.md`、`数值工作汇总_20261004.zip`：外部探索性计算，尚未纳入正式复现链，不宣称计划已执行。
- `boundary_review_20261003/` 及同名 ZIP：既含第9节文案建议，也含本地未采用的渐近展开、云端计算和补丁，不能整删。已完成的局部订正文案与尚未处理的图13标记绑定、允许区间核查有不同范围，依据 `../sec9_boundary_wording_20261004/verification.json` 的记录区分。
- `阈值定义_讨论总结与修改说明.md`：已完成工作的讨论总结，仍有独有来源说明、未采用论证和后续事项；不是一份可以整体删除的纯旧执行计划。
- `阈值定义重点摘录.pdf`：来源摘录，保留，不按已执行计划删除。
- 冻结来源包中的 `plans/后续研究计划_最新版.md` 有尚未完成的任务，随完整包原样迁移，不删改。

本轮保留旧讨论文档，不把文档中的旧版本说法当作正式稿的最新结论。后续按具体计划执行完后，再核查是否存在独有信息，使用回收站清理确认可删除的文件。

成功验证后的最后盘点发现讨论区有本轮操作之外的变化：`ai/boundary_review_20261003.zip` 不再存在，新增 `ai/后续研究计划_最新版.md`。本轮没有删除该 ZIP，也没有创建该计划；不擅自恢复、覆盖或删除这些现场变化。另由本轮新增 `ai/README.md` 说明目录用途。最终现场状态见 [final_inventory.json](final_inventory.json)，迁移和保护文件的结论与讨论区外部变动分别记录。

提交前追加核查：阈值讨论总结与冻结包 `review/此前阈值定义修改说明.md` 完全逐字节相同，均为 6461 字节、SHA-256 为 `9abfd2eeedd83f3e48414cb09a9e6300bf5a1e7789fa30d6624b8f9c2bce927b`，且活动入口不引用 `ai/` 副本。因此可清理的是重复副本，而不是宣称全部后续任务已完成；本次仅确认可删除，未执行删除。前述最初保留判定是当时的保守处理。

提交前现场还检测到 `ai/总览.md` 缺失和数值汇总 ZIP 的解包目录出现，属于本轮操作之外的变化，不恢复、不覆盖，也不纳入本次 Git 提交。以 `final_inventory.json` 的提交前盘点为准。

## 实际执行的核查

完整结果见 [verification.json](verification.json)、迁移前清单见 [before.json](before.json)。

- 冻结清单的 86 条内容记录及清单本身共 87 文件：迁移前后 SHA-256 和文件集合一致。
- 原包只读 `scripts/verify_release.py`：40 个锁定文件校验通过，见 [frozen_locked_check.json](frozen_locked_check.json)。
- 正式论文工程、图件、原始数据、已有结果和历史验收资料共 972 个保护文件：哈希不变。
- 9 份活动 Python：替换新旧路径后 AST 一致；2 份 JSON 索引除路径外语义不变。
- 两个独立空输出目录：实际执行源码收集、完整性核查、来源清单生成；每轮覆盖 20 图、4 正文表、3 补充表。理论来源读取检查只比较冻结来源自身，不冒充当前新增证明的独立审查。
- 联合核心及参数：实际从新路径加载；不调用求根、积分、拟合或扫描。
- 隔离文案回归：调用 `paper_sync.prepare_manuscript`，沿用 `results/20261003_release_final/` 的已有验收输出，生成稿只放于忽略的检查目录，没有覆盖正式稿。
- 新冻结目录的全部文件未被项目 Git 忽略规则屏蔽，`text` 属性全部为 `unset`。

成功命令：

```powershell
reproducibility/.venv/Scripts/python.exe -B reproducibility/release_reports/source_relocation_20261004/verify.py verify
```

核查运行目录为 `reproducibility/dev_source_relocation_20261004/`，保留实际生成的检查证据，不是正式计算结果。两次前置环境问题和失败退出记录见 [failed_attempts.md](failed_attempts.md)，没有改写失败为通过。

文本差异检查保留索引原有 CRLF：普通 `git diff --check` 将 `registry.json` 的 5 行 CR 识别为尾部空白；采用 `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check -- .gitattributes .gitignore AGENTS.md README.md reproducibility` 后退出码为 0。未为消除此提示整体转换历史索引的换行。

本轮未重新执行科学计算、未重编译或重新审阅 PDF。主稿、补充材料、PDF 和所有图件均原样保留；本轮通过范围仅为目录整理、来源完整性和入口/文案回归，不称为新的全文科学复现。
