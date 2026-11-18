# NEW-4bd 附录 A、B 按外部意见补证明与改准（N58）

- 基准 `430d487`（NEW-4bc）。范围：`paper/appendices/A_proofs_sensitivity.tex`、`paper/appendices/B_control_cost.tex`。
- 来源：作者 2026-11-19 把 ChatGPT 按作者修改习惯对附录 A、B 的审阅（逐节意见、59 条逐句、4 处证明缺口、2 个可选的简化证明）贴入对话。Claude 对照源文件、正文陈述（命题 `prop:threshold-tradeoff`(ii) 要求导数严格为负；定理 `thm:joint:representation`(iii) 已写“取处处满足……的代表后”）与补充材料核对：48 条照用、5 条改后采用、5 条不采用（另 3 条随简化证明消失），4 处缺口成立；两个简化证明经验算成立。作者回复“按你的建议来”。

## 1 四处证明缺口

| 位置 | 补正 |
|---|---|
| A.5(ii) | 对式 `eq:cost:state` 用 Leibniz 公式写出 $\partial J_q/\partial\eta$、$\partial J/\partial\eta$，两项均严格为负，直接落到命题的导数陈述 |
| A.6 | 速度界在时间变量中前置，由此得到 $S$ 与反函数均为 Lipschitz、$c_c$ 可测；$q<1$ 写成几乎处处；(iii) 开头写明取处处满足界限的代表；“可测性在 (ii) 之后证明”“最后补全 (i)”两句改为“再证 (i) 的反方向” |
| A.8(ii) | 严格成本差的区间取 $(S_c,\min\{S_c+\delta,S^*\})$ |
| A.9 第二步 | $r=r_{\rm cont}$ 时补 $\zeta_s'\ge0$ 且至多在 $p=2$ 为零，积分得严格递增 |

## 2 两个简化证明（作者决定采用）

- A.9 第一步端点极限：删去 $\kappa$、$h$ 的估计，改为在 $(1,1)$ 与 $(\zeta_{\rm sw},\zeta_{\rm sw})$ 用隐函数定理（$E_\zeta(1,1)=-2(1-b)$，$E_\zeta(\zeta_{\rm sw},\zeta_{\rm sw})=-2(\zeta_{\rm sw}-b)/\zeta_{\rm sw}^2$），再由 $(p,\infty)$ 内零点唯一得局部解即 $\zeta_s$。
- 引理 `lem:proof:fold-free` 的 $0<\sigma<\sigma_c$ 部分：删去按 $X(p)$ 与实根分情形的论证，改为 $\partial(F/\sigma^2)/\partial\sigma=2p(bw\sigma-p^2)/\sigma^3<0$，依据 $p^4-16(2p-3)=(p-2)^2(p^2+4p+12)\ge0$。`test_new4bd.py` 用 sympy 核对这三个恒等式。

## 3 其余改动（按外部意见编号）

- 照用：1–4、6–9、11、14–29、31–33、36、38–41、43–48、50、52–54、59。主要是写明比较对象与量词、补一两步推导（A.1 延拓、A.2 由几乎处处负导数到严格递减、A.3 正极限与积分方向、A.7 可测选择与 (ii) 改为成本密度之差、A.8 一致收敛与子列不等式、A.10 两个最优性不等式与斜率为强度平方积分）、拆段、统一证明标题（删“本小节证明……”）、补 $E(\zeta_{\rm sw},\zeta_{\rm sw})=0$、“单峰性”改“最小点及其连续性”、表 `tab:sensitivity` 依据栏精确到分项并删 $\theta$ 一句。
- 改后采用：10（$\partial F/\partial\beta$ 两项分别判号）、13（方括号严格为负）、51（表注采用措辞，不加“$q_0=0$ 时取右导数”：全稿没有这一约定）、56（补式 `eq:s1:barS` 出处）、58（保留“下降速度恒为”，补 $dt$）。
- 不采用：30、42、49（标题与表题的可选改名）；55、57（附录 B 是计算，没有对应命题，不套证明环境）。
- 随简化证明消失：34、35、37。

## 4 陈述与数字

- statement_diff（附录 A 对 `430d487`）：陈述 0 变化，证明有变化 2 条（命题 `prop:model:positive`、引理 `lem:proof:fold-free`），工具只比对同一文件内紧随陈述的证明；其余小节的证明改动见上。证明逻辑除第 2 节两处局部换证外不变。报告 `NEW_4bd_statements.md`。
- check_tex：标签缺失 0，悬空引用 0；数字缺 0，增 2（12、16，来自因式分解 $p^4-16(2p-3)=(p-2)^2(p^2+4p+12)$）。报告 `NEW_4bd_check.md`。

## 5 核验

- 两份 PDF 编译：undefined 0，multiply defined 0，Overfull 0；正文 33 页、补充 13 页，页数不变。全量测试 466 项通过（NEW-4bc 时 464 项加新增 2 项）。
- 新增 `nr_audit/tests/test_new4bd.py`（措辞断言与 sympy 恒等式）。

## 6 删除清单与待作者决定

- 删去：“本小节证明……”八处、A.1 末句对 (i)(ii) 的复述、A.9 的 $\kappa,h$ 估计与根位置讨论（换证）、表注 $\theta$ 一句（A.4 已有）。因篇幅删去的机制句：无。
- 待作者决定：无。
