#!/usr/bin/env pwsh
# Codex: install managed Skills, global rules, and MCP servers.
# Usage: cd path\to\.agents  then  powershell -ExecutionPolicy Bypass -File ".\scripts\setup-codex-agents.ps1"
[CmdletBinding()]
param(
    [string]$CodexHome,
    [string]$PipIndexUrl,
    [switch]$UseOfficialPipIndex,
    [switch]$SkipMcpInstall,
    [switch]$SkipSkillUpdate,
    [switch]$SkipRulesUpdate,
    [switch]$WhatIf,
    [switch]$NoClearScreen,
    [switch]$NoColor
)

$ErrorActionPreference = "Stop"

$script:DefaultPipIndexUrl = "https://pypi.tuna.tsinghua.edu.cn/simple"
if ($UseOfficialPipIndex) {
    $script:PipIndexUrl = $null
} elseif ([string]::IsNullOrWhiteSpace($PipIndexUrl)) {
    $script:PipIndexUrl = $script:DefaultPipIndexUrl
} else {
    $script:PipIndexUrl = $PipIndexUrl.Trim()
}

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
    PipIndexLabel = ""
    Warnings = [System.Collections.Generic.List[string]]::new()
    WhatIf = [bool]$WhatIf
}

function Write-DetailLog {
    param([string]$Message)
    [void]$script:DetailLog.Add($Message)
}

function Invoke-LoggedNativeCommand {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$FailureMessage
    )
    $display = "$FilePath $($ArgumentList -join ' ')"
    Write-Host ("  -> " + $display)
    Write-DetailLog "running: $display"
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $FilePath @ArgumentList 2>&1 | ForEach-Object {
            $line = [string]$_
            Write-DetailLog $line
            Write-Host ("     " + $line)
        }
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($exitCode -ne 0) {
        throw "$FailureMessage (exit code $exitCode)"
    }
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

function Test-PythonVersionAtLeast {
    param(
        [string]$FilePath,
        [string[]]$ArgumentPrefix = @(),
        [int]$Major = 3,
        [int]$Minor = 10
    )
    $args = @($ArgumentPrefix)
    $args += @("-c", "import sys; raise SystemExit(0 if sys.version_info >= ($Major, $Minor) else 1)")
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $FilePath @args *> $null
        return ($LASTEXITCODE -eq 0)
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Resolve-PythonRuntime {
    $candidates = @(
        [PSCustomObject]@{ FilePath = "py"; Args = @("-3.13"); Label = "py -3.13" },
        [PSCustomObject]@{ FilePath = "py"; Args = @("-3.12"); Label = "py -3.12" },
        [PSCustomObject]@{ FilePath = "py"; Args = @("-3.11"); Label = "py -3.11" },
        [PSCustomObject]@{ FilePath = "py"; Args = @("-3.10"); Label = "py -3.10" },
        [PSCustomObject]@{ FilePath = "python"; Args = @(); Label = "python" }
    )
    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.FilePath -ErrorAction SilentlyContinue)) {
            continue
        }
        if (Test-PythonVersionAtLeast -FilePath $candidate.FilePath -ArgumentPrefix $candidate.Args) {
            Write-DetailLog "selected Python runtime: $($candidate.Label)"
            return $candidate
        }
        Write-DetailLog "skip Python runtime below 3.10: $($candidate.Label)"
    }
    throw "Required Python 3.10+ not found. Install Python 3.10+ or make it available via the Windows py launcher."
}

function Invoke-PythonRuntime {
    param(
        [string[]]$ArgumentList,
        [string]$FailureMessage
    )
    $args = @($script:PythonRuntime.Args)
    $args += $ArgumentList
    Invoke-LoggedNativeCommand -FilePath $script:PythonRuntime.FilePath -ArgumentList $args -FailureMessage $FailureMessage
}

function Get-PipIndexLabel {
    if ($UseOfficialPipIndex) {
        return "official PyPI"
    }
    if ($script:PipIndexUrl -eq $script:DefaultPipIndexUrl) {
        return "tuna (Tsinghua)"
    }
    return [string]$script:PipIndexUrl
}

function Get-PipInstallExtraArgs {
    if ($UseOfficialPipIndex -or [string]::IsNullOrWhiteSpace($script:PipIndexUrl)) {
        return @()
    }
    $normalized = $script:PipIndexUrl.Trim().TrimEnd("/").ToLowerInvariant()
    if ($normalized -eq "https://pypi.org/simple" -or $normalized -eq "http://pypi.org/simple") {
        return @()
    }
    $trustedHost = ([Uri]$script:PipIndexUrl).Host
    return @("-i", $script:PipIndexUrl, "--trusted-host", $trustedHost)
}

function Test-VenvPythonVersion {
    param([string]$PythonPath)
    if (-not (Test-Path $PythonPath)) {
        return $false
    }
    return Test-PythonVersionAtLeast -FilePath $PythonPath
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

function Sync-ManagedDirectoryPreservingChildren {
    param(
        [string]$Source,
        [string]$Target,
        [string]$ManagedRoot,
        [string]$Label,
        [string[]]$PreserveNames = @()
    )
    if (-not (Test-Path $Source)) {
        Register-InstallWarning "managed source missing: $Label ($Source)"
        return $false
    }
    Assert-PathInside -Path $Target -Parent $ManagedRoot
    if ($WhatIf) {
        Write-DetailLog "[WhatIf] would sync managed directory preserving dependencies: $Label -> $Target"
        return $true
    }
    if (-not (Test-Path $Target)) {
        Copy-Item -LiteralPath $Source -Destination $Target -Recurse -Force
        Write-DetailLog "copied managed directory: $Label"
        return $true
    }

    $preserve = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($name in $PreserveNames) {
        [void]$preserve.Add($name)
    }

    Get-ChildItem -LiteralPath $Target -Force | ForEach-Object {
        if (-not $preserve.Contains($_.Name)) {
            Remove-Item -LiteralPath $_.FullName -Recurse -Force
        }
    }
    Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $Target -Recurse -Force
    }
    Write-DetailLog "synced managed directory preserving dependencies: $Label"
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

function Get-DependencyInputHash {
    param([string[]]$Paths)
    $parts = [System.Collections.Generic.List[string]]::new()
    foreach ($path in $Paths) {
        if (Test-Path $path) {
            $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
            [void]$parts.Add("$path=$hash")
        }
    }
    $joined = [string]::Join("`n", $parts)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($joined)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    }
    finally {
        $sha.Dispose()
    }
}

function Test-DependencyMarker {
    param(
        [string]$MarkerPath,
        [string]$ExpectedHash,
        [string[]]$RequiredPaths
    )
    if (-not (Test-Path $MarkerPath)) {
        return $false
    }
    foreach ($path in $RequiredPaths) {
        if (-not (Test-Path $path)) {
            return $false
        }
    }
    $actual = (Get-Content -LiteralPath $MarkerPath -Raw -ErrorAction SilentlyContinue).Trim()
    return $actual -eq $ExpectedHash
}

function Test-PythonModulesAvailable {
    param(
        [string]$PythonPath,
        [string[]]$Modules
    )
    if (-not (Test-Path $PythonPath)) {
        return $false
    }
    if ($Modules.Count -eq 0) {
        return $true
    }
    $script = @"
import importlib.util
import sys
missing = [m for m in sys.argv[1:] if importlib.util.find_spec(m) is None]
raise SystemExit(1 if missing else 0)
"@
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $PythonPath -c $script @Modules *> $null
        return ($LASTEXITCODE -eq 0)
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Set-DependencyMarker {
    param(
        [string]$MarkerPath,
        [string]$Hash
    )
    Set-Content -LiteralPath $MarkerPath -Value $Hash -Encoding UTF8
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
        $venvPython = ".\.venv\Scripts\python.exe"
        $requirements = Join-Path $RepoPath "requirements.txt"
        $marker = Join-Path $RepoPath ".agents-python-deps.sha256"
        $playwrightMarker = Join-Path $RepoPath ".agents-playwright-chromium.done"
        $inputHash = Get-DependencyInputHash -Paths @($requirements)
        Write-Host "  -> MCP ${Name}: checking venv"
        if ((Test-Path ".venv") -and -not (Test-VenvPythonVersion -PythonPath $venvPython)) {
            Remove-Item -LiteralPath ".venv" -Recurse -Force
            Write-DetailLog "removed incompatible venv: $Name"
        }
        if (-not (Test-Path ".venv")) {
            Write-Host "  -> MCP ${Name}: creating venv"
            Invoke-PythonRuntime -ArgumentList @("-m", "venv", ".venv") -FailureMessage "python venv creation failed: $Name"
            Write-DetailLog "created venv: $Name"
        }
        $requiredModules = @("mcp")
        $pipExtra = Get-PipInstallExtraArgs
        $depsReady = (Test-DependencyMarker -MarkerPath $marker -ExpectedHash $inputHash -RequiredPaths @($venvPython)) -and (Test-PythonModulesAvailable -PythonPath $venvPython -Modules $requiredModules)
        if (-not $depsReady) {
            Write-Host "  -> MCP ${Name}: installing Python dependencies (pip index: $(Get-PipIndexLabel))"
            Invoke-LoggedNativeCommand -FilePath $venvPython -ArgumentList (@("-m", "pip", "install", "--no-cache-dir", "--timeout", "30", "--retries", "3", "--upgrade", "pip") + $pipExtra) -FailureMessage "pip upgrade failed: $Name"
            Invoke-LoggedNativeCommand -FilePath $venvPython -ArgumentList (@("-m", "pip", "install", "--no-cache-dir", "--timeout", "30", "--retries", "3", "--prefer-binary", "-r", "requirements.txt") + $pipExtra) -FailureMessage "pip requirements install failed: $Name"
            if (-not (Test-PythonModulesAvailable -PythonPath $venvPython -Modules $requiredModules)) {
                throw "python dependency health check failed: $Name (missing module: mcp)"
            }
            Set-DependencyMarker -MarkerPath $marker -Hash $inputHash
        } else {
            Write-Host "  -> MCP ${Name}: dependencies up to date, skipped"
            Write-DetailLog "python dependencies unchanged, skipped pip install: $Name"
        }
        if ($Name -eq "campus-net-mcp") {
            if (-not (Test-Path $playwrightMarker)) {
                Write-Host "  -> MCP ${Name}: installing Playwright Chromium"
                Write-DetailLog "Installing Chromium for Playwright (first run may download binaries) ..."
                Invoke-LoggedNativeCommand -FilePath $venvPython -ArgumentList @("-m", "playwright", "install", "chromium") -FailureMessage "playwright chromium install failed: $Name"
                Set-Content -LiteralPath $playwrightMarker -Value (Get-Date -Format o) -Encoding UTF8
            } else {
                Write-DetailLog "playwright chromium marker exists, skipped install: $Name"
            }
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
        $packageJson = Join-Path $RepoPath "package.json"
        $packageLock = Join-Path $RepoPath "package-lock.json"
        $marker = Join-Path $RepoPath ".agents-node-deps.sha256"
        $inputHash = Get-DependencyInputHash -Paths @($packageJson, $packageLock)
        $entry = if ($Name -eq "deck-builder") {
            Join-Path $RepoPath "build\index.js"
        } else {
            Join-Path $RepoPath "dist\index.js"
        }
        if (Test-DependencyMarker -MarkerPath $marker -ExpectedHash $inputHash -RequiredPaths @($entry)) {
            Write-Host "  -> MCP ${Name}: dependencies up to date, skipped"
            Write-DetailLog "node dependencies unchanged, skipped npm install/build: $Name"
            return
        }
        Write-Host "  -> MCP ${Name}: installing Node dependencies"
        Invoke-LoggedNativeCommand -FilePath "npm" -ArgumentList @("install") -FailureMessage "npm install failed: $Name"
        Write-Host "  -> MCP ${Name}: building"
        Invoke-LoggedNativeCommand -FilePath "npm" -ArgumentList @("run", "build") -FailureMessage "npm build failed: $Name"
        Set-DependencyMarker -MarkerPath $marker -Hash $inputHash
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
        $script:PythonRuntime = Resolve-PythonRuntime
        Assert-Command "node"
        Assert-Command "npm"
    }
    Ensure-Directory $McpTargetRoot
    $localServers = @($ManagedMcpServers | Where-Object {
        [string]$_.kind -ne "npx" -and -not [string]::IsNullOrWhiteSpace([string]$_.sourceDir)
    })
    $count = 0
    $total = $localServers.Count
    $index = 0
    foreach ($server in $ManagedMcpServers) {
        $name = [string]$server.sourceDir
        if ([string]$server.kind -eq "npx") {
            Write-DetailLog "skip local source install for npx MCP: $($server.name)"
            continue
        }
        if ([string]::IsNullOrWhiteSpace($name)) {
            Register-InstallWarning "managed MCP missing sourceDir"
            continue
        }
        $index++
        Write-PhaseProgress -Phase "MCP $name" -Current $index -Total $total
        Write-Host "  -> MCP ${name}: syncing bundled source"
        $src = Resolve-ChildPath -Parent $McpSourceRoot -Child $name
        $dst = Resolve-ChildPath -Parent $McpTargetRoot -Child $name
        if (-not (Sync-ManagedDirectoryPreservingChildren -Source $src -Target $dst -ManagedRoot $McpTargetRoot -Label "mcp:$name" -PreserveNames @(".venv", "node_modules", ".agents-python-deps.sha256", ".agents-node-deps.sha256", ".agents-playwright-chromium.done"))) {
            Complete-PhaseProgress
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
        Complete-PhaseProgress
    }
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
        Write-Host "  -> Registering MCP: $mcpName"
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
        Write-SummaryLine -Label "Pip index" -Value $r.PipIndexLabel
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
    $script:InstallResult.PipIndexLabel = Get-PipIndexLabel
    Write-DetailLog "pip index: $($script:InstallResult.PipIndexLabel)"

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
