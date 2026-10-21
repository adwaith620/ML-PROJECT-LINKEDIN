@echo off
echo =====================================================================
echo   TalentLens — Frontend UI Launcher
echo =====================================================================

cd /d "%~dp0frontend"
echo [INFO] Running: npm run dev
npm run dev
pause
