"""外生阈值新版的来源与静态保护；只读取文件，不生成稿件或执行科学计算。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from icu_revision_text import (
    PROTECTED_ENVIRONMENTS, _joint_blocks, _section, bibliography_entries,
    citation_keys, normalize,
)


BUNDLE_RELATIVE = Path("ai/icu")
BASE_VERSION = "20261005_icu_conditional_link"
VERSION = "20261006_threshold_exogenous"
BASE_COMMIT = "b338cc5d861354590f8a4d38894dd82507536bbb"
TRUSTED_HASH_MANIFEST = "0624c75e3a153320030471b15572a551f8a65609758df28afab3daf151132eb5"
APPROVED_HASHES = {
    "README_替换说明.md": "2b5723fb83a893f44afc979f28ef2cd1e26ad541d3d0cf611d034f8b71b13d8d",
    "latex/flatten_curve_analysis_cn.tex": "cfd174f05f7a0f3a92a12097eadee50b7712e066f34c8e15d6102f85f299343c",
    "latex/flatten_curve_supplement_cn.tex": "b048368f95155b5cea425e3acdeed75f0a110bb11ac0fea12709c29e15216ab5",
    "latex/build_paper.ps1": "0d34b4bc811642577eea11d826de866c119f761bafee4a0bd5f383abcd49907d",
    "review/compilation_checks.json": "c5b36c132707320013caa81b21da6e9b21223a4005a258e8117c95c44b4d82a5",
    "review/static_checks.json": "e61e697557fb23689ce7688994d208a753eb51b636c4e2323d1ba54cd3fbcd17",
    "review/flatten_curve_analysis_cn.tex.diff": "9c6d1d4a41dad49cc01ca171e4f8d6e9e9dc084ac42f827823c34d80218ae409",
    "review/flatten_curve_supplement_cn.tex.diff": "b5743450b38c23742635fffd1241c7461d0bbfe8c1e7c6d98b3e6312d502de15",
}
APPROVED_TEXT_HASHES = {
    "before_main": "f759c7b28e46097957b4a0187532ae2b0e161c23b41fa4f7ec2cdbbf85645770",
    "before_supplement": "fed25e262e191449086eb47034c1a46f65817c901e0d2dc5af655800f5a21d45",
    "after_main": "e36328bd06dbf69daffe7ba0afa80196225c151cc4c30ee3e1cb95e1c6ab5eb7",
    "after_supplement": "6bf66e7be3e3115dcec184c11ca5e87b1af4a343c3b00234d38d4977843bbe64",
}
BASE_GIT_BLOBS = {
    "main": "0fde6f4e6397ef2f6e2e94defba30a72247e6573",
    "supplement": "6d6a29d9dfa992cb50ae85c85e13b9f7c06ac28a",
}
SEC9_BEFORE = (
    r"本节的阈值仍是设计参数，不据此为各个有效人口推断 ICU 配置；在比例情景中固定 "
    r"$\theta$ 相当于固定人均资源与换算系数，不等于固定全市床位总量。"
)
SEC9_AFTER = "本节仍将感染阈值作为设计参数。"
SUPPLEMENT_NEW_LABELS = ["sec:sup:medical-link", "sec:sup:threshold-scale"]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text_sha(text: str) -> str:
    return _sha(normalize(text).encode("utf-8"))


def _safe_file(bundle: Path, relative: str) -> Path:
    original = bundle / relative
    resolved = original.resolve()
    if not resolved.is_relative_to(bundle.resolve()):
        raise ValueError(f"修订包路径异常: {relative}")
    for component in (original, *original.parents):
        if component == bundle.parent:
            break
        if component.is_symlink() or (hasattr(component, "is_junction") and component.is_junction()):
            raise ValueError(f"修订包路径包含链接: {relative}")
    if not resolved.is_file():
        raise ValueError(f"修订包文件缺失: {relative}")
    return resolved


def validate_source_bundle(root: Path) -> dict[str, Any]:
    """逐字节核对八份来源文件和清单本身，批准身份不由可编辑清单自行决定。"""
    bundle = Path(root).resolve() / BUNDLE_RELATIVE
    manifest_path = _safe_file(bundle, "review/SHA256.json")
    if _sha(manifest_path.read_bytes()) != TRUSTED_HASH_MANIFEST:
        raise ValueError("修订包哈希清单不是已批准来源")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest != APPROVED_HASHES:
        raise ValueError("修订包文件清单与批准来源不一致")
    paths = {}
    for relative, expected in APPROVED_HASHES.items():
        target = _safe_file(bundle, relative)
        if _sha(target.read_bytes()) != expected:
            raise ValueError(f"修订包文件哈希不符: {relative}")
        paths[relative] = str(target)
    record = json.loads(Path(paths["review/static_checks.json"]).read_text(encoding="utf-8-sig"))
    expected_source = {
        "commit": BASE_COMMIT,
        "main_git_blob_verified": BASE_GIT_BLOBS["main"],
        "supp_git_blob_verified": BASE_GIT_BLOBS["supplement"],
    }
    if record.get("source") != expected_source:
        raise ValueError("修订包基线提交或 Git blob 不符")
    return {
        "passed": True, "bundle": str(bundle.resolve()), "source_paths": paths,
        "source_hashes": dict(APPROVED_HASHES), "manifest_sha256": TRUSTED_HASH_MANIFEST,
        "base_version": BASE_VERSION, "version": VERSION, "source": expected_source,
        "scientific_calculation_reexecuted": False,
    }


def _environments(text: str, names: tuple[str, ...]) -> dict[str, list[str]]:
    return {
        name: re.findall(r"\\begin\{" + re.escape(name) + r"\}.*?\\end\{" +
                         re.escape(name) + r"\}", text, re.S)
        for name in names
    }


def _table_bodies(text: str) -> list[str]:
    pattern = r"\\begin\{(?P<kind>tabular|tabularx|tabular\*)\}.*?\\end\{(?P=kind)\}"
    return [match.group() for match in re.finditer(pattern, text, re.S)]


def assert_protected_unchanged(before_main: str, after_main: str,
                               before_supplement: str, after_supplement: str) -> dict[str, Any]:
    """只允许本轮已批准的完整稿件对；医学说明移动不放宽数学和第9节保护。"""
    old_main, new_main = normalize(before_main), normalize(after_main)
    old_si, new_si = normalize(before_supplement), normalize(after_supplement)
    names = tuple(name for name in PROTECTED_ENVIRONMENTS if name != "table")
    old_env, new_env = _environments(old_main, names), _environments(new_main, names)
    if old_env != new_env:
        raise ValueError("保护内容变化: 原编号公式、理论、证明或图环境")
    counts = {name: len(rows) for name, rows in old_env.items()}
    expected_counts = {"theorem": 9, "proposition": 12, "lemma": 1, "corollaryn": 5,
                       "remarkn": 1, "proof": 27, "equation": 91, "align": 7, "figure": 24}
    if any(counts[name] != count for name, count in expected_counts.items()):
        raise ValueError("保护内容数量与批准基线不符")
    main_tables, si_tables = _table_bodies(old_main), _table_bodies(old_si)
    if len(main_tables) != 5 or main_tables != _table_bodies(new_main):
        raise ValueError("保护内容变化: 正文表体")
    if len(si_tables) != 3 or si_tables != _table_bodies(new_si):
        raise ValueError("保护内容变化: 补充表体")
    labels = lambda text: re.findall(r"\\label\{([^}]+)\}", text)
    if labels(old_main) != labels(new_main):
        raise ValueError("保护内容变化: 正文标签及次序")
    if labels(new_si) != labels(old_si) + SUPPLEMENT_NEW_LABELS:
        raise ValueError("补充材料只能增加批准的两个标签")
    if len(labels(new_main) + labels(new_si)) != len(set(labels(new_main) + labels(new_si))):
        raise ValueError("正文与补充材料存在重复标签")
    if _section(old_main, "sec:joint:compare-numerics", "sec:xian") != _section(
            new_main, "sec:joint:compare-numerics", "sec:xian"):
        raise ValueError("保护内容变化: 第7节")
    old_joint, new_joint = _joint_blocks(old_main), _joint_blocks(new_main)
    if len(old_joint) != 6 or old_joint != new_joint:
        raise ValueError("保护内容变化: JOINT_EXTRA 块")
    old_sec9 = _section(old_main, "sec:dominance", "sec:discussion")
    new_sec9 = _section(new_main, "sec:dominance", "sec:discussion")
    if old_sec9.count(SEC9_BEFORE) != 1 or new_sec9.count(SEC9_AFTER) != 1:
        raise ValueError("第9节批准的原、新句须唯一")
    if old_sec9.replace(SEC9_BEFORE, SEC9_AFTER, 1) != new_sec9:
        raise ValueError("保护内容变化: 第9节仅允许批准的开头句变化")
    normalized_hashes = {
        "before_main": _text_sha(old_main), "after_main": _text_sha(new_main),
        "before_supplement": _text_sha(old_si), "after_supplement": _text_sha(new_si),
    }
    if normalized_hashes != APPROVED_TEXT_HASHES:
        raise ValueError("完整文案不是批准的基线与候选稿，不允许额外编辑")
    return {
        "passed": True, "counts": counts, "labels": len(labels(old_main)),
        "main_tables": len(main_tables), "supplement_tables": len(si_tables),
        "figure_environments_preserved": True, "section7_preserved": True,
        "joint_extra_preserved": True, "sec9_only_approved_intro_change": True,
        "sec9_before_sha256_lf": _text_sha(old_sec9),
        "sec9_after_sha256_lf": _text_sha(new_sec9),
        "sec9_before_sentence_sha256_lf": _text_sha(SEC9_BEFORE),
        "sec9_after_sentence_sha256_lf": _text_sha(SEC9_AFTER),
        "text_hashes_lf": normalized_hashes,
        "scientific_calculation_reexecuted": False,
    }


def assert_citations_resolved(main_text: str, supplement_text: str, bib_text: str) -> dict[str, Any]:
    """分别核查两份文档的引用；文献条目保留，不要求移出的引用仍在正文出现。"""
    entries = bibliography_entries(bib_text)
    result = {}
    for name, text in (("main", main_text), ("supplement", supplement_text)):
        keys = citation_keys(text)
        missing = keys - entries.keys()
        if missing:
            raise ValueError(f"{name} 引用键在文献库中缺失: " + ", ".join(sorted(missing)))
        if text.count(r"\printbibliography") != 1:
            raise ValueError(f"{name} 须各有一次参考文献输出")
        result[name] = {"citation_keys": sorted(keys), "missing_citations": [],
                        "bibliography_print_count": 1}
    return {"passed": True, "bibliography_entry_count": len(entries), "documents": result}
