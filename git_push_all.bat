@echo off
echo Initializing git repository and pushing all files...

REM Initialize git if not already initialized
if not exist .git (
    git init
    echo Git repository initialized
)

REM Add remote if not already added
git remote -v | findstr "origin" > nul
if errorlevel 1 (
    git remote add origin https://github.com/strikerdlm/camara-de-altura-app.git
    echo Added remote origin
)

REM Add all files (will respect .gitignore)
git add .
echo Added all files

REM Commit changes
git commit -m "Upload complete project structure"
echo Committed changes

REM Push to master branch
git push -u origin master --force
echo Pushed to repository

echo Done!
pause 