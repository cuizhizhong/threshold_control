"""NEW-2：只读固定JSON，派生首次向下I=1终点、后续衰减充分条件和剩余感染尾界。"""
import csv
import json
import math
from audit_common import ROOT, RESULTS, dump
import params as PR
import import_return_numbers as IR


def remaining_bound(P, U, I):
    """U<Sc为充分条件；不满足时不截分母，不产生伪上界。"""
    if not math.isfinite(U) or not math.isfinite(I) or U < 0 or I < 0:
        raise ValueError('终点状态必须非负且有限')
    if U >= P.S_c:
        return dict(applicable=False, decay_rate=None, B_persons=None)
    rate = P.gamma * (1.0 - U / P.S_c)
    return dict(applicable=True, decay_rate=rate,
                B_persons=P.beta * P.c0 * U * I / (P.N * rate))


def build_audit(source_path=None, convergence_path=None, repository=None):
    data, identity = IR.read_source(source_path or ROOT / IR.SOURCE_PATH, repository)
    convergence, convergence_identity = IR.read_convergence(convergence_path, repository)
    rows = []
    for case, P in PR.CASES.items():
        for stay in IR.STAYS:
            for policy in IR.LAWS:
                key = f'{case}|{stay}|{policy}'
                v = data['runs'][key]
                U, S, Sq, I = (v[k] for k in ('U_term', 'S_term', 'Sq_term', 'I_term'))
                if not math.isclose(U, S + Sq, rel_tol=1e-13, abs_tol=1e-10):
                    raise ValueError(f'U与S+Sq不符: {key}')
                bound = remaining_bound(P, U, I)
                if abs(I - 1.0) > 1e-8:
                    raise ValueError(f'未到达I=1事件: {key}')
                rows.append(dict(case=case, model='exponential_return', mean_stay_days=stay,
                    policy=policy, T_cut_days=v['t_end'], C_cut_persons=v['C_term'],
                    S_cut_persons=S, Sq_cut_persons=Sq, I_cut_persons=I,
                    U_cut_persons=U, S_c_persons=P.S_c, U_over_Sc=U/P.S_c,
                    post_cut_growth_rate=P.gamma*(S/P.S_c-1),
                    exit_threshold_crossing=v['crossing'], **bound))
    groups = {}
    for case in PR.CASES:
        groups[case] = {}
        for stay in IR.STAYS:
            these = [r for r in rows if r['case']==case and r['mean_stay_days']==stay]
            if not all(r['applicable'] for r in these):
                raise ValueError(f'既有18行未全部满足尾界充分条件: {case}/{stay}')
            B = max(r['B_persons'] for r in these)
            groups[case][str(stay)] = dict(B_max_persons=B, B_display_up=f'{math.ceil(B*1000)/1000:.3f}')
    out = dict(description=__doc__, source=dict(path=IR.SOURCE_PATH, commit=IR.SOURCE_COMMIT, **identity),
               endpoint='first downward I=1 after exit', new_ode_solves=0,
               condition='baseline forever after exit; U_cut < S_c',
               formula='B=beta*c0*U_cut*I_cut/(N*gamma*(1-U_cut/S_c))',
               numeric_not_interval_certification=True, rows=rows, groups=groups,
               convergence_source=convergence_identity,
               solver_tolerance_max_rel_tight=convergence['tolerance_summary']['max_rel_change_tight'])
    return out


def validate_endpoint_sources(ep, convergence_path=None, repository=None):
    """宏生成前验证第二输入及派生字段，数值仍从已验证ep读取。"""
    convergence, identity = IR.read_convergence(convergence_path, repository)
    recorded = ep.get('convergence_source', {})
    for key in ('path', 'commit', 'archived_commit', 'sha256', 'blob'):
        if recorded.get(key) != identity[key]:
            raise ValueError(f'派生终点审计的收敛来源身份不符: {key}')
    if ep.get('solver_tolerance_max_rel_tight') != convergence['tolerance_summary']['max_rel_change_tight']:
        raise ValueError('派生终点审计的容差字段与已核验来源不符')
    return ep


def main():
    out = build_audit()
    rows, groups = out['rows'], out['groups']
    dump('new_return_endpoint.json', out)
    with open(RESULTS/'new_return_endpoint.csv','w',encoding='utf-8-sig',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    print(json.dumps(dict(n_rows=len(rows),groups=groups,
        U_over_Sc_range=[min(r['U_over_Sc'] for r in rows),max(r['U_over_Sc'] for r in rows)])))


if __name__ == '__main__':
    main()
