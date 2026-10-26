"""NEW-4m：成本最优控制跳变结构入稿的派生核验（补充引理 S5.2、命题 S5.3）。

依据 ai/成本最优/补充推导_20261026/ 与 ai/NEW_4m_jump_structure_plan_20261026.md。
符号部分只核对代数恒等式（存在性、唯一性与极限论证见补充 S5.3 的证明）；
图件部分只读 NEW-4d 正文图 7 与 NEW-2 补充图 S10 的已存跳变点，使用前按迁移清单登记的 SHA-256 校验，不重算背景；
求解器部分用既有逐状态求解器（allocation.py，定理 5.1 的有限比较）在少量权重上抽查跳变次数与位置，不代替证明。
稿件不引用本脚本的数字，不生成数值宏。

记号：ζ = S/S_c，p = cS/(c0 S_c) = xζ ∈ [1, ζ]，b = S̄/S_c，r = w_q/w_c，s = √r，
ζ_j = 2[b + (1-b)s]，k = sζ_j，G(p; ζ) = [(1-p/ζ)^2 + r(1-1/p)^2]/(p-b)。

运行：python nr_audit/audit_jump_structure.py（约一分钟）。输出 results/new4m_jump_structure.json 与 .md。
"""
import hashlib
import json
import math

import numpy as np
import sympy as sp

import allocation as AL
import params as PR
import plot_figure7 as F7
import state_integrals as SI
from audit_common import ROOT, RESULTS, dump
from text_identity import content_sha256

RECEIPT = ROOT / 'nr_audit' / 'manuscript_path_migration_NEW4g.json'
FIG7_MAIN = RESULTS / 'new4d_figure7.json'   # 正文图 7（NEW-4d 等高线相图）
FIG7_DETAIL = RESULTS / 'new_figure7.json'   # 补充图 S10 所用 NEW-2 缓存


# ---------------------------------------------------------------- 闭式
def r_cont(b):
    return 16.0 / (b + math.sqrt(b * b - 8 * b + 8)) ** 2


def z_sw(b):
    return (3 + math.sqrt(9 - 8 * b)) / 2


def r_hat(b):
    t = z_sw(b)
    return (t / (t - 1)) ** 2


def zeta_j(b, r):
    return 2 * (b + (1 - b) * math.sqrt(r))


def tie_roots(b, r):
    """ζ_j 上 p^2 - kp + k 的两根 (p_-, p_+)；k ≤ 4 时返回 None。"""
    k = math.sqrt(r) * zeta_j(b, r)
    if k <= 4:
        return None
    d = math.sqrt(k * (k - 4))
    return (k - d) / 2, (k + d) / 2


# ---------------------------------------------------------------- 符号核对
def symbolic_checks():
    p, z, b, s, m, t = sp.symbols('p zeta b s m t', positive=True)
    r = s ** 2
    G = ((1 - p / z) ** 2 + r * (1 - 1 / p) ** 2) / (p - b)
    Pi = p ** 4 / z ** 2 - (2 / z + m) * p ** 3 + (1 + r + m * b) * p ** 2 - 2 * r * p + r
    zj = 2 * (b + (1 - b) * s)
    k = s * zj
    mj = 2 * (s - 1) / zj
    out = {}
    out['Pi_expansion'] = sp.simplify(sp.expand(p ** 2 * (p - b) * (G - m)) - Pi) == 0
    # 系数比较：Π = ζ^{-2}(p^2 - ℓp + k)^2 的四个等式在 ζ = ζ_j、m = m_j、ℓ = k = sζ_j 时成立
    out['Pi_square_at_zeta_j'] = sp.simplify(sp.expand(Pi.subs({z: zj, m: mj}) - (p ** 2 - k * p + k) ** 2 / zj ** 2)) == 0
    out['square_identity'] = sp.simplify(sp.together(G.subs(z, zj) - mj
                                                     - (p ** 2 - k * p + k) ** 2 / (zj ** 2 * p ** 2 * (p - b)))) == 0
    # 二次项比较解出 ζ_j：s^2 + 2s/ζ = 1 + s^2 + 2b(s-1)/ζ
    zsol = sp.solve(sp.Eq(s ** 2 + 2 * s / z, 1 + s ** 2 + 2 * b * (s - 1) / z), z)
    out['quadratic_coeff_gives_zeta_j'] = len(zsol) == 1 and sp.simplify(zsol[0] - zj) == 0
    out['k_formula'] = sp.simplify(k - 2 * ((1 - b) * s ** 2 + b * s)) == 0
    out['quadratic_at_zeta_j'] = sp.simplify((zj ** 2 - k * zj + k) - zj * (s - (s - 1) * zj)) == 0
    # 因式分解（式 eq:sup:jump-factor），b = t(3-t)/2，t = ζ_sw
    lhs = (s - (s - 1) * zj).subs(b, t * (3 - t) / 2)
    out['factorization'] = sp.expand(lhs - (t - (t - 1) * s) * ((t - 2) * s + 3 - t)) == 0
    out['one_minus_b'] = sp.expand(2 * (1 - t * (3 - t) / 2) - (t - 1) * (t - 2)) == 0
    # 端点：ζ_j(√r_cont) = b + √(b^2-8b+8)；ζ_j(√r̂) = ζ_sw，两根为 ζ_sw 与 ζ_sw/(ζ_sw-1)
    sc = 4 / (b + sp.sqrt(b ** 2 - 8 * b + 8))
    out['zeta_j_at_rcont'] = sp.simplify(zj.subs(s, sc) - (b + sp.sqrt(b ** 2 - 8 * b + 8))) == 0
    sh = t / (t - 1)
    zj_h = zj.subs(s, sh).subs(b, t * (3 - t) / 2)
    out['zeta_j_at_rhat'] = sp.simplify(zj_h - t) == 0
    k_h = sp.simplify(sh * zj_h)
    out['roots_at_rhat'] = (sp.simplify(t ** 2 - k_h * t + k_h) == 0) and sp.simplify(k_h / t - t / (t - 1)) == 0
    # 与 p = 1 比较：G(1;ζ) - G(ζ;ζ) = (1-1/ζ)^2 [1/(1-b) - r/(ζ-b)]
    out['compare_with_p1'] = sp.simplify(G.subs(p, 1) - G.subs(p, z)
                                         - (1 - 1 / z) ** 2 * (1 / (1 - b) - r / (z - b))) == 0
    out['cross_derivative'] = sp.simplify(sp.diff(G, p, z)
                                          + 2 * ((p - b) ** 2 + b * (z - b)) / (z ** 3 * (p - b) ** 2)) == 0
    return out


# ---------------------------------------------------------------- 图件已存跳变点
def checked_json(path):
    raw = path.read_bytes()
    key = path.relative_to(ROOT).as_posix()
    expected = json.loads(RECEIPT.read_text(encoding='utf-8'))['protected_original_sha256'][key]
    ok = hashlib.sha256(raw).hexdigest() == expected or content_sha256(raw) == expected
    if not ok:
        raise ValueError(f'{key} 与迁移清单登记的 SHA-256 不符，不能使用')
    return json.loads(raw.decode('utf-8')), expected


def compare_points(points, b):
    """points: [(r, z, x_left, x_right)]；返回与 ζ_j、p_±/ζ_j 的最大差。"""
    dz = dx = 0.0
    for r, z, xl, xr in points:
        zj = zeta_j(b, r)
        pm, pp = tie_roots(b, r)
        dz = max(dz, abs(z - zj))
        dx = max(dx, abs(xl - pm / zj), abs(xr - pp / zj))
    return dict(n=len(points), max_abs_dz=dz, max_abs_dx=dx)


def figure_checks():
    main, sha_main = checked_json(FIG7_MAIN)
    detail, sha_detail = checked_json(FIG7_DETAIL)
    out = dict(sources={FIG7_MAIN.name: sha_main, FIG7_DETAIL.name: sha_detail}, cases={})
    for case in ('base', 'xian'):
        b = main['cases'][case]['b']
        pts_main = [(g['r'], g['z'], g['x_left'], g['x_right'])
                    for g in main['cases'][case]['gamma'] if g['kind'] == 'internal']
        pts_detail = [(row['r'], bp['z'], bp['x_left'], bp['x_right'])
                      for row in detail['cases'][case]['samples'] for bp in row['breakpoints']
                      if F7.edge_kind(bp) == 'internal']
        rc, rh = r_cont(b), r_hat(b)
        out['cases'][case] = dict(
            figure7=compare_points(pts_main, b), figureS10=compare_points(pts_detail, b),
            internal_r_inside_Aprime=all(rc < q[0] < rh for q in pts_main + pts_detail))
    return out


# ---------------------------------------------------------------- 求解器抽查
def p_opt(z, b, r):
    return AL.argmin_state(z, b, 1.0, r)[0] * z


def find_jumps(b, r, z_lo, z_hi, n=1500):
    zs = np.linspace(z_lo, z_hi, n)
    P = np.array([p_opt(float(z), b, r) for z in zs])
    jumps = []
    for i in np.where(np.abs(np.diff(P)) > 3 * (zs[1] - zs[0]))[0]:
        a, c, pa, pc = float(zs[i]), float(zs[i + 1]), P[i], P[i + 1]
        while c - a > 1e-13 * c:
            mid = 0.5 * (a + c)
            pm = p_opt(mid, b, r)
            if abs(pm - pa) >= abs(pc - pm):
                c, pc = mid, pm
            else:
                a, pa = mid, pm
        # 所选权重下真实跳幅不小于 0.1；尖点 r = r_cont 处最小点按立方根变化，二分到 1e-13 仍留约 1e-4 的差
        if abs(pc - pa) > 1e-3 and (not jumps or abs(a - jumps[-1]['z']) > 1e-9):
            jumps.append(dict(z=0.5 * (a + c), p_below=pa, p_above=pc))
    return jumps


def solver_checks(case, P, zstar):
    b = P.z_bar
    rc, rh, t = r_cont(b), r_hat(b), z_sw(b)
    out = dict(b=b, z_sw=t, r_cont=rc, r_hat=rh, z_star=zstar, ties={}, scans={})
    # ζ_j 上两个最小点等值，且即为求解器的全局最小值
    for r in np.linspace(rc, rh, 7)[1:-1]:
        zj = zeta_j(b, r)
        pm, pp = tie_roots(b, r)
        fm = AL.objective_x(pm / zj, zj, b, 1.0, r)
        fp = AL.objective_x(pp / zj, zj, b, 1.0, r)
        x, val, _ = AL.argmin_state(zj, b, 1.0, r)
        out['ties'][f'{r:.6f}'] = dict(
            zeta_j=zj, p_minus=pm, p_plus=pp, rel_gap_between_roots=abs(fm - fp) / fm,
            solver_rel_gap=abs(val - min(fm, fp)) / fm,
            solver_hits_root=min(abs(x * zj - pm), abs(x * zj - pp)) < 1e-7,
            order_ok=1 < pm < 2 < pp < zj < t)
    # 跳变次数与位置
    weights = [0.5, 2.0, rc] + list(np.linspace(rc, rh, 7)[1:-1]) + [rh, rh * 1.01, 5.0, 10.0, 20.0]
    for r in weights:
        z_hi = max(1.3 * zstar, 1.2 * (b + r * (1 - b)) + 1.0)
        J = find_jumps(b, float(r), 1.0005, z_hi)
        expect = 0 if r <= rc else 1
        rec = dict(n_jumps=len(J), expect=expect, jumps=J, location_ok=True, direction_ok=True)
        if expect and len(J) == 1:
            j = J[0]
            rec['direction_ok'] = j['p_below'] < j['p_above'] and j['p_below'] / j['z'] < j['p_above'] / j['z']
            if r < rh:
                rec['location_ok'] = abs(j['z'] - zeta_j(b, r)) < 1e-9
            else:
                lower = max(t, b + r * (1 - b))
                f_end = AL.objective_x(1.0, j['z'], b, 1.0, r)
                f_int = AL.objective_x(j['p_below'] / j['z'], j['z'], b, 1.0, r)
                rec['tie_rel_gap'] = abs(f_end - f_int) / f_end
                rec['location_ok'] = (j['z'] >= lower - 1e-9 and abs(j['p_above'] - j['z']) < 1e-6
                                      and rec['tie_rel_gap'] < 1e-8)
                if abs(r - rh) < 1e-15:
                    rec['location_ok'] = rec['location_ok'] and abs(j['z'] - t) < 1e-8 \
                        and abs(j['p_below'] - t / (t - 1)) < 1e-6
        rec['ok'] = rec['n_jumps'] == expect and rec['location_ok'] and rec['direction_ok']
        out['scans'][f'{r:.6f}'] = rec
    return out


# ---------------------------------------------------------------- 主程序
def main():
    out = dict(script='nr_audit/audit_jump_structure.py', symbolic=symbolic_checks(),
               figures=figure_checks(), solver={})
    for case, P in PR.CASES.items():
        zstar = SI.start_state(P)['z_star']
        out['solver'][case] = solver_checks(case, P, zstar)
    sym = out['symbolic']
    out['all_symbolic_ok'] = all(sym.values())
    figs_ok = all(c[f]['max_abs_dz'] < 1e-10 and c[f]['max_abs_dx'] < 1e-8 and c[f]['n'] > 0
                  and c['internal_r_inside_Aprime']
                  for c in out['figures']['cases'].values() for f in ('figure7', 'figureS10'))
    ties_ok = all(v['rel_gap_between_roots'] < 1e-12 and v['solver_rel_gap'] < 1e-10 and v['solver_hits_root']
                  and v['order_ok'] for o in out['solver'].values() for v in o['ties'].values())
    scans_ok = all(v['ok'] for o in out['solver'].values() for v in o['scans'].values())
    out['all_checks_ok'] = bool(out['all_symbolic_ok'] and figs_ok and ties_ok and scans_ok)
    dump('new4m_jump_structure.json', out)
    lines = ['# NEW-4m 跳变结构核验（audit_jump_structure.py 生成）', '',
             f"符号恒等式全部成立：{out['all_symbolic_ok']}；全部检查通过：{out['all_checks_ok']}。", '',
             '| 参数 | 图7内部跳变点 | 最大 |z-ζ_j| | 图S10内部跳变点 | 最大 |z-ζ_j| | 抽查权重 | 跳变次数与位置全部相符 |',
             '|---|---|---|---|---|---|---|']
    for case in ('base', 'xian'):
        f = out['figures']['cases'][case]
        s = out['solver'][case]['scans']
        lines.append(f"| {case} | {f['figure7']['n']} | {f['figure7']['max_abs_dz']:.1e} | {f['figureS10']['n']} | "
                     f"{f['figureS10']['max_abs_dz']:.1e} | {len(s)} | {all(v['ok'] for v in s.values())} |")
    (RESULTS / 'new4m_jump_structure.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(all_symbolic_ok=out['all_symbolic_ok'], figures_ok=figs_ok, ties_ok=ties_ok,
                          scans_ok=scans_ok, all_checks_ok=out['all_checks_ok']), ensure_ascii=False))


if __name__ == '__main__':
    main()
