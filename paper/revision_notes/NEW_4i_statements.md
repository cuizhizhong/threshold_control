# 定理类陈述与证明的变化

- 旧稿：2829f20:paper/flatten_curve_analysis_cn.tex 2829f20:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 41 条，新稿 41 条；共同 41 条，其中未变化 39 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:cost-minimum

```diff
@@ -3 +3 @@
-在相应的控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中（不另加总时长、调整次数或控制变化率等约束），二次干预强度成本的最小值可以达到，且
+在相应的控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中，二次干预强度成本的最小值可以达到，且
```

### rem:joint:headcount-cost

```diff
@@ -2 +2 @@
-由式\eqref{eq:joint:cumulative}与\eqref{eq:joint:quarantine}，对非负人数权重 $a_I,a_Q$，有
+由式\eqref{eq:joint:cumulative}与\eqref{eq:joint:quarantine}，对非负人数权重 $a_I,a_Q$（以天/人计，与 $J$ 的量纲一致），有
@@ -10 +9,0 @@
-按 $J$ 的时间量纲，$a_I,a_Q$ 的单位为时间/人数，$\kappa$ 无量纲。
@@ -13 +11,0 @@
-这里两项均计新增人数，不计隔离人天。
```

## 证明

有证明的陈述：旧稿 23 条，新稿 23 条；证明有变化 1 条。

- prop:sup:rhat：汉字 166 → 166

```diff
@@ -11,2 +11,2 @@
-利用恒等式 $d(x-\sigma)^2-ax^2(x-b\sigma)=(1-x)R(x)$，$R(x)=ax^2-d\sigma(2-\sigma)x+d\sigma^2$，对 $x\in[\sigma,1)$，$f(S,c_0x)\ge f(S,c_0)$ 等价于 $d(1-x)x^2+rR(x)\ge0$。
-在 $\sigma=S_c/S_{\rm sw}$ 上 $2b\sigma^2-3\sigma+1=0$，即 $2\sigma d=1-\sigma$，于是 $R(x)=a(x-1)(x-x_2)$，$x_2=\sigma/[2(1-\sigma)]<\sigma$。
+利用恒等式 $d(x-\sigma)^2-ax^2(x-b\sigma)=(1-x)P(x)$，$P(x)=ax^2-d\sigma(2-\sigma)x+d\sigma^2$，对 $x\in[\sigma,1)$，$f(S,c_0x)\ge f(S,c_0)$ 等价于 $d(1-x)x^2+rP(x)\ge0$。
+在 $\sigma=S_c/S_{\rm sw}$ 上 $2b\sigma^2-3\sigma+1=0$，即 $2\sigma d=1-\sigma$，于是 $P(x)=a(x-1)(x-x_2)$，$x_2=\sigma/[2(1-\sigma)]<\sigma$。
@@ -22 +22 @@
-令 $t=S_{\rm sw}/S_c$，则 $b=t(3-t)/2$，不等式 $r_{\rm cont}<\hat r$ 化为 $(t-1)(t-2)^2>0$。
+由 $\zeta_{\rm sw}=S_{\rm sw}/S_c$ 得 $b=\zeta_{\rm sw}(3-\zeta_{\rm sw})/2$，不等式 $r_{\rm cont}<\hat r$ 化为 $(\zeta_{\rm sw}-1)(\zeta_{\rm sw}-2)^2>0$。
```

