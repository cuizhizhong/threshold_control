"""NR-3 N3：成本最优控制在权重网格上的结构转折（补充表 S5）的复核与加密。

结构类别（不考虑能力约束，w_c = 1，r = w_q/w_c；与原 phase.json 的定义一致：有连续切换 / 有跳变切换 / 无切换）：
    A  在 S_sw 处连续切换（启动时为仅隔离控制），此后为一段连续的内部解
    A' 在 S_sw 处连续切换，随后在 S_sw 稍下方由一个内部解跳到另一个内部解（原 161 点网格上没有出现，原分类中归于 A）
    B  切换提前（z > S_sw/S_c）并跳变（启动时为仅隔离控制）
    C  没有仅隔离段（启动时已两者并用，无切换）
    ?  其他（如实报告）
步骤：(1) 用原 phase.json 读出 161 个网格点的类别序列；(2) 用本模块对全部 161 个网格点重新分类（N_z = N_local = 2001），
列出与原分类不同的点，并核对表 S5 的四对相邻网格点；(3) 在本模块类别不同的每对相邻网格点之间取 20 个对数等距的细分点
分类，找出每个观察到的改变区间，分别在 log r 上二分到宽度 < 1e-3（不假定类别对 r 单调）；(4) 括区两端用 N_z = 8001、
16001 复核类别，并记录跳变的位置与大小。
结论只是“所检验网格与精度下的转折括区”。

运行：conda run --no-capture-output -n thesis python nr_audit/audit_weights.py
输出：results/weight_brackets.json、results/weight_brackets.md
"""
import math

import numpy as np

import allocation as AL
import params as PR
import sources as SRC
import state_integrals as SI
from audit_common import RESULTS, dump

GRID = 0.1 * 200.0 ** (np.arange(161) / 160.0)       # 原网格：r ∈ [0.1, 20] 内 161 个对数等距点
TABLE_S5 = {'base': [(3.13, 3.24, 'A', 'B'), (13.00, 13.44, 'B', 'C')],
            'xian': [(2.65, 2.74, 'A', 'B'), (7.41, 7.66, 'B', 'C')]}
WIDTH = 1e-3


def classify(P, r, N_z=4001, N_local=4001):
    """结构分类。除 Policy 的 N_z 网格扫描外，另在 S_sw 两侧 ±2% 与 ±0.1% 的区间各用 N_local 点网格局部扫描
    （A→B 转折附近的内部—内部跳变只占很窄的状态区间、并贴近 S_sw，粗网格可能漏检）。"""
    pol = SI.Policy(P, 'opt', wc=1.0, wq=float(r), N_z=N_z)
    zsw = AL.z_sw_formula(P.z_bar)
    zb, xm, hh = P.z_bar, pol.x_min, pol.h

    def poly_at_end(z, end):
        lo, hi, _, _ = AL.x_bounds_raw(z, xm, hh)
        return float(np.polyval(AL.stationary_poly_x(z, zb, 1.0, float(r), 0.0), hi if end == 'hi' else lo))
    bps = list(pol.structure['breakpoints'])
    for w in (0.02, 1e-3):        # 两个尺度：±2% 与 ±0.1%（后者分辨贴近 S_sw 的跳变）
        loc = AL.scan_structure(pol.law.full, zsw * (1 - w), min(zsw * (1 + w), pol.z_star * (1 - 1e-12)), N_local, poly_at_end)
        for b in loc['breakpoints']:
            if all(abs(b['z'] - c['z']) > 1e-9 * b['z'] for c in bps):
                bps.append(b)
    bps.sort(key=lambda b: -b['z'])                       # 自 S* 向 S_c（时间顺序）
    top = pol.law.full(pol.z_star * (1 - 1e-12))[2]['label']
    info = dict(r=float(r), top_label=top, breakpoints=bps, steep_points=pol.structure['steep_points'], N_z=N_z,
                N_local=N_local)
    at_sw = [b for b in bps if b['continuous'] and abs(b['z'] - zsw) <= 1e-9 * zsw]
    int_jumps = [b for b in bps if not b['continuous'] and b['label_left'] == 'int' and b['label_right'] == 'int']
    if top == 'hi' and at_sw and len(bps) == 1:
        c = 'A'
    elif top == 'hi' and at_sw and int_jumps and len(bps) == 1 + len(int_jumps) and all(b['z'] < zsw for b in int_jumps):
        c = "A'"
        info['int_jumps'] = [dict(z=b['z'], size=abs(b['x_right'] - b['x_left'])) for b in int_jumps]
    elif top == 'hi' and bps and not bps[0]['continuous'] and bps[0]['label_right'] == 'hi' and bps[0]['z'] > zsw:
        c = 'B'
        info['jump_size'] = abs(bps[0]['x_right'] - bps[0]['x_left'])
        info['jump_z'] = bps[0]['z']
        info['n_other_breakpoints'] = len(bps) - 1
    elif top != 'hi' and not any('hi' in (b['label_left'], b['label_right']) for b in bps):
        c = 'C'
    else:
        c = '?'
    info['class'] = c
    return c, info


def original_classes(key):
    sw = SRC.load_json('phase')[key]['switches']
    by_r = {}
    for s in sw:
        by_r.setdefault(round(s['r'], 12), []).append(s)
    out = []
    for r in GRID:
        ss = by_r.get(round(r, 12), [])
        out.append('C' if not ss else ('B' if any(s['jump'] for s in ss) else 'A') if len(ss) == 1 else '?')
    return out


def nearest_grid(v):
    return int(np.argmin(np.abs(GRID - v)))


def refine(P, a, b, ca, cb, log):
    """在 [a, b] 内对 log r 二分，直到宽度 < WIDTH；返回括区与两端的分类信息。"""
    ia, ib = None, None
    while b - a >= WIDTH:
        m = math.sqrt(a * b)
        cm, im = classify(P, m)
        log.append(im)
        if cm == ca:
            a, ia = m, im
        elif cm == cb:
            b, ib = m, im
        else:
            return dict(lo=a, hi=b, status='unresolved', class_mid=cm, info_mid=im)
    return dict(lo=a, hi=b, width=b - a, status='resolved', info_lo=ia, info_hi=ib)


def main():
    out = {}
    for case, key in (('base', 'baseline'), ('xian', 'xian')):
        P = PR.CASES[case]
        orig = original_classes(key)
        ours = [classify(P, r, N_z=2001, N_local=2001) for r in GRID]
        cls = [c for c, _ in ours]
        res = dict(original_sequence=''.join(orig), nr_audit_sequence=' '.join(cls),
                   grid_disagreements=[dict(k=k, r=float(GRID[k]), original=orig[k], nr_audit=cls[k],
                                            int_jumps=ours[k][1].get('int_jumps')) for k in range(161) if orig[k] != cls[k]],
                   table_S5=[], changes=[])
        for r_lo, r_hi, c_lo, c_hi in TABLE_S5[case]:
            k = nearest_grid(r_lo)
            res['table_S5'].append(dict(r_lo=r_lo, r_hi=r_hi, table=(c_lo, c_hi), grid=(float(GRID[k]), float(GRID[k + 1])),
                                        original=(orig[k], orig[k + 1]), nr_audit=(cls[k], cls[k + 1])))
        for k in range(160):
            if cls[k] == cls[k + 1]:
                continue
            sub = np.exp(np.linspace(math.log(GRID[k]), math.log(GRID[k + 1]), 21))
            sub_cls = [classify(P, r)[0] for r in sub]
            log, brackets = [], []
            for j in range(20):
                if sub_cls[j] == sub_cls[j + 1]:
                    continue
                br = refine(P, float(sub[j]), float(sub[j + 1]), sub_cls[j], sub_cls[j + 1], log)
                br.update(from_=sub_cls[j], to=sub_cls[j + 1])
                if br['status'] == 'resolved':
                    br['check_fine'] = {f'{n}': dict(lo=classify(P, br['lo'], N_z=n, N_local=n)[0],
                                                     hi=classify(P, br['hi'], N_z=n, N_local=n)[0]) for n in (8001, 16001)}
                    br['stable_fine'] = all(v == dict(lo=br['from_'], hi=br['to']) for v in br['check_fine'].values())
                    for side in ('info_lo', 'info_hi'):
                        if br.get(side):
                            br[side] = {kk: br[side].get(kk) for kk in ('class', 'r', 'jump_z', 'jump_size', 'int_jumps')}
                brackets.append(br)
            res['changes'].append(dict(grid=(k, float(GRID[k]), float(GRID[k + 1])), grid_classes=(cls[k], cls[k + 1]),
                                       subdivision=[dict(r=float(r), cls=c) for r, c in zip(sub, sub_cls)], brackets=brackets))
        out[case] = res
    dump('weight_brackets.json', dict(description=__doc__.split('\n\n')[0], width_target=WIDTH,
                                      grid='r_k = 0.1·200^(k/160)，k = 0…160；全网格分类用 N_z = N_local = 2001，细分与二分用 4001，'
                                           '括区两端另用 8001、16001 复核', cases=out))
    L = ['# NR-3 N3：权重转折的复核与加密', '', f"目标括区宽度 < {WIDTH}；类别 A、A'、B、C 见 audit_weights.py 说明。", '']
    for case, res in out.items():
        L += [f'## {case}', '', f"原网格类别：`{res['original_sequence']}`", '',
              f"与原分类不同的网格点：{len(res['grid_disagreements'])} 个" +
              ('：' + '，'.join(f"r = {g['r']:.4f}（原 {g['original']}，本模块 {g['nr_audit']}）" for g in res['grid_disagreements'])
               if res['grid_disagreements'] else ''), '',
              '| 表 S5 | 网格点 | 原类别 | 本模块类别 |', '|---|---|---|---|']
        for t in res['table_S5']:
            L.append(f"| {t['r_lo']}–{t['r_hi']}（{t['table'][0]}→{t['table'][1]}） | {t['grid'][0]:.6f}–{t['grid'][1]:.6f} | "
                     f"{''.join(t['original'])} | {' '.join(t['nr_audit'])} |")
        L += ['', '| 网格区间 | 网格类别 | 加密括区 | 状态 | N_z=8001、16001 复核 | 括区端点的跳变 |', '|---|---|---|---|---|---|']
        for c in res['changes']:
            for b in c['brackets']:
                jumps = []
                for side in ('info_lo', 'info_hi'):
                    i = b.get(side) or {}
                    if i.get('jump_z'):
                        jumps.append(f"{side[5:]}：hi→int 于 z = {i['jump_z']:.6f}，Δx = {i['jump_size']:.4f}")
                    if i.get('int_jumps'):
                        jumps.append(f"{side[5:]}：int→int 于 z = {i['int_jumps'][0]['z']:.6f}，Δx = {i['int_jumps'][0]['size']:.4f}")
                L.append(f"| {c['grid'][1]:.6f}–{c['grid'][2]:.6f} | {c['grid_classes'][0]}→{c['grid_classes'][1]} | "
                         f"[{b['lo']:.6f}, {b['hi']:.6f}]（{b['from_']}→{b['to']}） | {b['status']} | {b.get('stable_fine')} | "
                         f"{'；'.join(jumps) or '—'} |")
        L.append('')
    (RESULTS / 'weight_brackets.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
