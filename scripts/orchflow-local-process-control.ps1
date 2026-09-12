param(
    [ValidateSet("status", "start", "stop", "restart", "run-api", "run-web")]
    [string] $Action = "status"
)

$ErrorActionPreference = "Stop"

$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$WebDir = Join-Path $RootDir "interface\web"

$config = @{
    ORCHFLOW_API_HOST = "localhost"
    ORCHFLOW_API_PORT = "8000"
    ORCHFLOW_RUNTIME_DIR = "runtime"
    ORCHFLOW_WEB_HOST = "localhost"
    ORCHFLOW_WEB_PORT = "5174"
    ORCHFLOW_WEB_URL = ""
}

function Read-OrchFlowEnv {
    param([string] $Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if ($trimmed.Length -eq 0 -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) {
            continue
        }

        $name, $value = $trimmed.Split("=", 2)
        $key = $name.Trim().ToUpperInvariant()
        if (-not $config.ContainsKey($key)) {
            continue
        }

        $config[$key] = $value.Trim().Trim('"')
    }
}

function Read-ProcessEnvOverrides {
    foreach ($key in @($config.Keys)) {
        $value = [System.Environment]::GetEnvironmentVariable($key)
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            $config[$key] = $value
        }
    }
}

function Resolve-OrchFlowPath {
    param([string] $Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RootDir $Path))
}

function Require-Tool {
    param(
        [string] $Name,
        [string] $Hint
    )

    if ($null -eq (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host "[error] Required tool not found: $Name"
        Write-Host "        $Hint"
        exit 1
    }
}

function Get-TrackedPid {
    param([string] $PidFile)

    if (-not (Test-Path -LiteralPath $PidFile)) {
        return $null
    }

    $rawPid = (Get-Content -LiteralPath $PidFile -TotalCount 1).Trim()
    $pidValue = 0
    if (-not [int]::TryParse($rawPid, [ref] $pidValue)) {
        return $null
    }

    return $pidValue
}

function Get-TrackedProcess {
    param([int] $ProcessId)

    return Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
}

function Test-OwnedProcess {
    param(
        [int] $ProcessId,
        [string] $MetadataFile
    )

    $process = Get-TrackedProcess -ProcessId $ProcessId
    if ($null -eq $process) {
        return $false
    }

    if (-not (Test-Path -LiteralPath $MetadataFile)) {
        return $false
    }

    try {
        $metadata = Get-Content -LiteralPath $MetadataFile -Raw | ConvertFrom-Json
    } catch {
        return $false
    }

    $startedAtUtc = $process.StartTime.ToUniversalTime().ToString("o")
    if ($metadata.pid -ne $ProcessId) {
        return $false
    }

    if ($metadata.processName -ne $process.ProcessName) {
        return $false
    }

    if ($metadata.startedAtUtc -ne $startedAtUtc) {
        return $false
    }

    return $true
}

function Write-ProcessMetadata {
    param(
        [string] $MetadataFile,
        [System.Diagnostics.Process] $Process,
        [string] $Name,
        [string] $Port
    )

    $metadata = [ordered]@{
        name = $Name
        pid = $Process.Id
        processName = $Process.ProcessName
        startedAtUtc = $Process.StartTime.ToUniversalTime().ToString("o")
        port = $Port
    }
    $metadata | ConvertTo-Json | Set-Content -LiteralPath $MetadataFile -Encoding ascii
}

function Get-ListeningPid {
    param([string] $Port)

    $portNumber = [int]$Port
    $connections = Get-NetTCPConnection -LocalPort $portNumber -State Listen -ErrorAction SilentlyContinue
    if ($null -ne $connections) {
        $owners = @($connections | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -gt 0 })
        if ($owners.Count -gt 0) {
            return [int]$owners[0]
        }
    }

    $netstatLines = netstat -ano | Select-String ":$Port\s"
    foreach ($line in $netstatLines) {
        $parts = ($line.ToString() -split "\s+") | Where-Object { $_ }
        if ($parts.Count -ge 5 -and $parts[3] -eq "LISTENING" -and $parts[4] -match "^\d+$") {
            return [int]$parts[4]
        }
    }

    return $null
}

function Write-ServiceCommand {
    param(
        [string] $Path,
        [string] $WorkingDirectory,
        [string[]] $Lines
    )

    $content = @(
        "@echo off",
        "cd /d `"$WorkingDirectory`""
    ) + $Lines
    Set-Content -LiteralPath $Path -Value $content -Encoding ascii
}

function Write-ProcessStatus {
    param(
        [string] $Name,
        [string] $PidFile,
        [string] $MetadataFile
    )

    $trackedPid = Get-TrackedPid -PidFile $PidFile
    if ($null -eq $trackedPid) {
        Write-Host "[stopped] $Name"
        return $true
    }

    $process = Get-TrackedProcess -ProcessId $trackedPid
    if ($null -eq $process) {
        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $MetadataFile -Force -ErrorAction SilentlyContinue
        Write-Host "[stopped] $Name (removed stale pid $trackedPid)"
        return $true
    }

    if (-not (Test-OwnedProcess -ProcessId $trackedPid -MetadataFile $MetadataFile)) {
        Write-Host "[unmanaged] $Name pid $trackedPid was not started by OrchFlow control; leaving pid file untouched."
        return $false
    }

    Write-Host "[running] $Name (pid $trackedPid)"
    return $true
}

function Stop-TrackedProcess {
    param(
        [string] $Name,
        [string] $PidFile,
        [string] $MetadataFile
    )

    $trackedPid = Get-TrackedPid -PidFile $PidFile
    if ($null -eq $trackedPid) {
        Write-Host "[stopped] $Name"
        return $true
    }

    $process = Get-TrackedProcess -ProcessId $trackedPid
    if ($null -eq $process) {
        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $MetadataFile -Force -ErrorAction SilentlyContinue
        Write-Host "[stopped] $Name (removed stale pid $trackedPid)"
        return $true
    }

    if (-not (Test-OwnedProcess -ProcessId $trackedPid -MetadataFile $MetadataFile)) {
        Write-Host "[blocked] $Name pid $trackedPid was not started by OrchFlow control. Stop it manually if needed."
        return $false
    }

    Write-Host "Stopping $Name pid $trackedPid ..."
    & taskkill /PID $trackedPid /T /F | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[error] Could not stop $Name pid $trackedPid."
        return $false
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $MetadataFile -Force -ErrorAction SilentlyContinue
    Write-Host "[stopped] $Name"
    return $true
}

function Test-StartPortAvailable {
    param(
        [string] $Name,
        [string] $PidFile,
        [string] $MetadataFile,
        [string] $Port
    )

    $listeningPid = Get-ListeningPid -Port $Port
    if ($null -eq $listeningPid) {
        return $true
    }

    $trackedPid = Get-TrackedPid -PidFile $PidFile
    if ($null -ne $trackedPid -and $trackedPid -eq $listeningPid -and (Test-OwnedProcess -ProcessId $trackedPid -MetadataFile $MetadataFile)) {
        return $true
    }

    Write-Host "[blocked] $Name port $Port is already in use by pid $listeningPid."
    Write-Host "          OrchFlow control will not track or stop a process it did not start."
    return $false
}

function Test-StartPortsAvailable {
    $apiAvailable = Test-StartPortAvailable -Name "API" -PidFile $apiPidFile -MetadataFile $apiMetadataFile -Port $config.ORCHFLOW_API_PORT
    $webAvailable = Test-StartPortAvailable -Name "Web" -PidFile $webPidFile -MetadataFile $webMetadataFile -Port $config.ORCHFLOW_WEB_PORT

    return $apiAvailable -and $webAvailable
}

function Start-TrackedProcess {
    param(
        [string] $Name,
        [string] $PidFile,
        [string] $MetadataFile,
        [string] $RequiredTool,
        [string] $ToolHint,
        [string] $CommandFile,
        [string] $WorkingDirectory,
        [string[]] $CommandLines,
        [string] $Port,
        [string] $LogFile
    )

    Require-Tool -Name $RequiredTool -Hint $ToolHint

    $trackedPid = Get-TrackedPid -PidFile $PidFile
    if ($null -ne $trackedPid -and (Test-OwnedProcess -ProcessId $trackedPid -MetadataFile $MetadataFile)) {
        Write-Host "[running] $Name already tracked at pid $trackedPid."
        return $true
    }

    if ($null -ne $trackedPid) {
        $process = Get-TrackedProcess -ProcessId $trackedPid
        if ($null -eq $process) {
            Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
            Remove-Item -LiteralPath $MetadataFile -Force -ErrorAction SilentlyContinue
        } elseif (-not (Test-OwnedProcess -ProcessId $trackedPid -MetadataFile $MetadataFile)) {
            Write-Host "[blocked] $Name pid $trackedPid was not started by OrchFlow control. Stop it manually if needed."
            return $false
        }
    }

    $existingListeningPid = Get-ListeningPid -Port $Port
    if ($null -ne $existingListeningPid) {
        Write-Host "[blocked] $Name port $Port is already in use by pid $existingListeningPid."
        Write-Host "          OrchFlow control will not track or stop a process it did not start."
        return $false
    }

    Write-Host "Starting $Name ..."
    Remove-Item -LiteralPath $LogFile -Force -ErrorAction SilentlyContinue
    Write-ServiceCommand -Path $CommandFile -WorkingDirectory $WorkingDirectory -Lines $CommandLines
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = "cmd.exe"
    $startInfo.UseShellExecute = $true
    $startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Minimized
    $escapedCommandFile = $CommandFile.Replace('"', '""')
    $startInfo.Arguments = '/d /s /c "{0}"' -f $escapedCommandFile
    [System.Diagnostics.Process]::Start($startInfo) | Out-Null

    $deadline = (Get-Date).AddSeconds(20)
    do {
        Start-Sleep -Milliseconds 500
        $listeningPid = Get-ListeningPid -Port $Port
        if ($null -ne $listeningPid) {
            $serviceProcess = Get-TrackedProcess -ProcessId $listeningPid
            if ($null -ne $serviceProcess) {
                Set-Content -LiteralPath $PidFile -Value $listeningPid -Encoding ascii
                Write-ProcessMetadata -MetadataFile $MetadataFile -Process $serviceProcess -Name $Name -Port $Port
                Write-Host "[started] $Name pid $listeningPid"
                return $true
            }
        }
    } while ((Get-Date) -lt $deadline)

    Write-Host "[error] $Name did not start listening on port $Port."
    Write-Host "        See $LogFile for startup output."
    return $false
}

Read-OrchFlowEnv -Path (Join-Path $RootDir ".env")
Read-ProcessEnvOverrides

if ([string]::IsNullOrWhiteSpace($env:UV_CACHE_DIR)) {
    $env:UV_CACHE_DIR = Join-Path $RootDir ".uv-cache"
}

$runtimeDir = Resolve-OrchFlowPath -Path $config.ORCHFLOW_RUNTIME_DIR
$apiPidFile = Join-Path $runtimeDir "orchflow-api.pid"
$webPidFile = Join-Path $runtimeDir "orchflow-web.pid"
$apiMetadataFile = Join-Path $runtimeDir "orchflow-api.json"
$webMetadataFile = Join-Path $runtimeDir "orchflow-web.json"
$apiCommandFile = Join-Path $runtimeDir "orchflow-api-control.cmd"
$webCommandFile = Join-Path $runtimeDir "orchflow-web-control.cmd"
$apiLogFile = Join-Path $runtimeDir "orchflow-api.log"
$webLogFile = Join-Path $runtimeDir "orchflow-web.log"
$webUrl = $config.ORCHFLOW_WEB_URL
if ([string]::IsNullOrWhiteSpace($webUrl)) {
    $webUrl = "http://$($config.ORCHFLOW_WEB_HOST):$($config.ORCHFLOW_WEB_PORT)"
}

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

$apiCommandLines = @(
    "set `"UV_CACHE_DIR=$env:UV_CACHE_DIR`"",
    "uv run uvicorn orchflow.external.api.app:create_app --factory --host $($config.ORCHFLOW_API_HOST) --port $($config.ORCHFLOW_API_PORT) --reload >> `"$apiLogFile`" 2>&1"
)
$webCommandLines = @(
    "corepack pnpm dev --host $($config.ORCHFLOW_WEB_HOST) --port $($config.ORCHFLOW_WEB_PORT) --strictPort >> `"$webLogFile`" 2>&1"
)

switch ($Action) {
    "run-api" {
        $ErrorActionPreference = "Continue"
        Require-Tool -Name "uv" -Hint "Install uv from https://docs.astral.sh/uv/"
        Set-Location -LiteralPath $RootDir
        & uv run uvicorn orchflow.external.api.app:create_app --factory --host $config.ORCHFLOW_API_HOST --port $config.ORCHFLOW_API_PORT --reload
        exit $LASTEXITCODE
    }
    "run-web" {
        $ErrorActionPreference = "Continue"
        Require-Tool -Name "corepack" -Hint "Install a Node.js version that includes Corepack."
        Set-Location -LiteralPath $WebDir
        & corepack pnpm dev --host $config.ORCHFLOW_WEB_HOST --port $config.ORCHFLOW_WEB_PORT --strictPort
        exit $LASTEXITCODE
    }
    "status" {
        Write-Host ""
        Write-Host "OrchFlow local process status"
        Write-Host "Runtime directory: $runtimeDir"
        $apiOk = Write-ProcessStatus -Name "API" -PidFile $apiPidFile -MetadataFile $apiMetadataFile
        $webOk = Write-ProcessStatus -Name "Web" -PidFile $webPidFile -MetadataFile $webMetadataFile
        if (-not ($apiOk -and $webOk)) {
            exit 1
        }
    }
    "start" {
        if (-not (Test-StartPortsAvailable)) {
            exit 1
        }

        $apiOk = Start-TrackedProcess -Name "API" -PidFile $apiPidFile -MetadataFile $apiMetadataFile -RequiredTool "uv" -ToolHint "Install uv from https://docs.astral.sh/uv/" -CommandFile $apiCommandFile -WorkingDirectory $RootDir -CommandLines $apiCommandLines -Port $config.ORCHFLOW_API_PORT -LogFile $apiLogFile
        if (-not $apiOk) {
            exit 1
        }
        $webOk = Start-TrackedProcess -Name "Web" -PidFile $webPidFile -MetadataFile $webMetadataFile -RequiredTool "corepack" -ToolHint "Install a Node.js version that includes Corepack." -CommandFile $webCommandFile -WorkingDirectory $WebDir -CommandLines $webCommandLines -Port $config.ORCHFLOW_WEB_PORT -LogFile $webLogFile
        if (-not $webOk) {
            Write-Host "Rolling back API start because Web did not start."
            Stop-TrackedProcess -Name "API" -PidFile $apiPidFile -MetadataFile $apiMetadataFile | Out-Null
            exit 1
        }
        Write-Host "Open $webUrl in your browser when the web client is ready."
    }
    "stop" {
        $webOk = Stop-TrackedProcess -Name "Web" -PidFile $webPidFile -MetadataFile $webMetadataFile
        $apiOk = Stop-TrackedProcess -Name "API" -PidFile $apiPidFile -MetadataFile $apiMetadataFile
        if (-not ($webOk -and $apiOk)) {
            exit 1
        }
    }
    "restart" {
        $webOk = Stop-TrackedProcess -Name "Web" -PidFile $webPidFile -MetadataFile $webMetadataFile
        $apiOk = Stop-TrackedProcess -Name "API" -PidFile $apiPidFile -MetadataFile $apiMetadataFile
        if (-not ($webOk -and $apiOk)) {
            exit 1
        }
        if (-not (Test-StartPortsAvailable)) {
            exit 1
        }
        $startApiOk = Start-TrackedProcess -Name "API" -PidFile $apiPidFile -MetadataFile $apiMetadataFile -RequiredTool "uv" -ToolHint "Install uv from https://docs.astral.sh/uv/" -CommandFile $apiCommandFile -WorkingDirectory $RootDir -CommandLines $apiCommandLines -Port $config.ORCHFLOW_API_PORT -LogFile $apiLogFile
        if (-not $startApiOk) {
            exit 1
        }
        $startWebOk = Start-TrackedProcess -Name "Web" -PidFile $webPidFile -MetadataFile $webMetadataFile -RequiredTool "corepack" -ToolHint "Install a Node.js version that includes Corepack." -CommandFile $webCommandFile -WorkingDirectory $WebDir -CommandLines $webCommandLines -Port $config.ORCHFLOW_WEB_PORT -LogFile $webLogFile
        if (-not $startWebOk) {
            exit 1
        }
        Write-Host "Open $webUrl in your browser when the web client is ready."
    }
}
