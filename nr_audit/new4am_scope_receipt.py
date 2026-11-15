"""NEW-4am（N41）：范围收紧的收据。只登记身份，不做任何计算。

记录经作者授权从稿件中删去的图、陈述与标签，被取代图件与存档源文件的 SHA-256，以及本轮新增的两个数字宏。
图件文件、S3 源文件与历史收据都原样保留；本脚本只读取它们的字节。

运行：python nr_audit/new4am_scope_receipt.py
"""
import hashlib
import json
import re
from pathlib import Path

from text_identity import content_sha256

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'nr_audit/results/new4am_scope.json'
MAIN = 'paper/flatten_curve_analysis_cn.tex'
SUPP = 'paper/flatten_curve_supplement_cn.tex'
ARCHIVED = 'paper/supplement_sections/S3_inflection.tex'

REMOVED_FIGURES = {
    'S8': dict(label='fig:xian_heatmaps', pdf='paper/figures/new4w/S8.pdf',
               former_tex='paper/supplement_sections/S6_xian.tex'),
    'S5': dict(label='fig:s1:lambda-sensitivity', pdf='paper/figures/new4t/S5.pdf', former_tex=ARCHIVED),
}
REMOVED_STATEMENTS = ['prop:dom:floor', 'prop:reference-population', 'prop:s1:lambda-sensitivity']
REMOVED_LABELS = sorted(REMOVED_STATEMENTS + [
    'app:lambda', 'eq:dom:Nfloor', 'eq:lambda-q0-sign', 'eq:s1:lambda', 'eq:s1:lambda-q0-stationary',
    'eq:small-threshold', 'fig:s1:lambda-sensitivity', 'fig:xian_heatmaps', 'sec:dom:region', 'sec:dominance',
    'sec:s1:inflection-position', 'sec:sup:baseline-contact-scan', 'sec:sup:inflection'])
NEW_MACROS = ['\\nrXianCutContactPct', '\\nrXianSingleDiffM']


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def input_files(main):
    """主文件及其 \\input 的各节源文件（相对仓库根目录）。"""
    text = (ROOT / main).read_text(encoding='utf-8')
    names = re.findall(r'^\\input\{((?:sections|appendices|supplement_sections)/[^}]+)\}', text, flags=re.M)
    return [main] + [f'paper/{n}.tex' for n in names]


def main():
    files = {m: input_files(m) for m in (MAIN, SUPP)}
    assert ARCHIVED not in files[SUPP]
    current = ''.join((ROOT / f).read_text(encoding='utf-8') for fs in files.values() for f in fs)
    assert not [lab for lab in REMOVED_LABELS if f'\\label{{{lab}}}' in current]
    figures = {k: dict(v, pdf_sha256=sha(v['pdf'])) for k, v in REMOVED_FIGURES.items()}
    receipt = dict(
        authorization='AGENTS.md N41（NEW-4am）', pre_cut_tag='pre-scope-cut-20261115',
        base_commit='6c022c8', scientific_activity=dict(ode_solves=0, optimization_solves=0, fits=0, redraws=0),
        current_inputs=files,
        archived_source=dict(path=ARCHIVED, content_sha256=content_sha256((ROOT / ARCHIVED).read_bytes()),
                             note='原样保留，不再由补充主文件 \\input；恢复时加回该行并撤销三处连带改动'),
        removed_figures=figures, removed_statements=REMOVED_STATEMENTS, removed_labels=REMOVED_LABELS,
        new_macros=NEW_MACROS, macro_source='nr_audit/results/new4w/xian_theta001.json')
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(f'写出 {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
