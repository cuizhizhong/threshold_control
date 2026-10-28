"""NEW-4w W3：西安设计阈值由 η = 0.002N 改为 0.001N 后的重算（N33）。

先在 η = 0.002N 下复现现稿的西安数值（预检），通过后在 η = 0.001N 下重算：
- 四种控制（仅减少接触、α = 0.5、仅隔离、成本最优，w_c = 1、w_q = 2）的表 3 指标与 S*/S_c；
- 能力代表点（c_min/c0 = 0.5、q_cap = 0.75）的成本最优控制与能力可行区域；
- 成本权重的 B→C 括区（仅隔离段消失，依赖 S*）与 r = 1 时的成本差；A→A′、A′→B 只依赖 b，复核不变；
- TDINN 与常规控制（与 η 无关，复核不变）以及两种阈值控制的全过程汇总；
- 人口缩放（θ = 0.001，六个人口）与 I0 敏感性（0.1、1、10 倍）；
- 开环完整方程的阈值偏差；仅隔离控制从启动到清零的时长；
- 绘图数据：能力区域网格、成本权重相图网格与跳变曲线、两种阈值控制的轨迹。
参数、初值与拟合不变；只改西安的 η。冻结结果只读，使用前登记 SHA-256。

运行（仓库根目录）：python -X utf8 nr_audit/new4w_xian_threshold.py
输出：nr_audit/results/new4w/ 下的 xian_theta001.json、xian_phase.npz、xian_capacity.npz、xian_trajectories.csv
"""
import csv
import hashlib
import json
import math
import subprocess
import time

import numpy as np

import audit_population_scale as APS
import audit_weights as AW
import allocation as AL
import params as PR
import plot_figure7_contour as F7
import simulate as SM
import state_integrals as SI
import tdinn as TD
from audit_common import ROOT, RESULTS, git_head, plain, tex_table_rows, num

OUT = RESULTS / 'new4w'
THETA_OLD, THETA_NEW = 0.002, 0.001
PRE_COMMIT = 'ebb7df5'          # NEW-4w W2：西安表格仍为 θ = 0.002 的最后一个提交
LAWS = ('c_only', 'alpha', 'q_only', 'opt')
JX = ROOT / 'reproducibility/results/20261005_sec7_v2_refinement/joint_extra'
XI = ROOT / 'reproducibility/results/20261003_release_final/xian'
FROZEN = [RESULTS / 'new4d_figure7.json', RESULTS / 'new4d_figure7.npz', RESULTS / 'new4d_cost_structure.json',
          RESULTS / 'weight_brackets.json', JX / 'capacity.json', JX / 'capacity_xian.npz',
          XI / 'timeseries.csv', XI / 'summary.csv']
CODE = ['simulate.py', 'state_integrals.py', 'allocation.py', 'model.py', 'params.py', 'tdinn.py',
        'audit_weights.py', 'audit_population_scale.py', 'plot_figure7_contour.py', 'new4w_xian_threshold.py']
IS, ILI, ISQ, IIQ, IR, ICI, ICIQ = range(7)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def xian(theta):
    return PR.XIAN.with_(eta=theta * PR.XIAN.N)


def laws(P):
    """四种控制：状态路径（主值）与开环完整方程（峰值与核验）。"""
    out = {}
    for law in LAWS:
        pol = SI.Policy(P, law)
        st, od = SI.state_path(pol), SM.run(pol)
        out[law] = dict(
            t1=st['t1'], t2=st['t2'], dt=st['dt'], t_end=st['t_end'], J=st['J'],
            total_to_clearance=st['total_infections_to_clearance'], total_inf=st['total_infections_inf'],
            dSq=st['sq_identity'], arc_infections=st['inf_identity'], z_star=st['z_star'], q_max=st['q_max'],
            peak_ratio=od['peak_I_plus_Iq_over_eta'], t_peak_tot=od['t_peak_I_plus_Iq'],
            ode=dict(dt=od['dt'], t_end=od['t_end'], J=od['J'], total=od['total_infections_to_clearance'],
                     dSq=od['arc_Sq_new'], plateau_abs_dev=od['plateau_abs_dev'],
                     post_upcross_eta=od['post_upcross_eta'], segments=od['segments']),
            _runner=od['_runner'])
    return out


def capacity_point(P):
    C = PR.REP_CAPACITY['xian']
    pol = SI.Policy(P, 'opt', cap=C)
    st, od = SI.state_path(pol), SM.run(pol)
    start = SI.start_state(P)
    q_max, z_star = start['q_max'], start['z_star']
    return dict(c_min=C.c_min, q_cap=C.q_cap, u_max=1 - C.c_min / P.c0,
                q_only_feasible=bool(C.q_cap >= q_max), c_only_feasible=bool(C.c_min <= P.c0 / z_star),
                joint_feasible=bool(C.c_min * (1 - C.q_cap) <= P.c0 * (1 - q_max)),
                J=st['J'], dt=st['dt'], t_end=st['t_end'], total=st['total_infections_to_clearance'],
                ode_J=od['J'], ode_dt=od['dt'], segments=od['segments'], q_max=q_max, z_star=z_star,
                dt_upper=SI.state_path(SI.Policy(P, 'cap_upper', cap=C))['dt'],
                dt_lower=SI.state_path(SI.Policy(P, 'cap_lower', cap=C))['dt'])


def region_arrays(P):
    """能力可行区域：2 为仅隔离或仅减少接触可行，1 为只有联合控制可行，0 为不可行（推论 4.x 的闭式判据）。"""
    start = SI.start_state(P)
    q_max, z_star = start['q_max'], start['z_star']
    u, q = np.linspace(0.0, 0.999, 600), np.linspace(P.q0, 0.999, 600)
    U, Q = np.meshgrid(u, q)
    single = (Q >= q_max) | (U >= 1 - 1 / z_star)
    joint = (1 - U) * (1 - Q) <= 1 - q_max
    region = np.where(single, 2, np.where(joint, 1, 0)).astype(np.int8)
    bu = np.linspace(0.0, 0.999, 1201)          # 与冻结数据相同：细网格上取到 1 - 1/z* 为止
    bu = bu[bu <= 1 - 1 / z_star]
    bq = 1 - (1 - q_max) / (1 - bu)
    return dict(u=u, q=q, region=region, boundary_u=bu, boundary_q=bq,
                quarantine_line=np.array(q_max), contact_line=np.array(1 - 1 / z_star))


def phase_arrays(P, z_star, cs):
    """成本权重相图（与 NEW-4d 相同的网格与求解器），横轴取到给定的 z*。"""
    b, zsw = P.z_bar, cs['z_sw']
    z = np.linspace(1.002, z_star, 300)
    r = np.geomspace(0.9, F7.R_MAX, 300)
    Y = np.zeros((r.size, z.size))
    for i, rv in enumerate(r):
        for j, zv in enumerate(z):
            x, lab = F7.x_and_label(zv, b, rv)
            Y[i, j] = 0.0 if lab == 'hi' else (1 - x) / (1 - 1 / zv)
    gamma = []
    for rv in np.concatenate([np.linspace(cs['r_cont'] * (1 + 1e-3), cs['r_hat'], 25),
                              np.geomspace(cs['r_hat'], F7.R_MAX, 60)[1:]]):
        jmp = F7.jump_in(b, rv, cs['cusp_state'] - 0.05, z_star)
        if jmp is not None:
            gamma.append(dict(r=float(rv), z=float(jmp[0]), x_left=float(jmp[1]), x_right=float(jmp[2]), kind=jmp[3]))
    lo, hi = cs['r_hat'], 60.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if F7.x_and_label(z_star * (1 - 1e-12), b, mid)[1] == 'hi':
            lo = mid
        else:
            hi = mid
    case = dict(b=b, z_sw=zsw, z_star=z_star, r_cont=cs['r_cont'], r_hat=cs['r_hat'],
                cusp_state=cs['cusp_state'], r_C=0.5 * (lo + hi), gamma=gamma)
    return case, dict(xian_z=z, xian_r=r, xian_y=Y)


def weight_brackets(P):
    """A→A′、A′→B 端点复核；B→C 在 [7, 9] 内二分到宽度 < 1e-3；r = 1 时的成本差。"""
    old = {(x['from_'], x['to']): (x['lo'], x['hi'])
           for ch in json.loads((RESULTS / 'weight_brackets.json').read_text(encoding='utf-8'))['cases']['xian']['changes']
           for x in ch['brackets']}
    ends = {}
    for key in (('A', "A'"), ("A'", 'B')):
        lo, hi = old[key]
        ends['%s->%s' % key] = dict(lo=lo, hi=hi, class_lo=AW.classify(P, lo)[0], class_hi=AW.classify(P, hi)[0])
    a, b = 7.0, 9.0
    ca, cb = AW.classify(P, a)[0], AW.classify(P, b)[0]
    assert (ca, cb) == ('B', 'C'), (ca, cb)
    log = []
    br = AW.refine(P, a, b, 'B', 'C', log)
    assert br['status'] == 'resolved'
    br = dict(lo=br['lo'], hi=br['hi'], width=br['width'],
              check_fine={str(n): dict(lo=AW.classify(P, br['lo'], N_z=n, N_local=n)[0],
                                       hi=AW.classify(P, br['hi'], N_z=n, N_local=n)[0]) for n in (8001, 16001)})
    m_opt = SI.arc_integrals(SI.Policy(P, 'opt', wc=1.0, wq=1.0))
    m_q = SI.arc_integrals(SI.Policy(P, 'q_only', wc=1.0, wq=1.0))
    gap = dict(J_min=float(m_opt['J']), J_q_only=float(m_q['J']), gap_percent=float(100 * (1 - m_opt['J'] / m_q['J'])))
    return dict(unchanged_ends=ends, B_to_C=br, r1=gap)


def strategies(P, runs):
    """TDINN、常规控制（与 η 无关）与两种阈值控制的全过程汇总。"""
    td, _ = TD.run(P, TD.tdinn)
    rt, _ = TD.run(P, TD.routine_of(P))
    rows = dict(TDINN=dict(peak_I=td['peak_I'], total=td['total'], t_end=td['t_end']),
                routine=dict(peak_I=rt['peak_I'], total=rt['total'], t_end=rt['t_end']))
    for law in ('q_only', 'opt'):
        r = runs[law]
        rows[law] = dict(peak_I=P.eta, total=r['total_to_clearance'], t_end=r['t_end'],
                         t1=r['t1'], t2=r['t2'], dt=r['dt'])
    return rows


def initial_condition(P):
    """I0 为拟合值的 0.1、1、10 倍（与 audit_initial_condition.py 相同的设定，阈值改为 P.eta）。"""
    rows = []
    keys = ('t1', 'S_star', 'dt', 'J', 't_end', 'total_infections_to_clearance')
    for f in (0.1, 1.0, 10.0):
        I0 = f * PR.XIAN_I0
        Q = P.with_(I0=I0, S0=P.N - I0)
        for law in ('q_only', 'opt'):
            st = SI.state_path(SI.Policy(Q, law))
            rows.append(dict(factor=f, law=law, **{k: st[k] for k in keys}))
    fit = {r['law']: r for r in rows if r['factor'] == 1.0}
    shift = max(abs(r['t1'] - fit[r['law']]['t1']) for r in rows)
    max_rel = {k: max(abs(r[k] - fit[r['law']][k]) / abs(fit[r['law']][k]) for r in rows) for k in keys[1:]}
    return dict(rows=rows, t1_max_abs_shift=shift, max_abs_relative_change=max_rel)


def population(theta):
    a = [APS.run(N, theta * N) for N in APS.POPS]
    return dict(rows=a, spread_dt=APS.spread([r['dt'] for r in a]), spread_J=APS.spread([r['J'] for r in a]),
                t1_min=min(r['t1'] for r in a), t1_max=max(r['t1'] for r in a),
                dt_min=min(r['dt'] for r in a), dt_max=max(r['dt'] for r in a))


def trajectories(P, runs):
    """两种阈值控制的完整方程轨迹（开环），每阶段按 0.1 d 取样并含阶段端点。"""
    rows = []
    for law, name in (('q_only', 'quarantine_only'), ('opt', 'minimum_cost')):
        R = runs[law]['_runner']
        t_end = runs[law]['ode']['t_end']
        for label, sol, control, ta, tb in R.phases:
            tb = min(tb, t_end) if label == 'post' else tb
            tt = np.unique(np.r_[np.arange(ta, tb, 0.1), tb])
            Y = sol.sol(tt)
            phase = dict(routine='before', plateau='control', post='after')[label]
            for k, t in enumerate(tt):
                c, q = control(float(t))
                S, I = Y[IS, k] * P.N, math.exp(Y[ILI, k]) * P.N
                rows.append(dict(strategy=name, phase=phase, t=float(t), S=S, I=I, Sq=Y[ISQ, k] * P.N,
                                 Iq=Y[IIQ, k] * P.N, Ctotal=(Y[ICI, k] + Y[ICIQ, k]) * P.N, c=c, q=q,
                                 Rt=P.beta * c * (1 - q) * S / (P.gamma * P.N)))
    return rows


def precheck(cs):
    """η = 0.002N 下复现现稿：表 3、表 4、能力代表点、B→C 括区、相图缓存与能力区域。"""
    P = xian(THETA_OLD)
    runs = laws(P)
    # 预检对照 θ = 0.002 时的稿件（W4 改表之前的提交）
    pre = ROOT / 'paper/tmp/new4w/07_xian_pre_W4.tex'
    pre.parent.mkdir(parents=True, exist_ok=True)
    pre.write_bytes(subprocess.run(['git', 'show', f'{PRE_COMMIT}:paper/sections/07_xian.tex'], cwd=ROOT,
                                   capture_output=True, check=True).stdout)
    rows = tex_table_rows(pre.relative_to(ROOT).as_posix(), 'tab:xian:joint-compare')
    unit = 1e6
    table3 = []
    for row, law in zip(rows, LAWS):
        r = runs[law]
        vals = (r['dt'], r['t_end'], r['total_to_clearance'] / unit, r['dSq'] / unit, r['J'], r['peak_ratio'])
        for cell, v in zip(row[1:], vals):
            d = num(cell)
            dec = len(cell.split('.')[1]) if '.' in cell else 0
            table3.append(dict(law=law, display=cell, value=v, ok=abs(round(v, dec) - d) < 1e-9))
    cap = capacity_point(P)
    caps = [dict(name='J', display=41.62, value=cap['J'], ok=round(cap['J'], 2) == 41.62),
            dict(name='dt', display=116.8, value=cap['dt'], ok=round(cap['dt'], 1) == 116.8)]
    st = strategies(P, runs)
    t4 = [dict(name='q_only.total', ok=round(st['q_only']['total']) == 2377943),
          dict(name='q_only.t_end', ok=round(st['q_only']['t_end'], 2) == 258.10),
          dict(name='opt.total', ok=round(st['opt']['total']) == 2534829),
          dict(name='opt.t_end', ok=round(st['opt']['t_end'], 2) == 281.84),
          dict(name='TDINN.total', ok=round(st['TDINN']['total'], 2) == 2105.63),
          dict(name='TDINN.t_end', ok=round(st['TDINN']['t_end'], 2) == 45.29),
          dict(name='routine.peak', ok=round(st['routine']['peak_I']) == 1377552),
          dict(name='routine.total', ok=round(st['routine']['total']) == 4587183),
          dict(name='routine.t_end', ok=round(st['routine']['t_end'], 2) == 75.57)]
    # 相图缓存：同一网格与求解器重算西安网格，应与 NEW-4d 缓存逐元素相同
    old_case = json.loads((RESULTS / 'new4d_figure7.json').read_text(encoding='utf-8'))['cases']['xian']
    with np.load(RESULTS / 'new4d_figure7.npz') as d:
        y_old, z_old = d['xian_y'], d['xian_z']
    case, arr = phase_arrays(P, old_case['z_star'], cs)
    phase = dict(max_abs_diff_y=float(np.max(np.abs(arr['xian_y'] - y_old))), z_equal=bool(np.array_equal(arr['xian_z'], z_old)),
                 r_C=case['r_C'], r_C_old=old_case['r_C'], gamma_points=len(case['gamma']),
                 gamma_points_old=len(old_case['gamma']))
    phase['ok'] = phase['max_abs_diff_y'] < 1e-10 and phase['z_equal'] and abs(case['r_C'] - old_case['r_C']) < 1e-9
    with np.load(JX / 'capacity_xian.npz') as d:
        reg = region_arrays(P)
        same_len = reg['boundary_u'].shape == d['boundary_u'].shape
        region = dict(region_equal=bool(np.array_equal(reg['region'], d['region'])), boundary_same_length=same_len,
                      boundary_max_abs=float(max(np.max(np.abs(reg['boundary_u'] - d['boundary_u'])),
                                                 np.max(np.abs(reg['boundary_q'] - d['boundary_q']))))
                      if same_len else float('inf'),
                      lines_max_abs=float(max(abs(float(reg['quarantine_line']) - float(d['quarantine_line'].ravel()[0])),
                                              abs(float(reg['contact_line']) - float(d['contact_line'].ravel()[0])))))
    region['ok'] = region['region_equal'] and region['boundary_max_abs'] < 1e-12 and region['lines_max_abs'] < 1e-12
    wb = weight_brackets(P)
    bc = dict(lo=wb['B_to_C']['lo'], hi=wb['B_to_C']['hi'], ok=wb['B_to_C']['lo'] <= 7.4537 and wb['B_to_C']['hi'] >= 7.4530,
              r1_gap=wb['r1']['gap_percent'], r1_ok=round(wb['r1']['gap_percent'], 1) == 3.0)
    ok = (all(x['ok'] for x in table3) and all(x['ok'] for x in caps) and all(x['ok'] for x in t4)
          and phase['ok'] and region['ok'] and bc['ok'] and bc['r1_ok'])
    return dict(ok=ok, table3=table3, capacity=caps, table4=t4, phase=phase, region=region, weights=bc)


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    inputs = {p.relative_to(ROOT).as_posix(): dict(sha256=sha(p), content_sha256=text_sha(p)) for p in FROZEN}
    code = {f'nr_audit/{n}': text_sha(ROOT / 'nr_audit' / n) for n in CODE}
    cs = json.loads((RESULTS / 'new4d_cost_structure.json').read_text(encoding='utf-8'))['cases']['xian']
    pre = precheck(cs)
    print('precheck ok:', pre['ok'], f'({time.time() - t0:.0f} s)', flush=True)
    if not pre['ok']:
        (OUT / 'xian_precheck_failed.json').write_text(json.dumps(plain(pre), ensure_ascii=False, indent=1),
                                                         encoding='utf-8', newline='\n')
        raise SystemExit('预检未通过，停止')

    P = xian(THETA_NEW)
    runs = laws(P)
    start = SI.start_state(P)
    cap = capacity_point(P)
    wb = weight_brackets(P)
    st = strategies(P, runs)
    ic = initial_condition(P)
    pop = population(THETA_NEW)
    case, arr = phase_arrays(P, start['z_star'], cs)
    reg = region_arrays(P)
    traj = trajectories(P, runs)
    print('compute done', f'({time.time() - t0:.0f} s)', flush=True)

    np.savez_compressed(OUT / 'xian_phase.npz', **arr)
    np.savez_compressed(OUT / 'xian_capacity.npz', **reg)
    with (OUT / 'xian_trajectories.csv').open('w', encoding='utf-8', newline='\n') as f:
        w = csv.DictWriter(f, fieldnames=list(traj[0]))
        w.writeheader()
        w.writerows(traj)
    q = runs['q_only']
    result = dict(
        script='nr_audit/new4w_xian_threshold.py', git_head=git_head(), authorization='AGENTS.md N33（NEW-4w）',
        settings=dict(theta=THETA_NEW, eta=P.eta, N=P.N, weights=[P.wc, P.wq],
                      capacity=dict(c_min=PR.REP_CAPACITY['xian'].c_min, q_cap=PR.REP_CAPACITY['xian'].q_cap)),
        inputs=inputs, code=code, precheck=pre,
        start=dict(z_star=start['z_star'], q_max=start['q_max'], S_star=start['S_star'],
                   z_sw=AL.z_sw_formula(P.z_bar)),
        laws={k: {kk: vv for kk, vv in v.items() if kk != '_runner'} for k, v in runs.items()},
        capacity=cap, weights=wb, strategies=st, initial_condition=ic, population=pop,
        phase=dict(case=case, npz_sha256=sha(OUT / 'xian_phase.npz')),
        region=dict(npz_sha256=sha(OUT / 'xian_capacity.npz'), q_max=float(reg['quarantine_line']),
                    contact_line=float(reg['contact_line'])),
        trajectories=dict(csv_content_sha256=text_sha(OUT / 'xian_trajectories.csv'), rows=len(traj)),
        holding=dict(q_only=q['t_end'] - q['t1'], opt=runs['opt']['t_end'] - runs['opt']['t1'],
                     c_only=runs['c_only']['t_end'] - runs['c_only']['t1']),
        plateau_abs_dev_q_only=q['ode']['plateau_abs_dev'],
        post_exit_upcross=any(len(v['ode']['post_upcross_eta']) for v in runs.values()),
        elapsed_s=time.time() - t0)
    (OUT / 'xian_theta001.json').write_text(json.dumps(plain(result), ensure_ascii=False, indent=1),
                                            encoding='utf-8', newline='\n')
    print(json.dumps(plain(dict(start=result['start'],
                                table3={k: [round(v[x], 4) for x in ('dt', 't_end', 'total_to_clearance', 'dSq', 'J', 'peak_ratio')]
                                        for k, v in result['laws'].items()},
                                capacity={k: cap[k] for k in ('J', 'dt', 'q_only_feasible', 'c_only_feasible', 'joint_feasible')},
                                B_to_C=wb['B_to_C'], r1=wb['r1'], strategies=st, holding=result['holding'],
                                t1_shift=ic['t1_max_abs_shift'],
                                population={k: pop[k] for k in ('t1_min', 't1_max', 'dt_min', 'dt_max', 'spread_dt', 'spread_J')},
                                r_C=case['r_C'], plateau=result['plateau_abs_dev_q_only'])), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
