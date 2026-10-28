# 全文极限写法统一（作者 2026-10-28 对话同意）

基准：`a37c6eb`（定理 5.2 证明的极限写法）。作者看过 `NEW_thm52_limit_notation.md` 末尾的清单后同意统一。本轮按定理 5.2 证明的写法处理其余各处：陈述与证明中的极限写成 $\lim_{x\to a^{\pm}}$ 或“在某点处的右（左）极限”，参数趋近写成“令 $x$ 从右（左）侧趋于 $a$”；不再使用 $\downarrow$、$\uparrow$、$\longrightarrow$ 与“$x\to a$ 时 $f\to L$”。

## 保留的箭头

- $\lim$ 下标中的箭头（通行写法）。
- 作终点标记的 $t\to\infty$：第 2.1 节“涉及 $t\to\infty$ 的结论”、第 2.4 节“其他终点（如 $t\to\infty$）”、第 9 章“$t\to\infty$ 的累计感染”；补充命题 S6.1(ii) 证明中“无限时间的终点为 $i\to0$”。这些是终点的名称，不是在求极限。
- 补充 S5 中权重区间转折的标记 A$\to$A$'$、A$'\to$B、B$\to$C（表 S1 与正文）。

## 修改表

| 位置 | 原写法 | 新写法 | 类别 |
|---|---|---|---|
| 定理 4.1(iii)（陈述） | $t\uparrow t_2$ 时 $c(t)\to c_0$、$q(t)\to q_0$ | $c$ 与 $q$ 在 $t_2$ 处的左极限分别为 $c_0$ 与 $q_0$ | 措辞，含义不变 |
| 命题 5.4 式 (5.7)（陈述） | $\lim_{S\downarrow S_c}$（两处） | $\lim_{S\to S_c^{+}}$ | 记号，含义不变 |
| 3.3 节定理 3.5 后 | 流入 $I_q$ 的感染随 $I\to0$ 趋于零……故 $I_q\to0$；$S_q$ 与 $R$ 单调有界 | 由 $\lim_{t\to\infty}I(t)=0$……故 $\lim_{t\to\infty}I_q(t)=0$；$S_q$ 与 $R$ 单调有界，因而也收敛 | 叙述 |
| 5.3 节命题 5.7 后 | $J_{\min}/w_c$ 是凹函数且在 $r\to0^+$ 时趋于零 | $J_{\min}/w_c$ 是 $r$ 的凹函数，且 $\lim_{r\to0^{+}}J_{\min}/w_c=0$ | 叙述 |
| 6.4 节 | 等高线在 $S\to S_c$ 处趋于水平线 | 等高线在 $S_c$ 附近趋于水平线 | 叙述 |
| 附录 A.3（定理 3.5(i) 的证明） | 因此 $I\to0$；令 $I\to0$ | 因此 $\lim_{t\to\infty}I(t)=0$；在式 (A.1) 中令 $t$ 趋于无穷，由 $\lim_{t\to\infty}I(t)=0$ 与 $0<S_\infty<S_c$ 选择 $W_0$ 分支 | 证明写法 |
| 附录 A.6（定理 4.1(iii) 的证明） | $t\uparrow t_2$ 时 $S(t)\downarrow S_c$；当 $S\downarrow S_c$ 时两界均趋于 $c_0$，故 $c(t)\to c_0$；继而 $q\to q_0$ | 由 (ii)，$S$ 连续且严格减、$S(t_2)=S_c$，故 $\lim_{t\to t_2^{-}}S(t)=S_c$；由夹逼得 $\lim_{t\to t_2^{-}}c(t)=c_0$，再由式 (4.3) 得 $\lim_{t\to t_2^{-}}q(t)=q_0$ | 证明写法；写明夹逼 |
| 附录 A.9（命题 5.4(i) 的证明） | $S\downarrow S_c$ 等价于 $\epsilon\downarrow0$；当 $S\downarrow S_c$ 时右侧一致收敛于……；原问题最小点的任一序列都趋于 $w_q/(w_c+w_q)$；比值的极限给出式 (5.7) | $S>S_c$ 时 $0<\epsilon<1$，$\lim_{S\to S_c^{+}}\epsilon=0$；记右侧为 $g_S$、极限函数为 $g$，写出 $\lim_{S\to S_c^{+}}\sup_x|g_S-g|=0$；记 $X(S)$ 为最小点集合，证 $\lim_{S\to S_c^{+}}\sup_{x\in X(S)}|x-x^*|=0$（反证与原文相同）；写明两个比值分别等于 $x$ 与 $(1-x)/(1-\epsilon x)$ | 证明写法；“任一序列”精确化为对最小点集合的一致收敛，覆盖任一逐状态最小化选择，论证不变 |
| 补充引理 S2.1 的证明 | $c_0\to\infty$ 时趋于 $I_0+\beta_2^0S_0/\beta_1^0$ | $\lim_{c_0\to\infty}I_{\max}^{0}=I_0+\beta_2^0S_0/\beta_1^0$ | 证明写法 |
| 补充命题 S2.2(iii) 的证明 | 当 $c_0\downarrow c_{0,\min}$ 时 $S^*\to S_c$，所以 $\Delta t\to0$；$c_0\to\infty$ 时 $S^*\to\cdots$；$\Delta t=\cdots\longrightarrow0$；两端趋零 | 当 $c_0$ 从右侧趋于 $c_{0,\min}$ 时，$S^*$ 趋于 $S_c$，故 $\Delta t$ 趋于零；$\lim_{c_0\to\infty}S^*=\cdots$；显示式 $\Delta t=\cdots$，$\lim_{c_0\to\infty}\Delta t=0$；两端极限为零 | 证明写法；第一处用文字，因行内 $\lim_{c_0\to c_{0,\min}^{+}}$ 上下标叠在一起不易读 |
| 补充 S2.2.2 低阈值极限 | 不能直接令 $\theta\to0$；沿同时满足 $i_0\to0$、$\theta\to0$ 的序列……$s^*\to s_0$；令 $\theta\downarrow i_0$ 时控制时长趋于有限值（显示式） | 不能直接令 $\theta$ 趋于零；令 $i_0$ 与 $\theta$ 同时趋于零并保持 $0<i_0<\theta$……$s^*$ 与 $s_0$ 趋于同一极限；显示式 $\lim_{\theta\to i_0^{+}}\Delta t=\cdots$ | 叙述；式 (S2.4) 不变 |
| 补充定理 S4.1 的证明 | 两组公式在 $\alpha\downarrow0$ 时连续衔接 | $\alpha>0$ 的公式在 $\alpha=0$ 处的右极限就是 $\alpha=0$ 的公式 | 证明写法 |
| 补充命题 S5.4 的证明 | 若 $\zeta_n\to\zeta$；$\zeta\to\infty$ 时 $G(\zeta;\zeta)\le r/(\zeta-b)\to0$；令 $\zeta\uparrow\zeta_0$，其极限点……；两侧极限分别为 $p_+$ 与 $p_-$；极限为 $\zeta_0$ | 若 $\lim_{n\to\infty}\zeta_n=\zeta$；由 $G(\zeta;\zeta)\le r/(\zeta-b)$，$\lim_{\zeta\to\infty}G(\zeta;\zeta)=0$；令 $\zeta$ 从左侧趋于 $\zeta_0$，由第三个事实，任一极限点……；最小点在 $\zeta_{\rm j}$ 处的右极限与左极限分别为 $p_+$ 与 $p_-$；右极限为 $\zeta_0$，左极限为 $p_0$ | 证明写法；写明所用的“第三个事实” |

## 核对

- 陈述：正文 2 条措辞变化（定理 4.1(iii)、命题 5.4），含义不变；补充 0 条。证明：补充 4 段有变化（引理 S2.1、命题 S2.2、定理 S4.1、命题 S5.4），正文附录 A.3、A.6、A.9 的证明不紧随陈述，工具未计入，以 `git diff` 为准。证明逻辑不变。报告：`NEW_limit_unify_statements_main.md`、`NEW_limit_unify_statements_supp.md`。
- `check_tex`（对 a37c6eb）：标签缺失 0，悬空引用 0，数字缺 0、增 0，见 `NEW_limit_unify_check.md`。
- 编译：主稿 39 页、补充 18 页，未定义引用 0，重复标签 0，超过 10pt 的溢出 0；看过主稿第 10、13、18、31、33、34 页与补充第 2、5、11 页。
- `text_identity.py --refresh-current` 刷新 `nr_audit/manuscript_path_migration_NEW4g.json` 的当前内容哈希，历史 raw SHA 保持。
- 测试：全量 411 项通过（`NEW_limit_unify_pytest_full.xml`）。

## 待作者决定

无。
