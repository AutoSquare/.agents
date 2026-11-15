#!/usr/bin/env pwsh
# Static and preview checks for the DeepSeek Harness (DSH) host adapter.

$ErrorActionPreference = "Stop"

$agentsRoot = Split-Path -Parent $PSScriptRoot
$failures = [System.Collections.Generic.List[string]]::new()

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { $failures.Add($Message) }
}

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    if ($Expected -ne $Actual) { $failures.Add("$Message (expected=$Expected, actual=$Actual)") }
}

function Read-SkillFrontmatter {
    param([string]$Path)
    $text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    $match = [regex]::Match($text, "(?s)^\uFEFF?---\r?\n(.*?)\r?\n---")
    if (-not $match.Success) { return $null }
    $frontmatter = $match.Groups[1].Value
    return [pscustomobject]@{
        Name = [regex]::Match($frontmatter, "(?m)^name:\s*(.+)$").Groups[1].Value.Trim().Trim('"', "'")
        HasDescription = $frontmatter -match "(?m)^description:"
        Raw = $frontmatter
    }
}

$manifestPath = Join-Path $agentsRoot "manifest.json"
Assert-True (Test-Path -LiteralPath $manifestPath -PathType Leaf) "manifest.json is missing"
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$install = $manifest.dshInstallManifest
Assert-True ($null -ne $install) "manifest.json is missing dshInstallManifest"
Assert-Equal "portable-dsh-agents" ([string]$install.packageId) "dshInstallManifest.packageId"
Assert-True ((@($install.managedSkills)).Count -gt 0) "dshInstallManifest.managedSkills must not be empty"
Assert-Equal 14 ((@($install.managedRules)).Count) "dshInstallManifest.managedRules should contain 14 files"
Assert-Equal 4 ((@($install.managedMcpServers)).Count) "dshInstallManifest.managedMcpServers should contain 4 servers"

$skillsRoot = Join-Path $agentsRoot "skills"
$dirNameExceptions = @{ "git-guardrails" = "git-guardrails-claude-code" }
$skillNamePattern = "^[a-z0-9]+(-[a-z0-9]+)*$"
foreach ($name in @($install.managedSkills)) {
    $skillFile = Join-Path $skillsRoot "$name\SKILL.md"
    Assert-True (Test-Path -LiteralPath $skillFile -PathType Leaf) "managed skill is missing SKILL.md: $name"
    if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) { continue }
    $frontmatter = Read-SkillFrontmatter -Path $skillFile
    Assert-True ($null -ne $frontmatter) "managed skill has no valid frontmatter: $name"
    if ($null -eq $frontmatter) { continue }
    Assert-True ($frontmatter.Name -match $skillNamePattern) "managed skill name must be kebab-case: $name -> '$($frontmatter.Name)'"
    Assert-True (-not $frontmatter.Name.StartsWith("ckm:")) "managed skill must not keep a ckm: prefix: $name"
    Assert-True $frontmatter.HasDescription "managed skill must have a description: $name"
    $expectedName = $name
    if ($dirNameExceptions.ContainsKey($name)) { $expectedName = $dirNameExceptions[$name] }
    Assert-Equal $expectedName $frontmatter.Name "managed skill name should match its directory: $name"
}

foreach ($name in @($install.pathRewriteSkills)) {
    Assert-True ((@($install.managedSkills)) -contains $name) "pathRewriteSkills entry is not managed: $name"
    Assert-True (Test-Path -LiteralPath (Join-Path $skillsRoot $name) -PathType Container) "pathRewriteSkills entry directory is missing: $name"
}

$rulesRoot = Join-Path $agentsRoot "rules\dsh"
Assert-True (Test-Path -LiteralPath (Join-Path $rulesRoot "AGENTS.md") -PathType Leaf) "rules/dsh/AGENTS.md is missing"
foreach ($rule in @($install.managedRules)) {
    Assert-True (Test-Path -LiteralPath (Join-Path $rulesRoot "rules\$rule") -PathType Leaf) "managed DSH rule is missing: $rule"
}
$agentsBody = Get-Content -LiteralPath (Join-Path $rulesRoot "AGENTS.md") -Raw -Encoding UTF8
foreach ($needle in @("exit_plan_mode", "~/.dsh/rules/", "mcp__<server>__<tool>", "disable-model-invocation")) {
    Assert-True ($agentsBody.Contains($needle)) "rules/dsh/AGENTS.md must mention: $needle"
}

$installerPath = Join-Path $agentsRoot "scripts\setup-dsh-agents.ps1"
Assert-True (Test-Path -LiteralPath $installerPath -PathType Leaf) "scripts/setup-dsh-agents.ps1 is missing"
if (Test-Path -LiteralPath $installerPath -PathType Leaf) {
    $installerSource = Get-Content -LiteralPath $installerPath -Raw -Encoding UTF8
    foreach ($needle in @("Invoke-RetiredMcpCleanup", "retiredMcpServers", "portable-agents:dsh mcp managed", "pathRewriteSkills", "Test-PatchYaml", "WhatIf")) {
        Assert-True ($installerSource.Contains($needle)) "setup-dsh-agents.ps1 must contain: $needle"
    }
}

$templatePath = Join-Path $agentsRoot "mcp.template.dsh.yml"
Assert-True (Test-Path -LiteralPath $templatePath -PathType Leaf) "mcp.template.dsh.yml is missing"
if (Test-Path -LiteralPath $templatePath -PathType Leaf) {
    $template = Get-Content -LiteralPath $templatePath -Raw -Encoding UTF8
    foreach ($needle in @("@deepseek-ai/dsh-mcp-client", "{{DSH_HOME}}", "{{NODE}}", "CAMPNET_USER_ROOT", "insert:", "serverName: academic-research", "serverName: zotero", "serverName: deck-builder", "serverName: campus-net")) {
        Assert-True ($template.Contains($needle)) "mcp.template.dsh.yml must contain: $needle"
    }
    Assert-True (-not $template.Contains("ppt-markdown")) "mcp.template.dsh.yml must not reference the retired MCP"
}

$dshToolsPath = Join-Path $agentsRoot "skills\using-superpowers\references\dsh-tools.md"
Assert-True (Test-Path -LiteralPath $dshToolsPath -PathType Leaf) "using-superpowers/references/dsh-tools.md is missing"
if (Test-Path -LiteralPath $dshToolsPath -PathType Leaf) {
    $dshTools = Get-Content -LiteralPath $dshToolsPath -Raw -Encoding UTF8
    foreach ($needle in @("todo_write", "subagent", "ask_user_question", "exit_plan_mode", "mcp__<serverName>__<toolName>")) {
        Assert-True ($dshTools.Contains($needle)) "dsh-tools.md must mention: $needle"
    }
}

$dshDocPath = Join-Path $agentsRoot "DSH.md"
Assert-True (Test-Path -LiteralPath $dshDocPath -PathType Leaf) "DSH.md is missing"
if (Test-Path -LiteralPath $dshDocPath -PathType Leaf) {
    $dshDoc = Get-Content -LiteralPath $dshDocPath -Raw -Encoding UTF8
    foreach ($needle in @("setup-dsh-agents.ps1", "cordis.patch.yml", "mcp__", ".dsh\skills")) {
        Assert-True ($dshDoc.Contains($needle)) "DSH.md must mention: $needle"
    }
}

$readme = Get-Content -LiteralPath (Join-Path $agentsRoot "README.md") -Raw -Encoding UTF8
Assert-True ($readme.Contains("DeepSeek Harness")) "README.md must document the DSH host"

# Preview run: -WhatIf must not write anything into a fresh DSH home.
$tempHome = Join-Path ([System.IO.Path]::GetTempPath()) ("dsh-whatif-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempHome -Force | Out-Null
try {
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $installerPath -WhatIf -SkipMcpInstall -DshHome $tempHome 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    Assert-Equal 0 $exitCode "setup-dsh-agents.ps1 -WhatIf should exit 0"
    $created = @(Get-ChildItem -LiteralPath $tempHome -Force -Recurse -ErrorAction SilentlyContinue)
    Assert-Equal 0 $created.Count "setup-dsh-agents.ps1 -WhatIf must not create files"
    if ($exitCode -ne 0) {
        $tail = ($output | Select-Object -Last 10) -join " | "
        $failures.Add("WhatIf output: $tail")
    }
} finally {
    Remove-Item -LiteralPath $tempHome -Recurse -Force -ErrorAction SilentlyContinue
}

if ($failures.Count -gt 0) {
    Write-Host "DSH adapter tests failed ($($failures.Count)):" -ForegroundColor Red
    foreach ($failure in $failures) { Write-Host "  - $failure" -ForegroundColor Red }
    exit 1
}

Write-Host "DSH adapter tests passed." -ForegroundColor Green
