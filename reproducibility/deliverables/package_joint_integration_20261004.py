"""扩充本轮新交付包的图源资产，不改已验收的计算或发布程序。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_joint_release import build, sha


def package(root: Path, output: Path, runs: list[Path], report: Path) -> dict:
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root / "reproducibility/deliverables") or output.exists():
        raise ValueError("只允许创建本项目deliverables中的全新交付目录")
    # 预先检查扩展来源；不能在原打包器已生成包后才发现外部链接。
    extra = sorted(p for p in (root / "reproducibility/assets").rglob("*") if p.is_file())
    extra.append(Path(__file__).resolve())
    for source in extra:
        if source.is_symlink() or not source.resolve().is_relative_to(root):
            raise ValueError("交付图源存在链接或越界：" + str(source))
    source_hashes = {source: sha(source) for source in extra}
    # 原入口保持原样；这里仅扩充打包选择，不参与科学计算与正式发布。
    receipt = build(root, output, runs, report)
    manifest_path = output / "package_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = {item["path"]: item for item in manifest["files"]}
    for source in extra:
        relative = source.relative_to(root)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        expected = source_hashes[source]
        if sha(source) != expected or sha(target) != expected:
            raise RuntimeError("包装扩选前后图源发生变化：" + str(relative))
        records[relative.as_posix()] = {
            "path": relative.as_posix(), "sha256": expected, "size": target.stat().st_size
        }
    manifest["files"] = [records[key] for key in sorted(records)]
    manifest["file_count"] = len(records)
    manifest["selection_extension"] = {
        "purpose": "保留完整流程图1及MATLAB绘图适配所需的本地图源资产",
        "paths": [p.relative_to(root).as_posix() for p in extra],
        "original_packager_changed": False,
        "scientific_or_publication_sources_changed": False,
        "wrapper_sha256": sha(Path(__file__)),
    }
    for item in manifest["files"]:
        if sha(output / item["path"]) != item["sha256"]:
            raise RuntimeError("最终包文件哈希失败：" + item["path"])
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2,
                                        allow_nan=False) + "\n", encoding="utf-8")
    archive = Path(receipt["zip"])
    if archive.resolve() != output.with_suffix(".zip"):
        raise ValueError("原入口返回的本次ZIP路径异常")
    # 只重建上面同一调用新生成的ZIP，不触碰任何历史包。
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(output.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(output).as_posix())
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad is not None:
            raise RuntimeError("ZIP CRC核查失败：" + bad)
    receipt.update({"file_count": len(records), "zip_sha256": sha(archive),
                    "selection_extension_applied": True, "zip_crc_check_passed": True,
                    "wrapper_sha256": sha(Path(__file__))})
    receipt_path = Path(receipt["archive_manifest"])
    if receipt_path.resolve() != output.with_name(output.name + "_archive_manifest.json"):
        raise ValueError("本次交付收据路径异常")
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2,
                                       allow_nan=False) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.root, args.out, args.run, args.report),
                     ensure_ascii=False, indent=2))
