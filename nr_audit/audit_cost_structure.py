"""NEW-4d：成本结构定理入稿的派生核验与新增数字（第 5 章定理、截断推论、权重单调性命题，补充 S5 的 r̂ 命题）。

依据 ai/成本最优/ 专稿与 ai/NEW_4d_cost_structure_plan.md。只调用本模块已有的逐状态求解器（allocation.py，
定理 5.1 的有限比较）与状态积分（state_integrals.py），不重算 ODE、不改旧括区与旧表值。
符号部分只核对代数恒等式与系数下界（证明中的存在性与量词论证见附录 A）；数值部分是定理结论的抽查，不代替证明。

记号（与附录 A 新小节一致）：ζ = S/S_c，p = cS/(c0 S_c) = xζ ∈ [1, ζ]，b = S̄/S_c，r = w_q/w_c，
E = (p-b)^2 ∂G/∂p，G(p; ζ) = [(1-p/ζ)^2 + r(1-1/p)^2]/(p-b)。

运行：python nr_audit/audit_cost_structure.py（约数分钟）。输出 results/new4d_cost_structure.json 与 .md。
"""
import json
import math

import numpy as np
import sympy as sp

import allocation as AL
import params as PR
import state_integrals as SI
from audit_common import RESULTS, dump


# ---------------------------------------------------------------- 闭式
def r_cont(b):
    return 16.0 / (b + math.sqrt(b * b - 8 * b + 8)) ** 2


def z_sw(b):
    return (3 + math.sqrt(9 - 8 * b)) / 2


def r_hat(b):
    t = z_sw(b)
    return (t / (t - 1)) ** 2


# ---------------------------------------------------------------- 符号核对
def symbolic_checks():
    p, z, b, r, s, w = sp.symbols('p zeta b r s w', positive=True)
    G = ((1 - p / z) ** 2 + r * (1 - 1 / p) ** 2) / (p - b)
    phi = (p - 1) * (3 * p - p ** 2 - 2 * b) / p ** 3
    psi = (2 * p - 3) / p ** 4
    E = (p ** 2 - 2 * b * p) / z ** 2 + 2 * b / z - 1 + r * phi
    X = p ** 3 - 6 * p ** 2 + 6 * p + 2 * b * (3 * p - 4)
    out = {}
    out['E_is_numerator_of_G_p'] = sp.simplify(sp.diff(G, p) * (p - b) ** 2 - E) == 0
    out['E_p_formula'] = sp.simplify(sp.diff(E, p) - 2 * (p - b) * (1 / z ** 2 - r * psi)) == 0
    out['E_zeta_formula'] = sp.simplify(sp.diff(E, z) + 2 * ((p - b) ** 2 + b * (z - b)) / z ** 3) == 0
    out['phi_prime_formula'] = sp.simplify(sp.diff(phi, p) + 2 * (2 * p - 3) * (p - b) / p ** 4) == 0
    out['E_at_p1'] = sp.simplify(E.subs(p, 1) + (z - 1) * (z + 1 - 2 * b) / z ** 2) == 0
    out['E_at_p_eq_zeta'] = sp.simplify(E.subs(z, p) - r * phi) == 0
    # 折叠：E = 0 且 1/ζ = sqrt(rψ) ⇒ -p^3 E = F1
    F1 = r * X - 2 * sp.sqrt(r) * b * p * sp.sqrt(2 * p - 3) + p ** 3
    out['fold_reduces_to_F1'] = sp.simplify(sp.expand(-p ** 3 * E.subs(z, 1 / sp.sqrt(r * psi))) - sp.expand(F1)) == 0
    # s = sqrt(r_cont) 处 F1 = (w-1)^2 Q / (8(s-1))，b = (s^2-2)/(s(s-1))，p = (w^2+3)/2
    bs = (s ** 2 - 2) / (s * (s - 1))
    F1s = (s ** 2 * X - 2 * s * b * p * w + p ** 3).subs(p, (w ** 2 + 3) / 2).subs(b, bs)
    Q = ((s - 1) * (s ** 2 + 1) * w ** 3 * (w + 2) + 12 * (s - 1) * w ** 2
         - 2 * (s ** 3 + 3 * s ** 2 - 11 * s + 3) * w + (9 * s ** 2 + 11 * s - s ** 3 - 27))
    out['F1_at_rcont_factorizes'] = sp.simplify(sp.together(F1s) - (w - 1) ** 2 * Q / (8 * (s - 1))) == 0
    bb = sp.symbols('bb', positive=True)
    out['s_rcont_root'] = sp.simplify(((1 - bb) * (4 / (bb + sp.sqrt(bb ** 2 - 8 * bb + 8))) ** 2
                                       + bb * 4 / (bb + sp.sqrt(bb ** 2 - 8 * bb + 8)) - 2)) == 0
    # Q 的系数下界：s ∈ (√2, 2)
    c0 = 9 * s ** 2 + 11 * s - s ** 3 - 27
    c1 = -2 * (s ** 3 + 3 * s ** 2 - 11 * s + 3)
    out['Q_const_at_sqrt2'] = sp.simplify(c0.subs(s, sp.sqrt(2)) - 9 * (sp.sqrt(2) - 1)) == 0
    ss = np.linspace(math.sqrt(2), 2, 20001)
    f0 = sp.lambdify(s, c0)(ss)
    f1 = sp.lambdify(s, c1)(ss)
    out['Q_const_increasing'] = bool(np.all(np.diff(f0) > 0))
    out['Q_lin_decreasing_min_minus2'] = bool(np.all(np.diff(f1) < 0) and abs(f1[-1] + 2) < 1e-12)
    out['Q_quadratic_lower_bound_discriminant'] = float(4 - 4 * 9 * (math.sqrt(2) - 1) * 12 * (math.sqrt(2) - 1))
    WW, SS = np.meshgrid(np.linspace(0, math.sqrt(3), 801), ss[::40])
    out['Q_min_on_box'] = float(sp.lambdify((w, s), Q)(WW, SS).min())
    # r_cont < 27/(9-8b)，r_cont < r̂：在 b 网格上数值抽查（文字证明见附录 A 与补充 S5）
    bgrid = np.linspace(1e-6, 1 - 1e-6, 200001)
    rc = 16 / (bgrid + np.sqrt(bgrid ** 2 - 8 * bgrid + 8)) ** 2
    t = (3 + np.sqrt(9 - 8 * bgrid)) / 2
    out['min_rinf_minus_rcont'] = float((27 / (9 - 8 * bgrid) - rc).min())
    out['min_rhat_minus_rcont'] = float(((t / (t - 1)) ** 2 - rc).min())
    out['rcont_range'] = [float(rc.min()), float(rc.max())]
    out['rcont_increasing_in_b'] = bool(np.all(np.diff(rc) > 0))
    return out


# ---------------------------------------------------------------- 单峰性抽查：E(·, ζ) 在 (1, ζ) 内的变号次数
def E_num(p, z, b, r):
    return (p * p - 2 * b * p) / z ** 2 + 2 * b / z - 1 + r * (p - 1) * (3 * p - p * p - 2 * b) / p ** 3


def sign_changes(b, r, z, n=4001):
    """E(·, ζ) 在 [1, ζ] 上的变号次数；两端用精确式 E(1, ζ) < 0 与 E(ζ, ζ) = rφ(ζ)，
    避免内部最小点贴近仅隔离端点（ζ 稍小于 ζ_sw）时网格漏掉最后一次变号。"""
    p = np.linspace(1, z, n)
    e = E_num(p, z, b, r)
    e[0] = -(z - 1) * (z + 1 - 2 * b) / z ** 2
    e[-1] = r * (z - 1) * (3 * z - z * z - 2 * b) / z ** 3
    e = e[e != 0]
    return int(np.sum(np.sign(e[1:]) != np.sign(e[:-1])))


def unimodality_scan(b, r, zs):
    zsw = z_sw(b)
    bad = []
    for z in zs:
        if abs(z / zsw - 1) < 1e-6:          # E(ζ_sw, ζ_sw) = 0，端点符号未定，跳过
            continue
        nc = sign_changes(b, r, z)
        expect = 1 if z < zsw * (1 - 1e-9) else 0
        if nc != expect:
            bad.append((float(z), nc))
    return bad


# ---------------------------------------------------------------- 主程序
def main():
    out = dict(script='nr_audit/audit_cost_structure.py', cases={})
    out['symbolic'] = symbolic_checks()
    wb = json.loads((RESULTS / 'weight_brackets.json').read_text(encoding='utf-8'))
    zgrid = lambda zmax, n: np.linspace(1.0, zmax, n)[1:]
    for case, P in PR.CASES.items():
        b = P.z_bar
        start = SI.start_state(P)
        zstar = start['z_star']
        rc, rh = r_cont(b), r_hat(b)
        uc = b + math.sqrt(b * b - 8 * b + 8)
        br = {(x['from_'], x['to']): (x['lo'], x['hi'])
              for ch in wb['cases'][case]['changes'] for x in ch['brackets']}
        o = dict(b=b, z_sw=z_sw(b), z_star=zstar, r_cont=rc, r_hat=rh, cusp_state=uc,
                 bracket_A_Ap=br[('A', "A'")], bracket_Ap_B=br[("A'", 'B')],
                 r_cont_in_bracket=br[('A', "A'")][0] <= rc <= br[('A', "A'")][1],
                 r_hat_in_bracket=br[("A'", 'B')][0] <= rh <= br[("A'", 'B')][1])
        # 定理：r ≤ r_cont 时单峰（含边界 r = r_cont）；r 稍大于 r_cont 时折叠出现（尖点处 ζ = U_c）
        zs = np.concatenate([np.linspace(1.0005, 6.0, 1500), np.linspace(uc - 0.02, uc + 0.02, 400)])
        o['unimodal_violations'] = {f'{r:.6g}': unimodality_scan(b, r, zs)
                                    for r in (0.25, 0.5, 1.0, 2.0, rc * (1 - 1e-6), rc)}
        o['fold_above_rcont'] = max(sign_changes(b, rc * 1.01, z) for z in np.linspace(uc - 0.05, z_sw(b), 400))
        # r̂：在 ζ_sw 稍上方，仅隔离控制是否为全局最优（官方求解器）
        zt = z_sw(b) * (1 + 1e-7)
        o['q_only_global_just_above_zsw'] = {
            f'{r:.6g}': AL.argmin_state(zt, b, 1.0, r)[2]['label'] == 'hi'
            for r in (rh * (1 - 1e-4), rh * (1 + 1e-4))}
        # 截断推论：能力代表点上，截断与有限比较一致
        cap = PR.REP_CAPACITY[case]
        xmin, h = AL.cap_factors(P, cap)
        clip = {}
        for r in (0.5, 1.0, 2.0, rc):
            dmax = 0.0
            for z in zgrid(zstar, 1500):
                lo, hi, _, _ = AL.x_bounds_raw(float(z), xmin, h)
                xf = AL.argmin_state(float(z), b, 1.0, r)[0]
                xc = AL.argmin_state(float(z), b, 1.0, r, x_min=xmin, h=h)[0]
                dmax = max(dmax, abs(min(hi, max(lo, xf)) - xc))
            clip[f'{r:.6g}'] = dmax
        o['clip_max_abs_diff_x'] = clip
        # 权重单调性：x*(z; r) 随 r 不增（含能力约束）；q* 随 z 不减（即 u = xz 不减）
        rs = np.geomspace(0.2, 20, 31)
        zz = zgrid(zstar, 600)
        mono = {}
        for label, kw in (('free', {}), ('cap', dict(x_min=xmin, h=h))):
            X = np.array([[AL.argmin_state(float(z), b, 1.0, float(r), **kw)[0] for z in zz] for r in rs])
            U = X * zz[None, :]
            mono[label] = dict(max_increase_in_r=float(np.max(np.diff(X, axis=0))),
                               max_decrease_of_u_in_z=float(np.max(-np.diff(U, axis=1))))
        o['monotonicity'] = mono
        # r = 1 时与仅隔离控制的成本差（正文 6.5 节一句）
        m_opt = SI.arc_integrals(SI.Policy(P, 'opt', wc=1.0, wq=1.0))
        m_q = SI.arc_integrals(SI.Policy(P, 'q_only', wc=1.0, wq=1.0))
        o['r1'] = dict(J_min=float(m_opt['J']), J_q_only=float(m_q['J']),
                       gap_percent=float(100 * (1 - m_opt['J'] / m_q['J'])),
                       dt_min=float(m_opt['dt']), dt_q_only=float(m_q['dt']))
        out['cases'][case] = o
        print(case, json.dumps({k: o[k] for k in ('r_cont', 'r_hat', 'r_cont_in_bracket', 'r_hat_in_bracket',
                                                  'fold_above_rcont', 'q_only_global_just_above_zsw',
                                                  'clip_max_abs_diff_x', 'monotonicity', 'r1')},
                                ensure_ascii=False, default=float))
    sym = out['symbolic']
    out['all_symbolic_ok'] = all(v for k, v in sym.items() if isinstance(v, bool))
    out['all_checks_ok'] = bool(
        out['all_symbolic_ok'] and sym['Q_min_on_box'] > 0 and sym['Q_quadratic_lower_bound_discriminant'] < 0
        and sym['min_rinf_minus_rcont'] > 0 and sym['min_rhat_minus_rcont'] > 0
        and all(o['r_cont_in_bracket'] and o['r_hat_in_bracket'] for o in out['cases'].values())
        and all(not v for o in out['cases'].values() for v in o['unimodal_violations'].values())
        and all(o['fold_above_rcont'] >= 3 for o in out['cases'].values())
        and all(o['q_only_global_just_above_zsw'][k] == (i == 0)
                for o in out['cases'].values() for i, k in enumerate(o['q_only_global_just_above_zsw']))
        and all(v < 1e-9 for o in out['cases'].values() for v in o['clip_max_abs_diff_x'].values())
        and all(m['max_increase_in_r'] < 1e-9 and m['max_decrease_of_u_in_z'] < 1e-9
                for o in out['cases'].values() for m in o['monotonicity'].values()))
    dump('new4d_cost_structure.json', out)
    lines = ['# NEW-4d 成本结构核验（audit_cost_structure.py 生成）', '',
             f"符号恒等式全部成立：{out['all_symbolic_ok']}；全部检查通过：{out['all_checks_ok']}。", '',
             '| 参数 | b | r_cont | A→A′ 括区 | r̂ | A′→B 括区 | 截断最大差 | r=1 成本差 % |', '|---|---|---|---|---|---|---|---|']
    for case, o in out['cases'].items():
        lines.append(f"| {case} | {o['b']:.6f} | {o['r_cont']:.7f} | [{o['bracket_A_Ap'][0]:.6f}, {o['bracket_A_Ap'][1]:.6f}] | "
                     f"{o['r_hat']:.7f} | [{o['bracket_Ap_B'][0]:.6f}, {o['bracket_Ap_B'][1]:.6f}] | "
                     f"{max(o['clip_max_abs_diff_x'].values()):.1e} | {o['r1']['gap_percent']:.3f} |")
    (RESULTS / 'new4d_cost_structure.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print('all_checks_ok =', out['all_checks_ok'])


if __name__ == '__main__':
    main()
