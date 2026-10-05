param(
    [string]$Python = '',
    [string]$Matlab = '',
    [string]$OutputDirectory = '',
    [int]$Repeats = 2,
    [ValidateSet('all','joint-extra')][string]$Scope = 'all'
)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
if(-not $Python) {
    $taskVenv=Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if(Test-Path -LiteralPath $taskVenv) { $Python=$taskVenv }
    else { $Python=(Get-Command python -ErrorAction Stop).Source }
}
if(-not $Matlab -and $Scope -eq 'all') { $Matlab=(Get-Command matlab -ErrorAction Stop).Source }
if(-not $OutputDirectory) {
    $OutputDirectory=Join-Path $PSScriptRoot ('runs\'+(Get-Date -Format 'yyyyMMdd_HHmmss'))
}
$env:PYTHONUTF8='1'
$env:MPLBACKEND='Agg'
Push-Location $taskRoot
try {
    $taskArguments=@('--output',$OutputDirectory,'--scope',$Scope,'--repeats',$Repeats)
    if($Matlab) { $taskArguments+=@('--matlab',$Matlab) }
    & $Python -B (Join-Path $PSScriptRoot 'run_all.py') @taskArguments
    if($LASTEXITCODE -ne 0) { throw "整稿复现未通过，退出码 $LASTEXITCODE；请保留输出中的失败报告。" }
} finally { Pop-Location }
