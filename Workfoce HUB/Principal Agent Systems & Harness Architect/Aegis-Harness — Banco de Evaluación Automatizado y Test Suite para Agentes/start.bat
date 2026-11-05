@echo off
setlocal enabledelayedexpansion
title Aegis-Harness - Banco de Evaluacion Automatizado (Cero Docker)
cd /d "%~dp0"
chcp 65001 >nul

echo =====================================================================
echo  AEGIS-HARNESS - Banco de Evaluacion y Quality Gate para Agentes IA
echo  Dashboard Web: http://127.0.0.1:8085/
echo  Normativas: EU AI Act (Art. 15) ^| NIS2 (Art. 21) ^| Cero Docker 100%%
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
echo   [1] Iniciar Dashboard Web de Evaluacion en Vivo (http://127.0.0.1:8085/)
echo   [2] Ejecutar Bateria Completa de 120 Casos y Quality Gate (Consola)
echo   [3] Ejecutar Suite Completa de Tests Automatizados (Pytest)
echo.
set /p opt="Opcion (1-3, defecto 1): "

if "%opt%"=="2" (
    echo.
    echo [INFO] Iniciando bateria de evaluacion CLI...
    python main.py
) else if "%opt%"=="3" (
    echo.
    echo [INFO] Ejecutando suite de pytest...
    python -m pytest tests -v
) else (
    echo.
    echo [INFO] Iniciando Dashboard Web en http://127.0.0.1:8085/ ...
    echo [INFO] Presione CTRL+C para detener el servidor.
    echo.
    python -m aegis.dashboard
)

:end
echo.
pause
