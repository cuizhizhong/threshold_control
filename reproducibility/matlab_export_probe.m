function matlab_export_probe(workspace, only_heatmap)
% 仅用于隔离导出法回归；输入是本轮已重算 CSV，不是新的科学复算。
workspace = strrep(char(workspace), '/', filesep);
if nargin < 2, only_heatmap = false; end
module = fullfile(workspace, 'scenario1_threshold_landscape');
assert(isfolder(module));
assert(isfile(fullfile(module, 'current_run', 'output_csv', 'landscape_summary.csv')));
addpath(fullfile(module, 'common'));
set(groot, 'DefaultFigureVisible', 'off');
if ~only_heatmap
    run_isolated(fullfile(workspace, 'code', 'scenario1_q_control_with_quarantine_panels.m'));
    close all;
end
run_isolated(fullfile(module, 'scripts', 'plot_heatmaps.m'));
close all;
if only_heatmap, fprintf('MATLAB_HEATMAP_IMAGE_PROBE_OK\n'); return; end
addpath(fullfile(workspace, 'latex', 'revision_layout_v5'));
layout_matlab();
fprintf('MATLAB_ALL_FIVE_EXPORT_PROBE_OK\n');
end

function run_isolated(filename)
run(filename);
end
