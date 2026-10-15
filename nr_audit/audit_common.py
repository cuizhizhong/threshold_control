"""NR-3 各审计脚本的公共部分：结果写出、稿件表格的读取、显示值与全精度值的舍入核对。"""
import datetime
import json
import math
import pathlib
import re
import subprocess

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / 'results'


def plain(v):
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, np.ndarray):
        return [plain(w) for w in v.tolist()]
    if isinstance(v, dict):
        return {str(k): plain(w) for k, w in v.items() if not str(k).startswith('_')}
    if isinstance(v, (list, tuple)):
        return [plain(w) for w in v]
    if isinstance(v, float) and not math.isfinite(v):
        return None
    return v


def git_head():
    try:
        return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return None


def dump(name, obj):
    RESULTS.mkdir(parents=True, exist_ok=True)
    obj = dict(generated=datetime.datetime.now().isoformat(timespec='seconds'), git_head=git_head(), **obj)
    (RESULTS / name).write_text(json.dumps(plain(obj), ensure_ascii=False, indent=1), encoding='utf-8')


def rel(a, b):
    return abs(a - b) / abs(b) if b != 0 else abs(a - b)


# ---------------------------------------------------------------- 稿件表格
def tex_table_rows(path, label):
    """读取含 \\label{label} 的表格环境中 \\midrule 与 \\bottomrule 之间、含 & 的行，返回单元格字符串列表。"""
    text = (ROOT / path).read_text(encoding='utf-8')
    k = text.index('\\label{' + label + '}')
    a = text.rfind('\\begin{table', 0, k)
    b = text.index('\\end{table', k)
    body = text[a:b]
    body = body[body.index('\\midrule'):body.index('\\bottomrule')]
    rows = []
    for line in body.split('\\\\'):
        line = line.replace('\\midrule', '').strip()
        if '&' not in line or '\\multicolumn' in line:
            continue
        rows.append([c.strip() for c in line.split('&')])
    return rows


def num(cell):
    """单元格中的数（去掉 \\num{}、$、≈、%、逗号与 {---}）；不是数时返回 None。"""
    s = cell.replace('\\num{', '').replace('}', '').replace('{', '').replace('$', '').replace('\\approx', '')
    s = s.replace(',', '').replace('\\%', '').strip()
    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------------------------------------------- 显示值核对
def display_unit(display):
    """显示串的末位单位：'300.4' → 0.1；'2106' → 1；'1.53e6' → 1e4；'5.04' → 0.01。"""
    s = display.strip().lower()
    if 'e' in s:
        mant, ex = s.split('e')
        d = len(mant.split('.')[1]) if '.' in mant else 0
        return 10.0 ** (int(ex) - d)
    d = len(s.split('.')[1]) if '.' in s else 0
    return 10.0 ** (-d)


class Registry:
    """稿件中保留数字的登记：显示值、全精度复算值、来源与判定。
    判定：'consistent'（复算值按显示位数舍入后与显示值一致）；'display_differs'（不一致但相对差 ≤ 1%）；
    'stop'（相对差 > 1%，按 NR 计划 5.2 节停止自动入稿）。"""

    def __init__(self):
        self.rows = []

    def add(self, id_, where, display, value, unit='', source='', note='', old=None, old_source=None):
        d = float(display)
        u = display_unit(display)
        ok = abs(value - d) <= 0.5 * u * (1 + 1e-9) + 1e-12 * abs(d)
        r = rel(value, d)
        status = 'consistent' if ok else ('stop' if r > 0.01 else 'display_differs')
        row = dict(id=id_, where=where, display=display, value=value, unit=unit, status=status, rel_to_display=r,
                   source=source, note=note)
        if old is not None:
            row.update(old=old, old_source=old_source, rel_to_old=rel(value, old))
        self.rows.append(row)
        return row

    def summary(self):
        out = {}
        for r in self.rows:
            out[r['status']] = out.get(r['status'], 0) + 1
        return out
