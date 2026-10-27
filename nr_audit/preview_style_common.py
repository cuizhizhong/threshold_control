"""本轮独立风格预览的共用样式与输出工具；不写正式图件或历史收据。"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

import plot_xian_fig2_style as F2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper/tmp/supplement_style_preview_20261027'
MATERIALS = ROOT / 'nr_audit/results/new4t_figures'
STYLE, RC, MM = F2.STYLE, F2.RC, F2.MM
TEXT_WIDTH_IN = F2.TEXT_WIDTH_PT / 72.0
SOURCE_REF = 'pipeline-final-20261006'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_blob(path):
    return subprocess.check_output(['git', 'show', f'{SOURCE_REF}:{path}'], cwd=ROOT)


def material_file(name, preview_name=None):
    """优先读取已入库材料并先验身份；临时目录仅供入稿前的预览使用。"""
    stored = MATERIALS / name
    if stored.exists():
        manifest = ROOT / 'nr_audit/results/new4t_figures.json'
        if manifest.exists():
            rec = json.loads(manifest.read_text(encoding='utf-8'))['materials'][stored.relative_to(ROOT).as_posix()]
            if sha(stored) != rec['sha256']:
                raise ValueError(f'NEW-4t材料身份不匹配：{stored.name}')
        return stored
    return OUT / (preview_name or name)


def palette():
    """MATLAB原生parula(256)，由一次独立样式查询导出。"""
    rgb = np.asarray(json.loads(material_file('parula256.json').read_text(encoding='utf-8')), dtype=float)
    assert rgb.shape == (256, 3) and np.all((rgb >= 0) & (rgb <= 1))
    return ListedColormap(rgb, name='matlab_parula256_exact')


def array_sha(values):
    a = np.ascontiguousarray(values, dtype=np.float64)
    return hashlib.sha256(a.tobytes()).hexdigest()


def save(fig, name, checks, inputs, old_pdf):
    """保存独立预览；字体、坐标与对象数量纳入本轮收据。"""
    OUT.mkdir(parents=True, exist_ok=True)
    old_pdf = Path(old_pdf)
    if not old_pdf.is_absolute():
        old_pdf = ROOT / old_pdf
    old_sha = sha(old_pdf)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    text_bounds = []
    for item in fig.findobj(matplotlib.text.Text):
        if not item.get_visible() or not item.get_text():
            continue
        box = item.get_window_extent(renderer)
        text_bounds.append(dict(text=item.get_text(), bounds=[float(x) for x in box.extents]))
    axes = [dict(xlim=list(ax.get_xlim()), ylim=list(ax.get_ylim()),
                 xscale=ax.get_xscale(), yscale=ax.get_yscale(), title=ax.get_title(),
                 lines=len(ax.lines), patches=len(ax.patches), collections=len(ax.collections))
            for ax in fig.axes]
    pdf, png = OUT / f'{name}.pdf', OUT / f'{name}.png'
    fig.savefig(pdf, dpi=600, metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(png, dpi=300)
    fonts = sorted(set(f.decode() for f in re.findall(rb'/BaseFont\s*/([A-Za-z0-9+\-]+)', pdf.read_bytes())))
    assert fonts and all(re.search(r'cm(r|mi|sy|ex)10', f, re.I) for f in fonts), fonts
    assert sha(old_pdf) == old_sha
    receipt = dict(figure=name, preview_only=True, style=STYLE,
                   old_pdf=old_pdf.relative_to(ROOT).as_posix(), old_pdf_sha256=old_sha,
                   inputs=inputs, checks=checks, axes=axes, fonts=fonts,
                   size_mm=[float(v / MM) for v in fig.get_size_inches()],
                   output_sha256={p.name: sha(p) for p in (pdf, png)}, text_bounds_px=text_bounds)
    (OUT / f'{name}.receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    plt.close(fig)
    print(f'{name}: saved independent PDF/PNG preview')
    return receipt
