@echo off
chcp 65001 >nul
title LALA — Tempe Inditex OCR Form Digitizer (PySide6 Native)
cd /d "%~dp0"

echo ===============================================================================
echo                LALA — OCR FOR ALL PARTICIPANT DIGITIZER
echo               Tempe Inditex (Elche) - Entorno Nativo Windows
echo ===============================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado en el sistema o no se encuentra en el PATH.
    pause
    exit /b 1
)

echo Seleccione el modo de ejecucion:
echo   [1] Iniciar Aplicacion de Escritorio (PySide6 GUI)
echo   [2] Ejecutar Bateria de Pruebas TDD (pytest -p no:cacheprovider)
echo   [3] Ejecutar Auditoria Code Doctor (Ruff + Mypy + Bandit)
echo   [4] Generar Datos Sinteticos y Muestras de Prueba
echo.
set /p OPT="Opcion (1-4): "

if "%OPT%"=="1" start "" python main.py
if "%OPT%"=="2" python -m pytest tests/ -p no:cacheprovider -v
if "%OPT%"=="3" (
    echo --- [1/3] Ruff Linter ---
    ruff check --no-cache .
    echo --- [2/3] Mypy Type Checker ---
    mypy --ignore-missing-imports --cache-dir "%TEMP%\mypy_cache" config.py main.py gui/ services/ tests/
    echo --- [3/3] Bandit Security Audit ---
    bandit -r -s B101,B104 .
)
if "%OPT%"=="4" (
    cd sample_data
    python generate_samples.py
    cd ..
)
pause
exit /b 0
