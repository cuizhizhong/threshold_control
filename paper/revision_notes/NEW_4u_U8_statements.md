# 定理类陈述与证明的变化

- 旧稿：f127b3a:paper/appendices/A_proofs_sensitivity.tex f127b3a:paper/sections/02_model.tex f127b3a:paper/sections/03_single_control.tex f127b3a:paper/sections/06_numerics.tex f127b3a:paper/sections/07_xian.tex f127b3a:paper/sections/08_discussion.tex f127b3a:paper/sections/09_conclusion.tex f127b3a:paper/supplement_sections/S7_return.tex
- 新稿：paper/appendices/A_proofs_sensitivity.tex paper/sections/02_model.tex paper/sections/03_single_control.tex paper/sections/06_numerics.tex paper/sections/07_xian.tex paper/sections/08_discussion.tex paper/sections/09_conclusion.tex paper/supplement_sections/S7_return.tex

带标签的陈述：旧稿 18 条，新稿 18 条；共同 18 条，其中未变化 15 条，有变化 3 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:scaling

```diff
@@ -6 +6 @@
-\item 使用绝对终点 $I=1$ 时，$t_{\rm end}$ 及计算至该终点的累计新增感染比例一般仍含 $N$。
+\item 使用绝对终点 $I=1$ 时，终点条件 $i=1/N$ 含 $N$，$t_{\rm end}$ 及计算至该终点的累计新增感染比例的表达式因而仍含 $N$。
```

### prop:dom:floor

```diff
@@ -1 +1 @@
-设无回流模型~\eqref{eq:model:full}的总人口为 $N_{\rm eff}$，$S_q(0)=0$。
+设无回流模型\eqref{eq:model:full}的总人口为 $N_{\rm eff}$，$S_q(0)=0$。
```

### cor:return:right-discontinuity

```diff
@@ -2 +2 @@
-固定控制律 $\pi$（上述状态函数 $c_c$），并设对 $\omega=0$ 与每个 $\omega>0$，在模型\eqref{eq:return:model}中实施 $\pi$ 的阈值策略都有解，即平台能维持到 $S$ 首次到达 $S_c$。
+固定控制律 $\pi$（上述状态函数 $c_c$），并设对 $\omega=0$ 与每个 $\omega>0$，在模型\eqref{eq:return:model}中实施 $\pi$ 的阈值策略都有解，即阈值控制能维持到 $S$ 首次到达 $S_c$。
```

## 证明

有证明的陈述：旧稿 10 条，新稿 10 条；证明有变化 1 条。

- prop:return:final-size：汉字 143 → 143

```diff
@@ -5 +5 @@
-未感染接触者被追踪的流量 $A_q=(1-\beta)cqSI/N=\frac{1-\beta}{\beta}qF\le\frac{1-\beta}{\beta}F$ 可积。
+未感染接触者被追踪的流量 $A_q=(1-\beta)cqSI/N=[(1-\beta)/\beta]qF\le[(1-\beta)/\beta]F$ 可积。
```

