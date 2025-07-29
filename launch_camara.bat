@echo off
REM Launch script for Camara Application
REM This ensures the app runs from the correct directory

echo ========================================
echo    CAMARA APPLICATION LAUNCHER
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo Current directory: %CD%
echo.

REM Check if virtual environment exists
if exist "registry\Scripts\activate.bat" (
    echo Activating virtual environment...
    call registry\Scripts\activate.bat
    echo Virtual environment activated.
    echo.
) else (
    echo Warning: Virtual environment not found at registry\Scripts\
    echo Using system Python...
    echo.
)

REM Check if main.py exists
if exist "main.py" (
    echo Starting Camara Application...
    echo.
    python main.py
) else (
    echo Error: main.py not found in current directory!
    echo Please ensure you're running this script from the correct folder:
    echo C:\Users\User\OneDrive\FAC\Research\Altitude Chamber\Obervador de Registro\a_camara
    echo.
    pause
    exit /b 1
)

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with error. Press any key to close...
    pause >nul
) 