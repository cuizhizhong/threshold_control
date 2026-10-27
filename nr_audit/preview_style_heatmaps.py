"""补充图 S4、S6、S8 的独立风格预览，不覆盖正式图件。

S4、S8 的指标矩阵与 S6 的局部加密分类全部只读复用。
唯一辅助求解是作者明确允许的 S4 原 241 个阈值点上的触发边界，
逐项照录 critical_c0_for_eta.m 的公式、参数与括区规则，不求解模型轨迹。
所有背景使用公共模块提供的精确 MATLAB parula(256)。
"""
import argparse
import hashlib
import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm
from matplotlib.image import NonUniformImage
from matplotlib.path import Path as PlotPath
from matplotlib.lines import Line2D

from preview_style_common import ROOT, OUT, F2, STYLE, RC, MM, TEXT_WIDTH_IN, palette, sha, save, material_file


BASELINE = ROOT / 'reproducibility/results/20261003_release_final/baseline'
XIAN = ROOT / 'reproducibility/results/20261003_release_final/xian'
RESULTS = ROOT / 'nr_audit/results'
BLACK, RED, PURPLE = F2.BLACK, F2.RED, (0.494, 0.184, 0.556)


def summarize(values):
    """保存实际送入绘图函数的数组身份，不把重绘称为新数值结果。"""
    array = np.ascontiguousarray(np.asarray(values, dtype='<f8'))
    finite = array[np.isfinite(array)]
    return dict(shape=list(array.shape), sha256=hashlib.sha256(array.tobytes()).hexdigest(),
                finite_count=int(finite.size), nan_count=int(np.isnan(array).sum()),
                min=float(finite.min()) if finite.size else None,
                max=float(finite.max()) if finite.size else None)


def input_hashes(paths):
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}


def contour_reference_inputs():
    """保存作者指定的EPS画法来源；入库后无需访问外部参考文件。"""
    manifest = material_file('style_reference_sha256.json', 'reference/inputs_sha256.json')
    references = json.loads(manifest.read_text(encoding='utf-8'))
    return {**input_hashes([manifest]), **references}


def mesh_matches(mesh, source):
    actual = np.asarray(np.ma.filled(mesh.get_array(), np.nan)).reshape(source.shape)
    assert np.array_equal(actual, source, equal_nan=True)
    return dict(source=summarize(source), plotted=summarize(actual), exact_match=True)


def math_colorbar(fig, artist, axis, label):
    cb = fig.colorbar(artist, cax=axis)
    # 数学量放在色条顶部，避免窄面板之间的纵向标签相互挤压。
    cb.ax.set_title(label, fontsize=STYLE['label'], pad=4)
    cb.ax.tick_params(labelsize=STYLE['tick'], direction='in', length=2.5,
                      width=STYLE['lw_axes'])
    cb.outline.set_linewidth(STYLE['lw_axes'])
    return cb


def four_panel_grid(height_mm, grouped=False):
    fig = plt.figure(figsize=(.8 * TEXT_WIDTH_IN, height_mm * MM))
    axes, cbaxes = [], []
    if grouped:
        groups = fig.add_gridspec(2, 2, left=.085, right=.94, bottom=.105, top=.94,
                                 wspace=.38, hspace=.32)
        for row in range(2):
            for col in range(2):
                pair = groups[row, col].subgridspec(1, 2, width_ratios=[1, .045], wspace=.08)
                axes.append(fig.add_subplot(pair[0]))
                cbaxes.append(fig.add_subplot(pair[1]))
        return fig, axes, cbaxes
    grid = fig.add_gridspec(2, 4, width_ratios=[1, .045, 1, .045],
                           left=.085, right=.94, bottom=.105, top=.94,
                           wspace=.48, hspace=.32)
    for row in range(2):
        for col in range(2):
            axes.append(fig.add_subplot(grid[row, 2 * col]))
            cbaxes.append(fig.add_subplot(grid[row, 2 * col + 1]))
    return fig, axes, cbaxes


def baseline_boundary(etas, params):
    """完全照录 MATLAB 原边界公式及增长边界/倍增括区；只求原阈值点。"""
    beta, gamma, q0, pop, s0, i0 = (params[k] for k in ('beta', 'gamma', 'q0', 'N', 'S0', 'I0'))
    h = beta + q0 * (1 - beta)
    a = beta * (1 - q0) / h
    lower = gamma * pop / (beta * (1 - q0) * s0)
    cache_file = material_file('S4_boundary_display.json')
    identity = dict(
        csv_sha256=sha(BASELINE / 'landscape_summary.csv'),
        formula_sha256=sha(ROOT / 'scenario1_threshold_landscape/common/critical_c0_for_eta.m'),
        parameters_sha256=hashlib.sha256(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest(),
        etas=summarize(etas))
    if cache_file.exists():
        cache = json.loads(cache_file.read_text(encoding='utf-8'))
        assert cache['identity'] == identity, 'S4边界缓存的CSV、公式、参数或阈值点已改变，禁止静默重求'
        roots = np.asarray(cache['roots'], dtype=float)
        assert roots.shape == np.asarray(etas).shape and np.all(np.isfinite(roots))
        sc = gamma * pop / (beta * roots * (1 - q0))
        residual = np.abs(i0 + a * (s0 - sc) + a * sc * np.log(sc / s0) - etas)
        assert float(residual.max()) < 5e-10
        receipt = dict(cache['solver_receipt'])
        receipt.update(cache_reused=True, new_root_calls_this_run=0,
                       reused_root_residual_max=float(residual.max()),
                       cache_path=cache_file.relative_to(ROOT).as_posix(), cache_sha256=sha(cache_file))
        return roots, receipt
    raise FileNotFoundError('S4边界缓存缺失；请恢复入库材料，不自动重新求根。')


def baseline_limits(z, metric):
    if metric == 'Delta_t':
        return (0., 215.)
    vals = z[np.isfinite(z)]
    lo, hi = float(vals.min()), float(vals.max())
    raw = (hi - lo) / 8
    exponent = np.floor(np.log10(raw))
    fraction = raw / 10**exponent
    nice_fraction = next(v for v in (1, 2, 5, 10) if fraction <= v)
    step = nice_fraction * 10**exponent
    return float(np.floor(lo / step) * step), float(np.ceil(hi / step) * step)


def leading_fill(z):
    """与原图一致：仅填列首的 NaN，随后用原解析边界的白色遮罩覆盖。"""
    displayed = z.copy()
    for column in range(z.shape[1]):
        good = np.flatnonzero(np.isfinite(z[:, column]))
        if good.size and good[0] > 0:
            displayed[:good[0], column] = z[good[0], column]
    assert np.array_equal(displayed[np.isfinite(z)], z[np.isfinite(z)])
    return displayed


def label_longest_contours(ax, contours, x_span, y_span, fmt='%g'):
    positions = []
    xmin, xmax = sorted(ax.get_xlim())
    ymin, ymax = sorted(ax.get_ylim())
    for segments in contours.allsegs:
        segments = [s for s in segments if len(s) >= 2]
        if not segments:
            continue
        longest = max(segments, key=lambda s: np.hypot(np.diff(s[:, 0]) / x_span,
                                                      np.diff(s[:, 1]) / y_span).sum())
        inside = longest[(longest[:, 0] > xmin + .045 * x_span)
                         & (longest[:, 0] < xmax - .045 * x_span)
                         & (longest[:, 1] > ymin + .05 * y_span)
                         & (longest[:, 1] < ymax - .05 * y_span)]
        candidates = inside if len(inside) else longest
        positions.append(tuple(candidates[len(candidates) // 2]))
    if positions:
        labels = ax.clabel(contours, inline=True, manual=positions, fmt=fmt,
                           fontsize=STYLE['note'], inline_spacing=2, colors='black')
        for label in labels:
            xx, yy = label.get_position()
            if xx < xmin + .045 * x_span:
                # 极靠左的180等值线没有足够宽度容纳竖排数字；向内留白并水平左对齐。
                label.set_position((max(xx, xmin + .02 * x_span), yy))
                label.set_rotation(0)
                label.set_ha('left')


def preview_s4():
    source = BASELINE / 'landscape_summary.csv'
    boundary_source = ROOT / 'scenario1_threshold_landscape/common/critical_c0_for_eta.m'
    plot_source = ROOT / 'scenario1_threshold_landscape/scripts/plot_heatmaps.m'
    inputs = input_hashes([source, boundary_source, plot_source])
    inputs.update(contour_reference_inputs())
    frame = pd.read_csv(source, float_precision='round_trip')
    x, y = np.sort(frame.eta_percent.unique()), np.sort(frame.c0.unique())
    assert len(x) == 241 and len(y) == 118
    params = {k: float(frame[k].iloc[0]) for k in ('beta', 'gamma', 'q0', 'N', 'S0', 'I0')}
    eta_by_x = frame.groupby('eta_percent').eta.first().reindex(x).to_numpy()
    boundary, solves = baseline_boundary(eta_by_x, params)
    fields = [('t1', r'$t_1$', [1, 2, 5, 10, 20]),
              ('Delta_t', r'$\Delta t$', [5, 10, 20, 40, 80]),
              ('t_end', r'$t_{\rm end}$', [30, 50, 80, 120, 180]),
              ('I_t_cum', r'$I_{t_{\rm cum}}$', [180, 220, 260, 300, 340])]
    checks = dict(x=summarize(x), y=summarize(y), boundary=summarize(boundary),
                  auxiliary_boundary_roots=solves, metrics={}, new_ode_solves=0,
                  new_optimization_solves=0, axes_limits=[.2, 5., 2.3, 14.],
                  contour_style=dict(line_color='red', linestyle='-.', label_color='black',
                                     inline_gap=True, label_path_effects=[]))
    with plt.rc_context(RC):
        fig, axes, cbaxes = four_panel_grid(100, grouped=True)
        for k, (ax, cax, (metric, symbol, levels)) in enumerate(zip(axes, cbaxes, fields)):
            z = frame.pivot(index='c0', columns='eta_percent', values=metric).reindex(index=y, columns=x).to_numpy()
            displayed = leading_fill(z)
            limits = baseline_limits(z, metric)
            plotted = displayed.copy()
            fill_levels = np.linspace(limits[0], limits[1], 201)
            artist = ax.contourf(x, y, plotted, levels=fill_levels, cmap=palette(),
                                 norm=Normalize(*limits), antialiased=False)
            # 仅栅格化填色背景，避免PDF阅读器在相邻矢量色块间显示白色细缝。
            # 等值线、解析边界、文字与坐标轴仍按矢量输出。
            # Matplotlib 3.9 的 QuadContourSet 不接受 set_rasterized；
            # 用坐标轴的栅格化层级只处理 zorder=0 的这一层。
            artist.set_zorder(0)
            ax.set_rasterization_zorder(1)
            assert np.array_equal(plotted, displayed, equal_nan=True)
            ax.fill_between(x, np.full(x.shape, y.min()), boundary, color='white',
                            edgecolor='none', zorder=2)
            contours = ax.contour(x, y, z, levels=levels, colors=[RED],
                                  linestyles='-.', linewidths=STYLE['lw_vline'], zorder=3)
            label_longest_contours(ax, contours, 4.8, 11.7)
            line, = ax.plot(x, boundary, color=BLACK, lw=STYLE['lw_ref'], zorder=4)
            assert np.array_equal(line.get_xdata(), x) and np.array_equal(line.get_ydata(), boundary)
            ax.set(xlim=(.2, 5), ylim=(2.3, 14), xlabel=r'$\eta/N\;(\%)$', ylabel=r'$c_0$')
            ax.set_xticks([.2, 1, 2, 3, 4, 5], ['0.2', '1', '2', '3', '4', '5'])
            ax.set_yticks([2.3, 4, 6, 8, 10, 12, 14], ['2.3', '4', '6', '8', '10', '12', '14'])
            ax.set_box_aspect(1)
            ax.set_title(f'({chr(97 + k)})')
            cb = math_colorbar(fig, artist, cax, symbol)
            cb.set_ticks(dict(t1=[0, 10, 20, 30, 40, 50, 60],
                              Delta_t=[0, 50, 100, 150, 200],
                              t_end=[0, 50, 100, 150, 200, 250, 300],
                              I_t_cum=[50, 100, 150, 200, 250, 300, 350, 400])[metric])
            checks['metrics'][metric] = dict(source=summarize(z), displayed=summarize(displayed),
                plotted=summarize(plotted), plotted_equals_displayed=True,
                existing_finite_values_preserved=True, normalization='linear',
                color_limits=list(limits), contour_levels=levels,
                background_rasterized=True, background_dpi=600,
                text_contours_and_boundary_vector=True)
        save(fig, 'S4', checks, inputs, ROOT / 'paper/figures/scenario1_heatmaps_c0_eta.pdf')
        plt.close(fig)


def preview_s6():
    import plot_figure7 as f7

    cs_path = RESULTS / 'new4d_cost_structure.json'
    inputs = input_hashes([f7.DATA, f7.NPZ, cs_path])
    data = json.loads(f7.DATA.read_text(encoding='utf-8'))
    f7.validate_cached_inputs(data)
    arrays = dict(np.load(f7.NPZ, allow_pickle=False))
    closed_form = json.loads(cs_path.read_text(encoding='utf-8'))
    colors = dict(continuous=BLACK, endpoint=RED, internal=PURPLE)
    checks = dict(cache_validation_passed=True, new_classifications=0, new_background_solves=0,
                  new_ode_solves=0, panels={})
    with plt.rc_context(RC):
        fig = plt.figure(figsize=(TEXT_WIDTH_IN, 64 * MM))
        gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, .045], left=.075, right=.94,
                             bottom=.135, top=.91, wspace=.28)
        axes = [fig.add_subplot(gs[0]), fig.add_subplot(gs[1])]
        cax = fig.add_subplot(gs[2])
        for k, (case, ax) in enumerate(zip(('base', 'xian'), axes)):
            z, r = arrays[case + '_z'], arrays[case + '_r']
            background_r, background_y = arrays[case + '_background_r'], arrays[case + '_background_y']
            # 直接使用原非均匀r及原节点数据；仅在显示像素间作矩形双线性插值，
            # 不增加状态网格、不重新分类，也不使用会形成三角扇齿的Gouraud网格。
            mesh = NonUniformImage(ax, interpolation='bilinear', cmap=palette(),
                                   norm=Normalize(0, 1), origin='lower', zorder=0)
            mesh.set_data(z, background_r, background_y)
            ax.add_image(mesh)
            mesh.set_clip_box(ax.bbox)
            panel = dict(z=summarize(z), r=summarize(r), background_r=summarize(background_r),
                         background=mesh_matches(mesh, background_y), boundaries={},
                         display_interpolation='NonUniformImage bilinear：原非均匀坐标/原节点RGB的矩形显示插值，不新增数值网格或分类',
                         background_rasterized=True, white_line_outline=False)
            zero_boundary = []
            boundary_vertices = {}
            for kind, color in colors.items():
                xs = []
                for row in data['cases'][case]['samples']:
                    values = [b['z'] for b in row['breakpoints'] if f7.edge_kind(b) == kind]
                    xs.append(values[0] if values else np.nan)
                xs = np.asarray(xs)
                line, = ax.plot(xs, r, color=color, lw=STYLE['lw_ref'])
                ax.scatter(xs, r, color=color, s=.65, zorder=4, linewidths=0)
                assert np.array_equal(line.get_xdata(), xs, equal_nan=True)
                assert np.array_equal(line.get_ydata(), r)
                panel['boundaries'][kind] = dict(x=summarize(xs), y=summarize(r), plotted_exactly=True)
                boundary_vertices[kind] = np.column_stack((xs, r))
                if kind in ('continuous', 'endpoint'):
                    zero_boundary.extend([float(xx), float(rr)] for xx, rr in zip(xs, r) if np.isfinite(xx))
            point = closed_form['cases'][case]
            known_endpoint = [point['z_sw'], point['r_hat']]
            connectors = {}
            for kind, which in (('endpoint', 'min'), ('continuous', 'max')):
                vertices = boundary_vertices[kind]
                vertices = vertices[np.isfinite(vertices[:, 0])]
                index = int(np.argmin(vertices[:, 1]) if which == 'min' else np.argmax(vertices[:, 1]))
                start = vertices[index].tolist()
                if not np.allclose(start, known_endpoint, rtol=0, atol=1e-14):
                    ax.plot([start[0], known_endpoint[0]], [start[1], known_endpoint[1]],
                            color=colors[kind], lw=STYLE['lw_ref'], zorder=2)
                    connectors[kind] = dict(from_=start, to=known_endpoint,
                                             scope='仅连接既存边界采样端点与已存闭式菱形点，原节点数组不变')
            panel['known_endpoint_connectors'] = connectors
            # 纯零区按已存黑/红节点及已知闭式衔接点精确覆盖；
            # 该矢量轮廓不来自新的分支判别或求解。
            zero_boundary.append([point['z_sw'], point['r_hat']])
            zero_boundary = np.asarray(sorted(zero_boundary, key=lambda row: row[1]))
            assert abs(zero_boundary[0, 1] - r[0]) < 1e-12
            assert abs(zero_boundary[-1, 1] - r[-1]) < 1e-12
            zero_polygon = np.vstack(([z[-1], r[0]], zero_boundary, [z[-1], r[-1]]))
            ax.fill(zero_polygon[:, 0], zero_polygon[:, 1], facecolor=palette()(0),
                    edgecolor='none', antialiased=False, zorder=1)
            zero_at_rows = np.interp(background_r, zero_boundary[:, 1], zero_boundary[:, 0])
            zero_nodes = z[None, :] >= zero_at_rows[:, None]
            covered_nonzero = background_y[zero_nodes & (background_y > 1e-12)]
            assert covered_nonzero.size == 0
            panel['zero_region_mask'] = dict(
                boundary_nodes=summarize(zero_boundary), polygon=summarize(zero_polygon),
                source='已存continuous/endpoint节点及(z_sw,r_hat)闭式端点',
                facecolor=list(palette()(0)), vector=True, new_classifications=0,
                covered_original_nodes=int(zero_nodes.sum()), covered_nonzero_nodes=0,
                covered_max_nonzero_y=0., zero_tolerance=1e-12)
            panel['branch_display_partitions'] = s6_branch_display_layers(
                ax, z, background_r, background_y, data['cases'][case]['samples'], point,
                zero_boundary, f7)
            # 参考线在结构边界下方，避免同位时浅色虚线覆盖黑色分界的中心。
            ax.axvline(point['z_sw'], color=F2.GRAY, ls='--', lw=STYLE['lw_vline'], zorder=1.5)
            ax.plot(point['cusp_state'], point['r_cont'], 'o', ms=4, mfc='none', mec=BLACK,
                    mew=.7, zorder=6)
            ax.plot(point['z_sw'], point['r_hat'], 'D', ms=3.8, mfc='none', mec=BLACK,
                    mew=.7, zorder=6)
            ax.set(xlim=(z[-1], z[0]), ylim=(r[0], r[-1]), xlabel=r'$S/S_c$ (time $\rightarrow$)')
            if case == 'base':
                ax.set_xticks([2.270, 2.265, 2.260, 2.255], ['2.270', '2.265', '2.260', '2.255'])
            else:
                ax.set_xticks([2.56, 2.55, 2.54, 2.53, 2.52, 2.51])
            if k == 0:
                ax.set_ylabel(r'$r=w_q/w_c$')
            ax.set_title(f'({chr(97 + k)})')
            panel.update(xlim=list(ax.get_xlim()), ylim=list(ax.get_ylim()), normalization='linear',
                         color_limits=[0, 1], cusp=[point['cusp_state'], point['r_cont']],
                         switch=[point['z_sw'], point['r_hat']])
            checks['panels'][case] = panel
        math_colorbar(fig, mesh, cax, r'$y$')
        handles = [Line2D([], [], c=colors['continuous'], lw=STYLE['lw_ref'], label='Continuous entry'),
                   Line2D([], [], c=colors['endpoint'], lw=STYLE['lw_ref'], label='Endpoint-to-interior jump'),
                   Line2D([], [], c=colors['internal'], lw=STYLE['lw_ref'], label='Interior-to-interior jump'),
                   Line2D([], [], ls='none', marker='o', ms=3.2, mfc='none', mec=BLACK,
                          label=r'$r_{\rm cont}$'),
                   Line2D([], [], ls='none', marker='D', ms=3.2, mfc='none', mec=BLACK,
                          label=r'$\hat r$ at $S_{\rm sw}$')]
        legend = axes[1].legend(handles=handles, loc='upper right', ncol=1,
                                fontsize=STYLE['legend'], handlelength=1.8,
                                borderaxespad=.5, labelspacing=.35)
        F2.frame_legend(legend)
        checks['legend'] = dict(panel='b', position='upper right', entries=5,
                                fallback='若遮挡边界则删除图内图例，由现有图注说明')
        save(fig, 'S6', checks, inputs, ROOT / 'paper/figures/joint_v2/joint_phase_detail.pdf')
        plt.close(fig)


def s6_branch_display_layers(ax, z, r, values, samples, point, zero_boundary, f7):
    """以缓存跳变折线切分显示，避免不同分支的RGB跨跳变混色。

    各层使用相同的原非均匀网格，只在其clip范围之外延拓同分支的边缘值。
    clip内的每一个原节点值保持原样；这些是显示分区，不是新的科学分类。
    """
    internal = []
    for row in samples:
        for edge in row['breakpoints']:
            if f7.edge_kind(edge) == 'internal':
                zz = edge['z']
                internal.append([row['r'], zz,
                                 (1 - edge['x_left']) / (1 - 1 / zz),
                                 (1 - edge['x_right']) / (1 - 1 / zz)])
    internal = np.asarray(sorted(internal, key=lambda row: row[0]))
    assert len(internal) > 1 and np.all(internal[:, 2] >= internal[:, 3])
    rc, rh = point['r_cont'], point['r_hat']
    jump = np.vstack(([point['cusp_state'], rc], internal[:, [1, 0]], [point['z_sw'], rh]))
    jump = jump[np.argsort(jump[:, 1])]
    after_hat = zero_boundary[zero_boundary[:, 1] > rh]
    strong_polygon = np.vstack(([z[0], rc], jump, after_hat, [z[0], r[-1]]))
    weak_outer = zero_boundary[(zero_boundary[:, 1] > rc) & (zero_boundary[:, 1] < rh)]
    weak_polygon = np.vstack((jump, weak_outer[::-1], [point['z_sw'], rc]))
    strong, weak = values.copy(), values.copy()
    strong_keep = np.ones(values.shape, dtype=bool)
    weak_keep = np.ones(values.shape, dtype=bool)
    thin_rows = []
    for j, rr in enumerate(r):
        if rr < rc:
            # 连续场与分支场的共边从同一缓存插值，避免水平色缝。
            continue
        outer = float(np.interp(rr, zero_boundary[:, 1], zero_boundary[:, 0]))
        jump_at = float(np.interp(rr, jump[:, 1], jump[:, 0])) if rr <= rh else outer
        keep = z <= jump_at
        assert np.any(keep)
        strong_keep[j] = keep
        strong[j, ~keep] = values[j, np.flatnonzero(keep)[-1]]
        if rr <= rh:
            keep_weak = (z >= jump_at) & (z < outer)
            weak_keep[j] = keep_weak
            good = np.flatnonzero(keep_weak)
            if len(good):
                weak[j, :good[0]] = values[j, good[0]]
                weak[j, good[-1] + 1:] = values[j, good[-1]]
            else:
                # 极窄显示区没有原网格节点时，仅用缓存右侧分支值及零区闭式端点。
                side_r = np.r_[internal[:, 0], rh]
                side_y = np.r_[internal[:, 3], 0.]
                weak[j, :] = np.interp(rr, side_r, side_y)
                thin_rows.append(float(rr))
        else:
            weak_keep[j] = False
            weak[j, :] = 0.
    assert np.array_equal(strong[strong_keep], values[strong_keep])
    assert np.array_equal(weak[weak_keep], values[weak_keep])
    reports = {}
    for name, displayed, keep, polygon, order in (
            ('strong', strong, strong_keep, strong_polygon, .2),
            ('weak', weak, weak_keep, weak_polygon, .3)):
        image = NonUniformImage(ax, interpolation='bilinear', cmap=palette(),
                                norm=Normalize(0, 1), origin='lower', zorder=order)
        image.set_data(z, r, displayed)
        ax.add_image(image)
        image.set_clip_path(PlotPath(polygon), ax.transData)
        image.set_clip_box(ax.bbox)
        reports[name] = dict(display_array=summarize(displayed), clip_polygon=summarize(polygon),
                             retained_original_node_count=int(keep.sum()),
                             retained_original_values_exact=True,
                             extrapolation='仅clip外采用同分支最近节点，显示区无节点时用缓存x_right侧颜色约束')
    return dict(method='原节点RGB矩形双线性插值，按缓存跳变折线作显示分区clip；不是新增科学分类',
                new_classifications=0, new_grid_nodes=0, new_solves=0,
                jump_nodes=summarize(jump), cached_side_values=summarize(internal),
                continuous_field_below_r_cont='原场保留，共边使用同一原缓存RGB',
                thin_weak_rows_using_cached_side_colors=thin_rows, layers=reports)


def xian_contour_levels(values, metric):
    """照录原热图档位规则；仅对已存矩阵求显示等值线。"""
    finite = values[np.isfinite(values)]
    lo, hi = float(finite.min()), float(finite.max())
    if metric in {'control_duration', 'clear_time', 'J'}:
        positive = finite[finite > 0]
        lo, hi = float(positive.min()), float(positive.max())
        base = 10.**np.floor(np.log10(lo))
        for ratio in (2., 4., 8.):
            seq, value = [], base
            while value < hi:
                seq.append(value)
                value *= ratio
            if len([v for v in seq if v > lo]) <= 8:
                break
        raw = np.asarray([v for v in seq if v > lo])
    else:
        raw = np.linspace(lo, hi, 6)
    levels = np.unique(np.round(raw, decimals=8))
    return levels[(levels > lo) & (levels < hi)]


def path_length_px(path, transform):
    vertices = transform.transform(path.vertices)
    keep = path.codes[1:] != 1 if path.codes is not None else np.ones(len(vertices) - 1, dtype=bool)
    return float(np.linalg.norm(np.diff(vertices, axis=0), axis=1)[keep].sum())


def path_receipts(paths, levels):
    return [dict(level=float(level), vertices=summarize(path.vertices),
                 codes_sha256=hashlib.sha256(np.asarray(path.codes, dtype='u1').tobytes()).hexdigest())
            for level, path in zip(levels, paths)]


def label_xian_contours(ax, contours, x, y, fmt):
    """先在最终对数坐标内选点再切线；不事后隐藏已经切断等高线的标签。"""
    originals = [path.deepcopy() for path in contours.get_paths()]
    positions, labeled_levels = [], []
    lx0, lx1 = np.log10(x.min()), np.log10(x.max())
    y0, y1 = float(y.min()), float(y.max())
    for level, segments in zip(contours.levels, contours.allsegs):
        good_segments = [seg for seg in segments if len(seg) > 2]
        if not good_segments:
            continue
        segment = max(good_segments, key=lambda seg: np.linalg.norm(
            np.diff(ax.transData.transform(seg), axis=0), axis=1).sum())
        u = (np.log10(segment[:, 0]) - lx0) / (lx1 - lx0)
        v = (segment[:, 1] - y0) / (y1 - y0)
        inside = (u > .075) & (u < .925) & (v > .13) & (v < .87)
        # 与两条固定参照线留开小间距，避免数字落在黑色竖线上。
        for reference in (151.90, 26326.):
            inside &= np.abs(np.log10(segment[:, 0] / reference)) > .055
        candidates = segment[inside]
        if len(candidates):
            positions.append(tuple(candidates[len(candidates) // 2]))
            labeled_levels.append(float(level))
    labels = []
    if positions:
        # Matplotlib 3.9 的manual+levels子集索引不一致；沿全部原level定位，
        # 手动点均在选中level的原顶点上，并逐条核对实际标注的level。
        labels = list(ax.clabel(contours, inline=True, inline_spacing=2,
                                manual=positions, fontsize=STYLE['note'], fmt=fmt, colors='black'))
        assert [label.get_text() for label in labels] == [fmt % level for level in labeled_levels]
    ax.figure.canvas.draw()
    renderer = ax.figure.canvas.get_renderer()
    final_paths = contours.get_paths()
    gap_metrics = []
    for level, original, final in zip(contours.levels, originals, final_paths):
        before = path_length_px(original, ax.transData)
        after = path_length_px(final, ax.transData)
        removed = max(0., before - after)
        selected = [label for label in labels if label.get_text() == fmt % level]
        permitted = sum(float(np.hypot(*label.get_window_extent(renderer).size)) + 4 for label in selected)
        # 弧线插值与字体包围盒允许2px舍入余量；无标签的等高线不应被截断。
        assert removed <= permitted + 2., (float(level), removed, permitted)
        gap_metrics.append(dict(level=float(level), before_length_px=before, after_length_px=after,
                                removed_length_px=removed, label_count=len(selected),
                                label_gap_upper_bound_px=permitted + 2., pass_=True))
    return dict(raw_paths=path_receipts(originals, contours.levels),
                final_paths=path_receipts(final_paths, contours.levels),
                label_positions=[list(p) for p in positions], labeled_levels=labeled_levels,
                hidden_after_inline_cut=0, gap_metrics=gap_metrics,
                coordinate_order='log坐标、范围、刻度固定后生成等高线，再内域选点inline标注')


def preview_s8():
    source, reference = XIAN / 'heatmap.csv', XIAN / 'reference.json'
    old_source = ROOT / 'xian_control_comparison/threshold_landscape_analysis/threshold_landscape_analysis.py'
    inputs = input_hashes([source, reference, old_source])
    inputs.update(contour_reference_inputs())
    frame = pd.read_csv(source, float_precision='round_trip')
    x, y = np.sort(frame.eta.unique()), np.sort(frame.c0.unique())
    fields = [('control_duration', r'$\Delta t$'), ('clear_time', r'$t_{\rm end}$'),
              ('cum_total_infections', r'$I_{t_{\rm cum}}$'), ('J', r'$J$')]
    checks = dict(x=summarize(x), y=summarize(y), metrics={}, new_ode_solves=0,
                  new_optimization_solves=0, reference_positions=[151.90, 26326.],
                  contour_style=dict(line_color='red', linestyle='-.', label_color='black',
                                     inline_gap=True, label_path_effects=[]),
                  removed_annotation='删除Δt约1.48×10^4 d≈40 yr的整段数值说明及箭头，仅预览',
                  existing_reference_discrepancy=dict(
                      original_plot_source=151.90, current_manuscript_caption=152.55,
                      disposition='本轮仅改风格，保留正式旧图与原绘图源码的151.90；未调整数字'))
    with plt.rc_context(RC):
        fig, axes, cbaxes = four_panel_grid(104)
        for k, (ax, cax, (metric, symbol)) in enumerate(zip(axes, cbaxes, fields)):
            z = frame.pivot(index='c0', columns='eta', values=metric).reindex(index=y, columns=x).to_numpy()
            finite = z[np.isfinite(z)]
            lo, hi = float(finite.min()), float(finite.max())
            norm = Normalize(lo, hi) if metric == 'cum_total_infections' else LogNorm(lo, hi)
            ax.set_xscale('log')
            mesh = ax.pcolormesh(x, y, np.ma.masked_invalid(z), shading='auto', cmap=palette(),
                                 norm=norm, edgecolors='face', linewidth=.2,
                                 antialiased=False, snap=True, rasterized=True)
            comparison = mesh_matches(mesh, z)
            # 固定与原pcolormesh相同的显示边界，再生成等高线及其标签缺口。
            ax.set_xlim(ax.get_xlim())
            ax.set_ylim(ax.get_ylim())
            ax.set_xticks([100, 1000, 10000, 30000], ['100', '1000', '10000', '30000'])
            ax.set_yticks([6, 8, 10, 12, 13])
            fig.canvas.draw()
            levels = xian_contour_levels(z, metric)
            contours = ax.contour(x, y, z, levels=levels, colors=[RED], linestyles='-.',
                                  linewidths=STYLE['lw_vline'])
            path_check = label_xian_contours(ax, contours, x, y,
                                             '%.3g' if metric == 'cum_total_infections' else '%.0f')
            for eta, dash in ((151.90, (0, (4, 2))), (26326., (0, (1.2, 2.)))):
                ax.axvline(eta, color=BLACK, lw=STYLE['lw_vline'], ls=dash, alpha=.82, zorder=5)
            if metric == 'control_duration':
                for eta, label in ((151.90, r'$I_{\rm peak}^{\rm T}$'), (26326., r'$\eta=0.002N$')):
                    ax.text(eta, float(y.max()) * .985, label, rotation=90, ha='right', va='top',
                            fontsize=STYLE['note'], color=BLACK, clip_on=False)
            if k >= 2:
                ax.set_xlabel(r'$\eta$')
            else:
                ax.tick_params(labelbottom=False)
            if k % 2 == 0:
                ax.set_ylabel(r'$c_0$')
            else:
                ax.tick_params(labelleft=False)
            ax.set_title(f'({chr(97 + k)})')
            cb = math_colorbar(fig, mesh, cax, symbol)
            if metric == 'cum_total_infections':
                cb.formatter.set_powerlimits((0, 0))
                cb.update_ticks()
            checks['metrics'][metric] = dict(**comparison,
                normalization='linear' if metric == 'cum_total_infections' else 'log',
                color_limits=[lo, hi], contour_levels=levels.tolist(),
                contour_paths_and_inline_gaps=path_check,
                xlim=list(ax.get_xlim()), ylim=list(ax.get_ylim()),
                xscale=ax.get_xscale(), yscale=ax.get_yscale())
        save(fig, 'S8', checks, inputs, ROOT / 'paper/figures/xian_heatmaps.pdf')
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('figures', nargs='*', choices=['S4', 'S6', 'S8'])
    args = parser.parse_args()
    for name in args.figures or ['S4', 'S6', 'S8']:
        dict(S4=preview_s4, S6=preview_s6, S8=preview_s8)[name]()


if __name__ == '__main__':
    main()
