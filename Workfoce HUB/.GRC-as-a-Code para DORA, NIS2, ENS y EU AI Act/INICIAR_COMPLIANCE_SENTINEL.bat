@echo off
title COMPLIANCE SENTINEL - GRC-as-a-Code
color 09
echo =====================================================================
echo         COMPLIANCE SENTINEL - GRC-as-a-Code para DORA, NIS2, ENS
echo       Cumplimiento Europeo NIS2, RGPD y Cyber Resilience Act
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit...
echo Por favor, espere unos instantes mientras se carga el Consejo Regulador...
echo.

cd /d "%~dp0"
python -m streamlit run app_streamlit.py --server.port 8505 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit. Verifique su entorno de Python.
    pause
)
