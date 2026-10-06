#!/usr/bin/env bash
# paper/ 编译脚本（Linux/macOS）：先编译补充材料，再编译主稿；不运行任何科学计算。
# 阶段 2 拆分文件后，把下面两个变量改成新的主文件名（不带 .tex）。
SUPPLEMENT=flatten_curve_supplement_cn
MAIN=flatten_curve_analysis_cn

set -euo pipefail
cd "$(dirname "$0")"
for doc in "$SUPPLEMENT" "$MAIN"; do
  xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" >/dev/null || { echo "$doc 首遍编译失败，见 $doc.log"; exit 1; }
  biber "$doc" >/dev/null || { echo "$doc 参考文献编译失败，见 $doc.blg"; exit 1; }
  for pass in 1 2; do
    xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" >/dev/null || { echo "$doc 交叉引用编译失败，见 $doc.log"; exit 1; }
  done
done
for doc in "$SUPPLEMENT" "$MAIN"; do
  pages=$(tr -d '\n' < "$doc.log" | grep -ao 'Output written on[^(]*([0-9]* pages' | grep -o '[0-9]* pages' || true)
  undef=$(grep -ac 'undefined' "$doc.log" || true)
  multi=$(grep -ac 'multiply defined' "$doc.log" || true)
  echo "$doc: $pages；含 undefined 的行 $undef；含 multiply defined 的行 $multi"
done
