# SIQR 模型下接触减少与追踪隔离的阈值控制

研究含接触追踪与隔离的 SIQR 型模型：在社区非隔离感染人数上限 $I\le\eta$ 下，比较接触减少与追踪隔离的分配。内容包括仅隔离阈值控制的解析解、联合阈值控制的状态参数化与可行条件、控制时长—累计感染—隔离人数的排序关系、二次成本下的最优分配，以及西安疫情参数下的数值应用。目标期刊为 Bulletin of Mathematical Biology 类英文生物数学期刊；目前在修改中文稿，之后译成英文。

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

数值结果和图件已经计算完成，保存在 `reproducibility/results/` 与 `paper/figures/` 中。计算脚本暂按原样保留，其中的路径仍指向清理前的目录结构，不能直接运行；投稿前将整理为“每张图、每张表对应一个脚本”的形式并重新运行验证。

## 历史

2026-10-06 之前的完整状态（含稿件控制与审计管线、讨论记录、旧稿及各轮修订目录）保存在标签 `pipeline-final-20261006`：

```powershell
git show pipeline-final-20261006:<路径>                          # 查看某个旧文件
git restore --source pipeline-final-20261006 -- <路径>           # 取回某个旧文件
```
