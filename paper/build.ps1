# paper/ 编译脚本：先编译补充材料，再编译主稿；不运行任何科学计算。
# 阶段 2 拆分文件后，把下面两个变量改成新的主文件名（不带 .tex）。
$Supplement = 'flatten_curve_supplement_cn'
$Main = 'flatten_curve_analysis_cn'

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    foreach ($doc in @($Supplement, $Main)) {
        & xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "$doc 首遍编译失败，见 $doc.log" }
        & biber $doc | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "$doc 参考文献编译失败，见 $doc.blg" }
        foreach ($pass in 1..2) {
            & xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "$doc 交叉引用编译失败，见 $doc.log" }
        }
    }
    foreach ($doc in @($Supplement, $Main)) {
        $log = Get-Content "$doc.log" -Raw -Encoding UTF8
        $pages = [regex]::Match($log, 'Output written on[\s\S]*?\((\d+)\s+pages').Groups[1].Value
        $undef = ([regex]::Matches($log, 'undefined')).Count
        $multi = ([regex]::Matches($log, 'multiply defined')).Count
        $overfull = ([regex]::Matches($log, 'Overfull \\hbox \((\d+\.?\d*)pt') | Where-Object { [double]$_.Groups[1].Value -gt 10 }).Count
        Write-Host ("{0}: {1} 页；undefined {2} 处；multiply defined {3} 处；超过 10pt 的 Overfull hbox {4} 处" -f $doc, $pages, $undef, $multi, $overfull)
    }
} finally {
    Pop-Location
}
