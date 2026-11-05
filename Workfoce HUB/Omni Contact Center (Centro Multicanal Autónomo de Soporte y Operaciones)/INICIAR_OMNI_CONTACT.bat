@echo off
title QUANTIGRADE - OMNI CONTACT - Contact Center IA Multimodal
color 03
echo =====================================================================
echo    QUANTIGRADE - OMNI CONTACT - Contact Center IA (PORT 8508)
echo       Cumplimiento Europeo NIS2, RGPD y Cyber Resilience Act
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit...
echo Por favor, espere unos instantes mientras se cargan los adaptadores multicanal...
echo.

cd /d "%~dp0"
python -m streamlit run app_streamlit.py --server.port 8508 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit. Verifique su entorno de Python.
    pause
)
