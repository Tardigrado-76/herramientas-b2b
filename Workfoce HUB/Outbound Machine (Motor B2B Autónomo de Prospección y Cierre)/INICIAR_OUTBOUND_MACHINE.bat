@echo off
title QUANTIGRADE - OUTBOUND MACHINE - Motor B2B Autonomo de Prospeccion
color 0E
echo =====================================================================
echo    QUANTIGRADE - OUTBOUND MACHINE - Motor B2B (PORT 8504)
echo       Cumplimiento Europeo NIS2, RGPD y Cyber Resilience Act
echo =====================================================================
echo.
echo Iniciando servidor ejecutivo Streamlit...
echo Por favor, espere unos instantes mientras se carga el enjambre de prospeccion...
echo.

cd /d "%~dp0"
python -m streamlit run app_streamlit.py --server.port 8504 --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar Streamlit. Verifique su entorno de Python.
    pause
)
