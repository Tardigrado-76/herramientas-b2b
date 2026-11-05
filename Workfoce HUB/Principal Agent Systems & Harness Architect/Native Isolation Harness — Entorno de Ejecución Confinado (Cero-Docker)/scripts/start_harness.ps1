# Start Native Isolation Harness CLI & Monitor
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🛡️ NATIVE ISOLATION HARNESS (100% CERO DOCKER)" -ForegroundColor Green
Write-Host "Normativas: EU AI Act Art. 15 | NIS2 Art. 21 | DORA Art. 9" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location -Path $projectRoot
$env:PYTHONPATH = Join-Path $projectRoot "src"

python src/native_isolation_harness/cli/harness_cli.py
