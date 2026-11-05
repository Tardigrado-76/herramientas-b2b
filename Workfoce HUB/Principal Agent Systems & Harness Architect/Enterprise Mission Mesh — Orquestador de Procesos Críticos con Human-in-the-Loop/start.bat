@echo off
setlocal enabledelayedexpansion
title Enterprise Mission Mesh - Orquestador HITL y Sagas
cd /d "%~dp0"
chcp 65001 >nul

echo =====================================================================
echo  ENTERPRISE MISSION MESH - Orquestador HITL con 1-Click Rollback
echo  Portal Local Web: http://127.0.0.1:8765/portal
echo  Normativas: EU AI Act (Art. 14) ^| Estatuto de los Trabajadores Art. 34.9
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

if not "%~1"=="" (
    python main.py %*
    goto end
)

echo Seleccione el modo de ejecucion:
echo   [1] Iniciar Servidor de la Malla y Portal Local (Puerto 8765)
echo   [2] Ejecutar Simulacion de Incidente Laboral Kronos con Rollback
echo   [3] Abrir CLI Interactivo de la Malla
echo.
set /p opt="Opcion (1-3, defecto 1): "

if "%opt%"=="2" (
    echo.
    echo [INFO] Iniciando Simulacion de Incidente Kronos...
    python scripts\simulate_kronos_incident.py
) else if "%opt%"=="3" (
    echo.
    echo [INFO] Iniciando CLI de la Malla...
    python -m enterprise_mission_mesh.cli.mesh_cli --help
) else (
    echo.
    echo [INFO] Iniciando servidor FastAPI y Portal HITL en http://127.0.0.1:8765/portal ...
    echo [INFO] Presione CTRL+C para detener el servicio.
    echo.
    python main.py
)

:end
echo.
pause
