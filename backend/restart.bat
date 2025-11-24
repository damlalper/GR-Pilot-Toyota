@echo off
echo ======================================
echo Stopping old backend processes...
echo ======================================

REM Kill all Python processes running main.py
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a on port 8000
    taskkill /F /PID %%a 2>nul
)

REM Wait for port to be released
timeout /t 3 /nobreak >nul

echo.
echo ======================================
echo Starting new backend...
echo ======================================
echo.

REM Start backend
python main.py

pause
