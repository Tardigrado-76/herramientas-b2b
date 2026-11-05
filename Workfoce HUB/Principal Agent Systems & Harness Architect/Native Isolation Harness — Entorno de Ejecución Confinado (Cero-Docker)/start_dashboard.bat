@echo off
setlocal enabledelayedexpansion
title Native Isolation Harness - Dashboard Web SOC (Puerto 8088)
cd /d "%~dp0"
chcp 65001 >nul

echo =====================================================================
echo  NATIVE ISOLATION HARNESS - Dashboard Web y Monitor SOC
echo  URL: http://127.0.0.1:8088/
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

echo [INFO] Iniciando servidor del Dashboard en http://127.0.0.1:8088/ ...
echo [INFO] Presione CTRL+C para detener el servicio.
echo.
python -m native_isolation_harness.dashboard.server
pause
