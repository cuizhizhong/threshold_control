"""固定本地JSON导入18条回流结果；校验字节，有历史时额外核对Git，不重跑ODE。"""
import argparse
import hashlib
import json
import math
import pathlib
import subprocess
from audit_common import ROOT, dump

SOURCE_BRANCH = 'research/return-effects'
SOURCE_COMMIT = 'bb52b965a8cd98dd07a5c41b9997dae433128756'
ARCHIVED_COMMIT = '9887340091911eda76753c1d2cc2afa23430cc62'
SOURCE_PATH = 'r7_return/results/r7_3_exponential_return.json'
SOURCE_BLOB = '582def57c4a957e242d884dff50d6c8937e9137a'
SOURCE_SHA256 = '3ca0a3d245314230df83c0717e07ed73ab67129803c284ea46eab8921cdfb05f'
STAYS = (7, 14, 30)
LAWS = ('q_only', 'opt_noreturn', 'c_only')
KEYS = ('status', 'dt', 'J', 'C_term', 'L', 'crossing', 't_end', 'termination',
        'C_term_below_L', 'U_below_Sc_at_end')


def read_source(path, repository=None):
    """缺失、字节损坏或语义不符均失败；历史不可用只影响额外历史核对。"""
    path = pathlib.Path(path)
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != SOURCE_SHA256:
        raise ValueError(f'固定回流输入SHA-256不符: {path}: {sha}')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if blob != SOURCE_BLOB:
        raise ValueError(f'固定回流输入blob不符: {blob}')
    history = 'not_available'
    repository = pathlib.Path(repository) if repository is not None else ROOT
    if (repository / '.git').exists():
        try:
            known = subprocess.run(['git', 'cat-file', '-e', SOURCE_COMMIT],
                                   cwd=repository, capture_output=True)
            if known.returncode == 0:
                historical = subprocess.check_output(
                    ['git', 'show', f'{SOURCE_COMMIT}:{SOURCE_PATH}'], cwd=repository)
                if historical != raw:
                    raise ValueError('历史blob与固定本地输入不一致')
                history = 'matched'
        except FileNotFoundError:
            history = 'git_unavailable'
    data = json.loads(raw.decode('utf-8'))
    if (data['model'], data['endpoint'], data['weights']) != (
            'exponential_return', 'first_below_one', {'w_c': 1.0, 'w_q': 2.0}):
        raise ValueError('回流输入模型、终点或权重不符')
    for case in ('base', 'xian'):
        for stay in STAYS:
            for law in LAWS:
                key = f'{case}|{stay}|{law}'
                row = data['runs'][key]
                if row['status'] != 'ok' or row['termination'] != 'first_below_one' or not row['reached']:
                    raise ValueError(f'回流轨迹未成功到达指定终点: {key}')
                for field in ('dt', 'J', 'C_term', 'L', 't_end'):
                    if not math.isfinite(row[field]):
                        raise ValueError(f'回流字段非有限: {key}.{field}')
    return data, dict(sha256=sha, blob=blob, history_check=history)


def build_import(path=None, repository=None):
    path = pathlib.Path(path) if path is not None else ROOT / SOURCE_PATH
    data, identity = read_source(path, repository)
    runs = {f'{case}|{stay}|{law}': {
        k: data['runs'][f'{case}|{stay}|{law}'][k] for k in KEYS}
        for case in ('base', 'xian') for stay in STAYS for law in LAWS}
    try:
        actual_input = path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        actual_input = str(path.resolve())
    out = dict(
        description='NEW-1：自固定本地JSON导入18条指数回流结果，不重算；终点为退出后首次向下I=1。',
        source=dict(branch=SOURCE_BRANCH, commit=SOURCE_COMMIT, archived_commit=ARCHIVED_COMMIT,
                    path=SOURCE_PATH, input_file=actual_input, **identity,
                    acceptance='来源G2于2026-10-15通过，NR-7 G-N3于2026-10-16接收',
                    use='固定参数、初值、控制律与首次I=1终点；无Git快照仅历史核对未执行'),
        runs=runs,
        all_not_crossed=all(r['crossing'] == 'not_crossed' for r in runs.values()),
        all_above_L=all(not r['C_term_below_L'] for r in runs.values()))
    if not out['all_not_crossed'] or not out['all_above_L']:
        raise ValueError('18条固定轨迹的已接收判定不符')
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-json', type=pathlib.Path, default=ROOT / SOURCE_PATH)
    parser.add_argument('--output-json', type=pathlib.Path)
    args = parser.parse_args(argv)
    out = build_import(args.source_json)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    else:
        dump('return_import.json', out)
    print(f"导入{len(out['runs'])}条；SHA-256正确；历史核对: {out['source']['history_check']}")


if __name__ == '__main__':
    main()
