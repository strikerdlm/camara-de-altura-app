@echo off
echo ======================================================
echo  Iniciando Camara Hiperbarica
echo ======================================================
echo.

:: Try to run with Python directly
python entry.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo iniciar la aplicacion.
    echo Intentando con la ruta completa a Python...
    
    :: Try with Python from standard installation paths
    if exist "C:\Python312\python.exe" (
        "C:\Python312\python.exe" entry.py
    ) else if exist "C:\Python311\python.exe" (
        "C:\Python311\python.exe" entry.py
    ) else if exist "C:\Python310\python.exe" (
        "C:\Python310\python.exe" entry.py
    ) else if exist "C:\Python39\python.exe" (
        "C:\Python39\python.exe" entry.py
    ) else if exist "C:\Python38\python.exe" (
        "C:\Python38\python.exe" entry.py
    ) else (
        echo.
        echo ERROR: No se pudo encontrar Python.
        echo Por favor instale Python 3.8 o superior desde:
        echo https://www.python.org/downloads/
    )
)

echo.
echo Presione cualquier tecla para salir...
pause > nul 