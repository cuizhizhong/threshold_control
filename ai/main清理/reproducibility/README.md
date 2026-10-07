# reproducibility：计算代码与数值结果

2026-10-06 起，本目录只保留计算代码和数值结果。稿件控制管线（受控稿源、正文文字同步、发布、审计脚本与测试、运行记录和验收报告）已经删除，完整版本见标签 `pipeline-final-20261006`。

## 保留的内容

| 文件或目录 | 作用 |
|---|---|
| `xian.py` | 西安日报数据的初值拟合、TDINN/仅隔离/常规三策略参照与阈值响应；原管线中西安计算的权威实现 |
| `population.py` | 固定绝对初值下的有效人口边界与代表轨迹 |
| `c0.py` | 常规接触率 $c_0$ 的响应、驻点曲线与 $\beta$ 拐点存在域 |
| `joint.py`、`joint_extra/` | 联合阈值控制：`joint.py` 复现联合基准并做开环核对；`joint_extra/` 计算四种分配比较、能力限制、成本权重与乘子解（含自带测试） |
| `figures.py`、`finalize_matlab_figures.py`、`plotting_checks.py`、`matlab_*.m` | 图件生成与绘图辅助 |
| `bootstrap.py`、`checks.py` | 公共函数与科学检查 |
| `results/` | 已完成的数值结果：`20261003_release_final/`（仅隔离基准、西安、人口、c0 等）与两轮联合控制结果 `joint_integration_20261004/`、`20261005_sec7_v2_refinement/` |
| `registry.json`、`registry.md` | 原管线记录的图表与数据来源对应关系（按当时图号），代码整理时参考 |
| `manuscript_audit_notes.md` | 求解器、容差、未取整初值等数值设置 |
| `configuration.md`、`configuration_index.json`、`environment.json`、`requirements.txt` | 运行环境与参数配置记录 |
| `assets/` | 模型示意图等素材 |

## 现状

这些脚本中的路径仍指向清理前的结构（如 `latex/`、`latex/revision_*`、`archive_unused/`），原来的一键入口 `run_all` 已删除，因此不能直接运行。投稿前的代码整理阶段会：把需要的文件从标签取回或迁移到新位置，修复路径，建立“每张图、每张表一个脚本”的入口，并重新运行核对论文中的数字和图。
