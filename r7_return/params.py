"""R7 回流计算的参数。

取值来源：
- 基准与西安参数：AGENTS.md 第 8 节。
- 西安 I0：reproducibility/manuscript_audit_notes.md 中的未取整拟合值 0.00100659188867187，
  S0 = N - I0（与 reproducibility/results/20261003_release_final/xian/reference.json 一致）。
- 两组算例 S_q(0) = I_q(0) = R(0) = 0。

两套归一化（不得混用，变量名写明属于哪一套）：
- 按 N 归一（完整方程，稿件命题 prop:scaling 的记号）：后缀 `_N`，
  如 s_N = S/N、i_N = I/N、sc_N = S_c/N、sbar_N = S̄/N。
- 按 S_c 归一（分配函数与 S 坐标求积）：以 `z` 开头，
  如 z = S/S_c、z_star = S*/S_c、z_bar = S̄/S_c = (1-β)(1-q0)；控制律 x(z) = c/c0。
"""
from dataclasses import dataclass, replace
import math


@dataclass(frozen=True)
class Params:
    """一组模型参数。人数量（N、S0、I0、η 等）以人计，时间以天计。"""
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
        """常规传播临界值 S_c = γN / (βc0(1-q0))。"""
        return self.gamma * self.N / (self.beta * self.c0 * (1.0 - self.q0))

    @property
    def S_bar(self):
        """S̄ = γN(1-β)/(βc0)，满足 S̄/S_c = (1-β)(1-q0)。"""
        return self.gamma * self.N * (1.0 - self.beta) / (self.beta * self.c0)

    @property
    def U0(self):
        """初始总易感者 U(0) = S0 + S_q(0)。"""
        return self.S0 + self.Sq0

    @property
    def L_bound(self):
        """命题 R2 的下界 L = U(0) - S_c（人）。"""
        return self.U0 - self.S_c

    # ---------- 第一套：按 N 归一 ----------
    @property
    def sc_N(self):
        """s_c = S_c/N = γ/(βc0(1-q0))。"""
        return self.gamma / (self.beta * self.c0 * (1.0 - self.q0))

    @property
    def sbar_N(self):
        """s̄ = S̄/N。"""
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
        """z0 = S0/S_c。"""
        return self.S0 / self.S_c

    def with_(self, **kw):
        """返回改动若干字段后的副本（例如改权重）。"""
        return replace(self, **kw)


# 基准参数（AGENTS.md 第 8 节）：η = 0.05N
BASE = Params(name='base', N=763.0, S0=762.0, I0=1.0, beta=0.155, gamma=0.3504,
              delta_q=0.3504, c0=10.0, q0=0.01526, eta=0.05 * 763.0)

# 西安参数（AGENTS.md 第 8 节；I0 为未取整拟合值）：η = 0.002N = 26326（设计情景）
XIAN_I0 = 0.00100659188867187
XIAN = Params(name='xian', N=13163000.0, S0=13163000.0 - XIAN_I0, I0=XIAN_I0, beta=0.1498,
              gamma=0.2953, delta_q=0.3531, c0=12.8872, q0=0.3230, eta=0.002 * 13163000.0)

CASES = {'base': BASE, 'xian': XIAN}


def omega_from_stay(mean_stay_days):
    """平均停留 1/ω（天）换算为回流率 ω；mean_stay=inf 对应 ω=0。"""
    return 0.0 if math.isinf(mean_stay_days) else 1.0 / mean_stay_days
