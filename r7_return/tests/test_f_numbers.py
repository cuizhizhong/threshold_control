"""(f) R7-3：make_numbers.py 生成的宏与全精度 JSON 一致。
宏名只用字母且不重复；tex 中的宏与 JSON 一一对应；数字宏的展示值与全精度值在展示位数内一致。
需先运行 r7_3_numerics.py 与 make_numbers.py（结果已随提交保存）。"""
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(HERE)
TEX = os.path.join(ROOT, 'paper', 'generated', 'r7_numbers.tex')
FULL = os.path.join(HERE, 'results', 'r7_numbers_full.json')

pytestmark = pytest.mark.skipif(not (os.path.exists(TEX) and os.path.exists(FULL)),
                                reason='尚未生成 r7_numbers.tex')


def _tex_macros():
    out = {}
    with open(TEX, encoding='utf-8') as fh:
        for line in fh:
            if line.startswith('%') or not line.strip():
                continue
            m = re.fullmatch(r'\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}\n?', line)
            assert m, f'不是单行 \\newcommand：{line!r}'
            assert m.group(1) not in out
            out[m.group(1)] = m.group(2)
    return out


def test_names_and_one_to_one():
    tex = _tex_macros()
    with open(FULL, encoding='utf-8') as fh:
        full = json.load(fh)
    assert set(tex) == set(full['macros'])
    assert all(re.fullmatch(r'rs[A-Za-z]+', k) for k in tex)
    assert full['n_macros'] == len(tex)


def _parse(display):
    s = display.replace(r'\ensuremath{', '').rstrip('}')
    m = re.fullmatch(r'(-?[0-9.]+)\\times10\^\{(-?[0-9]+)', s)
    if m:
        return float(m.group(1)) * 10 ** int(m.group(2)), len(m.group(1).replace('-', '').replace('.', '').lstrip('0'))
    try:
        return float(s), None
    except ValueError:
        return None, None


def test_display_matches_full_value():
    with open(FULL, encoding='utf-8') as fh:
        full = json.load(fh)
    for name, it in full['macros'].items():
        v = it['value']
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        shown, _ = _parse(it['display'])
        if shown is None:
            continue
        unit = it['unit']
        if unit == '10^6 人':
            v = v / 1e6
        elif unit == '%':
            v = 100 * v
        # 展示值与全精度值之差不超过展示末位的半个单位（科学记数按尾数的末位）
        d = it['display'].replace(r'\ensuremath{', '')
        m = re.fullmatch(r'-?[0-9]+(?:\.([0-9]+))?\\times10\^\{(-?[0-9]+)\}\}', d)
        if m:
            dec = len(m.group(1) or '')
            assert abs(shown - v) <= 0.5 * 10 ** (int(m.group(2)) - dec) * (1 + 1e-9), name
        else:
            dec = len(d.split('.')[1].rstrip('}')) if '.' in d else 0
            assert abs(shown - v) <= 0.5 * 10 ** (-dec) * (1 + 1e-9), name
