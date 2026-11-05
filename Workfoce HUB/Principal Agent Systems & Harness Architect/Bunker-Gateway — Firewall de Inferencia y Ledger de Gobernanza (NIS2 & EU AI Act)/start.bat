@echo off
setlocal enabledelayedexpansion
title Bunker-Gateway - Firewall de Inferencia y Ledger de Gobernanza
cd /d "%~dp0"
chcp 65001 >nul

echo =====================================================================
echo  Panel de Control y Dashboard Web: http://127.0.0.1:8080/
echo  Reverse Proxy OpenAI / Anthropic: http://127.0.0.1:8080/v1
echo  Normativas: EU AI Act (Arts. 12, 14, 15) ^| NIS2 (Art. 21) ^| DORA
echo =====================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el PATH del sistema.
    echo Por favor instale Python 3.11+ y agreguelo al PATH.
    echo.
    pause
    exit /b 1
)

set "PYTHONPATH=%~dp0src"

echo [INFO] Iniciando servidor de proxy y firewall agéntico en el puerto 8080...
echo [INFO] Presione CTRL+C para detener el servicio.
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El servidor se detuvo con codigo de error %errorlevel%.
)

echo.
pause
