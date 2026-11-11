# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/02_model.tex
- 新稿：paper/sections/02_model.tex

带标签的陈述：旧稿 2 条，新稿 4 条；共同 1 条，其中未变化 0 条，有变化 1 条。

只在旧稿中（新稿中找不到该标签的陈述，需说明去向）：eq:model:plateau-requirement

只在新稿中（新增或改了首个标签）：lem:model:balance、def:model:threshold-strategy、cor:model:below-threshold

## 陈述有变化（逐条确认数学含义是否等价）

### prop:model:threshold-rationale

```diff
@@ -1 +1 @@
-设常规轨迹在有限时刻 $t_1$ 首次由下方到达 $I=\eta$，且 $S(t_1)=S^*>S_c$，则
+设条件\eqref{eq:model:trigger}成立，则
@@ -4,8 +4,2 @@
-\item 常规轨迹在 $[0,t_1)$ 上满足 $I<\eta$，而 $\dot I(t_1)>0$，因此在 $t_1$ 之后继续采用 $(c_0,q_0)$ 会立即越过阈值；
-\item 在 $I=\eta$ 的状态上，$\dot I\le0$ 当且仅当
-\[
-\frac{\beta c(1-q)S}{N}\le\gamma,
-\]
-且若在某个时间区间上 $I\equiv\eta$，则该区间上几乎处处取等号；
-\item 从状态 $(S,\eta)$ 起恢复并保持 $(c_0,q_0)$，此后始终有 $I\le\eta$，当且仅当 $S\le S_c$。
-因此，沿任一从 $(S^*,\eta)$ 出发并持续维持 $I=\eta$ 的轨迹，$S$ 首次降到 $S_c$ 的时刻是可以直接恢复常规控制的最早时刻。
+\item 若自 $t_1$ 起继续实施常规控制，则存在 $\varepsilon>0$，使 $I$ 在 $(t_1,t_1+\varepsilon)$ 上大于 $\eta$；
+\item 设某一时刻 $t_a$ 有 $I(t_a)=\eta$，且自 $t_a$ 起实施常规控制，则对一切 $t\ge t_a$ 有 $I(t)\le\eta$，当且仅当 $S(t_a)\le S_c$。
```

## 证明

有证明的陈述：旧稿 0 条，新稿 1 条；证明有变化 0 条。

