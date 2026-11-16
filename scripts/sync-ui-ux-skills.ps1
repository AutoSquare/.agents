#!/usr/bin/env pwsh
# 从 ui-ux-pro-max-skill 同步 7 个 UI/UX Skill 到 <配置包根目录>/skills/，改写为 Cursor 用户级路径，并把 ckm: 技能名归一化为 kebab-case。
param(
    [string]$UpstreamPath,
    [switch]$Assemble,
    [switch]$DryRun,
    [switch]$SkipPathRewrite
)

$ErrorActionPreference = "Stop"

$AgentsRoot = Split-Path -Parent $PSScriptRoot
$SkillsTarget = Join-Path $AgentsRoot "skills"

if ($UpstreamPath) {
    $UpstreamRoot = $UpstreamPath
}
else {
    $UpstreamRoot = Join-Path (Split-Path -Parent $AgentsRoot) "ui-ux-pro-max-skill"
}

$ClaudeSkillsRoot = Join-Path $UpstreamRoot ".claude\skills"
$UiUxSrcRoot = Join-Path $UpstreamRoot "src\ui-ux-pro-max"

$SkillNames = @(
    "ui-ux-pro-max",
    "design",
    "banner-design",
    "ui-styling",
    "slides",
    "design-system",
    "brand"
)

$ClaudeKitSkills = @(
    "design",
    "banner-design",
    "ui-styling",
    "slides",
    "design-system",
    "brand"
)

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Copy-Tree {
    param(
        [string]$Source,
        [string]$Destination
    )
    if (-not (Test-Path $Source)) {
        throw "Source not found: $Source"
    }
    if ($DryRun) {
        Write-Host "[dry-run] copy: $Source -> $Destination"
        return
    }
    Ensure-Directory (Split-Path -Parent $Destination)
    if (Test-Path $Destination) {
        Remove-Item $Destination -Recurse -Force
    }
    Copy-Item $Source $Destination -Recurse -Force
}

function Invoke-PathRewrite {
    param(
        [string]$SkillRoot,
        [string]$SkillName
    )

    $cursorRoot = '$env:USERPROFILE\.cursor\skills\'
    $rewriteCount = 0

    $textExtensions = @(".md", ".cjs", ".js", ".py", ".txt")
    $files = Get-ChildItem -Path $SkillRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $textExtensions -contains $_.Extension.ToLowerInvariant() }

    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        if (-not $content) { continue }

        $original = $content

        $content = $content -replace 'python3 skills/ui-ux-pro-max/scripts/search\.py', 'python "$env:USERPROFILE\.cursor\skills\ui-ux-pro-max\scripts\search.py"'
        $content = $content -replace '~/.claude/skills/', $cursorRoot
        $content = $content -replace '\.claude/skills/', $cursorRoot

        if ($SkillName -eq "design-system") {
            $content = $content -replace 'python scripts/search-slides\.py', ('python "' + $cursorRoot + 'design-system\scripts\search-slides.py"')
        }
        if ($SkillName -eq "ui-styling") {
            $content = $content -replace 'python scripts/shadcn_add\.py', ('python "' + $cursorRoot + 'ui-styling\scripts\shadcn_add.py"')
            $content = $content -replace 'python scripts/tailwind_config_gen\.py', ('python "' + $cursorRoot + 'ui-styling\scripts\tailwind_config_gen.py"')
        }

        $content = $content -replace 'python3 ', 'python '

        if ($file.Name -eq "sync-brand-to-tokens.cjs" -and $file.DirectoryName -like "*\brand\scripts") {
            $content = $content -replace "const GENERATE_TOKENS_SCRIPT = '[^']+';", "const GENERATE_TOKENS_SCRIPT = path.join(process.env.USERPROFILE, '.cursor', 'skills', 'design-system', 'scripts', 'generate-tokens.cjs');"
        }

        $content = $content -replace 'python (\$env:USERPROFILE\\\.cursor\\skills\\[^\s\r\n"]+)', 'python "$1"'
        $content = $content -replace 'node (\$env:USERPROFILE\\\.cursor\\skills\\[^\s\r\n"]+)', 'node "$1"'
        $content = [regex]::Replace($content, '"(\$env:USERPROFILE\\\.cursor\\skills\\[^"]+)"', {
            param($m)
            '"' + ($m.Groups[1].Value -replace '/', '\') + '"'
        })

        if ($content -ne $original) {
            if (-not $DryRun) {
                Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
            }
            $rewriteCount++
        }
    }

    return $rewriteCount
}

function Invoke-SkillNameNormalize {
    param(
        [string]$SkillRoot
    )

    $skillFile = Join-Path $SkillRoot "SKILL.md"
    if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) { return $false }

    $bytes = [System.IO.File]::ReadAllBytes($skillFile)
    $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
    $content = [System.Text.Encoding]::UTF8.GetString($bytes)
    if ($hasBom) { $content = $content.Substring(1) }

    $normalized = [regex]::Replace($content, '(?m)^name:\s*ckm:([a-z0-9-]+)\s*$', 'name: $1', 1)
    if ($normalized -eq $content) { return $false }
    if (-not $DryRun) {
        $encoding = New-Object System.Text.UTF8Encoding($hasBom)
        [System.IO.File]::WriteAllText($skillFile, $normalized, $encoding)
    }
    return $true
}

function Get-CkmSkillNames {
    param([string[]]$SkillDirs)

    $hits = @()
    foreach ($dir in $SkillDirs) {
        $skillFile = Join-Path $dir "SKILL.md"
        if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) { continue }
        $content = Get-Content -LiteralPath $skillFile -Raw -Encoding UTF8
        if ($content -match '(?m)^name:\s*ckm:') { $hits += $skillFile }
    }
    return $hits
}
function Test-NoClaudePaths {
    param([string[]]$SkillDirs)

    $patterns = @('.claude/skills', '~/.claude/skills')
    $hits = @()

    $textExtensions = @(".md", ".cjs", ".js", ".py", ".txt")

    foreach ($dir in $SkillDirs) {
        if (-not (Test-Path $dir)) { continue }
        $files = Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $textExtensions -contains $_.Extension.ToLowerInvariant() }
        foreach ($file in $files) {
            foreach ($pattern in $patterns) {
                $match = Select-String -Path $file.FullName -Pattern $pattern -SimpleMatch -ErrorAction SilentlyContinue
                if ($match) {
                    foreach ($m in $match) {
                        $hits += "$($m.Path):$($m.LineNumber): $pattern"
                    }
                }
            }
        }
    }

    return $hits
}

if (-not (Test-Path $UpstreamRoot)) {
    throw "Upstream not found: $UpstreamRoot`nUse -UpstreamPath to point at ui-ux-pro-max-skill."
}

if (-not (Test-Path $ClaudeSkillsRoot)) {
    throw "Claude skills root not found: $ClaudeSkillsRoot"
}

Write-Host "Upstream: $UpstreamRoot"
Write-Host "Target:   $SkillsTarget"

if ($Assemble) {
    $assembleScript = Join-Path $UpstreamRoot "scripts\assemble_skill_md.py"
    if (-not (Test-Path $assembleScript)) {
        throw "assemble script not found: $assembleScript"
    }
    if ($DryRun) {
        Write-Host "[dry-run] python $assembleScript"
    }
    else {
        Push-Location $UpstreamRoot
        try {
            python $assembleScript
            Write-Host "assembled ui-ux-pro-max SKILL.md"
        }
        finally {
            Pop-Location
        }
    }
}

$syncedDirs = @()
$totalRewrites = 0

foreach ($name in $ClaudeKitSkills) {
    $source = Join-Path $ClaudeSkillsRoot $name
    $target = Join-Path $SkillsTarget $name
    Copy-Tree -Source $source -Destination $target
    $syncedDirs += $target
    Write-Host "synced: $name"
}
$normalizedCount = 0
foreach ($name in $ClaudeKitSkills) {
    if (Invoke-SkillNameNormalize -SkillRoot (Join-Path $SkillsTarget $name)) {
        $normalizedCount++
        Write-Host "name normalize: $name (ckm: prefix removed)"
    }
}

$uiUxTarget = Join-Path $SkillsTarget "ui-ux-pro-max"
if (-not $DryRun) {
    Ensure-Directory $uiUxTarget
    Copy-Item (Join-Path $ClaudeSkillsRoot "ui-ux-pro-max\SKILL.md") (Join-Path $uiUxTarget "SKILL.md") -Force
    Copy-Tree -Source (Join-Path $UiUxSrcRoot "data") -Destination (Join-Path $uiUxTarget "data")
    Copy-Tree -Source (Join-Path $UiUxSrcRoot "scripts") -Destination (Join-Path $uiUxTarget "scripts")
}
else {
    Write-Host "[dry-run] ui-ux-pro-max: SKILL.md + data + scripts"
}
$syncedDirs += $uiUxTarget
Write-Host "synced: ui-ux-pro-max (with data/scripts from src)"

if (-not $SkipPathRewrite) {
    foreach ($name in $SkillNames) {
        $skillRoot = Join-Path $SkillsTarget $name
        if (-not (Test-Path $skillRoot)) { continue }
        $count = Invoke-PathRewrite -SkillRoot $skillRoot -SkillName $name
        $totalRewrites += $count
        Write-Host "path rewrite: $name ($count files)"
    }
}
else {
    Write-Host "skip path rewrite (-SkipPathRewrite)"
}

if (-not $DryRun) {
    $hits = Test-NoClaudePaths -SkillDirs $syncedDirs
    if ($hits.Count -gt 0) {
        Write-Warning "Residual Claude paths found ($($hits.Count)):"
        $hits | Select-Object -First 20 | ForEach-Object { Write-Warning $_ }
        throw "Path rewrite incomplete. Fix sync-ui-ux-skills.ps1 or upstream content."
    }
    Write-Host "path verify: OK (no .claude/skills or ~/.claude/skills in synced skills)"

    $ckmHits = Get-CkmSkillNames -SkillDirs $syncedDirs
    if ($ckmHits.Count -gt 0) {
        Write-Warning "Residual ckm: skill names found ($($ckmHits.Count)):"
        $ckmHits | ForEach-Object { Write-Warning $_ }
        throw "Skill name normalization incomplete. Fix sync-ui-ux-skills.ps1."
    }
    Write-Host "name verify: OK (no ckm: prefixed skill names)"
}

$fileCount = 0
$sizeBytes = 0
foreach ($name in $SkillNames) {
    $dir = Join-Path $SkillsTarget $name
    if (Test-Path $dir) {
        $files = Get-ChildItem $dir -Recurse -File
        $fileCount += $files.Count
        $sizeBytes += ($files | Measure-Object -Property Length -Sum).Sum
    }
}

Write-Host ""
Write-Host "Summary:"
Write-Host "  skills:     $($SkillNames -join ', ')"
Write-Host "  files:      $fileCount"
Write-Host "  size (MB):  $([math]::Round($sizeBytes / 1MB, 2))"
Write-Host "  rewrites:   $totalRewrites file(s)"
Write-Host "  names:      $normalizedCount normalized"
if ($DryRun) {
    Write-Host "  mode:       dry-run (no files written)"
}
