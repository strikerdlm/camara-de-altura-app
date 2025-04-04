#!/bin/bash
# IMPORTANT: If this file doesn't execute, run:
#   chmod +x run.sh
# This is often needed when files are transferred from Windows to Linux/macOS

# Console colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if the script is being run with execute permissions
check_permissions() {
    if [ ! -x "$0" ]; then
        echo "This script does not have execution permissions."
        echo "Please run: chmod +x $0"
        echo "Then try running the script again."
        exit 1
    fi
}

# Check permissions
check_permissions

echo -e "${BLUE}Iniciando Registro Entrenamiento en Camara de Altura...${NC}"

# Error handling function
handle_error() {
    local exit_code=$1
    local error_msg=$2
    local is_warning=${3:-false}
    
    if [ "$is_warning" = true ]; then
        echo -e "${YELLOW}ADVERTENCIA: $error_msg${NC}"
        # Continue execution for warnings
    else
        echo -e "${RED}ERROR: $error_msg${NC}"
        
        # Create logs directory if it doesn't exist
        mkdir -p logs
        
        # Log error details
        timestamp=$(date "+%Y-%m-%d %H:%M:%S")
        echo "[$timestamp] ERROR: $error_msg" >> logs/run_errors.log
        
        if [ "$exit_code" -ne 0 ]; then
            echo -e "${RED}La aplicación no pudo iniciarse correctamente.${NC}"
            echo "Presione Enter para salir..."
            read
            exit $exit_code
        fi
    fi
}

# Determine Python command
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    # Check if 'python' is Python 3
    python_version=$(python --version 2>&1)
    if [[ $python_version == *"Python 3"* ]]; then
        PYTHON_CMD="python"
    else
        handle_error 1 "Python 3 no está instalado. Por favor instale Python 3.8 o superior."
    fi
else
    handle_error 1 "Python no está instalado. Por favor instale Python 3.8 o superior."
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "El entorno virtual no existe. Ejecutando setup_env.sh primero..."
    bash ./setup_env.sh
    exit $?
fi

# Create required directories
mkdir -p assets data logs backup

# Function to check directory permissions
check_directory_permissions() {
    local dir=$1
    if [ ! -w "$dir" ]; then
        handle_error 0 "El directorio $dir no tiene permisos de escritura. Algunas funcionalidades pueden no estar disponibles." true
        
        # Try to fix permissions
        echo "Intentando corregir permisos para $dir..."
        chmod -R u+w "$dir" 2>/dev/null
        if [ $? -ne 0 ]; then
            handle_error 0 "No se pudieron corregir los permisos. Por favor, ejecute esta aplicación con permisos adecuados." true
        fi
    fi
}

# Check directory permissions
for dir in "assets" "data" "logs" "backup"; do
    check_directory_permissions "$dir"
done

# Activate virtual environment
echo "Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    handle_error 1 "No se pudo activar el entorno virtual. Intente ejecutar setup_env.sh nuevamente."
fi

# Update pip without warnings
echo "Actualizando pip y paquetes de construcción..."
$PYTHON_CMD -m pip install --upgrade pip setuptools wheel --no-warn-script-location > /dev/null 2>&1
if [ $? -ne 0 ]; then
    handle_error 0 "No se pudo actualizar pip. Intentando continuar..." true
fi

# Function to install a package with fallbacks
install_package() {
    local package="$1"
    local is_critical="${2:-false}"
    local max_retries=2
    local retry=0
    
    echo "Verificando/Instalando $package..."
    
    # Check if package is already installed
    if $PYTHON_CMD -c "import $package" &>/dev/null; then
        echo -e "${GREEN}$package ya está instalado.${NC}"
        return 0
    fi
    
    # Try to install the package with binary preference
    pip install --prefer-binary "$package" --no-warn-script-location > /dev/null 2>&1
    
    # Check if installation was successful
    if [ $? -ne 0 ]; then
        # Retry with different approaches
        while [ $retry -lt $max_retries ]; do
            retry=$((retry + 1))
            echo "Reintento $retry/$max_retries para $package..."
            
            # For retry 1, try with regular pip install
            if [ $retry -eq 1 ]; then
                pip install "$package" --no-warn-script-location > /dev/null 2>&1
            # For retry 2, try with --no-deps
            elif [ $retry -eq 2 ]; then
                pip install --no-deps "$package" --no-warn-script-location > /dev/null 2>&1
            fi
            
            # Check if retry was successful
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}Instalación de $package exitosa en el reintento $retry.${NC}"
                return 0
            fi
        done
        
        # If all retries failed
        if [ "$is_critical" = true ]; then
            handle_error 1 "No se pudo instalar $package. Este paquete es esencial."
        else
            handle_error 0 "No se pudo instalar $package. Algunas funcionalidades pueden no estar disponibles." true
            return 1
        fi
    else
        echo -e "${GREEN}Instalación de $package exitosa.${NC}"
        return 0
    fi
}

# Check critical dependencies
# First check without trying to install
if ! $PYTHON_CMD -c "import ttkbootstrap" &>/dev/null; then
    echo "ttkbootstrap no está instalado. Instalando..."
    install_package "ttkbootstrap" true
fi

# Install missing dependencies if any
missing_packages=()

# Basic imports check and collection of missing packages
check_import() {
    local package="$1"
    local import_name="${2:-$1}"
    
    if ! $PYTHON_CMD -c "import $import_name" &>/dev/null; then
        missing_packages+=("$package")
    fi
}

# Check all required packages
check_import "pillow" "PIL"
check_import "numpy"
check_import "pandas"

# If missing packages, try to install them
if [ ${#missing_packages[@]} -gt 0 ]; then
    echo "Instalando dependencias faltantes..."
    for pkg in "${missing_packages[@]}"; do
        install_package "$pkg" false
    done
fi

# Handle numpy specially if missing
if ! $PYTHON_CMD -c "import numpy" &>/dev/null; then
    echo "Instalando numpy..."
    pip install --prefer-binary numpy==1.24.3 --no-warn-script-location
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}No se pudo instalar numpy==1.24.3, intentando versión compatible...${NC}"
        pip install --prefer-binary "numpy<2.0.0" --no-warn-script-location
        if [ $? -ne 0 ]; then
            handle_error 0 "No se pudo instalar numpy. Algunas funcionalidades pueden no estar disponibles." true
        fi
    fi
fi

# Final verification of critical packages
if ! $PYTHON_CMD -c "import ttkbootstrap" &>/dev/null; then
    handle_error 1 "No se pudo verificar la instalación de ttkbootstrap. La aplicación no puede iniciarse."
fi

# Launch application with error handling
echo -e "${GREEN}Iniciando aplicación...${NC}"
$PYTHON_CMD main.py

# Check exit code from Python application
exit_code=$?
if [ $exit_code -ne 0 ]; then
    handle_error $exit_code "La aplicación finalizó con código de error $exit_code."
fi

exit 0 