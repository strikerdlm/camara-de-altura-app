#!/bin/bash

# Script para crear un entorno virtual sin depender del módulo venv
# Útil cuando el módulo venv no está disponible y no se tienen permisos de administrador

# Colores para la salida en terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}  Configuración Manual de Entorno Virtual  ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# Hacer este script ejecutable
chmod +x "$0"

# Determinar el comando de Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    # Verificar si 'python' es Python 3
    python_version=$(python --version 2>&1)
    if [[ $python_version == *"Python 3"* ]]; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}ERROR: Python 3 no está instalado.${NC}"
        echo "Por favor instale Python 3.8 o superior."
        exit 1
    fi
else
    echo -e "${RED}ERROR: Python no está instalado.${NC}"
    echo "Por favor instale Python 3.8 o superior."
    exit 1
fi

echo -e "Usando: ${GREEN}$($PYTHON_CMD --version)${NC}"

# Verificar si pip está disponible
if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    echo -e "${YELLOW}pip no está disponible. Intentando instalar pip...${NC}"
    
    # Descargar get-pip.py
    echo "Descargando get-pip.py..."
    if command -v curl &>/dev/null; then
        curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    elif command -v wget &>/dev/null; then
        wget https://bootstrap.pypa.io/get-pip.py
    else
        echo -e "${RED}ERROR: No se pudo descargar pip. Se requiere curl o wget.${NC}"
        echo "Por favor instale pip manualmente para continuar."
        exit 1
    fi
    
    # Instalar pip
    echo "Instalando pip..."
    $PYTHON_CMD get-pip.py --user
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: No se pudo instalar pip.${NC}"
        exit 1
    else
        echo -e "${GREEN}pip instalado correctamente.${NC}"
        # Eliminar el archivo descargado
        rm get-pip.py
    fi
fi

# Instalar virtualenv si no está disponible
if ! $PYTHON_CMD -m pip list | grep -q virtualenv; then
    echo "Instalando virtualenv..."
    $PYTHON_CMD -m pip install --user virtualenv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: No se pudo instalar virtualenv.${NC}"
        exit 1
    else
        echo -e "${GREEN}virtualenv instalado correctamente.${NC}"
    fi
else
    echo -e "${GREEN}virtualenv ya está instalado.${NC}"
fi

# Crear directorios necesarios
mkdir -p assets data logs backup

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual nuevo..."
    $PYTHON_CMD -m virtualenv venv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: No se pudo crear el entorno virtual.${NC}"
        exit 1
    else
        echo -e "${GREEN}Entorno virtual creado correctamente.${NC}"
    fi
else
    echo -e "${YELLOW}El entorno virtual ya existe.${NC}"
fi

# Activar el entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: No se pudo activar el entorno virtual.${NC}"
    exit 1
fi

# Actualizar pip y setuptools
echo "Actualizando pip y setuptools..."
pip install --upgrade pip setuptools wheel

# Instalar dependencias críticas primero
echo "Instalando dependencias críticas..."
pip install --prefer-binary ttkbootstrap

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: No se pudo instalar ttkbootstrap.${NC}"
    echo "Este paquete es esencial para la aplicación."
    exit 1
fi

# Instalar otras dependencias
echo "Instalando dependencias adicionales..."
pip install --prefer-binary pillow numpy pandas

echo -e "${GREEN}"
echo "======================================================"
echo " Entorno configurado correctamente!"
echo " Para activar el entorno manualmente:"
echo " source venv/bin/activate"
echo "======================================================"
echo -e "${NC}"

# Iniciar la aplicación
echo "Presione Enter para iniciar la aplicación..."
read

$PYTHON_CMD main.py

exit 0 