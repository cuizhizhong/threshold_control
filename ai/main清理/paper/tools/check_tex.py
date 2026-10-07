#!/usr/bin/env python3
"""只读检查：比较修改前后的 LaTeX 稿件，不修改任何文件。

用法（在仓库根目录运行）：
  python paper/tools/check_tex.py \
      --old paper/revision_notes/baseline_main.tex paper/revision_notes/baseline_supplement.tex \
      --new paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex \
      --bib paper/references.bib --out paper/revision_notes/check_report.md

  --old / --new 各给一组文件（主稿与补充材料）；文件中的 \\input / \\include 会被递归展开。
  可选：--hedge 统计限定性词语；--stats 统计各节汉字数。

检查内容：
  1. 标签：旧稿有而新稿没有的 \\label；新稿中指向不存在标签的 \\ref 类引用（主稿与补充材料合并判断）。
  2. 引用：新稿 \\cite 中不在 bib 里的键；bib 中未被引用的条目（给出 --bib 时）。
  3. 数字：正文（\\begin{document} 之后）的数值字面量按多重集合比较，
     列出“旧稿有、新稿缺”和“新稿新增”，附上下文。为减少噪声，忽略：
     一位整数、下标/上标位置的数字、排版长度与表格格式参数、标签/引用键/文件路径中的数字。
退出码：存在悬空引用或丢失标签时为 1，否则为 0。
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REF_CMDS = r"(?:ref|eqref|cref|Cref|autoref|pageref|nameref)"
HEDGE_WORDS = ["不能", "不是", "不表示", "不意味着", "并不", "据此", "而非", "不等于", "不直接",
               "不保证", "不推断", "不声称", "尚待", "核查", "名义", "本稿", "无需", "不必",
               "对账", "仅作", "只作", "限于", "复现说明"]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def strip_comments(text: str) -> str:
    # 去掉未转义 % 之后的内容
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def expand(path: Path, seen: set[Path] | None = None) -> str:
    """递归展开 \\input{...} / \\include{...}；找不到的文件原样保留命令。"""
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)
    text = strip_comments(read(path))

    def repl(m: re.Match) -> str:
        name = m.group(2).strip()
        cand = (path.parent / name)
        for c in (cand, cand.with_suffix(".tex") if cand.suffix != ".tex" else cand):
            if c.is_file():
                return expand(c, seen)
        return m.group(0)

    return re.sub(r"\\(input|include)\{([^}]*)\}", repl, text)


def load(paths: list[str]) -> list[tuple[str, str]]:
    return [(p, expand(Path(p))) for p in paths]


def body(text: str) -> str:
    a = text.find(r"\begin{document}")
    b = text.rfind(r"\end{document}")
    return text[a if a >= 0 else 0: b if b >= 0 else len(text)]


def labels(text: str) -> list[str]:
    return re.findall(r"\\label\{([^}]*)\}", text)


def refs(text: str) -> list[str]:
    keys = []
    for group in re.findall(r"\\" + REF_CMDS + r"\*?\{([^}]*)\}", text):
        keys += [k.strip() for k in group.split(",") if k.strip()]
    return keys


def cites(text: str) -> list[str]:
    keys = []
    for group in re.findall(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", text):
        keys += [k.strip() for k in group.split(",") if k.strip()]
    return keys


def bib_keys(path: Path) -> list[str]:
    return re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", read(path))


_LAYOUT = [
    r"\\label\{[^}]*\}",
    r"\\" + REF_CMDS + r"\*?\{[^}]*\}",
    r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{[^}]*\}",
    r"\\(?:includegraphics|input|include|addbibresource|graphicspath|externaldocument)(?:\[[^\]]*\])?\{(?:[^{}]|\{[^{}]*\})*\}",
    r"\\(?:setlength|addtolength)\{[^}]*\}\{[^}]*\}",
    r"\\renewcommand\{\\arraystretch\}\{[^}]*\}",
    r"\\(?:vspace|hspace|addlinespace|Needspace|allowdisplaybreaks)\*?(?:\[[^\]]*\]|\{[^}]*\})",
    r"table-format\s*=\s*[\d.]+",
    r"[-+]?\d*\.?\d+\s*(?:pt|em|ex|cm|mm|in|bp|sp|pc)\b",
    r"[-+]?\d*\.?\d+\s*\\(?:textwidth|linewidth|columnwidth|textheight|baselineskip)",
    r"[pmb]\{[^}]*\}",          # 表格列宽 p{0.25\linewidth}
    r"\\emergencystretch\s*=\s*\S+",
    r"\\def\\[a-zA-Z]+\{[^}]*\}",
    r"https?://\S+",
]
_NUM = re.compile(r"(?<![A-Za-z\\_^\d.])(?<!_\{)(?<!\^\{)\d+(?:\.\d+)?")


def numbers(text: str) -> list[tuple[str, str]]:
    """返回 (数字, 上下文) 列表。"""
    t = body(text)
    for pat in _LAYOUT:
        t = re.sub(pat, " ", t)
    out = []
    for m in _NUM.finditer(t):
        s = m.group(0)
        if "." not in s and len(s) < 2:
            continue  # 一位整数噪声太大，忽略
        ctx = re.sub(r"\s+", " ", t[max(0, m.start() - 30): m.end() + 30]).strip()
        out.append((s, ctx))
    return out


def cjk_by_section(text: str) -> list[tuple[str, int]]:
    t = body(text)
    parts = re.split(r"(?=\\section\*?\{)", t)
    res = []
    for p in parts:
        m = re.match(r"\\section\*?\{([^}]*)\}", p)
        res.append((m.group(1) if m else "（节前）", len(re.findall(r"[\u4e00-\u9fff]", p))))
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", nargs="+", required=True)
    ap.add_argument("--new", nargs="+", required=True)
    ap.add_argument("--bib")
    ap.add_argument("--hedge", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()

    old, new = load(a.old), load(a.new)
    old_all = "\n".join(t for _, t in old)
    new_all = "\n".join(t for _, t in new)
    lines: list[str] = ["# check_tex 报告", "", f"- 旧稿：{', '.join(a.old)}", f"- 新稿：{', '.join(a.new)}", ""]
    bad = False

    # 1 标签与引用
    old_lab, new_lab = Counter(labels(old_all)), Counter(labels(new_all))
    missing = sorted(set(old_lab) - set(new_lab))
    dup = sorted(k for k, v in new_lab.items() if v > 1)
    dangling = sorted(set(refs(new_all)) - set(new_lab))
    lines += ["## 1 标签与交叉引用", "",
              f"- 旧稿有、新稿缺的标签（{len(missing)}）：" + ("、".join(missing) if missing else "无"),
              f"- 新稿中悬空的引用（{len(dangling)}）：" + ("、".join(dangling) if dangling else "无"),
              f"- 新稿中重复定义的标签（{len(dup)}）：" + ("、".join(dup) if dup else "无"), ""]
    bad |= bool(missing or dangling)

    # 2 文献
    if a.bib:
        bk = set(bib_keys(Path(a.bib)))
        ck = set(cites(new_all))
        lines += ["## 2 参考文献", "",
                  f"- 新稿引用了但 bib 中没有（{len(ck - bk)}）：" + ("、".join(sorted(ck - bk)) or "无"),
                  f"- bib 中有但新稿未引用（{len(bk - ck)}）：" + ("、".join(sorted(bk - ck)) or "无"), ""]

    # 3 数字
    on, nn = numbers(old_all), numbers(new_all)
    oc, nc = Counter(s for s, _ in on), Counter(s for s, _ in nn)
    lost, added = oc - nc, nc - oc
    octx, nctx = defaultdict(list), defaultdict(list)
    for s, c in on:
        octx[s].append(c)
    for s, c in nn:
        nctx[s].append(c)
    lines += ["## 3 数值字面量（多重集合比较）", "",
              f"旧稿 {sum(oc.values())} 个，新稿 {sum(nc.values())} 个；旧稿有、新稿缺 {sum(lost.values())} 个；新稿新增 {sum(added.values())} 个。", ""]
    if lost:
        lines += ["### 旧稿有、新稿缺", "", "| 数字 | 缺少次数 | 旧稿中的上下文（最多 3 处） |", "|---|---:|---|"]
        for s in sorted(lost, key=lambda x: (-lost[x], x)):
            lines.append(f"| {s} | {lost[s]} | " + " ／ ".join(octx[s][:3]).replace("|", "\\|") + " |")
        lines.append("")
    if added:
        lines += ["### 新稿新增", "", "| 数字 | 新增次数 | 新稿中的上下文（最多 3 处） |", "|---|---:|---|"]
        for s in sorted(added, key=lambda x: (-added[x], x)):
            lines.append(f"| {s} | {added[s]} | " + " ／ ".join(nctx[s][:3]).replace("|", "\\|") + " |")
        lines.append("")

    # 4 可选统计
    if a.hedge:
        ob, nb = body(old_all), body(new_all)
        lines += ["## 4 限定性词语计数（正文）", "", "| 词语 | 旧稿 | 新稿 |", "|---|---:|---:|"]
        lines += [f"| {w} | {ob.count(w)} | {nb.count(w)} |" for w in HEDGE_WORDS]
        lines.append("")
    if a.stats:
        lines += ["## 5 各节汉字数（新稿）", "", "| 节 | 汉字数 |", "|---|---:|"]
        for _, t in new:
            lines += [f"| {name} | {n} |" for name, n in cjk_by_section(t)]
        lines.append("")

    report = "\n".join(lines)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(report, encoding="utf-8")
        summary = (f"标签缺失 {len(missing)}，悬空引用 {len(dangling)}，"
                   f"数字缺 {sum(lost.values())}、增 {sum(added.values())}；报告：{a.out}")
        _print(summary)
    else:
        _print(report)
    return 1 if bad else 0


def _print(s: str) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台
    except Exception:
        pass
    print(s)


if __name__ == "__main__":
    sys.exit(main())
