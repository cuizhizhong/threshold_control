# 定理类陈述与证明的变化

- 旧稿：fffed42:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 9 条，新稿 9 条；共同 9 条，其中未变化 7 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### lem:s1:Sstar-sensitivity

```diff
@@ -1 +1 @@
-在条件\eqref{eq:model:trigger}下，启动状态满足
+设条件\eqref{eq:model:trigger}成立，则启动时的易感者人数满足
```

### prop:threshold-tradeoff

```diff
@@ -1 +1,4 @@
-设条件\eqref{eq:model:trigger}成立，则仅隔离控制满足
+设条件\eqref{eq:model:trigger}成立，则对仅隔离控制，
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 启动时刻、最大隔离比例与控制时长满足
@@ -3,5 +6,3 @@
-\frac{\partial t_1}{\partial\eta}>0,\quad
-\frac{\partial q_{\max}}{\partial\eta}<0,\quad
-\frac{\partial\Delta t}{\partial\eta}<0,\quad
-\frac{\partial J_q}{\partial\eta}<0,\quad
-\frac{\partial J}{\partial\eta}<0,
+\frac{\partial t_1}{\partial\eta}>0,\qquad
+\frac{\partial q_{\max}}{\partial\eta}<0,\qquad
+\frac{\partial\Delta t}{\partial\eta}<0;
@@ -9,2 +10,3 @@
-且 $\partial\Itcum/\partial\eta>0$；
-计算至无限时刻的累计新增感染也随 $\eta$ 严格增加。
+\item 成本满足 $\partial J_q/\partial\eta<0$、$\partial J/\partial\eta<0$；
+\item $\partial\Itcum/\partial\eta>0$，计算至无限时刻的总累计新增感染也随 $\eta$ 严格增加。
+\end{enumerate}
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 0 条。

