"""NEW-4w W3：西安设计阈值改为 η = 0.001N 后的收敛核验（N33）。

复用 audit_convergence.py 的三项检查（控制网格、状态网格、积分容差三档），只把西安参数的 η 换成 0.001N，
并把西安的转折附近权重换成新的 B→C 括区两侧（括区取自 results/new4w/xian_theta001.json）。基准参数不变。
原 results/convergence.json 只读保留；本脚本写 results/new4w/convergence.json 与 convergence.md。

运行（仓库根目录，先运行 new4w_xian_threshold.py）：python -X utf8 nr_audit/new4w_convergence.py
"""
import json

import audit_convergence as AC
import audit_common
import params as PR
from audit_common import RESULTS, plain, git_head

OUT = RESULTS / 'new4w'


def main():
    w3 = json.loads((OUT / 'xian_theta001.json').read_text(encoding='utf-8'))
    bc = w3['weights']['B_to_C']
    r_bc = 0.5 * (bc['lo'] + bc['hi'])
    X1 = PR.XIAN.with_(eta=w3['settings']['eta'])
    PR.XIAN = X1
    PR.CASES['xian'] = X1
    old_weights = AC.WEIGHTS['xian']
    AC.WEIGHTS['xian'] = (2.0, 2.65, 2.74, round(r_bc - 0.04, 2), round(r_bc + 0.21, 2))

    def dump(name, obj):
        obj = dict(script='nr_audit/new4w_convergence.py', git_head=git_head(), eta_xian=X1.eta,
                   weights_xian=AC.WEIGHTS['xian'], weights_xian_old=old_weights, **obj)
        (OUT / name).write_text(json.dumps(plain(obj), ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')

    AC.dump = dump
    AC.RESULTS = OUT
    AC.main()


if __name__ == '__main__':
    main()
