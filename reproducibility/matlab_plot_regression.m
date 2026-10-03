function matlab_plot_regression(workspace)
% 只重绘既有本轮新算 CSV 的图；不运行网格重算或清理入口。
workspace = strrep(char(workspace), '/', filesep);
module = fullfile(workspace, 'scenario1_threshold_landscape');
assert(isfolder(module));
assert(isfile(fullfile(module, 'current_run', 'output_csv', 'landscape_summary.csv')));
addpath(fullfile(module, 'common'));
set(groot, 'DefaultFigureVisible', 'off');
run_isolated(fullfile(module, 'scripts', 'plot_heatmaps.m'));
set(groot, 'DefaultFigureVisible', 'off');
run_isolated(fullfile(workspace, 'code', 'scenario1_q_control_with_quarantine_panels.m'));
close all;
addpath(fullfile(workspace, 'latex', 'revision_layout_v5'));
layout_matlab();
fprintf('MATLAB_PLOT_ONLY_REGRESSION_OK\n');
end

function run_isolated(filename)
run(filename);
end
