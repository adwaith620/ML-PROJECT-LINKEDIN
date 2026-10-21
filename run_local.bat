@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo   TalentLens — Resume Screening & Skill Gap Analysis System
echo   Starting Local Development Environment (FastAPI + Vite React)
echo =====================================================================
echo.

:: Detect Python with required packages
set PYTHON_EXE=
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else (
    where py >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py -3.11"
    ) else (
        where python >nul 2>&1
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=python"
        ) else (
            echo [ERROR] Python is not installed or not found on PATH.
            pause
            exit /b 1
        )
    )
)

echo [INFO] Using Python: !PYTHON_EXE!
!PYTHON_EXE! --version

:: Check Node.js and npm
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not found on PATH. Please install Node.js v18+.
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not found on PATH.
    pause
    exit /b 1
)

echo [INFO] Using Node:
node --version
npm --version
echo.

:: Start Backend API in background window
echo [INFO] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "TalentLens Backend API" cmd /k "title TalentLens Backend && cd /d "%~dp0" && !PYTHON_EXE! -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

:: Give backend 2 seconds to initialize
timeout /t 2 /nobreak >nul

:: Start Frontend Vite in background window
echo [INFO] Starting Vite Frontend on http://127.0.0.1:5173 ...
start "TalentLens Frontend UI" cmd /k "title TalentLens Frontend && cd /d "%~dp0frontend" && npm run dev"

echo.
echo =====================================================================
echo   TalentLens services are launching:
echo   - Frontend UI:  http://127.0.0.1:5173
echo   - Backend API:  http://127.0.0.1:8000
echo   - API Docs:     http://127.0.0.1:8000/docs
echo   - Health Check: http://127.0.0.1:8000/api/health
echo.
echo   Press any key to open the application in your default browser...
echo =====================================================================
pause >nul
start http://127.0.0.1:5173
