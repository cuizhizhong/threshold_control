# NEW-4w W6：回流相关的文字与补充 S7 重写

基准：`8d7eb11`（W5 记录）。数值取自 `nr_audit/results/new4w/return14_summary.json`（W5），经 `make_numbers.py` 生成 `\nrRw…` 宏（40 个）。

## 修改

| 位置 | 改动 | 对应 |
|---|---|---|
| 第 2.1 节第三条简化 | 改为"隔离易感者在清零之前不释放，即在模型中不返回 $S$"；加两句：指标都计算到清零时间，不依赖清零后是否释放；涉及 $t\to\infty$ 的结论假设始终不释放。指引改到第 8.3、8.4 节与补充 S7 | X1 |
| 第 8.1 节 TDINN 段 | 输入病例一句分两种情形：此后仍不释放时有效再生数低于 1；清零后释放时，以隔离为主的控制 $S+S_q$ 仍远高于 $S_c$，与 TDINN 一样需防范输入病例 | X3 |
| 第 8.3 节 | 两段压成一段：理论结果针对清零前不释放的情形；14 d 回流下仍成立的结构与改变的量级；追踪隔离的保护是暂时的 | X2、X3 |
| 第 8.4 节局限 | 加两句：不释放的假设要求从强化干预到清零持续隔离，基准约一个月、西安超过一年（仅隔离控制约 373 d），西安结果为持续隔离假设下的外推；阈值一句改为"按名义的重症监护床位与重症比例选取，未经当地临床标定"。局限仍为两段 | X4 |
| 补充 S7 | 重写为两小节。"模型与设定"含式 `eq:return:model`、$1/\omega=14$ d、策略实施方式、终点式 `eq:return:cut`、恒等式 `eq:return:U` 与五种控制及数值方法一句；"数值结果"含新表 `tab:sup:return:term`（两组参数各四行）、仍成立的三条结论、改变的量级及其原因 | X2、X5 |

## 删去的陈述与标签（作者 2026-10-28 同意，N33）

- **陈述**：引理 `lem:return:U`（总易感者恒等式）、命题 `prop:return:final-size`（$t\to\infty$ 下界）、推论 `cor:return:right-discontinuity`（右不连续），以及有限时间退出的论证、截断后的剩余感染（尾界）一节。
  - 恒等式改为 S7.1 中的一行式子，沿用标签 `eq:return:U`；
  - 累计感染接近 $U(0)-S_c$ 一事，改由恒等式与"终止时 $U<S_c$"的数值事实说明。
- **标签**：`lem:return:U`、`prop:return:final-size`、`eq:return:lower`、`cor:return:right-discontinuity`、`eq:return:discontinuity`、`tab:sup:return:cinf`、`eq:return:tail`。这 7 个都在授权清单内，`check_tex` 的缺失项正是这 7 个，悬空引用 0。
- 这是对 N3 中已接收回流理论结果的撤回；来源分支的结果文件只读保留。

## 删去的数字的去向

旧 S7 与第 8.3 节的回流数字（7、14、30 d 三档、$\theta=0.002$ 的西安值、尾界、积分容差对照、无回流 $t\to\infty$ 对照表）不再入稿。它们仍保存在：

- `results/return_import.json`、`new_return_endpoint.json`、`noreturn_inf_crosscheck.json`；
- 旧的 `\nrRet…` 宏照常生成，只是不再被引用。

`check_tex`：数字缺 29、增 42。

## 文献

`Ketcheson2021Finite` 只在删去的命题讨论中被引用，现不再引用，条目留在 bib 中。`Ashcroft2021`、`Wells2021` 保留，作为 14 d 停留时间的依据。

## 检查

- 编译：主稿 39 页、补充 18 页（原 21 页），undefined 0，Overfull 0。
- `statement_diff`：S7 的 3 条陈述只在旧稿中（即上述删去的陈述），其余文件陈述 0 变化。
- 测试：全量 409 项通过；`test_new4w.py` 新增 2 项（`\nrRw` 宏与 W5 汇总一致；S7、8.3 节所写结论与 Q1–Q4 一致、旧标签与旧宏不再出现），共 411 项。
- 页面：补充第 15–17 页（S7 与表 S3）、正文第 29 页（8.3、8.4 节）已查看。
