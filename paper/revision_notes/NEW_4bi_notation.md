# NEW-4bi 记号：$r_{\rm cont}\to r_*$，TDINN 控制函数记为 $c_{\rm D},q_{\rm D}$（N63）

- 基准 `92be471`（NEW-4bh）。作者 2026-11-19 认为 $c_{\rm TDINN}$ 等下标不够专业，把 ChatGPT 的建议贴入对话；Claude 核对用法后，作者选“D 与 $r_*$ 都改”。$S_{\rm sw}$、$\zeta_{\rm sw}$ 保留（$S_*$ 易与 $S^*$ 混，$\zeta_s$ 与附录驻点曲线 $\zeta_s(p)$ 重名）。

## 改动

| 记号 | 位置 | 改动 |
|---|---|---|
| $c_{\rm TDINN},q_{\rm TDINN}$ → $c_{\rm D},q_{\rm D}$ | 第 7.1 节式 (7.1)，仅此两处 | 引导句补“（这里记为 $c_{\rm D}(t),q_{\rm D}(t)$）”；文字中仍称“TDINN 控制”；图件只写方法名，不改 |
| $r_{\rm cont}$ → $r_*$ | 第 5、6、7、8 章，附录 A，补充权重结构与数值方法两节，共 38 处 | 机械替换；“权重界限”的名称与定义式不变。存档文件 `S3_inflection.tex`、`S4_explicit_control.tex` 不动 |
| 补充图 S5 图例 | `fig:sup:phase-detail` | 新入口 `nr_audit/plot_new4bi_notation.py` 调用原绘图函数 `preview_style_heatmaps.preview_s6`（只读已校验的缓存，不分类、不求解），先确认未改字的重画与现入稿 `paper/figures/new4t/S6.pdf` 逐字节相同，再把图例 $r_{\rm cont}$ 改为 $r_*$，另存 `paper/figures/new4bi/S6.pdf`；收据 `nr_audit/results/new4bi_notation.json`。原图件与历史收据只读保留 |

## 核验与清单

- 陈述变化 4 条，均只换记号：定理 `thm:joint:cost-structure`、引理 `lem:proof:fold-free`、命题 `prop:sup:rhat`、`prop:sup:jump`；证明变化 2 条同理。报告 `NEW_4bi_statements.md`、`NEW_4bi_check.md`：标签缺失 0，悬空引用 0，数字缺 0、增 0。
- 两份 PDF：undefined 0，Overfull 0；正文 33 页、补充 12 页不变。
- 新增 `nr_audit/tests/test_new4bi.py`；`test_new4ax.py`、`test_new4ba.py` 中含 $r_{\rm cont}$ 的断言、`test_new4t_figures.py` 中 S6 的入稿路径断言增加被 NEW-4bi 取代的分支；`text_identity.py --refresh-current` 刷新当前内容 SHA。全量测试 473 项：首轮仅 `test_new4t_figures[S6]`（入稿路径）失败（`NEW_4bi_pytest_full.xml`），补分支后该文件与相关测试通过。
- 参数、初值、数字、宏、标签与其余图件不变；不新增计算。待作者决定：无。
