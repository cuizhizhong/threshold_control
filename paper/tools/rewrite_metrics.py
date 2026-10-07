#!/usr/bin/env python3
"""只读统计：衡量一次改写到底改了多少，以及行文是否紧凑。不修改任何文件。

用法（在仓库根目录运行）：
  python paper/tools/rewrite_metrics.py --old <旧稿 tex，可多个> --new <新稿 tex，可多个> [--out 报告.md]
         [--watch "无额外能力限制,0<\beta<1,完整初值"]

  --old 可以是整篇主稿（会展开 \\input），也可以是某个章节在改写前的版本；
  --new 通常是改写后的单个章节文件，如 paper/sections/03_single_control.tex。
  取某个提交里的旧版本：git show <提交>:paper/sections/03_single_control.tex > 旧版本.tex

统计对象分三类：
  正文   ：定理类环境、证明、公式、图表环境之外的文字；
  陈述   ：theorem/proposition/lemma/corollary/definition/remark 等环境内的文字；
  证明   ：proof 环境内的文字。
只计汉字及其他文字，公式（$…$、\\[…\\]、equation/align 等）一律剔除。

输出：
  1. 汉字数：新旧对比及变化比例；
  2. 句子沿用率：新稿每一句与旧稿最相近的一句按顺序对上的字符比例（沿用度）。
     ≥0.80 记为“沿用原句”（含只换了几个词的句子），0.50–0.80 记为“部分改写”，
     <0.50 记为“重写”。只换词、删限定语或在原句前后追加分句的句子会落在前两类；
  3. 段落结构（新稿正文）：段落数、单句段落数、平均段长、每段数字个数的最大值和超过 4 个数字的段落数、
     平均句长与超过 80 字的长句数；
  4. 限定性与否定词计数（正文），以及 --watch 指定的短语在新旧稿中的出现次数；
  5. 沿用最多的若干原句，便于定位没有真正重写的段落。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

STATEMENT_ENVS = ["theorem", "proposition", "lemma", "corollary", "corollaryn", "definition",
                  "remark", "remarkn", "assumption", "example", "conjecture"]
MATH_ENVS = ["equation", "equation*", "align", "align*", "gather", "gather*", "multline",
             "multline*", "eqnarray", "eqnarray*", "split", "cases", "array", "aligned", "gathered"]
FLOAT_ENVS = ["figure", "figure*", "table", "table*", "tabular", "tabular*", "threeparttable",
              "tikzpicture"]
HEDGE = ["不能", "不是", "不表示", "不意味着", "并不", "据此", "而非", "不等于", "不直接", "不保证",
         "不推断", "不声称", "尚待", "核查", "名义", "本稿", "无需", "不必", "对账", "仅作", "只作",
         "限于", "仅限", "只针对", "只说明", "只刻画", "不作为", "不代表", "不构成", "不能据此",
         "口径", "需要说明", "需要指出", "值得注意", "应当注意"]
SENT_SPLIT = re.compile(r"(?<=[。！？；])")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def expand(path: Path, seen=None) -> str:
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return ""
    seen.add(path)
    text = strip_comments(read(path))

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


def body(text: str) -> str:
    a = text.find(r"\begin{document}")
    b = text.rfind(r"\end{document}")
    if a < 0:
        return text
    return text[a: b if b > a else len(text)]


def cut_envs(text: str, names: list[str], sep: str = "\n\n") -> tuple[str, list[str]]:
    """把指定环境整体取出；返回（剩余文本，取出的环境内容列表）。支持嵌套同名环境。"""
    taken = []
    pat = re.compile(r"\\(begin|end)\{(" + "|".join(re.escape(n) for n in names) + r")\}")
    out, depth, start, last = [], 0, 0, 0
    for m in pat.finditer(text):
        if m.group(1) == "begin":
            if depth == 0:
                out.append(text[last:m.start()])
                start = m.end()
            depth += 1
        else:
            if depth > 0:
                depth -= 1
                if depth == 0:
                    taken.append(text[start:m.start()])
                    last = m.end()
                    out.append(sep)
    out.append(text[last:] if depth == 0 else "")
    return "".join(out), taken


def plain(text: str) -> str:
    """去掉公式与命令，只留可读文字；段落分隔保留为空行。"""
    t, _ = cut_envs(text, MATH_ENVS, sep=" X ")   # 行间公式属于所在段落，不切段
    t = re.sub(r"\\\[.*?\\\]", " X ", t, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", " ", t, flags=re.S)
    t = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", "X", t, flags=re.S)   # 行内公式记为一个占位符
    t = re.sub(r"\\(label|ref|eqref|cref|Cref|cite|citep|citet|autoref|pageref|includegraphics|"
               r"input|include|addbibresource|vspace|hspace)\*?(\[[^\]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\(section|subsection|subsubsection|paragraph|caption|textbf|emph|textit)\*?"
               r"(\[[^\]]*\])?\{([^{}]*)\}", r"\3", t)
    t = re.sub(r"\\[a-zA-Z@]+\*?", " ", t)
    t = re.sub(r"[{}~]", "", t)
    return t


def split_parts(text: str) -> dict[str, str]:
    t = body(text)
    t, _ = cut_envs(t, FLOAT_ENVS)
    t, proofs = cut_envs(t, ["proof"])
    t, stmts = cut_envs(t, STATEMENT_ENVS)
    return {"正文": plain(t), "陈述": plain("\n\n".join(stmts)), "证明": plain("\n\n".join(proofs))}


def cjk(s: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", s))


def sentences(s: str) -> list[str]:
    out = []
    for para in re.split(r"\n\s*\n", s):
        para = re.sub(r"\s+", "", para)
        for x in SENT_SPLIT.split(para):
            if cjk(x) >= 8:
                out.append(x)
    return out


def paragraphs(s: str) -> list[str]:
    return [p for p in (re.sub(r"\s+", "", x) for x in re.split(r"\n\s*\n", s)) if cjk(p) >= 15]


def grams(s: str, n: int = 3) -> set[str]:
    s = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9X]", "", s)
    return {s[i:i + n] for i in range(max(1, len(s) - n + 1))}


def best_match(new_sents: list[str], old_sents: list[str]) -> list[tuple[float, str, str]]:
    """对新稿每句，返回（沿用度，新句，最相近的旧句）。

    先用汉字 2-gram 找出共享片段最多的 5 个旧句作候选，再用 difflib 计算新句中
    能与候选旧句按顺序对上的字符比例（沿用度 = 对上的字符数 / 新句字符数），取最大值。
    只换了个别词、删了限定语或在原句前后追加分句的句子，沿用度仍然较高。
    """
    import difflib

    def key(x: str) -> str:
        return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9X]", "", x)

    old_k = [key(x) for x in old_sents]
    old_g = [grams(x, 2) for x in old_sents]
    index: dict[str, list[int]] = {}
    for i, g in enumerate(old_g):
        for k in g:
            index.setdefault(k, []).append(i)
    res = []
    for s in new_sents:
        ks = key(s)
        cand: dict[int, int] = {}
        for k in grams(s, 2):
            for i in index.get(k, ()):
                cand[i] = cand.get(i, 0) + 1
        best, bi = 0.0, -1
        for i, _ in sorted(cand.items(), key=lambda kv: -kv[1])[:5]:
            sm = difflib.SequenceMatcher(None, ks, old_k[i], autojunk=False)
            r = sum(b.size for b in sm.get_matching_blocks()) / max(1, len(ks))
            if r > best:
                best, bi = r, i
        res.append((best, s, old_sents[bi] if bi >= 0 else ""))
    return res


def prose_numbers_per_paragraph(raw: str) -> list[int]:
    """正文（不含定理、证明、图表环境）每段中的数值字面量个数；一位整数不计。"""
    t = body(raw)
    t, _ = cut_envs(t, FLOAT_ENVS)
    t, _ = cut_envs(t, ["proof"])
    t, _ = cut_envs(t, STATEMENT_ENVS)
    t = re.sub(r"\\(label|ref|eqref|cref|cite|includegraphics)\*?\{[^}]*\}", " ", t)
    out = []
    for para in re.split(r"\n\s*\n", t):
        if cjk(para) < 15:
            continue
        out.append(len(re.findall(r"(?<![A-Za-z_\\^{\d.])\d+(?:\.\d+)?(?![\d])", para))
                   - len(re.findall(r"(?<![A-Za-z_\\^{\d.])\d(?![\d.])", para)))
    return out


def hedge_counts(s: str) -> dict[str, int]:
    t = re.sub(r"\s+", "", s)
    return {w: t.count(w) for w in HEDGE if t.count(w)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", nargs="+", required=True)
    ap.add_argument("--new", nargs="+", required=True)
    ap.add_argument("--out")
    ap.add_argument("--top", type=int, default=15, help="列出沿用最多的原句条数")
    ap.add_argument("--watch", default="", help="逗号分隔的短语，统计其在新旧稿全文（含公式源码）中的出现次数")
    a = ap.parse_args()

    old_raw = "\n".join(expand_spec(p) for p in a.old)
    new_raw = "\n".join(expand_spec(p) for p in a.new)
    old, new = split_parts(old_raw), split_parts(new_raw)
    L = ["# 改写统计", "", f"- 旧稿：{' '.join(a.old)}", f"- 新稿：{' '.join(a.new)}", ""]

    L += ["## 1 汉字数", "", "| 部分 | 旧稿 | 新稿 | 变化 |", "|---|---:|---:|---:|"]
    for k in ("正文", "陈述", "证明"):
        o, n = cjk(old[k]), cjk(new[k])
        L.append(f"| {k} | {o} | {n} | {((n - o) / o * 100 if o else 0):+.0f}% |")
    L.append("")
    L.append("注：旧稿若是整篇，汉字数变化没有意义，只看第 2 节的保留率。")
    L.append("")

    L += ["## 2 句子沿用率（新稿每句与旧稿最相近一句按顺序对上的字符比例）", "",
          "| 部分 | 新稿句数 | 沿用原句（≥0.80） | 部分改写（0.50–0.80） | 重写（<0.50） |",
          "|---|---:|---:|---:|---:|"]
    kept_examples = []
    for k in ("正文", "陈述", "证明"):
        ns, os_ = sentences(new[k]), sentences(old["正文"] + "\n\n" + old["陈述"] + "\n\n" + old["证明"])
        if not ns:
            L.append(f"| {k} | 0 | – | – | – |")
            continue
        m = best_match(ns, os_)
        hi = sum(1 for r, _, _ in m if r >= 0.80)
        mid = sum(1 for r, _, _ in m if 0.50 <= r < 0.80)
        lo = len(m) - hi - mid
        f = lambda x: f"{x}（{x / len(m) * 100:.0f}%）"
        L.append(f"| {k} | {len(m)} | {f(hi)} | {f(mid)} | {f(lo)} |")
        if k == "正文":
            kept_examples = sorted([r for r in m if r[0] >= 0.80], key=lambda r: -cjk(r[1]))
    L.append("")

    ps, ss = paragraphs(new["正文"]), sentences(new["正文"])
    nsent = [len([x for x in SENT_SPLIT.split(p) if cjk(x) >= 4]) for p in ps]
    nums = [n for n in prose_numbers_per_paragraph(new_raw)]
    L += ["## 3 段落结构（新稿正文）", "",
          f"- 段落数：{len(ps)}；其中单句段落 {sum(1 for k in nsent if k <= 1)} 个；"
          f"平均每段 {sum(nsent) / max(1, len(ps)):.1f} 句、{sum(cjk(p) for p in ps) / max(1, len(ps)):.0f} 字",
          f"- 每段数字个数：最多 {max(nums) if nums else 0} 个；超过 4 个数字的段落 {sum(1 for n in nums if n > 4)} 个",
          f"- 句子数：{len(ss)}；平均句长 {sum(cjk(s) for s in ss) / max(1, len(ss)):.0f} 字；"
          f"超过 80 字的长句 {sum(1 for s in ss if cjk(s) > 80)} 句", ""]

    ho, hn = hedge_counts(old["正文"]), hedge_counts(new["正文"])
    L += ["## 4 限定性与否定词（正文）", "", "| 词语 | 旧稿 | 新稿 |", "|---|---:|---:|"]
    for w in HEDGE:
        if ho.get(w) or hn.get(w):
            L.append(f"| {w} | {ho.get(w, 0)} | {hn.get(w, 0)} |")
    L += ["", f"合计：旧稿 {sum(ho.values())}，新稿 {sum(hn.values())}；"
              f"新稿每千字 {sum(hn.values()) / max(1, cjk(new['正文'])) * 1000:.1f} 个。", ""]
    watch = [w.strip() for w in a.watch.split(",") if w.strip()]
    if watch:
        ob, nb = re.sub(r"\s+", "", body(old_raw)), re.sub(r"\s+", "", body(new_raw))
        L += ["### 指定短语（全文，含公式源码）", "", "| 短语 | 旧稿 | 新稿 |", "|---|---:|---:|"]
        L += [f"| {w} | {ob.count(w.replace(' ', ''))} | {nb.count(w.replace(' ', ''))} |" for w in watch]
        L.append("")

    if kept_examples:
        L += [f"## 5 正文中沿用原句的较长句子（前 {a.top} 句）", ""]
        for r, s, _ in kept_examples[: a.top]:
            L.append(f"- （{r:.2f}）{s[:120]}{'…' if len(s) > 120 else ''}")
        L.append("")

    rep = "\n".join(L)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(rep, encoding="utf-8")
        print(f"报告：{a.out}")
    else:
        print(rep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
