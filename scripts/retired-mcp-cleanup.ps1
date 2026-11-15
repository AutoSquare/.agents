function Invoke-RetiredMcpCleanup {
    [CmdletBinding()]
    param(
        [string[]]$Names,
        [string]$Context,
        [scriptblock]$Exists,
        [scriptblock]$Remove,
        [switch]$WhatIf,
        [scriptblock]$InputProvider
    )

    $removedCount = 0
    $customInputProvider = $null -ne $InputProvider
    if (-not $customInputProvider) {
        $InputProvider = { param($prompt) Read-Host $prompt }
    }

    foreach ($name in @($Names)) {
        if ([string]::IsNullOrWhiteSpace($name) -or -not (& $Exists $name)) {
            continue
        }
        if ($WhatIf) {
            Write-Host "[WhatIf] retired MCP found in ${Context}: $name; a normal run will ask before removal."
            continue
        }
        if (-not $customInputProvider -and [Console]::IsInputRedirected) {
            Write-Warning "Retired MCP kept because interactive confirmation is unavailable (${Context}): $name"
            continue
        }

        try {
            $answer = & $InputProvider "Retired MCP '$name' found in $Context. Remove it? [y/N]"
        } catch {
            Write-Warning "Retired MCP kept because confirmation could not be read (${Context}): $name"
            continue
        }

        $normalized = if ($null -eq $answer) { "" } else { ([string]$answer).Trim().ToLowerInvariant() }
        if ($normalized -notin @("y", "yes")) {
            Write-Host "  kept retired MCP: $name"
            continue
        }

        & $Remove $name
        $removedCount++
        Write-Host "  removed retired MCP: $name"
    }

    return $removedCount
}
