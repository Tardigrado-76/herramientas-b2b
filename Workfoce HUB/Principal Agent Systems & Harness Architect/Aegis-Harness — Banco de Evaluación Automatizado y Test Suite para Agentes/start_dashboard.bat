@echo off
setlocal enabledelayedexpansion
title Aegis-Harness Web Dashboard (Puerto 8085)
cd /d "%~dp0"
chcp 65001 >nul

echo =====================================================================
echo  AEGIS-HARNESS - Dashboard Web de Evaluacion y Quality Gate
echo  URL: http://127.0.0.1:8085/
echo  Normativas: EU AI Act (Art. 15) ^| NIS2 (Art. 21) ^| Cero Docker 100%%
echo =====================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el PATH del sistema.
    pause
    exit /b 1
)

set "PYTHONPATH=%~dp0src"
set "CURRENT_DIR=%~dp0"

echo [INFO] Iniciando servidor del Dashboard en http://127.0.0.1:8085/ ...
echo [INFO] Presione CTRL+C para detener el servicio.
echo.
python -m aegis.dashboard
pause
