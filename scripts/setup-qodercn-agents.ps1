#!/usr/bin/env pwsh
# QoderCN: install Skills, Rules, and MCP servers to ~/.qoder-cn/
# Usage: run from the .agents directory of this repo:
#   powershell -ExecutionPolicy Bypass -File ".\scripts\setup-qodercn-agents.ps1"
[CmdletBinding()]
param(
    [switch]$SkipMcpInstall,
    [switch]$SkipSkillUpdate,
    [switch]$SkipRules,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$ScriptRoot = $PSScriptRoot
$AgentsRoot = Split-Path $ScriptRoot -Parent
$QoderRoot = Join-Path $env:USERPROFILE ".qoder-cn"
$SkillsSource = Join-Path $AgentsRoot "skills"
$SkillsTarget = Join-Path $QoderRoot "skills"
$RulesSource = Join-Path $AgentsRoot "rules\qoder"
$RulesTarget = Join-Path $QoderRoot "rules"
$AgentsMdSource = Join-Path $RulesSource "AGENTS.md"
$AgentsMdTarget = Join-Path $QoderRoot "AGENTS.md"
$McpServersRoot = Join-Path $QoderRoot "mcp-servers"
$ManifestPath = Join-Path $AgentsRoot "manifest.json"
$QoderSettingsPath = Join-Path $QoderRoot "settings.json"
$RetiredMcpCleanupLibrary = Join-Path $ScriptRoot "retired-mcp-cleanup.ps1"
if (-not (Test-Path -LiteralPath $RetiredMcpCleanupLibrary -PathType Leaf)) {
    throw "retired MCP cleanup library not found: $RetiredMcpCleanupLibrary"
}
. $RetiredMcpCleanupLibrary

# ── Helpers ──────────────────────────────────────────────────────────

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        if ($WhatIf) { Write-Host "[WhatIf] would create: $Path"; return }
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "  created: $Path"
    }
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
    } finally { $ErrorActionPreference = $prevEAP }
    if ($exitCode -ne 0) { throw "$FailureMessage (exit $exitCode)" }
}

function Resolve-PythonRuntime {
    $candidates = @(
        @{ FilePath = "py"; Args = @("-3.13"); Label = "py -3.13" },
        @{ FilePath = "py"; Args = @("-3.12"); Label = "py -3.12" },
        @{ FilePath = "py"; Args = @("-3.11"); Label = "py -3.11" },
        @{ FilePath = "py"; Args = @("-3.10"); Label = "py -3.10" },
        @{ FilePath = "python"; Args = @(); Label = "python" }
    )
    foreach ($c in $candidates) {
        if (-not (Get-Command $c.FilePath -ErrorAction SilentlyContinue)) { continue }
        try {
            & $c.FilePath $($c.Args) -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" *> $null
            if ($LASTEXITCODE -eq 0) { return $c }
        } catch {}
    }
    throw "Python 3.10+ not found. Install Python 3.10+ or use the Windows py launcher."
}

function Get-InstallManifest {
    if (-not (Test-Path $ManifestPath)) { throw "manifest.json not found: $ManifestPath" }
    $manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $install = $manifest.qodercnInstallManifest
    if (-not $install) { throw "manifest.json is missing the qodercnInstallManifest section" }
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

# ── Phase 1: Skills ─────────────────────────────────────────────────

function Install-Skills {
    param([string[]]$ManagedSkills)
    if ($SkipSkillUpdate) { Write-Host "Skills: skipped (-SkipSkillUpdate)"; return 0 }
    Ensure-Directory $SkillsTarget
    $count = 0
    $total = $ManagedSkills.Count
    $index = 0
    foreach ($name in $ManagedSkills) {
        $index++
        Write-Host "`rSkills $index/$total" -NoNewline
        $src = Join-Path $SkillsSource $name
        $dst = Join-Path $SkillsTarget $name
        if (-not (Test-Path $src)) { Write-Warning "skip skill (missing): $name"; continue }
        if ($WhatIf) { Write-Host "[WhatIf] would copy skill: $name"; $count++; continue }
        if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
        Copy-Item $src $dst -Recurse -Force
        $count++
    }
    Write-Host ""
    Write-Host "Skills: $count/$total installed -> $SkillsTarget"
    return $count
}

# ── Phase 2: Rules ──────────────────────────────────────────────────

function Install-Rules {
    if ($SkipRules) { Write-Host "Rules: skipped (-SkipRules)"; return }
    Ensure-Directory $QoderRoot
    Ensure-Directory $RulesTarget

    # Resident entry file: thin AGENTS.md with hard constraints (rules/ auto-loaded via trigger frontmatter)
    if (-not (Test-Path -LiteralPath $AgentsMdSource -PathType Leaf)) {
        throw "Qoder AGENTS.md source not found: $AgentsMdSource"
    }
    if ($WhatIf) { Write-Host "[WhatIf] would copy AGENTS.md -> $AgentsMdTarget" }
    else {
        Copy-Item -LiteralPath $AgentsMdSource $AgentsMdTarget -Force
        Write-Host "  AGENTS.md -> $AgentsMdTarget"
    }

    $context = Get-InstallManifest
    $managedRules = @($context.Install.managedRules)
    $total = $managedRules.Count
    $count = 0
    foreach ($rule in $managedRules) {
        $src = Join-Path $RulesSource $rule
        if (-not (Test-Path -LiteralPath $src -PathType Leaf)) { Write-Warning "skip rule (missing): $rule"; continue }
        if ($WhatIf) { Write-Host "[WhatIf] would copy rule: $rule"; $count++; continue }
        Copy-Item -LiteralPath $src (Join-Path $RulesTarget $rule) -Force
        $count++
    }
    Write-Host "Rules: $count/$total modular rules -> $RulesTarget"
}

# ── Phase 3: MCP Servers ────────────────────────────────────────────

function Ensure-McpRepo {
    param([string]$Name)
    $target = Join-Path $McpServersRoot $Name
    if (Test-Path $target) { return $target }
    $bundled = Join-Path $AgentsRoot "mcp-servers-src\$Name"
    if (Test-Path $bundled) {
        Copy-Item $bundled $target -Recurse -Force
        Write-Host "  copied bundled: $Name"
        return $target
    }
    throw "MCP source not found: $Name"
}

function Install-AcademicResearchMcp {
    param($Python)
    Write-Host "MCP: academic-research ..."
    $repo = Ensure-McpRepo "academic-research-mcp"
    Push-Location $repo
    try {
        $venvPython = ".\.venv\Scripts\python.exe"
        if (-not (Test-Path ".venv")) {
            Invoke-LoggedCommand $Python.FilePath ($Python.Args + @("-m", "venv", ".venv")) "venv failed: academic-research"
        }
        Invoke-LoggedCommand $venvPython @("-m", "pip", "install", "--no-cache-dir", "--timeout", "30", "-r", "requirements.txt") "pip failed: academic-research"
    } finally { Pop-Location }
}

function Install-ZoteroMcp {
    Write-Host "MCP: zotero ..."
    $repo = Ensure-McpRepo "zotero-mcp"
    Push-Location $repo
    try {
        Invoke-LoggedCommand "npm" @("install") "npm install failed: zotero-mcp"
        Invoke-LoggedCommand "npm" @("run", "build") "npm build failed: zotero-mcp"
    } finally { Pop-Location }
}

function Install-DeckBuilderMcp {
    Write-Host "MCP: deck-builder ..."
    $repo = Ensure-McpRepo "deck-builder"
    Push-Location $repo
    try {
        Invoke-LoggedCommand "npm" @("install") "npm install failed: deck-builder"
        Invoke-LoggedCommand "npm" @("run", "build") "npm build failed: deck-builder"
    } finally { Pop-Location }
}

function Install-CampusNetMcp {
    param($Python)
    Write-Host "MCP: campus-net ..."
    $repo = Ensure-McpRepo "campus-net-mcp"
    Push-Location $repo
    try {
        $venvPython = ".\.venv\Scripts\python.exe"
        if (-not (Test-Path ".venv")) {
            Invoke-LoggedCommand $Python.FilePath ($Python.Args + @("-m", "venv", ".venv")) "venv failed: campus-net"
        }
        Invoke-LoggedCommand $venvPython @("-m", "pip", "install", "--no-cache-dir", "--timeout", "30", "-r", "requirements.txt") "pip failed: campus-net"
        Invoke-LoggedCommand $venvPython @("-m", "playwright", "install", "chromium") "playwright failed: campus-net"
    } finally { Pop-Location }
}

function Register-McpServers {
    Write-Host "MCP: registering with qoderclicn ..."
    $qoderCli = "qoderclicn"
    if (-not $WhatIf -and -not (Get-Command $qoderCli -ErrorAction SilentlyContinue)) {
        Write-Warning "qoderclicn not found in PATH. Please register MCP servers manually or restart the CLI."
        return
    }

    $manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $retiredMcpServers = @($manifest.retiredMcpServers)
    $retiredRemoved = Invoke-RetiredMcpCleanup `
        -Names $retiredMcpServers `
        -Context "QoderCN MCP config" `
        -WhatIf:$WhatIf `
        -Exists {
            param($name)
            if (-not (Test-Path -LiteralPath $QoderSettingsPath -PathType Leaf)) {
                return $false
            }
            $settings = Get-Content -LiteralPath $QoderSettingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
            return $settings.mcpServers -and ($settings.mcpServers.PSObject.Properties.Name -contains $name)
        } `
        -Remove {
            param($name)
            & $qoderCli mcp remove $name -s user 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "qoderclicn mcp remove failed: $name"
            }
        }
    Write-Host "  retired MCP registrations removed: $retiredRemoved"

    if ($WhatIf) {
        Write-Host "[WhatIf] would refresh 4 managed MCP registrations"
        return
    }

    $academicPython = Join-Path $McpServersRoot "academic-research-mcp\.venv\Scripts\python.exe"
    $academicServer = Join-Path $McpServersRoot "academic-research-mcp\server.py"
    $zoteroEntry = Join-Path $McpServersRoot "zotero-mcp\dist\index.js"
    $deckEntry = Join-Path $McpServersRoot "deck-builder\build\index.js"
    $campusPython = Join-Path $McpServersRoot "campus-net-mcp\.venv\Scripts\python.exe"
    $campusServer = Join-Path $McpServersRoot "campus-net-mcp\server.py"

    # Remove existing entries first (ignore errors if not present)
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    foreach ($name in @("academic-research", "zotero", "deck-builder", "campus-net")) {
        try {
            & $qoderCli mcp remove $name -s user 2>&1 | Out-Null
        } catch {}
    }
    $ErrorActionPreference = $prevEAP

    # academic-research
    & $qoderCli mcp add academic-research -s user -- $academicPython $academicServer
    Write-Host "  registered: academic-research"

    # zotero
    & $qoderCli mcp add zotero -s user -- node $zoteroEntry
    Write-Host "  registered: zotero"

    # deck-builder
    & $qoderCli mcp add deck-builder -s user -- node $deckEntry
    Write-Host "  registered: deck-builder"

    # campus-net
    & $qoderCli mcp add campus-net -s user -- $campusPython $campusServer
    Write-Host "  registered: campus-net"
}

# ── Main ────────────────────────────────────────────────────────────

try {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "  QoderCN Agents Setup" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""

    Ensure-Directory $QoderRoot
    Ensure-Directory $McpServersRoot

    # Skills
    $managedSkills = Get-ManagedSkills
    $skillCount = Install-Skills -ManagedSkills $managedSkills

    # Rules
    Install-Rules

    # MCP
    if (-not $SkipMcpInstall) {
        $python = Resolve-PythonRuntime
        Write-Host "Python: $($python.Label)"

        if ($WhatIf) {
            Write-Host "[WhatIf] would install 4 local MCP servers"
            Register-McpServers
        } else {
            Install-AcademicResearchMcp -Python $python
            Install-ZoteroMcp
            Install-DeckBuilderMcp
            Install-CampusNetMcp -Python $python
            Register-McpServers
        }
    } else {
        Write-Host "MCP: skipped (-SkipMcpInstall)"
    }

    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  Done!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Skills:   $SkillsTarget"
    Write-Host "Rules:    $AgentsMdTarget + $RulesTarget\"
    Write-Host "MCP:      $McpServersRoot\"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart QoderCN CLI or run /skills reload"
    Write-Host "  2. Run /mcp reload to refresh MCP servers"
    Write-Host "  3. Set environment variables if needed:"
    Write-Host "     S2_API_KEY, OPENALEX_EMAIL, CROSSREF_EMAIL, NCBI_API_KEY"
    Write-Host "     CAMPUS_USERNAME, CAMPUS_PASSWORD"
}
catch {
    Write-Host ""
    Write-Host "Install failed." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    throw
}
