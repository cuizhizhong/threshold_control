#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
for tool in xelatex biber; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Missing tool: $tool" >&2; exit 1; }
done
xelatex -interaction=nonstopmode -halt-on-error flatten_curve_supplement_cn.tex
xelatex -interaction=nonstopmode -halt-on-error flatten_curve_supplement_cn.tex
xelatex -interaction=nonstopmode -halt-on-error flatten_curve_analysis_cn.tex
biber flatten_curve_analysis_cn
xelatex -interaction=nonstopmode -halt-on-error flatten_curve_analysis_cn.tex
xelatex -interaction=nonstopmode -halt-on-error flatten_curve_analysis_cn.tex
