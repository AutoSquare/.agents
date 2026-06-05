param (
    [switch]$WhatIf,
    [switch]$SkipMcpInstall,
    [switch]$UseOfficialPipIndex,
    [string]$PipIndexUrl
)

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

$workspaceRoot = Split-Path (Split-Path $MyInvocation.MyCommand.Path)
$manifestPath = Join-Path $workspaceRoot "manifest.json"
if (-not (Test-Path $manifestPath)) {
    Write-Error "manifest.json not found in $workspaceRoot"
    exit 1
}

$manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$manifestConfig = $manifest.antigravityInstallManifest
if (-not $manifestConfig) {
    Write-Error "antigravityInstallManifest not found in manifest.json."
    exit 1
}

$targetBase = Join-Path $env:USERPROFILE ".gemini\config\plugins\agents"
$skillsTarget = Join-Path $targetBase "skills"
$mcpTarget = Join-Path $targetBase "mcp-servers"
$pluginJsonPath = Join-Path $targetBase "plugin.json"

if (-not $WhatIf) {
    New-Item -ItemType Directory -Force -Path $targetBase | Out-Null
    New-Item -ItemType Directory -Force -Path $skillsTarget | Out-Null
    New-Item -ItemType Directory -Force -Path $mcpTarget | Out-Null
}

function Resolve-PythonCommand {
    $commands = @("py -3.13", "py -3.12", "py -3.11", "py -3.10", "python3", "python")
    foreach ($cmd in $commands) {
        try {
            $parts = $cmd -split ' '
            $exe = $parts[0]
            $args = if ($parts.Length -gt 1) { $parts[1..($parts.Length-1)] + "--version" } else { "--version" }
            $output = & $exe $args 2>&1
            if ($LASTEXITCODE -eq 0 -and $output -match "Python 3\.(1[0-9]|2[0-9])") {
                return $cmd
            }
        } catch { continue }
    }
    return "python"
}

$pythonCmd = Resolve-PythonCommand
Write-Host ">>> Using Python: $pythonCmd" -ForegroundColor Cyan

Write-Host "`n>>> Copying Skills..." -ForegroundColor Cyan
foreach ($skill in $manifestConfig.managedSkills) {
    $src = Join-Path $workspaceRoot "skills\$skill"
    $dst = Join-Path $skillsTarget $skill
    Write-Host "  -> $skill"
    if (-not $WhatIf -and (Test-Path $src)) {
        Copy-Item -Path $src -Destination $skillsTarget -Recurse -Force
    }
}

$mcpServersConfig = @{}
if (Test-Path $pluginJsonPath) {
    try {
        $existingPlugin = Get-Content $pluginJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($existingPlugin.mcpServers) {
            foreach ($prop in $existingPlugin.mcpServers.PSObject.Properties) {
                $mcpServersConfig[$prop.Name] = $prop.Value
            }
        }
    } catch { 
        Write-Warning "Could not parse existing plugin.json mcpServers." 
    }
}

if (-not $SkipMcpInstall) {
    Write-Host "`n>>> Installing MCP Servers..." -ForegroundColor Cyan
    foreach ($mcp in $manifestConfig.managedMcpServers) {
        $mcpName = $mcp.name
        $mcpKind = $mcp.kind
        $sourceDir = $mcp.sourceDir
        
        if ($mcpKind -eq "npx") {
            Write-Host "  -> NPX MCP: $mcpName"
            $mcpServersConfig[$mcpName] = @{
                command = "npx"
                args = @("-y", "@botrun/mcp-ppt-generator")
            }
            continue
        }

        if (-not $sourceDir) { continue }
        
        $src = Join-Path $workspaceRoot "mcp-servers-src\$sourceDir"
        $dst = Join-Path $mcpTarget $sourceDir
        Write-Host "  -> $mcpName ($mcpKind)"
        
        if (-not $WhatIf) {
            if (Test-Path $src) {
                if (-not (Test-Path $dst)) {
                    New-Item -ItemType Directory -Force -Path $dst | Out-Null
                }
                Get-ChildItem -Path $src | Where-Object { $_.Name -notin @(".venv", "node_modules") } | Copy-Item -Destination $dst -Recurse -Force
            }
            
            if ($mcpKind -eq "python") {
                $venvPath = Join-Path $dst ".venv"
                if (-not (Test-Path $venvPath)) {
                    Write-Host "    Creating Python venv..."
                    $pyArgs = ($pythonCmd -split ' ')
                    $pyExe = $pyArgs[0]
                    $pyRest = if ($pyArgs.Length -gt 1) { $pyArgs[1..($pyArgs.Length-1)] } else { @() }
                    & $pyExe $pyRest -m venv $venvPath
                }
                $pipExe = Join-Path $venvPath "Scripts\pip.exe"
                $reqPath = Join-Path $dst "requirements.txt"
                if (Test-Path $reqPath) {
                    Write-Host "    Installing pip dependencies..."
                    $pipCmdArgs = @("install", "-r", $reqPath, "--timeout", "30")
                    if ($PipIndexUrl) {
                        $pipCmdArgs += @("-i", $PipIndexUrl)
                    } elseif (-not $UseOfficialPipIndex) {
                        $pipCmdArgs += @("-i", "https://pypi.tuna.tsinghua.edu.cn/simple")
                    }
                    $process = Start-Process -FilePath $pipExe -ArgumentList $pipCmdArgs -Wait -NoNewWindow -PassThru
                }
                
                $mcpServersConfig[$mcpName] = @{
                    command = Join-Path $venvPath "Scripts\python.exe"
                    args = @("-m", $mcpName)
                    env = @{
                        PYTHONPATH = Join-Path $dst "src"
                    }
                }
                
                if ($mcpName -eq "campus-net") {
                    $mcpServersConfig[$mcpName].args = @("-m", "campus_net_mcp")
                    Write-Host "    Installing Playwright browsers..."
                    $pythonBin = Join-Path $venvPath "Scripts\python.exe"
                    $process = Start-Process -FilePath $pythonBin -ArgumentList @("-m", "playwright", "install", "chromium") -Wait -NoNewWindow -PassThru
                }
                if ($mcpName -eq "academic-research") {
                    $mcpServersConfig[$mcpName].args = @("-m", "academic_research_mcp")
                }
            } elseif ($mcpKind -eq "node") {
                $packageJson = Join-Path $dst "package.json"
                if (Test-Path $packageJson) {
                    Write-Host "    Installing npm dependencies & building..."
                    Push-Location $dst
                    $process = Start-Process -FilePath "npm.cmd" -ArgumentList @("install") -Wait -NoNewWindow -PassThru
                    $process = Start-Process -FilePath "npm.cmd" -ArgumentList @("run", "build") -Wait -NoNewWindow -PassThru
                    Pop-Location
                }
                $mcpServersConfig[$mcpName] = @{
                    command = "node"
                    args = @(Join-Path $dst "dist\index.js")
                }
            }
        }
    }
}

Write-Host "`n>>> Aggregating Rules..." -ForegroundColor Cyan
$rulesContent = "# Antigravity Agents Bundle Rules`n`n"
$rulesBase = Join-Path $workspaceRoot "rules\antigravity"
if (Test-Path $rulesBase) {
    $mainRule = Join-Path $rulesBase "AGENTS.md"
    if (Test-Path $mainRule) {
        $rulesContent += (Get-Content $mainRule -Raw -Encoding UTF8) + "`n`n"
    }
    $rulesDir = Join-Path $rulesBase "agent-rules"
    if (Test-Path $rulesDir) {
        $ruleFiles = Get-ChildItem -Path $rulesDir -Filter "*.md" | Sort-Object Name
        foreach ($file in $ruleFiles) {
            $rulesContent += "## $($file.BaseName)`n"
            $rulesContent += (Get-Content $file.FullName -Raw -Encoding UTF8) + "`n`n"
        }
    }
}

Write-Host "`n>>> Generating plugin.json..." -ForegroundColor Cyan
$pluginConfig = [ordered]@{
    name = "agents-bundle"
    description = "Portable agent skills, rules, and MCP servers tailored for Antigravity."
    mcpServers = $mcpServersConfig
    system_prompt = $rulesContent
}

if (-not $WhatIf) {
    $json = $pluginConfig | ConvertTo-Json -Depth 5
    Set-Content -Path $pluginJsonPath -Value $json -Encoding UTF8
    Write-Host "plugin.json generated at $pluginJsonPath" -ForegroundColor Green
}

Write-Host "`n✔ Antigravity setup complete!" -ForegroundColor Green
