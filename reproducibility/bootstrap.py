"""建立只含源码、原始输入及明确标识的视觉参考的隔离工作区。"""
from __future__ import annotations
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / 'ai' / 'threshold_control_reproducible_release_20261002'
SOURCE_DIRS = ('code', 'scenario1_threshold_landscape', 'scenario1_inflection',
               'xian_control_comparison', 'xian_dom', 'c0_sensitivity',
               'latex/revision_v4', 'latex/revision_style_restore', 'latex/revision_layout_v5')
UNUSED_PRIVATE_AUDITS = {
    'latex/revision_style_restore/review_collision_geometry.py',
    'latex/revision_style_restore/verify_revision.py',
    'latex/revision_v4/verify_revision.py',
    'latex/revision_layout_v5/verify_layout.py',
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def prepare_workspace(output_dir: Path, root: Path = ROOT) -> Path:
    output_dir = output_dir.resolve()
    if output_dir == root.resolve() or output_dir == (root/'latex').resolve():
        raise ValueError('输出根不得是工作区或正式论文目录。')
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f'必须使用空输出目录，不覆盖旧结果：{output_dir}')
    workspace = output_dir/'workspace'
    if workspace.exists():
        raise FileExistsError(f'必须使用空输出目录：{workspace}')
    workspace.mkdir(parents=True)
    manifest, adaptations = {}, []
    for rel in SOURCE_DIRS:
        for src in (root/rel).rglob('*'):
            if not src.is_file() or src.suffix.lower() not in {'.py','.m','.md'}:
                continue
            if src.relative_to(root).as_posix() in UNUSED_PRIVATE_AUDITS:
                continue
            if any(p in {'before','qa','current_run','outputs','__pycache__'} for p in src.relative_to(root/rel).parts):
                continue
            dst = workspace/src.relative_to(root)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src,dst)
            manifest[str(src.relative_to(root))] = sha(src)
    # 静态原始输入，不复制任何历史生成 CSV、NPZ 或 pickle。
    for rel in ('真实数据/Xianguankong.xlsx','refs/SIQR模型示意图_可编辑.pptx',
                'refs/SIQR模型示意图_Nature配色_可编辑.pptx'):
        src=root/rel
        if not src.exists():
            raise FileNotFoundError(src)
        dst=workspace/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        manifest[rel]=sha(src)
    # PDF 仅是标明用途的视觉回归参考，不供数值求解读取。
    refdir=output_dir/'visual_reference'
    for src in (root/'latex/figures').rglob('*.pdf'):
        dst=refdir/src.relative_to(root/'latex/figures')
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    for rel in ('latex/flatten_curve_analysis_cn.tex','latex/flatten_curve_supplement_cn.tex',
                'latex/elegantpaper.cls','latex/references.bib','latex/build_paper.ps1'):
        src=root/rel; dst=workspace/rel
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); manifest[rel]=sha(src)
    # 机械兼容适配仅作用于运行区副本，原绘图语句/历史脚本保持原样。
    for rel in ('latex/revision_layout_v5/layout_python.py',
                'latex/revision_style_restore/restore_figures.py',
                'latex/revision_v4/plot_revisions.py'):
        dst=workspace/rel; txt=dst.read_text(encoding='utf-8-sig')
        txt,n=re.subn(r"SKILL = .*?\n(?:sys\.path\.insert\(0, ?str\(SKILL\)\)\n)from audit_panel_alignment import require_matplotlib_panel_alignment",
                     'from plotting_checks import require_matplotlib_panel_alignment',txt)
        if n != 1:
            raise RuntimeError(f'未识别外部审计依赖块：{rel}')
        dst.write_text(txt,encoding='utf-8'); adaptations.append({'file':rel,'change':'使用项目内几何检查，移除外部技能路径'})
    dst=workspace/'latex/revision_layout_v5/layout_matlab.m'
    txt=dst.read_text(encoding='utf-8-sig')
    old="fullfile(root, 'archive_unused', 'generated_snapshots', ...\n    'scenario1_threshold_landscape_current_run', 'output_csv', 'landscape_summary.csv')"
    new="fullfile(root, 'scenario1_threshold_landscape', 'current_run', 'output_csv', 'landscape_summary.csv')"
    if old not in txt:
        raise RuntimeError('MATLAB 布局数据路径已改变，需显式适配。')
    dst.write_text(txt.replace(old,new),encoding='utf-8')
    adaptations.append({'file':str(dst.relative_to(workspace)),'change':'读取本次新计算图谱，而非历史快照'})
    dump(output_dir/'source_manifest.json',{'source_files':manifest,'adaptations':adaptations,
         'historical_numerical_caches_copied':False,'visual_reference_only':str(refdir)})
    return workspace

def environment(output_dir: Path) -> dict:
    import numpy, scipy, pandas, matplotlib, openpyxl, PIL
    env={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
         'packages':{m.__name__:m.__version__ for m in (numpy,scipy,pandas,matplotlib,openpyxl,PIL)},
         'tools':{},'fonts':{},'nature_skills_used':False}
    for name in ('xelatex','biber','matlab'):
        exe=shutil.which(name); env['tools'][name]={'path':exe}
        if exe and name!='matlab':
            env['tools'][name]['version']=subprocess.run([exe,'--version'],capture_output=True,text=True,errors='replace').stdout.splitlines()[0]
    try:
        import pymupdf
        env['packages']['PyMuPDF']=pymupdf.VersionBind
    except ImportError:
        env['packages']['PyMuPDF']='missing'
    import importlib.metadata
    pinned={line.split('==',1)[0]:line.split('==',1)[1]
            for line in (Path(__file__).parent/'requirements.txt').read_text(encoding='utf-8').splitlines()
            if '==' in line and not line.startswith('#')}
    mismatches={name:{'expected':version,'actual':importlib.metadata.version(name)}
                for name,version in pinned.items() if importlib.metadata.version(name)!=version}
    env['pinned_packages']=pinned;env['package_version_mismatches']=mismatches
    if mismatches:
        dump(output_dir/'environment.json',env)
        raise RuntimeError('Python 环境与锁定依赖不同，请先安装 requirements.txt：'+str(mismatches))
    from matplotlib.font_manager import findfont, FontProperties
    for name in ('Times New Roman','STIXGeneral'):
        path=Path(findfont(FontProperties(family=name),fallback_to_default=False))
        env['fonts'][name]={'path':str(path),'sha256':sha(path)}
    for name in ('simsun.ttc','simkai.ttf'):
        # 系统字体目录由系统变量发现，不写死某台机器的软件位置。
        import os
        path=Path(os.environ.get('WINDIR',''))/'Fonts'/name
        if path.is_file():env['fonts'][name]={'path':str(path),'sha256':sha(path)}
    kpse=shutil.which('kpsewhich')
    if kpse:
        for name in ('texgyretermes-regular.otf','texgyretermes-italic.otf',
                     'texgyretermes-bold.otf','texgyretermes-bolditalic.otf'):
            found=subprocess.run([kpse,name],capture_output=True,text=True,errors='replace',check=True).stdout.strip()
            if found and Path(found).is_file():
                env['fonts'][name]={'path':found,'sha256':sha(Path(found))}
    dump(output_dir/'environment.json',env)
    return env
