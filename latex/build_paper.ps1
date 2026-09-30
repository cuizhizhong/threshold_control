# 先编译补充表的跨文档标签，再编译主稿与文献。
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    foreach ($pass in 1..2) {
        & xelatex -interaction=nonstopmode -halt-on-error flatten_curve_supplement_cn.tex
        if ($LASTEXITCODE -ne 0) { throw '补充材料编译失败' }
    }
    & xelatex -interaction=nonstopmode -halt-on-error flatten_curve_analysis_cn.tex
    if ($LASTEXITCODE -ne 0) { throw '主稿首遍编译失败' }
    & biber flatten_curve_analysis_cn
    if ($LASTEXITCODE -ne 0) { throw '参考文献编译失败' }
    foreach ($pass in 1..2) {
        & xelatex -interaction=nonstopmode -halt-on-error flatten_curve_analysis_cn.tex
        if ($LASTEXITCODE -ne 0) { throw '主稿交叉引用编译失败' }
    }
} finally {
    Pop-Location
}

