# 定理类陈述与证明的变化

- 旧稿：07f7fbb:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 9 条，新稿 9 条；共同 9 条，其中未变化 7 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### rem:release-at-exit

```diff
@@ -8 +8,2 @@
-因此 $\xi S_q(t_2^-)>0$ 时，$I$ 在 $t_2$ 之后立即超过 $\eta$，即退出时一次性解除对未感染接触者的隔离，会使社区感染重新增长。
+因此 $\xi S_q(t_2^-)>0$ 时，$I$ 在 $t_2$ 之后立即上升并超过 $\eta$。
+也就是说，退出时一次性解除对未感染接触者的隔离，会使社区传播重新扩大。
```

### thm:s1:Itcum

```diff
@@ -1 +1,4 @@
-设条件\eqref{eq:model:trigger}成立，则仅隔离控制下统计至 $t_{\rm end}$ 的总累计新增感染为
+设条件\eqref{eq:model:trigger}成立，则对仅隔离控制，
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 统计至 $t_{\rm end}$ 的总累计新增感染为
@@ -5 +8 @@
-&+\beta\left[S^*-S_c+\bar S\ln\frac{S^*-\bar S}{S_c-\bar S}\right].
+&+\beta\left[S^*-S_c+\bar S\ln\frac{S^*-\bar S}{S_c-\bar S}\right];
@@ -8 +11,2 @@
-将 $S_{\rm end}$ 替换为 $S_\infty$，即得计算至无限时刻的累计新增感染。
+\item 计算至无限时刻的总累计新增感染由式\eqref{eq:s1:cumulative}把 $S_{\rm end}$ 换成 $S_\infty$ 得到。
+\end{enumerate}
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:Itcum：汉字 66 → 94

```diff
@@ -1 +1 @@
-由式\eqref{eq:model:full}，常规控制下总新增感染的流入为 $\beta c_0SI/N$，而 $-\dot S=c_0[\beta+(1-\beta)q_0]SI/N$，故前后常规阶段均有
+(i) 由式\eqref{eq:model:full}，常规控制下总新增感染的流入为 $\beta c_0SI/N$，而 $-\dot S=c_0[\beta+(1-\beta)q_0]SI/N$，故前后两个常规阶段都有
@@ -3 +3 @@
-\frac{\beta c_0SI}{N}=\frac{\beta}{\beta+q_0(1-\beta)}(-\dot S),
+\frac{\beta c_0SI}{N}=\frac{\beta}{\beta+q_0(1-\beta)}(-\dot S).
@@ -5,2 +5,2 @@
-所以两段的积分分别由 $S_0-S^*$、$S_c-S_{\rm end}$ 给出。
-阈值控制期内用 $dt=-N\,dS/[c_0\eta(S-\bar S)]$，得
+积分得两段的累计新增感染，分别为 $\beta/[\beta+q_0(1-\beta)]$ 乘以 $S_0-S^*$ 与 $S_c-S_{\rm end}$。
+阈值控制期内，由定理~\ref{thm:s1:qc-structure}的证明，$\dot S=-(c_0\eta/N)(S-\bar S)$，故 $dt=-N\,dS/[c_0\eta(S-\bar S)]$，得
@@ -12,2 +12,3 @@
-三段相加即得结论；
-无限时刻的表达由极限得到。
+三段相加即得式\eqref{eq:s1:cumulative}。
+(ii) 由定理~\ref{thm:s1:tend}(i)，$t\to\infty$ 时 $S(t)\to S_\infty$。
+退出后一段的累计新增感染因而以 $S_c-S_\infty$ 代替 $S_c-S_{\rm end}$，其余两段不变。
```

