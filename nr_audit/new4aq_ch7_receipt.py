"""NEW-4aq（N45）：第 7 章与补充西安一节逐句修订的收据。只登记身份与新读数的来源，不做计算。

补充图 fig:xian_eta_sens 经作者同意不再入稿（图件文件只读保留）；第 7.3 节新写出的常规控制读数取自已登记的
results/new4w/xian_theta001.json 的 strategies 字段（与表 4 同源）。

运行：python nr_audit/new4aq_ch7_receipt.py
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'nr_audit/results/new4aq_ch7.json'
SRC = 'nr_audit/results/new4w/xian_theta001.json'
REMOVED_FIGURE = dict(label='fig:xian_eta_sens', pdf='paper/figures/new4o/xian_eta_sensitivity.pdf',
                      former_tex='paper/supplement_sections/S6_xian.tex')


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main():
    s6 = (ROOT / REMOVED_FIGURE['former_tex']).read_text(encoding='utf-8')
    assert REMOVED_FIGURE['label'] not in s6 and 'xian_eta_sensitivity' not in s6
    st = json.loads((ROOT / SRC).read_text(encoding='utf-8'))['strategies']
    eta = 0.001 * 13163000
    readings = dict(
        routine_peak_I=st['routine']['peak_I'], routine_peak_over_eta=st['routine']['peak_I'] / eta,
        routine_total=st['routine']['total'], q_only_total=st['q_only']['total'], opt_total=st['opt']['total'],
        q_only_over_routine=st['q_only']['total'] / st['routine']['total'],
        opt_over_routine=st['opt']['total'] / st['routine']['total'],
        q_only_t_end=st['q_only']['t_end'], opt_t_end=st['opt']['t_end'], tdinn_t_end=st['TDINN']['t_end'])
    receipt = dict(authorization='AGENTS.md N45（NEW-4aq）', base_commit='9a404b9',
                   scientific_activity=dict(ode_solves=0, optimization_solves=0, fits=0, redraws=0),
                   removed_figure=dict(REMOVED_FIGURE, pdf_sha256=sha(REMOVED_FIGURE['pdf'])),
                   readings_source=dict(path=SRC, sha256=sha(SRC)), readings=readings)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(readings, indent=1))


if __name__ == '__main__':
    main()
