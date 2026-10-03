function capture = matlab_tick_capture(fig, filename, target_size_bp)
%MATLAB_TICK_CAPTURE 最小刻度诊断：跟踪原始 HG、刷新及复制锁定导出。
% 输入必须为本次新绘制的 live HG 场景；不读取历史 FIG/PDF 作为内容。
% 本入口只读刻度和几何，不设置 Units、Position、Tick 或 TickMode。
% 读取 auto 属性本身可能触发 HG 惰性计算，故 before_drawnow 表示首次读取，
% 不是对 MATLAB 内部尚未计算状态的断言。唯一显式刷新是下方 drawnow。

assert(isgraphics(fig, 'figure') && isscalar(fig), 'A live HG figure is required.');
if nargin < 3, target_size_bp = []; end
filename = char(filename);
[folder, stem, ~] = fileparts(filename);
assert(~isempty(stem), 'An output filename or stem is required.');
if isempty(folder), folder = pwd; end
if ~isfolder(folder), mkdir(folder); end
capture_file = fullfile(folder, [stem '.tick_capture.json']);
geometry_file = fullfile(folder, [stem '.geometry.json']);
assert(~isfile(capture_file), 'Refusing to overwrite an existing tick capture.');

capture = struct('purpose', 'live HG auto tick selection diagnostic', ...
    'status', 'not_yet_executed', 'matlab_version', version, ...
    'screen_pixels_per_inch', double(get(groot, 'ScreenPixelsPerInch')), ...
    'requested_target_size_bp', target_size_bp, ...
    'historical_content_used', false, 'tick_property_setting_performed', false, ...
    'geometry_property_setting_by_capture_performed', false, ...
    'original_before_drawnow', tick_snapshot(fig));
drawnow;
capture.original_after_drawnow = tick_snapshot(fig);
capture.original_ticks_unchanged_by_drawnow = same_ticks( ...
    capture.original_before_drawnow, capture.original_after_drawnow);
capture.original_axes_count = numel(capture.original_after_drawnow.axes);
capture.expected_six_axes_present = capture.original_axes_count == 6;
export_error = [];
try
    % 不自行 copyobj 或锁定，直接观测当前正式导出入口的真实行为。
    exported = matlab_export_deterministic(fig, filename, target_size_bp);
    capture.export_report = exported;
    capture.export_reference_geometry = exported.reference_geometry;
    capture.export_succeeded = exported.all_exports_succeeded;
catch err
    export_error = err;
    capture.export_succeeded = false;
    capture.error_identifier = err.identifier;
    capture.error_message = err.message;
    % 导出器若已保存失败记录，则保留其真实参考几何；不伪造成功状态。
    if isfile(geometry_file)
        try
            exported = jsondecode(fileread(geometry_file));
            capture.export_report = exported;
            if isfield(exported, 'reference_geometry')
                capture.export_reference_geometry = exported.reference_geometry;
            end
        catch read_err
            capture.export_report_read_error = read_err.message;
        end
    end
end

if isgraphics(fig, 'figure')
    % 不在这里再刷新或重设原图，避免隐藏导出前后原 HG 的瞬时差异。
    capture.original_after_export = tick_snapshot(fig);
    capture.original_ticks_unchanged_by_export = same_ticks( ...
        capture.original_after_drawnow, capture.original_after_export);
else
    capture.original_figure_valid_after_export = false;
    capture.original_ticks_unchanged_by_export = false;
end
capture.status = 'capture_completed';
fid = fopen(capture_file, 'w', 'n', 'UTF-8');
assert(fid >= 0, 'Cannot open the tick capture report.');
file_guard = onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid, '%s', jsonencode(capture));
fprintf('MATLAB_TICK_CAPTURE_COMPLETE %s\n', capture_file);
if ~isempty(export_error), rethrow(export_error); end
end

function snapshot = tick_snapshot(fig)
% 只记录原始单位和原始位置；不通过来回切换 Units 测量点坐标。
snapshot = struct('figure', struct('units', char(fig.Units), ...
    'position', fig.Position, 'renderer', char(fig.Renderer), ...
    'renderer_mode', char(fig.RendererMode)), 'axes', {{}});
aa = findall(fig, 'Type', 'axes');
rows = cell(1, numel(aa));
properties = {'Tag', 'XLim', 'YLim', 'XLimMode', 'YLimMode', ...
    'XScale', 'YScale', 'XTick', 'YTick', 'XTickMode', 'YTickMode', ...
    'XTickLabel', 'YTickLabel', 'XTickLabelMode', 'YTickLabelMode', ...
    'XTickLabelRotation', 'YTickLabelRotation', 'TickLabelInterpreter', ...
    'Position', 'InnerPosition', 'OuterPosition', 'PositionConstraint', ...
    'FontName', 'FontSize', 'FontUnits'};
for k = 1:numel(aa)
    ax = aa(k);
    row = struct('index', k, 'parent_class', class(ax.Parent), ...
        'Units', char(ax.Units), 'Title', {ax.Title.String}, ...
        'XLabel', {ax.XLabel.String}, 'YLabel', {ax.YLabel.String});
    for j = 1:numel(properties)
        if isprop(ax, properties{j}), row.(properties{j}) = ax.(properties{j}); end
    end
    rulers = {'XAxis', 'YAxis'};
    for j = 1:numel(rulers)
        if isprop(ax, rulers{j})
            ruler = ax.(rulers{j});
            if isscalar(ruler) && isprop(ruler, 'Exponent')
                row.([rulers{j} '_Exponent']) = ruler.Exponent;
            end
            if isscalar(ruler) && isprop(ruler, 'ExponentMode')
                row.([rulers{j} '_ExponentMode']) = char(ruler.ExponentMode);
            end
        end
    end
    rows{k} = row;
end
snapshot.axes = rows;
end

function unchanged = same_ticks(a, b)
% 仅比较原 HG 的刻度及其选择模式，不混入允许改变的导出布局几何。
unchanged = numel(a.axes) == numel(b.axes);
if ~unchanged, return; end
fields = {'XLim', 'YLim', 'XLimMode', 'YLimMode', 'XTick', 'YTick', ...
    'XTickMode', 'YTickMode', 'XTickLabel', 'YTickLabel', ...
    'XTickLabelMode', 'YTickLabelMode', 'XAxis_Exponent', ...
    'YAxis_Exponent', 'XAxis_ExponentMode', 'YAxis_ExponentMode'};
for k = 1:numel(a.axes)
    for j = 1:numel(fields)
        field = fields{j};
        has_a = isfield(a.axes{k}, field); has_b = isfield(b.axes{k}, field);
        if has_a ~= has_b || (has_a && ~isequaln(a.axes{k}.(field), b.axes{k}.(field)))
            unchanged = false;
            return;
        end
    end
end
end
