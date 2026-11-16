#!/usr/bin/env pwsh
# ZCode: install Skills, Rules, and local MCP servers for the ZCode host.
# Usage: run from the .agents directory of this repo:
#   powershell -ExecutionPolicy Bypass -File ".\scripts\setup-zcode-agents.ps1"
[CmdletBinding()]
param(
    [switch]$SkipMcpInstall,
    [switch]$SkipSkillUpdate,
    [switch]$SkipRules,
    [switch]$WhatIf,
    [string]$ZcodeHome,
    [switch]$NoPathRewrite,
    [string]$PipIndexUrl,
    [switch]$UseOfficialPipIndex
)

$ErrorActionPreference = "Stop"

$ScriptRoot = $PSScriptRoot
$AgentsRoot = Split-Path $ScriptRoot -Parent
$ManifestPath = Join-Path $AgentsRoot "manifest.json"
$SkillsSource = Join-Path $AgentsRoot "skills"
$RulesSourceRoot = Join-Path $AgentsRoot "rules\zcode"
$RulesSource = Join-Path $RulesSourceRoot "rules"
$AgentsMdSource = Join-Path $RulesSourceRoot "AGENTS.md"
$RetiredMcpCleanupLibrary = Join-Path $ScriptRoot "retired-mcp-cleanup.ps1"
if (-not (Test-Path -LiteralPath $RetiredMcpCleanupLibrary -PathType Leaf)) {
    throw "retired MCP cleanup library not found: $RetiredMcpCleanupLibrary"
}
. $RetiredMcpCleanupLibrary

# ── Resolve ZCode home ───────────────────────────────────────────────

if ([string]::IsNullOrWhiteSpace($ZcodeHome)) {
    $ZcodeHome = Join-Path $env:USERPROFILE ".zcode"
}
$ZcodeHome = [System.IO.Path]::GetFullPath($ZcodeHome).TrimEnd("\")

$SkillsTarget = Join-Path $ZcodeHome "skills"
$RulesTarget = Join-Path $ZcodeHome "rules"
$AgentsMdTarget = Join-Path $ZcodeHome "AGENTS.md"
$McpServersRoot = Join-Path $ZcodeHome "mcp-servers"
$CampusNetUserRoot = Join-Path $ZcodeHome "campus-net"
$ConfigPath = Join-Path $ZcodeHome "cli\config.json"

$RulesManagedStart = "<!-- >>> portable-agents:zcode managed rules >>> -->"
$RulesManagedEnd = "<!-- <<< portable-agents:zcode managed rules <<< -->"

$script:ZcodeConfig = $null

$script:DefaultPipIndexUrl = "https://pypi.tuna.tsinghua.edu.cn/simple"
if ($UseOfficialPipIndex) {
    $script:EffectivePipIndexUrl = $null
} elseif ([string]::IsNullOrWhiteSpace($PipIndexUrl)) {
    $script:EffectivePipIndexUrl = $script:DefaultPipIndexUrl
} else {
    $script:EffectivePipIndexUrl = $PipIndexUrl.Trim()
}

# ── Helpers ──────────────────────────────────────────────────────────

function Write-Phase {
    param([string]$Message)
    Write-Host ""
    Write-Host "== $Message" -ForegroundColor Cyan
}

function Ensure-Directory {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) { return }
    if ($WhatIf) { Write-Host "[WhatIf] would create directory: $Path"; return }
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

function Backup-File {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backup = "$Path.bak-$stamp"
    Copy-Item -LiteralPath $Path -Destination $backup -Force
    Write-Host "  backup: $backup"
    return $backup
}

function Invoke-LoggedCommand {
    param([string]$FilePath, [string[]]$ArgumentList, [string]$FailureMessage)
    $display = "$FilePath $($ArgumentList -join ' ')"
    Write-Host "  -> $display"
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $FilePath @ArgumentList 2>&1 | ForEach-Object { Write-Host ("     " + [string]$_) }
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prevEAP
    }
    if ($exitCode -ne 0) { throw "$FailureMessage (exit $exitCode)" }
}

function Get-InstallManifest {
    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "manifest.json not found: $ManifestPath"
    }
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $install = $manifest.zcodeInstallManifest
    if (-not $install) { throw "manifest.json is missing the zcodeInstallManifest section" }
    return [pscustomobject]@{ Manifest = $manifest; Install = $install }
}

function Get-ManagedSkills {
    $context = Get-InstallManifest
    $managed = @($context.Install.managedSkills)
    if ($managed.Count -eq 0 -and $context.Manifest.skillGroups) {
        $seen = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach ($group in $context.Manifest.skillGroups.PSObject.Properties) {
            foreach ($name in @($group.Value)) { [void]$seen.Add([string]$name) }
        }
        $managed = @($seen)
    }
    return $managed
}

function Get-PipInstallExtraArgs {
    if ($UseOfficialPipIndex -or [string]::IsNullOrWhiteSpace($script:EffectivePipIndexUrl)) {
        return @()
    }
    try {
        $trustedHost = ([Uri]$script:EffectivePipIndexUrl).Host
        return @("-i", $script:EffectivePipIndexUrl, "--trusted-host", $trustedHost)
    } catch {
        return @()
    }
}

function Get-PipIndexLabel {
    if ($UseOfficialPipIndex -or [string]::IsNullOrWhiteSpace($script:EffectivePipIndexUrl)) {
        return "official PyPI"
    }
    return [string]$script:EffectivePipIndexUrl
}

# ── Phase 1: Skills ─────────────────────────────────────────────────

function Invoke-SkillPathRewrite {
    param([string]$SkillRoot)

    $target = Join-Path $ZcodeHome "skills"
    $targetForward = $target.Replace("\", "/")
    $mapping = @(
        @{ From = '$env:USERPROFILE\.cursor\skills'; To = $target },
        @{ From = '%USERPROFILE%\.cursor\skills'; To = $target },
        @{ From = '~/.cursor/skills'; To = $targetForward }
    )
    $textExtensions = @(".md", ".txt", ".json", ".py", ".js", ".mjs", ".cjs", ".ps1", ".sh", ".yaml", ".yml", ".vue")
    $rewritten = 0

    $files = Get-ChildItem -LiteralPath $SkillRoot -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        if ($textExtensions -notcontains $file.Extension.ToLowerInvariant()) { continue }
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
        $text = [System.Text.Encoding]::UTF8.GetString($bytes)
        if ($hasBom) { $text = $text.Substring(1) }
        $original = $text
        foreach ($entry in $mapping) {
            $text = $text.Replace($entry.From, $entry.To)
        }
        if ($text -ne $original) {
            $rewritten++
            if (-not $WhatIf) {
                [System.IO.File]::WriteAllText($file.FullName, $text, (New-Object System.Text.UTF8Encoding($hasBom)))
            }
        }
    }
    return $rewritten
}

function Install-Skills {
    param([string[]]$ManagedSkills, [string[]]$PathRewriteSkills)

    if ($SkipSkillUpdate) { Write-Host "Skills: skipped (-SkipSkillUpdate)"; return }
    Ensure-Directory $SkillsTarget
    $total = $ManagedSkills.Count
    $index = 0
    $installed = 0
    $rewrittenFiles = 0
    foreach ($name in $ManagedSkills) {
        $index++
        Write-Host ("  skills {0}/{1}: {2}" -f $index, $total, $name)
        $source = Join-Path $SkillsSource $name
        $target = Join-Path $SkillsTarget $name
        if (-not (Test-Path -LiteralPath $source -PathType Container)) {
            Write-Warning "skip skill (missing): $name"
            continue
        }
        if ($WhatIf) {
            Write-Host "[WhatIf] would copy skill: $name"
            $installed++
            continue
        }
        if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
        Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
        if (-not $NoPathRewrite -and ($PathRewriteSkills -contains $name)) {
            $rewrittenFiles += (Invoke-SkillPathRewrite -SkillRoot $target)
        }
        $installed++
    }
    Write-Host ("Skills: {0}/{1} installed -> {2}" -f $installed, $total, $SkillsTarget)
    if ($rewrittenFiles -gt 0) {
        Write-Host ("  path rewrite: {0} file(s) -> {1}" -f $rewrittenFiles, $ZcodeHome)
    }
}

# ── Phase 2: Rules ──────────────────────────────────────────────────

function Write-ManagedBlock {
    param(
        [string]$Path,
        [string]$StartMarker,
        [string]$EndMarker,
        [string]$Body
    )

    $existing = ""
    $hasBom = $false
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        $bytes = [System.IO.File]::ReadAllBytes($Path)
        $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
        $existing = [System.Text.Encoding]::UTF8.GetString($bytes)
        if ($hasBom) { $existing = $existing.Substring(1) }
    }

    $nl = "`n"
    if ($existing.Contains("`r`n")) { $nl = "`r`n" }
    $normalizedBody = $Body.Trim()
    $block = $StartMarker + $nl + $normalizedBody + $nl + $EndMarker

    $startIndex = $existing.IndexOf($StartMarker)
    $endIndex = $existing.IndexOf($EndMarker)
    if ($startIndex -ge 0 -and $endIndex -gt $startIndex) {
        $after = $endIndex + $EndMarker.Length
        $updated = $existing.Substring(0, $startIndex) + $block + $existing.Substring($after)
    } elseif ([string]::IsNullOrWhiteSpace($existing)) {
        $updated = $block + $nl
    } else {
        $updated = $existing.TrimEnd() + $nl + $nl + $block + $nl
    }

    if ($updated -eq $existing) { return $false }
    if ($WhatIf) {
        Write-Host "[WhatIf] would update managed block: $Path"
        return $true
    }
    if (Test-Path -LiteralPath $Path -PathType Leaf) { [void](Backup-File $Path) }
    [System.IO.File]::WriteAllText($Path, $updated, (New-Object System.Text.UTF8Encoding($hasBom)))
    Write-Host "  updated: $Path"
    return $true
}

function Install-Rules {
    if ($SkipRules) { Write-Host "Rules: skipped (-SkipRules)"; return }
    if (-not (Test-Path -LiteralPath $AgentsMdSource -PathType Leaf)) {
        throw "ZCode AGENTS.md source not found: $AgentsMdSource"
    }
    Ensure-Directory $ZcodeHome
    $agentBody = [System.IO.File]::ReadAllText($AgentsMdSource, [System.Text.Encoding]::UTF8)
    if ($agentBody.Length -gt 0 -and $agentBody[0] -eq [char]0xFEFF) { $agentBody = $agentBody.Substring(1) }
    [void](Write-ManagedBlock -Path $AgentsMdTarget -StartMarker $RulesManagedStart -EndMarker $RulesManagedEnd -Body $agentBody)

    Ensure-Directory $RulesTarget
    $count = 0
    if (Test-Path -LiteralPath $RulesSource -PathType Container) {
        foreach ($rule in (Get-ChildItem -LiteralPath $RulesSource -File -Filter "*.md" | Sort-Object Name)) {
            if ($WhatIf) {
                Write-Host "[WhatIf] would copy rule: $($rule.Name)"
                $count++
                continue
            }
            Copy-Item -LiteralPath $rule.FullName -Destination (Join-Path $RulesTarget $rule.Name) -Force
            $count++
        }
    }
    Ensure-Directory $CampusNetUserRoot
    Write-Host "Rules: $AgentsMdTarget + $count file(s) -> $RulesTarget"
}

# ── Phase 3: MCP builds ─────────────────────────────────────────────

function Resolve-PythonRuntime {
    $candidates = @(
        @{ FilePath = "py"; Args = @("-3.13"); Label = "py -3.13" },
        @{ FilePath = "py"; Args = @("-3.12"); Label = "py -3.12" },
        @{ FilePath = "py"; Args = @("-3.11"); Label = "py -3.11" },
        @{ FilePath = "py"; Args = @("-3.10"); Label = "py -3.10" },
        @{ FilePath = "python"; Args = @(); Label = "python" }
    )
    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.FilePath -ErrorAction SilentlyContinue)) { continue }
        try {
            & $candidate.FilePath @($candidate.Args + @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)")) *> $null
            if ($LASTEXITCODE -eq 0) { return $candidate }
        } catch {}
    }
    throw "Python 3.10+ not found. Install Python 3.10+ or use the Windows py launcher."
}

function Sync-McpRepo {
    param([string]$Name)

    $source = Join-Path $AgentsRoot "mcp-servers-src\$Name"
    $target = Join-Path $McpServersRoot $Name
    if (-not (Test-Path -LiteralPath $source -PathType Container)) {
        throw "MCP source not found: $source"
    }
    if ($WhatIf) {
        Write-Host "[WhatIf] would sync MCP source: $Name"
        return $target
    }
    Ensure-Directory $McpServersRoot
    Ensure-Directory $target
    $robocopyArgs = @($source, $target, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NP", "/R:1", "/W:1")
    & robocopy @robocopyArgs | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed for ${Name} (exit $LASTEXITCODE)" }
    return $target
}

function Get-DependencyHash {
    param([string]$Repo, [string[]]$RelativePaths)

    $builder = New-Object System.Text.StringBuilder
    foreach ($relative in $RelativePaths) {
        $full = Join-Path $Repo $relative
        if (Test-Path -LiteralPath $full -PathType Leaf) {
            $fileHash = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash
            [void]$builder.Append($relative).Append(":").Append($fileHash).Append(";")
        }
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($builder.ToString())
    return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "")
}

function Test-DependenciesUnchanged {
    param(
        [string]$Repo,
        [string]$MarkerName,
        [string]$Hash,
        [string[]]$EntryPaths
    )

    $marker = Join-Path $Repo $MarkerName
    if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) { return $false }
    $saved = (Get-Content -LiteralPath $marker -Raw).Trim()
    if ($saved -ne $Hash) { return $false }
    foreach ($entry in $EntryPaths) {
        if (-not (Test-Path -LiteralPath (Join-Path $Repo $entry))) { return $false }
    }
    return $true
}

function Install-PythonMcp {
    param(
        [string]$Name,
        $Python,
        [string]$EntryFile,
        [switch]$InstallPlaywright
    )

    $repo = Sync-McpRepo $Name
    if ($WhatIf) {
        Write-Host "[WhatIf] would build Python MCP: $Name"
        return
    }
    $hash = Get-DependencyHash -Repo $repo -RelativePaths @("requirements.txt")
    if (Test-DependenciesUnchanged -Repo $repo -MarkerName ".agents-python-deps.sha256" -Hash $hash -EntryPaths @($EntryFile, ".venv\Scripts\python.exe")) {
        Write-Host "  python deps unchanged, skipped: $Name"
        return
    }
    Push-Location $repo
    try {
        $venvPython = ".\.venv\Scripts\python.exe"
        if (-not (Test-Path -LiteralPath ".venv" -PathType Container)) {
            Invoke-LoggedCommand $Python.FilePath (@($Python.Args) + @("-m", "venv", ".venv")) "venv failed: $Name"
        }
        $pipExtra = Get-PipInstallExtraArgs
        Invoke-LoggedCommand $venvPython (@("-m", "pip", "install", "--no-cache-dir", "--timeout", "30", "--retries", "3", "--upgrade", "pip") + $pipExtra) "pip upgrade failed: $Name"
        Invoke-LoggedCommand $venvPython (@("-m", "pip", "install", "--no-cache-dir", "--timeout", "30", "--retries", "3", "--prefer-binary", "-r", "requirements.txt") + $pipExtra) "pip requirements install failed: $Name"
        if ($InstallPlaywright) {
            Invoke-LoggedCommand $venvPython @("-m", "playwright", "install", "chromium") "playwright install failed: $Name"
        }
        Invoke-LoggedCommand $venvPython @("-c", "import server; print('server import ok')") "server import check failed: $Name"
        Set-Content -LiteralPath (Join-Path $repo ".agents-python-deps.sha256") -Value $hash -Encoding ASCII
    } finally {
        Pop-Location
    }
}

function Install-NodeMcp {
    param([string]$Name, [string]$EntryFile)

    $repo = Sync-McpRepo $Name
    if ($WhatIf) {
        Write-Host "[WhatIf] would build Node MCP: $Name"
        return
    }
    $hashPaths = @("package.json")
    $hash = Get-DependencyHash -Repo $repo -RelativePaths $hashPaths
    if (Test-DependenciesUnchanged -Repo $repo -MarkerName ".agents-node-deps.sha256" -Hash $hash -EntryPaths @($EntryFile, "node_modules")) {
        Write-Host "  node deps unchanged, skipped: $Name"
        return
    }
    Push-Location $repo
    try {
        Invoke-LoggedCommand "npm" @("install", "--no-audit", "--no-fund") "npm install failed: $Name"
        Invoke-LoggedCommand "npm" @("run", "build") "npm build failed: $Name"
        Set-Content -LiteralPath (Join-Path $repo ".agents-node-deps.sha256") -Value $hash -Encoding ASCII
    } finally {
        Pop-Location
    }
}

# ── Phase 4: MCP registration (~/.zcode/cli/config.json) ────────────

function Get-ConfigText {
    if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) { return "" }
    $bytes = [System.IO.File]::ReadAllBytes($ConfigPath)
    $script:ConfigHasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
    $text = [System.Text.Encoding]::UTF8.GetString($bytes)
    if ($script:ConfigHasBom) { $text = $text.Substring(1) }
    return $text
}

function Get-ServersObject {
    # Ensures $script:ZcodeConfig.mcp.servers exists and returns the servers object.
    $config = $script:ZcodeConfig
    if (-not ($config.PSObject.Properties["mcp"])) {
        $config | Add-Member -NotePropertyName "mcp" -NotePropertyValue ([pscustomobject]@{})
    }
    if ($config.mcp -isnot [System.Management.Automation.PSCustomObject]) {
        throw "config.json field 'mcp' is not a JSON object: $ConfigPath"
    }
    if (-not ($config.mcp.PSObject.Properties["servers"])) {
        $config.mcp | Add-Member -NotePropertyName "servers" -NotePropertyValue ([pscustomobject]@{})
    }
    if ($config.mcp.servers -isnot [System.Management.Automation.PSCustomObject]) {
        throw "config.json field 'mcp.servers' is not a JSON object: $ConfigPath"
    }
    return $config.mcp.servers
}

function Test-ManagedServerExists {
    param([string]$Name)
    if ($null -eq $script:ZcodeConfig) { return $false }
    try {
        $servers = $script:ZcodeConfig.mcp.servers
    } catch { return $false }
    if ($null -eq $servers -or $servers -isnot [System.Management.Automation.PSCustomObject]) { return $false }
    return [bool]($servers.PSObject.Properties[$Name])
}

function Remove-ManagedServer {
    param([string]$Name)
    $servers = Get-ServersObject
    $servers.PSObject.Properties.Remove($Name)
}

function Set-ManagedServer {
    param([string]$Name, $Entry)

    $servers = Get-ServersObject
    if ($servers.PSObject.Properties[$Name]) {
        $servers.$Name = $Entry
    } else {
        $servers | Add-Member -NotePropertyName $Name -NotePropertyValue $Entry
    }
}

function Build-ManagedServerEntries {
    $nodePath = (Get-Command node -ErrorAction Stop).Source
    $academicPython = Join-Path $McpServersRoot "academic-research-mcp\.venv\Scripts\python.exe"
    $academicScript = Join-Path $McpServersRoot "academic-research-mcp\server.py"
    $zoteroEntry = Join-Path $McpServersRoot "zotero-mcp\dist\index.js"
    $deckEntry = Join-Path $McpServersRoot "deck-builder\build\index.js"
    $campusPython = Join-Path $McpServersRoot "campus-net-mcp\.venv\Scripts\python.exe"
    $campusScript = Join-Path $McpServersRoot "campus-net-mcp\server.py"

    # ZCode does not expand ${...} templates in config files and passes env
    # verbatim, so optional credentials are NOT written here: stdio children
    # inherit the process environment. Only fixed paths go into `env`.
    return [ordered]@{
        "academic-research" = [pscustomobject]@{
            type = "stdio"
            command = $academicPython
            args = @($academicScript)
        }
        "zotero" = [pscustomobject]@{
            type = "stdio"
            command = $nodePath
            args = @($zoteroEntry)
        }
        "deck-builder" = [pscustomobject]@{
            type = "stdio"
            command = $nodePath
            args = @($deckEntry)
        }
        "campus-net" = [pscustomobject]@{
            type = "stdio"
            command = $campusPython
            args = @($campusScript)
            env = [pscustomobject]@{
                CAMPNET_USER_ROOT = $CampusNetUserRoot
            }
        }
    }
}

function Test-ConfigJson {
    param([string]$Path, [string[]]$ExpectedServers)

    try {
        $parsed = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8) | ConvertFrom-Json
    } catch {
        Write-Warning "written config failed to parse: $($_.Exception.Message)"
        return $false
    }
    foreach ($name in $ExpectedServers) {
        if (-not ($parsed.mcp.servers.PSObject.Properties[$name])) { return $false }
    }
    return $true
}

function Register-McpServers {
    $script:ConfigHasBom = $false
    $existing = Get-ConfigText
    if (-not [string]::IsNullOrWhiteSpace($existing)) {
        try {
            $script:ZcodeConfig = $existing | ConvertFrom-Json
        } catch {
            throw "ZCode config.json is not valid JSON; fix it manually before installing: $ConfigPath"
        }
    } else {
        $script:ZcodeConfig = [pscustomobject]@{}
    }

    $manifest = (Get-InstallManifest).Manifest
    $retiredNames = @($manifest.retiredMcpServers)
    $removed = Invoke-RetiredMcpCleanup `
        -Names $retiredNames `
        -Context "ZCode config ($ConfigPath)" `
        -WhatIf:$WhatIf `
        -Exists { param($name) Test-ManagedServerExists -Name $name } `
        -Remove { param($name) Remove-ManagedServer -Name $name }
    Write-Host "  retired MCP registrations removed: $removed"

    $entries = Build-ManagedServerEntries
    foreach ($name in $entries.Keys) {
        Set-ManagedServer -Name $name -Entry $entries[$name]
    }

    $updated = ($script:ZcodeConfig | ConvertTo-Json -Depth 100)
    $expectedServers = @($entries.Keys)

    if ($WhatIf) {
        Write-Host "[WhatIf] would write managed MCP servers to: $ConfigPath"
        return
    }
    if ($updated.Trim() -eq $existing.Trim()) {
        Write-Host "  managed MCP entries unchanged: $ConfigPath"
        return
    }

    Ensure-Directory (Split-Path -Parent $ConfigPath)
    $temporary = "$ConfigPath.tmp-$([guid]::NewGuid().ToString('N'))"
    [System.IO.File]::WriteAllText($temporary, $updated, (New-Object System.Text.UTF8Encoding($script:ConfigHasBom)))
    if (-not (Test-ConfigJson -Path $temporary -ExpectedServers $expectedServers)) {
        Remove-Item -LiteralPath $temporary -Force
        throw "Rendered ZCode config failed JSON validation; the original config was not modified."
    }
    if (Test-Path -LiteralPath $ConfigPath -PathType Leaf) { [void](Backup-File $ConfigPath) }
    Move-Item -LiteralPath $temporary -Destination $ConfigPath -Force
    Write-Host "  registered managed MCP servers -> $ConfigPath"
}

# ── Main ────────────────────────────────────────────────────────────

try {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "  ZCode Agents Setup" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "ZCode home: $ZcodeHome"
    Write-Host "Config:     $ConfigPath"
    Write-Host "Mode:       $(if ($WhatIf) { 'preview (-WhatIf)' } else { 'install' })"

    Ensure-Directory $ZcodeHome
    $context = Get-InstallManifest
    $managedSkills = Get-ManagedSkills
    $pathRewriteSkills = @($context.Install.pathRewriteSkills)

    Write-Phase "Skills"
    Install-Skills -ManagedSkills $managedSkills -PathRewriteSkills $pathRewriteSkills

    Write-Phase "Rules"
    Install-Rules

    Write-Phase "MCP"
    if (-not $SkipMcpInstall) {
        $python = Resolve-PythonRuntime
        Write-Host "Python:   $($python.Label)"
        Write-Host "Pip index: $(Get-PipIndexLabel)"
        Install-PythonMcp -Name "academic-research-mcp" -Python $python -EntryFile "server.py"
        Install-NodeMcp -Name "zotero-mcp" -EntryFile "dist\index.js"
        Install-NodeMcp -Name "deck-builder" -EntryFile "build\index.js"
        Install-PythonMcp -Name "campus-net-mcp" -Python $python -EntryFile "server.py" -InstallPlaywright
        Register-McpServers
    } else {
        Write-Host "MCP: skipped (-SkipMcpInstall)"
    }

    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  Done" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "Skills:  $SkillsTarget"
    Write-Host "Rules:   $AgentsMdTarget + $RulesTarget\"
    Write-Host "MCP:     $McpServersRoot\"
    Write-Host "Config:  $ConfigPath"
    Write-Host "Campus:  $CampusNetUserRoot"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart ZCode sessions (Settings > Skills / MCP) to refresh discovery."
    Write-Host "  2. Verify managed skills appear; /<name> invokes a skill explicitly."
    Write-Host "  3. Set env vars if needed: S2_API_KEY, OPENALEX_EMAIL, CROSSREF_EMAIL, NCBI_API_KEY,"
    Write-Host "     CAMPUS_USERNAME, CAMPUS_PASSWORD, CAMPUS_OUTPUT_DIR, PADDLEOCR_TOKEN"
    Write-Host "     (stdio MCP children inherit the process environment)."
    Write-Host "  4. Verify MCP tools: mcp__academic-research__*, mcp__zotero__*, mcp__deck-builder__*, mcp__campus-net__*."
} catch {
    Write-Host ""
    Write-Host "Install failed." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    throw
}
