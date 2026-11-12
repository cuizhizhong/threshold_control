# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 7 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### cor:s1:qc-structure

```diff
@@ -1,4 +1 @@
-对定理~\ref{thm:s1:qc-structure}中的仅隔离控制，
-\begin{enumerate}
-\renewcommand{\labelenumi}{(\roman{enumi})}
-\item 隔离比例在 $t_1$ 从 $q_0$ 跳升至
+对定理~\ref{thm:s1:qc-structure}中的仅隔离控制，隔离比例在 $t_1$ 从 $q_0$ 跳升至
@@ -8,8 +5 @@
-在 $(t_1,t_2)$ 上严格递减，并在 $t_2$ 连续恢复为 $q_0$；
-\item 设隔离比例受能力约束 $q\le q_{\rm cap}$，其中 $q_0\le q_{\rm cap}<1$，则上述仅隔离控制可实施（即全程 $q(t)\le q_{\rm cap}$），当且仅当
-\[
-q_{\max}\le q_{\rm cap}
-\quad\Longleftrightarrow\quad
-\frac{\beta c_0(1-q_{\rm cap})S^*}{N}\le\gamma.
-\]
-\end{enumerate}
+在 $(t_1,t_2)$ 上严格递减，并在 $t_2$ 连续恢复为 $q_0$。
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- cor:s1:qc-structure：汉字 66 → 32

```diff
@@ -1 +1 @@
-(i) 由式\eqref{eq:s1:q-control}，$q_c(S)$ 关于 $S$ 严格增加，$S^*>S_c$ 给出启动时的跳升。
+由式\eqref{eq:s1:q-control}，$q_c(S)$ 关于 $S$ 严格增加，$S^*>S_c$ 给出启动时的跳升。
@@ -8,2 +7,0 @@
-(ii) 由 (i)，隔离比例在启动时取得最大值，故全程可实施当且仅当 $q_{\max}\le q_{\rm cap}$。
-代入式\eqref{eq:s1:qmax}即得所述等价式。
```

