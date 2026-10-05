"""冻结交付包、原始输入及运行源码版本核查。"""
from __future__ import annotations
import json
from pathlib import Path
from bootstrap import dump, sha


def run(root: Path, output: Path) -> dict:
    release=root/'joint_control/threshold_control_reproducible_release_20261002'
    manifest=json.loads((release/'MANIFEST_SHA256.json').read_text(encoding='utf-8'))
    frozen=[]
    for rel,expected in manifest['files'].items():
        source=release/rel
        actual=sha(source) if source.is_file() else None
        frozen.append({'file':rel,'expected_sha256':expected['sha256'],
                       'actual_sha256':actual,'passed':actual==expected['sha256']})
    runner={str(p.relative_to(root)).replace('\\','/'):sha(p)
            for p in (root/'reproducibility').iterdir()
            if p.is_file() and p.suffix in {'.py','.m','.ps1','.txt'}}
    for relative in ('reproducibility/joint_extra','reproducibility/manuscript_versions','reproducibility/tests'):
        runner.update({p.relative_to(root).as_posix():sha(p) for p in (root/relative).rglob('*')
                       if p.is_file() and '__pycache__' not in p.parts and
                       p.suffix.lower() in {'.py','.json','.md','.tex'}})
    assets={str(p.relative_to(root)).replace('\\','/'):sha(p)
            for p in (root/'reproducibility/assets').rglob('*') if p.is_file()}
    original={'真实数据/Xianguankong.xlsx':sha(root/'真实数据/Xianguankong.xlsx')}
    source_manifest=json.loads((output/'source_manifest.json').read_text(encoding='utf-8'))
    originals={rel:sha(root/rel) if (root/rel).is_file() else None
               for rel in source_manifest['source_files']}
    original_failures=[rel for rel,current in originals.items()
                       if current!=source_manifest['source_files'][rel]]
    report={'passed':all(r['passed'] for r in frozen) and not original_failures,'frozen_release':frozen,
            'runner_source_hashes':runner,'static_art_assets':assets,'raw_inputs':original,
            'source_input_hashes':originals,'changed_original_sources':original_failures,
            'frozen_manifest_sha256':sha(release/'MANIFEST_SHA256.json'),
            'limitations':'版本/输入一致性核查，不认证代码正确性或数学证明。'}
    dump(output/'validation/source_integrity.json',report)
    if not report['passed']:raise RuntimeError('冻结交付包发生变化，停止正式复现。')
    return report


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();run(Path(__file__).resolve().parents[1],args.output)
