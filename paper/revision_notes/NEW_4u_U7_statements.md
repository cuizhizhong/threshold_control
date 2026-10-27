# 定理类陈述与证明的变化

- 旧稿：f295f43:paper/sections/07_xian.tex f295f43:paper/supplement_sections/S6_xian.tex
- 新稿：paper/sections/07_xian.tex paper/supplement_sections/S6_xian.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 0 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:dom:floor

```diff
@@ -1 +1,2 @@
-在 $S_q(0)=0$ 的无回流模型中，能够容纳给定重构轨迹的有效人口须满足
+设无回流模型~\eqref{eq:model:full}的总人口为 $N_{\rm eff}$，$S_q(0)=0$。
+若它的一条解在某一时刻的社区与隔离累计新增感染分别等于重构轨迹的 $I_{\rm cum}^{\rm T}$ 与 $I_{q_{\rm cum}}^{\rm T}$，则
```

### prop:reference-population

```diff
@@ -1,2 +1 @@
-固定 $s_0,i_0,\theta$ 和模型参数，且 $i_0<\theta<i_{\max}^{0}$。
-在 $N\theta>1$ 的范围内，仅隔离控制的清零时间、计算至该终点的累计新增感染及其占人口的比例均随 $N$ 严格增加。
+固定 $s_0,i_0,\theta$ 和模型参数，设 $i_0<\theta<i_{\max}^{0}$，则在 $N\theta>1$ 的范围内，仅隔离控制的清零时间、计算至该终点的累计新增感染及其占人口的比例均随 $N$ 严格增加。
```

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 2 条。

- prop:dom:floor：汉字 22 → 28

```diff
@@ -1 +1,2 @@
-由式\eqref{eq:count-identities}，$S_q(T)=(1-\beta)I_{q_{\rm cum}}(T)/\beta$。
+记该时刻为 $T$。
+由式\eqref{eq:count-identities}与 $S_q(0)=0$，$S_q(T)=(1-\beta)I_{q_{\rm cum}}(T)/\beta$。
```

- prop:reference-population：汉字 85 → 98

```diff
@@ -1,2 +1,2 @@
-归一化轨迹及启动、控制时长与 $N$ 无关。
-退出后 $i(t)$ 从 $\theta$ 严格下降至零，终点为 $i=1/N$。
+由正文命题~\ref{prop:scaling}的证明，归一化轨迹及启动、控制时长与 $N$ 无关。
+由正文定理~\ref{thm:s1:tend}，退出后 $i(t)$ 从 $\theta$ 严格下降至零，终点为 $i=1/N$。
```

