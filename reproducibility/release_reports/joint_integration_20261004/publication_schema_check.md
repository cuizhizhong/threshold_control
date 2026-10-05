# 发布前审阅记录格式检查

首次正式发布命令在进入产物复制和正式编译之前返回非零：`独立人工审阅记录未绑定当前 PDF 或存在阻断问题`。

原因是独立审阅 JSON 将实测哈希保存在 `pdfs.main.sha256_independently_measured` 和 `pdfs.supplement.sha256_independently_measured`，而发布守卫读取顶层 `main_pdf_sha256`、`supplement_pdf_sha256`。已完成的人工审阅和实测哈希没有变化，也不存在阻断排版问题。

仅补齐审阅记录字段与逐页结论索引，保留原详细记录；不修改发布守卫、阈值、PDF、科学输出或受控稿源。首次拒绝发生在 `report_dir.mkdir`、`publish` 之前，未更新正式文件。本次拒绝是记录格式检查，不是科学计算失败，不计作新的科学复跑。
