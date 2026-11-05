@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title AUTONOMA SWE-FLEET - Gas Town Control Plane
color 0B
echo =====================================================================
echo    AUTONOMA SWE-FLEET — Enjambre de Ingenieria de Software (PORT 8512)
echo       Gas Town + White Coding + Skills-Manager
echo       Git Worktrees Aislados + Beads Ledger + The Witness Watchdog
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit en el puerto 8512...
echo Por favor, espere unos instantes mientras se inicializa la flota...
echo.

cd /d "%~dp0"

REM Intento con Python del sistema o entorno activo
python -m streamlit run app_streamlit.py --server.port 8512 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit con el comando 'python'.
    echo Intentando con el lanzador py...
    py -m streamlit run app_streamlit.py --server.port 8512 --server.headless false
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR CRITICO] No se encontro Python o faltan dependencias instaladas.
    echo Ejecute: pip install -r requirements.txt
    pause
)
