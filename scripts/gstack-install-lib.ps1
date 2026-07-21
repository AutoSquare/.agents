# gstack integration shared by the Codex and Cursor installers.
# Dot-source this file, then call Install-GstackBundle.

function Get-GstackRequiredBinaries {
    return @(
        "browse\dist\browse",
        "browse\dist\find-browse",
        "design\dist\design",
        "make-pdf\dist\pdf",
        "bin\gstack-global-discover",
        "browse\dist\server-node.mjs",
        "browse\dist\bun-polyfill.cjs"
    )
}

function Test-GstackRuntimeReady {
    param([Parameter(Mandatory = $true)][string]$RuntimeRoot)

    foreach ($relativePath in Get-GstackRequiredBinaries) {
        if (-not (Test-Path -LiteralPath (Join-Path $RuntimeRoot $relativePath) -PathType Leaf)) {
            return $false
        }
    }
    return $true
}

function Invoke-GstackBun {
    param(
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    Push-Location -LiteralPath $WorkingDirectory
    try {
        $bun = Get-Command "bun" -ErrorAction SilentlyContinue
        if ($bun) {
            & $bun.Source @Arguments
        } else {
            $npx = Get-Command "npx.cmd" -ErrorAction SilentlyContinue
            if (-not $npx) {
                $npx = Get-Command "npx" -ErrorAction SilentlyContinue
            }
            if (-not $npx) {
                throw "gstack runtime build requires Bun, or Node.js/npm so npx can download Bun."
            }
            & $npx.Source --yes bun @Arguments
        }
        if ($LASTEXITCODE -ne 0) {
            throw "gstack Bun command failed (exit $LASTEXITCODE): $($Arguments -join ' ')"
        }
    } finally {
        Pop-Location
    }
}

function Move-GstackWindowsExecutable {
    param([Parameter(Mandatory = $true)][string]$PathWithoutExtension)

    $exePath = "$PathWithoutExtension.exe"
    if (Test-Path -LiteralPath $exePath -PathType Leaf) {
        if (Test-Path -LiteralPath $PathWithoutExtension) {
            Remove-Item -LiteralPath $PathWithoutExtension -Force
        }
        Move-Item -LiteralPath $exePath -Destination $PathWithoutExtension -Force
    }
}

function Build-GstackRuntime {
    param([Parameter(Mandatory = $true)][string]$RuntimeRoot)

    Write-Host "Building gstack runtime (first install or version change)..." -ForegroundColor Cyan
    Invoke-GstackBun -WorkingDirectory $RuntimeRoot -Arguments @("install", "--frozen-lockfile")

    $extensionLib = Join-Path $RuntimeRoot "extension\lib"
    New-Item -ItemType Directory -Path $extensionLib -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $RuntimeRoot "node_modules\xterm\lib\xterm.js") -Destination (Join-Path $extensionLib "xterm.js") -Force
    Copy-Item -LiteralPath (Join-Path $RuntimeRoot "node_modules\xterm\css\xterm.css") -Destination (Join-Path $extensionLib "xterm.css") -Force
    Copy-Item -LiteralPath (Join-Path $RuntimeRoot "node_modules\xterm-addon-fit\lib\xterm-addon-fit.js") -Destination (Join-Path $extensionLib "xterm-addon-fit.js") -Force

    $builds = @(
        @("browse/src/cli.ts", "browse/dist/browse"),
        @("browse/src/find-browse.ts", "browse/dist/find-browse"),
        @("design/src/cli.ts", "design/dist/design"),
        @("make-pdf/src/cli.ts", "make-pdf/dist/pdf"),
        @("bin/gstack-global-discover.ts", "bin/gstack-global-discover")
    )
    foreach ($build in $builds) {
        $outputPath = Join-Path $RuntimeRoot $build[1]
        New-Item -ItemType Directory -Path (Split-Path -Parent $outputPath) -Force | Out-Null
        Invoke-GstackBun -WorkingDirectory $RuntimeRoot -Arguments @(
            "build", "--compile", $build[0], "--outfile", $build[1]
        )
        Move-GstackWindowsExecutable -PathWithoutExtension $outputPath
    }

    Invoke-GstackBun -WorkingDirectory $RuntimeRoot -Arguments @(
        "build",
        "browse/src/server.ts",
        "--target=node",
        "--outfile", "browse/dist/server-node.mjs",
        "--external", "playwright",
        "--external", "playwright-core",
        "--external", "diff",
        "--external", "bun:sqlite",
        "--external", "@ngrok/ngrok"
    )

    $serverPath = Join-Path $RuntimeRoot "browse\dist\server-node.mjs"
    $serverText = [System.IO.File]::ReadAllText($serverPath)
    $serverText = $serverText.Replace("import.meta.dir", "__browseNodeSrcDir")
    $serverText = $serverText.Replace(
        'import { Database } from "bun:sqlite";',
        'const Database = null; // bun:sqlite stubbed on Node'
    )
    $firstNewline = $serverText.IndexOf("`n")
    if ($firstNewline -lt 0) {
        throw "gstack Node server bundle has an unexpected format: $serverPath"
    }
    $compatibilityHeader = @'
// -- Windows Node.js compatibility (auto-generated) --
import { fileURLToPath as _ftp } from "node:url";
import { dirname as _dn } from "node:path";
const __browseNodeSrcDir = _dn(_dn(_ftp(import.meta.url))) + "/src";
{ const _r = createRequire(import.meta.url); _r("./bun-polyfill.cjs"); }
// -- end compatibility --
'@
    $serverText = $serverText.Substring(0, $firstNewline + 1) + $compatibilityHeader + "`n" + $serverText.Substring($firstNewline + 1)
    [System.IO.File]::WriteAllText($serverPath, $serverText, [System.Text.UTF8Encoding]::new($false))
    Copy-Item -LiteralPath (Join-Path $RuntimeRoot "browse\src\bun-polyfill.cjs") -Destination (Join-Path $RuntimeRoot "browse\dist\bun-polyfill.cjs") -Force

    $version = (Get-Content -LiteralPath (Join-Path $RuntimeRoot "VERSION") -Raw -Encoding UTF8).Trim()
    foreach ($relativePath in @("browse\dist\.version", "design\dist\.version", "make-pdf\dist\.version")) {
        [System.IO.File]::WriteAllText((Join-Path $RuntimeRoot $relativePath), "$version`n", [System.Text.UTF8Encoding]::new($false))
    }

    if (-not (Test-GstackRuntimeReady -RuntimeRoot $RuntimeRoot)) {
        throw "gstack runtime build completed but required artifacts are missing: $RuntimeRoot"
    }
}

function Install-GstackBundle {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("codex", "cursor")][string]$TargetHost,
        [Parameter(Mandatory = $true)][string]$AgentsRoot,
        [Parameter(Mandatory = $true)][string]$SkillsTarget,
        [switch]$WhatIf,
        [switch]$SkipBuild
    )

    $manifestPath = Join-Path $AgentsRoot "manifest.json"
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $integration = $manifest.gstackIntegration
    if (-not $integration) {
        throw "gstackIntegration missing in manifest.json"
    }

    $managedSkills = @($integration.selectedSkills)
    $hostSkillsSource = Join-Path $AgentsRoot ("host-skills\{0}" -f $TargetHost)
    $runtimeSource = Join-Path $AgentsRoot ([string]$integration.runtimeSourceDir)
    $runtimeTarget = Join-Path $SkillsTarget "gstack"
    $markerPath = Join-Path $runtimeTarget ".portable-agents-managed.json"
    $sourceVersion = (Get-Content -LiteralPath (Join-Path $runtimeSource "VERSION") -Raw -Encoding UTF8).Trim()
    $count = 0

    if (-not $WhatIf -and (Test-Path -LiteralPath $runtimeTarget)) {
        $preflightManaged = Test-Path -LiteralPath $markerPath -PathType Leaf
        $preflightReady = Test-GstackRuntimeReady -RuntimeRoot $runtimeTarget
        $preflightVersion = ""
        if (Test-Path -LiteralPath (Join-Path $runtimeTarget "VERSION") -PathType Leaf) {
            $preflightVersion = (Get-Content -LiteralPath (Join-Path $runtimeTarget "VERSION") -Raw -Encoding UTF8).Trim()
        }
        if (-not $preflightManaged -and -not ($preflightVersion -eq $sourceVersion -and $preflightReady)) {
            throw "An unmanaged gstack runtime already exists at $runtimeTarget. Move it aside or install a compatible v$sourceVersion runtime before rerunning."
        }
    }

    foreach ($name in $managedSkills) {
        $source = Join-Path $hostSkillsSource $name
        $target = Join-Path $SkillsTarget $name
        if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md") -PathType Leaf)) {
            throw "gstack host skill source missing: $source"
        }
        if ($WhatIf) {
            Write-DetailLog "[WhatIf] would update gstack skill: $name"
        } else {
            if (Test-Path -LiteralPath $target) {
                Remove-Item -LiteralPath $target -Recurse -Force
            }
            Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
            Write-DetailLog "updated gstack skill: $name"
        }
        $count++
    }

    if ($WhatIf) {
        Write-DetailLog "[WhatIf] would install gstack runtime v${sourceVersion}: $runtimeTarget"
        return [PSCustomObject]@{ SkillCount = $count; RuntimeReady = $false; BuildSkipped = [bool]$SkipBuild }
    }

    $runtimeReady = Test-GstackRuntimeReady -RuntimeRoot $runtimeTarget
    $targetVersion = ""
    if (Test-Path -LiteralPath (Join-Path $runtimeTarget "VERSION") -PathType Leaf) {
        $targetVersion = (Get-Content -LiteralPath (Join-Path $runtimeTarget "VERSION") -Raw -Encoding UTF8).Trim()
    }
    $isManaged = Test-Path -LiteralPath $markerPath -PathType Leaf

    if ((Test-Path -LiteralPath $runtimeTarget) -and -not $isManaged) {
        if ($targetVersion -eq $sourceVersion -and $runtimeReady) {
            Write-DetailLog "reused compatible unmanaged gstack runtime v${targetVersion}: $runtimeTarget"
            return [PSCustomObject]@{ SkillCount = $count; RuntimeReady = $true; BuildSkipped = $true }
        }
        throw "An unmanaged gstack runtime already exists at $runtimeTarget. Move it aside or install a compatible v$sourceVersion runtime before rerunning."
    }

    if ($isManaged -and $targetVersion -eq $sourceVersion -and $runtimeReady) {
        Write-DetailLog "gstack runtime already ready: v$targetVersion"
        return [PSCustomObject]@{ SkillCount = $count; RuntimeReady = $true; BuildSkipped = $true }
    }

    if (Test-Path -LiteralPath $runtimeTarget) {
        Remove-Item -LiteralPath $runtimeTarget -Recurse -Force
    }
    Copy-Item -LiteralPath $runtimeSource -Destination $runtimeTarget -Recurse -Force

    if ($SkipBuild) {
        Register-InstallWarning "gstack runtime source installed but binaries were not built (-SkipGstackBuild)."
    } else {
        Build-GstackRuntime -RuntimeRoot $runtimeTarget
        $runtimeReady = $true
    }

    $marker = [ordered]@{
        package = "portable-agents"
        source = [string]$manifest.skillSources.gstack.source
        version = $sourceVersion
        host = $TargetHost
        runtimeReady = [bool]$runtimeReady
    } | ConvertTo-Json
    [System.IO.File]::WriteAllText($markerPath, "$marker`n", [System.Text.UTF8Encoding]::new($false))
    Write-DetailLog "installed gstack runtime v${sourceVersion}: $runtimeTarget"

    return [PSCustomObject]@{ SkillCount = $count; RuntimeReady = [bool]$runtimeReady; BuildSkipped = [bool]$SkipBuild }
}
