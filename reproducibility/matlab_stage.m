function matlab_stage(workspace, report_dir)
% 从原函数重算论文 MATLAB 数据；不运行清空目录的旧 run_all。
workspace = strrep(char(workspace), '/', filesep);
report_dir = strrep(char(report_dir), '/', filesep);
assert(isfolder(workspace), 'Reproduction workspace does not exist.');
module = fullfile(workspace, 'scenario1_threshold_landscape');
addpath(fullfile(module, 'common'));
assert(exist('lambertw', 'file') ~= 0, 'Symbolic Math Toolbox lambertw is required.');
cfg = scenario1_params();
assert(startsWith(cfg.paths.run_dir, [workspace filesep]), ...
    'Refusing output outside isolated workspace.');
ensure_output_dirs(cfg);
set(groot, 'DefaultFigureVisible', 'off');
% 每个脚本由独立函数作用域运行，避免原脚本 clear 清掉入口参数。
run_isolated(fullfile(module, 'scripts', 'generate_landscape_data.m'));
run_isolated(fullfile(module, 'scripts', 'validate_main_outputs.m'));
run_isolated(fullfile(module, 'scripts', 'write_main_summary_tables.m'));
run_isolated(fullfile(module, 'scripts', 'plot_heatmaps.m'));
% 旧样式默认值函数会打开图窗；原6绘制前重新锁定不可见，避免显示器窗口约束。
set(groot, 'DefaultFigureVisible', 'off');
run_isolated(fullfile(workspace, 'code', 'scenario1_q_control_with_quarantine_panels.m'));
% 本次副本的原6输出入口已接入fixed-scene vector，不再顺次第二次导出同图。
addpath(fullfile(workspace, 'latex', 'revision_layout_v5'));
layout_matlab();
T = readtable(fullfile(cfg.paths.output_csv, 'landscape_summary.csv'));
assert(height(T) == 28438, 'Wrong grid size.');
report = struct('status', 'pass', 'source', 'original MATLAB scientific functions', ...
    'grid_rows', height(T), 'valid_rows', sum(logical(T.valid)), ...
    'maximum_q_exit_error', max(abs(T.q_t2_error(logical(T.valid)))), ...
    'matlab_version', version, 'symbolic_version', ver('symbolic'), ...
    'historical_cache_used', false);
if ~isfolder(report_dir), mkdir(report_dir); end
fid = fopen(fullfile(report_dir, 'matlab_science.json'), 'w');
assert(fid >= 0, 'Cannot write MATLAB report.');
guard = onCleanup(@() fclose(fid)); %#ok<NASGU>
fprintf(fid, '%s', jsonencode(report));
fprintf('FULL_MATLAB_REPRODUCTION_OK\n');
end

function run_isolated(path)
run(path);
end
