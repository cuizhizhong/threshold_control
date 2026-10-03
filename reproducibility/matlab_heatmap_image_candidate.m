function report = matlab_heatmap_image_candidate(fig, filename, target_size_bp)
%MATLAB_HEATMAP_IMAGE_CANDIDATE 独立热图原生 PNG 实验，不调用 print/vector。
% 只接受本次新绘制的 HG 场景；不读取或转码历史图、PDF、FIG、JPEG。
% 保留 source Renderer/RendererMode；两个干净副本只区分 GraphicsSmoothing。
% 像素吸附是几何稳定化，不改网格、等高线、字体、颜色、线型或线宽。
% 输出 stem.smoothing_on.png、stem.smoothing_off.png、stem.image_geometry.json。
assert(isgraphics(fig, 'figure') && isscalar(fig), 'A live HG figure is required.');
if nargin < 3, target_size_bp = []; end
[folder, stem, ~] = fileparts(char(filename));
assert(~isempty(stem), 'An output stem is required.');
if isempty(folder), folder = pwd; end
if ~isfolder(folder), mkdir(folder); end
report_file = fullfile(folder, [stem '.image_geometry.json']);
assert(~isfile(report_file), 'Refusing to overwrite an existing image candidate report.');
dpi = double(get(groot, 'ScreenPixelsPerInch'));
assert(isfinite(dpi) && dpi > 0, 'Invalid logical screen DPI.');
step = 72 / dpi;
reference = copyobj(fig, groot);
reference_guard = onCleanup(@() close_if_valid(reference)); %#ok<NASGU>
reference.Visible = 'off';
drawnow;
source = geometry(reference);
source_semantics = scientific_semantics(reference);
source_renderer = renderer_state(reference);
if isempty(target_size_bp), target_size_bp = source.figure.position_bp(3:4); end
target_size_bp = double(reshape(target_size_bp, 1, []));
assert(numel(target_size_bp) == 2 && all(isfinite(target_size_bp)) && ...
    all(target_size_bp > 0), 'The target size must contain two positive point values.');
pixels = max(1, round(target_size_bp / step));
canvas_bp = pixels * step;
layout_freeze = flatten_layout(reference);
[locks, maximum_snap_bp] = capture_locks(reference, canvas_bp, step);
apply_locks(reference, locks, pixels);
drawnow;
apply_locks(reference, locks, pixels);
drawnow;
assert(isequaln(source_semantics, scientific_semantics(reference)), ...
    'Geometry locking changed HG scientific data, font or line-style properties.');
assert(isequaln(source_renderer, renderer_state(reference)), ...
    'Geometry locking changed the source renderer or its mode.');
report = struct('purpose', 'native heatmap PNG smoothing experiment', ...
    'status', 'not_yet_executed', 'matlab_version', version, ...
    'screen_pixels_per_inch', dpi, 'point_per_logical_pixel', step, ...
    'target_size_bp', target_size_bp, 'export_size_bp', target_size_bp + 3, ...
    'integer_canvas_pixels', pixels, 'integer_canvas_size_bp', canvas_bp, ...
    'maximum_edge_snap_bp', maximum_snap_bp, ...
    'maximum_canvas_size_displacement_bp', max(abs(canvas_bp - target_size_bp)), ...
    'source_geometry', source, 'source_renderer', source_renderer, ...
    'reference_geometry', geometry(reference), 'layout_freeze', {layout_freeze}, ...
    'source_semantics_unchanged', true, 'historical_content_used', false, ...
    'renderer_setting_performed', false, 'print_or_vector_export_used', false, ...
    'resolution_dpi', 600, 'padding', 'figure', 'preserve_aspect_ratio', 'on', ...
    'independent_first_export_per_mode', true, 'mode_results', {{}});
states = {'on', 'off'};
results = cell(1, numel(states));
for k = 1:numel(states)
    output = fullfile(folder, [stem '.smoothing_' states{k} '.png']);
    result = struct('graphics_smoothing', states{k}, 'output', output, ...
        'export_succeeded', false, 'error_identifier', '', 'error_message', '');
    candidate = [];
    try
        assert(~isfile(output), 'Refusing to overwrite an existing image candidate output.');
        candidate = copyobj(reference, groot);
        candidate.Visible = 'off';
        assert(isprop(candidate, 'GraphicsSmoothing'), 'GraphicsSmoothing is unavailable.');
        candidate.GraphicsSmoothing = states{k};
        apply_locks(candidate, locks, pixels);
        drawnow;
        apply_locks(candidate, locks, pixels);
        drawnow;
        result.before = geometry(candidate);
        result.renderer_same_before = isequaln(source_renderer, renderer_state(candidate));
        result.historical_content_used = false;
        result.data_fonts_line_style_same_before = ...
            isequaln(source_semantics, scientific_semantics(candidate));
        assert(result.renderer_same_before, 'The fresh clone changed the source renderer.');
        assert(result.data_fonts_line_style_same_before, 'The fresh clone changed HG semantics.');
        % 直接从 HG 调用原生 image 路径；PNG 无损，无 vector 中间层或 JPEG 编码。
        exportgraphics(candidate, output, 'ContentType', 'image', 'Resolution', 600, ...
            'BackgroundColor', 'white', 'Units', 'points', ...
            'Width', target_size_bp(1) + 3, 'Height', target_size_bp(2) + 3, ...
            'Padding', 'figure', 'PreserveAspectRatio', 'on');
        result.after_immediate = geometry(candidate);
        drawnow;
        result.after_drawnow = geometry(candidate);
        result.immediate_geometry_drift = geometry_drift(result.before, result.after_immediate);
        result.settled_geometry_drift = geometry_drift(result.before, result.after_drawnow);
        result.renderer_same_after = isequaln(source_renderer, renderer_state(candidate));
        result.data_fonts_line_style_same_after = ...
            isequaln(source_semantics, scientific_semantics(candidate));
        assert(result.data_fonts_line_style_same_after, 'Native image export changed HG semantics.');
        assert(isfile(output), 'Native image export did not create the requested PNG.');
        info = dir(output); result.output_bytes = info.bytes;
        result.export_succeeded = true;
    catch err
        result.error_identifier = err.identifier;
        result.error_message = err.message;
        if ~isempty(candidate) && isgraphics(candidate, 'figure')
            result.geometry_at_failure = geometry(candidate);
        end
    end
    close_if_valid(candidate);
    results{k} = result;
end
report.mode_results = results;
report.status = 'experiment_completed';
report.all_exports_succeeded = all(cellfun(@(r) r.export_succeeded, results));
% 不把单次成功或 HG 属性一致自动升级为跨进程像素重复/实际线型验收通过。
fid = fopen(report_file, 'w', 'n', 'UTF-8');
assert(fid >= 0, 'Cannot open the image candidate geometry report.');
file_guard = onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid, '%s', jsonencode(report));
fprintf('MATLAB_HEATMAP_IMAGE_CANDIDATE_COMPLETE %s\n', report_file);
end

function records = flatten_layout(fig)
% 先测全部元素相对 figure 的物理位置，再让测试副本脱离 tiledlayout 管理。
types = {'axes', 'legend', 'colorbar'};
groups = cell(1, numel(types)); positions = cell(1, numel(types)); records = {};
for t = 1:numel(types)
    groups{t} = findall(fig, 'Type', types{t});
    positions{t} = cell(1, numel(groups{t}));
    for k = 1:numel(groups{t})
        h = groups{t}(k); positions{t}{k} = figure_position_bp(h, fig);
        if ~isequal(h.Parent, fig)
            parent = h.Parent;
            row = struct('type', types{t}, 'index', k, 'parent_class', class(parent), ...
                'figure_position_bp', positions{t}{k}, 'relative_parent_position_bp', position_bp(h));
            if isprop(parent, 'InnerPosition') && isprop(parent, 'Units')
                units = parent.Units; parent.Units = 'points';
                row.parent_inner_position_bp = parent.InnerPosition; parent.Units = units;
            end
            records{end + 1} = row; %#ok<AGROW>
        end
    end
end
for t = 1:numel(types)
    objects = groups{t};
    for k = numel(objects):-1:1
        h = objects(k);
        if ~isequal(h.Parent, fig)
            h.Parent = fig; h.Units = 'points'; h.Position = positions{t}{k};
        end
    end
end
drawnow;
end

function [locks, largest] = capture_locks(fig, canvas_bp, step)
types = {'axes', 'legend', 'colorbar'};
locks = struct('boxes', {cell(1, numel(types))}, 'texts', {{}}); largest = 0;
for t = 1:numel(types)
    hh = findall(fig, 'Type', types{t}); rows = cell(1, numel(hh));
    for k = 1:numel(hh)
        hh(k).Units = 'normalized'; wanted = hh(k).Position .* canvas_bp([1 2 1 2]);
        edges = [wanted(1:2), wanted(1:2) + wanted(3:4)];
        snapped = round(edges / step) * step;
        snapped(3:4) = max(snapped(3:4), snapped(1:2) + step);
        fixed = [snapped(1:2), snapped(3:4) - snapped(1:2)];
        rows{k} = fixed; largest = max(largest, max(abs(edges - snapped)));
        if t == 1
            tt = findall(hh(k), 'Type', 'text');
            for j = 1:numel(tt)
                if ~ismember(char(tt(j).Units), {'points', 'normalized'}), continue; end
                tt(j).Units = 'normalized'; p = tt(j).Position;
                p(1:2) = p(1:2) .* fixed(3:4); old = p;
                p(1:2) = round(p(1:2) / step) * step;
                largest = max(largest, max(abs(p(1:2) - old(1:2))));
                locks.texts{end + 1} = struct('axes_index', k, 'text_index', j, 'position_bp', p); %#ok<AGROW>
            end
        end
    end
    locks.boxes{t} = rows;
end
end

function apply_locks(fig, locks, pixels)
% 不设置 Renderer、RendererMode、PaperSize、PaperPosition 或任何线型属性。
if isprop(fig, 'WindowState'), fig.WindowState = 'normal'; end
if isprop(fig, 'WindowStyle'), fig.WindowStyle = 'normal'; end
fig.Units = 'pixels'; fig.Position = [64 64 pixels]; fig.Resize = 'off';
fig.ToolBar = 'none'; fig.MenuBar = 'none';
types = {'axes', 'legend', 'colorbar'};
for t = 1:numel(types)
    hh = findall(fig, 'Type', types{t});
    assert(numel(hh) == numel(locks.boxes{t}), 'Cloning changed a geometry object count.');
    for k = 1:numel(hh)
        hh(k).Units = 'points';
        if t == 1
            if isprop(hh(k), 'PositionConstraint'), hh(k).PositionConstraint = 'innerposition'; end
            if isprop(hh(k), 'Toolbar') && ~isempty(hh(k).Toolbar), hh(k).Toolbar.Visible = 'off'; end
        elseif t == 2
            hh(k).AutoUpdate = 'off'; hh(k).Location = 'none';
        end
        hh(k).Position = locks.boxes{t}{k};
    end
end
aa = findall(fig, 'Type', 'axes');
for k = 1:numel(locks.texts)
    item = locks.texts{k}; tt = findall(aa(item.axes_index), 'Type', 'text');
    h = tt(item.text_index); h.Units = 'points'; h.Position = item.position_bp;
end
end

function result = renderer_state(fig)
result = struct('renderer', char(fig.Renderer), 'renderer_mode', char(fig.RendererMode));
end

function snapshot = geometry(fig)
snapshot = struct('figure', struct('units', char(fig.Units), ...
    'position', fig.Position, 'position_bp', position_bp(fig), ...
    'renderer', char(fig.Renderer), 'renderer_mode', char(fig.RendererMode), ...
    'graphics_smoothing', char(fig.GraphicsSmoothing)), 'axes', {{}}, ...
    'legends', {{}}, 'colorbars', {{}}, 'texts', {{}});
types = {'axes', 'legend', 'colorbar'}; fields = {'axes', 'legends', 'colorbars'};
for t = 1:numel(types)
    hh = findall(fig, 'Type', types{t}); rows = cell(1, numel(hh));
    for k = 1:numel(hh)
        row = struct('index', k, 'parent_class', class(hh(k).Parent), ...
            'units', char(hh(k).Units), 'position_bp', figure_position_bp(hh(k), fig));
        properties = {'XLim', 'YLim', 'ZLim', 'XScale', 'YScale', 'ZScale', 'CLim', ...
            'PlotBoxAspectRatio', 'PlotBoxAspectRatioMode', 'DataAspectRatio', ...
            'DataAspectRatioMode', 'View', 'CameraPosition', 'CameraPositionMode', ...
            'CameraTarget', 'CameraTargetMode', 'CameraUpVector', 'CameraUpVectorMode', ...
            'CameraViewAngle', 'CameraViewAngleMode', 'Location'};
        for j = 1:numel(properties)
            if isprop(hh(k), properties{j}), row.(properties{j}) = hh(k).(properties{j}); end
        end
        rows{k} = row;
    end
    snapshot.(fields{t}) = rows;
end
tt = findall(fig, 'Type', 'text'); rows = cell(1, numel(tt));
for k = 1:numel(tt)
    rows{k} = struct('units', char(tt(k).Units), 'position', tt(k).Position, ...
        'string', {tt(k).String}, 'font_name', tt(k).FontName, 'font_size', tt(k).FontSize, ...
        'font_units', char(tt(k).FontUnits), 'rotation', tt(k).Rotation);
end
snapshot.texts = rows;
end

function p = position_bp(h)
units = h.Units; guard = onCleanup(@() set(h, 'Units', units)); %#ok<NASGU>
h.Units = 'points'; p = h.Position;
end

function p = figure_position_bp(h, fig)
if isequal(h.Parent, fig), p = position_bp(h);
else, p = hgconvertunits(fig, getpixelposition(h, true), 'pixels', 'points', fig); end
end

function drift = geometry_drift(before, after)
drift = struct('figure_position_maximum_bp', ...
    max(abs(before.figure.position_bp - after.figure.position_bp)));
overall = drift.figure_position_maximum_bp; fields = {'axes', 'legends', 'colorbars'};
for t = 1:numel(fields)
    aa = before.(fields{t}); bb = after.(fields{t});
    assert(numel(aa) == numel(bb), 'Native export changed an object count.');
    deltas = zeros(1, numel(aa));
    for k = 1:numel(aa)
        a = aa{k}.position_bp; b = bb{k}.position_bp;
        deltas(k) = max(abs([a(1:2), a(1:2) + a(3:4)] - [b(1:2), b(1:2) + b(3:4)]));
    end
    drift.([fields{t} '_per_object_bp']) = deltas;
    drift.([fields{t} '_edge_maximum_bp']) = max([0 deltas]);
    overall = max(overall, max([0 deltas]));
end
drift.box_geometry_maximum_bp = overall;
end

function signature = scientific_semantics(fig)
types = {'line', 'surface', 'image', 'patch', 'scatter', 'contour', 'axes', 'text', 'legend'};
properties = {'XData', 'YData', 'ZData', 'CData', 'Faces', 'Vertices', 'FaceVertexCData', ...
    'SizeData', 'Color', 'LineColor', 'FaceColor', 'EdgeColor', 'FaceAlpha', 'EdgeAlpha', ...
    'LineWidth', 'LineStyle', 'Marker', 'MarkerSize', 'MarkerFaceColor', 'MarkerEdgeColor', ...
    'String', 'FontName', 'FontSize', 'FontUnits', 'FontWeight', 'FontAngle', 'Rotation', ...
    'Interpreter', 'DisplayName', 'LevelList', 'TextList', 'ContourMatrix', 'Fill', 'ShowText', ...
    'XLim', 'YLim', 'ZLim', 'XScale', 'YScale', 'ZScale', 'CLim', 'Colormap', 'View', ...
    'PlotBoxAspectRatioMode', 'DataAspectRatioMode', 'CameraPositionMode', ...
    'CameraTargetMode', 'CameraUpVectorMode', 'CameraViewAngleMode'};
signature = cell(1, numel(types));
for t = 1:numel(types)
    hh = findall(fig, 'Type', types{t}); rows = cell(1, numel(hh));
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
    % JSON 仅用于无句柄排序；最后 isequaln 比较未舍入的原始 HG 属性。
    keys = cellfun(@jsonencode, rows, 'UniformOutput', false); [~, order] = sort(keys);
    signature{t} = rows(order);
end
end

function close_if_valid(fig)
if ~isempty(fig) && isgraphics(fig, 'figure'), delete(fig); end
end
