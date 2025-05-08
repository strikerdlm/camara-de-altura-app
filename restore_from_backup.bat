@echo off
echo ======================================================
echo     HERRAMIENTA DE RESTAURACIÓN DE LA APLICACIÓN
echo ======================================================
echo.
echo Este script le ayudará a restaurar la aplicación desde un respaldo.
echo.
echo IMPORTANTE: Antes de continuar, asegúrese de:
echo 1. Haber extraído el archivo a_camara.rar a una carpeta
echo 2. Saber la ruta de esa carpeta
echo.
echo ------------------------------------------------------
echo.

set /p RUTA_BACKUP=Por favor, ingrese la ruta de la carpeta donde extrajo el respaldo (temp_restore): 

if not exist "%RUTA_BACKUP%\main.py" (
    echo.
    echo ERROR: No se encontró el archivo main.py en la ruta especificada.
    echo Asegúrese de haber extraído correctamente el archivo a_camara.rar.
    echo.
    pause
    exit /b
)

echo.
echo Creando copia de seguridad de los archivos actuales...
mkdir backup_before_restore 2>nul
copy tab2_alumnos.py backup_before_restore\ 2>nul
copy tab4_rd.py backup_before_restore\ 2>nul
copy tab5_reactores.py backup_before_restore\ 2>nul
copy tab6_sintomas.py backup_before_restore\ 2>nul
copy tab7_exportar.py backup_before_restore\ 2>nul
echo Copia de seguridad creada en la carpeta "backup_before_restore"
echo.

echo Restaurando archivos desde el respaldo...
copy "%RUTA_BACKUP%\tab2_alumnos.py" . /y
copy "%RUTA_BACKUP%\tab4_rd.py" . /y
copy "%RUTA_BACKUP%\tab5_reactores.py" . /y
copy "%RUTA_BACKUP%\tab6_sintomas.py" . /y
copy "%RUTA_BACKUP%\tab7_exportar.py" . /y

echo.
echo Restauración completada.
echo.
echo Ahora debería verificar que la aplicación funcione correctamente.
echo Ejecute "python main.py" para iniciar la aplicación.
echo.
echo Si encuentra problemas, asegúrese de que todos los archivos tengan la importación correcta:
echo "from ttkbootstrap.scrolled import ScrolledFrame"
echo.
echo Si necesita restaurar los archivos anteriores, los encontrará en la carpeta "backup_before_restore".
echo.
pause 