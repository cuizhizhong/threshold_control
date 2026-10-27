# NEW-4s 图 3 标题与图 4 风格

作者 2026-10-27 指示（根 `AGENTS.md` N29），基准 `0940c1d`（NEW-4r 后续）。

## 修改

- **图 3**：两面板标题只写 (a)、(b)，横轴标签只写 $I_{t_{\rm cum}}$。数据与图注不变。
- **图 4（`fig:joint:compare`）**：按图 2 风格重绘，新入口为 `nr_audit/plot_new4s_figures.py`。
  - **数据**：只读 `joint_extra/` 的 `trajectories_baseline.csv`、`compare_baseline.csv`、`input_manifest.json`，原字节 SHA 已登记；与原图数据相同。
  - **风格**：Computer Modern 字体，四边坐标框，刻度朝内，带框图例。
  - **面板标题**：只写 (a)–(d)。
  - **线型**：三种控制都用实线，颜色与图 9 一致（仅减少接触绿、仅隔离控制蓝、成本最优控制紫），只有显式族 $\alpha=0.5$ 用品红虚线（作者追加）。仅隔离控制与成本最优控制在前段重合，上层的紫线较细，蓝线仍可见。
  - **曲线名称**：改用现行术语，原为 Quarantine only、Minimum-cost allocation 等。
  - **参照线**：$q_0$、$1$、$S_c/N$ 改为红色虚线。
  - **图例**：从图底移到 (b) 右上角的空白处。
  - **图件**：新图 `figures/new4s/joint_compare_baseline.pdf`，0.85 倍版心宽；旧图件保留。
- **图 4 图注**：补“红色虚线依次为 $q_0$、$1$ 与 $S_c/N$”。

## 核对与验证

- **数据核对**：四条轨迹都画到各自的清零时间；$\max(I+I_q)/\eta$ 与 `compare_baseline.csv`、正文表 1 一致（1.02、1.64、1.92、1.89）。
- **测试**：新增测试 3 项，核对输入、输出、宽度、清零时间与峰值；`figure_table_sources.py` 映射已更新。
- **检查**（相对 `0940c1d`）：`check_tex` 标签缺失 0、数字不变；`statement_diff` 陈述 0 变化。
- **构建**：主 36 页、补充 20 页，undefined 0；渲染检查了主稿第 11、19 页。
- **全量测试**：384 项通过（新增 3）。
