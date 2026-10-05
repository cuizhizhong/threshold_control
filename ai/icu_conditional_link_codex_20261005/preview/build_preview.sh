#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
xelatex -interaction=nonstopmode -halt-on-error 修改内容阅读稿.tex
biber 修改内容阅读稿
xelatex -interaction=nonstopmode -halt-on-error 修改内容阅读稿.tex
xelatex -interaction=nonstopmode -halt-on-error 修改内容阅读稿.tex
