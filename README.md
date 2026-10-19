# SIQR 模型下接触减少与追踪隔离的阈值控制

研究含接触追踪与隔离的 SIQR 型模型，在给定阈值策略下比较接触控制与追踪隔离的组合。无回流模型提供解析解、能力可行性、感染与未感染者隔离的计数取舍及二次干预强度成本优化；补充材料分析正回流对长期解释的影响。西安部分是固定参数情景。当前分支整理中文审阅版，英译和main更新另行执行。

## 目录

| 目录 | 内容 |
|---|---|
| `paper/` | 正式稿（中文）、参考文献、模板、图、编译脚本，以及 `revision_notes/` 中的修改记录 |
| `reproducibility/` | 计算代码与数值结果（见该目录 README） |
| `code/`、`scenario1_*`、`c0_sensitivity/`、`xian_control_comparison/`、`xian_dom/`、`joint_control/` | 各计算模块与冻结的 20261002 交付包 |
| `真实数据/` | 西安原始数据 |
| `refs/` | 参考文献 |

规则与写作规范见 `AGENTS.md`（Codex 读取；`CLAUDE.md` 指向同一文件，供 Claude Code 读取）。

## 编译

Windows PowerShell（先编译补充材料，再编译主稿）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper\build.ps1
```

Linux/macOS：`bash paper/build.sh`。需要 xelatex 与 biber。

## 计算代码的现状

`nr_audit/` 是当前无回流核验与发布适配入口，依赖安装、轻量检查、完整回归和固定回流输入的导入方式见该目录README。`r7_return/` 是按固定提交引入的只读回流计算来源，含结果与容差记录；本稿不运行它的旧宏生成器。

`reproducibility/` 和其他旧模块只读；部分旧绘图层仍指向历史结构，不能直接运行。图表数据与入口映射见 `nr_audit/results/figure_table_sources.csv`，其中区分已核标量、历史报告与本轮实际重绘，不承诺全部图件在本轮重算。

新工作树初次构建时，主稿与补充相互引用可能需要运行两轮完整构建。PDF和中间产物不入Git。数据许可、公开链接和最终投稿信息由作者确认，本分支不自动发布。

## 历史

2026-10-06 之前的完整状态（含稿件控制与审计管线、讨论记录、旧稿及各轮修订目录）保存在标签 `pipeline-final-20261006`：

```powershell
git show pipeline-final-20261006:<路径>                          # 查看某个旧文件
git restore --source pipeline-final-20261006 -- <路径>           # 取回某个旧文件
```
