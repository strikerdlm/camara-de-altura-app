@echo off
echo ========================================
echo    CAMARA APPLICATION STARTER
echo ========================================
echo.

REM Ensure we're in the correct directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo Current directory: %CD%
echo Preparing high-resolution application...
echo.

REM Activate virtual environment if available
if exist "registry\Scripts\activate.bat" (
    echo Activating virtual environment...
    call registry\Scripts\activate.bat
    echo.
)

REM Regenerate the high-resolution icon
if exist "assets\windows_icon_fix.py" (
    echo Generating high-resolution icon...
    python assets\windows_icon_fix.py
    echo.
)

REM Start the application with the new icon
echo Starting Camara Application...
echo.
python main.py

REM If application closes abnormally
if errorlevel 1 (
    echo.
    echo Application closed with error.
    echo Check the logs folder for error details.
) else (
    echo.
    echo Application closed normally.
)
echo.
pause 