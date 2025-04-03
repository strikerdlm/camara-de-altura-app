@echo off
echo Iniciando Registro Entrenamiento en Camara de Altura...

if not exist registry (
    echo Creando entorno virtual...
    python -m venv registry
)

call registry\Scripts\activate

if not exist assets mkdir assets
if not exist data mkdir data
if not exist logs mkdir logs
if not exist backup mkdir backup

if not exist registry\Scripts\pip.exe (
    echo Reparando instalacion de pip...
    python -m ensurepip
)

echo Instalando o actualizando dependencias...
pip install -r requirements.txt

echo Iniciando aplicacion...
python main.py

pause 