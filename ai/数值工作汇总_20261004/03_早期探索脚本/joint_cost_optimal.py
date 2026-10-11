"""
联合阈值控制：平台类内成本最优分配的逐状态全局求解与正向验证。

理论依据（第6.4节定理6.9）：以 S 为自变量后，
    J + kappa*Δt = N/(eta*c0) * ∫_1^{s*} [wc(1-x)^2 + wq(1-1/(x s))^2 + kappa] / (x s - sbar) ds,
其中 s = S/Sc, x = c/c0, sbar = (1-beta)(1-q0)。各状态互不耦合，
因此在每个 s 上做一元全局最小化即得平台类内的全局最优；无需配点法或打靶法。
kappa = 0 为成本最优；kappa > 0 偏向缩短控制期；kappa < 0 偏向减少隔离易感者（效率前沿）。
"""
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.integrate import solve_ivp, cumulative_trapezoid, simpson
from scipy.interpolate import interp1d


# ---------------- 基本量 ----------------
def basic_quantities(p):
    N, beta, gam, c0, q0 = p['N'], p['beta'], p['gamma'], p['c0'], p['q0']
    Sc = gam * N / (beta * c0 * (1 - q0))
    Sbar = gam * N * (1 - beta) / (beta * c0)
    # 常规阶段首次积分确定首次触及 I=eta 时的 S*（取 S*>Sc 的根）
    b1 = c0 * (beta + q0 * (1 - beta)) / N
    b2 = beta * c0 * (1 - q0) / N
    rho = gam / b1
    C0 = p['I0'] + b2 / b1 * p['S0'] - rho * np.log(p['S0'])
    g = lambda S: p['eta'] + b2 / b1 * S - rho * np.log(S) - C0
    Sstar = brentq(g, Sc, p['S0'])
    return Sc, Sbar, Sstar


def x_bounds(s, p):
    """允许区间 [x_lo, x_hi]，含能力限制 c >= cmin, q <= qcap。"""
    x_lo = max(p.get('cmin', 0.0) / p['c0'], 1.0 / s)
    qcap = p.get('qcap', 1.0)
    x_hi = 1.0 if qcap >= 1.0 else min(1.0, (1 - p['q0']) / ((1 - qcap) * s))
    return x_lo, x_hi


def integrand(x, s, sbar, wc, wq, kappa):
    return (wc * (1 - x) ** 2 + wq * (1 - 1 / (x * s)) ** 2 + kappa) / (x * s - sbar)


def pointwise_global_min(s, p, sbar, wc, wq, kappa, ngrid=2001):
    """在 [x_lo, x_hi] 上求一元全局最小：细网格找全部局部极小 + 有界加密 + 端点比较。
    返回 (x*, 局部极小个数)。"""
    x_lo, x_hi = x_bounds(s, p)
    if x_hi - x_lo < 1e-14:
        return x_lo, 1
    xs = np.linspace(x_lo, x_hi, ngrid)
    v = integrand(xs, s, sbar, wc, wq, kappa)
    cand = [x_lo, x_hi]
    nloc = 0
    for k in range(len(xs)):
        left = v[k - 1] if k > 0 else np.inf
        right = v[k + 1] if k < len(xs) - 1 else np.inf
        if v[k] <= left and v[k] <= right:
            nloc += 1
            a, b = xs[max(k - 1, 0)], xs[min(k + 1, len(xs) - 1)]
            if b > a:
                r = minimize_scalar(lambda x: integrand(x, s, sbar, wc, wq, kappa),
                                    bounds=(a, b), method='bounded',
                                    options={'xatol': 1e-13})
                cand.append(r.x)
    cand = np.array(cand)
    vals = integrand(cand, s, sbar, wc, wq, kappa)
    return cand[np.argmin(vals)], nloc


# ---------------- 求解 ----------------
def solve_allocation(p, wc=1.0, wq=2.0, kappa=0.0, ns=4001, policy='optimal'):
    """policy: 'optimal'（逐状态全局最优）, 'q_only'（x=1）, 'c_only'（x=1/s）。"""
    Sc, Sbar, Sstar = basic_quantities(p)
    sbar, sstar = Sbar / Sc, Sstar / Sc
    s = np.linspace(1.0, sstar, ns)
    x = np.empty_like(s)
    nloc = np.zeros(ns, dtype=int)
    for i, si in enumerate(s):
        if policy == 'q_only':
            x[i] = 1.0
        elif policy == 'c_only':
            x[i] = 1.0 / si
        else:
            x[i], nloc[i] = pointwise_global_min(si, p, sbar, wc, wq, kappa)
    pref = p['N'] / (p['eta'] * p['c0'])
    cost_dens = (wc * (1 - x) ** 2 + wq * (1 - 1 / (x * s)) ** 2) / (x * s - sbar)
    time_dens = 1.0 / (x * s - sbar)
    J = pref * simpson(cost_dens, x=s)
    dT = pref * simpson(time_dens, x=s)
    # 时间映射：t - t1 = pref * ∫_s^{s*} time_dens
    tau = pref * (cumulative_trapezoid(time_dens[::-1], -s[::-1], initial=0.0))[::-1]
    c = p['c0'] * x
    q = 1 - (1 - p['q0']) / (x * s)
    beta, gam, eta = p['beta'], p['gamma'], p['eta']
    infections = beta * (Sstar - Sc) + gam * eta * (1 - beta) * dT
    Sq_new = (1 - beta) * (Sstar - Sc - gam * eta * dT)
    return dict(Sc=Sc, Sbar=Sbar, Sstar=Sstar, s=s, x=x, c=c, q=q, tau=tau,
                J=J, dT=dT, infections=infections, Sq_new=Sq_new,
                max_local_minima=nloc.max(), s_sw=(3 + np.sqrt(9 - 8 * sbar)) / 2)


# ---------------- 正向验证（状态反馈） ----------------
def forward_check(p, sol, wc=1.0, wq=2.0):
    N, beta, gam, dq, c0, q0, eta = (p[k] for k in ['N', 'beta', 'gamma', 'delta_q', 'c0', 'q0', 'eta'])
    Sc = sol['Sc']
    x_of_s = interp1d(sol['s'], sol['x'], kind='linear', fill_value='extrapolate')

    def rhs(t, y, mode):
        S, I, Sq, Iq, R, Jc = y
        if mode == 'base':
            c, q = c0, q0
        else:  # 平台期：状态反馈 c = c0 x*(S/Sc), q 由平衡条件确定
            c = c0 * float(x_of_s(S / Sc))
            q = 1 - (1 - q0) * Sc * c0 / (c * S)
        inc = c * S * I / N
        uc, uq = 1 - c / c0, (q - q0) / (1 - q0)
        return [-(beta + (1 - beta) * q) * inc, beta * (1 - q) * inc - gam * I,
                (1 - beta) * q * inc, beta * q * inc - dq * Iq, gam * I + dq * Iq,
                (wc * uc ** 2 + wq * uq ** 2) if mode == 'plat' else 0.0]

    hit = lambda t, y, m: y[1] - eta; hit.terminal = True; hit.direction = 1
    y0 = [p['S0'], p['I0'], 0, 0, 0, 0]
    s1 = solve_ivp(rhs, [0, 1e4], y0, args=('base',), events=hit, rtol=1e-11, atol=1e-10)
    t1, y1 = s1.t_events[0][0], s1.y_events[0][0].copy(); y1[1] = eta
    ex = lambda t, y, m: y[0] - Sc; ex.terminal = True; ex.direction = -1
    s2 = solve_ivp(rhs, [t1, t1 + 1e5], y1, args=('plat',), events=ex,
                   rtol=1e-11, atol=1e-10, max_step=sol['dT'] / 2000)
    t2 = s2.t_events[0][0]
    return dict(t1=t1, dT_sim=t2 - t1, J_sim=s2.y_events[0][0][5],
                I_drift=np.max(np.abs(s2.y[1] - eta)) / eta)


# ---------------- 示例 ----------------
if __name__ == '__main__':
    cases = {
        '基准 N=763, eta=0.05N': dict(N=763, S0=762, I0=1, beta=0.155, gamma=0.3504,
                                      delta_q=0.3504, c0=10, q0=0.01526, eta=0.05 * 763),
        '西安 theta=0.002': dict(N=13163000, S0=13163000 - 1.00663e-3, I0=1.00663e-3,
                                beta=0.1498, gamma=0.2953, delta_q=0.3531, c0=12.8872,
                                q0=0.3230, eta=0.002 * 13163000),
    }
    for name, p in cases.items():
        print('=' * 60, '\n', name)
        for pol in ['optimal', 'q_only', 'c_only']:
            sol = solve_allocation(p, policy=pol)
            print(f'  {pol:8s}: J={sol["J"]:.6f}, Δt={sol["dT"]:.4f} d, '
                  f'控制期新增感染={sol["infections"]:.6g}, 新增隔离易感者={sol["Sq_new"]:.6g}')
        sol = solve_allocation(p)
        mixed = np.where(sol['x'][1:] < 1 - 1e-6)[0] + 1          # 排除 s=1 处的退化区间
        sw = sol['s'][mixed[-1] + 1] if len(mixed) and mixed[-1] + 1 < len(sol['s']) else np.nan
        print(f'  切换阈值公式 s_sw={sol["s_sw"]:.4f}; 数值上此后仅隔离的 s={sw:.4f}; '
              f's*={sol["Sstar"]/sol["Sc"]:.4f}; 最多局部极小个数={sol["max_local_minima"]}')
        chk = forward_check(p, sol)
        print(f'  正向验证: Δt_sim={chk["dT_sim"]:.6f} (误差 {abs(chk["dT_sim"]-sol["dT"]):.1e}), '
              f'J_sim={chk["J_sim"]:.6f} (误差 {abs(chk["J_sim"]-sol["J"]):.1e}), '
              f'I 相对漂移={chk["I_drift"]:.1e}')
    # 权重比敏感性（基准参数）
    p = cases['基准 N=763, eta=0.05N']
    print('=' * 60, '\n 权重比敏感性（基准参数）')
    for wq in [0.5, 1, 2, 5]:
        sol = solve_allocation(p, wc=1, wq=wq)
        dx = np.abs(np.diff(sol['x'])); k = np.argmax(dx)
        print(f'  r={wq}: J_min={sol["J"]:.5f}, Δt={sol["dT"]:.4f}, '
              f'最多局部极小={sol["max_local_minima"]}, x* 最大相邻跳跃={dx[k]:.3f} (位于 s≈{sol["s"][k]:.3f})')
