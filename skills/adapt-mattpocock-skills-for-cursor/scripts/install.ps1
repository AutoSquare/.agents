#Requires -Version 5.1
param(
    [string]$Source = "",
    [switch]$IncludeAll,
    [string]$Dest = ""
)

$ErrorActionPreference = "Stop"

if (-not $Dest) { $Dest = Join-Path $env:USERPROFILE ".cursor\skills" }
if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest -Force | Out-Null }

function Find-MattpocockRoot {
    param([string]$Hint)
    if ($Hint -and (Test-Path (Join-Path $Hint "skills"))) { return (Resolve-Path $Hint).Path }
    $candidates = @(
        (Join-Path (Get-Location) "mattpocock"),
        (Join-Path (Get-Location) "..\mattpocock")
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path (Join-Path $c "skills"))) { return (Resolve-Path $c).Path }
    }
    return $null
}

$root = Find-MattpocockRoot -Hint $Source
if (-not $root) {
    Write-Error "Cannot find mattpocock repo (skills/ missing). Pass -Source <path>."
}

$skillsRoot = Join-Path $root "skills"
$skipDirs = if ($IncludeAll) { @() } else { @("deprecated", "personal", "in-progress") }

$slashFrom = @(
    '/setup-matt-pocock-skills',
    '/improve-codebase-architecture',
    '/grill-with-docs',
    '/grill-me',
    '/to-issues',
    '/to-prd',
    '/zoom-out',
    '/prototype',
    '/diagnose',
    '/triage',
    '/tdd',
    '/caveman',
    '/handoff'
)

# Chinese "skill" word (ji neng) - built from char codes for script encoding safety
$cnSkill = -join @([char]0x6280, [char]0x80FD)

$slashTo = @(
    "**setup-matt-pocock-skills** $cnSkill",
    "**improve-codebase-architecture** $cnSkill",
    "**grill-with-docs** $cnSkill",
    "**grill-me** $cnSkill",
    "**to-issues** $cnSkill",
    "**to-prd** $cnSkill",
    "**zoom-out** $cnSkill",
    "**prototype** $cnSkill",
    "**diagnose** $cnSkill",
    "**triage** $cnSkill",
    "**tdd** $cnSkill",
    "**caveman** $cnSkill",
    "**handoff** $cnSkill"
)

function Convert-CursorText {
    param([string]$Text)
    $out = $Text
    $bt = [char]0x60
    for ($i = 0; $i -lt $slashFrom.Length; $i++) {
        $escaped = [regex]::Escape($slashFrom[$i])
        # Backtick-wrapped slash commands: `/triage`
        $out = $out -replace ([regex]::Escape($bt) + $escaped + [regex]::Escape($bt)), $slashTo[$i]
        # Plain slash after whitespace or line start (not paths like ../foo/)
        $out = [regex]::Replace($out, '(^|\s)' + $escaped + '(?=[\s\.,;:!?\u3002\uff09\uff0c]|$)', {
            param($m) $m.Groups[1].Value + $slashTo[$i]
        })
    }
    $out = $out -replace '~/.claude/skills', '~/.cursor/skills'
    $out = $out -replace '\.claude/settings\.json', '.cursor/hooks.json'
    $out = $out -replace 'npx skills@latest add mattpocock/skills', 'adapt-mattpocock-skills-for-cursor (install to ~/.cursor/skills/)'
    return $out
}

$textExtensions = @('.md', '.sh', '.txt', '.json', '.yaml', '.yml')

function Copy-SkillDir {
    param([string]$SrcDir, [string]$DestName)
    $target = Join-Path $Dest $DestName
    if (Test-Path $target) { Remove-Item $target -Recurse -Force }
    Copy-Item -Path $SrcDir -Destination $target -Recurse -Force
    Get-ChildItem -Path $target -Recurse -File | ForEach-Object {
        $ext = $_.Extension.ToLowerInvariant()
        if ($textExtensions -notcontains $ext) { return }
        $raw = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8
        if ($null -eq $raw) { return }
        $converted = Convert-CursorText -Text $raw
        if ($converted -ne $raw) {
            [System.IO.File]::WriteAllText($_.FullName, $converted)
        }
    }
    Write-Host ('  installed: ' + $DestName)
}

Write-Host ('Source: ' + $root)
Write-Host ('Dest:   ' + $Dest)
Write-Host ''

$installed = New-Object System.Collections.Generic.List[string]
Get-ChildItem -Path $skillsRoot -Directory | ForEach-Object {
    $bucket = $_.Name
    if ($skipDirs -contains $bucket) {
        Write-Host ('skip bucket: ' + $bucket)
        return
    }
    Get-ChildItem -Path $_.FullName -Directory | ForEach-Object {
        $skillDir = $_.FullName
        $skillMd = Join-Path $skillDir 'SKILL.md'
        if (-not (Test-Path $skillMd)) { return }
        $name = $_.Name
        if ($name -eq 'git-guardrails-claude-code') {
            $destName = 'git-guardrails'
            Copy-SkillDir -SrcDir $skillDir -DestName $destName
            $note = @"

## Cursor

Adapted from git-guardrails-claude-code. Use Cursor hooks (beforeShellExecution), not .claude/settings.json.
See: ~/.cursor/skills/adapt-mattpocock-skills-for-cursor/CURSOR-GIT-GUARDRAILS.md
"@
            $guardPath = Join-Path (Join-Path $Dest $destName) 'SKILL.md'
            Add-Content -Path $guardPath -Value $note -Encoding UTF8
            [void]$installed.Add($destName)
        } else {
            Copy-SkillDir -SrcDir $skillDir -DestName $name
            [void]$installed.Add($name)
        }
    }
}

Write-Host ''
Write-Host ('Done. Installed ' + $installed.Count + ' skills.')
$installed | Sort-Object | ForEach-Object { Write-Host ('  - ' + $_) }
Write-Host ''
Write-Host 'Restart Cursor or open a new Agent chat to load skills.'
