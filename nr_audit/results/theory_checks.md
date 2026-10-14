# NR-1 代数核对结果（`nr_audit/theory_checks.py`）

只核对代数；不代替存在性、可测性与量词论证。example 为参数算例（证据类型 N），只说明可能性。

共 118 项，通过 118 项，未通过 0 项。

| 组 | 编号 | 内容 | 方法 | 结果 | 细节 |
|---|---|---|---|---|---|
| A | A1 | 式(2.1)五式右端之和为 0（总人数守恒） | symbolic | 通过 |  |
| A | A2 | 式(2.10)第一式：dI_cum/dt = dI/dt + gamma I | symbolic | 通过 |  |
| A | A3 | 式(2.10)第二式：dS_q/dt = (1-beta)/beta · dI_qcum/dt | symbolic | 通过 |  |
| A | A4 | -dS/dt = dItcum/dt + dS_q/dt（易感者流出只有感染与未感染隔离两条去路） | symbolic | 通过 |  |
| A | A5 | 常规控制下 R_e = beta c0 (1-q0) S/(gamma N) = S/S_c | symbolic | 通过 |  |
| A | A6 | beta2^0/beta1^0 = rho1/S_c（式 2.3 末式） | symbolic | 通过 |  |
| A | A7 | 常规控制下 dI/dt = gamma I (S/S_c - 1)（附录 A.1(iii)、A.2） | symbolic | 通过 |  |
| A | A8 | 式(3.1)三种 z_eta 写法相等，且 z_eta∈(-1/e,0) | numeric | 通过 | 最大相对差 2.03e-39 |
| A | A9 | 定理 3.1：S*=-S_c W_{-1}(z_eta) 满足 I(S*)=eta 且 S_c<S*<S0；W_0 分支给出 S<S_c 的交点 | numeric | 通过 | 首次积分最大相对残差 2.64e-39 |
| A | A10 | 定理 3.5：S_end、S_inf 的 W_0 表达满足退出后首次积分(A.1)，且 0<S_inf<S_end<S_c | numeric | 通过 | 最大残差 1.2e-35 |
| B | B1 | 式(3.4)：S̄/S_c=(1-beta)(1-q0) | symbolic | 通过 |  |
| B | B2 | S_c - S̄ = S_c(beta+q0(1-beta))>0 | symbolic | 通过 |  |
| B | B3 | 式(4.3) 两种写法相等：1-gamma N/(beta c S) = 1-c0(1-q0)S_c/(cS) | symbolic | 通过 |  |
| B | B4 | 平衡式下 c[beta+(1-beta)q]S = cS - c0 S̄（式 4.1、附录 A.6） | symbolic | 通过 |  |
| B | B5 | 平衡式即 beta c(1-q)S/N = gamma | symbolic | 通过 |  |
| B | B6 | 定理 3.2：c=c0、q=q_c(S)、I=eta 时 dS/dt = -(c0 eta/N)(S - S̄) | symbolic | 通过 |  |
| B | B7 | 式(3.6) 的 S(t) 满足上述线性方程且 S(t1)=S* | symbolic | 通过 |  |
| B | B8 | 式(3.7)：S(t1+Δt)=S_c | symbolic | 通过 |  |
| B | B9 | 式(3.9) 第一种写法 = q_c(S(t)) | symbolic | 通过 |  |
| B | B10 | 式(3.9) 第二种写法 = q_c(S(t)) | symbolic | 通过 |  |
| B | B11 | 式(3.11)：dq_c/dt = -(gamma eta/beta)(S-S̄)/S^2 | symbolic | 通过 |  |
| B | B12 | 式(3.14)：d²q_c/dt² = (gamma c0 eta²/(beta N))(S-S̄)(2S̄-S)/S³ | symbolic | 通过 |  |
| B | B13 | 式(3.13)：q_inf = q_c(2S̄) = 1 - 1/[2(1-beta)] | symbolic | 通过 |  |
| B | B14 | 式(3.13)：S(t_inf)=2S̄ | symbolic | 通过 |  |
| B | B15 | 推论 3.3：1-q_max = gamma N/(beta c0 S*) = (1-q0)S_c/S*（推论 4.8 证明） | symbolic | 通过 |  |
| B | B16 | 式(4.6)：q_c(S)=q_cap 时 c = c0(1-q0)S_c/((1-q_cap)S) | symbolic | 通过 |  |
| B | B17 | 式(4.7) 两种写法：beta c_min(1-q_cap)S*/N - gamma ∝ c_min(1-q_cap) - c0(1-q_max) | symbolic | 通过 |  |
| B | B18 | 式(4.9) 与式(4.3) 一致：q_c(S;alpha)=1-(1-q0)S_c/[S_c+alpha(S-S_c)] | symbolic | 通过 |  |
| B | B19 | 定理 4.3 证明：c_c(S;alpha)S - c0 S̄ = c0[S_c - S̄ + alpha(S-S_c)] | symbolic | 通过 |  |
| B | B20 | 式(4.10) 满足 dS/dt = -(eta/N)(c_c S - c0 S̄) 且 S(t1)=S* | symbolic | 通过 |  |
| B | B21 | 式(4.11)：S(t1+Δt(alpha))=S_c | symbolic | 通过 |  |
| B | B22 | 式(4.12)：alpha↓0 时 Δt(alpha) → N(S*-S_c)/(c0 eta(S_c-S̄)) | numeric | 通过 | 最大残差 0.0 |
| B | B23 | 式(4.11) 在 alpha=1 时等于式(3.7) | symbolic | 通过 |  |
| B | B24 | 定理 4.5(ii)：∂c_c(S;alpha)/∂alpha = c0(1-S_c/S)（S>S_c 时 >0） | symbolic | 通过 |  |
| B | B25 | 推论 4.4：c(S*;lo)=c_min | symbolic | 通过 |  |
| B | B26 | 推论 4.4：q(S*;hi)=q_cap | symbolic | 通过 |  |
| B | B27 | 推论 4.4：(hi-lo)·c0(S*-S_c)(1-q_cap) = c0(1-q0)S_c - c_min(1-q_cap)S*（非空⇔式 4.7） | symbolic | 通过 |  |
| C | C1 | beta c0 S̄/N = gamma(1-beta)（式 4.15 证明） | symbolic | 通过 |  |
| C | C2 | 式(4.15)：beta(eta/N)∫cS dt = beta(S*-S_c)+gamma eta(1-beta)Δt | symbolic | 通过 |  |
| C | C3 | 式(4.16)：(S*-S_c) - 控制期感染 = (1-beta)(S*-S_c-gamma eta Δt) | symbolic | 通过 |  |
| C | C4 | 式(4.16) 的独立路径：ΔS_q=(1-beta)(eta/N)∫cqS dt，平衡式下 cqS=cS-c0(1-q0)S_c | symbolic | 通过 |  |
| C | C5 | 定理 3.6：∫_{S_c}^{S*} S/(S-S̄)dS = S*-S_c+S̄ ln[(S*-S̄)/(S_c-S̄)] | numeric | 通过 | 最大残差 5.67e-41 |
| C | C6 | 定理 3.6 平台项 = beta(S*-S_c)+(1-beta)gamma eta Δt_q（与式 4.15 同形） | symbolic | 通过 |  |
| C | C7 | 前后常规阶段 beta c0 S I/N = kappa0·(-dS/dt)，kappa0=beta/(beta+q0(1-beta)) | symbolic | 通过 |  |
| C | C8 | 式(4.14) 左界 = ∫ dS/(c0(S-S̄)) 乘 N/eta | numeric | 通过 | 最大残差 1.64e-40 |
| C | C9 | 式(4.14) 右界 = ∫ dS/(c0(S_c-S̄)) 乘 N/eta | symbolic | 通过 |  |
| C | C10 | 命题 4.9：dItcum/dt = beta/(beta+(1-beta)q)·(-dS/dt) | symbolic | 通过 |  |
| C | C11 | 命题 4.9：系数 beta/(beta+(1-beta)q) 关于 q 递减（导数 = -beta(1-beta)/(...)^2） | symbolic | 通过 |  |
| C | C12 | 命题 7.1：S0-S(T) = I_cum + I_qcum + S_q(T) = I_cum + I_qcum/beta（S_q(0)=0） | symbolic | 通过 |  |
| D | D1 | 式(5.2)：(q-q0)/(1-q0) = 1 - c0 S_c/(cS) | symbolic | 通过 |  |
| D | D2 | 式(5.1)：成本率 × dt/dS = (N/eta) f，dt/dS = -N/(eta(cS-c0S̄)) | symbolic | 通过 |  |
| D | D3 | 式(5.4)：∂f/∂c × c³(cS-c0S̄)²/S 恰等于五次式（附录 A.7） | symbolic | 通过 |  |
| D | D4 | 五次式最高次系数为 w_c/c0² | symbolic | 通过 |  |
| D | D5 | 附录 A.8：∂f/∂c·D² = n'(c)D - S n(c) | symbolic | 通过 |  |
| D | D6 | 附录 A.8 左端点 c=c0S_c/S 处的量 | symbolic | 通过 |  |
| D | D7 | 附录 A.8 右端点 c=c0 处的量 | symbolic | 通过 |  |
| D | D8 | 式(5.6)：S_sw 是 S²-3S_cS+2S_cS̄ 的较大根 | symbolic | 通过 |  |
| D | D9 | S_sw/S_c = (3+√(9-8u))/2，u=S̄/S_c=(1-beta)(1-q0) | numeric | 通过 | 最大残差 7.03e-42 |
| D | D10 | 5.3 节：0<S̄<S_c ⇒ 2S_c<S_sw<3S_c（比值关于 u 严格递减，u=0 处 3、u=1 处 2） | symbolic | 通过 |  |
| D | D11 | 附录 A.8：较小根/S_c=(3-√(9-8u))/2 严格增、在 u=1 处为 1，故 u<1 时小于 1（较小根 < S_c） | symbolic | 通过 |  |
| D | D12 | 附录 A.9：f(S,c0(1-zx))/z² 的表达（一般权重） | symbolic | 通过 |  |
| D | D13 | 附录 A.9：(q-q0)/(1-q0)=z(1-x)/(1-zx) | symbolic | 通过 |  |
| D | D14 | z→0 的极限函数 = [w_c x²+w_q(1-x)²]/(c0(S_c-S̄)) | symbolic | 通过 |  |
| D | D15 | 极限函数严格凸，唯一最小点 x*=w_q/(w_c+w_q)（默认权重 2/3） | symbolic | 通过 | x*=[w_q/(w_c + w_q)] |
| D | D16 | 退出比例：接触降幅/(1-S_c/S) → w_q/(w_c+w_q)，隔离增幅/(1-S_c/S) → w_c/(w_c+w_q) | symbolic | 通过 |  |
| D | D17 | 两种归一化强度之比 → w_q/w_c（不是 c 与 q 原值之比）；图 7 的 y → r/(1+r)，r=w_q/w_c | symbolic | 通过 |  |
| D | D18 | 默认权重：2/3、1/3 | symbolic | 通过 |  |
| D | D19 | 附录 B.1 第一个部分分式 | symbolic | 通过 |  |
| D | D20 | 附录 B.1 第二个部分分式 | symbolic | 通过 |  |
| D | D21 | 式(B.1) = (N/(c0 eta))∫J_q 被积函数 | numeric | 通过 | 最大残差 2.51e-39 |
| D | D22 | 式(B.2) = (2N/(c0 eta))∫J 被积函数（默认权重 w_q=2） | numeric | 通过 | 最大残差 1.13e-37 |
| D | D23 | 式(A.5)：仅隔离控制 f(S,c0)=w_q(1-S_c/S)²/(c0(S-S̄)) | symbolic | 通过 |  |
| D | D24 | 式(B.3)：仅减少接触的 J（w_c=1） | numeric | 通过 | 最大残差 1.01e-37 |
| D | D25 | 仅减少接触时 f 不含 w_q、与 w_c 成正比，故式(B.3) 对应 w_c=1（B.1 开头的“取默认权重”须覆盖 B.2） | symbolic | 通过 |  |
| D | D26 | 式(3.25)：J 的归一化表达与 S 积分一致（eta=theta N） | symbolic | 通过 |  |
| D | D27 | 命题 5.2 证明：两项归一化强度同时为零 ⇔ c=c0 且 S=S_c | symbolic | 通过 | [{S: -N*gamma/(beta*c0*(q0 - 1)), c: c0}] |
| D | D28 | 注记 5.5：Δt 的被积函数 (N/eta)/(cS-c0S̄)；J+kappa Δt 的逐状态被积函数为 f+kappa/(cS-c0S̄) | symbolic | 通过 |  |
| S | S1 | 附录 A.3：∂F/∂S = rho1(1/S - 1/S_c) | symbolic | 通过 |  |
| S | S2 | 附录 A.3：∂F/∂c0 = -(rho1/c0) ln(S/S0) | symbolic | 通过 |  |
| S | S3 | 附录 A.3：∂F/∂beta | symbolic | 通过 |  |
| S | S4 | 附录 A.3：∂F/∂q0 | symbolic | 通过 |  |
| S | S5 | 附录 A.3：S̄<S*<S0 ⇒ (S0-S*)-S̄ln(S0/S*)>0（另有 ln x<x-1 的证明） | numeric | 通过 | 2000 点最小相对值 0.0388 |
| S | S6 | 式(A.2)：∂S*/∂eta = 1/[rho1(1/S*-1/S_c)] | symbolic | 通过 |  |
| S | S7 | 式(A.2)：∂S*/∂c0 = ln(S*/S0)/[c0(1/S*-1/S_c)] | symbolic | 通过 |  |
| S | S8 | 式(A.3)：∂S*/∂beta | symbolic | 通过 |  |
| S | S9 | 式(A.4)：∂S*/∂q0 | symbolic | 通过 |  |
| S | S10 | 附录 A.4：∂Δt/∂eta = -Δt/eta + N/(c0 eta (S*-S̄))·∂S*/∂eta | symbolic | 通过 |  |
| S | S11 | 式(A.6)：∂Itcum/∂eta 的表达 | symbolic | 通过 |  |
| S | S12 | 附录 A.4：beta S_c/(S_c-S̄) = beta/(beta+q0(1-beta)) | symbolic | 通过 |  |
| S | S13 | 附录 A.4：∂S_end/∂eta = -1/[rho1(1/S_end-1/S_c)] | symbolic | 通过 |  |
| S | S14 | S/(S-S̄) 关于 S 的导数 = -S̄/(S-S̄)² <0 | symbolic | 通过 |  |
| S | S15 | 附录 A.5：∂S̄/∂beta = -gamma N/(c0 beta²) | symbolic | 通过 |  |
| S | S16 | 附录 A.5：∂(S_c-S̄)/∂beta = -q0 S_c/beta | symbolic | 通过 |  |
| S | S17 | 附录 A.5：∂S̄/∂c0=-S̄/c0，∂S_c/∂c0=-S_c/c0，∂S_c/∂q0=S_c/(1-q0) | symbolic | 通过 |  |
| S | S18 | 式(3.24)：∂Δt/∂c0 的表达（代入 ∂S*/∂c0） | symbolic | 通过 |  |
| S | S19 | 式(3.23)：dI_max^0/dc0 = -(rho1/c0)ln(S_c/S0) | symbolic | 通过 |  |
| S | S20 | 补充 S2：∂B/∂c0 = 0，∂B/∂eta = 0 | symbolic | 通过 |  |
| S | S21 | 补充 S2：∂B/∂beta = -1/[(1-beta)(beta+q0(1-beta))] | symbolic | 通过 |  |
| S | S22 | 补充 S2：∂B/∂q0 = -1/[(1-q0)(beta+q0(1-beta))] | symbolic | 通过 |  |
| S | S23c0 | 补充 S2：∂A/∂c0 的表达 | symbolic | 通过 |  |
| S | S23beta | 补充 S2：∂A/∂beta 的表达 | symbolic | 通过 |  |
| S | S24 | 补充 S2.3：构造点满足触发与拐点条件，闭式与一般式一致，两点导数一正一负 | symbolic+example | 通过 | r=21/20: eta=3172.6, Imax=21583.8, dλ/dq0=0.6852; r=2: eta=78511.2, Imax=96922.3, dλ/dq0=-3.588 |
| S | S25 | 补充 S4 命题：∂s_end/∂N = -1/[N²(rho1/N)(1/s_end-1/s_c)] | symbolic | 通过 |  |
| F | F1 | 释放前后 S+S_q 不变（只从 S_q 转到 S；I、I_q、R 连续，总人口不变） | symbolic | 通过 |  |
| F | F2 | R_e(t2+) = 1 + xi S_q(t2-)/S_c | symbolic | 通过 |  |
| F | F3 | dI/dt(t2+) = gamma eta xi S_q(t2-)/S_c | symbolic | 通过 |  |
| F | F4 | xi=0 时 dI/dt(t2+)=0、R_e=1（恢复常规参数、不释放，回到定理 3.5 的情形） | symbolic | 通过 |  |
| F | F5 | （说明）启动前 S_q 增量 = (1-beta)q0/(beta+(1-beta)q0)·(S0-S*)；q0=0 且仅减少接触时 S_q(t2-)=S_q(0) | symbolic | 通过 |  |
| G | G1 | c0 - c0S_c/S = c0(1-S_c/S)>0（S>S_c），故 c_min<c0 ⇒ c^-(S)<c0 | symbolic | 通过 |  |
| G | G2 | c0(1-q0)S_c/((1-q_cap)S) - c0S_c/S = c0S_c(q_cap-q0)/((1-q_cap)S)，故 q_cap>q0 ⇒ c^+(S)>c0S_c/S | symbolic | 通过 |  |
| G | G3 | c0∈[c^-,c^+] ⇔ S ≤ (1-q0)S_c/(1-q_cap)；该界 / S_c = (1-q0)/(1-q_cap) >1 ⇔ q_cap>q0 | symbolic | 通过 |  |
| G | G4 | c0S_c/S ≥ c_min ⇔ S ≤ c0S_c/c_min；该界 >S_c ⇔ c_min<c0 | symbolic | 通过 |  |
| G | G5 | （算例 N）c_min/c0=0.9、q_cap=0.6 满足 c_min<c0、q_cap>q0，但式(4.7)不成立：两个不等式不蕴含整段可行 | example | 通过 | S*/S_c=4.0440, q_max=0.7565, c_min(1-q_cap)=3.600 > c0(1-q_max)=2.435 |
| G | G6 | （算例 N）c_min/c0=0.9、q_cap=0.8：S<S_sw 时约束最小点落在 c=c_min 上——两种措施都强于常规，但不在约束区间内部 | example | 通过 | S_sw/S_c=2.2654; S/S_c=1.2: 无约束 c*/c0=0.8994; 约束 c*/c0=0.9000, q*=0.0882; S/S_c=1.6: 无约束 c*/c0=0.8083; 约束 c*/c0=0.9000, q*=0.3162; S/S_c=2.0: 无约束 c*/c0=0.8447; 约束 c*/c0=0.9000, q*=0.4529 |
| R | R-基准 | 基准参数：S*/S_c、S_sw/S_c、q_max、Δt（仅隔离、仅减少接触）、beta(S0-S_c) 与稿件舍入值一致 | example | 通过 | SsSc=4.043996; SswSc=2.265369; qmax=0.7564933; dtq=5.902556; dtc=36.26077; lb=90.96017 |
| R | R-基准-lb | 基准参数：退出下界 beta(S0-S_c) 占表 2 各控制总累计新增感染（计至清零）的比例 | example | 通过 | 仅减少接触:0.145; alpha05:0.281; 仅隔离:0.318; 成本最优:0.297 |
| R | R-西安 | 西安参数：S*/S_c、S_sw/S_c、q_max、Δt（仅隔离、仅减少接触）、beta(S0-S_c) 与稿件舍入值一致 | example | 通过 | SsSc=4.377906; SswSc=2.548251; qmax=0.8453599; dtq=85.07108; dtc=308.7939; lb=1526293.0 |
| R | R-西安-lb | 西安参数：退出下界 beta(S0-S_c) 占表 2 各控制总累计新增感染（计至清零）的比例 | example | 通过 | 仅减少接触:0.396; alpha05:0.578; 仅隔离:0.642; 成本最优:0.602 |
