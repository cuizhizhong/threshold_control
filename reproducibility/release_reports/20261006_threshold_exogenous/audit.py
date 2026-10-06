"""本轮最终只继承科学证据的核查与交付收集，不执行计算或绘图入口。"""
from pathlib import Path
import difflib
import json
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bootstrap import ROOT, dump, sha
from document_revision import MAIN, SUPPLEMENT, SOURCE_NAMES, read
from manuscript_version import CURRENT_POINTER, load_version, version_texts
from paper_sync import prepare_manuscript
from threshold_revision import check_revision, normalized, VERSION_ID

output = Path(__file__).resolve().parent
review = output / 'review'
if (output / 'final_state.json').exists():
    raise FileExistsError('已有最终核查清单，不覆盖')
record, version = check_revision(ROOT, review)
publication = read(review / 'publication.json')
if publication.get('passed') is not True or publication.get('scientific_calculation_reexecuted') is not False:
    raise RuntimeError('正式发布未通过或科学身份不符')
current = load_version(ROOT, required=True)
if current['version'] != VERSION_ID or sha(current['_directory'] / 'manifest.json') != record['manifest_sha256']:
    raise RuntimeError('活动版本不是本轮已验收来源')
main, si = version_texts(current)
generated, generated_si, regression = prepare_manuscript(ROOT, review / 'generation_active_pointer',
    scientific_reference=ROOT / current['inherited_science_reference'],
    joint_extra_directory=Path(record['inheritance']['joint_extra_directory']),
    inherited_joint_publication=record['inheritance'])
if normalized(generated) != normalized(main) or normalized(generated_si) != normalized(si):
    raise RuntimeError('默认活动指针生成回归恢复旧内容')
if regression.get('scientific_calculation_reexecuted') is not False:
    raise RuntimeError('默认生成回归冒充科学运行')
formal_hashes = {name: sha(ROOT / 'latex' / name) for name in SOURCE_NAMES + (MAIN + '.pdf', SUPPLEMENT + '.pdf')}
for name in SOURCE_NAMES:
    if formal_hashes[name] != record['candidate_sha256'][name]:
        raise RuntimeError('最终正式源文件不是批准候选：' + name)
with (output / 'postpublication_tests.log').open('w', encoding='utf-8') as log:
    tested = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'reproducibility/tests', '-v'],
        cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=180)
if tested.returncode:
    raise RuntimeError('发布后的接口回归失败')
test_log = (output / 'postpublication_tests.log').read_text(encoding='utf-8')
count = int(re.search(r'Ran (\d+) tests', test_log).group(1))
changed_sources = ['AGENTS.md', 'README.md', 'reproducibility/README.md', 'reproducibility/bootstrap.py',
    'reproducibility/build.py', 'reproducibility/manuscript_version.py', 'reproducibility/run_all.py',
    'reproducibility/postprocess_joint_extra.py', 'reproducibility/threshold_revision.py',
    'reproducibility/threshold_revision_text.py', 'reproducibility/tests/test_bootstrap_version_assets.py',
    'reproducibility/tests/test_build_bibliography.py', 'reproducibility/tests/test_manuscript_version.py',
    'reproducibility/tests/test_threshold_revision.py', 'reproducibility/tests/test_threshold_revision_text.py']
collection = []
for relative in changed_sources:
    path = ROOT / relative
    saved = output / 'implementation_source' / relative
    saved.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, saved)
    collection.append({'source': relative, 'file': saved.relative_to(ROOT).as_posix(), 'sha256': sha(saved)})
with (output / 'implementation.diff').open('w', encoding='utf-8') as diff:
    for relative in changed_sources:
        old = subprocess.run(['git', 'show', 'b338cc5:' + relative], cwd=ROOT, capture_output=True)
        prior = old.stdout.decode('utf-8-sig') if old.returncode == 0 else ''
        new = (ROOT / relative).read_text(encoding='utf-8-sig')
        diff.write(''.join(difflib.unified_diff(prior.splitlines(keepends=True), new.splitlines(keepends=True),
                   fromfile='baseline/' + relative, tofile='current/' + relative)))
build = read(review / 'document/build_report.json')
documents = {stem: {'page_count': info['page_count'], 'final_pdf_sha256': formal_hashes[stem + '.pdf'],
    'reviewed_pdf_sha256': info['pdf_sha256'], 'formal_render_and_text_identical': publication['documents'][stem]['passed'],
    'printed_references': len(build['bibliographies'][stem]['printed_bibliography_keys'])}
    for stem, info in build['documents'].items()}
final = {'passed': True, 'version': VERSION_ID, 'manifest_sha256': record['manifest_sha256'],
    'baseline_commit': 'b338cc5d861354590f8a4d38894dd82507536bbb',
    'baseline_archive_sha256': sha(output / 'baseline_b338cc5.zip'),
    'formal_files_sha256': formal_hashes, 'documents': documents,
    'protected_files_checked': len(record['protected_files_sha256']), 'protected_files_sha256_unchanged': True,
    'scientific_calculation_reexecuted': False, 'default_active_pointer_regression_passed': True,
    'document_interface_tests': {'passed': True, 'count': count, 'log_sha256': sha(output / 'postpublication_tests.log')},
    'implementation_files': collection, 'implementation_diff_sha256': sha(output / 'implementation.diff'),
    'page_review_sha256': sha(review / 'manual_review.json'), 'publication_sha256': sha(review / 'publication.json'),
    'git_writes': False, 'clinical_calibration': False,
    'unexecuted': ['A–D重新计算', '西安重新拟合及TDINN积分', '旧MATLAB实验', '临床校准',
                  '图中案例标记绑定与连续人口允许区间核查']}
dump(output / 'final_state.json', final)
print(json.dumps({'passed': True, 'tests': count, 'protected_files': final['protected_files_checked'],
                  'documents': documents, 'scientific_calculation_reexecuted': False}, ensure_ascii=False))
