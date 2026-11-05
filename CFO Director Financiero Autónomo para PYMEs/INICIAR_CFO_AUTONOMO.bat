@echo off
title QUANTIGRADE - AUTONOMO CFO - Director Financiero para PYMEs
color 0B
echo =====================================================================
echo    QUANTIGRADE - AUTONOMO CFO - Director Financiero (PORT 8501)
echo       Cumplimiento Europeo NIS2, RGPD y Cyber Resilience Act
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit...
echo Por favor, espere unos instantes mientras se cargan los agentes...
echo.

cd /d "%~dp0"
python -m streamlit run app_streamlit.py --server.port 8501 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit. Verifique su entorno de Python.
    pause
)
