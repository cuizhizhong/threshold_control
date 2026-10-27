"""生成本轮预览：主图6/8仅换连续色带，补图样式由独立模块生成。

运行 python -X utf8 nr_audit/preview_supplement_style.py。
仅写paper/tmp/supplement_style_preview_20261027，不替换正式图、不运行模型求解。
"""
import hashlib
import json

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.collections import QuadMesh

import plot_new4p_figures as P
from preview_style_common import ROOT, OUT, RC, palette, save, sha, array_sha, material_file


def geometry(fig):
    """连续色带变更前后比较全部可见曲线、曲面与坐标几何。"""
    out = []
    for ax in fig.axes:
        item = dict(xlim=list(ax.get_xlim()), ylim=list(ax.get_ylim()),
                    xscale=ax.get_xscale(), yscale=ax.get_yscale(),
                    bounds=list(ax.get_position().bounds),
                    texts=[(t.get_text(), list(t.get_position())) for t in ax.texts],
                    lines=[(array_sha(l.get_xdata()), array_sha(l.get_ydata())) for l in ax.lines],
                    collections=[])
        for c in ax.collections:
            arr = c.get_array()
            item['collections'].append(dict(values=array_sha(arr) if arr is not None else None,
                                             paths=[array_sha(v.vertices) for v in c.get_paths()],
                                             clim=list(c.get_clim())))
        out.append(item)
    return out


def main_figures():
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in P.INPUTS}
    palette_path = material_file('parula256.json')
    reference_path = material_file('style_reference_sha256.json', 'reference/inputs_sha256.json')
    inputs[palette_path.relative_to(ROOT).as_posix()] = sha(palette_path)
    inputs[reference_path.relative_to(ROOT).as_posix()] = sha(reference_path)
    inputs.update(json.loads(reference_path.read_text(encoding='utf-8')))
    receipt = json.loads((ROOT / 'nr_audit/results/new4p_figures.json').read_text(encoding='utf-8'))
    with plt.rc_context(RC):
        for name, fn, ax_index, old, key in (
            ('Main6', P.phase_baseline, 0, 'joint_phase_baseline', 'joint_phase_baseline'),
            ('Main8', P.xian_joint, 1, 'xian_joint', 'xian_joint'),
        ):
            fig, checks = fn()
            assert checks == receipt['checks'][key]
            # 先完成自动布局，避免字体测量引起的非科学几何漂移。
            fig.canvas.draw()
            before = geometry(fig)
            target = fig.axes[ax_index]
            mesh = next(c for c in target.collections if isinstance(c, QuadMesh))
            categorical_colors = fig.axes[0].collections[0].get_facecolors().copy() if name == 'Main8' else None
            mesh.set_cmap(palette())
            # 作者指定F4参考画法：红色点划等高线、黑色沿线数字，不加白色描边。
            for c in target.collections:
                if c is not mesh and hasattr(c, 'levels'):
                    c.set_edgecolor(P.RED)
                    c.set_linestyle('-.')
                    c.set_linewidth(.6)
            for t in target.texts:
                if t.get_text() in {'0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'}:
                    t.set_color(P.BLACK)
                    t.set_path_effects([])
                elif t.get_text() == r'$r=2$':
                    t.set_color('white')
                    t.set_path_effects([pe.withStroke(linewidth=.6, foreground='#222222', alpha=.7)])
            # 色柱只保留连续色带及数值刻度；等高线只显示在相图内。
            colorbar_index = len(fig.axes) - 1 if name == 'Main8' else 1
            colorbar_axis = fig.axes[colorbar_index]
            auxiliary_count = len(colorbar_axis.lines)
            for line in list(colorbar_axis.lines):
                line.remove()
            fig.canvas.draw()
            after = geometry(fig)
            expected = [dict(item) for item in before]
            expected[colorbar_index]['lines'] = []
            assert expected == after, f'{name}: geometry changed outside colorbar auxiliary lines'
            if categorical_colors is not None:
                assert np.array_equal(categorical_colors, fig.axes[0].collections[0].get_facecolors())
            checks = dict(cached_checks=checks, geometry_unchanged=True,
                          category_colors_unchanged=name == 'Main8',
                          palette='MATLAB parula(256)', contour_style='F4: red dash-dot lines, black labels, no text halo',
                          colorbar_style=dict(auxiliary_lines_before=auxiliary_count,
                                              auxiliary_lines_after=len(colorbar_axis.lines),
                                              plot_geometry_unchanged=True, position_unchanged=True),
                          geometry_sha256=hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest())
            save(fig, name, checks, inputs, ROOT / f'paper/figures/new4p/{old}.pdf')


def main():
    import preview_style_curves
    import preview_style_heatmaps
    preview_style_curves.main()
    preview_style_heatmaps.main()
    main_figures()


if __name__ == '__main__':
    main()
