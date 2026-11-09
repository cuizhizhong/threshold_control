# 定理类陈述与证明的变化

- 旧稿：4c5ae62:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 9 条，新稿 9 条；共同 9 条，其中未变化 8 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:inflection

```diff
@@ -1 +1 @@
-设条件\eqref{eq:model:trigger}成立，则
+设条件\eqref{eq:model:trigger}成立，$q_c(t)$ 为定理~\ref{thm:s1:qc-structure}中的隔离比例，则
@@ -4 +4 @@
-\item $q_c(t)$ 在 $(t_1,t_2)$ 内存在唯一拐点，当且仅当
+\item $q_c(t)$ 在 $(t_1,t_2)$ 内存在唯一拐点（下称内部拐点），当且仅当
@@ -8 +8 @@
-等价地，$\frac12<(1-\beta)(1-q_0)<-\frac12W_{-1}(z_\eta)$；
+等价地，$1/2<(1-\beta)(1-q_0)<-W_{-1}(z_\eta)/2$；
@@ -15 +15,2 @@
-且 $q_0<\qinf<q_{\max}$，隔离比例的下降速度在 $t_{\rm inf}$ 唯一达到最大值。
+且 $q_0<\qinf<q_{\max}$；
+\item 内部拐点存在时，隔离比例的下降速度 $|dq_c/dt|$ 在 $(t_1,t_2)$ 上于 $t_{\rm inf}$ 唯一取得最大值。
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:inflection：汉字 111 → 141

```diff
@@ -7,2 +7,4 @@
-由式\eqref{eq:s1:barS}，阈值控制期内 $S\ge S_c>\bar S$，故其符号由 $2\bar S-S$ 决定。
-$S$ 从 $S^*$ 严格下降至 $S_c$，所以恰在式\eqref{eq:s1:inflection-condition}成立时穿过 $2\bar S$，且只穿过一次。
+由式\eqref{eq:s1:barS}，阈值控制期内 $S\ge S_c>\bar S$，故 $d^2q_c/dt^2$ 与 $2\bar S-S$ 同号。
+$S$ 在 $(t_1,t_2)$ 上从 $S^*$ 严格下降至 $S_c$。
+若式\eqref{eq:s1:inflection-condition}成立，$S$ 恰在一个时刻经过 $2\bar S$，$d^2q_c/dt^2$ 在该时刻由负变正，这是 $(t_1,t_2)$ 内唯一的拐点。
+否则 $2\bar S-S$ 在 $(t_1,t_2)$ 上不变号，没有拐点。
@@ -12 +14,3 @@
-二阶导数先负后正，而一阶导数始终为负，故 $|dq_c/dt|$ 在该时刻唯一达到最大值。
+(iii) 由 (i) 的证明，$d^2q_c/dt^2$ 在 $t_{\rm inf}$ 之前为负、之后为正；
+由式\eqref{eq:s1:qprime}，$dq_c/dt<0$。
+因此 $|dq_c/dt|$ 在 $(t_1,t_{\rm inf}]$ 上严格增加，在 $[t_{\rm inf},t_2)$ 上严格减少，于 $t_{\rm inf}$ 唯一取得最大值。
```

