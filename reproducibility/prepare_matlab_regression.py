"""正式绘图出口的隔离五图回归准备；不把复用CSV称为科学复算。"""
from __future__ import annotations
import argparse
import hashlib
import shutil
from pathlib import Path

from bootstrap import ROOT,dump,prepare_workspace
from figures import prepare_matlab_graphics


def prepare(destination: Path,csv: Path) -> Path:
    workspace=prepare_workspace(destination,ROOT)
    target=workspace/'scenario1_threshold_landscape/current_run/output_csv/landscape_summary.csv'
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(csv,target)
    (workspace/'latex/figures/layout_v5').mkdir(parents=True,exist_ok=True)
    (workspace/'latex/revision_layout_v5/qa').mkdir(parents=True,exist_ok=True)
    heat=workspace/'scenario1_threshold_landscape/scripts/plot_heatmaps.m'
    text=heat.read_text(encoding='utf-8-sig')
    heat.write_text(text.replace("'Visible', 'on'","'Visible', 'off'"),encoding='utf-8')
    adaptations=prepare_matlab_graphics(workspace)
    # 只跳过不进入正文的六张独立热图导出；其绘制与最终合图原逻辑仍运行。
    text=heat.read_text(encoding='utf-8')
    needle="""if nargin < 4
    target_size_bp = [];
end
ok = false;"""
    replacement="""if nargin < 4
    target_size_bp = [];
end
if isempty(target_size_bp), ok=true; return; end
ok = false;"""
    if needle not in text:
        raise RuntimeError('Unrecognized non-target heatmap export branch')
    heat.write_text(text.replace(needle,replacement),encoding='utf-8')
    dump(destination/'plot_regression_input.json',{'purpose':'production drawing regression only',
        'fresh_science_rerun':False,'test_only_reuses_current_generated_csv':True,
        'source_csv':str(csv.resolve()),'csv_sha256':hashlib.sha256(csv.read_bytes()).hexdigest(),
        'original_source_modified':False,'adaptations':adaptations})
    return workspace


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    parser.add_argument('csv',type=Path)
    args=parser.parse_args()
    print(prepare(args.output,args.csv))
