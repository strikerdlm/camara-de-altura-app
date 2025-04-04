@echo off
echo Iniciando Registro Entrenamiento en Camara de Altura...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo Por favor instale Python 3.8 o superior desde https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check which virtual environment exists and use it
if exist "venv" (
    set "VENV_DIR=venv"
) else if exist "registry" (
    set "VENV_DIR=registry"
) else (
    echo Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    set "VENV_DIR=venv"
)

:: Activate the virtual environment
echo Activando entorno virtual: %VENV_DIR%
call %VENV_DIR%\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

:: Create required directories
if not exist assets mkdir assets
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backup mkdir backup

:: Update pip using python -m pip to avoid PATH issues
echo Actualizando pip...
python -m pip install --upgrade pip setuptools wheel --no-warn-script-location
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo actualizar pip. Continuando de todas formas...
)

:: Fix distutils issue for Python 3.12+
echo Instalando dependencias de construccion...
python -m pip install setuptools --upgrade
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo instalar setuptools. Algunas instalaciones pueden fallar...
)

:: Install dependencies one by one with error handling
echo Instalando dependencias principales...

:: Install ttkbootstrap
echo Verificando ttkbootstrap...
python -c "import ttkbootstrap" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando ttkbootstrap...
    python -m pip install --prefer-binary ttkbootstrap
    
    :: Verify again after installation
    python -c "import ttkbootstrap" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: ttkbootstrap no se instaló correctamente, intentando otra vez...
        python -m pip install ttkbootstrap
        
        :: Final verification
        python -c "import ttkbootstrap" >nul 2>&1
        if %errorlevel% neq 0 (
            echo ERROR: No se pudo instalar ttkbootstrap, que es esencial para la aplicación.
            pause
            exit /b 1
        ) else (
            echo ttkbootstrap instalado correctamente en el segundo intento.
        )
    ) else (
        echo ttkbootstrap instalado correctamente.
    )
) else (
    echo ttkbootstrap ya esta instalado.
)

:: Install Pillow
echo Verificando Pillow...
python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Pillow...
    python -m pip install --prefer-binary pillow
    
    :: Verify installation
    python -c "import PIL" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: No se pudo instalar Pillow. Algunas funcionalidades pueden no estar disponibles.
    ) else (
        echo Pillow instalado correctamente.
    )
) else (
    echo Pillow ya esta instalado.
)

:: Install matplotlib
echo Verificando matplotlib...
python -c "import matplotlib" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando matplotlib...
    python -m pip install --prefer-binary matplotlib
    
    :: Verify installation
    python -c "import matplotlib" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: No se pudo instalar matplotlib. Algunas funcionalidades pueden no estar disponibles.
    ) else (
        echo matplotlib instalado correctamente.
    )
) else (
    echo matplotlib ya esta instalado.
)

:: Special handling for numpy due to build issues
echo Verificando numpy...
python -c "import numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando numpy...
    python -m pip install --prefer-binary numpy==1.24.3
    
    :: Verify installation
    python -c "import numpy" >nul 2>&1
    if %errorlevel% equ 0 (
        echo numpy instalado correctamente.
    ) else (
        echo ADVERTENCIA: No se pudo instalar numpy==1.24.3, intentando versión compatible...
        python -m pip install --prefer-binary "numpy<2.0.0"
        
        :: Verify installation
        python -c "import numpy" >nul 2>&1
        if %errorlevel% equ 0 (
            echo numpy instalado correctamente.
        ) else (
            python -m pip install --prefer-binary numpy
            
            :: Verify installation
            python -c "import numpy" >nul 2>&1
            if %errorlevel% neq 0 (
                echo ADVERTENCIA: No se pudo instalar numpy. Algunas funcionalidades pueden no estar disponibles.
            ) else (
                echo numpy instalado correctamente.
            )
        )
    )
) else (
    echo numpy ya esta instalado.
)

:: Install additional useful packages if possible
echo Verificando pandas...
python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando pandas...
    python -m pip install --prefer-binary pandas
    
    :: Verify installation
    python -c "import pandas" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: No se pudo instalar pandas. Algunas funcionalidades pueden no estar disponibles.
    ) else (
        echo pandas instalado correctamente.
    )
) else (
    echo pandas ya esta instalado.
)

echo Verificando openpyxl...
python -c "import openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando openpyxl...
    python -m pip install --prefer-binary openpyxl
    
    :: Verify installation
    python -c "import openpyxl" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: No se pudo instalar openpyxl. Algunas funcionalidades pueden no estar disponibles.
    ) else (
        echo openpyxl instalado correctamente.
    )
) else (
    echo openpyxl ya esta instalado.
)

:: Verify ttkbootstrap before launching
python -c "import ttkbootstrap" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: ttkbootstrap no esta disponible. La aplicación no puede iniciarse.
    pause
    exit /b 1
)

:: Start the application
echo Iniciando aplicacion...
python main.py
if %errorlevel% neq 0 (
    echo ERROR: La aplicación terminó con código de error %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo Presione cualquier tecla para salir...
pause >nul
exit /b 0 