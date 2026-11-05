# Start Enterprise Mission Mesh Native Host Server
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🛡️ INICIANDO ENTERPRISE MISSION MESH (100% CERO DOCKER)" -ForegroundColor Green
Write-Host "Host: 127.0.0.1 | Puerto: 8765 | Portal Local Activo" -ForegroundColor Yellow
Write-Host "Normativas: EU AI Act Art. 14 | Estatuto Trabajadores Art. 34.9" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location -Path $projectRoot
$env:PYTHONPATH = Join-Path $projectRoot "src"

python -m uvicorn enterprise_mission_mesh.server:app --host 127.0.0.1 --port 8765
