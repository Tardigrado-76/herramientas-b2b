@echo off
setlocal enabledelayedexpansion
title Native Isolation Harness - Entorno de Ejecucion Confinado
cd /d "%~dp0"
chcp 65001 >nul

echo =====================================================================
echo  NATIVE ISOLATION HARNESS - Micro-Sandbox Nativo (Cero Docker)
echo  Dashboard Web: http://127.0.0.1:8088/
echo  Kernel Win32 Job Objects ^| Anti Path-Traversal ^| Borrado NIST 800-88
echo  Normativas: EU AI Act (Art. 15) ^| NIS2 (Art. 21) ^| DORA (Art. 9)
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
set "CURRENT_DIR=%~dp0"

if not "%~1"=="" (
    python main.py %*
    goto end
)

echo Seleccione una opcion:
echo   [1] Iniciar Dashboard Web y Monitor SOC en Vivo (http://127.0.0.1:8088/)
echo   [2] Abrir Monitor de Seguridad SOC en Consola (Rich TUI)
echo   [3] Iniciar Terminal CLI del Harness (Self-Test)
echo   [4] Ejecutar Suite de Aislamiento y Pruebas de Red-Team
echo.
set /p opt="Opcion (1-4, defecto 1): "

if "%opt%"=="2" (
    echo.
    echo [INFO] Abriendo Monitor SOC en Consola...
    python src/native_isolation_harness/cli/soc_monitor.py
) else if "%opt%"=="3" (
    echo.
    echo [INFO] Ejecutando Harness CLI...
    python main.py
) else if "%opt%"=="4" (
    echo.
    echo [INFO] Ejecutando bateria de estres y aislamiento...
    powershell -ExecutionPolicy Bypass -File scripts\test_harness_isolation.ps1
) else (
    echo.
    echo [INFO] Iniciando Dashboard Web en http://127.0.0.1:8088/ ...
    echo [INFO] Presione CTRL+C para detener el servicio.
    echo.
    python -m native_isolation_harness.dashboard.server
)

:end
echo.
pause
