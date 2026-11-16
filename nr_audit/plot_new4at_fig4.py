"""NEW-4at（N48）：删去显式控制族后，正文图 4（fig:joint:compare）只画三种控制。

复用 NEW-4s 的绘图函数 plot_new4s_figures.joint_compare 与同一组既有轨迹（只读，使用前按 NEW-4s 收据核对 SHA-256），
只从曲线集合中去掉显式族 alpha = 0.5；字体、配色、线型、版面、坐标范围与参照线不变（横轴上限由最长的仅减少接触决定，
去掉 alpha = 0.5 后不变）。不求解模型。

运行：python -X utf8 nr_audit/plot_new4at_fig4.py。输出 paper/figures/new4at/joint_compare_baseline.pdf、
paper/tmp/new4at/joint_compare_baseline.png（预览，不入库）与 results/new4at_fig4.json。
原图 paper/figures/new4s/joint_compare_baseline.pdf 与收据 results/new4s_figures.json 只读保留。
"""
import json
import re

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

import plot_new4s_figures as S
import plot_xian_fig2_style as F2
from audit_common import ROOT, RESULTS, dump

OUT = ROOT / 'paper' / 'figures' / 'new4at'
PREVIEW = ROOT / 'paper' / 'tmp' / 'new4at'
OLD_FIG = ROOT / 'paper' / 'figures' / 'new4s' / 'joint_compare_baseline.pdf'
REMOVED = 'alpha_0.5'


def main():
    old = json.loads((RESULTS / 'new4s_figures.json').read_text(encoding='utf-8'))
    inputs = {f'{S.JX.relative_to(ROOT).as_posix()}/{n}': S.sha(S.JX / n) for n in S.INPUTS}
    assert inputs == old['inputs_sha256'], '图 4 的输入与 NEW-4s 收据不一致'
    old_tmax = old['checks']['tmax']
    del S.LAWS[REMOVED]
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(F2.RC):
        fig, checks = S.joint_compare()
        pdf = OUT / 'joint_compare_baseline.pdf'
        fig.savefig(pdf, metadata={'CreationDate': None, 'ModDate': None})
        fig.savefig(PREVIEW / 'joint_compare_baseline.png', dpi=300)
        size = [round(float(v) / S.MM, 2) for v in fig.get_size_inches()]
        plt.close(fig)
    assert checks['tmax'] == old_tmax
    for key, v in checks['laws'].items():                   # 其余三种控制的轨迹记录与 NEW-4s 相同
        assert v == old['checks']['laws'][key], key
    fonts = sorted({f.decode() for f in re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-]+)', pdf.read_bytes())})
    assert all(re.search(r'cm(r|mi|sy|ex)10', f, re.I) for f in fonts), fonts
    rec = dict(script='nr_audit/plot_new4at_fig4.py', authorization='AGENTS.md N48（NEW-4at）',
               reuses='nr_audit/plot_new4s_figures.py: joint_compare', removed_law=REMOVED,
               inputs_sha256=inputs, superseded=dict(path=OLD_FIG.relative_to(ROOT).as_posix(), sha256=S.sha(OLD_FIG)),
               outputs={pdf.relative_to(ROOT).as_posix(): dict(sha256=S.sha(pdf), size_mm=size, fonts=fonts)},
               checks=checks, scientific_activity=dict(ode_solves=0, optimization_solves=0, fits=0))
    dump('new4at_fig4.json', rec)
    print(json.dumps(dict(outputs=rec['outputs'], laws=list(checks['laws'])), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
