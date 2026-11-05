# Aegis-Harness Quality Gate Automation Script (Windows Native / Cero Docker)
# Exit code 0 if all tests pass and quality gate passes. Exit code 1 if quality gate fails.

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "AEGIS-HARNESS: Quality Gate Execution and Audit Certification" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location -Path $ProjectRoot
$env:PYTHONPATH = Join-Path $ProjectRoot "src"

# 1. Run Pytest Suite
Write-Host "[1/3] Running Internal Unit and Integration Tests..." -ForegroundColor Yellow
python -m pytest tests -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Internal test suite failed!" -ForegroundColor Red
    exit 1
}
Write-Host "All internal tests passed." -ForegroundColor Green
Write-Host ""

# 2. Run Aegis CLI Evaluation over 120 Test Cases
Write-Host "[2/3] Running Aegis-Harness 120-Test Battery..." -ForegroundColor Yellow
python -m aegis.runner
if ($LASTEXITCODE -ne 0) {
    Write-Host "Quality Gate rejected agent deployment!" -ForegroundColor Red
    exit 1
}
Write-Host "Quality Gate passed." -ForegroundColor Green
Write-Host ""

# 3. Verify Audit Ledger Integrity
Write-Host "[3/3] Verifying NIS2 / EU AI Act Audit Ledger Cryptographic Chain..." -ForegroundColor Yellow
python -c "import sys; from aegis.ledger import AuditLedger; l = AuditLedger(); v, count, err = l.verify_integrity(); print(f'Ledger blocks verified: {count}'); sys.exit(0 if v else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Audit ledger verification failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "AEGIS-HARNESS QUALITY GATE PASSED - AGENT CERTIFIED FOR PRODUCTION" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
exit 0
