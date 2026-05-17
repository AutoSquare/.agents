#!/usr/bin/env pwsh
# Cursor 专用：将本迁移包中的 Skills 与用户级 MCP 写入 %USERPROFILE%\.cursor\（非 Claude Desktop / VS Code 通用安装）。
param(
    [switch]$SkipMcpInstall,
    [switch]$OverwriteSkills,
    [switch]$InstallRules,
    [switch]$OverwriteRules,
    [switch]$BackupMcpJson = $true
)

$ErrorActionPreference = "Stop"

$AgentsRoot = Split-Path -Parent $PSScriptRoot
$ProjectRoot = Split-Path -Parent $AgentsRoot
$CursorRoot = Join-Path $env:USERPROFILE ".cursor"
$SkillsSource = Join-Path $AgentsRoot "skills"
$SkillsTarget = Join-Path $CursorRoot "skills"
$RulesSource = Join-Path (Join-Path $AgentsRoot "rules") "cursor"
$RulesTarget = Join-Path $ProjectRoot ".cursor\rules"
$McpServersRoot = Join-Path $CursorRoot "mcp-servers"
$McpJsonPath = Join-Path $CursorRoot "mcp.json"

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Copy-Rules {
    if (-not (Test-Path $RulesSource)) {
        Write-Host "skip rules: source not found ($RulesSource)"
        return
    }
    $mdcFiles = Get-ChildItem -Path $RulesSource -Filter "*.mdc" -File -ErrorAction SilentlyContinue
    if (-not $mdcFiles -or $mdcFiles.Count -eq 0) {
        Write-Host "skip rules: no .mdc files in $RulesSource"
        return
    }
    Ensure-Directory (Join-Path $ProjectRoot ".cursor")
    Ensure-Directory $RulesTarget
    foreach ($f in $mdcFiles) {
        $target = Join-Path $RulesTarget $f.Name
        if ((Test-Path $target) -and -not $OverwriteRules) {
            Write-Host "skip rule (exists): $($f.Name)"
            continue
        }
        Copy-Item $f.FullName $target -Force
        Write-Host "installed rule -> project: $($f.Name)"
    }
    Write-Host "rules target: $RulesTarget"
}

function Copy-Skills {
    Ensure-Directory $SkillsTarget
    Get-ChildItem -Path $SkillsSource -Directory | ForEach-Object {
        $target = Join-Path $SkillsTarget $_.Name
        if ((Test-Path $target) -and -not $OverwriteSkills) {
            Write-Host "skip skill (exists): $($_.Name)"
            return
        }
        if (Test-Path $target) {
            Remove-Item $target -Recurse -Force
        }
        Copy-Item $_.FullName $target -Recurse -Force
        Write-Host "installed skill: $($_.Name)"
    }
}

function Ensure-McpRepo {
    param(
        [string]$Name,
        [string]$Url
    )
    $target = Join-Path $McpServersRoot $Name
    if (Test-Path $target) {
        return $target
    }

    $bundled = Join-Path (Join-Path $AgentsRoot "mcp-servers-src") $Name
    if (Test-Path $bundled) {
        Copy-Item $bundled $target -Recurse -Force
        Write-Host "copied bundled MCP source: $Name"
        return $target
    }

    Assert-Command "git"
    git clone $Url $target
    return $target
}

function Install-AcademicResearchMcp {
    Assert-Command "python"
    $repo = Ensure-McpRepo "academic-research-mcp" "https://github.com/alisoroushmd/academic-research-mcp.git"
    Push-Location $repo
    try {
        if (-not (Test-Path ".venv")) {
            python -m venv ".venv"
        }
        & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
        & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
    }
    finally {
        Pop-Location
    }
}

function Install-ZoteroMcp {
    Assert-Command "npm"
    $repo = Ensure-McpRepo "zotero-mcp" "https://github.com/Xpropel/zotero-mcp.git"
    Push-Location $repo
    try {
        npm install
        npm run build
    }
    finally {
        Pop-Location
    }
}

function Install-CampusNetMcp {
    Assert-Command "python"
    $bundled = Join-Path (Join-Path $AgentsRoot "mcp-servers-src") "campus-net-mcp"
    if (-not (Test-Path $bundled)) {
        throw "Bundled MCP not found: $bundled"
    }
    $dest = Join-Path $McpServersRoot "campus-net-mcp"
    if (-not (Test-Path $dest)) {
        Copy-Item $bundled $dest -Recurse -Force
        Write-Host "copied bundled MCP source: campus-net-mcp"
    }
    Push-Location $dest
    try {
        if (-not (Test-Path ".venv")) {
            python -m venv ".venv"
        }
        & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
        & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
        Write-Host "Installing Chromium for Playwright (first run may download binaries) ..."
        & ".\.venv\Scripts\python.exe" -m playwright install chromium
    }
    finally {
        Pop-Location
    }
}

function Install-DeckBuilderMcp {
    Assert-Command "npm"
    $repo = Ensure-McpRepo "deck-builder" "https://github.com/toontube/deck-builder.git"
    Push-Location $repo
    try {
        npm install
        npm run build
    }
    finally {
        Pop-Location
    }
}

function Set-McpJson {
    Ensure-Directory $CursorRoot
    if ((Test-Path $McpJsonPath) -and $BackupMcpJson) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        Copy-Item $McpJsonPath "$McpJsonPath.bak-$timestamp" -Force
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
    Write-Host "updated MCP config: $McpJsonPath"
}

Ensure-Directory $CursorRoot
Ensure-Directory $McpServersRoot

Copy-Skills

if ($InstallRules) {
    Copy-Rules
}

if (-not $SkipMcpInstall) {
    Install-AcademicResearchMcp
    Install-ZoteroMcp
    Install-DeckBuilderMcp
    Install-CampusNetMcp
}

Set-McpJson

Write-Host ""
if ($InstallRules) {
    Write-Host "Rules installed under project .cursor/rules/ (commit .cursor/rules to git if desired)."
}
Write-Host "Done. Restart Cursor, then enable/check servers in Settings > Tools & MCP."
