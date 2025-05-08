@echo off
echo Preparing high-resolution application...

REM Regenerate the high-resolution icon
python assets\windows_icon_fix.py

REM Start the application with the new icon
echo Starting application with high-resolution icon...
python main.py

REM If application closes abnormally
echo Application closed.
pause 