# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 9 条，新稿 9 条；共同 9 条，其中未变化 9 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 6 条，新稿 6 条；证明有变化 1 条。

- thm:s1:Itcum：汉字 106 → 104

```diff
@@ -1 +1 @@
-由式\eqref{eq:model:full}，常规控制下总新增感染的流入为 $\beta c_0SI/N$，而 $-\dot S=c_0[\beta+(1-\beta)q_0]SI/N$，故前后两个常规阶段都有
+由式\eqref{eq:model:full}，常规控制下新增感染速率为 $\beta c_0SI/N$，而 $-\dot S=c_0[\beta+q_0(1-\beta)]SI/N$，故前后两个常规阶段都有
```

