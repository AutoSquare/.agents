#!/usr/bin/env pwsh
# Cursor: install Skills and user-level MCP; rules are opt-in via -ProjectPath
# Usage: cd path\to\.agents  then  powershell -ExecutionPolicy Bypass -File ".\scripts\setup-cursor-agents.ps1"
[CmdletBinding()]
param(
    [string]$ProjectPath,
    [switch]$SkipMcpInstall,
    [switch]$SkipSkillUpdate,
    [switch]$WhatIf,
    [switch]$BackupMcpJson,
    [switch]$OverwriteSkills,
    [switch]$InstallRules,
    [switch]$OverwriteRules,
    [switch]$InstallProjectRules,
    [switch]$InstallGlobalRules,
    [switch]$SkipRules,
    [switch]$NoClearScreen,
    [switch]$NoColor
)

if (-not $PSBoundParameters.ContainsKey('BackupMcpJson')) {
    $BackupMcpJson = $true
}

if ($InstallRules -or $OverwriteRules) {
    Write-Warning "Deprecated: -InstallRules / -OverwriteRules. Use -ProjectPath `"工程根路径`" instead."
}
if ($InstallProjectRules) {
    Write-Warning "Deprecated: -InstallProjectRules. Use -ProjectPath `"工程根路径`" instead."
}
if ($InstallGlobalRules) {
    Write-Warning "Deprecated: -InstallGlobalRules. Cursor does not load ~/.cursor/rules/ into Settings."
}
if ($SkipRules) {
    Write-Warning "Deprecated: -SkipRules. Rules are not installed by default; omit -ProjectPath to skip."
}
if ($OverwriteSkills) {
    Write-Warning "Deprecated: -OverwriteSkills. Managed skills are updated incrementally by default; use -SkipSkillUpdate to skip."
}

$ErrorActionPreference = "Stop"

$AgentsRoot = Split-Path -Parent $PSScriptRoot
$CursorRoot = Join-Path $env:USERPROFILE ".cursor"
$SkillsSource = Join-Path $AgentsRoot "skills"
$SkillsTarget = Join-Path $CursorRoot "skills"
$RulesSource = Join-Path (Join-Path $AgentsRoot "rules") "cursor"
$AgentsMdPath = Join-Path (Join-Path $AgentsRoot "rules") "universal\AGENTS.md"
$ManifestPath = Join-Path $AgentsRoot "manifest.json"
$McpServersRoot = Join-Path $CursorRoot "mcp-servers"
$McpJsonPath = Join-Path $CursorRoot "mcp.json"

function Test-ShowDetailLog {
    return $VerbosePreference -eq 'Continue'
}

$script:DetailLog = [System.Collections.Generic.List[string]]::new()
$script:InstallResult = [PSCustomObject]@{
    PackageId = ''
    SkillCount = 0
    ProjectRuleCount = 0
    ProjectRulesTarget = $null
    McpServerCount = 0
    McpSkipped = $false
    McpConfigUpdated = $false
    Warnings = [System.Collections.Generic.List[string]]::new()
    WhatIf = [bool]$WhatIf
    UiUxSmokePath = $null
}

function Write-DetailLog {
    param([string]$Message)
    [void]$script:DetailLog.Add($Message)
}

function Write-PhaseProgress {
    param(
        [string]$Phase,
        [int]$Current = 0,
        [int]$Total = 0
    )
    $msg = if ($Total -gt 0) { "${Phase} ${Current}/${Total}" } else { $Phase }
    $padLen = [Math]::Max(0, 64 - $msg.Length)
    Write-Host ("`r" + $msg + (' ' * $padLen)) -NoNewline
}

function Complete-PhaseProgress {
    Write-Host ""
}

function Dump-DetailLog {
    if ($script:DetailLog.Count -eq 0) {
        return
    }
    Write-SummaryText ''
    Write-SummaryText '--------------------------------------------------' -Role Divider
    Write-SummaryText '  详细日志' -Role Section
    Write-SummaryText '--------------------------------------------------' -Role Divider
    foreach ($line in $script:DetailLog) {
        Write-SummaryText $line -Role Default
    }
}

function Register-InstallWarning {
    param([string]$Message)
    Write-Warning $Message
    [void]$script:InstallResult.Warnings.Add($Message)
}

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        if ($WhatIf) {
            Write-DetailLog "[WhatIf] would create directory: $Path"
            return
        }
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-DetailLog "created directory: $Path"
    }
}

function Get-InstallManifest {
    if (-not (Test-Path $ManifestPath)) {
        throw "manifest.json not found: $ManifestPath"
    }
    $manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $install = $manifest.installManifest
    if (-not $install) {
        throw "installManifest missing in manifest.json"
    }

    $managedSkills = @($install.managedSkills)
    if ($managedSkills.Count -eq 0 -and $manifest.skillGroups) {
        $seen = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach ($group in $manifest.skillGroups.PSObject.Properties) {
            foreach ($name in @($group.Value)) {
                [void]$seen.Add([string]$name)
            }
        }
        $managedSkills = @($seen)
    }

    $managedRules = @($install.managedRules)
    if ($managedRules.Count -eq 0 -and (Test-Path $RulesSource)) {
        $managedRules = @(Get-ChildItem -Path $RulesSource -Filter "*.mdc" -File | ForEach-Object { $_.Name })
    }

    $legacyRuleFiles = @()
    if ($install.legacyRuleFilesToRemove) {
        $legacyRuleFiles = @($install.legacyRuleFilesToRemove)
    }

    return [PSCustomObject]@{
        PackageId = [string]$install.packageId
        ManagedSkills = $managedSkills
        ManagedRules = $managedRules
        LegacyRuleFilesToRemove = $legacyRuleFiles
    }
}

function Test-ManifestConsistency {
    param($InstallManifest)
    foreach ($name in $InstallManifest.ManagedSkills) {
        $src = Join-Path $SkillsSource $name
        if (-not (Test-Path $src)) {
            Register-InstallWarning "managed skill source missing: $name ($src)"
        }
    }
    if (Test-Path $RulesSource) {
        $onDisk = @(Get-ChildItem -Path $RulesSource -Filter "*.mdc" -File | ForEach-Object { $_.Name })
        foreach ($file in $onDisk) {
            if ($InstallManifest.ManagedRules -notcontains $file) {
                Register-InstallWarning "rules/cursor has unmanaged file (will not be installed): $file"
            }
        }
        foreach ($file in $InstallManifest.ManagedRules) {
            if ($onDisk -notcontains $file) {
                Register-InstallWarning "managed rule missing on disk: $file"
            }
        }
    }
}

function Install-ManagedSkills {
    param($ManagedSkills)
    if ($SkipSkillUpdate) {
        Write-DetailLog "skip skills: -SkipSkillUpdate"
        return 0
    }
    Ensure-Directory $SkillsTarget
    $total = $ManagedSkills.Count
    $count = 0
    $index = 0
    foreach ($name in $ManagedSkills) {
        $index++
        Write-PhaseProgress -Phase 'Skills' -Current $index -Total $total
        $src = Join-Path $SkillsSource $name
        $dst = Join-Path $SkillsTarget $name
        if (-not (Test-Path $src)) {
            Register-InstallWarning "skip skill (missing source): $name"
            continue
        }
        if ($WhatIf) {
            Write-DetailLog "[WhatIf] would update skill: $name"
            $count++
            continue
        }
        if (Test-Path $dst) {
            Remove-Item $dst -Recurse -Force
        }
        Copy-Item $src $dst -Recurse -Force
        Write-DetailLog "updated skill: $name"
        $count++
    }
    Complete-PhaseProgress
    if (-not $WhatIf) {
        $pptMakerTarget = Join-Path $SkillsTarget "ppt-maker"
        if (Test-Path $pptMakerTarget) {
            $kitOk = Test-Path (Join-Path $pptMakerTarget "kit-template")
            $scaffoldOk = Test-Path (Join-Path $pptMakerTarget "scripts\scaffold.mjs")
            if ($kitOk -and $scaffoldOk) {
                Write-DetailLog "ppt-maker: kit-template and scaffold.mjs OK"
            } else {
                Register-InstallWarning "ppt-maker: missing kit-template or scripts/scaffold.mjs — re-run sync-to-agents from sandbox"
            }
            Write-DetailLog "ppt-maker: requires Node.js 18+; style customization requires ui-ux-pro-max + Python 3"
        }
    }
    return $count
}

function Install-ManagedRulesToTarget {
    param(
        [string]$TargetDir,
        [string[]]$ManagedRules,
        [string[]]$LegacyRuleFiles,
        [string]$Label
    )
    if (-not (Test-Path $RulesSource)) {
        Write-DetailLog "skip rules ($Label): source not found ($RulesSource)"
        return 0
    }
    Ensure-Directory $TargetDir
    $total = $ManagedRules.Count
    $count = 0
    $index = 0
    foreach ($legacy in $LegacyRuleFiles) {
        $legacyPath = Join-Path $TargetDir $legacy
        if (Test-Path $legacyPath) {
            if ($WhatIf) {
                Write-DetailLog "[WhatIf] would remove legacy rule ($Label): $legacy"
            } else {
                Remove-Item $legacyPath -Force
                Write-DetailLog "removed legacy rule ($Label): $legacy"
            }
        }
    }
    foreach ($file in $ManagedRules) {
        $index++
        Write-PhaseProgress -Phase "Rules ($Label)" -Current $index -Total $total
        $src = Join-Path $RulesSource $file
        $dst = Join-Path $TargetDir $file
        if (-not (Test-Path $src)) {
            Register-InstallWarning "skip rule (missing source): $file"
            continue
        }
        if ($WhatIf) {
            Write-DetailLog "[WhatIf] would update rule ($Label): $file"
        } else {
            Copy-Item $src $dst -Force
            Write-DetailLog "updated rule ($Label): $file"
        }
        $count++
    }
    Complete-PhaseProgress
    if ($count -gt 0) {
        Write-DetailLog "rules target ($Label): $TargetDir"
    }
    return $count
}

function Resolve-ProjectRulesTarget {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw "ProjectPath is empty."
    }
    if (-not (Test-Path $Path)) {
        throw "ProjectPath not found: $Path"
    }
    $resolved = (Resolve-Path $Path).Path
    return Join-Path $resolved ".cursor\rules"
}

function Format-AgentsMdSectionTitle {
    param([string]$Title)
    $trimmed = $Title.Trim()
    if ($trimmed -match '^\d+\.\s*(.+)$') {
        return $Matches[1].Trim()
    }
    return $trimmed
}

function Get-AgentsMdUserRuleSections {
    $empty = [PSCustomObject]@{
        Count = 0
        Titles = @()
        SkippedTitle = $null
    }
    if (-not (Test-Path $AgentsMdPath)) {
        return $empty
    }
    $allTitles = [System.Collections.Generic.List[string]]::new()
    $lines = Get-Content $AgentsMdPath -Encoding UTF8
    foreach ($line in $lines) {
        if ($line -match '^## (.+)$') {
            [void]$allTitles.Add($Matches[1].Trim())
        }
    }
    if ($allTitles.Count -eq 0) {
        return $empty
    }
    $skippedTitle = Format-AgentsMdSectionTitle -Title $allTitles[0]
    if ($allTitles.Count -le 1) {
        return [PSCustomObject]@{
            Count = 0
            Titles = @()
            SkippedTitle = $skippedTitle
        }
    }
    $userRuleTitles = [System.Collections.Generic.List[string]]::new()
    for ($i = 1; $i -lt $allTitles.Count; $i++) {
        [void]$userRuleTitles.Add((Format-AgentsMdSectionTitle -Title $allTitles[$i]))
    }
    return [PSCustomObject]@{
        Count = $userRuleTitles.Count
        Titles = @($userRuleTitles)
        SkippedTitle = $skippedTitle
    }
}

function Test-UseConsoleColor {
    if ($NoColor) {
        return $false
    }
    try {
        return -not [Console]::IsOutputRedirected
    }
    catch {
        return $true
    }
}

function Get-SummaryForegroundColor {
    param(
        [ValidateSet('Title', 'Divider', 'Section', 'Label', 'Value', 'Step', 'ListItem', 'Muted', 'Command', 'Warning', 'Default')]
        [string]$Role
    )
    switch ($Role) {
        'Title' { return 'Cyan' }
        'Divider' { return 'DarkGray' }
        'Section' { return 'Yellow' }
        'Label' { return 'Gray' }
        'Value' { return 'Green' }
        'Step' { return 'White' }
        'ListItem' { return 'Cyan' }
        'Muted' { return 'DarkGray' }
        'Command' { return 'DarkCyan' }
        'Warning' { return 'Yellow' }
        default { return $null }
    }
}

function Write-SummaryText {
    param(
        [string]$Text,
        [string]$Role = 'Default',
        [switch]$NoNewline
    )
    $hostParams = @{}
    if ($NoNewline) {
        $hostParams['NoNewline'] = $true
    }
    if (Test-UseConsoleColor) {
        $color = Get-SummaryForegroundColor -Role $Role
        if ($color) {
            $hostParams['ForegroundColor'] = $color
        }
    }
    Write-Host $Text @hostParams
}

function Write-SummaryLine {
    param(
        [string]$Label,
        [string]$Value,
        [int]$LabelWidth = 10
    )
    $padding = ' ' * [Math]::Max(1, $LabelWidth - $Label.Length)
    $linePrefix = '  ' + $Label + $padding
    if (Test-UseConsoleColor) {
        Write-Host $linePrefix -NoNewline -ForegroundColor Gray
        Write-Host $Value -ForegroundColor Green
    } else {
        Write-Host ($linePrefix + $Value)
    }
}

function Write-SummaryWarningLine {
    param([string]$Message)
    if (Test-UseConsoleColor) {
        Write-Host '  ' -NoNewline
        Write-Host '! ' -NoNewline -ForegroundColor Red
        Write-Host $Message -ForegroundColor Yellow
    } else {
        Write-Host ('  ! ' + $Message)
    }
}

function Show-InstallSummary {
    $r = $script:InstallResult
    $shouldClear = (-not $WhatIf) -and (-not $NoClearScreen) -and (-not (Test-ShowDetailLog))
    if ($shouldClear) {
        Clear-Host
    }

    $divider = '=================================================='
    $section = '--------------------------------------------------'
    if ($WhatIf) {
        Write-SummaryText $divider -Role Divider
        Write-SummaryText '  Cursor Agents Setup 预览（WhatIf）' -Role Title
        Write-SummaryText $divider -Role Divider
        Write-SummaryText '' -Role Default
        $skillLabel = if ($SkipSkillUpdate) { '跳过' } else { "$($r.SkillCount) 将更新" }
        Write-SummaryLine -Label '包版本' -Value $r.PackageId
        Write-SummaryLine -Label 'Skills' -Value ($skillLabel + '  ->  ~/.cursor/skills/')
        if ($r.McpSkipped) {
            Write-SummaryLine -Label 'MCP' -Value '跳过（-SkipMcpInstall）'
        } else {
            Write-SummaryLine -Label 'MCP' -Value '将更新配置  ->  ~/.cursor/mcp.json'
        }
        if ($r.ProjectRuleCount -gt 0) {
            Write-SummaryLine -Label 'Rules' -Value ("$($r.ProjectRuleCount) 将安装  ->  " + $r.ProjectRulesTarget)
        } else {
            Write-SummaryLine -Label 'Rules' -Value '未安装（默认）'
        }
        $whatIfUserRules = Get-AgentsMdUserRuleSections
        if ($whatIfUserRules.Count -gt 0) {
            $whatIfHint = "正式安装后需手动录入 $($whatIfUserRules.Count) 条"
            if ($whatIfUserRules.SkippedTitle) {
                $whatIfHint += "（首节「$($whatIfUserRules.SkippedTitle)」已排除）"
            }
            Write-SummaryLine -Label 'User Rules' -Value $whatIfHint
        }
        Write-SummaryText '' -Role Default
        Write-SummaryText $section -Role Divider
        Write-SummaryText '  说明' -Role Section
        Write-SummaryText $section -Role Divider
        Write-SummaryText '  以上为预览，未写入磁盘。去掉 -WhatIf 后执行正式安装。' -Role Muted
        Write-SummaryText $divider -Role Divider
        return
    }

    Write-SummaryText $divider -Role Divider
    Write-SummaryText '  Cursor Agents Setup 完成' -Role Title
    Write-SummaryText $divider -Role Divider
    Write-SummaryText '' -Role Default
    Write-SummaryLine -Label '包版本' -Value $r.PackageId
    if ($SkipSkillUpdate) {
        Write-SummaryLine -Label 'Skills' -Value '跳过（-SkipSkillUpdate）'
    } else {
        Write-SummaryLine -Label 'Skills' -Value ("$($r.SkillCount) 已更新  ->  ~/.cursor/skills/")
    }
    if ($r.McpSkipped) {
        Write-SummaryLine -Label 'MCP' -Value '跳过（-SkipMcpInstall）'
    } elseif ($r.McpConfigUpdated) {
        Write-SummaryLine -Label 'MCP' -Value ("已配置（$($r.McpServerCount) 个服务）  ->  ~/.cursor/mcp.json")
    } else {
        Write-SummaryLine -Label 'MCP' -Value '未更新'
    }
    if ($r.ProjectRuleCount -gt 0) {
        Write-SummaryLine -Label 'Rules' -Value ("$($r.ProjectRuleCount) 已安装  ->  " + $r.ProjectRulesTarget)
    } else {
        Write-SummaryLine -Label 'Rules' -Value '未安装（默认）'
    }
    $userRules = Get-AgentsMdUserRuleSections
    if ($userRules.Count -gt 0) {
        Write-SummaryLine -Label 'User Rules' -Value ("需手动 $($userRules.Count) 条  ->  rules/universal/AGENTS.md")
    }

    if ($r.Warnings.Count -gt 0) {
        Write-SummaryText '' -Role Default
        Write-SummaryText $section -Role Divider
        Write-SummaryText '  警告' -Role Section
        Write-SummaryText $section -Role Divider
        $showCount = [Math]::Min(5, $r.Warnings.Count)
        for ($i = 0; $i -lt $showCount; $i++) {
            Write-SummaryWarningLine -Message $r.Warnings[$i]
        }
        $remaining = $r.Warnings.Count - $showCount
        if ($remaining -gt 0) {
            Write-SummaryText ("  ... 另有 $remaining 条，见 -Verbose") -Role Muted
        }
    }

    Write-SummaryText '' -Role Default
    Write-SummaryText $section -Role Divider
    Write-SummaryText '  下一步' -Role Section
    Write-SummaryText $section -Role Divider
    Write-SummaryText '  1. 重启 Cursor' -Role Step
    Write-SummaryText '  2. Settings -> Tools and MCP  检查/启用服务' -Role Step
    if ($userRules.Count -eq 0) {
        Register-InstallWarning "AGENTS.md not found or has fewer than 2 section headings: $AgentsMdPath"
        Write-SummaryText ('  3. Settings -> Rules -> User  按 AGENTS.md 逐条录入（参照: ' + $AgentsMdPath + '）') -Role Step
    } else {
        Write-SummaryText ("  3. Settings -> Rules -> User  按 AGENTS.md 逐条录入（共 $($userRules.Count) 条）：") -Role Step
        foreach ($title in $userRules.Titles) {
            Write-SummaryText ('     ' + $title) -Role ListItem
        }
        Write-SummaryText '' -Role Default
        if ($userRules.SkippedTitle) {
            Write-SummaryText ("     首节已排除，无需录入：「$($userRules.SkippedTitle)」") -Role Muted
        }
    }
    Write-SummaryText '' -Role Default
    Write-SummaryText '  勿整份粘贴 AGENTS.md；勿用 Include third-party 导入。' -Role Muted
    if ($r.ProjectRuleCount -gt 0) {
        Write-SummaryText '  Project 规则已在 Settings -> Rules -> Project 可见（打开对应工程时）。' -Role Muted
        Write-SummaryText '  User Rules 仍须手动录入（跨项目生效）。' -Role Muted
    }

    Write-SummaryText '' -Role Default
    Write-SummaryText $section -Role Divider
    Write-SummaryText '  可选' -Role Section
    Write-SummaryText $section -Role Divider
    if ($r.ProjectRuleCount -eq 0) {
        Write-SummaryText '  Project Rules:' -Role Step
        Write-SummaryText '    .\scripts\setup-cursor-agents.ps1 -ProjectPath "D:\path\to\project"' -Role Command
        Write-SummaryText '' -Role Default
    }
    if ($r.UiUxSmokePath) {
        Write-SummaryText '  UI/UX 冒烟（可选）:' -Role Step
        Write-SummaryText ('    python "' + $r.UiUxSmokePath + '" fintech --design-system -n 1') -Role Command
        Write-SummaryText '' -Role Default
    }
    Write-SummaryText $divider -Role Divider
}

function Ensure-McpRepo {
    param(
        [string]$Name,
        [string]$Url
    )
    $target = Join-Path $McpServersRoot $Name
    if (Test-Path $target) {
        Write-DetailLog "MCP repo exists: $Name"
        return $target
    }

    $bundled = Join-Path (Join-Path $AgentsRoot "mcp-servers-src") $Name
    if (Test-Path $bundled) {
        Copy-Item $bundled $target -Recurse -Force
        Write-DetailLog "copied bundled MCP source: $Name"
        return $target
    }

    Assert-Command "git"
    Write-DetailLog "git clone $Url -> $target"
    git clone $Url $target
    return $target
}

function Install-AcademicResearchMcp {
    Write-PhaseProgress -Phase 'MCP academic-research'
    Assert-Command "python"
    $repo = Ensure-McpRepo "academic-research-mcp" "https://github.com/alisoroushmd/academic-research-mcp.git"
    Push-Location $repo
    try {
        if (-not (Test-Path ".venv")) {
            python -m venv ".venv"
            Write-DetailLog "created venv: academic-research-mcp"
        }
        & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip 2>&1 | ForEach-Object { Write-DetailLog $_ }
        & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt 2>&1 | ForEach-Object { Write-DetailLog $_ }
    }
    finally {
        Pop-Location
    }
    Complete-PhaseProgress
}

function Install-ZoteroMcp {
    Write-PhaseProgress -Phase 'MCP zotero'
    Assert-Command "npm"
    $repo = Ensure-McpRepo "zotero-mcp" "https://github.com/Xpropel/zotero-mcp.git"
    Push-Location $repo
    try {
        npm install 2>&1 | ForEach-Object { Write-DetailLog $_ }
        npm run build 2>&1 | ForEach-Object { Write-DetailLog $_ }
    }
    finally {
        Pop-Location
    }
    Complete-PhaseProgress
}

function Install-CampusNetMcp {
    Write-PhaseProgress -Phase 'MCP campus-net'
    Assert-Command "python"
    $bundled = Join-Path (Join-Path $AgentsRoot "mcp-servers-src") "campus-net-mcp"
    if (-not (Test-Path $bundled)) {
        throw "Bundled MCP not found: $bundled"
    }
    $dest = Join-Path $McpServersRoot "campus-net-mcp"
    if (-not (Test-Path $dest)) {
        Copy-Item $bundled $dest -Recurse -Force
        Write-DetailLog "copied bundled MCP source: campus-net-mcp"
    }
    Push-Location $dest
    try {
        if (-not (Test-Path ".venv")) {
            python -m venv ".venv"
            Write-DetailLog "created venv: campus-net-mcp"
        }
        & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip 2>&1 | ForEach-Object { Write-DetailLog $_ }
        & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt 2>&1 | ForEach-Object { Write-DetailLog $_ }
        Write-DetailLog "Installing Chromium for Playwright (first run may download binaries) ..."
        & ".\.venv\Scripts\python.exe" -m playwright install chromium 2>&1 | ForEach-Object { Write-DetailLog $_ }
    }
    finally {
        Pop-Location
    }
    Complete-PhaseProgress
}

function Install-DeckBuilderMcp {
    Write-PhaseProgress -Phase 'MCP deck-builder'
    Assert-Command "npm"
    $repo = Ensure-McpRepo "deck-builder" "https://github.com/toontube/deck-builder.git"
    Push-Location $repo
    try {
        npm install 2>&1 | ForEach-Object { Write-DetailLog $_ }
        npm run build 2>&1 | ForEach-Object { Write-DetailLog $_ }
    }
    finally {
        Pop-Location
    }
    Complete-PhaseProgress
}

function Set-McpJson {
    Write-PhaseProgress -Phase 'MCP config'
    if ($WhatIf) {
        Write-DetailLog "[WhatIf] would update MCP config: $McpJsonPath"
        Complete-PhaseProgress
        return 0
    }
    Ensure-Directory $CursorRoot
    if ((Test-Path $McpJsonPath) -and $BackupMcpJson) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        Copy-Item $McpJsonPath "$McpJsonPath.bak-$timestamp" -Force
        Write-DetailLog "backed up MCP config: $McpJsonPath.bak-$timestamp"
    }

    $existing = [ordered]@{ mcpServers = [ordered]@{} }
    if (Test-Path $McpJsonPath) {
        $raw = Get-Content $McpJsonPath -Raw
        if ($raw.Trim()) {
            $parsed = $raw | ConvertFrom-Json
            if ($parsed.mcpServers) {
                $existing.mcpServers = [ordered]@{}
                $parsed.mcpServers.PSObject.Properties | ForEach-Object {
                    $existing.mcpServers[$_.Name] = $_.Value
                }
            }
        }
    }

    foreach ($purge in @("brave-search")) {
        if ($existing.mcpServers.Keys -contains $purge) {
            [void]$existing.mcpServers.Remove($purge)
        }
    }
    $academicPython = Join-Path $McpServersRoot "academic-research-mcp\.venv\Scripts\python.exe"
    $academicServer = Join-Path $McpServersRoot "academic-research-mcp\server.py"
    $zoteroServer = Join-Path $McpServersRoot "zotero-mcp\dist\index.js"
    $deckBuilderServer = Join-Path $McpServersRoot "deck-builder\build\index.js"
    $campusPython = Join-Path $McpServersRoot "campus-net-mcp\.venv\Scripts\python.exe"
    $campusServer = Join-Path $McpServersRoot "campus-net-mcp\server.py"

    $existing.mcpServers["academic-research"] = [ordered]@{
        command = $academicPython
        args = @($academicServer)
        env = [ordered]@{
            S2_API_KEY = '${env:S2_API_KEY}'
            OPENALEX_EMAIL = '${env:OPENALEX_EMAIL}'
            CROSSREF_EMAIL = '${env:CROSSREF_EMAIL}'
            NCBI_API_KEY = '${env:NCBI_API_KEY}'
        }
    }
    $existing.mcpServers["zotero"] = [ordered]@{
        command = "node"
        args = @($zoteroServer)
    }
    $existing.mcpServers["deck-builder"] = [ordered]@{
        command = "node"
        args = @($deckBuilderServer)
    }
    $existing.mcpServers["ppt-markdown"] = [ordered]@{
        command = "npx"
        args = @("-y", "@botrun/mcp-ppt-generator")
    }
    $existing.mcpServers["campus-net"] = [ordered]@{
        command = $campusPython
        args = @($campusServer)
        env = [ordered]@{
            CAMPUS_USERNAME = '${env:CAMPUS_USERNAME}'
            CAMPUS_PASSWORD = '${env:CAMPUS_PASSWORD}'
            OPENALEX_EMAIL = '${env:OPENALEX_EMAIL}'
            CROSSREF_EMAIL = '${env:CROSSREF_EMAIL}'
            CAMPUS_OUTPUT_DIR = '${env:CAMPUS_OUTPUT_DIR}'
        }
    }

    $existing | ConvertTo-Json -Depth 20 | Set-Content $McpJsonPath -Encoding UTF8
    Write-DetailLog "updated MCP config: $McpJsonPath"
    Complete-PhaseProgress
    return @($existing.mcpServers.Keys).Count
}

try {
    $installManifest = Get-InstallManifest
    $script:InstallResult.PackageId = $installManifest.PackageId
    Write-PhaseProgress -Phase ('install package: ' + $installManifest.PackageId)
    Complete-PhaseProgress
    Write-DetailLog "install package: $($installManifest.PackageId)"

    Test-ManifestConsistency -InstallManifest $installManifest

    Ensure-Directory $CursorRoot
    Ensure-Directory $McpServersRoot

    if (-not $WhatIf) {
        Assert-Command "python"
        if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) {
            Register-InstallWarning "node not found: brand/design-system/ui-styling scripts may not run until Node.js is installed."
        }
    }

    $script:InstallResult.SkillCount = Install-ManagedSkills -ManagedSkills $installManifest.ManagedSkills

    if ($ProjectPath) {
        $projectRulesTarget = Resolve-ProjectRulesTarget -Path $ProjectPath
        $script:InstallResult.ProjectRulesTarget = $projectRulesTarget
        Ensure-Directory (Split-Path $projectRulesTarget -Parent)
        $script:InstallResult.ProjectRuleCount = Install-ManagedRulesToTarget `
            -TargetDir $projectRulesTarget `
            -ManagedRules $installManifest.ManagedRules `
            -LegacyRuleFiles $installManifest.LegacyRuleFilesToRemove `
            -Label "project"
    }

    if (-not $SkipMcpInstall -and -not $WhatIf) {
        Install-AcademicResearchMcp
        Install-ZoteroMcp
        Install-DeckBuilderMcp
        Install-CampusNetMcp
    }
    elseif ($SkipMcpInstall) {
        $script:InstallResult.McpSkipped = $true
        Write-DetailLog "skip MCP install: -SkipMcpInstall"
    }

    $mcpCount = Set-McpJson
    if ($mcpCount -gt 0) {
        $script:InstallResult.McpServerCount = $mcpCount
        $script:InstallResult.McpConfigUpdated = $true
    }

    if (-not $WhatIf) {
        $uiUxSmoke = Join-Path $SkillsTarget "ui-ux-pro-max\scripts\search.py"
        if (Test-Path $uiUxSmoke) {
            $script:InstallResult.UiUxSmokePath = $uiUxSmoke
        }
    }

    Show-InstallSummary
    if (Test-ShowDetailLog) {
        Dump-DetailLog
    }
}
catch {
    Complete-PhaseProgress
    Write-Host ""
    Write-Host '安装失败。' -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Dump-DetailLog
    throw
}
