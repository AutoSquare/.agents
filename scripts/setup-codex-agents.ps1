#!/usr/bin/env pwsh
# Codex: install managed Skills, global rules, and MCP servers.
# Usage: cd path\to\.agents  then  powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1"
[CmdletBinding()]
param(
    [string]$CodexHome,
    [switch]$SkipMcpInstall,
    [switch]$SkipSkillUpdate,
    [switch]$SkipRulesUpdate,
    [switch]$WhatIf,
    [switch]$NoClearScreen,
    [switch]$NoColor
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    $CodexHome = Join-Path $env:USERPROFILE ".codex"
}

$AgentsRoot = Split-Path -Parent $PSScriptRoot
$CodexHome = [System.IO.Path]::GetFullPath($CodexHome)
$SkillsSource = Join-Path $AgentsRoot "skills"
$SkillsTarget = Join-Path $CodexHome "skills"
$RulesSource = Join-Path (Join-Path $AgentsRoot "rules") "codex-global"
$RulesTarget = Join-Path $CodexHome "agent-rules"
$AgentsMdSource = Join-Path $RulesSource "AGENTS.md"
$AgentsMdTarget = Join-Path $CodexHome "AGENTS.md"
$ManifestPath = Join-Path $AgentsRoot "manifest.json"
$McpSourceRoot = Join-Path $AgentsRoot "mcp-servers-src"
$McpTargetRoot = Join-Path $CodexHome "mcp-servers"

$script:DetailLog = [System.Collections.Generic.List[string]]::new()
$script:InstallResult = [PSCustomObject]@{
    PackageId = ""
    CodexHome = $CodexHome
    SkillCount = 0
    RuleCount = 0
    McpSourceCount = 0
    McpRegisteredCount = 0
    McpSkipped = [bool]$SkipMcpInstall
    Warnings = [System.Collections.Generic.List[string]]::new()
    WhatIf = [bool]$WhatIf
}

function Write-DetailLog {
    param([string]$Message)
    [void]$script:DetailLog.Add($Message)
}

function Register-InstallWarning {
    param([string]$Message)
    Write-Warning $Message
    [void]$script:InstallResult.Warnings.Add($Message)
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

function Write-SummaryText {
    param(
        [string]$Text,
        [string]$Color = $null
    )
    if ((Test-UseConsoleColor) -and $Color) {
        Write-Host $Text -ForegroundColor $Color
    } else {
        Write-Host $Text
    }
}

function Write-SummaryLine {
    param(
        [string]$Label,
        [string]$Value
    )
    Write-SummaryText ("  {0,-12}{1}" -f $Label, $Value)
}

function Write-PhaseProgress {
    param(
        [string]$Phase,
        [int]$Current = 0,
        [int]$Total = 0
    )
    $msg = if ($Total -gt 0) { "${Phase} ${Current}/${Total}" } else { $Phase }
    $padLen = [Math]::Max(0, 64 - $msg.Length)
    Write-Host ("`r" + $msg + (" " * $padLen)) -NoNewline
}

function Complete-PhaseProgress {
    Write-Host ""
}

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Ensure-Directory {
    param([string]$Path)
    if (Test-Path $Path) {
        return
    }
    if ($WhatIf) {
        Write-DetailLog "[WhatIf] would create directory: $Path"
        return
    }
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    Write-DetailLog "created directory: $Path"
}

function Resolve-ChildPath {
    param(
        [string]$Parent,
        [string]$Child
    )
    if ($Child -match '[\\/]' -or $Child -match '^\.' -or [System.IO.Path]::IsPathRooted($Child)) {
        throw "Unsafe managed name: $Child"
    }
    return Join-Path $Parent $Child
}

function Assert-PathInside {
    param(
        [string]$Path,
        [string]$Parent
    )
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $fullParent = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\', '/')
    if (-not $fullPath.StartsWith($fullParent + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify path outside managed root: $fullPath"
    }
}

function Copy-ManagedDirectory {
    param(
        [string]$Source,
        [string]$Target,
        [string]$ManagedRoot,
        [string]$Label
    )
    if (-not (Test-Path $Source)) {
        Register-InstallWarning "managed source missing: $Label ($Source)"
        return $false
    }
    Assert-PathInside -Path $Target -Parent $ManagedRoot
    if ($WhatIf) {
        Write-DetailLog "[WhatIf] would refresh managed directory: $Label -> $Target"
        return $true
    }
    if (Test-Path $Target) {
        Remove-Item -LiteralPath $Target -Recurse -Force
    }
    Copy-Item -LiteralPath $Source -Destination $Target -Recurse -Force
    Write-DetailLog "refreshed managed directory: $Label"
    return $true
}

function Remove-Utf8BomIfPresent {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return
    }
    if ($WhatIf) {
        Write-DetailLog "[WhatIf] would normalize UTF-8 BOM if present: $Path"
        return
    }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $normalized = New-Object byte[] ($bytes.Length - 3)
        [Array]::Copy($bytes, 3, $normalized, 0, $normalized.Length)
        [System.IO.File]::WriteAllBytes($Path, $normalized)
        Write-DetailLog "removed UTF-8 BOM: $Path"
    }
}

function Get-CodexInstallManifest {
    if (-not (Test-Path $ManifestPath)) {
        throw "manifest.json not found: $ManifestPath"
    }
    $manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $install = $manifest.codexInstallManifest
    if (-not $install) {
        throw "codexInstallManifest missing in manifest.json"
    }
    return [PSCustomObject]@{
        PackageId = [string]$install.packageId
        ManagedSkills = @($install.managedSkills)
        ManagedRules = @($install.managedRules)
        ManagedMcpServers = @($install.managedMcpServers)
    }
}

function Install-CodexRules {
    param($InstallManifest)
    if ($SkipRulesUpdate) {
        Write-DetailLog "skip rules: -SkipRulesUpdate"
        return 0
    }
    if (-not (Test-Path $AgentsMdSource)) {
        throw "Codex AGENTS.md source missing: $AgentsMdSource"
    }
    Ensure-Directory $CodexHome
    Ensure-Directory $RulesTarget
    $count = 0
    if ($WhatIf) {
        Write-DetailLog "[WhatIf] would update AGENTS.md: $AgentsMdTarget"
    } else {
        if (Test-Path $AgentsMdTarget) {
            $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
            Copy-Item -LiteralPath $AgentsMdTarget -Destination "$AgentsMdTarget.bak-$timestamp" -Force
            Write-DetailLog "backed up AGENTS.md: $AgentsMdTarget.bak-$timestamp"
        }
        Copy-Item -LiteralPath $AgentsMdSource -Destination $AgentsMdTarget -Force
        Write-DetailLog "updated AGENTS.md: $AgentsMdTarget"
    }
    $count++

    $total = $InstallManifest.ManagedRules.Count
    $index = 0
    foreach ($file in $InstallManifest.ManagedRules) {
        $index++
        Write-PhaseProgress -Phase "Rules" -Current $index -Total $total
        $src = Join-Path (Join-Path $RulesSource "agent-rules") $file
        $dst = Resolve-ChildPath -Parent $RulesTarget -Child $file
        if (-not (Test-Path $src)) {
            Register-InstallWarning "managed rule source missing: $file"
            continue
        }
        if ($WhatIf) {
            Write-DetailLog "[WhatIf] would update managed rule: $file"
        } else {
            Copy-Item -LiteralPath $src -Destination $dst -Force
            Write-DetailLog "updated managed rule: $file"
        }
        $count++
    }
    Complete-PhaseProgress
    return $count
}

function Install-CodexSkills {
    param($ManagedSkills)
    if ($SkipSkillUpdate) {
        Write-DetailLog "skip skills: -SkipSkillUpdate"
        return 0
    }
    Ensure-Directory $SkillsTarget
    $count = 0
    $total = $ManagedSkills.Count
    $index = 0
    foreach ($name in $ManagedSkills) {
        $index++
        Write-PhaseProgress -Phase "Skills" -Current $index -Total $total
        $src = Resolve-ChildPath -Parent $SkillsSource -Child $name
        $dst = Resolve-ChildPath -Parent $SkillsTarget -Child $name
        if (Copy-ManagedDirectory -Source $src -Target $dst -ManagedRoot $SkillsTarget -Label "skill:$name") {
            Remove-Utf8BomIfPresent -Path (Join-Path $dst "SKILL.md")
            $count++
        }
    }
    Complete-PhaseProgress
    return $count
}

function Install-PythonMcp {
    param(
        [string]$Name,
        [string]$RepoPath
    )
    Push-Location $RepoPath
    try {
        if (-not (Test-Path ".venv")) {
            python -m venv ".venv"
            Write-DetailLog "created venv: $Name"
        }
        & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip 2>&1 | ForEach-Object { Write-DetailLog $_ }
        & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt 2>&1 | ForEach-Object { Write-DetailLog $_ }
        if ($Name -eq "campus-net-mcp") {
            & ".\.venv\Scripts\python.exe" -m playwright install chromium 2>&1 | ForEach-Object { Write-DetailLog $_ }
        }
    }
    finally {
        Pop-Location
    }
}

function Install-NodeMcp {
    param(
        [string]$Name,
        [string]$RepoPath
    )
    Push-Location $RepoPath
    try {
        npm install 2>&1 | ForEach-Object { Write-DetailLog $_ }
        npm run build 2>&1 | ForEach-Object { Write-DetailLog $_ }
    }
    finally {
        Pop-Location
    }
}

function Install-CodexMcpSources {
    param($ManagedMcpServers)
    if ($SkipMcpInstall) {
        Write-DetailLog "skip MCP install: -SkipMcpInstall"
        return 0
    }
    if (-not $WhatIf) {
        Assert-Command "python"
        Assert-Command "node"
        Assert-Command "npm"
    }
    Ensure-Directory $McpTargetRoot
    $count = 0
    $total = $ManagedMcpServers.Count
    $index = 0
    foreach ($server in $ManagedMcpServers) {
        $index++
        $name = [string]$server.sourceDir
        if ([string]$server.kind -eq "npx") {
            Write-DetailLog "skip local source install for npx MCP: $($server.name)"
            continue
        }
        if ([string]::IsNullOrWhiteSpace($name)) {
            Register-InstallWarning "managed MCP missing sourceDir"
            continue
        }
        Write-PhaseProgress -Phase "MCP source" -Current $index -Total $total
        $src = Resolve-ChildPath -Parent $McpSourceRoot -Child $name
        $dst = Resolve-ChildPath -Parent $McpTargetRoot -Child $name
        if (-not (Copy-ManagedDirectory -Source $src -Target $dst -ManagedRoot $McpTargetRoot -Label "mcp:$name")) {
            continue
        }
        if (-not $WhatIf) {
            switch ([string]$server.kind) {
                "python" { Install-PythonMcp -Name $name -RepoPath $dst }
                "node" { Install-NodeMcp -Name $name -RepoPath $dst }
                "npx" { Write-DetailLog "npx MCP has no local source build: $name" }
                default { Register-InstallWarning "unknown MCP kind for ${name}: $($server.kind)" }
            }
        }
        $count++
    }
    Complete-PhaseProgress
    return $count
}

function Invoke-CodexMcpRemove {
    param([string]$Name)
    $output = & codex mcp remove $Name 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-DetailLog "codex mcp remove skipped ($Name): $output"
    } else {
        Write-DetailLog "removed managed MCP registration: $Name"
    }
}

function Invoke-CodexMcpAdd {
    param(
        [string]$Name,
        [string[]]$Command,
        [string[]]$Env = @()
    )
    $codexArgs = @("mcp", "add")
    foreach ($pair in $Env) {
        $codexArgs += @("--env", $pair)
    }
    $codexArgs += @($Name, "--")
    $codexArgs += $Command
    & codex @codexArgs 2>&1 | ForEach-Object { Write-DetailLog $_ }
    if ($LASTEXITCODE -ne 0) {
        throw "codex mcp add failed: $Name"
    }
    Write-DetailLog "registered managed MCP: $Name"
}

function Register-CodexMcpServers {
    param($ManagedMcpServers)
    Assert-Command "codex"
    $count = 0
    foreach ($server in $ManagedMcpServers) {
        $mcpName = [string]$server.name
        if ([string]::IsNullOrWhiteSpace($mcpName)) {
            continue
        }
        if ($WhatIf) {
            Write-DetailLog "[WhatIf] would refresh MCP registration: $mcpName"
            $count++
            continue
        }
        Invoke-CodexMcpRemove -Name $mcpName
        switch ($mcpName) {
            "academic-research" {
                $python = Join-Path $McpTargetRoot "academic-research-mcp\.venv\Scripts\python.exe"
                $entry = Join-Path $McpTargetRoot "academic-research-mcp\server.py"
                Invoke-CodexMcpAdd -Name $mcpName -Command @($python, $entry)
            }
            "zotero" {
                $entry = Join-Path $McpTargetRoot "zotero-mcp\dist\index.js"
                Invoke-CodexMcpAdd -Name $mcpName -Command @("node", $entry)
            }
            "deck-builder" {
                $entry = Join-Path $McpTargetRoot "deck-builder\build\index.js"
                Invoke-CodexMcpAdd -Name $mcpName -Command @("node", $entry)
            }
            "ppt-markdown" {
                Invoke-CodexMcpAdd -Name $mcpName -Command @("npx", "-y", "@botrun/mcp-ppt-generator")
            }
            "campus-net" {
                $python = Join-Path $McpTargetRoot "campus-net-mcp\.venv\Scripts\python.exe"
                $entry = Join-Path $McpTargetRoot "campus-net-mcp\server.py"
                $campusRoot = Join-Path $CodexHome "campus-net"
                Invoke-CodexMcpAdd -Name $mcpName -Command @($python, $entry) -Env @("CAMPNET_USER_ROOT=$campusRoot")
            }
            default {
                Register-InstallWarning "skip unknown managed MCP registration: $mcpName"
                continue
            }
        }
        $count++
    }
    return $count
}

function Show-InstallSummary {
    $r = $script:InstallResult
    if ((-not $WhatIf) -and (-not $NoClearScreen)) {
        Clear-Host
    }
    $title = if ($WhatIf) { "Codex Agents Setup Preview (WhatIf)" } else { "Codex Agents Setup Complete" }
    Write-SummaryText "==================================================" "DarkGray"
    Write-SummaryText ("  " + $title) "Cyan"
    Write-SummaryText "==================================================" "DarkGray"
    Write-SummaryLine -Label "Package" -Value $r.PackageId
    Write-SummaryLine -Label "CodexHome" -Value $r.CodexHome
    $rulesStatus = if ($SkipRulesUpdate) { "skipped" } else { "$($r.RuleCount) updated" }
    $skillsStatus = if ($SkipSkillUpdate) { "skipped" } else { "$($r.SkillCount) refreshed" }
    Write-SummaryLine -Label "Rules" -Value ($rulesStatus + "  ->  `$CODEX_HOME/AGENTS.md, agent-rules/")
    Write-SummaryLine -Label "Skills" -Value ($skillsStatus + "  ->  `$CODEX_HOME/skills/")
    if ($r.McpSkipped) {
        Write-SummaryLine -Label "MCP" -Value "skipped (-SkipMcpInstall)"
    } else {
        Write-SummaryLine -Label "MCP" -Value ("$($r.McpSourceCount) sources refreshed, $($r.McpRegisteredCount) registrations refreshed  ->  `$CODEX_HOME/mcp-servers/")
    }
    Write-SummaryText ""
    Write-SummaryText "  Incremental boundary" "Yellow"
    Write-SummaryText "  Only manifest-managed skills/rules/MCP entries are overwritten. User-installed items are not removed, renamed, or uninstalled."
    if ($r.Warnings.Count -gt 0) {
        Write-SummaryText ""
        Write-SummaryText "  Warnings" "Yellow"
        foreach ($warning in $r.Warnings) {
            Write-SummaryText ("  ! " + $warning) "Yellow"
        }
    }
    if ($WhatIf) {
        Write-SummaryText ""
        Write-SummaryText "  Preview only. No disk changes were made. Remove -WhatIf to install." "DarkGray"
    }
    Write-SummaryText "==================================================" "DarkGray"
}

function Dump-DetailLog {
    if ($script:DetailLog.Count -eq 0) {
        return
    }
    Write-SummaryText ""
    Write-SummaryText "Detail log" "Yellow"
    foreach ($line in $script:DetailLog) {
        Write-SummaryText $line
    }
}

try {
    $installManifest = Get-CodexInstallManifest
    $script:InstallResult.PackageId = $installManifest.PackageId

    $script:InstallResult.RuleCount = Install-CodexRules -InstallManifest $installManifest
    $script:InstallResult.SkillCount = Install-CodexSkills -ManagedSkills $installManifest.ManagedSkills
    $script:InstallResult.McpSourceCount = Install-CodexMcpSources -ManagedMcpServers $installManifest.ManagedMcpServers
    if (-not $SkipMcpInstall) {
        $script:InstallResult.McpRegisteredCount = Register-CodexMcpServers -ManagedMcpServers $installManifest.ManagedMcpServers
    }

    Show-InstallSummary
    if ($VerbosePreference -eq "Continue") {
        Dump-DetailLog
    }
}
catch {
    Complete-PhaseProgress
    Write-Host ""
    Write-Host "Install failed." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Dump-DetailLog
    throw
}
