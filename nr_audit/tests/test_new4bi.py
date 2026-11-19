"""NEW-4bi（N63）：r_cont 改记 r_*，TDINN 控制函数记为 c_D、q_D；补充图 S5 图例只改这一记号。"""
import hashlib
import json

from conftest import SRC

ROOT = SRC.ROOT


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def active_tex():
    files = sorted((ROOT / 'paper/sections').glob('*.tex')) + sorted((ROOT / 'paper/appendices').glob('*.tex'))
    files += [p for p in sorted((ROOT / 'paper/supplement_sections').glob('*.tex'))
              if not p.name.startswith(('S3_', 'S4_'))]           # S3、S4 为存档文件，不再 \input
    files += [ROOT / 'paper/flatten_curve_analysis_cn.tex', ROOT / 'paper/flatten_curve_supplement_cn.tex']
    return {p.name: p.read_text(encoding='utf-8') for p in files}


def test_notation():
    tex = active_tex()
    allt = ''.join(tex.values())
    assert 'r_{\\rm cont}' not in allt and allt.count('r_*') >= 38
    assert '_{\\rm TDINN}' not in allt
    xt = tex['07_xian.tex']
    assert '（这里记为 $c_{\\rm D}(t),q_{\\rm D}(t)$）' in xt
    assert 'c_{\\rm D}(t)&=(12.8872-3.4625)e^{-(0.0463t)^2}+3.4625' in xt
    assert 'q_{\\rm D}(t)&=(0.3230-0.9844)e^{-(0.0452t)^2}+0.9844' in xt
    assert 'r_*(b)=\\frac{16}{\\bigl(b+\\sqrt{b^2-8b+8}\\bigr)^2}' in tex['05_quadratic_cost.tex']
    # S_sw、zeta_sw 不改
    assert allt.count('S_{\\rm sw}') >= 70 and 'zeta_{\\rm sw}' in allt


def test_figure_s5_relabel():
    s5 = (ROOT / 'paper/supplement_sections/S5_weight_structure.tex').read_text(encoding='utf-8')
    assert 'figures/new4bi/S6.pdf' in s5 and 'figures/new4t/S6.pdf' not in s5
    rec = json.loads((SRC.HERE / 'results/new4bi_notation.json').read_text(encoding='utf-8'))
    f = rec['figures']['fig:sup:phase-detail']
    assert f['reproduced_identical'] and f['current_pdf'] == 'paper/figures/new4t/S6.pdf'
    assert f['current_pdf_sha256'] == f['reproduced_sha256'] == sha(ROOT / f['current_pdf'])
    assert f['text_change'] == dict(old='$r_{\\rm cont}$', new='$r_*$', count=1) and f['other_texts_unchanged']
    assert sha(ROOT / f['pdf']) == f['pdf_sha256']
    assert rec['scientific_activity'] == dict(ode_solves=0, optimization_solves=0, fits=0, classification_solves=0)
    assert all(v == 0 for k, v in f['source_checks'].items() if k.startswith('new_'))
