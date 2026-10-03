"""创建源码隔离副本，比较所有五幅 MATLAB 图的原生导出法。

这不是科学复算入口：明确复用本轮刚计算的图谱 CSV 作为绘图测试输入。
正式 runner、历史源脚本和已失败的运行记录均不修改。
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from pathlib import Path

from bootstrap import ROOT, dump, prepare_workspace
from figures import prepare_matlab_graphics


def prepare(destination: Path, csv: Path, *, heatmap_native_image=False) -> Path:
    workspace = prepare_workspace(destination, ROOT)
    copied = workspace / 'scenario1_threshold_landscape/current_run/output_csv/landscape_summary.csv'
    copied.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(csv, copied)
    (workspace / 'latex/revision_layout_v5/qa').mkdir(parents=True, exist_ok=True)
    (workspace / 'latex/figures/layout_v5').mkdir(parents=True, exist_ok=True)
    prepare_matlab_graphics(workspace)
    # 相同原绘制语句；只把输出入口接到独立的各导出法候选函数。
    path = workspace / 'latex/revision_layout_v5/layout_matlab.m'
    text = path.read_text(encoding='utf-8-sig')
    text, count = re.subn(r"function export_final\(fig,stem,sz,here\)[\s\S]*$",
        "function export_final(fig,stem,sz,here)\nmatlab_export_candidate(fig,[stem '.pdf'],sz);\nclose(fig);\nend\n", text)
    assert count == 1
    path.write_text(text, encoding='utf-8')
    path = workspace / 'scenario1_threshold_landscape/scripts/plot_heatmaps.m'
    text = path.read_text(encoding='utf-8-sig').replace("'Visible', 'on'", "'Visible', 'off'")
    text, count = re.subn(r'function ok = save_heatmap_figure_safe\(fig, filename, logfid, target_size_bp\)[\s\S]*$',
        "function ok = save_heatmap_figure_safe(fig, filename, logfid, target_size_bp)\n"
        "if nargin < 4 || isempty(target_size_bp), ok=true; return; end\n"
        "matlab_export_candidate(fig,filename,target_size_bp);\nok=true;\nend\n", text)
    assert count == 1
    if heatmap_native_image:
        text = text.replace('matlab_export_candidate(fig,filename,target_size_bp);',
                            'matlab_heatmap_image_candidate(fig,filename,target_size_bp);')
    path.write_text(text, encoding='utf-8')
    path = workspace / 'code/scenario1_q_control_with_quarantine_panels.m'
    text = path.read_text(encoding='utf-8-sig')
    text, count = re.subn(r"exportgraphics\(gcf, figure_path, \.\.\.\s*'Resolution', 600, 'BackgroundColor', 'white'\);",
                        'matlab_export_candidate(gcf,figure_path,[]);', text)
    if count==0:
        text,count=re.subn(r'matlab_export_deterministic\(gcf,figure_path,\[\]\);',
                          'matlab_export_candidate(gcf,figure_path,[]);',text)
    assert count == 1
    path.write_text(text, encoding='utf-8')
    dump(destination / 'probe_manifest.json', {
        'purpose': 'test-only native export comparison; not a complete science rerun',
        'test_only_reuses_current_generated_csv': True,
        'scientific_recomputation': False,
        'csv_source': str(csv.resolve()),
        'csv_sha256': hashlib.sha256(csv.read_bytes()).hexdigest(),
        'original_scripts_modified': False,
        'heatmap_native_image_test':heatmap_native_image,
        'workspace': str(workspace),
    })
    return workspace


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--heatmap-native-image',action='store_true')
    args = parser.parse_args()
    print(prepare(args.destination, args.csv, heatmap_native_image=args.heatmap_native_image))
