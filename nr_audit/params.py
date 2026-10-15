"""无回流模型 (2.1) 的参数、初值与能力约束代表点。

复制来源：research/return-effects 分支提交 bb52b96（R7-3，G2 通过）的 r7_return/params.py
（blob b5467aae，与本分支 91123ea 中的同名文件逐字节相同）。改动：删去回流专用的
L_bound（命题 R2 的下界）与 omega_from_stay；增加常规轨迹的派生量（a、κ0、λ_F、ρ1、β1^0、β2^0）、
能力约束 Capacity 与两个能力代表点。数值本身未改。

取值来源（逐项见 results/source_manifest.json，由 tests/test_sources.py 核对）：
- 基准：joint_control/threshold_control_reproducible_release_20261002/numerics/inputs/
  baseline_parameters.json（原 joint_extra 的输入），η = 0.05N = 38.15。
- 西安：reproducibility/results/20261003_release_final/xian/reference.json 的 parameters 与
  I0_abs = 0.00100659188867187（未取整拟合值；reproducibility/manuscript_audit_notes.md），
  S0 = N - I0，η = 0.002N = 26326（设计情景）。
- 两组算例 S_q(0) = I_q(0) = R(0) = 0；权重默认 w_c = 1、w_q = 2（稿件式 (2.13) 之后）。
- 能力代表点：稿件图 6 图注与 joint_extra/capacity.json 的 point 字段。

两套归一化（不得混用，变量名写明属于哪一套）：
- 按 N 归一（完整方程，稿件命题 prop:scaling 的记号）：后缀 `_N`，
  如 s_N = S/N、i_N = I/N、sc_N = S_c/N、sbar_N = S̄/N、eta_N = θ = η/N。
- 按 S_c 归一（控制律与 S 坐标求积）：以 `z` 开头，
  如 z = S/S_c、z_star = S*/S_c、z_bar = S̄/S_c = (1-β)(1-q0)；控制律 x(z) = c/c0。
人数以人计，时间以天计。
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Params:
    """一组模型参数与初值。"""
    name: str
    N: float
    S0: float
    I0: float
    beta: float
    gamma: float
    delta_q: float
    c0: float
    q0: float
    eta: float
    Sq0: float = 0.0
    Iq0: float = 0.0
    R0: float = 0.0
    wc: float = 1.0      # 二次干预强度成本的默认权重 w_c
    wq: float = 2.0      # 默认权重 w_q

    # ---------- 人数尺度的派生量 ----------
    @property
    def S_c(self):
        """常规传播临界值 S_c = γN / (βc0(1-q0))（式 2.2）。"""
        return self.gamma * self.N / (self.beta * self.c0 * (1.0 - self.q0))

    @property
    def S_bar(self):
        """S̄ = (1-β)γN/(βc0)（式 3.4），S̄/S_c = (1-β)(1-q0)。"""
        return self.gamma * self.N * (1.0 - self.beta) / (self.beta * self.c0)

    @property
    def a(self):
        """常规控制下 S 的总移出系数 β + (1-β)q0。"""
        return self.beta + (1.0 - self.beta) * self.q0

    @property
    def kappa0(self):
        """常规轨迹 dI/dS = -κ0(1 - S_c/S)，κ0 = β2^0/β1^0·S_c = β(1-q0)/(β+(1-β)q0)。"""
        return self.beta * (1.0 - self.q0) / self.a

    @property
    def lamF(self):
        """常规控制下新增感染占 S 移出的比例 β/(β+(1-β)q0)。"""
        return self.beta / self.a

    @property
    def beta1_0(self):
        """β1^0 = c0[β+q0(1-β)]/N（式 2.3）。"""
        return self.c0 * self.a / self.N

    @property
    def beta2_0(self):
        """β2^0 = βc0(1-q0)/N（式 2.3）。"""
        return self.beta * self.c0 * (1.0 - self.q0) / self.N

    @property
    def rho1(self):
        """ρ1 = γ/β1^0 = κ0·S_c（式 2.3）。"""
        return self.gamma / self.beta1_0

    @property
    def S_tot0(self):
        """初始易感者总数 S0 + S_q(0)（无回流时 S + S_q 的减少即累计新增感染）。"""
        return self.S0 + self.Sq0

    # ---------- 第一套：按 N 归一 ----------
    @property
    def sc_N(self):
        return self.gamma / (self.beta * self.c0 * (1.0 - self.q0))

    @property
    def sbar_N(self):
        return self.gamma * (1.0 - self.beta) / (self.beta * self.c0)

    @property
    def s0_N(self):
        return self.S0 / self.N

    @property
    def i0_N(self):
        return self.I0 / self.N

    @property
    def eta_N(self):
        """θ = η/N。"""
        return self.eta / self.N

    # ---------- 第二套：按 S_c 归一 ----------
    @property
    def z_bar(self):
        """z̄ = S̄/S_c = (1-β)(1-q0)。"""
        return (1.0 - self.beta) * (1.0 - self.q0)

    @property
    def z0(self):
        return self.S0 / self.S_c

    def with_(self, **kw):
        """返回改动若干字段后的副本（例如改权重或 I0）。"""
        return replace(self, **kw)


@dataclass(frozen=True)
class Capacity:
    """能力约束：接触率不低于 c_min（人数尺度的接触率，d^-1），隔离比例不超过 q_cap。
    要求 0 ≤ c_min ≤ c0、q0 ≤ q_cap < 1（第 4.1 节）。"""
    c_min: float
    q_cap: float

    def check(self, P):
        if not (0.0 <= self.c_min <= P.c0):
            raise ValueError(f'c_min = {self.c_min} 不在 [0, c0] 内')
        if not (P.q0 <= self.q_cap < 1.0):
            raise ValueError(f'q_cap = {self.q_cap} 不在 [q0, 1) 内')
        return self


# 基准参数：η = 0.05N
BASE = Params(name='base', N=763.0, S0=762.0, I0=1.0, beta=0.155, gamma=0.3504,
              delta_q=0.3504, c0=10.0, q0=0.01526, eta=0.05 * 763.0)

# 西安参数（I0 为未取整拟合值）：η = 0.002N = 26326（设计情景）
XIAN_I0 = 0.00100659188867187
XIAN = Params(name='xian', N=13163000.0, S0=13163000.0 - XIAN_I0, I0=XIAN_I0, beta=0.1498,
              gamma=0.2953, delta_q=0.3531, c0=12.8872, q0=0.3230, eta=0.002 * 13163000.0)

CASES = {'base': BASE, 'xian': XIAN}

# 能力约束代表点（稿件图 6 图注：基准 c_min/c0 = 0.5、q_cap = 0.6；西安 c_min/c0 = 0.5、q_cap = 0.75）
REP_CAPACITY = {'base': Capacity(c_min=0.5 * BASE.c0, q_cap=0.6),
                'xian': Capacity(c_min=0.5 * XIAN.c0, q_cap=0.75)}
