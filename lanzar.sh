#!/bin/bash

# Colors for terminal output
BLUE='\033[0;34m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Make this script executable
chmod +x "$0"

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE} Iniciando Camara Hiperbarica ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# Try to find Python
PYTHON_CMD=""

check_python() {
    local cmd=$1
    if command -v $cmd &>/dev/null; then
        # Check if it's Python 3
        local version=$($cmd --version 2>&1)
        if [[ $version == *"Python 3"* ]]; then
            PYTHON_CMD=$cmd
            return 0
        fi
    fi
    return 1
}

# Try standard Python commands
check_python "python3" || check_python "python" || check_python "/usr/bin/python3" || check_python "/usr/local/bin/python3"

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}ERROR: No se pudo encontrar Python 3 en su sistema.${NC}"
    echo "Por favor instale Python 3.8 o superior."
    
    # Suggest installation command based on OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case $ID in
            ubuntu|debian|linuxmint)
                echo -e "Pruebe: ${GREEN}sudo apt-get install python3${NC}"
                ;;
            fedora)
                echo -e "Pruebe: ${GREEN}sudo dnf install python3${NC}"
                ;;
            centos|rhel)
                echo -e "Pruebe: ${GREEN}sudo yum install python3${NC}"
                ;;
            arch|manjaro)
                echo -e "Pruebe: ${GREEN}sudo pacman -S python${NC}"
                ;;
            *)
                echo "Visite https://www.python.org/downloads/ para descargar Python"
                ;;
        esac
    elif [[ "$(uname)" == "Darwin" ]]; then
        echo -e "En macOS, puede instalarlo con: ${GREEN}brew install python${NC}"
        echo "O descárguelo desde https://www.python.org/downloads/"
    fi
    
    echo ""
    read -p "Presione Enter para salir..." 
    exit 1
fi

echo -e "Usando Python: ${GREEN}$($PYTHON_CMD --version)${NC}"

# Make the scripts executable
chmod +x setup_env.sh run.sh

# Run the entry script
$PYTHON_CMD entry.py

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo -e "${RED}La aplicación finalizó con código de error: $EXIT_CODE${NC}"
else
    echo -e "${GREEN}La aplicación finalizó correctamente.${NC}"
fi

echo ""
read -p "Presione Enter para salir..." 