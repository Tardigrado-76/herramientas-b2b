@echo off
chcp 65001 >nul
title Kronos Enterprise Hub — Cero Docker (Node.js Native)
cd /d "%~dp0"

echo ===============================================================================
echo                KRONOS ENTERPRISE WORKFORCE ^& TIME-TRACKING
echo                      Modo Nativo Soberano (Cero-Docker)
echo ===============================================================================
echo.

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no está instalado o no se encuentra en el PATH.
    pause
    exit /b 1
)

echo [1/3] Verificando dependencias de monorepo...
if not exist "node_modules" (
    echo Instalando paquetes npm...
    call npm install
)

echo.
echo Seleccione el modo de operacion:
echo   [1] Iniciar Plataforma Completa (Backend :3001 + Frontend :3000)
echo   [2] Ejecutar Suite de Pruebas TDD (Jest Backend + Node Test Frontend)
echo   [3] Ejecutar Auditoría Code Doctor (ESLint + TypeScript Compile)
echo   [4] Iniciar solo Backend API (:3001)
echo   [5] Iniciar solo Frontend Dashboard (:3000)
echo.
set /p OPT="Opcion (1-5): "

if "%OPT%"=="1" (
    start "Kronos Backend API" cmd /k "chcp 65001 >nul && npm run dev:backend"
    timeout /t 3 >nul
    start "Kronos Frontend Dashboard" cmd /k "chcp 65001 >nul && npm run dev:frontend"
    timeout /t 2 >nul
    start http://localhost:3000
    echo Plataforma iniciada con exito.
    pause
    exit /b 0
)
if "%OPT%"=="2" (
    echo Ejecutando tests backend...
    call npm run test --workspace=apps/backend
    echo Ejecutando tests frontend...
    call npm run test --workspace=apps/frontend
    pause
    exit /b 0
)
if "%OPT%"=="3" (
    call npm run lint
    pause
    exit /b 0
)
if "%OPT%"=="4" npm run dev:backend
if "%OPT%"=="5" npm run dev:frontend
pause
exit /b 0
