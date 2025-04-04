@echo off
echo Fixing permissions for run.sh script...

:: Remove readonly attribute if present
attrib -R run.sh

:: Using PowerShell to set proper permissions (executable bit for Linux)
powershell -Command "& {(Get-Item -Path 'run.sh').Attributes = 'Archive'}"

:: Add execution info to help Linux users
echo Adding execution reminder to run.sh file...
echo :: When using in Linux/macOS, you may need to run: chmod +x run.sh > run_chmod_reminder.txt

echo Permission fixes completed. When transferring to Linux/macOS systems,
echo you may still need to run: chmod +x run.sh
echo.

pause 