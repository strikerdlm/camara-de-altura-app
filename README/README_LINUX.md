# Guía de Instalación para Linux - Cámara Hiperbárica

Este documento proporciona instrucciones detalladas para configurar y ejecutar la aplicación Cámara Hiperbárica en sistemas operativos Linux.

## Requisitos del Sistema

- **Sistema Operativo**: Cualquier distribución Linux moderna (Ubuntu, Debian, Fedora, CentOS, etc.)
- **Python**: Versión 3.8 o superior
- **Espacio en Disco**: ~500MB (incluyendo entorno virtual)
- **Memoria RAM**: 2GB mínimo recomendado

## Instalación Paso a Paso

### 1. Instalar Dependencias Básicas

Primero, necesitamos instalar Python y otras dependencias esenciales.

#### En Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-tk git
```

#### En Fedora/RHEL/CentOS:

```bash
sudo dnf install -y python3 python3-pip python3-tkinter git
```

#### En Arch Linux:

```bash
sudo pacman -S python python-pip tk git
```

### 2. Descargar la Aplicación

```bash
# Clonar el repositorio (o descargar el zip y extraerlo)
git clone https://github.com/usuario/camara-hiperbarica.git
cd camara-hiperbarica
```

### 3. Configurar Permisos de Ejecución

Es necesario dar permisos de ejecución a los scripts:

```bash
chmod +x setup_env.sh
chmod +x run.sh
chmod +x setup_manual_venv.sh
chmod +x lanzar.sh
```

### 4. Método 1: Instalación con el Script de Entrada Unificado

Este es el método más simple y automático:

```bash
python3 entry.py
```

El script detectará automáticamente su entorno y realizará la configuración necesaria.

### 5. Método 2: Instalación Manual

Si prefiere más control sobre el proceso de instalación:

```bash
# Configurar el entorno
./setup_env.sh

# Ejecutar la aplicación
./run.sh
```

### 6. Método 3: Instalación Manual sin sudo

Si no tiene permisos de administrador o experimenta problemas con venv:

```bash
./setup_manual_venv.sh
```

## Solución de Problemas Comunes

### Error: "python3: command not found"

**Solución**: Instalar Python 3

```bash
# En Ubuntu/Debian
sudo apt update
sudo apt install python3

# En Fedora/RHEL/CentOS
sudo dnf install python3

# En Arch Linux
sudo pacman -S python
```

### Error: "Módulo venv no disponible"

**Solución**: Instalar el módulo venv

```bash
# En Ubuntu/Debian
sudo apt install python3-venv

# En Fedora/RHEL/CentOS
sudo dnf install python3-libs

# En Arch Linux
# (venv debería estar incluido con python)
```

O use el método alternativo:

```bash
./setup_manual_venv.sh
```

### Error: "tkinter no está disponible"

**Solución**: Instalar el paquete tkinter

```bash
# En Ubuntu/Debian
sudo apt install python3-tk

# En Fedora/RHEL/CentOS
sudo dnf install python3-tkinter

# En Arch Linux
sudo pacman -S tk
```

### Error: "npm: command not found"

Si necesita instalar algún paquete de npm durante la configuración:

```bash
# En Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm -y

# En Fedora/RHEL/CentOS
sudo dnf install nodejs npm -y

# En Arch Linux
sudo pacman -S nodejs npm
```

### Error: Problemas de Permisos

Si experimenta errores de permiso al ejecutar los scripts:

```bash
# Dar permisos explícitos
chmod +x setup_env.sh run.sh

# Si el problema persiste con cualquier directorio
chmod -R 755 assets/ data/ logs/ backup/
```

### Error: "No module named 'ttkbootstrap'"

Si ttkbootstrap no se instala correctamente:

```bash
# Activar el entorno virtual primero
source venv/bin/activate

# Instalar manualmente
pip install ttkbootstrap pillow numpy pandas
```

### Error: La Interfaz Gráfica no se Muestra

Si la interfaz gráfica no aparece:

1. Confirme que X11 está instalado y funcionando:
   ```bash
   sudo apt install xorg openbox  # En Ubuntu/Debian
   ```

2. Compruebe la variable DISPLAY:
   ```bash
   echo $DISPLAY
   # Debería mostrar algo como ":0"
   ```

3. Si usa SSH, asegúrese de habilitar el reenvío X11:
   ```bash
   ssh -X usuario@servidor
   ```

## Verificar la Instalación

Para verificar que todo está correctamente instalado:

```bash
source venv/bin/activate
python -c "import tkinter; import ttkbootstrap; print('Todo instalado correctamente')"
```

Si no hay errores, la instalación es correcta.

## Actualizaciones

Para actualizar la aplicación:

1. Respalde sus datos:
   ```bash
   cp -r data/ data_backup/
   ```

2. Actualice el código:
   ```bash
   git pull  # Si usa git
   ```

3. Actualice las dependencias:
   ```bash
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   ```

## Desinstalación

Si desea eliminar la aplicación:

```bash
# Opcional: respaldo de datos primero
cp -r data/ ~/backup_camara_hiperbarica/

# Eliminar directorio completo
cd ..
rm -rf camara-hiperbarica/
```

## Comandos Útiles

- **Activar entorno virtual manualmente**: `source venv/bin/activate`
- **Desactivar entorno virtual**: `deactivate`
- **Ver logs de errores**: `cat logs/app_errors.log`
- **Verificar versión de Python**: `python3 --version`
- **Verificar dependencias instaladas**: `source venv/bin/activate && pip list`
- **Crear un acceso directo en el escritorio**:
  ```bash
  echo "[Desktop Entry]
  Name=Cámara Hiperbárica
  Comment=Sistema de Registro para Cámara de Altura
  Exec=$(pwd)/lanzar.sh
  Icon=$(pwd)/assets/icon.png
  Terminal=false
  Type=Application
  Categories=Utility;" > ~/Desktop/CamaraHiperbarica.desktop
  
  chmod +x ~/Desktop/CamaraHiperbarica.desktop
  ```

## Soporte

Si encuentra problemas adicionales, consulte los archivos de registro en la carpeta `logs/` o contáctenos a través de:

- Correo electrónico: soporte@ejemplo.com
- Sitio web: https://ejemplo.com/soporte

---

© 2024 Fuerza Aérea Colombiana 