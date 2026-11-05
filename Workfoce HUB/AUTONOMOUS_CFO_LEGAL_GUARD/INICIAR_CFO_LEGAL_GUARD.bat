@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

title AUTONOMOUS VERTICAL CFO & LEGAL GUARD - Micro-SaaS
color 0A
echo =====================================================================
echo    AUTONOMOUS VERTICAL CFO & LEGAL GUARD (PORT 8510)
echo       CFO Autonomo, Antifraude de Facturas y Compliance Fiscal
echo       Ley Crea y Crece, VeriFactu (RD 1007/2023), NIS2 y RGPD
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit en el puerto 8510...
echo Por favor, espere unos instantes mientras se carga el sistema...
echo.

cd /d "%~dp0"

REM Intento con Python del sistema o entorno activo
python -m streamlit run app_streamlit.py --server.port 8510 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit con el comando 'python'.
    echo Intentando con el lanzador py...
    py -m streamlit run app_streamlit.py --server.port 8510 --server.headless false
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR CRITICO] No se encontro Python o faltan dependencias instaladas.
    echo Ejecute: pip install -r requirements.txt
    pause
)
