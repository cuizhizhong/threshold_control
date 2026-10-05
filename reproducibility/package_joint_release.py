"""按批准稿源打包可编译论文、活动源码及本轮证据；不打包环境或字体。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from bootstrap import SOURCE_DIRS, UNUSED_PRIVATE_AUDITS
from manuscript_version import load_version


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(root: Path, output: Path, runs: list[Path], report: Path) -> dict:
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root / 'reproducibility/deliverables') or output.exists():
        raise ValueError('交付目录必须是项目deliverables内尚未存在的新目录')
    version = load_version(root, required=True)
    selected = set()
    for name in ['AGENTS.md', 'README.md', '.gitattributes', '.gitignore',
                 'latex/flatten_curve_analysis_cn.tex', 'latex/flatten_curve_analysis_cn.pdf',
                 'latex/flatten_curve_supplement_cn.tex', 'latex/flatten_curve_supplement_cn.pdf',
                 'latex/elegantpaper.cls', 'latex/references.bib', 'latex/build_paper.ps1',
                 '真实数据/Xianguankong.xlsx', 'refs/SIQR模型示意图_可编辑.pptx',
                 'refs/SIQR模型示意图_Nature配色_可编辑.pptx', 'joint_control/README.md']:
        selected.add(root / name)
    for figure in version['inventory']['main']['figures']:
        selected.add(root / 'latex/figures' / figure['image'])
    for folder in SOURCE_DIRS:
        for path in (root / folder).rglob('*'):
            if not path.is_file() or path.suffix.lower() not in {'.py', '.m', '.md'}:
                continue
            if path.relative_to(root).as_posix() in UNUSED_PRIVATE_AUDITS:
                continue
            if any(p in {'before', 'qa', 'current_run', 'outputs', '__pycache__'}
                   for p in path.relative_to(root / folder).parts):
                continue
            selected.add(path)
    selected.update(path for path in (root / 'reproducibility').glob('*')
                    if path.is_file() and path.suffix in {'.py', '.ps1', '.json', '.md', '.txt', '.m'})
    for folder in ['reproducibility/publication', 'reproducibility/joint_extra', 'reproducibility/tests',
                   'reproducibility/manuscript_versions',
                   'reproducibility/release_reports/20261003_release_final',
                   'reproducibility/backups/joint_integration_20261004_212826',
                   'reproducibility/backups/joint_integration_first_round_solver_20261004',
                   'reproducibility/backups/joint_integration_second_round_solver_20261004',
                   'joint_control/threshold_control_reproducible_release_20261002',
                   version['inherited_science_reference']]:
        selected.update(p for p in (root / folder).rglob('*')
                        if p.is_file() and '__pycache__' not in p.parts)
    for run in runs:
        run = run.resolve()
        if not run.is_relative_to(root / 'reproducibility'):
            raise ValueError('运行证据路径不在复现工程内')
        # 本轮未取整结果、输入锁定及诊断；不把编译缓存当科研数据。
        selected.update(p for p in run.rglob('*') if p.is_file()
                        and p.suffix.lower() in {'.csv', '.json', '.npz', '.md', '.txt', '.py'}
                        and 'workspace' not in p.relative_to(run).parts)
        # 发布后的汇集副本也交付；原隔离运行仍是计算来源，不把副本冒充新运行。
        collected = root / 'reproducibility/results' / run.name
        if collected.is_dir():
            selected.update(p for p in collected.rglob('*') if p.is_file()
                            and p.suffix.lower() in {'.csv', '.json', '.npz', '.md', '.txt'})
    selected.update(p for p in report.resolve().rglob('*')
                    if p.is_file() and p.suffix.lower() in {'.md', '.json', '.patch', '.log', '.txt'})
    missing = [str(p.relative_to(root)) for p in selected if not p.is_file()]
    if missing:
        raise FileNotFoundError(missing)
    output.mkdir(parents=True)
    manifest = []
    for source in sorted(selected):
        relative = source.relative_to(root)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if sha(source) != sha(target):
            raise RuntimeError('复制后哈希不一致：' + str(relative))
        manifest.append({'path': relative.as_posix(), 'sha256': sha(target),
                         'size': target.stat().st_size})
    record = {'version': version['version'], 'approved_tasks': version['approved_tasks'],
              'file_count': len(manifest), 'files': manifest,
              'fonts_or_environment_distributed': False,
              'excluded': 'AI讨论及线性/返回新探索不作为本轮新证据；原冻结来源整体保留。',
              'run_evidence': [str(p.resolve().relative_to(root)).replace('\\', '/') for p in runs]}
    (output / 'package_manifest.json').write_text(json.dumps(record, ensure_ascii=False, indent=2,
                                                          allow_nan=False)+'\n', encoding='utf-8')
    archive = output.with_suffix('.zip')
    if archive.exists():
        raise FileExistsError(archive)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(output.rglob('*')):
            if path.is_file():
                z.write(path, path.relative_to(output).as_posix())
    receipt = {'directory': str(output), 'zip': str(archive), 'zip_sha256': sha(archive),
               'file_count': len(manifest), 'copied_bytes_verified': True}
    receipt_path = output.with_name(output.name + '_archive_manifest.json')
    if receipt_path.exists():
        raise FileExistsError(receipt_path)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2,
                                      allow_nan=False) + '\n', encoding='utf-8')
    return {**receipt, 'archive_manifest': str(receipt_path)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--run', type=Path, action='append', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.root, args.out, args.run, args.report), ensure_ascii=False, indent=2))
