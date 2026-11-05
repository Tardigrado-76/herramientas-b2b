@echo off
title QUANTIGRADE - WORKFORCE AI HUB - Empleados de IA Autonomos
color 0A
echo =====================================================================
echo    QUANTIGRADE - WORKFORCE AI HUB - Empleados de IA (PORT 8502)
echo       Cumplimiento Europeo NIS2, RGPD y Cyber Resilience Act
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit...
echo Por favor, espere unos instantes mientras se carga el ecosistema...
echo.

cd /d "%~dp0"
python -m streamlit run app_streamlit.py --server.port 8502 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit. Verifique su entorno de Python.
    pause
)
