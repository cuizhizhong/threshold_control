# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/supplement_sections/S1_medical.tex
- 新稿：paper/supplement_sections/S1_medical.tex

带标签的陈述：旧稿 1 条，新稿 1 条；共同 1 条，其中未变化 0 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### lem:sup:infected-bound

```diff
@@ -1,2 +1 @@
-设条件\eqref{eq:model:trigger}成立，$I_q(0)\le(\kappa_I-1)\eta$。
-则对 $\mathcal A(\eta)$ 中任一控制和所有 $t\ge0$，有
+设条件\eqref{eq:model:trigger}成立，且 $I_q(0)\le(\kappa_I-1)\eta$，则对 $\mathcal A(\eta)$ 中任一控制和所有 $t\ge0$，有
```

## 证明

有证明的陈述：旧稿 1 条，新稿 1 条；证明有变化 1 条。

- lem:sup:infected-bound：汉字 68 → 112

```diff
@@ -1,4 +1,4 @@
-$\mathcal A(\eta)$ 中始终有 $I\le\eta$（退出后由定理~\ref{thm:s1:tend}）、$c\le c_0$ 与 $S\le S_0$，故新增感染 $F=\beta cSI/N\le\beta c_0S_0\eta/N$。
-阈值控制期内，由式\eqref{eq:model:balance}，进入 $I_q$ 的流量为 $F-\gamma\eta$；
-其余时段控制为 $(c_0,q_0)$，流量为 $q_0F$，而 $S_0>S_c$ 给出 $q_0\beta c_0S_0/N\le\beta c_0S_0/N-\gamma$。
-两种情形下流量都不超过 $\delta_q(\kappa_I-1)\eta$，于是几乎处处有
+对 $\mathcal A(\eta)$ 中的控制，始终有 $I\le\eta$（退出后由定理~\ref{thm:s1:tend}）、$c\le c_0$ 与 $S\le S_0$，故单位时间的新增感染 $F=\beta cSI/N$ 满足 $F\le\beta c_0S_0\eta/N$，其中比例 $q$ 进入 $I_q$，其余进入 $I$。
+阈值控制期内，由式\eqref{eq:model:balance}，进入 $I$ 的流量为 $\gamma\eta$，进入 $I_q$ 的流量为 $F-\gamma\eta$。
+其余时段控制为 $(c_0,q_0)$，进入 $I_q$ 的流量为 $q_0F$，而 $S_0>S_c$ 给出 $q_0\beta c_0S_0/N\le\beta c_0S_0/N-\gamma$。
+两种情形下进入 $I_q$ 的流量都不超过 $\delta_q(\kappa_I-1)\eta$，于是几乎处处有
@@ -8,2 +8 @@
-由 $I_q(0)\le(\kappa_I-1)\eta$ 即得 $I_q\le(\kappa_I-1)\eta$。
-再与 $I\le\eta$ 相加。
+由比较原理与 $I_q(0)\le(\kappa_I-1)\eta$，对所有 $t\ge0$ 有 $I_q(t)\le(\kappa_I-1)\eta$，再与 $I\le\eta$ 相加即得结论。
```


---

## 附录 A（A_proofs_sensitivity.tex）

# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/appendices/A_proofs_sensitivity.tex
- 新稿：paper/appendices/A_proofs_sensitivity.tex

带标签的陈述：旧稿 1 条，新稿 1 条；共同 1 条，其中未变化 1 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 1 条，新稿 1 条；证明有变化 0 条。

