# 定理 5.2 证明的极限写法（作者 2026-10-28 对话指示）

基准：`d70f31a`。范围：附录 A.10“连续结构”中定理~5.2（`thm:joint:cost-structure`）的证明，以及该定理陈述 (i) 中同一极限的写法。作者指出期刊论文证明极限时不用 $x\downarrow a$、$x\uparrow a$ 或“$x\to a$ 时 $f\to L$”这类箭头写法，要求按数学期刊的规范改写。

## 改法

极限一律写成 $\lim_{x\to a^{+}}f(x)=L$ 或 $\lim_{x\to a^{-}}f(x)=L$（单侧极限用上标 $\pm$），需要单独看的极限写成显示式；“令参数趋于某值取极限”用文字“令 $r$ 从左侧趋于 $r_{\rm cont}$”。$\lim$ 下标中的箭头是通行写法，保留。

| 位置 | 原写法 | 新写法 | 类别 |
|---|---|---|---|
| 定理 5.2(i) | $S\downarrow S_c$ 时 $c_c^*(S)\to c_0$ | 在 $S_c$ 处的右极限为 $c_0$ | 措辞（含义不变）；用文字是因为行内 $\lim$ 在该行断开或溢出 |
| 证明第一步，$E(p,\cdot)$ 的范围 | 由 $r\varphi(p)$ 降至 $r\varphi(p)-1<0$ | 显示式 $E(p,p)=r\varphi(p)$，$\lim_{\zeta\to\infty}E(p,\zeta)=r\varphi(p)-1<0$；前面补“对所有 $p>1$ 有 $r\varphi(p)<1$”（由已证的 $r_{\rm cont}<27/(9-8b)$ 直接得到） | 写法；补依据 |
| 证明第一步，曲线两端 | $p\to1$ 或 $p\to\zeta_{\rm sw}$ 时 $E(p,p)\to0$，$E_\zeta$ 在有界集上有负上界，故 $\zeta_s(p)-p\to0$，即 $\zeta_s(1+)=1$、$\zeta_s(\zeta_{\rm sw}-)=\zeta_{\rm sw}$ | 记 $\kappa=2(1-b)^2/(\zeta_{\rm sw}+1)^3$，由式 (A.9) 在 $p\le\zeta\le p+1$ 上 $E_\zeta<-\kappa$；$r\varphi(p)<\kappa$ 时得 $0<\zeta_s(p)-p<r\varphi(p)/\kappa$；由 $\varphi(1)=\varphi(\zeta_{\rm sw})=0$ 得两个单侧极限（显示式） | 证明补步：原句“$E_\zeta$ 有负上界”的论证写成显式估计，思路不变，并补上原句隐含的有界性（只在 $[p,p+1]$ 上用下界） |
| 证明第二步 | 令 $r\uparrow r_{\rm cont}$ 取极限，$r=r_{\rm cont}$ 时曲线上 $E_p\ge0$，零点只可能在 $p=2$ | 先设 $r<r_{\rm cont}$，再设 $r=r_{\rm cont}$：由引理 A.1 零点只可能在 $p=2$；$E$ 关于 $r$ 连续且 $E_\zeta<0$，故 $\zeta_s(p)$ 随 $r$ 连续，在 $r<r_{\rm cont}$ 的不等式中令 $r$ 从左侧趋于 $r_{\rm cont}$ 得 $E_p\ge0$ | 写法；补出取极限的依据；“$p$ 接近 1 时 $E_p>0$”改为已证的“$p\le3/2$ 时 $E_p>0$” |
| 证明第三步 | $\zeta\uparrow\zeta_{\rm sw}$ 时 $p^*\to\zeta_{\rm sw}$，$\zeta\downarrow1$ 时 $p^*\to1$ | 由第二步，$p^*$ 是 $(1,\zeta_{\rm sw})$ 到自身的严格增连续双射，故有两个单侧极限（显示式）；回到原变量后写出 $\lim_{S\to S_c^{+}}c_c^*=\lim_{S\to S_{\rm sw}^{-}}c_c^*=c_0$，由此得 $c_c^*$ 连续 | 写法；补出 (i) 中连续性与右极限的推导 |

## 核对

- 陈述：`statement_diff` 报告陈述变化 1 条（定理 5.2(i)，仅措辞，数学含义不变），见 `NEW_thm52_limit_statements.md`。该工具只把紧随陈述的证明计入对照，附录 A.10 的证明未被识别，证明差异以 `git diff` 为准（上表）。证明的逻辑步骤不变，第一步的估计是原论证的显式化。
- 新估计的数值核对：对 $b\in\{0.05,0.3,0.5,0.8,0.95,(1-\beta)(1-q_0)\}$、$r\in\{0.3,1,2,r_{\rm cont}\}$，在 $(1,\zeta_{\rm sw})$ 上 4000 个点检查 $E_\zeta<-\kappa$（$p\le\zeta\le p+1$）、$r\varphi<1$ 以及 $0<\zeta_s(p)-p<r\varphi(p)/\kappa$，全部成立（一次性脚本，未入库）。
- `check_tex`（对 HEAD）：标签缺失 0，悬空引用 0，数字缺 0、增 0，见 `NEW_thm52_limit_check.md`。
- 编译：主稿 39 页、补充 18 页，未定义引用 0，重复标签 0，超过 10pt 的溢出 0；看过第 17、35、36 页。
- 测试：见 STATUS 本行。

## 全文其他箭头式极限（本轮未改，待作者决定是否统一）

| 位置 | 写法 | 性质 |
|---|---|---|
| 定理 4.1(iii)（`04_joint_control.tex`） | $t\uparrow t_2$ 时 $c(t)\to c_0$、$q(t)\to q_0$ | 陈述；NEW-4u 复查时按作者追加写明 $t\uparrow t_2$ |
| 附录 A.6 定理 4.1(iii) 的证明 | $t\uparrow t_2$ 时 $S(t)\downarrow S_c$；$c(t)\to c_0$ | 证明 |
| 命题 5.4 式 (5.7) | $\lim_{S\downarrow S_c}$ | 陈述 |
| 附录 A.9 命题 5.4 的证明 | $S\downarrow S_c$ 等价于 $\epsilon\downarrow0$；当 $S\downarrow S_c$ 时一致收敛 | 证明 |
| 附录 A.3 定理 3.5 的证明 | 因此 $I\to0$；令 $I\to0$ | 证明 |
| 3.3 节定理 3.5 后、5.3 节命题 5.7 后、6.4 节 | $I\to0$、$I_q\to0$；$r\to0^+$ 时趋于零；$S\to S_c$ 处 | 叙述 |
| 补充 S2 | $c_0\downarrow c_{0,\min}$、$c_0\to\infty$、$\theta\downarrow i_0$ 等 | 补充证明与叙述 |
| 补充 S4 | $\alpha\downarrow0$ 时连续衔接 | 补充叙述 |
| 补充 S5 | $\zeta_n\to\zeta$；$\zeta\to\infty$ 时 $\to0$；令 $\zeta\uparrow\zeta_0$ | 补充证明 |

## 待作者决定

1. 是否按本轮写法统一上表各处（陈述与证明改为 $\lim$ 或“右（左）极限”，叙述中的 $t\to\infty$ 等终点记号可保留）。作者 2026-10-28 同意统一，已完成，见 `NEW_limit_unify.md`。
