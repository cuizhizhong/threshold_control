# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 6 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:tend

```diff
@@ -9 +9 @@
-\item 存在唯一的清零时间 $t_{\rm end}>t_2$，满足 $I(t_{\rm end})=1$、$\dot I(t_{\rm end})<0$。
+\item 在 $(t_2,\infty)$ 上恰有一个时刻 $t_{\rm end}$ 满足 $I(t_{\rm end})=1$、$\dot I(t_{\rm end})<0$。
```

### thm:s1:Itcum

```diff
@@ -1,4 +1 @@
-设条件\eqref{eq:model:trigger}成立，则对仅隔离控制，
-\begin{enumerate}
-\renewcommand{\labelenumi}{(\roman{enumi})}
-\item 总累计新增感染为
+设条件\eqref{eq:model:trigger}成立，则仅隔离控制的总累计新增感染为
@@ -11,2 +8 @@
-\item 计算至无限时刻的总累计新增感染由式\eqref{eq:s1:cumulative}把 $S_{\rm end}$ 换成 $S_\infty$ 得到。
-\end{enumerate}
+把其中的 $S_{\rm end}$ 换成 $S_\infty$，即得计算至无限时刻的总累计新增感染。
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:Itcum：汉字 106 → 106

```diff
@@ -1 +1 @@
-(i) 由式\eqref{eq:model:full}，常规控制下总新增感染的流入为 $\beta c_0SI/N$，而 $-\dot S=c_0[\beta+(1-\beta)q_0]SI/N$，故前后两个常规阶段都有
+由式\eqref{eq:model:full}，常规控制下总新增感染的流入为 $\beta c_0SI/N$，而 $-\dot S=c_0[\beta+(1-\beta)q_0]SI/N$，故前后两个常规阶段都有
@@ -14,2 +14 @@
-(ii) 由定理~\ref{thm:s1:tend}(i)，$t\to\infty$ 时 $S(t)\to S_\infty$。
-退出后一段的累计新增感染因而以 $S_c-S_\infty$ 代替 $S_c-S_{\rm end}$，其余两段不变。
+由定理~\ref{thm:s1:tend}(i)，$t\to\infty$ 时 $S(t)\to S_\infty$，退出后一段的累计新增感染因而以 $S_c-S_\infty$ 代替 $S_c-S_{\rm end}$，其余两段不变。
```

