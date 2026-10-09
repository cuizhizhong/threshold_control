# 定理类陈述与证明的变化

- 旧稿：pre-rewrite-20261007:paper/sections/07_xian.tex
- 新稿：paper/sections/07_xian.tex

带标签的陈述：旧稿 1 条，新稿 1 条；共同 1 条，其中未变化 1 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 1 条，新稿 1 条；证明有变化 1 条。

- prop:dom:floor：汉字 40 → 22

```diff
@@ -1,3 +1,2 @@
-由式\eqref{eq:count-identities}，隔离易感者人数为
-$S_q(T)=(1-\beta)I_{q_{\rm cum}}(T)/\beta$。
-易感者流出的三部分为社区感染、隔离感染和未感染者隔离，故
+由式\eqref{eq:count-identities}，$S_q(T)=(1-\beta)I_{q_{\rm cum}}(T)/\beta$。
+易感者的流出由上述三部分组成，故
@@ -8 +7 @@
-再用 $S_0\le N_{\rm eff}$ 即得。
+再由 $S(T)\ge0$ 与 $S_0\le N_{\rm eff}$ 即得。
```

