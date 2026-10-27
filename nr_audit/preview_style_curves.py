"""仅生成 S1/S2/S3/S5 风格预览；只读既有绘图对象，不运行模型或参数扫描。"""
import hashlib
import json
import pickle
import re
import subprocess

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter

from preview_style_common import ROOT, OUT, F2, STYLE, RC, MM, TEXT_WIDTH_IN, array_sha, git_blob, save

TAG = 'pipeline-final-20261006'
ARCHIVE = 'latex/revision_layout_v5'
COLORS = [F2.GREEN, F2.MAGENTA, F2.BLUE, F2.BLACK]
C0_COLORS = {4: F2.GRAY, 5: F2.GREEN, 8: F2.MAGENTA, 10: F2.BLUE, 12: F2.BLACK}
Y_LABELS = [r'$t_1$', r'$\Delta t$', r'$t_{\rm end}$', r'$q_{\max}$', r'$J$', r'$I_{t_{\rm cum}}$']


def source(name, suffix='matlab_geometry.json'):
    folder = 'data' if suffix == 'pickle' else 'qa'
    rel = f'{ARCHIVE}/{folder}/{name}.{suffix}'
    raw = git_blob(rel)
    return raw, {f'git:{TAG}:{rel}': hashlib.sha256(raw).hexdigest()}


def layout_source(inputs):
    rel = f'{ARCHIVE}/layout_matlab.m'
    raw = git_blob(rel)
    inputs[f'git:{TAG}:{rel}'] = hashlib.sha256(raw).hexdigest()
    return raw.decode('utf-8-sig')


def old_path(name):
    return ROOT / 'paper/figures/layout_v5' / f'{name}.pdf'


def old_ratio(path):
    info = subprocess.check_output(['pdfinfo', str(path)]).decode('utf-8', errors='replace')
    size = re.search(r'Page size:\s+([\d.]+)\s+x\s+([\d.]+)\s+pts', info)
    if not size:
        raise ValueError(f'无法读取旧图尺寸：{path}')
    w, h = map(float, size.groups())
    return h / w


def ordered_axes(geometry):
    pairs = zip(geometry['positions'], geometry['series'])
    return [s for _, s in sorted(pairs, key=lambda p: (-p[0][1], p[0][0]))]


def array_record(x, y):
    return dict(x_sha256=array_sha(x), y_sha256=array_sha(y), x_count=int(np.asarray(x).size), y_count=int(np.asarray(y).size))


def assert_original(line, item):
    before = array_record(item['x'], item['y'])
    after = array_record(line.get_xdata(), line.get_ydata())
    assert before == after
    return before


def frame(ax, panel):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(STYLE['lw_axes'])
    ax.tick_params(which='major', direction='in', top=True, right=True, labelsize=STYLE['tick'],
                   length=2.5, width=STYLE['lw_axes'], pad=2.0)
    ax.tick_params(which='minor', direction='in', top=True, right=True,
                   length=1.4, width=STYLE['lw_axes'])
    ax.grid(False)
    ax.set_title(f'({panel})', fontsize=STYLE['title'])


def legend(ax, **kwargs):
    leg = ax.legend(fontsize=STYLE['legend'], frameon=True, fancybox=False,
                    edgecolor='black', framealpha=1, **kwargs)
    leg.get_frame().set_linewidth(STYLE['lw_axes'])
    return leg


def verify_arrays(fig, original):
    """完成一次实际绘制后逐对象复查，渲染器不得改变输入数组。"""
    fig.canvas.draw()
    current = [array_record(line.get_xdata(), line.get_ydata()) for ax in fig.axes for line in ax.lines]
    expected = [{key: value for key, value in item.items() if key in ('x_sha256', 'y_sha256', 'x_count', 'y_count')}
                for item in original]
    assert current == expected, '实际绘制后曲线数组身份变化'


def metric_summaries(name, number, by_eta):
    raw, inputs = source(name)
    layout_source(inputs)
    geometry = json.loads(raw)
    series = ordered_axes(geometry)
    fig, axes = plt.subplots(2, 3, figsize=(TEXT_WIDTH_IN, TEXT_WIDTH_IN * old_ratio(old_path(name))))
    fig.subplots_adjust(left=.073, right=.985, bottom=.115, top=.945, wspace=.34, hspace=.51)
    original = []
    # 坐标范围按现图保留。J 面板上界为原图的最大已存 J，其他范围为原图刻度边界。
    jmax = max(max(np.atleast_1d(s['y'])) for s in series[4])
    limits = [(0, 10), (0, 250), (0, 250), (.45, .85), (0, jmax), (150, 350)] if by_eta else [
        (0, 50), (0, 250), (0, 350), (0, 1), (0, jmax), (50, 300)]
    values = [5, 8, 10, 12] if by_eta else [.2, .6, 1, 2]
    labels = [rf'$c_0={v:g}$' for v in values] if by_eta else [rf'$\eta/N={v:g}\%$' for v in values]
    for i, ax in enumerate(axes.flat):
        items = series[i]
        curves = list(reversed([s for s in items if s['marker'] == 'none']))
        assert len(curves) == 4
        for item, color, label in zip(curves, COLORS, labels):
            line, = ax.plot(item['x'], item['y'], color=color, lw=STYLE['lw_main'], label=label)
            original.append(dict(panel=chr(97 + i), kind='curve', **assert_original(line, item)))
        for item in items:
            if item['marker'] != 'none':
                line, = ax.plot(np.atleast_1d(item['x']), np.atleast_1d(item['y']), ls='none', marker=item['marker'],
                                color=F2.RED, mfc=F2.RED, mec='white', mew=.5, ms=3.4)
                original.append(dict(panel=chr(97 + i), kind='extremum', **assert_original(line, item)))
        ax.set_ylim(*limits[i])
        ax.set_ylabel(Y_LABELS[i])
        if by_eta:
            ax.set_xscale('log')
            ax.set_xlim(.2, 5)
            ax.xaxis.set_major_locator(FixedLocator([.2, .5, 1, 2, 5]))
            ax.xaxis.set_major_formatter(FixedFormatter(['0.2', '0.5', '1', '2', '5']))
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.set_xlabel(r'$\eta/N\;(\%)$')
            if i == 3:
                ax.set_yticks([.45, .55, .65, .75, .85])
        else:
            ax.set_xlim(2.3, 14)
            ax.set_xticks([4, 6, 8, 10, 12, 14])
            ax.set_xlabel(r'$c_0$')
        frame(ax, chr(97 + i))
    legend(axes.flat[2], loc='upper right', handlelength=1.45, labelspacing=.17, borderpad=.3)
    verify_arrays(fig, original)
    checks = dict(source_artists_preserved=True, arrays_verified_after_draw=True, arrays=original, no_resampling=True,
                  panel_count=6, curve_count=24, extremum_marker_count=sum(s['kind'] == 'extremum' for s in original),
                  range_provenance=dict(source=f'git:{TAG}:{ARCHIVE}/layout_matlab.m',
                                        limits_preserved=limits,
                                        J_upper=float(jmax), J_upper_equals_existing_maximum=True,
                                        J_native_PDF_check='原PDF转SVG后，S1最大J路径或S2最大J端点恰位于原J轴顶边y=185；不是1.05倍上界'))
    return save(fig, number, checks, inputs, old_path(name))


def quarantine_trajectories():
    name = 'baseline_q_joint'
    raw, inputs = source(name)
    layout = layout_source(inputs)
    assert 'xmax = max([rows.t2]+.08*[rows.Delta_t]);' in layout
    assert 'ymax = min(1,1.08*max([rows.q_max])+.02);' in layout
    geometry = json.loads(raw)
    series = ordered_axes(geometry)
    fig, axes = plt.subplots(1, 2, figsize=(TEXT_WIDTH_IN, TEXT_WIDTH_IN * old_ratio(old_path(name))))
    fig.subplots_adjust(left=.074, right=.987, bottom=.145, top=.93, wspace=.24)
    original = []
    range_checks = []
    for panel, (ax, items) in enumerate(zip(axes, series)):
        curves = list(reversed([s for s in items if s['style'] == '-' and s['marker'] == 'none']))
        values = [4, 5, 8, 10, 12] if panel == 0 else [.2, .6, 1, 2]
        colors = [C0_COLORS[v] for v in values] if panel == 0 else COLORS
        assert len(curves) == len(values)
        for item, value, color in zip(curves, values, colors):
            label = rf'$c_0={value:g}$' if panel == 0 else rf'$\eta/N={value:g}\%$'
            line, = ax.plot(item['x'], item['y'], color=color, lw=STYLE['lw_main'], label=label)
            original.append(dict(panel=chr(97 + panel), kind='curve', **assert_original(line, item)))
            # 使用原对象中的颜色联系同一条轨迹的启动/退出标记，标记的坐标直接复用。
            for marker in [s for s in items if s['marker'] in ('^', '|') and s['color'] == item['color']]:
                point, = ax.plot(np.atleast_1d(marker['x']), np.atleast_1d(marker['y']), ls='none', marker=marker['marker'],
                                 color=color, mfc='white', mec=color, mew=.7, ms=4 if marker['marker'] == '^' else 6)
                original.append(dict(panel=chr(97 + panel), kind=marker['marker'], **assert_original(point, marker)))
        for item in items:
            if item['marker'] == 'o':
                point, = ax.plot(np.atleast_1d(item['x']), np.atleast_1d(item['y']), ls='none', marker='o',
                                 mfc=F2.RED, mec='white', mew=.4, ms=3.6)
                original.append(dict(panel=chr(97 + panel), kind='inflection', **assert_original(point, item)))
            elif item['style'] in ('--', ':') and item['marker'] == 'none':
                line, = ax.plot(item['x'], item['y'], color=F2.RED, ls=item['style'], lw=STYLE['lw_ref'],
                                alpha=STYLE['ref_alpha'], label=r'$q_0$' if item['style'] == '--' else r'$q_{\rm inf}$')
                original.append(dict(panel=chr(97 + panel), kind='reference', **assert_original(line, item)))
        xmax = max(max(np.atleast_1d(s['x'])) for s in items)
        source_xmax = max(float(s['x'][-1]) + .08 * (float(s['x'][-1]) - float(s['x'][0])) for s in curves)
        assert abs(source_xmax - xmax) < 1e-11
        ymax = min(1, 1.08 * max(max(np.atleast_1d(s['y'])) for s in curves) + .02)
        range_checks.append(dict(panel=chr(97 + panel), xlim=[0, xmax], ylim=[0, ymax],
                                 original_xmax_formula_error=abs(source_xmax - xmax)))
        ax.set(xlim=(0, xmax), ylim=(0, ymax), xlabel=r'$t$', ylabel=r'$q_c(t)$')
        ax.set_xticks([0, 5, 10, 15, 20] if panel == 0 else [0, 50, 100, 150])
        frame(ax, chr(97 + panel))
        legend(ax, loc='upper right', handlelength=1.45, labelspacing=.22, borderpad=.35)
    verify_arrays(fig, original)
    checks = dict(source_artists_preserved=True, arrays_verified_after_draw=True, arrays=original, no_resampling=True, panel_count=2,
                  curve_count=9, original_object_count=sum(map(len, series)), drawn_object_count=sum(len(a.lines) for a in axes),
                  range_provenance=dict(source=f'git:{TAG}:{ARCHIVE}/layout_matlab.m',
                                        xmax_formula='max(t2+0.08*Delta_t)', ymax_formula='min(1,1.08*max(q_max)+0.02)',
                                        uses_same_original_range_formulas=True, panels=range_checks))
    assert checks['original_object_count'] == checks['drawn_object_count']
    return save(fig, 'S3', checks, inputs, old_path(name))


def fingerprint(figure):
    result = []
    for ax in figure.axes:
        lines = [array_record(l.get_xdata(orig=True), l.get_ydata(orig=True)) for l in ax.lines]
        patches = []
        for patch in ax.patches:
            item = dict(vertices_sha256=array_sha(patch.get_path().vertices), facecolor=list(patch.get_facecolor()))
            if hasattr(patch, 'get_bbox'):
                item['data_bbox'] = list(patch.get_bbox().bounds)
            patches.append(item)
        result.append(dict(lines=lines, patches=patches, xlim=list(ax.get_xlim()), ylim=list(ax.get_ylim()),
                           xscale=ax.get_xscale(), yscale=ax.get_yscale()))
    return result


def lambda_sensitivity():
    name = 'scenario1_inflection_lambda_sensitivity'
    raw, inputs = source(name, 'pickle')
    # 此pickle为固定Git标签内已核对的本项目Matplotlib缓存；不导入原计算脚本。
    fig = pickle.loads(raw)
    before = fingerprint(fig)
    width = .8 * TEXT_WIDTH_IN
    fig.set_layout_engine(None)
    fig.set_size_inches(width, width * old_ratio(old_path(name)))
    fig.subplots_adjust(left=.10, right=.98, bottom=.11, top=.94, wspace=.24, hspace=.38)
    for i, ax in enumerate(fig.axes):
        if ax.get_legend() is not None:
            ax.get_legend().remove()
        for text in list(ax.texts):
            if re.fullmatch(r'\(?[a-f]\)?', text.get_text()):
                text.remove()
        current = F2.BLUE
        for line in ax.lines:
            if np.asarray(line.get_xdata()).size > 1:
                label = line.get_label()
                current = F2.GREEN if 'beta=0.1$' in label else F2.MAGENTA if 'beta=0.12$' in label else F2.BLUE
                line.set_color(current)
                line.set_linewidth(STYLE['lw_main'])
            else:
                line.set_color(current)
                line.set_markeredgecolor(current)
                line.set_markerfacecolor('white')
                line.set_markeredgewidth(.8)
                line.set_markersize(3.5)
        ax.xaxis.label.set_fontsize(STYLE['label'])
        ax.yaxis.label.set_fontsize(STYLE['label'])
        frame(ax, chr(97 + i))
        # 缓存中域外的预生成刻度不会出现在原图；删去这些不可见刻度，避免预览收据误报越界文字。
        lo, hi = ax.get_xlim()
        ax.set_xticks([v for v in ax.get_xticks() if lo <= v <= hi])
        ax.set_xlim(lo, hi)
    legend(fig.axes[0], handles=[
        Patch(facecolor='#f0f0f0', edgecolor='none', label='Not triggered'),
        Patch(facecolor='#c7c7c7', edgecolor='none', label='No internal inflection')],
        loc='upper right', handlelength=1.25, labelspacing=.25, borderpad=.32)
    legend(fig.axes[3], handles=[Line2D([], [], color=color, lw=STYLE['lw_main'], label=rf'$\beta={value:g}$')
                               for value, color in zip([.10, .12, .155], [F2.GREEN, F2.MAGENTA, F2.BLUE])],
           loc='upper left', handlelength=1.55, labelspacing=.22, borderpad=.32)
    for text in fig.findobj(matplotlib.text.Text):
        text.set_fontfamily('serif')
        text.set_math_fontfamily('cm')
        if text in [a.xaxis.label for a in fig.axes] + [a.yaxis.label for a in fig.axes]:
            text.set_fontsize(STYLE['label'])
    fig.canvas.draw()
    after = fingerprint(fig)
    assert before == after, 'S5 曲线或灰区几何发生变化'
    checks = dict(source_artists_preserved=True, arrays_verified_after_draw=True, no_resampling=True, no_parameter_scan=True, arrays_and_regions=before,
                  panel_count=len(fig.axes), curve_count=6, extremum_marker_count=3,
                  grey_region_count=sum(len(a.patches) for a in fig.axes))
    return save(fig, 'S5', checks, inputs, old_path(name))


def main():
    with plt.rc_context(RC):
        metric_summaries('c0_sensitivity_selected_eta', 'S1', False)
        metric_summaries('eta_sensitivity_selected_c0', 'S2', True)
        quarantine_trajectories()
        lambda_sensitivity()


if __name__ == '__main__':
    main()
