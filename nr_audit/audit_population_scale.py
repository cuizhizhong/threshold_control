"""NR-6：人口缩放情景（原补充 S4“规模的作用”一段，移入补充 S3.1）的数字复核。

固定西安传播参数与全市拟合的绝对初值 I0 = 0.00100659188867187，S0 = N - I0，其余初始仓室为零，仅隔离控制：
(a) θ = η/N = 0.002，N 取 5e4、1e5、5e5、1e6、5e6、13163000（与原 `fixed_absolute_scale.csv` 的六行相同）；
(b) 固定绝对阈值 η = 100，N 由 13163000 降到 5e4；
(c) 对数因子 ln[(S*-S̄)/(S_c-S̄)] 在 θ ∈ [5e-4, 8e-3]（η = 100）内的取值。
报告 t1、Δt、J、清零时间及相对极差，并与原 CSV（只读）对照。不重新拟合；这是人口缩放的数值情景，
同时改变 N、i0 = I0/N 与 η = θN，不是固定西安人口下的初值敏感性检验（后者见 audit_initial_condition.py）。

运行：conda run --no-capture-output -n thesis python nr_audit/audit_population_scale.py
输出：results/population_scale.json、results/population_scale.md
"""
import csv
import math

import params as PR
import state_integrals as SI
from audit_common import RESULTS, ROOT, dump

POPS = (5.0e4, 1.0e5, 5.0e5, 1.0e6, 5.0e6, 13163000.0)
OLD_CSV = ROOT / 'reproducibility' / 'results' / '20261003_release_final' / 'population' / 'fixed_absolute_scale.csv'


def run(N, eta):
    X = PR.XIAN
    P = X.with_(N=N, S0=N - PR.XIAN_I0, I0=PR.XIAN_I0, eta=eta)
    st = SI.state_path(SI.Policy(P, 'q_only'))
    sstar = st['S_star']
    L = math.log((sstar - P.S_bar) / (P.S_c - P.S_bar))
    return dict(N=N, eta=eta, theta=eta / N, i0=PR.XIAN_I0 / N, t1=st['t1'], S_star=sstar, dt=st['dt'], J=st['J'],
                t_end=st['t_end'], log_factor=L, dt_from_formula=N / (P.c0 * eta) * L)


def spread(vals):
    return (max(vals) - min(vals)) / max(vals)


def main():
    a = [run(N, 0.002 * N) for N in POPS]
    b = [run(N, 100.0) for N in (13163000.0, 5.0e4)]
    c = [run(100.0 / th, 100.0) for th in (5e-4, 8e-3)]
    old = {}
    if OLD_CSV.exists():
        with OLD_CSV.open(encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                old[float(r['N'])] = dict(t1=float(r['t1']), dt=float(r['Delta_t']), J=float(r['J']))
    rows_cmp = []
    for r in a:
        o = old.get(r['N'])
        if o:
            rows_cmp.append(dict(N=r['N'], rel_t1=abs(r['t1'] - o['t1']) / o['t1'], rel_dt=abs(r['dt'] - o['dt']) / o['dt'],
                                 rel_J=abs(r['J'] - o['J']) / o['J']))
    out = dict(
        description='NR-6：人口缩放情景复核。a：θ=0.002，六个人口；b：η=100，N=13163000 与 5e4；c：η=100 时 θ=5e-4 与 8e-3 的对数因子。'
                    'old_compare 为与原 fixed_absolute_scale.csv 的相对差（只读对照）。',
        a_fixed_theta=a, b_fixed_eta=b, c_log_factor=c,
        spread_dt=spread([r['dt'] for r in a]), spread_J=spread([r['J'] for r in a]),
        t1_min=min(r['t1'] for r in a), t1_max=max(r['t1'] for r in a),
        old_compare=rows_cmp, old_compare_max=max([max(r['rel_t1'], r['rel_dt'], r['rel_J']) for r in rows_cmp] or [None]))
    dump('population_scale.json', out)
    L = ['# NR-6 人口缩放情景复核', '',
         '| 情景 | N | η | θ | t1 (d) | Δt (d) | J (d) | t_end (d) | 对数因子 |', '|---|---|---|---|---|---|---|---|---|']
    for tag, rows in (('θ=0.002', a), ('η=100', b), ('η=100，θ 端点', c)):
        for r in rows:
            L.append(f"| {tag} | {r['N']:.6g} | {r['eta']:.6g} | {r['theta']:.4g} | {r['t1']:.4f} | {r['dt']:.4f} | "
                     f"{r['J']:.4f} | {r['t_end']:.2f} | {r['log_factor']:.4f} |")
    L += ['', f"θ=0.002 的六个人口：Δt 相对极差 {out['spread_dt']:.3e}，J 相对极差 {out['spread_J']:.3e}；"
              f"t1 由 {out['t1_min']:.4f} 增至 {out['t1_max']:.4f} d。",
          f"与原 CSV 的最大相对差（t1、Δt、J）：{out['old_compare_max']:.2e}。"]
    (RESULTS / 'population_scale.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
