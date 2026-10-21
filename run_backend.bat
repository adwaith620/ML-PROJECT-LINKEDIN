@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo   TalentLens — Backend Service Launcher
echo =====================================================================

set PYTHON_EXE=
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [INFO] Running: !PYTHON_EXE! -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
cd /d "%~dp0"
!PYTHON_EXE! -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
