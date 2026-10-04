# 按固化清单回收旧产物；不永久删除，不提交 Git，不改正式论文。
param([ValidateSet('Prepare','SnapshotDirectories','RecoverJournal','Recycle','Verify','RecycleVerification','Finalize')][string]$Mode = 'Prepare')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$taskReportDir = $PSScriptRoot
$taskManifestPath = Join-Path $taskReportDir 'manifest.json'
$taskJournalPath = Join-Path $taskReportDir 'recycle_journal.json'
$taskProtectedPath = Join-Path $taskReportDir 'protected_before.json'
$taskVerifyDir = Join-Path $taskRoot 'tmp/cleanup_verify_20261003'
function Save-Report($Path, $Object) {
    # 原子发布生成报告，避免索引器映射旧文件时就地写入失败。
    $staged = $Path + '.write-' + [Guid]::NewGuid().ToString('N')
    [IO.File]::WriteAllText($staged, ($Object | ConvertTo-Json -Depth 40) + "`n", [Text.UTF8Encoding]::new($false))
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        try { [IO.File]::Move($staged, $Path, $true); return }
        catch [IO.IOException] {
            if ($attempt -eq 19) { throw }
            Start-Sleep -Milliseconds 100
        }
    }
}
function Read-Report($Path) { Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -AsHashtable }
function Checked-Path([string]$Relative) {
    $full = [IO.Path]::GetFullPath((Join-Path $taskRoot $Relative))
    if (-not $full.StartsWith($taskRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "目标越界：$full"
    }
    $cursor = $full
    while ($cursor -ne $taskRoot) {
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "拒绝链接或重解析点：$cursor"
            }
        }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
    return $full
}
function Relative-Path([string]$Path) { [IO.Path]::GetRelativePath($taskRoot, $Path).Replace('\','/') }
function Tree-Files([string]$Relative) {
    $full = Checked-Path $Relative
    foreach ($item in Get-ChildItem -LiteralPath $full -Recurse -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "拒绝链接：$($item.FullName)" }
        if (-not $item.PSIsContainer) { $item }
    }
}
function Hash-File([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Record-File([IO.FileInfo]$Item) {
    @{ file = (Relative-Path $Item.FullName); absolute_path = $Item.FullName; bytes = $Item.Length; sha256 = (Hash-File $Item.FullName) }
}
$taskFormal = @(
    'figures/Fig1.pdf','figures/optimal_control_with_quarantine_panels.pdf',
    'figures/layout_v5/baseline_q_joint.pdf','figures/scenario1_heatmaps_c0_eta.pdf',
    'figures/layout_v5/scenario1_inflection_lambda_sensitivity.pdf','figures/layout_v5/scenario1_inflection_scan_t.pdf',
    'figures/layout_v5/c0_sensitivity_selected_eta.pdf','figures/layout_v5/eta_sensitivity_selected_c0.pdf',
    'figures/layout_v5/xian_observed_fit.pdf','figures/layout_v5/xian_strategy_process.pdf',
    'figures/xian_eta_sensitivity.pdf','figures/xian_heatmaps.pdf','figures/fig_dom_combined.pdf',
    'figures/layout_v5/population_threshold_levers.pdf','figures/layout_v5/c0_sensitivity_panel.pdf',
    'figures/layout_v5/c0_phase_stationary.pdf','figures/layout_v5/fig_panel_B_trajectory_decomposition.pdf',
    'figures/layout_v5/critical_population_cases.pdf','figures/c0_sensitivity_scan.pdf','figures/c0_beta_existence.pdf'
)
if ($Mode -eq 'Prepare') {
    if (Test-Path -LiteralPath $taskManifestPath) { throw '清单已存在，禁止重写或扩大范围。' }
    $groups = [ordered]@{}
    $groups.ai_duplicates = @('ai/flatten_curve_analysis_cn.tex','ai/flatten_curve_analysis_cn.pdf','ai/threshold_control_reproducible_release_20261002.zip')
    $groups.legacy_figures_tables = @('figures','table','latex/table' | ForEach-Object { Tree-Files $_ } | ForEach-Object { Relative-Path $_.FullName })
    $groups.unused_formal_exports = @(Tree-Files 'latex/figures' | Where-Object { (Relative-Path $_.FullName).Substring(6) -notin $taskFormal } | ForEach-Object { Relative-Path $_.FullName })
    $groups.old_tmp = @(Tree-Files 'tmp' | ForEach-Object { Relative-Path $_.FullName })
    $groups.python_cache = @(Tree-Files 'reproducibility/__pycache__' | ForEach-Object { Relative-Path $_.FullName })
    $groups.tex_intermediates = @(
        'flatten_curve_analysis_cn.aux','flatten_curve_analysis_cn.bbl','flatten_curve_analysis_cn.bcf',
        'flatten_curve_analysis_cn.blg','flatten_curve_analysis_cn.log','flatten_curve_analysis_cn.out',
        'flatten_curve_analysis_cn.run.xml','flatten_curve_analysis_cn.synctex.gz.sum.synctex',
        'flatten_curve_supplement_cn.aux','flatten_curve_supplement_cn.bcf','flatten_curve_supplement_cn.log',
        'flatten_curve_supplement_cn.out','flatten_curve_supplement_cn.run.xml'
    ) | ForEach-Object { 'latex/' + $_ }
    $expected = @{ai_duplicates=3;legacy_figures_tables=44;unused_formal_exports=78;old_tmp=177;python_cache=22;tex_intermediates=13}
    $tracked = @(& git -c core.quotePath=false ls-files)
    if ($LASTEXITCODE -ne 0) { throw '无法读取 Git 文件清单' }
    $records = @()
    foreach ($group in $groups.Keys) {
        if (@($groups[$group]).Count -ne $expected[$group]) { throw "候选数量变化：$group" }
        foreach ($relative in $groups[$group]) {
            $item = Get-Item -LiteralPath (Checked-Path $relative) -Force
            if ($item.PSIsContainer) { throw "不是文件：$relative" }
            $record = Record-File $item
            $record.group = $group; $record.git_tracked = $relative -cin $tracked
            $record.reason = switch ($group) {
                'ai_duplicates' {'冻结包的完全重复副本'}
                'legacy_figures_tables' {'当前论文及独立复现不读取的旧导出'}
                'unused_formal_exports' {'不属于正式稿引用20PDF的旧导出或预览'}
                'old_tmp' {'此前临时检查产物'}
                'python_cache' {'可重新生成的字节码缓存'}
                'tex_intermediates' {'可由完整编译入口重新生成的中间产物'}
            }
            $records += $record
        }
    }
    if ($records.Count -ne 337 -or @($records.file | Select-Object -Unique).Count -ne 337) { throw '清单数量或唯一性不符' }
    foreach ($extension in @('tex','pdf')) {
        if ((Hash-File (Join-Path $taskRoot "ai/flatten_curve_analysis_cn.$extension")) -ne
            (Hash-File (Join-Path $taskRoot "ai/threshold_control_reproducible_release_20261002/latex/flatten_curve_analysis_cn.$extension"))) { throw 'AI 稿并非完全重复' }
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead((Join-Path $taskRoot 'ai/threshold_control_reproducible_release_20261002.zip'))
    try {
        $entries = @($zip.Entries | Where-Object { $_.Name })
        $releaseFiles = @(Tree-Files 'ai/threshold_control_reproducible_release_20261002')
        if ($entries.Count -ne 87 -or $releaseFiles.Count -ne 87) { throw '冻结包或 ZIP 文件数量变化' }
        foreach ($entry in $entries) {
            $relative = $entry.FullName.Replace('\','/')
            $prefix = 'threshold_control_reproducible_release_20261002/'
            if ($relative.StartsWith($prefix)) { $relative = $relative.Substring($prefix.Length) }
            $source = Checked-Path ('ai/threshold_control_reproducible_release_20261002/' + $relative)
            $stream = $entry.Open()
            try { $actual = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stream)).ToLowerInvariant() } finally { $stream.Dispose() }
            if ($actual -ne (Hash-File $source)) { throw "ZIP 内容不同：$relative" }
        }
    } finally { $zip.Dispose() }
    $protected = @()
    $excludedRoot = @('.git','.venv','.claude','.vscode','tmp')
    foreach ($top in Get-ChildItem -LiteralPath $taskRoot -Force) {
        if ($top.Name -in $excludedRoot) { continue }
        if ($top.PSIsContainer) {
            # 本地 Python 环境不是研究材料；逐个目录枚举，避免跟随链接。
            $stack = [Collections.Generic.Stack[string]]::new(); $stack.Push($top.FullName)
            while ($stack.Count) {
                $dir = $stack.Pop()
                foreach ($item in Get-ChildItem -LiteralPath $dir -Force) {
                    $rel = Relative-Path $item.FullName
                    if ($rel -eq 'reproducibility/.venv' -or $rel.StartsWith('reproducibility/release_reports/cleanup_20261003')) { continue }
                    [void](Checked-Path $rel)
                    if ($item.PSIsContainer) { $stack.Push($item.FullName) }
                    elseif ($rel -notin $records.file -and $rel -ne 'README.md') { $protected += (Record-File $item) }
                }
            }
        } elseif ($top.Name -ne 'README.md') { $protected += (Record-File $top) }
    }
    Save-Report $taskProtectedPath @{files=$protected;count=$protected.Count;readme_before=(Record-File (Get-Item -LiteralPath (Join-Path $taskRoot 'README.md')))}
    $manifest = @{ root=$taskRoot;created_at=(Get-Date).ToString('o');head=(& git rev-parse HEAD);expected_count=337;files=$records;formal_figures=$taskFormal;groups=$expected;permanent_delete_allowed=$false;new_files_auto_included=$false }
    Save-Report $taskManifestPath $manifest
    Save-Report $taskJournalPath @{state='prepared';files=@();directories=@();failures=@();permanent_delete_used=$false;git_writes=$false}
    Write-Output "Prepared 337 candidates; protected=$($protected.Count); bytes=$(($records.bytes | Measure-Object -Sum).Sum)"
    exit 0
}
$manifest = Read-Report $taskManifestPath
$journal = Read-Report $taskJournalPath
if ($Mode -eq 'SnapshotDirectories') {
    if ($journal.state -ne 'prepared') { throw '目录快照必须在回收前生成' }
    $directoryPath = Join-Path $taskReportDir 'directory_manifest.json'
    if (Test-Path -LiteralPath $directoryPath) { throw '目录快照已固化' }
    $directories = @()
    foreach ($relative in @('figures','table','latex/table','latex/figures','tmp','reproducibility/__pycache__')) {
        $full = Checked-Path $relative
        $directories += $relative
        foreach ($item in Get-ChildItem -LiteralPath $full -Directory -Recurse -Force) {
            $rel = Relative-Path $item.FullName
            [void](Checked-Path $rel); $directories += $rel
        }
    }
    Save-Report $directoryPath @{directories=@($directories | Select-Object -Unique | Sort-Object Length -Descending);new_directories_auto_included=$false}
    Write-Output "Directory snapshot=$($directories.Count)"
    exit 0
}
function Recycle-One([hashtable]$Record) {
    $full = Checked-Path $Record.file
    if ((Hash-File $full) -ne $Record.sha256) { throw "回收前内容变化：$full" }
    $previous = @(Get-ChildItem -LiteralPath $script:taskRecycleDir -Filter '$I*' -File -Force | ForEach-Object { $_.Name })
    [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($full, [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
        [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin, [Microsoft.VisualBasic.FileIO.UICancelOption]::ThrowException)
    $found = $null
    foreach ($info in Get-ChildItem -LiteralPath $script:taskRecycleDir -Filter '$I*' -File -Force) {
        if ($info.Name -in $previous) { continue }
        $data = [IO.File]::ReadAllBytes($info.FullName)
        $version = [BitConverter]::ToInt64($data,0)
        $offset = if ($version -eq 2) {28} elseif ($version -eq 1) {24} else {throw '不识别的回收站记录'}
        $original = [Text.Encoding]::Unicode.GetString($data,$offset,$data.Length-$offset).TrimEnd([char]0)
        if ($original -ieq $full) {
            $payload = Join-Path $script:taskRecycleDir ('$R' + $info.Name.Substring(2))
            if ((Hash-File $payload) -ne $Record.sha256) { throw "回收站内容哈希不符：$full" }
            $found = @{file=$Record.file;sha256=$Record.sha256;bytes=$Record.bytes;recycle_info=$info.FullName;recycle_payload=$payload;verified_recoverable=$true;time=(Get-Date).ToString('o')}
            break
        }
    }
    if (-not $found -or (Test-Path -LiteralPath $full)) { throw "无法确认已进入回收站，立即停止：$full" }
    return $found
}
if ($Mode -in @('RecoverJournal','Recycle','RecycleVerification')) {
    $taskSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $taskRecycleDir = 'E:\$Recycle.Bin\' + $taskSid
    if (-not (Test-Path -LiteralPath $taskRecycleDir)) { throw '本人回收站不存在；不作永久删除' }
    $volume = (& mountvol E:\ /L).Trim()
    if ($volume -notmatch 'Volume(\{[^}]+\})') { throw '无法识别 E 盘回收站设置' }
    $settings = Get-ItemProperty -LiteralPath ('HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\BitBucket\Volume\' + $Matches[1])
    if ($settings.NukeOnDelete -ne 0 -or $settings.MaxCapacity -lt 1024) { throw '回收站配置不满足可恢复清理条件' }
    Add-Type -AssemblyName Microsoft.VisualBasic
    $journal.windows_user_sid = $taskSid
    if ($Mode -eq 'RecoverJournal') {
        # 只读核对回收站以补齐日志写入失败后的记录，不执行任何删除。
        $byOriginal = @{}
        foreach ($info in Get-ChildItem -LiteralPath $taskRecycleDir -Filter '$I*' -File -Force) {
            $data = [IO.File]::ReadAllBytes($info.FullName)
            $version = [BitConverter]::ToInt64($data,0)
            $offset = if ($version -eq 2) {28} elseif ($version -eq 1) {24} else {continue}
            $original = [Text.Encoding]::Unicode.GetString($data,$offset,$data.Length-$offset).TrimEnd([char]0)
            $byOriginal[$original] = $info.FullName
        }
        $recovered = @()
        foreach ($record in $manifest.files) {
            $full = Checked-Path $record.file
            if (Test-Path -LiteralPath $full) {
                if ((Hash-File $full) -ne $record.sha256) { throw "剩余候选发生变化：$full" }
                continue
            }
            if (-not $byOriginal.ContainsKey($full)) { throw "缺失候选没有回收记录：$full" }
            $info = $byOriginal[$full]
            $payload = Join-Path $taskRecycleDir ('$R' + [IO.Path]::GetFileName($info).Substring(2))
            if ((Hash-File $payload) -ne $record.sha256) { throw "回收站内容不同：$full" }
            $recovered += @{file=$record.file;sha256=$record.sha256;bytes=$record.bytes;recycle_info=$info;recycle_payload=$payload;verified_recoverable=$true;journal_reconciled=$true;time=(Get-Date).ToString('o')}
        }
        $journal.failures += @{error='原日志就地写入遇到用户映射文件占用；已改用原子发布并逐项核对回收站';recovered_files=$recovered.Count;time=(Get-Date).ToString('o')}
        $journal.files=$recovered;$journal.state='prepared'
        Save-Report $taskJournalPath $journal
        Write-Output "Reconciled=$($recovered.Count); remaining=$(337-$recovered.Count); no deletion performed"
        exit 0
    }
    try {
        if ($Mode -eq 'Recycle') {
            if ($journal.state -ne 'prepared') { throw '不允许重放已执行清单' }
            # 整批预检通过后才回收首个文件。
            foreach ($record in $manifest.files) {
                if ($record.file -in $journal.files.file) { continue }
                if ((Hash-File (Checked-Path $record.file)) -ne $record.sha256) { throw "候选变化：$($record.file)" }
            }
            $journal.state='recycling'; Save-Report $taskJournalPath $journal
            foreach ($record in $manifest.files) {
                if ($record.file -in $journal.files.file) { continue }
                $journal.files += (Recycle-One $record); Save-Report $taskJournalPath $journal
                if ($journal.files.Count % 25 -eq 0) { Write-Output "Recycled and verified $($journal.files.Count)/337" }
            }
            $dirs = (Read-Report (Join-Path $taskReportDir 'directory_manifest.json')).directories
            foreach ($relative in $dirs) {
                $dir = Checked-Path $relative
                if ((Test-Path -LiteralPath $dir) -and @(Get-ChildItem -LiteralPath $dir -Force).Count -eq 0) {
                    [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($dir,[Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,[Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin,[Microsoft.VisualBasic.FileIO.UICancelOption]::ThrowException)
                    $journal.directories += (Relative-Path $dir)
                }
            }
            $journal.state='recycled_pending_validation'
        } else {
            $validation = Read-Report (Join-Path $taskReportDir 'verification.json')
            if (-not $validation.passed) { throw '验证未通过，保留临时目录' }
            $extra = @(Tree-Files 'tmp/cleanup_verify_20261003' | ForEach-Object { Record-File $_ })
            Save-Report (Join-Path $taskReportDir 'verification_tmp_manifest.json') @{files=$extra;count=$extra.Count}
            $journal.verification_tmp_files=@()
            foreach ($record in $extra) { $journal.verification_tmp_files += (Recycle-One $record); Save-Report $taskJournalPath $journal }
            foreach ($dir in @(Get-ChildItem -LiteralPath $taskVerifyDir -Directory -Recurse -Force | Sort-Object {$_.FullName.Length} -Descending) + @((Get-Item -LiteralPath $taskVerifyDir))) {
                [void](Checked-Path (Relative-Path $dir.FullName))
                if (@(Get-ChildItem -LiteralPath $dir.FullName -Force).Count -ne 0) { throw '临时目录出现清单外文件，不回收目录' }
                [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($dir.FullName,[Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,[Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin,[Microsoft.VisualBasic.FileIO.UICancelOption]::ThrowException)
            }
            $journal.verification_tmp_recycled=$true
        }
        Save-Report $taskJournalPath $journal
    } catch {
        $journal.state='stopped';$journal.failures += @{error=$_.Exception.Message;time=(Get-Date).ToString('o')}
        Save-Report $taskJournalPath $journal; throw
    }
    Write-Output "State=$($journal.state); original_files_recycled=$($journal.files.Count)"
    exit 0
}
if ($Mode -eq 'Verify') {
    $baseline = Read-Report $taskProtectedPath
    $changed = @()
    foreach ($record in $baseline.files) {
        $full = Checked-Path $record.file
        if (-not (Test-Path -LiteralPath $full) -or (Hash-File $full) -ne $record.sha256) { $changed += $record.file }
    }
    $remaining = @($manifest.files | Where-Object { Test-Path -LiteralPath (Checked-Path $_.file) } | ForEach-Object { $_.file })
    $actualFigures = @(Tree-Files 'latex/figures' | ForEach-Object { (Relative-Path $_.FullName).Substring(6) })
    $figureDifference = @(Compare-Object $taskFormal $actualFigures)
    $result = @{passed=($changed.Count -eq 0 -and $remaining.Count -eq 0 -and $figureDifference.Count -eq 0 -and $journal.files.Count -eq 337);protected_files_checked=$baseline.count;changed_protected_files=$changed;remaining_candidates=$remaining;formal_figure_count=$actualFigures.Count;formal_figure_difference=$figureDifference;recycled_files=$journal.files.Count;bytes=($manifest.files.bytes | Measure-Object -Sum).Sum;time=(Get-Date).ToString('o')}
    Save-Report (Join-Path $taskReportDir 'preservation_check.json') $result
    if (-not $result.passed) { throw '清理后保护核查失败' }
    Write-Output "Protection passed: $($baseline.count) files unchanged; 337 recycled; formal figures=20"
}
if ($Mode -eq 'Finalize') {
    $preserved = Read-Report (Join-Path $taskReportDir 'preservation_check.json')
    $verification = Read-Report (Join-Path $taskReportDir 'verification.json')
    if (-not $preserved.passed -or -not $verification.passed -or -not $journal.verification_tmp_recycled) { throw '清理或验收尚未全部通过' }
    if ((Test-Path -LiteralPath $taskVerifyDir) -or $journal.files.Count -ne 337) { throw '临时目录未清或原始清单数量不同' }
    foreach ($record in @($journal.files) + @($journal.verification_tmp_files)) {
        if (Test-Path -LiteralPath (Checked-Path $record.file)) { throw "回收文件又出现在原处：$($record.file)" }
        if ((Hash-File $record.recycle_payload) -ne $record.sha256) { throw "可恢复内容变化：$($record.file)" }
    }
    $publication = Read-Report (Join-Path $taskRoot 'reproducibility/release_reports/publication_manifest.json')
    foreach ($record in $publication.files) {
        if ((Hash-File (Checked-Path $record.file)) -ne $record.final_sha256) { throw "正式文件变化：$($record.file)" }
    }
    $collection = Read-Report (Join-Path $taskRoot 'reproducibility/release_reports/collection_manifest.json')
    foreach ($record in $collection.files) {
        if ((Hash-File (Checked-Path $record.file)) -ne $record.sha256) { throw "汇集证据变化：$($record.file)" }
    }
    if ((& git rev-parse HEAD) -ne $manifest.head) { throw '本轮发生未授权提交' }
    $deleted = @(& git -c core.quotePath=false diff --name-only --diff-filter=D)
    $expectedDeleted = @($manifest.files | Where-Object { $_.git_tracked } | ForEach-Object { $_.file })
    if (@(Compare-Object $expectedDeleted $deleted).Count) { throw 'Git 删除范围与固化清单不一致' }
    $modified = @(& git -c core.quotePath=false diff --name-only --diff-filter=M)
    if ($modified.Count -ne 1 -or $modified[0] -ne 'README.md') { throw '出现清单外已跟踪文件修改' }
    $journal.state='complete'; Save-Report $taskJournalPath $journal
    $final = @{passed=$true;original_candidates=337;original_bytes=$preserved.bytes;original_mib=[Math]::Round($preserved.bytes/1MB,2);verification_tmp_files_recycled=$journal.verification_tmp_files.Count;all_recycle_payloads_sha256_verified=$true;protected_files_unchanged=$preserved.protected_files_checked;formal_publication_files_rechecked=$publication.files.Count;collected_evidence_rechecked=$collection.files.Count;pdf_pages_compared=48;formal_figures=20;printed_references=20;tracked_deletions=$deleted.Count;head_unchanged=$true;git_commit_or_push=$false;permanent_delete_used=$false;source_models_or_results_changed=$false;full_numerical_rerun=$false;completed_at=(Get-Date).ToString('o');limitations='仅验证清理的依赖、编译、页面等价及版本完整性；不重新认证数学证明或重跑全文数值。'}
    Save-Report (Join-Path $taskReportDir 'final_report.json') $final
    Write-Output ($final | ConvertTo-Json -Compress)
}
