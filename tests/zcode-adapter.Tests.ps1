#!/usr/bin/env pwsh
# Static and preview checks for the ZCode host adapter.

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
$install = $manifest.zcodeInstallManifest
Assert-True ($null -ne $install) "manifest.json is missing zcodeInstallManifest"
Assert-Equal "portable-zcode-agents" ([string]$install.packageId) "zcodeInstallManifest.packageId"
Assert-True ((@($install.managedSkills)).Count -gt 0) "zcodeInstallManifest.managedSkills must not be empty"
Assert-Equal 14 ((@($install.managedRules)).Count) "zcodeInstallManifest.managedRules should contain 14 files"
Assert-Equal 4 ((@($install.managedMcpServers)).Count) "zcodeInstallManifest.managedMcpServers should contain 4 servers"

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

$rulesRoot = Join-Path $agentsRoot "rules\zcode"
Assert-True (Test-Path -LiteralPath (Join-Path $rulesRoot "AGENTS.md") -PathType Leaf) "rules/zcode/AGENTS.md is missing"
foreach ($rule in @($install.managedRules)) {
    Assert-True (Test-Path -LiteralPath (Join-Path $rulesRoot "rules\$rule") -PathType Leaf) "managed ZCode rule is missing: $rule"
}
$agentsBody = Get-Content -LiteralPath (Join-Path $rulesRoot "AGENTS.md") -Raw -Encoding UTF8
foreach ($needle in @("~/.zcode/rules/", "mcp__<server>__<tool>", "计划模式", "disable-model-invocation", "ExitPlanMode", "Skill")) {
    Assert-True ($agentsBody.Contains($needle)) "rules/zcode/AGENTS.md must mention: $needle"
}

$installerPath = Join-Path $agentsRoot "scripts\setup-zcode-agents.ps1"
Assert-True (Test-Path -LiteralPath $installerPath -PathType Leaf) "scripts/setup-zcode-agents.ps1 is missing"
if (Test-Path -LiteralPath $installerPath -PathType Leaf) {
    $installerSource = Get-Content -LiteralPath $installerPath -Raw -Encoding UTF8
    foreach ($needle in @("Invoke-RetiredMcpCleanup", "retiredMcpServers", "portable-agents:zcode managed rules", "pathRewriteSkills", "mcp.servers", "zcodeInstallManifest", "WhatIf")) {
        Assert-True ($installerSource.Contains($needle)) "setup-zcode-agents.ps1 must contain: $needle"
    }
}

$zcodeDocPath = Join-Path $agentsRoot "ZCODE.md"
Assert-True (Test-Path -LiteralPath $zcodeDocPath -PathType Leaf) "ZCODE.md is missing"
if (Test-Path -LiteralPath $zcodeDocPath -PathType Leaf) {
    $zcodeDoc = Get-Content -LiteralPath $zcodeDocPath -Raw -Encoding UTF8
    foreach ($needle in @("setup-zcode-agents.ps1", "mcp.servers", "mcp__", ".zcode\skills")) {
        Assert-True ($zcodeDoc.Contains($needle)) "ZCODE.md must mention: $needle"
    }
    Assert-True (-not $zcodeDoc.Contains("ppt-markdown")) "ZCODE.md must not reference the retired MCP"
}

$readme = Get-Content -LiteralPath (Join-Path $agentsRoot "README.md") -Raw -Encoding UTF8
Assert-True ($readme.Contains("ZCode")) "README.md must document the ZCode host"

# Preview run: -WhatIf must not write anything into a fresh ZCode home.
$tempHome = Join-Path ([System.IO.Path]::GetTempPath()) ("zcode-whatif-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempHome -Force | Out-Null
try {
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $installerPath -WhatIf -SkipMcpInstall -ZcodeHome $tempHome 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    Assert-Equal 0 $exitCode "setup-zcode-agents.ps1 -WhatIf should exit 0"
    $created = @(Get-ChildItem -LiteralPath $tempHome -Force -Recurse -ErrorAction SilentlyContinue)
    Assert-Equal 0 $created.Count "setup-zcode-agents.ps1 -WhatIf must not create files"
    if ($exitCode -ne 0) {
        $tail = ($output | Select-Object -Last 10) -join " | "
        $failures.Add("WhatIf output: $tail")
    }
} finally {
    Remove-Item -LiteralPath $tempHome -Recurse -Force -ErrorAction SilentlyContinue
}

if ($failures.Count -gt 0) {
    Write-Host "ZCode adapter tests failed ($($failures.Count)):" -ForegroundColor Red
    foreach ($failure in $failures) { Write-Host "  - $failure" -ForegroundColor Red }
    exit 1
}

Write-Host "ZCode adapter tests passed." -ForegroundColor Green
