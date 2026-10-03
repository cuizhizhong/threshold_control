function result = matlab_fixed_graphics(operation, varargin)
% 仅锁定图形导出几何；不改变科学数据、曲线或原样式。
switch operation
    case 'panel'
        fixed_panel_label(varargin{1}, varargin{2});
        result = true;
    case 'heatmap'
        result = fixed_heatmap_export(varargin{1}, varargin{2}, varargin{3});
    case 'six_approved_ticks'
        result = fixed_six_approved_ticks(varargin{1});
    otherwise
        error('Unknown fixed graphics operation: %s', operation);
end
end

function result = fixed_six_approved_ticks(fig)
% 当前 MATLAB auto picker 已在新源 HG 中选择 50；明确恢复批准参考的100刻度。
% 这是此版本基准图的显示配置，不改变数据、ylim、其它轴或任何字体属性。
aa = findall(fig, 'Type', 'axes');
assert(numel(aa) == 6, 'The approved baseline requires exactly six axes.');
match = arrayfun(@(ax) isequal(ax.Title.String, '$I$') && ...
    isequal(ax.YLabel.String, '$I(t)$'), aa);
assert(nnz(match) == 1, 'Cannot uniquely identify the approved community I axis.');
ax = aa(match);
before_limits = ax.YLim;
before_children = ax.Children;
old_ticks = ax.YTick;
ax.YTick = 0:100:300;
assert(isequaln(ax.YLim, before_limits) && isequal(ax.Children, before_children), ...
    'Approved tick restoration changed limits or plotted objects.');
result = struct('axis_title', ax.Title.String, 'source_auto_ticks', old_ticks, ...
    'approved_ticks', ax.YTick, 'reference', ...
    'latex/figures/optimal_control_with_quarantine_panels.pdf', ...
    'change_is_display_only', true);
setappdata(fig, 'ApprovedTickRestoration', result);
end

function fixed_panel_label(ax, k)
% 偏移来自已认可 PDF 的 TimesNewRomanPS-BoldMT 字符原点。
% 三个独立字符避免 print 对整个非数学字符串施加不稳定的 0.75 pt 字距。
assert(k >= 1 && k <= 6);
label = sprintf('(%c)', 'a' + k - 1);
h = text(ax, -.02, 1.015, label(1), 'Units', 'normalized', ...
    'FontName', 'Times New Roman', 'FontSize', 11, 'FontWeight', 'bold', ...
    'Interpreter', 'none', 'Color', [.133 .133 .133], ...
    'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom', 'Clipping', 'off');
h.Units = 'points';
anchor = h.Position;
closing_offsets = [9, 9, 8.25, 9, 9, 7.5];
% 阈值敏感性图的批准参考中 (b) 右括号原点是 9.75 pt。
if strcmp(ax.XScale, 'log') && k == 2
    closing_offsets(k) = 9.75;
end
offsets = [0, 3.75, closing_offsets(k)];
for j = 2:3
    text(ax, anchor(1) + offsets(j), anchor(2), label(j), 'Units', 'points', ...
        'FontName', 'Times New Roman', 'FontSize', 11, 'FontWeight', 'bold', ...
        'Interpreter', 'none', 'Color', [.133 .133 .133], ...
        'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom', 'Clipping', 'off');
end
end

function okay = fixed_heatmap_export(fig, filename, target_size_bp)
% 先从新HG生成确定的原生路径/字体；Python600dpi无损封装保持原image形式。
report = matlab_export_deterministic(fig,filename,target_size_bp);
okay = report.all_exports_succeeded;
end
