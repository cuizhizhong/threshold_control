# 定理类陈述与证明的变化

- 旧稿：pre-explicit-cut-20261116:paper/sections/04_joint_control.tex
- 新稿：paper/sections/04_joint_control.tex

带标签的陈述：旧稿 3 条，新稿 3 条；共同 3 条，其中未变化 2 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:comparison

```diff
@@ -12 +11,0 @@
-\item 显式族的 $\Delta t(\alpha)$ 在 $[0,1]$ 上严格递减；
```

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 1 条。

- thm:joint:comparison：汉字 195 → 175

```diff
@@ -12,2 +12 @@
-(ii) 显式族中 $c_c(S;\alpha)$ 对 $S>S_c$ 随 $\alpha$ 严格增加，由 (i)，其控制时长严格减少。
-(iii) 积分式\eqref{eq:joint:Sdot}，得
+(ii) 积分式\eqref{eq:joint:Sdot}，得
@@ -25 +24 @@
-(iv) 由 $0<\beta<1$，式\eqref{eq:joint:cumulative}中 $\Delta t$ 的系数 $\gamma\eta(1-\beta)$ 为正，式\eqref{eq:joint:quarantine}中的系数 $-(1-\beta)\gamma\eta$ 为负，其余各项对所有控制相同。
+(iii) 由 $0<\beta<1$，式\eqref{eq:joint:cumulative}中 $\Delta t$ 的系数 $\gamma\eta(1-\beta)$ 为正，式\eqref{eq:joint:quarantine}中的系数 $-(1-\beta)\gamma\eta$ 为负，其余各项对所有控制相同。
```

