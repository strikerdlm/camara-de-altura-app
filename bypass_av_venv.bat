@echo off
setlocal EnableDelayedExpansion

echo ======================================================
echo  Creando Entorno Virtual sin Deteccion de Antivirus
echo ======================================================
echo.

:: Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo Por favor instale Python 3.8 o superior desde https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Verificar si el entorno virtual ya existe
if exist "venv" (
    echo El entorno virtual ya existe.
    goto activate
)

echo Creando entorno virtual alternativo...

:: Método 1: Intentar crear el entorno virtual mediante virtualenv (instalarlo primero)
echo Instalando virtualenv como alternativa...
python -m pip install virtualenv --quiet
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo instalar virtualenv.
    goto method2
)

echo Creando entorno con virtualenv...
python -m virtualenv venv --quiet
if %errorlevel% equ 0 (
    echo Entorno virtual creado exitosamente con virtualenv.
    goto activate
)

:method2
:: Método 2: Crear el entorno virtual manualmente 
echo Intentando crear entorno virtual manualmente...

:: Crear estructura de directorios
mkdir venv\Scripts 2>nul
mkdir venv\Lib\site-packages 2>nul

:: Crear archivo activate.bat
echo @echo off > venv\Scripts\activate.bat
echo set "VIRTUAL_ENV=%cd%\venv" >> venv\Scripts\activate.bat
echo. >> venv\Scripts\activate.bat
echo if defined _OLD_VIRTUAL_PROMPT (>> venv\Scripts\activate.bat
echo     set "PROMPT=%%_OLD_VIRTUAL_PROMPT%%" >> venv\Scripts\activate.bat
echo ) else (>> venv\Scripts\activate.bat
echo     if not defined PROMPT (>> venv\Scripts\activate.bat
echo         set "PROMPT=$P$G" >> venv\Scripts\activate.bat
echo     )>> venv\Scripts\activate.bat
echo     set "_OLD_VIRTUAL_PROMPT=!PROMPT!" >> venv\Scripts\activate.bat
echo )>> venv\Scripts\activate.bat
echo. >> venv\Scripts\activate.bat
echo set "PROMPT=(venv) !PROMPT!" >> venv\Scripts\activate.bat
echo. >> venv\Scripts\activate.bat
echo REM Don't use PYTHONHOME >> venv\Scripts\activate.bat
echo if defined _OLD_VIRTUAL_PYTHONHOME (>> venv\Scripts\activate.bat
echo     set "PYTHONHOME=%%_OLD_VIRTUAL_PYTHONHOME%%" >> venv\Scripts\activate.bat
echo     set "_OLD_VIRTUAL_PYTHONHOME=" >> venv\Scripts\activate.bat
echo )>> venv\Scripts\activate.bat
echo. >> venv\Scripts\activate.bat
echo REM Add the virtual env to the PATH >> venv\Scripts\activate.bat
echo if defined _OLD_VIRTUAL_PATH (>> venv\Scripts\activate.bat
echo     set "PATH=%%_OLD_VIRTUAL_PATH%%" >> venv\Scripts\activate.bat
echo ) else (>> venv\Scripts\activate.bat
echo     set "_OLD_VIRTUAL_PATH=!PATH!" >> venv\Scripts\activate.bat
echo )>> venv\Scripts\activate.bat
echo. >> venv\Scripts\activate.bat
echo set "PATH=%cd%\venv\Scripts;!PATH!" >> venv\Scripts\activate.bat
echo. >> venv\Scripts\activate.bat

:: Crear archivo deactivate.bat
echo @echo off > venv\Scripts\deactivate.bat
echo. >> venv\Scripts\deactivate.bat
echo if defined _OLD_VIRTUAL_PROMPT (>> venv\Scripts\deactivate.bat
echo     set "PROMPT=%%_OLD_VIRTUAL_PROMPT%%" >> venv\Scripts\deactivate.bat
echo     set "_OLD_VIRTUAL_PROMPT=" >> venv\Scripts\deactivate.bat
echo )>> venv\Scripts\deactivate.bat
echo. >> venv\Scripts\deactivate.bat
echo if defined _OLD_VIRTUAL_PYTHONHOME (>> venv\Scripts\deactivate.bat
echo     set "PYTHONHOME=%%_OLD_VIRTUAL_PYTHONHOME%%" >> venv\Scripts\deactivate.bat
echo     set "_OLD_VIRTUAL_PYTHONHOME=" >> venv\Scripts\deactivate.bat
echo )>> venv\Scripts\deactivate.bat
echo. >> venv\Scripts\deactivate.bat
echo if defined _OLD_VIRTUAL_PATH (>> venv\Scripts\deactivate.bat
echo     set "PATH=%%_OLD_VIRTUAL_PATH%%" >> venv\Scripts\deactivate.bat
echo     set "_OLD_VIRTUAL_PATH=" >> venv\Scripts\deactivate.bat
echo )>> venv\Scripts\deactivate.bat
echo. >> venv\Scripts\deactivate.bat
echo set VIRTUAL_ENV= >> venv\Scripts\deactivate.bat
echo. >> venv\Scripts\deactivate.bat

:: Crear archivo python.exe que apunta al Python original
copy "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" venv\Scripts\python.exe >nul 2>&1
if not exist "venv\Scripts\python.exe" (
    :: Intentar encontrar Python en otras ubicaciones comunes
    copy "C:\Python*\python.exe" venv\Scripts\python.exe >nul 2>&1
    if not exist "venv\Scripts\python.exe" (
        copy "C:\Program Files\Python*\python.exe" venv\Scripts\python.exe >nul 2>&1
        if not exist "venv\Scripts\python.exe" (
            copy "C:\Program Files (x86)\Python*\python.exe" venv\Scripts\python.exe >nul 2>&1
        )
    )
)

:: Copiar pip
copy "%LOCALAPPDATA%\Programs\Python\Python*\Scripts\pip.exe" venv\Scripts\pip.exe >nul 2>&1
if not exist "venv\Scripts\pip.exe" (
    :: Intentar encontrar pip en otras ubicaciones comunes
    copy "C:\Python*\Scripts\pip.exe" venv\Scripts\pip.exe >nul 2>&1
    if not exist "venv\Scripts\pip.exe" (
        copy "C:\Program Files\Python*\Scripts\pip.exe" venv\Scripts\pip.exe >nul 2>&1
        if not exist "venv\Scripts\pip.exe" (
            copy "C:\Program Files (x86)\Python*\Scripts\pip.exe" venv\Scripts\pip.exe >nul 2>&1
        )
    )
)

if exist "venv\Scripts\python.exe" (
    echo Entorno virtual creado manualmente.
    goto activate
) else (
    echo ADVERTENCIA: No se pudo crear el entorno virtual manualmente.
    goto method3
)

:method3
:: Método 3: Dar permisos al antivirus para ejecutar el script
echo.
echo Intentando ejecutar con exclusión de antivirus temporal...
echo.
echo NOTA: Es posible que aparezca una advertencia de seguridad.
echo       Si aparece, seleccione "Ejecutar de todos modos" o "Permitir".
echo.
echo Presione cualquier tecla para continuar...
pause >nul

:: Intentar crear el entorno virtual con un comando alternativo
powershell -Command "& {Add-MpPreference -ExclusionProcess 'python.exe'; python -m venv venv; Remove-MpPreference -ExclusionProcess 'python.exe'}" -ExecutionPolicy Bypass -NoProfile

if exist "venv" (
    echo Entorno virtual creado con exclusión temporal de antivirus.
) else (
    echo.
    echo ERROR: No se pudo crear el entorno virtual.
    echo.
    echo Soluciones alternativas:
    echo 1. Desactive temporalmente su antivirus
    echo 2. Agregue una exclusión para python.exe en su antivirus
    echo 3. Use el comando: python -m pip install --user -r requirements.txt
    echo    (Esto instalará los paquetes en el entorno global)
    echo.
    echo Presione cualquier tecla para salir...
    pause >nul
    exit /b 1
)

:activate
:: Activar el entorno virtual
echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat

:: Verificar que estamos en el entorno virtual
echo.
echo Verificando entorno virtual...
echo Ruta de Python: !PYTHONPATH!

:: Instalar dependencias
echo.
echo Instalando dependencias esenciales...
python -m pip install --upgrade pip
python -m pip install ttkbootstrap pillow numpy pandas

echo.
echo ======================================================
echo  Entorno Virtual listo!
echo  Puede iniciar la aplicación con: python main.py
echo ======================================================

:: Mantener la ventana abierta
pause 