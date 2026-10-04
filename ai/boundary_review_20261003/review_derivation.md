# 数学推导与修改意见（新增审查推导）

本推导限定为仅隔离控制，固定绝对 I0，其他初始仓室为零，即 s0=1-i0。传播参数与参照 JT、Tmax 不变。不将结果推广为任意人口模型或累计感染/清零边界的结论。

## 1. 正初值极限，而不是零初值疫情

为缩短本推导，临时记

\[
a=\frac{\beta(1-q_0)}{\beta+q_0(1-\beta)},\quad
b=\frac{\gamma}{c_0[\beta+q_0(1-\beta)]},\quad s_c=b/a.
\]

这些只用于证明，不建议增加到正文符号表。
归一化首次触发方程为
\[
\theta=i_0+a(1-i_0-s^*)+b\ln\frac{s^*}{1-i_0}.
\]
将其写为
\[
\theta=G(s^*)+h(i_0),\quad
G(s)=a(1-s)+b\ln s,\quad
h(i)=(1-a)i-b\ln(1-i).
\]
在 s>s_c 上 G'(s)=-a+b/s<0；固定一个内部 theta>0，即使 i0 趋于0，代数方程的相应根仍满足 s_c<s^*<1。因此其为正初值公式的光滑延拓，而非 I0=0 解的触发点。真正 I0=0 的ODE始终 I=0，没有 t1。启动时间不具有这里所用的有限零初值延拓。

由隐函数微分，固定 theta 时
\[
\frac{\partial s^*}{\partial i_0}=\frac{1-a+b/(1-i_0)}{a-b/s^*}>0,
\quad
\frac{\partial s^*}{\partial\theta}=-\frac1{a-b/s^*}<0.
\]

## 2. 阈值边界的正则性与一阶展开

对于 F=J 或 Delta t，均有 F(theta,i0)=U(s^*)/theta，其中
\[
U_T(s)=\frac1{c_0}\ln\frac{s-\bar s}{s_c-\bar s},\quad
U_J(s)=\frac2{c_0}\int_{s_c}^s\frac{(1-s_c/u)^2}{u-\bar s}\,du.
\]
在内部触发区间 U,U'>0。于是
\[
F_\theta=-F/\theta+(U'/\theta)s^*_\theta<0,\quad
F_{i_0}=(U'/\theta)s^*_{i_0}>0.
\]
现稿 prop:threshold-tradeoff 已陈述严格导数符号；上式补足零初值光滑延拓和沿 s0=1-i0 的导数。

令 F(theta(i),i)=K>0，零极限根记为 theta(0)，则
\[
\theta'(0)=-\frac{F_{i_0}}{F_\theta}\bigg|_{(\theta(0),0)}>0.
\]
这里原函数在内部是光滑的，因此可以用二阶Taylor式，不只是由可导性推出O(i^2)。得到
\[
\eta(N)=N\theta(I_0/N)=N\theta(0)+\theta'(0)I_0+O(I_0^2/N).
\]
余项不能省略，不能把实际边界叫作精确平移直线。在含有所有相关 i0 的紧区间上，若 M 上界控制二阶导数，则
\[
|\eta(N)-N\theta(0)-\theta'(0)I_0|\le M I_0^2/(2N).
\]

便于复核的显式系数为
\[
\theta'(0)=\frac{(1-a+b)U'(s^*)}{U'(s^*)+K(a-b/s^*)},
\]
其中 s^* 在对应零极限根处取值。

## 3. 实际图件使用的另一条参考线

当前 reproduction/population.py（正式目录名为 reproducibility）在 N_ref=13163000 下计算 theta_root，再传给绘图函数。因此原图斜率为 theta(I0/N_ref)，并非 theta(0)。相对于该参考线，
\[
\eta(N)-N\theta(I_0/N_{\rm ref})=
\theta'(0)I_0(1-N/N_{\rm ref})
+O(I_0^2/N+NI_0^2/N_{\rm ref}^2).
\]
当 N=N_ref 时，两者精确相同（实际输出另有浮点/求根误差）；不可称所有人口下都有同一个正截距偏移。

## 4. 精确集合与人口交点

正文集合应先用实际的 J(eta,N)、Delta t(eta,N) 定义，同时保留 I0<eta<Imax_no(N) 的严格触发条件及 eta<=Ipeak_T。近似直线只解释图像，不决定成员资格。

在边界内部，1-i0>s_c 给出 0<h'(i0)<1，且
\[
0<\theta'(i_0)=h'(i_0)\frac{U'}{U'+K(a-b/s^*)}<h'(i_0)<1.
\]
因此
\[
\frac{d}{dN}[N\theta(I_0/N)]
=\theta-i_0\theta'(i_0)>\theta-i_0>0.
\]
所以对这两类内部边界，固定峰值水平的交点至多一个；存在时可用实际指标求根定义 N*。这不包含累计感染或清零等值线的唯一性结论。

当成本约束起作用时，应定义 J(Ipeak_T,N*_infty)=JT，而不是把有限初值下的精确交点仍定义为 Ipeak_T 除以常数 theta。第一阶近似为
\[
N^*\simeq\frac{I_{\rm peak}^{\rm T}-\kappa I_0}{\theta(0)}.
\]
仓库已直接求解精确交点，表格显示值无需强制更改；eq:dom:main-interval 的符号区间与取整区间之间应使用约等号。

## 5. 写作取舍

9.1保留固定绝对初值；4.4保持原条件。9.5用实际指标定义集合，明确绘图参考斜率来源。将本推导放附录，正文只用一阶式及必要说明，不新画一张几乎重合的图。新数值必须另接入 reproducibility，记录参考输入、精度、误差和图件斜率，不以本目录的独立诊断冒充已验收结果。
