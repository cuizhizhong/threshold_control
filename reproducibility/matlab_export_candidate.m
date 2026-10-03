function report = matlab_export_candidate(fig, filename, target_size_bp)
%MATLAB_EXPORT_CANDIDATE 测试专用原生导出，不替换论文正式导出入口。
% 输入必须是本次重新绘制的 HG figure；不读取 FIG、PDF 或历史缓存。
% 每种方式直接 copyobj 同一个未导出基准，且只做一次首次导出。
% 像素吸附只用于锁定导出几何；数据、字体、配色、线宽及 LineStyle 不变。
% 输出 stem.print.pdf、stem.vector.pdf、stem.svg、stem.png、stem.geometry.json。

assert(isgraphics(fig, 'figure') && isscalar(fig), 'A live HG figure is required.');
if nargin < 3, target_size_bp = []; end
filename = char(filename);
[folder, stem, ~] = fileparts(filename);
assert(~isempty(stem), 'An output filename or stem is required.');
if isempty(folder), folder = pwd; end
if ~isfolder(folder), mkdir(folder); end
report_file = fullfile(folder, [stem '.geometry.json']);
assert(~isfile(report_file), 'Refusing to overwrite an existing candidate report.');

dpi = double(get(groot, 'ScreenPixelsPerInch'));
assert(isscalar(dpi) && isfinite(dpi) && dpi > 0, 'Invalid logical screen DPI.');
bp_per_pixel = 72 / dpi;
reference = copyobj(fig, groot);
reference_guard = onCleanup(@() close_if_valid(reference)); %#ok<NASGU>
reference.Visible = 'off';
source_geometry = geometry_snapshot(reference, bp_per_pixel);
source_science = science_signature(reference);
if isempty(target_size_bp)
    target_size_bp = source_geometry.figure.position_bp(3:4);
end
target_size_bp = double(reshape(target_size_bp, 1, []));
assert(numel(target_size_bp) == 2 && all(isfinite(target_size_bp)) && ...
    all(target_size_bp > 0), 'The target size must be two positive point values.');
canvas_pixels = max(1, round(target_size_bp / bp_per_pixel));
canvas_bp = canvas_pixels * bp_per_pixel;
[locks, normalization] = normalize_scene(reference, canvas_pixels, canvas_bp, ...
    target_size_bp, bp_per_pixel);
reference_geometry = geometry_snapshot(reference, bp_per_pixel);
assert(isequaln(source_science, science_signature(reference)), ...
    'Geometry normalization unexpectedly changed scientific HG properties.');

report = struct('purpose', 'native MATLAB export candidate experiment', ...
    'status', 'not_yet_executed', 'matlab_version', version, ...
    'screen_pixels_per_inch', dpi, 'point_per_logical_pixel', bp_per_pixel, ...
    'target_size_bp', target_size_bp, 'integer_canvas_pixels', canvas_pixels, ...
    'integer_canvas_size_bp', canvas_bp, 'source_geometry', source_geometry, ...
    'reference_geometry', reference_geometry, 'normalization', normalization, ...
    'source_science_unchanged', true, 'historical_content_used', false, ...
    'independent_first_export_per_mode', true, 'mode_results', {{}});
modes = {'print_pdf', 'exportgraphics_vector_pdf', 'print_svg', 'exportgraphics_png'};
suffixes = {'.print.pdf', '.vector.pdf', '.svg', '.png'};
results = cell(1, numel(modes));
for k = 1:numel(modes)
    output = fullfile(folder, [stem suffixes{k}]);
    result = struct('mode', modes{k}, 'output', output, ...
        'export_succeeded', false, 'error_identifier', '', 'error_message', '');
    candidate = [];
    try
        assert(~isfile(output), 'Refusing to overwrite an existing candidate output.');
        % 不从上一导出 mode 复制；print/exportgraphics 的副作用不能串行传递。
        candidate = copyobj(reference, groot);
        candidate.Visible = 'off';
        apply_locks(candidate, locks, canvas_pixels, target_size_bp);
        drawnow;
        apply_locks(candidate, locks, canvas_pixels, target_size_bp);
        drawnow;
        result.before = geometry_snapshot(candidate, bp_per_pixel);
        result.scientific_hg_properties_same_before = ...
            isequaln(source_science, science_signature(candidate));
        assert(result.scientific_hg_properties_same_before, ...
            'The fresh clone changed scientific HG properties.');
        switch modes{k}
            case 'print_pdf'
                print(candidate, output, '-dpdf', '-painters');
            case 'exportgraphics_vector_pdf'
                exportgraphics(candidate, output, 'ContentType', 'vector', ...
                    'BackgroundColor', 'white', 'Units', 'points', ...
                    'Width', target_size_bp(1), 'Height', target_size_bp(2), ...
                    'Padding', 'figure', 'PreserveAspectRatio', 'on');
            case 'print_svg'
                print(candidate, output, '-dsvg', '-painters');
            case 'exportgraphics_png'
                % PNG 为无损编码；不经过 MATLAB JPEG 或已有 PDF 的栅格化。
                exportgraphics(candidate, output, 'Resolution', 600, ...
                    'BackgroundColor', 'white', 'Units', 'points', ...
                    'Width', target_size_bp(1), 'Height', target_size_bp(2), ...
                    'Padding', 'figure', 'PreserveAspectRatio', 'on');
        end
        % 不在导出后重新 apply_locks，否则会掩盖导出器对对象的修改。
        result.after_immediate = geometry_snapshot(candidate, bp_per_pixel);
        drawnow;
        result.after_drawnow = geometry_snapshot(candidate, bp_per_pixel);
        result.immediate_geometry_drift = geometry_drift(result.before, result.after_immediate);
        result.settled_geometry_drift = geometry_drift(result.before, result.after_drawnow);
        result.scientific_hg_properties_same_after = ...
            isequaln(source_science, science_signature(candidate));
        assert(result.scientific_hg_properties_same_after, ...
            'The exporter changed scientific HG properties.');
        assert(isfile(output), 'The exporter did not create the requested file.');
        info = dir(output);
        result.output_bytes = info.bytes;
        result.export_succeeded = true;
    catch err
        result.error_identifier = err.identifier;
        result.error_message = err.message;
        if ~isempty(candidate) && isgraphics(candidate, 'figure')
            result.geometry_at_failure = geometry_snapshot(candidate, bp_per_pixel);
        end
    end
    close_if_valid(candidate);
    results{k} = result;
end
report.mode_results = results;
report.status = 'experiment_completed';
report.all_exports_succeeded = all(cellfun(@(x) x.export_succeeded, results));
% 这里只报告执行状态，不声称两次运行重复一致或原样式验收通过。
fid = fopen(report_file, 'w', 'n', 'UTF-8');
assert(fid >= 0, 'Cannot open the candidate geometry report.');
file_guard = onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid, '%s', jsonencode(report));
fprintf('MATLAB_EXPORT_CANDIDATE_COMPLETE %s\n', report_file);
end

function [locks, summary] = normalize_scene(fig, pixels, canvas_bp, target_bp, step)
% 先读取相对几何，再调整固定画布；避免原 figure 高度的半像素决定轴边界。
layout_freeze = freeze_layout_parents(fig);
aa = ordered_objects(fig, 'axes');
ll = ordered_objects(fig, 'legend');
cc = ordered_objects(fig, 'colorbar');
locks = struct('axes', {cell(1, numel(aa))}, 'legends', {cell(1, numel(ll))}, ...
    'colorbars', {cell(1, numel(cc))}, 'manual_texts', {{}});
maximum_snap = 0;
for k = 1:numel(aa)
    assert(isequal(aa(k).Parent, fig), ...
        'This experiment currently requires axes parented directly by the figure.');
    aa(k).Units = 'normalized';
    relative = aa(k).Position;
    wanted = relative .* canvas_bp([1 2 1 2]);
    fixed = snap_box(wanted, step);
    locks.axes{k} = struct('position_bp', fixed, 'source_relative_position', relative);
    maximum_snap = max(maximum_snap, edge_displacement(wanted, fixed));
    tt = findall(aa(k), 'Type', 'text');
    for j = 1:numel(tt)
        if ~ismember(char(tt(j).Units), {'points', 'normalized'}), continue; end
        tt(j).Units = 'normalized';
        relative_text = tt(j).Position;
        wanted_text = relative_text;
        wanted_text(1:2) = relative_text(1:2) .* fixed(3:4);
        fixed_text = wanted_text;
        fixed_text(1:2) = round(wanted_text(1:2) / step) * step;
        item = struct('axes_index', k, 'text_index', j, ...
            'position_bp', fixed_text, 'source_relative_position', relative_text);
        locks.manual_texts{end + 1} = item; %#ok<AGROW>
        maximum_snap = max(maximum_snap, max(abs(wanted_text(1:2) - fixed_text(1:2))));
    end
end
for kind = 1:2
    if kind == 1, objects = ll; field = 'legends'; else, objects = cc; field = 'colorbars'; end
    for k = 1:numel(objects)
        objects(k).Units = 'normalized';
        relative = objects(k).Position;
        wanted = relative .* canvas_bp([1 2 1 2]);
        fixed = snap_box(wanted, step);
        locks.(field){k} = struct('position_bp', fixed, 'source_relative_position', relative);
        maximum_snap = max(maximum_snap, edge_displacement(wanted, fixed));
    end
end
apply_locks(fig, locks, pixels, target_bp);
drawnow;
apply_locks(fig, locks, pixels, target_bp);
drawnow;
summary = struct('pixel_snap_is_geometry_only', true, ...
    'maximum_edge_or_manual_anchor_snap_bp', maximum_snap, ...
    'maximum_canvas_size_displacement_bp', max(abs(canvas_bp - target_bp)), ...
    'scientific_hg_line_styles_changed', false, 'layout_freeze', layout_freeze, ...
    'axes_units', 'points', 'legend_units', 'points', ...
    'legend_location', 'none', 'pixel_grid_step_bp', step);
end

function records = freeze_layout_parents(fig)
% tiledlayout 的 PositionConstraint 不生效；在测试副本中脱离自动布局管理。
% 先一次性测量所有对象相对 figure 的规范物理位置，再改 Parent。
% 不删坐标轴、colorbar、曲线、文字或布局对象；原输入 figure 不受影响。
types = {'axes', 'legend', 'colorbar'};
groups = cell(1, numel(types));
positions = cell(1, numel(types));
records = {};
for t = 1:numel(types)
    groups{t} = ordered_objects(fig, types{t});
    positions{t} = cell(1, numel(groups{t}));
    for k = 1:numel(groups{t})
        h = groups{t}(k);
        positions{t}{k} = position_in_figure_points(h, fig);
        if ~isequal(h.Parent, fig)
            parent = h.Parent;
            item = struct('type', types{t}, 'index', k, ...
                'source_parent_class', class(parent), ...
                'figure_position_bp', positions{t}{k}, ...
                'relative_parent_position_bp', position_in_points(h));
            if isprop(parent, 'InnerPosition') && isprop(parent, 'Units')
                old_units = parent.Units;
                parent.Units = 'points';
                item.parent_inner_position_bp = parent.InnerPosition;
                parent.Units = old_units;
            end
            records{end + 1} = item; %#ok<AGROW>
        end
    end
end
for t = 1:numel(types)
    % 逆序 reparent，保留兄弟 HG 对象的原绘制次序。
    objects = groups{t};
    for k = numel(objects):-1:1
        h = objects(k);
        if ~isequal(h.Parent, fig)
            h.Parent = fig;
            h.Units = 'points';
            h.Position = positions{t}{k};
        end
    end
end
drawnow;
end

function apply_locks(fig, locks, pixels, target_bp)
% 纸张设置先于实际几何记录；整数 screen canvas 与物理纸张分别显式记录。
if isprop(fig, 'WindowState'), fig.WindowState = 'normal'; end
if isprop(fig, 'WindowStyle'), fig.WindowStyle = 'normal'; end
fig.Units = 'pixels';
fig.Position = [64 64 pixels];
fig.Resize = 'off';
fig.ToolBar = 'none';
fig.MenuBar = 'none';
fig.Color = 'w';
fig.InvertHardcopy = 'off';
fig.PaperUnits = 'points';
fig.PaperSize = target_bp;
fig.PaperPosition = [0 0 target_bp];
fig.PaperPositionMode = 'manual';
fig.Renderer = 'painters';
aa = ordered_objects(fig, 'axes');
assert(numel(aa) == numel(locks.axes), 'Axes changed during cloning.');
for k = 1:numel(aa)
    aa(k).Units = 'points';
    if isprop(aa(k), 'PositionConstraint'), aa(k).PositionConstraint = 'innerposition'; end
    aa(k).Position = locks.axes{k}.position_bp;
    if isprop(aa(k), 'Toolbar') && ~isempty(aa(k).Toolbar)
        aa(k).Toolbar.Visible = 'off';
    end
end
ll = ordered_objects(fig, 'legend');
assert(numel(ll) == numel(locks.legends), 'Legends changed during cloning.');
for k = 1:numel(ll)
    ll(k).Units = 'points';
    ll(k).AutoUpdate = 'off';
    ll(k).Location = 'none';
    ll(k).Position = locks.legends{k}.position_bp;
end
cc = ordered_objects(fig, 'colorbar');
assert(numel(cc) == numel(locks.colorbars), 'Colorbars changed during cloning.');
for k = 1:numel(cc)
    cc(k).Units = 'points';
    cc(k).Position = locks.colorbars{k}.position_bp;
end
for k = 1:numel(locks.manual_texts)
    item = locks.manual_texts{k};
    tt = findall(aa(item.axes_index), 'Type', 'text');
    h = tt(item.text_index);
    h.Units = 'points';
    h.Position = item.position_bp;
end
end

function objects = ordered_objects(fig, type)
% findall 的 HG 子对象顺序在直接 copyobj 时保留，不依赖新句柄数值排序。
objects = findall(fig, 'Type', type);
end

function fixed = snap_box(wanted, step)
edges = [wanted(1:2), wanted(1:2) + wanted(3:4)];
edges = round(edges / step) * step;
edges(3:4) = max(edges(3:4), edges(1:2) + step);
fixed = [edges(1:2), edges(3:4) - edges(1:2)];
end

function delta = edge_displacement(a, b)
ea = [a(1:2), a(1:2) + a(3:4)];
eb = [b(1:2), b(1:2) + b(3:4)];
delta = max(abs(ea - eb));
end

function snapshot = geometry_snapshot(fig, step)
source_units = char(fig.Units);
position_bp = position_in_points(fig);
fig.Units = 'pixels';
pixels = fig.Position;
fig.Units = source_units;
snapshot = struct('figure', struct('units', source_units, ...
    'position_in_original_units', fig.Position, 'position_pixels', pixels, ...
    'position_bp', position_bp, 'logical_pixel_size_bp', step), ...
    'paper', struct('units', char(fig.PaperUnits), 'size', fig.PaperSize, ...
    'position', fig.PaperPosition, 'position_mode', char(fig.PaperPositionMode)), ...
    'axes', {{}}, 'legends', {{}}, 'colorbars', {{}}, 'texts', {{}});
for kind = 1:3
    types = {'axes', 'legend', 'colorbar'};
    fields = {'axes', 'legends', 'colorbars'};
    objects = ordered_objects(fig, types{kind});
    rows = cell(1, numel(objects));
    for k = 1:numel(objects)
        h = objects(k);
        row = struct('index', k, 'units', char(h.Units), ...
            'parent_class', class(h.Parent), ...
            'position_bp', position_in_figure_points(h, fig));
        if isprop(h, 'Location'), row.location = char(h.Location); end
        if isprop(h, 'PositionConstraint'), row.position_constraint = char(h.PositionConstraint); end
        if strcmp(types{kind}, 'axes')
            properties = {'XLim', 'YLim', 'ZLim', 'XScale', 'YScale', 'ZScale', ...
                'CLim', 'PlotBoxAspectRatio', 'PlotBoxAspectRatioMode', ...
                'DataAspectRatio', 'DataAspectRatioMode', 'View', ...
                'CameraPosition', 'CameraPositionMode', 'CameraTarget', ...
                'CameraTargetMode', 'CameraUpVector', 'CameraUpVectorMode', ...
                'CameraViewAngle', 'CameraViewAngleMode'};
            for j = 1:numel(properties)
                if isprop(h, properties{j}), row.(properties{j}) = h.(properties{j}); end
            end
        end
        rows{k} = row;
    end
    snapshot.(fields{kind}) = rows;
end
tt = findall(fig, 'Type', 'text');
rows = cell(1, numel(tt));
for k = 1:numel(tt)
    rows{k} = struct('index', k, 'units', char(tt(k).Units), ...
        'position', tt(k).Position, 'string', {tt(k).String}, ...
        'font_name', tt(k).FontName, 'font_size', tt(k).FontSize, ...
        'font_units', char(tt(k).FontUnits), 'interpreter', char(tt(k).Interpreter));
end
snapshot.texts = rows;
end

function position = position_in_points(h)
units = h.Units;
unit_guard = onCleanup(@() set(h, 'Units', units)); %#ok<NASGU>
h.Units = 'points';
position = h.Position;
end

function position = position_in_figure_points(h, fig)
if isequal(h.Parent, fig)
    position = position_in_points(h);
else
    % recursive 位置包含父容器的 InnerPosition 偏移；单位转换保留像素原点约定。
    recursive_pixels = getpixelposition(h, true);
    position = hgconvertunits(fig, recursive_pixels, 'pixels', 'points', fig);
end
end

function drift = geometry_drift(before, after)
fields = {'axes', 'legends', 'colorbars'};
drift = struct('figure_position_maximum_bp', ...
    max(abs(before.figure.position_bp - after.figure.position_bp)));
overall = drift.figure_position_maximum_bp;
for f = 1:numel(fields)
    a = before.(fields{f}); b = after.(fields{f});
    assert(numel(a) == numel(b), 'Object count changed during export.');
    deltas = zeros(1, numel(a));
    for k = 1:numel(a), deltas(k) = edge_displacement(a{k}.position_bp, b{k}.position_bp); end
    drift.([fields{f} '_edge_maximum_bp']) = max([0 deltas]);
    drift.([fields{f} '_per_object_bp']) = deltas;
    overall = max(overall, max([0 deltas]));
end
drift.box_geometry_maximum_bp = overall;
end

function signature = science_signature(fig)
% 比较 HG 科学数据与显示语义；不把允许调整的 Position/Units 纳入数据签名。
types = {'line', 'surface', 'image', 'patch', 'scatter', 'contour', 'axes', 'text', 'legend'};
properties = {'XData', 'YData', 'ZData', 'CData', 'Faces', 'Vertices', ...
    'FaceVertexCData', 'SizeData', 'Color', 'FaceColor', 'EdgeColor', ...
    'LineWidth', 'LineStyle', 'Marker', 'MarkerSize', 'MarkerFaceColor', ...
    'MarkerEdgeColor', 'String', 'FontName', 'FontSize', 'FontUnits', ...
    'FontWeight', 'FontAngle', 'Interpreter', 'DisplayName', ...
    'LevelList', 'TextList', 'Fill', 'ShowText', 'XLim', 'YLim', 'ZLim', ...
    'XScale', 'YScale', 'ZScale', 'CLim', 'View', 'PlotBoxAspectRatioMode', ...
    'DataAspectRatioMode', 'CameraPositionMode', 'CameraTargetMode', ...
    'CameraUpVectorMode', 'CameraViewAngleMode'};
signature = cell(1, numel(types));
for t = 1:numel(types)
    hh = findall(fig, 'Type', types{t});
    rows = cell(1, numel(hh));
    for k = 1:numel(hh)
        row = struct('type', types{t});
        for j = 1:numel(properties)
            if isprop(hh(k), properties{j}), row.(properties{j}) = hh(k).(properties{j}); end
        end
        if strcmp(types{t}, 'axes')
            physical = {'PlotBoxAspectRatio', 'DataAspectRatio', 'CameraPosition', ...
                'CameraTarget', 'CameraUpVector', 'CameraViewAngle'};
            for j = 1:numel(physical)
                mode = [physical{j} 'Mode'];
                if isprop(hh(k), mode) && strcmp(hh(k).(mode), 'manual')
                    row.(physical{j}) = hh(k).(physical{j});
                end
            end
        end
        rows{k} = row;
    end
    % 布局容器 reparent 会改变遍历次序；只作排序键，不舍入原始数值用于比较。
    keys = cellfun(@jsonencode, rows, 'UniformOutput', false);
    [~, order] = sort(keys);
    signature{t} = rows(order);
end
end

function close_if_valid(fig)
if ~isempty(fig) && isgraphics(fig, 'figure'), delete(fig); end
end
