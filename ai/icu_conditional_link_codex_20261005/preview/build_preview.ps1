$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
& xelatex -interaction=nonstopmode -halt-on-error "修改内容阅读稿.tex"
if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass 1 failed" }
& biber "修改内容阅读稿"
if ($LASTEXITCODE -ne 0) { throw "Biber failed" }
& xelatex -interaction=nonstopmode -halt-on-error "修改内容阅读稿.tex"
if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass 2 failed" }
& xelatex -interaction=nonstopmode -halt-on-error "修改内容阅读稿.tex"
if ($LASTEXITCODE -ne 0) { throw "XeLaTeX pass 3 failed" }
