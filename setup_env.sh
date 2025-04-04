#!/bin/bash

# Console colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE} Configurando entorno virtual para Camara Hiperbarica ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

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
        echo "[$timestamp] ERROR: $error_msg" >> logs/setup_errors.log
        
        if [ "$exit_code" -ne 0 ]; then
            echo -e "${RED}La instalación no pudo completarse.${NC}"
            echo "Presione Enter para salir..."
            read
            exit $exit_code
        fi
    fi
}

# Check if Python is installed
echo "Verificando instalación de Python..."
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

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_VERSION_MAJOR" -lt 3 ] || ([ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -lt 8 ]); then
    handle_error 1 "Se requiere Python 3.8 o superior. Versión detectada: $PYTHON_VERSION"
else
    echo -e "${GREEN}Python $PYTHON_VERSION detectado.${NC}"
fi

# Check if tkinter is available
echo "Verificando disponibilidad de tkinter..."
if ! $PYTHON_CMD -c "import tkinter" &>/dev/null; then
    # On different Linux distros, tkinter might have different package names
    SYSTEM=$(uname -s)
    if [ "$SYSTEM" = "Linux" ]; then
        DISTRO=$(cat /etc/os-release | grep -w ID | cut -d= -f2 | tr -d '"')
        
        echo -e "${YELLOW}Tkinter no está disponible.${NC}"
        
        case $DISTRO in
            "ubuntu"|"debian"|"linuxmint")
                echo -e "Por favor instale tkinter con: ${GREEN}sudo apt-get install python3-tk${NC}"
                ;;
            "fedora")
                echo -e "Por favor instale tkinter con: ${GREEN}sudo dnf install python3-tkinter${NC}"
                ;;
            "arch"|"manjaro")
                echo -e "Por favor instale tkinter con: ${GREEN}sudo pacman -S tk${NC}"
                ;;
            "opensuse"|"suse")
                echo -e "Por favor instale tkinter con: ${GREEN}sudo zypper install python3-tk${NC}"
                ;;
            *)
                echo -e "Por favor instale el paquete de tkinter para Python 3"
                ;;
        esac
        
        handle_error 1 "Tkinter es necesario para esta aplicación."
    elif [ "$SYSTEM" = "Darwin" ]; then
        echo -e "${YELLOW}Tkinter no está disponible en macOS.${NC}"
        echo -e "Por favor, reinstale Python desde python.org con soporte para tkinter."
        handle_error 1 "Tkinter es necesario para esta aplicación."
    else
        handle_error 1 "Tkinter no está disponible. Por favor instale tkinter para su sistema."
    fi
fi

# Check for venv module
echo "Verificando módulo venv..."
if ! $PYTHON_CMD -c "import venv" &>/dev/null; then
    # Get system information
    SYSTEM=$(uname -s)
    
    if [ "$SYSTEM" = "Linux" ]; then
        # Try to detect Linux distribution
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
        else
            DISTRO="unknown"
        fi
        
        echo -e "${YELLOW}Módulo venv no disponible.${NC}"
        
        # Distribution-specific installation commands
        case $DISTRO in
            "ubuntu"|"debian"|"linuxmint"|"pop")
                echo -e "Intentando instalar python3-venv..."
                sudo apt-get install -y python3-venv
                
                # If sudo fails, provide manual instructions
                if [ $? -ne 0 ]; then
                    echo -e "${RED}No se pudo instalar automáticamente.${NC}"
                    echo -e "Por favor ejecute: ${GREEN}sudo apt-get install python3-venv${NC}"
                    handle_error 1 "Se requiere el módulo venv para continuar."
                fi
                ;;
            "fedora"|"rhel"|"centos")
                echo -e "Intentando instalar python3-venv..."
                sudo dnf install -y python3-libs python3-devel python3-pip
                
                if [ $? -ne 0 ]; then
                    echo -e "${RED}No se pudo instalar automáticamente.${NC}"
                    echo -e "Por favor ejecute: ${GREEN}sudo dnf install python3-libs python3-devel python3-pip${NC}"
                    handle_error 1 "Se requiere el módulo venv para continuar."
                fi
                ;;
            "arch"|"manjaro")
                echo -e "En Arch Linux, venv debería estar incluido con Python."
                echo -e "Si falta, intente: ${GREEN}sudo pacman -S python${NC}"
                
                # Try using direct Python functionality if venv module is missing
                echo "Intentando crear entorno virtual usando python3 -m venv directamente..."
                ;;
            "opensuse"|"suse")
                echo -e "Intentando instalar python3-venv..."
                sudo zypper install -y python3-venv
                
                if [ $? -ne 0 ]; then
                    echo -e "${RED}No se pudo instalar automáticamente.${NC}"
                    echo -e "Por favor ejecute: ${GREEN}sudo zypper install python3-venv${NC}"
                    handle_error 1 "Se requiere el módulo venv para continuar."
                fi
                ;;
            *)
                # Try alternate methods for venv creation for unknown distributions
                echo -e "Distribución desconocida. Intentando métodos alternativos..."
                
                # Try using pip to install virtualenv as an alternative
                echo "Instalando virtualenv mediante pip como alternativa..."
                $PYTHON_CMD -m pip install --user virtualenv
                
                if [ $? -eq 0 ]; then
                    # If successful, we'll use virtualenv instead of venv later
                    echo -e "${GREEN}virtualenv instalado como alternativa a venv.${NC}"
                    USE_VIRTUALENV=true
                else
                    echo -e "${RED}No se pudo instalar virtualenv.${NC}"
                    echo "Por favor instale manualmente el módulo venv o virtualenv para su distribución."
                    echo "En la mayoría de distribuciones Linux:"
                    echo "  - Ubuntu/Debian: sudo apt-get install python3-venv"
                    echo "  - Fedora: sudo dnf install python3-libs"
                    echo "  - Arch Linux: sudo pacman -S python"
                    echo "  - openSUSE: sudo zypper install python3-venv"
                    echo "  - O alternativamente: pip install --user virtualenv"
                    handle_error 1 "Se requiere venv o virtualenv para continuar."
                fi
                ;;
        esac
        
        # Check again after attempted install
        if ! $PYTHON_CMD -c "import venv" &>/dev/null && [ "${USE_VIRTUALENV}" != "true" ]; then
            handle_error 1 "No se pudo instalar el módulo venv. Intente instalarlo manualmente según las instrucciones anteriores."
        fi
    elif [ "$SYSTEM" = "Darwin" ]; then
        # macOS handling
        echo -e "${YELLOW}Módulo venv no disponible en macOS.${NC}"
        
        # Try installing with pip first
        echo "Intentando instalar virtualenv con pip..."
        $PYTHON_CMD -m pip install --user virtualenv
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}virtualenv instalado como alternativa a venv.${NC}"
            USE_VIRTUALENV=true
        else
            echo -e "${RED}No se pudo instalar virtualenv.${NC}"
            echo "Intente reinstalar Python desde python.org o utilice:"
            echo "  brew install python"
            handle_error 1 "Se requiere venv o virtualenv para continuar."
        fi
    else
        handle_error 1 "Sistema operativo no reconocido. El módulo venv es necesario para crear el entorno virtual."
    fi
fi

# Create virtual environment if it doesn't exist
USE_VIRTUALENV=${USE_VIRTUALENV:-false}

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual nuevo..."
    
    if [ "$USE_VIRTUALENV" = "true" ]; then
        # Use virtualenv instead of venv if that's what we installed
        $PYTHON_CMD -m virtualenv venv
    else
        # Use standard venv
        $PYTHON_CMD -m venv venv
    fi
    
    if [ $? -ne 0 ]; then
        handle_error 1 "No se pudo crear el entorno virtual."
    fi
else
    echo -e "${GREEN}Entorno virtual ya existe.${NC}"
fi

# Create required directories
mkdir -p assets data logs backup

# Activate virtual environment
echo "Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    handle_error 1 "No se pudo activar el entorno virtual."
fi

# Upgrade pip and setuptools - Fix for distutils and notifications
echo "Actualizando pip y setuptools a las últimas versiones..."
$PYTHON_CMD -m pip install --upgrade pip setuptools wheel --no-warn-script-location
if [ $? -ne 0 ]; then
    handle_error 0 "No se pudo actualizar pip. Intentando continuar..." true
fi

# Install dependencies with fallbacks
echo "Instalando dependencias básicas..."

# Function to install a package with retries and fallbacks
install_package() {
    local package="$1"
    local is_critical="${2:-false}"
    local max_retries=2
    local retry=0
    
    echo "Instalando $package..."
    
    # Try to install the package with binary preference
    pip install --prefer-binary "$package"
    
    # Check if installation was successful
    if [ $? -ne 0 ]; then
        # Retry with different approaches
        while [ $retry -lt $max_retries ]; do
            retry=$((retry + 1))
            echo "Reintento $retry/$max_retries para $package..."
            
            # For retry 1, try with regular pip install
            if [ $retry -eq 1 ]; then
                pip install "$package"
            # For retry 2, try with --no-deps
            elif [ $retry -eq 2 ]; then
                pip install --no-deps "$package"
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
            handle_error 0 "No se pudo instalar $package. La aplicación podría funcionar incorrectamente." true
            return 1
        fi
    else
        echo -e "${GREEN}Instalación de $package exitosa.${NC}"
        return 0
    fi
}

# Install ttkbootstrap first as it's critical
install_package "ttkbootstrap" true

# Install the remaining dependencies
packages=("pillow" "matplotlib")
for pkg in "${packages[@]}"; do
    install_package "$pkg" false
done

# Handle numpy specially due to build issues
echo "Instalando numpy..."
pip install --prefer-binary numpy==1.24.3
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}No se pudo instalar numpy==1.24.3, intentando versión compatible...${NC}"
    pip install --prefer-binary "numpy<2.0.0"
    if [ $? -ne 0 ]; then
        handle_error 0 "No se pudo instalar numpy. Algunas funcionalidades pueden no estar disponibles." true
    fi
fi

# Install remaining packages
remaining_packages=("pandas" "pyarrow" "openpyxl" "python-dotenv" "cairosvg" "svglib")
for pkg in "${remaining_packages[@]}"; do
    install_package "$pkg" false
done

# Verify ttkbootstrap is available before launching
$PYTHON_CMD -c "import ttkbootstrap" 2>/dev/null
if [ $? -ne 0 ]; then
    handle_error 1 "No se pudo verificar la instalación de ttkbootstrap. La aplicación no funcionará correctamente."
fi

echo -e "${GREEN}"
echo "======================================================"
echo " Entorno configurado correctamente!"
echo " Para activar el entorno manualmente:"
echo " source venv/bin/activate"
echo "======================================================"
echo -e "${NC}"

echo "Presione Enter para iniciar la aplicación..."
read

# Launch the application
$PYTHON_CMD main.py
if [ $? -ne 0 ]; then
    handle_error 1 "La aplicación no pudo iniciarse correctamente."
fi 