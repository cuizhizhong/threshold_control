"""保存本次文字分流前的工程文件及保护哈希，不运行科学计算。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
BACKUP = ROOT / 'reproducibility/backups/before_audit_separation_20261003'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    if BACKUP.exists() or (REPORT / 'baseline.json').exists():
        raise FileExistsError('备份或基线已存在，拒绝覆盖')
    backup_names = [
        'latex/flatten_curve_analysis_cn.tex', 'latex/flatten_curve_analysis_cn.pdf',
        'latex/flatten_curve_supplement_cn.tex', 'latex/flatten_curve_supplement_cn.pdf',
        'latex/flatten_curve_analysis_cn.aux', 'latex/flatten_curve_supplement_cn.aux',
        'latex/elegantpaper.cls', 'latex/references.bib', 'latex/build_paper.ps1',
        'reproducibility/paper_sync.py', 'reproducibility/README.md',
    ]
    BACKUP.mkdir(parents=True)
    for name in backup_names:
        destination = BACKUP / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode('utf-8').split('\0')
    files = {ROOT / name for name in tracked if name and (ROOT / name).is_file()}
    for directory in ('真实数据', 'refs', 'ai/threshold_control_reproducible_release_20261002',
                      'latex/figures', 'reproducibility/results', 'reproducibility/runs',
                      'reproducibility/release_reports', 'reproducibility/backups'):
        files.update(p for p in (ROOT / directory).rglob('*') if p.is_file()
                     and REPORT not in p.parents and BACKUP not in p.parents)
    records = [{'file': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
               for p in sorted(files)]
    baseline = {'protected_files': records, 'backup_files': backup_names,
                'allowed_existing_changes': [
                    'latex/flatten_curve_analysis_cn.tex', 'latex/flatten_curve_analysis_cn.pdf',
                    'latex/flatten_curve_supplement_cn.tex', 'latex/flatten_curve_supplement_cn.pdf',
                    'reproducibility/paper_sync.py', 'reproducibility/README.md'],
                'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
                'git_status_before': subprocess.check_output(['git', 'status', '--porcelain=v1', '-z'], cwd=ROOT).decode('utf-8'),
                'no_numerical_rerun': True, 'nature_skills_used': False,
                'backup': BACKUP.relative_to(ROOT).as_posix()}
    (REPORT / 'baseline.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'protected_count': len(records), 'backup_file_count': len(backup_names)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
