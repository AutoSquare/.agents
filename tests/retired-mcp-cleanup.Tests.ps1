#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

$agentsRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $agentsRoot
$failures = [System.Collections.Generic.List[string]]::new()

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )
    if (-not $Condition) {
        $failures.Add($Message)
    }
}

function Assert-Equal {
    param(
        $Expected,
        $Actual,
        [string]$Message
    )
    if ($Expected -ne $Actual) {
        $failures.Add("$Message (expected=$Expected, actual=$Actual)")
    }
}

$manifestPath = Join-Path $agentsRoot "manifest.json"
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$retiredNames = @($manifest.retiredMcpServers)
Assert-Equal 1 $retiredNames.Count "manifest.retiredMcpServers should contain one entry"
Assert-Equal "ppt-markdown" ([string]$retiredNames[0]) "ppt-markdown should be the retired MCP"

$activeCatalog = @($manifest.mcpServers.PSObject.Properties.Name)
$codexManaged = @($manifest.codexInstallManifest.managedMcpServers | ForEach-Object { [string]$_.name })
$antigravityManaged = @($manifest.antigravityInstallManifest.managedMcpServers | ForEach-Object { [string]$_.name })
$qoderManaged = @($manifest.qodercnInstallManifest.managedMcpServers | ForEach-Object { [string]$_.name })
$dshManaged = @($manifest.dshInstallManifest.managedMcpServers | ForEach-Object { [string]$_.name })
foreach ($activeNames in @($activeCatalog, $codexManaged, $antigravityManaged, $qoderManaged, $dshManaged)) {
    Assert-True (-not ($activeNames -contains "ppt-markdown")) "active MCP lists must not contain ppt-markdown"
}

$qoderRulesRoot = Join-Path $agentsRoot "rules\qoder"
foreach ($rule in @($manifest.qodercnInstallManifest.managedRules)) {
    $rulePath = Join-Path $qoderRulesRoot $rule
    Assert-True (Test-Path -LiteralPath $rulePath -PathType Leaf) "qodercn managed rule is missing: $rulePath"
    $ruleSource = Get-Content -LiteralPath $rulePath -Raw -Encoding UTF8
    Assert-True (-not $ruleSource.Contains("ppt-markdown")) "qodercn rule must not reference ppt-markdown: $rulePath"
    Assert-True (-not $ruleSource.Contains("@botrun/mcp-ppt-generator")) "qodercn rule must not reference the retired npm package: $rulePath"
}
$qoderAgentsMdPath = Join-Path $qoderRulesRoot "AGENTS.md"
Assert-True (Test-Path -LiteralPath $qoderAgentsMdPath -PathType Leaf) "qodercn AGENTS.md entry file is missing: $qoderAgentsMdPath"

$scriptPaths = @(
    (Join-Path $agentsRoot "scripts\setup-codex-agents.ps1"),
    (Join-Path $agentsRoot "scripts\setup-cursor-agents.ps1"),
    (Join-Path $agentsRoot "scripts\setup-antigravity-agents.ps1"),
    (Join-Path $agentsRoot "scripts\setup-qodercn-agents.ps1"),
    (Join-Path $agentsRoot "scripts\setup-dsh-agents.ps1")
)
foreach ($scriptPath in $scriptPaths) {
    $source = Get-Content -LiteralPath $scriptPath -Raw -Encoding UTF8
    Assert-True ($source.Contains("Invoke-RetiredMcpCleanup")) "installer must invoke retired MCP cleanup: $scriptPath"
    Assert-True ($source.Contains("retiredMcpServers")) "installer must read the centralized retired list: $scriptPath"
    Assert-True (-not $source.Contains("@botrun/mcp-ppt-generator")) "installer must not register the retired npm package: $scriptPath"
}

$configurationRecord = Get-ChildItem -LiteralPath $workspaceRoot -File | Where-Object { $_.Name -like "MCP*Skills*.md" } | Select-Object -First 1
Assert-True ($null -ne $configurationRecord) "workspace MCP and Skills configuration record should exist"

$activeReferencePaths = @(
    (Join-Path $agentsRoot "README.md"),
    (Join-Path $agentsRoot "CODEX.md"),
    (Join-Path $agentsRoot "PORTABLE.md"),
    (Join-Path $agentsRoot "ANTIGRAVITY.md"),
    (Join-Path $agentsRoot "mcp.md"),
    (Join-Path $agentsRoot "mcp.template.json"),
    (Join-Path $agentsRoot "skills.md"),
    (Join-Path $agentsRoot "workflows.md"),
    (Join-Path $agentsRoot "skills\academic-ppt-builder\SKILL.md"),
    (Join-Path $agentsRoot "rules\cursor\literature-workflow.mdc"),
    (Join-Path $agentsRoot "rules\codex-global\agent-rules\12-literature-workflow.md"),
    (Join-Path $agentsRoot "rules\antigravity\agent-rules\12-literature-workflow.md"),
    (Join-Path $agentsRoot "DSH.md"),
    (Join-Path $agentsRoot "mcp.template.dsh.yml"),
    (Join-Path $agentsRoot "rules\dsh\AGENTS.md"),
    $configurationRecord.FullName
)
foreach ($referencePath in $activeReferencePaths) {
    $source = Get-Content -LiteralPath $referencePath -Raw -Encoding UTF8
    Assert-True (-not $source.Contains("ppt-markdown")) "active documentation must not reference ppt-markdown: $referencePath"
    Assert-True (-not $source.Contains("@botrun/mcp-ppt-generator")) "active documentation must not reference the retired npm package: $referencePath"
}

$helperPath = Join-Path $agentsRoot "scripts\retired-mcp-cleanup.ps1"
if (-not (Test-Path -LiteralPath $helperPath -PathType Leaf)) {
    $failures.Add("retired MCP cleanup helper is missing: $helperPath")
} else {
    . $helperPath

    function Invoke-CleanupScenario {
        param(
            [string]$Answer,
            [switch]$WhatIf,
            [switch]$Missing,
            [switch]$InputThrows
        )
        $state = @{
            "custom-mcp" = "keep"
            "deck-builder" = "keep"
        }
        if (-not $Missing) {
            $state["ppt-markdown"] = "retired"
        }
        $promptCount = 0
        $removed = Invoke-RetiredMcpCleanup `
            -Names @("ppt-markdown") `
            -Context "test config" `
            -WhatIf:$WhatIf `
            -Exists { param($name) $state.ContainsKey($name) } `
            -Remove { param($name) [void]$state.Remove($name) } `
            -InputProvider {
                param($prompt)
                $promptCount++
                if ($InputThrows) {
                    throw "stdin unavailable"
                }
                return $Answer
            }
        return [PSCustomObject]@{
            State = $state
            PromptCount = $promptCount
            Removed = $removed
        }
    }

    $accepted = Invoke-CleanupScenario -Answer "yes"
    Assert-True (-not $accepted.State.ContainsKey("ppt-markdown")) "explicit yes should remove the retired MCP"
    Assert-True $accepted.State.ContainsKey("custom-mcp") "cleanup must preserve custom MCP entries"
    Assert-Equal 1 $accepted.Removed "explicit yes should report one removal"

    foreach ($answer in @("", "n", "invalid")) {
        $declined = Invoke-CleanupScenario -Answer $answer
        Assert-True $declined.State.ContainsKey("ppt-markdown") "non-affirmative input should preserve the retired MCP"
        Assert-Equal 0 $declined.Removed "non-affirmative input should report zero removals"
    }

    $preview = Invoke-CleanupScenario -Answer "yes" -WhatIf
    Assert-True $preview.State.ContainsKey("ppt-markdown") "WhatIf must preserve the retired MCP"
    Assert-Equal 0 $preview.PromptCount "WhatIf must not prompt"

    $missing = Invoke-CleanupScenario -Answer "yes" -Missing
    Assert-Equal 0 $missing.PromptCount "missing retired MCP must not prompt"

    $unattended = Invoke-CleanupScenario -InputThrows
    Assert-True $unattended.State.ContainsKey("ppt-markdown") "unavailable stdin must default to preserving the retired MCP"
    Assert-Equal 0 $unattended.Removed "unavailable stdin should report zero removals"
}

if ($failures.Count -gt 0) {
    Write-Host "Retired MCP cleanup tests failed ($($failures.Count)):" -ForegroundColor Red
    foreach ($failure in $failures) {
        Write-Host "  - $failure" -ForegroundColor Red
    }
    exit 1
}

Write-Host "Retired MCP cleanup tests passed." -ForegroundColor Green
