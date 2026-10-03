$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
function Invoke-Checked([string]$Command, [string[]]$Arguments) {
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Command failed with exit code $LASTEXITCODE" }
}
Invoke-Checked "xelatex" @("-interaction=nonstopmode", "-halt-on-error", "flatten_curve_supplement_cn.tex")
Invoke-Checked "xelatex" @("-interaction=nonstopmode", "-halt-on-error", "flatten_curve_supplement_cn.tex")
Invoke-Checked "xelatex" @("-interaction=nonstopmode", "-halt-on-error", "flatten_curve_analysis_cn.tex")
Invoke-Checked "biber" @("flatten_curve_analysis_cn")
Invoke-Checked "xelatex" @("-interaction=nonstopmode", "-halt-on-error", "flatten_curve_analysis_cn.tex")
Invoke-Checked "xelatex" @("-interaction=nonstopmode", "-halt-on-error", "flatten_curve_analysis_cn.tex")
