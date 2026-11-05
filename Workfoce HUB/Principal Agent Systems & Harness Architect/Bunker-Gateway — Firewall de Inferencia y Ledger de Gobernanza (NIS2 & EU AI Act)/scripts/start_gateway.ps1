# Script de Arranque de Bunker-Gateway (100% Cero Docker)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🛡️ INICIANDO BUNKER-GATEWAY (FIREWALL DE INFERENCIA & LEDGER)" -ForegroundColor Green
Write-Host "Reverse Proxy: http://127.0.0.1:8080/v1" -ForegroundColor Yellow
Write-Host "Normativas: EU AI Act (Arts. 12, 14, 15) & NIS2 (Art. 21)" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location -Path $projectRoot
$env:PYTHONPATH = Join-Path $projectRoot "src"

python -m uvicorn bunker_gateway.main:app --host 127.0.0.1 --port 8080

