$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"
$backendPython = Join-Path $backendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $backendDir)) {
    throw "Backend directory not found: $backendDir"
}

if (-not (Test-Path $frontendDir)) {
    throw "Frontend directory not found: $frontendDir"
}

if (-not (Test-Path $backendPython)) {
    throw "Backend virtualenv Python not found: $backendPython"
}

if (-not (Test-Path (Join-Path $frontendDir "package.json"))) {
    throw "frontend/package.json not found."
}

$portsToClear = @(8000, 5173, 3000)

foreach ($port in $portsToClear) {
    $listeners = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($listener in $listeners) {
        Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Milliseconds 700

$backendCommand = "Set-Location '$backendDir'; & '$backendPython' -m uvicorn app.main:app --reload --port 8000"
$frontendCommand = "Set-Location '$frontendDir'; npm run dev -- --port 5173"

Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $backendCommand | Out-Null
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $frontendCommand | Out-Null

Write-Output "Backend starting on http://localhost:8000"
Write-Output "Frontend starting on http://localhost:5173"
Write-Output "Health check: http://localhost:8000/api/health"
