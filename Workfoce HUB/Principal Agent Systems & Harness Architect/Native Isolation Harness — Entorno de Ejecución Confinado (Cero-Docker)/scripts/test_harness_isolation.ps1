# Native Isolation Harness - Adversarial & Isolation Test Runner
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🛡️ NATIVE-ISOLATION-HARNESS: Stress & Adversarial Test Run" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Run full test suite with pytest
Write-Host "`n[1/3] Ejecutando suite completa de Pytest (Unit, Integration, Adversarial)..." -ForegroundColor Yellow
python -m pytest tests -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Las pruebas de pytest fallaron." -ForegroundColor Red
    exit 1
}

# 2. Run CLI execution self-test
Write-Host "`n[2/3] Ejecutando self-test mediante CLI del Harness..." -ForegroundColor Yellow
python src/native_isolation_harness/cli/harness_cli.py --script "print('CLI_HARNESS_TEST_OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Fallo en la ejecucion del CLI del Harness." -ForegroundColor Red
    exit 1
}

# 3. Verify SOC telemetry logs and secret redaction
Write-Host "`n[3/3] Verificando integridad de telemetría forense SOC (MITRE/CAPEC)..." -ForegroundColor Yellow
python scripts/verify_soc_alerts.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Fallo en la verificacion de alertas SOC." -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Todas las pruebas de confinamiento y aislamiento pasaron con exito (Cero Docker)." -ForegroundColor Green
