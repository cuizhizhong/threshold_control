#!/usr/bin/env python3
"""只读检查：列出改写前后发生变化的定理类陈述与证明，供作者逐条确认数学内容是否等价。

用法（在仓库根目录运行）：
  python paper/tools/statement_diff.py --old <旧稿 tex，可多个> --new <新稿 tex，可多个> [--out 报告.md]

例：与重写前的标签比较整篇主稿
  git show pre-rewrite-20261007:paper/sections/03_single_control.tex > 旧3.tex
  python paper/tools/statement_diff.py --old 旧3.tex --new paper/sections/03_single_control.tex

按 \\label 配对 theorem/proposition/lemma/corollary(n)/definition/remark(n) 环境；
证明按其前面最近的带标签陈述配对。比较时忽略空白差异。输出：
  - 未变化的陈述数；
  - 发生变化的陈述及其逐行差异（证明只报告是否变化及字数变化，避免报告过长；加 --proofs 显示差异）；
  - 只在旧稿或只在新稿中出现的标签。
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

ENVS = ["theorem", "proposition", "lemma", "corollary", "corollaryn", "definition", "remark",
        "remarkn", "assumption"]


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig")


def expand(path: Path, seen=None) -> str:
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)
    text = "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in read(path).splitlines())

    def repl(m):
        cand = path.parent / m.group(2).strip()
        for c in (cand, cand.with_suffix(".tex")):
            if c.is_file():
                return expand(c, seen)
        return m.group(0)

    return re.sub(r"\\(input|include)\{([^}]*)\}", repl, text)


def _git_show(rev: str, path: str):
    import subprocess
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8-sig") if r.returncode == 0 else None


def _expand_git(rev: str, path: str, seen: set) -> str:
    import posixpath
    if path in seen:
        return ""
    seen.add(path)
    text = _git_show(rev, path)
    if text is None:
        raise SystemExit(f"git 中找不到 {rev}:{path}")
    text = "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in text.splitlines())
    base = posixpath.dirname(path)

    def repl(m):
        cand = posixpath.normpath(posixpath.join(base, m.group(2).strip()))
        for c in (cand, cand + ".tex"):
            if _git_show(rev, c) is not None:
                return _expand_git(rev, c, seen)
        return m.group(0)

    return re.sub(r"\\(input|include)\{([^}]*)\}", repl, text)


def expand_spec(spec: str) -> str:
    """读入一个稿件来源：磁盘上的 tex 文件，或“版本:路径”形式的 git 版本
    （例如 pre-rewrite-20261007:paper/sections/06_numerics.tex，路径相对仓库根目录，须在仓库根目录运行）。
    两种情况都会递归展开 \\input / \\include。"""
    p = Path(spec)
    if p.is_file():
        return expand(p)
    if ":" in spec:
        rev, path = spec.split(":", 1)
        return _expand_git(rev, path.replace("\\", "/"), set())
    raise SystemExit(f"找不到文件：{spec}")


def collect(text: str) -> tuple[dict[str, str], dict[str, str]]:
    stmts, proofs = {}, {}
    pat = re.compile(r"\\begin\{(" + "|".join(ENVS) + r"|proof)\}(.*?)\\end\{\1\}", re.S)
    last = None
    for m in pat.finditer(text):
        env, content = m.group(1), m.group(2)
        if env == "proof":
            if last and last not in proofs:
                proofs[last] = content
            continue
        labels = re.findall(r"\\label\{([^}]*)\}", content)
        if labels:
            key = labels[0]
            stmts[key] = content
            last = key
    return stmts, proofs


def norm(s: str) -> str:
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    return re.sub(r"\s+", "", s)


def lines(s: str) -> list[str]:
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    out = []
    for ln in s.splitlines():
        ln = ln.strip()
        if ln:
            out += [x for x in re.split(r"(?<=[。；：])", ln) if x]
    return out


def cjk(s: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", nargs="+", required=True)
    ap.add_argument("--new", nargs="+", required=True)
    ap.add_argument("--out")
    ap.add_argument("--proofs", action="store_true", help="同时显示证明的逐行差异")
    a = ap.parse_args()
    os_, op = collect("\n".join(expand_spec(p) for p in a.old))
    ns, np_ = collect("\n".join(expand_spec(p) for p in a.new))

    L = ["# 定理类陈述与证明的变化", "", f"- 旧稿：{' '.join(a.old)}", f"- 新稿：{' '.join(a.new)}", ""]
    common = [k for k in os_ if k in ns]
    changed = [k for k in common if norm(os_[k]) != norm(ns[k])]
    L += [f"带标签的陈述：旧稿 {len(os_)} 条，新稿 {len(ns)} 条；共同 {len(common)} 条，"
          f"其中未变化 {len(common) - len(changed)} 条，有变化 {len(changed)} 条。", ""]
    only_old = [k for k in os_ if k not in ns]
    only_new = [k for k in ns if k not in os_]
    if only_old:
        L += ["只在旧稿中（新稿中找不到该标签的陈述，需说明去向）：" + "、".join(only_old), ""]
    if only_new:
        L += ["只在新稿中（新增或改了首个标签）：" + "、".join(only_new), ""]

    if changed:
        L += ["## 陈述有变化（逐条确认数学含义是否等价）", ""]
        for k in changed:
            L += [f"### {k}", "", "```diff"]
            L += [d for d in difflib.unified_diff(lines(os_[k]), lines(ns[k]), "旧", "新", n=0, lineterm="")
                  if not d.startswith(("---", "+++"))]
            L += ["```", ""]

    pc = [k for k in op if k in np_ and norm(op[k]) != norm(np_[k])]
    L += ["## 证明", "", f"有证明的陈述：旧稿 {len(op)} 条，新稿 {len(np_)} 条；证明有变化 {len(pc)} 条。", ""]
    lost = [k for k in op if k not in np_]
    if lost:
        L += ["旧稿有证明、新稿中未在其后找到证明（可能移至附录，需说明）：" + "、".join(lost), ""]
    for k in pc:
        L.append(f"- {k}：汉字 {cjk(op[k])} → {cjk(np_[k])}")
        if a.proofs:
            L += ["", "```diff"]
            L += [d for d in difflib.unified_diff(lines(op[k]), lines(np_[k]), "旧", "新", n=0, lineterm="")
                  if not d.startswith(("---", "+++"))]
            L += ["```", ""]
    L.append("")

    rep = "\n".join(L)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(rep, encoding="utf-8")
        print(f"陈述有变化 {len(changed)} 条，证明有变化 {len(pc)} 条；报告：{a.out}")
    else:
        print(rep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
