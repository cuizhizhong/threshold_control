# 定理类陈述与证明的变化

- 旧稿：430d487:paper/appendices/A_proofs_sensitivity.tex
- 新稿：paper/appendices/A_proofs_sensitivity.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 2 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 2 条。

- prop:model:positive：汉字 250 → 217

```diff
@@ -4 +4 @@
-$S$ 的方程关于 $S$ 线性，$I$ 的方程关于 $I$ 线性（把解中的另一变量看作已知函数），分别积分得
+沿局部解分别积分 $S$ 与 $I$ 的线性方程，得
@@ -14,2 +14 @@
-由非负性与总和守恒，解始终在有界集 $[0,N]^5$ 中，于是由延拓定理，它可以延拓到全部 $t\ge0$。
-因此 (i) 成立，且 (ii) 对一切 $t\ge0$ 成立。
+由非负性与总人口守恒，解始终位于紧集 $[0,N]^5$，故由延拓定理可延拓至 $[0,\infty)$。
```

- lem:proof:fold-free：汉字 144 → 145

```diff
@@ -0,0 +1 @@
+先证 $\sigma=\sigma_c$ 时的非负性与等号条件，再由 $F/\sigma^2$ 关于 $\sigma$ 的单调性得到 $0<\sigma<\sigma_c$ 时的严格正性。
@@ -18,3 +19,2 @@
-$F$ 是 $\sigma$ 的二次式，且 $F(p;0)=p^3>0$。
-若 $X(p)\le0$，$F$ 在 $\sigma>0$ 上严格减，故 $F(p;\sigma)>F(p;\sigma_c)\ge0$。
-若 $X(p)>0$ 且 $F$ 有实根 $\sigma_1\le\sigma_2$，则判别式非负给出 $X\le b^2w^2/p$，于是
+由 $p^4-16(2p-3)=(p-2)^2(p^2+4p+12)\ge0$，$p^2\ge4w$；
+又 $0<b<1$、$\sigma_c<2$，故 $0<\sigma\le\sigma_c$ 时 $bw\sigma<p^2$，从而
@@ -22 +22,2 @@
-\sigma_2\ge\frac{bpw}{X}\ge\frac{p^2}{bw}>\frac{p^2}{\sqrt{2p-3}}\ge4>\sigma_c;
+\frac{\partial}{\partial\sigma}\frac{F(p;\sigma)}{\sigma^2}
+=\frac{2p(bw\sigma-p^2)}{\sigma^3}<0.
@@ -24,2 +25 @@
-由 $F(p;\sigma_c)\ge0$ 得 $\sigma_c\le\sigma_1$，故 $F(p;\sigma)>0$。
-若 $F$ 无实根，亦有 $F>0$。
+因此 $0<\sigma<\sigma_c$ 时 $F(p;\sigma)/\sigma^2>F(p;\sigma_c)/\sigma_c^2\ge0$，即 $F(p;\sigma)>0$。
```

