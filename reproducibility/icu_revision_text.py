"""条件性 ICU 文案的严格局部合并与保护检查；本模块不写文件、不运行科学计算。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


BUNDLE_RELATIVE = Path("ai/icu_conditional_link_codex_20261005")
TRUSTED_HASH_MANIFEST = "4ba99ab212a653c0d996f5019b85436ea248706aee5f944cb44cbdc380a44ee5"
BAAS_KEY = "Baas2021Occupancy"
BAAS_DOI = "10.1007/s10729-021-09553-5"
PROTECTED_ENVIRONMENTS = (
    "equation", "align", "gather", "multline", "theorem", "lemma",
    "proposition", "corollaryn", "remarkn", "proof", "figure", "table",
)
SCALING_BEFORE = (
    r"采用第\ref{sec:model:strategy}节的比例设定时，固定人均可用容量 $C/N$ 和 "
    r"$\rho_{\mathrm{ICU}}$ 对应固定 $\theta$；固定床位总量 $C$ 后改变人口，"
    r"则一般不保持同一 $\theta$。"
)
SCALING_AFTER = (
    r"仅就第\ref{sec:xian:threshold-scale}节的比例参考情景而言，固定人均名义容量 $C/N$ 和 "
    r"$\rho_{\mathrm{ICU}}$ 对应固定 $\theta$；固定名义床位总量 $C$ 后改变人口，"
    r"则一般不保持同一 $\theta$。"
)
INTRO_BEFORE = "医疗资源相关的比例情景只说明阈值量级，感染下界则用于解释城市人口规模下规定退出目标的代价。"
INTRO_AFTER = (
    r"数值比较采用给定设计阈值，未按第\ref{sec:model:strategy}节的医疗需求充分条件校准；"
    "感染下界用于解释城市人口规模下规定退出目标的代价。"
)
INITIAL_BEFORE = (
    r"记初始病例在此后产生的平均需求为 $D_0(t)$，并假定对所比较策略均有 "
    r"$0\le D_0(t)\le D_{\mathrm{init}}<\infty$。该项包括初始时刻已经感染但以后才需要 ICU "
    "的病例，不能仅用初始在床人数代替。"
)
INITIAL_AFTER = (
    r"记初始时刻之前已经感染者在此后产生的平均需求为 $D_0(t)$，并假定对所比较策略均有 "
    r"$0\le D_0(t)\le D_{\mathrm{init}}<\infty$。该项包括以后才需要 ICU 的病例及其后续占用，"
    r"不限于初始 $I$、$I_q$ 仓室或初始在床者；即使已从传播模型移出，仍可能产生医疗需求。"
    r"因此，$D_{\mathrm{init}}$ 是共同的未来需求上界，不能仅用初始在床人数代替。"
)
CAPACITY_BEFORE = (
    r"设 $C>D_{\mathrm{init}}$ 为扣除其他病种占用和安全预留后可用于本病的容量，其中本病初始病例的"
    r"负担由 $D_{\mathrm{init}}$ 单独计入、不重复扣除。"
)
CAPACITY_AFTER = (
    r"设 $C>D_{\mathrm{init}}$ 为全过程固定的本病可用容量，已扣除其他病种占用和安全预留；"
    r"本病初始病例的未来负担由 $D_{\mathrm{init}}$ 单独计入，不再从 $C$ 重复扣除。"
)


def normalize(text: str) -> str:
    """只规范化 BOM 和换行，不压缩正文空白。"""
    return text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text_sha(text: str) -> str:
    return _sha(normalize(text).encode("utf-8"))


def _verified_bundle(root: Path) -> tuple[Path, dict[str, Any], dict[str, str]]:
    """核对只读来源的完整字节；不把更改过的清单视为新的批准来源。"""
    bundle = root.resolve() / BUNDLE_RELATIVE
    hash_path = bundle / "MANIFEST_SHA256.json"
    if not hash_path.is_file() or _sha(hash_path.read_bytes()) != TRUSTED_HASH_MANIFEST:
        raise ValueError("修订包哈希清单不是已批准来源")
    hashes = json.loads(hash_path.read_text(encoding="utf-8-sig"))["files"]
    for relative, expected in hashes.items():
        target = (bundle / relative).resolve()
        if not target.is_relative_to(bundle.resolve()) or target.is_symlink():
            raise ValueError(f"修订包路径异常: {relative}")
        if not target.is_file() or _sha(target.read_bytes()) != expected:
            raise ValueError(f"修订包文件哈希不符: {relative}")
    manifest = json.loads((bundle / "merge_manifest.json").read_text(encoding="utf-8-sig"))
    expected_ids = [f"{index:02d}_" for index in range(8)]
    operations = manifest.get("operations", [])
    if len(operations) != 8 or any(not row["id"].startswith(prefix)
                                  for row, prefix in zip(operations, expected_ids)):
        raise ValueError("修订包必须包含批准顺序的八个锚点")
    return bundle, manifest, hashes


def _replace_unique(text: str, before: str, after: str, name: str) -> str:
    count = text.count(before)
    if count != 1:
        raise ValueError(f"替换锚点须唯一: {name}; matches={count}")
    return text.replace(before, after, 1)


def citation_keys(text: str) -> set[str]:
    pattern = r"\\(?:cite|citep|citet|autocite|parencite|textcite|nocite)\*?(?:\[[^\]]*\])*\{([^}]+)\}"
    return {key.strip() for group in re.findall(pattern, text) for key in group.split(",") if key.strip()}


def bibliography_entries(bib_text: str) -> dict[str, str]:
    """按平衡花括号保留每条原文，拒绝重复键和不能完整解析的条目。"""
    text = normalize(bib_text)
    entries: dict[str, str] = {}
    starts = list(re.finditer(r"(?mi)^\s*@([A-Za-z]+)\s*\{", text))
    for index, match in enumerate(starts):
        kind = match.group(1).lower()
        if kind in {"comment", "preamble", "string"}:
            continue
        opening = text.index("{", match.start(), match.end())
        comma = text.find(",", opening + 1)
        if comma < 0:
            raise ValueError("参考文献条目缺少引用键")
        key = text[opening + 1:comma].strip()
        if not re.fullmatch(r"[^\s{},]+", key):
            raise ValueError("参考文献引用键格式异常")
        depth = 1
        position = opening + 1
        while depth and position < len(text):
            character = text[position]
            backslashes = 0
            previous = position - 1
            while previous >= 0 and text[previous] == "\\":
                backslashes += 1
                previous -= 1
            if backslashes % 2 == 0:
                depth += (character == "{") - (character == "}")
            position += 1
        if depth or (index + 1 < len(starts) and position > starts[index + 1].start()):
            raise ValueError(f"参考文献花括号未闭合: {key}")
        if key in entries:
            raise ValueError(f"重复参考文献键: {key}")
        entries[key] = text[match.start():position].lstrip()
    return entries


def _doi(entry: str) -> str | None:
    match = re.search(r"\bdoi\s*=\s*(?:\{([^}]+)\}|\"([^\"]+)\")", entry, re.I)
    if not match:
        return None
    value = (match.group(1) or match.group(2)).strip().lower()
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)


def assert_bibliography_preserved(before_bib: str, after_bib: str) -> dict[str, Any]:
    before, after = bibliography_entries(before_bib), bibliography_entries(after_bib)
    for key, original in before.items():
        if key not in after or after[key] != original:
            raise ValueError(f"原参考文献条目变化或遗漏: {key}")
    doi_keys: dict[str, list[str]] = {}
    for key, entry in after.items():
        if (doi := _doi(entry)):
            doi_keys.setdefault(doi, []).append(key)
    duplicates = {doi: keys for doi, keys in doi_keys.items() if len(keys) > 1}
    if duplicates:
        raise ValueError(f"重复 DOI: {duplicates}")
    added = sorted(after.keys() - before.keys())
    if len(added) > 1 or any(_doi(after[key]) != BAAS_DOI for key in added):
        raise ValueError("只允许增加一条 Baas DOI 文献")
    baas = doi_keys.get(BAAS_DOI, [])
    if len(baas) != 1:
        raise ValueError("Baas DOI 必须恰有一条")
    return {"old_entries_preserved": True, "old_entry_count": len(before),
            "new_entry_count": len(after), "added_keys": added, "baas_key": baas[0]}


def _section(text: str, start_label: str, end_label: str) -> str:
    start_marker, end_marker = (r"\label{" + key + "}" for key in (start_label, end_label))
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        raise ValueError("保护小节标签须唯一")
    start = text.rfind(r"\section", 0, text.index(start_marker))
    end = text.rfind(r"\section", 0, text.index(end_marker))
    if start < 0 or end <= start:
        raise ValueError("保护小节边界次序错误")
    return text[start:end]


def _joint_blocks(text: str) -> list[tuple[str, str]]:
    begins = re.findall(r"(?m)^% BEGIN JOINT_EXTRA:([^\r\n]+)$", text)
    ends = re.findall(r"(?m)^% END JOINT_EXTRA:([^\r\n]+)$", text)
    if len(begins) != len(set(begins)) or begins != ends:
        raise ValueError("JOINT_EXTRA 保护锚点缺失、重复或次序错误")
    result = []
    for name in begins:
        begin = "% BEGIN JOINT_EXTRA:" + name
        end = "% END JOINT_EXTRA:" + name
        left, right = text.index(begin), text.index(end)
        if right <= left:
            raise ValueError("JOINT_EXTRA 保护锚点次序错误")
        result.append((name, text[left:right + len(end)]))
    return result


def protected_payload(main_text: str, supplement_text: str = "") -> dict[str, Any]:
    """提取不能随本轮文案调整改变的原数学、表图和局部结论。"""
    main, supplement = normalize(main_text), normalize(supplement_text)
    # 分开逐环境匹配，避免 theorem 内部的 equation 被外层匹配吞掉。
    environments = {
        name: re.findall(r"\\begin\{" + re.escape(name) + r"\}.*?\\end\{" +
                         re.escape(name) + r"\}", main, re.S)
        for name in PROTECTED_ENVIRONMENTS
    }
    return {
        "environments": environments,
        "labels": re.findall(r"\\label\{([^}]+)\}", main),
        "headings": re.findall(r"\\(?:section|subsection|subsubsection|paragraph)\*?\{[^\n]*", main),
        "sec9": _section(main, "sec:dominance", "sec:discussion"),
        "joint_extra": _joint_blocks(main),
        "supplement": supplement,
        "supplement_tables": re.findall(r"\\begin\{table\}.*?\\end\{table\}", supplement, re.S),
    }


def assert_protected_unchanged(before_main: str, after_main: str,
                               before_supplement: str = "", after_supplement: str = "") -> dict[str, Any]:
    lost = citation_keys(before_main) - citation_keys(after_main)
    if lost:
        raise ValueError("遗漏旧引用键: " + ", ".join(sorted(lost)))
    before = protected_payload(before_main, before_supplement)
    after = protected_payload(after_main, after_supplement)
    changed = [key for key in before if before[key] != after[key]]
    if changed:
        raise ValueError("保护内容变化: " + ", ".join(changed))
    return {"passed": True, "counts": {key: len(rows) for key, rows in before["environments"].items()},
            "labels": len(before["labels"]), "supplement_tables": len(before["supplement_tables"]),
            "old_citation_keys_preserved": True, "sec9_preserved": True,
            "joint_extra_preserved": True, "supplement_unchanged": True}


def candidate_texts(root: Path, main_text: str, bib_text: str) -> tuple[str, str, dict[str, Any]]:
    """生成批准块及局部澄清；返回文本与记录，不写源稿、版本或报告。"""
    bundle, manifest, hashes = _verified_bundle(Path(root))
    source = normalize(main_text)
    candidate = source
    operations = []
    prepared = []
    for row in manifest["operations"]:
        before = normalize((bundle / row["before_file"]).read_text(encoding="utf-8-sig")).strip()
        after = normalize((bundle / row["after_file"]).read_text(encoding="utf-8-sig")).strip()
        if _text_sha(before) != row["before_sha256_lf"]:
            raise ValueError(f"原块 LF 哈希不符: {row['id']}")
        count = source.count(before)
        if count != 1:
            raise ValueError(f"替换锚点须唯一: {row['id']}; matches={count}")
        if source.count(after):
            raise ValueError(f"源稿混入已合并块: {row['id']}")
        prepared.append((row, before, after))
    for row, before, after in prepared:
        candidate = _replace_unique(candidate, before, after, row["id"])
        operations.append({"id": row["id"], "section": row["section"], "matches": 1,
                           "before_sha256_lf": row["before_sha256_lf"],
                           "after_source_sha256": hashes[row["after_file"]]})
    extra = (
        ("initial_future_burden", INITIAL_BEFORE, INITIAL_AFTER),
        ("fixed_disease_capacity", CAPACITY_BEFORE, CAPACITY_AFTER),
        ("scaling_reference", SCALING_BEFORE, SCALING_AFTER),
        ("introduction_design_threshold", INTRO_BEFORE, INTRO_AFTER),
    )
    for name, before, after in extra:
        candidate = _replace_unique(candidate, before, after, name)
        operations.append({"id": name, "matches": 1, "before_sha256_lf": _text_sha(before),
                           "after_sha256_lf": _text_sha(after)})

    original_entries = bibliography_entries(bib_text)
    same_doi = [key for key, entry in original_entries.items() if _doi(entry) == BAAS_DOI]
    if len(same_doi) > 1:
        raise ValueError("重复 DOI: " + BAAS_DOI)
    if same_doi:
        key = same_doi[0]
        updated_bib = bib_text
        if key != BAAS_KEY:
            candidate = _replace_unique(candidate, r"\cite{" + BAAS_KEY + "}", r"\cite{" + key + "}", "Baas citation key")
    else:
        if BAAS_KEY in original_entries:
            raise ValueError("Baas 引用键已用于不同 DOI")
        addition = (bundle / manifest["bib_addition"]["path"]).read_text(encoding="utf-8-sig")
        newline = "\r\n" if "\r\n" in bib_text else "\n"
        updated_bib = bib_text + ("" if bib_text.endswith(("\n", "\r")) else newline) + newline
        updated_bib += normalize(addition).replace("\n", newline)
        key = BAAS_KEY
    bibliography = assert_bibliography_preserved(bib_text, updated_bib)
    preservation = assert_protected_unchanged(source, candidate)
    extra_keys = citation_keys(candidate) - citation_keys(source)
    if extra_keys - {key}:
        raise ValueError("产生未批准的新引用键")
    if citation_keys(candidate) - bibliography_entries(updated_bib).keys():
        raise ValueError("候选稿引用键在文献库中缺失")
    report = {
        "passed": True, "operation": "approved conditional ICU prose merge only",
        "scientific_calculation_reexecuted": False,
        "source_text_sha256_lf": _text_sha(source), "candidate_text_sha256_lf": _text_sha(candidate),
        "bibliography_before_sha256": _sha(bib_text.encode("utf-8")),
        "bibliography_after_sha256": _sha(updated_bib.encode("utf-8")),
        "bundle_hash_manifest_sha256": TRUSTED_HASH_MANIFEST,
        "operations": operations, "preservation": preservation, "bibliography": bibliography,
        "clinical_calibration_performed": False,
    }
    # 与输入保持相同换行和 BOM；调用者自行决定候选落盘位置。
    if "\r\n" in main_text:
        candidate = candidate.replace("\n", "\r\n")
    if main_text.startswith("\ufeff"):
        candidate = "\ufeff" + candidate
    return candidate, updated_bib, report
