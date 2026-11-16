# 定理类陈述与证明的变化

- 旧稿：9d3c70d:paper/sections/04_joint_control.tex
- 新稿：paper/sections/04_joint_control.tex

带标签的陈述：旧稿 3 条，新稿 3 条；共同 3 条，其中未变化 0 条，有变化 3 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:representation

```diff
@@ -4 +4 @@
-\item 在几乎处处相等的意义下，$\mathcal A(\eta)$ 中的控制与满足
+\item 在几乎处处相等的意义下，$\mathcal A(\eta)$ 中的控制经 $c(t)=c_c(S(t))$ 与满足
@@ -8 +8 @@
-的有界可测函数 $c_c$ 一一对应，隔离比例由
+的可测函数 $c_c$ 一一对应，隔离比例由
@@ -14 +14 @@
-\item 状态轨迹与控制时长满足
+\item 阈值控制期内的 $S(t)$ 与控制时长 $\Delta t[c_c]=t_2-t_1$ 满足
@@ -22,2 +22,2 @@
-\item 选取满足式\eqref{eq:joint:contact-range}的逐点代表后，$c$ 与 $q$ 在 $t_2$ 处的左极限分别为 $c_0$ 与 $q_0$；
-若 $c_c(S)$ 连续，则两控制在阈值控制期内部连续。
+\item 取处处满足式\eqref{eq:joint:contact-range}的代表后，$c$ 与 $q$ 在 $t_2$ 处的左极限分别为 $c_0$ 与 $q_0$；
+若 $c_c$ 连续，则 $c$ 与 $q$ 在 $(t_1,t_2)$ 上连续。
```

### thm:joint:comparison

```diff
@@ -1 +1 @@
-设 $c_c$、$c_c^{(1)}$、$c_c^{(2)}$ 是 $\mathcal A(\eta)$ 中控制的状态函数。
+设条件\eqref{eq:model:trigger}成立，$c_c$、$c_c^{(1)}$、$c_c^{(2)}$ 是 $\mathcal A(\eta)$ 中控制的状态反馈函数，则
@@ -4 +4,2 @@
-\item 若 $c_c^{(1)}(S)\ge c_c^{(2)}(S)$ 几乎处处成立，则 $\Delta t[c_c^{(1)}]\le\Delta t[c_c^{(2)}]$，且前一不等式在正测度集合上严格成立时后一不等式严格；
+\item 若 $c_c^{(1)}(S)\ge c_c^{(2)}(S)$ 几乎处处成立，则 $\Delta t[c_c^{(1)}]\le\Delta t[c_c^{(2)}]$；
+若还在正测度集合上 $c_c^{(1)}>c_c^{(2)}$，则不等式严格。
@@ -12 +13 @@
-\item 沿 $c_c$ 对应的控制，阈值控制期累计新增感染与新增隔离易感者人数分别满足
+\item 沿 $c_c$ 对应的控制，阈值控制期的累计新增感染与新增隔离易感者人数分别满足
@@ -15 +16 @@
-&=\beta(S^*-S_c)+\gamma\eta(1-\beta)\Delta t,
+&=\beta(S^*-S_c)+\gamma\eta(1-\beta)\Delta t[c_c],
@@ -17,2 +18,2 @@
-S_q(t_2)-S_q(t_1)
-&=(1-\beta)\bigl[S^*-S_c-\gamma\eta\Delta t\bigr];
+\Delta S_q
+&=(1-\beta)\bigl[S^*-S_c-\gamma\eta\Delta t[c_c]\bigr];
@@ -20 +21 @@
-\item 阈值控制期累计新增感染是控制时长的严格增函数，新增隔离易感者人数是控制时长的严格减函数。
+\item 阈值控制期的累计新增感染是控制时长的严格增函数，新增隔离易感者人数是控制时长的严格减函数。
```

### cor:joint:whole-epidemic

```diff
@@ -1 +1 @@
-设两个允许控制在启动前及退出后均采用 $(c_0,q_0)$，并从同一初始状态首次到达同一阈值 $\eta$，则
+设条件\eqref{eq:model:trigger}成立，$\mathcal A(\eta)$ 中两个控制的各量分别记上标 (1)、(2)，则
```

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 2 条。

- thm:joint:comparison：汉字 175 → 206

```diff
@@ -1 +1 @@
-(i) 式\eqref{eq:joint:duration}的被积函数关于 $c_c(S)$ 严格递减。
+(i) 由式\eqref{eq:joint:contact-range}，式\eqref{eq:joint:duration}被积函数的分母 $c_c(S)S-c_0\bar S\ge c_0(S_c-\bar S)>0$，所以被积函数关于 $c_c(S)$ 严格递减。
@@ -11 +11,2 @@
-等号成立要求相应非负积分差为零，即两个状态函数几乎处处相等。
+等号成立要求相应的非负被积函数之差的积分为零，即 $c_c$ 与相应端点几乎处处相等。
+左界即仅隔离控制的控制时长\eqref{eq:s1:t2}。
@@ -17 +18 @@
-右端积分项乘以 $\beta$ 即为阈值控制期总新增感染；
+右端积分项乘以 $\beta$ 即为阈值控制期的累计新增感染 $\Itcum(t_2)-\Itcum(t_1)$；
@@ -21 +22 @@
-S^*-S_c=\Itcum(t_2)-\Itcum(t_1)+S_q(t_2)-S_q(t_1),
+S^*-S_c=\Itcum(t_2)-\Itcum(t_1)+\Delta S_q,
@@ -24 +25 @@
-(iii) 由 $0<\beta<1$，式\eqref{eq:joint:cumulative}中 $\Delta t$ 的系数 $\gamma\eta(1-\beta)$ 为正，式\eqref{eq:joint:quarantine}中的系数 $-(1-\beta)\gamma\eta$ 为负，其余各项对所有控制相同。
+(iii) 由 $0<\beta<1$，式\eqref{eq:joint:cumulative}中 $\Delta t$ 的系数 $\gamma\eta(1-\beta)$ 为正，式\eqref{eq:joint:quarantine}中的系数 $-\gamma\eta(1-\beta)$ 为负，其余各项对所有控制相同。
```

- cor:joint:whole-epidemic：汉字 137 → 138

```diff
@@ -1,2 +1,2 @@
-(i) 两个控制在启动前相同，由命题~\ref{prop:model:positive}中解的唯一性，启动前两条轨迹相同，故 $t_1,S^*$ 相同。
-退出时的状态均为 $(S_c,\eta)$，由常规系统解的唯一性，退出后的 $S,I$ 轨迹只相差时间平移；
+(i) 由 $t_1$ 的定义与定义~\ref{def:model:threshold-strategy}，两个控制在 $t_1$ 之前都沿常规轨迹运行，在 $t_1$ 都处于 $(S^*,\eta)$，并都在 $(S_c,\eta)$ 退出。
+常规控制下 $(S,I)$ 的方程是自治的，由解的唯一性，退出后两条 $(S,I)$ 轨迹只相差时间平移；
```

