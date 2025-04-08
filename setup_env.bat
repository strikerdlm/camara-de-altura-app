@echo off
echo ======================================================
echo  Configurando entorno virtual para Camara Hiperbarica
echo ======================================================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo Por favor instale Python 3.8 o superior desde https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if tkinter is available
python -c "import tkinter" > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Tkinter no esta disponible en su instalacion de Python.
    echo Por favor instale Python con soporte para tkinter (opcion "tcl/tk and IDLE" durante la instalacion).
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creando entorno virtual nuevo...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo Entorno virtual ya existe.
)

:: Activate virtual environment and install dependencies
echo Activando entorno virtual e instalando dependencias...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

:: Upgrade pip and setuptools - This will fix the notification and distutils issue
echo Actualizando pip y setuptools a las ultimas versiones...
python -m pip install --upgrade pip setuptools wheel --no-warn-script-location
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo actualizar pip, intentando continuar con la version actual.
)

:: Install each dependency individually to identify problematic packages
echo Instalando dependencias individualmente...

:: Install ttkbootstrap first as it's critical
echo Instalando ttkbootstrap...
pip install --prefer-binary ttkbootstrap
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar ttkbootstrap.
    echo Este paquete es esencial para la aplicacion.
    pause
    exit /b 1
)

:: Install the remaining dependencies
echo Instalando las demas dependencias...
for %%p in (
    pillow
    matplotlib
) do (
    echo Instalando %%p...
    pip install --prefer-binary %%p
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: No se pudo instalar %%p. La aplicacion podria funcionar incorrectamente.
    )
)

:: Handle numpy specially due to build issues
echo Instalando numpy...
pip install --prefer-binary numpy==1.24.3
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo instalar numpy==1.24.3, intentando version compatible...
    pip install --prefer-binary "numpy<2.0.0"
)

:: Install remaining packages
echo Instalando paquetes adicionales...
for %%p in (
    pandas
    pyarrow
    openpyxl
    python-dotenv
    cairosvg
    svglib
) do (
    echo Instalando %%p...
    pip install --prefer-binary %%p
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: No se pudo instalar %%p. La aplicacion podria funcionar incorrectamente.
    )
)

echo.
echo ======================================================
echo  Entorno configurado correctamente!
echo  Para activar el entorno manualmente:
echo  call venv\Scripts\activate.bat
echo ======================================================
echo.
echo Presione cualquier tecla para iniciar la aplicacion...
pause > nul

:: Verify ttkbootstrap is available before launching
python -c "import ttkbootstrap" > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: No se pudo verificar la instalacion de ttkbootstrap.
    echo La aplicacion puede no iniciar correctamente.
    pause
)

:: Launch the application
python main.py
if %errorlevel% neq 0 (
    echo ERROR: La aplicacion no pudo iniciarse correctamente.
    pause
    exit /b 1
) 