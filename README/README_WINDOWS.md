# Guía de Instalación para Windows - Cámara Hiperbárica

Este documento proporciona instrucciones detalladas para configurar y ejecutar la aplicación Cámara Hiperbárica en sistemas Windows, incluyendo soluciones para problemas comunes con antivirus.

## Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Python**: Versión 3.8 o superior
- **Espacio en Disco**: ~500MB (incluyendo entorno virtual)
- **Memoria RAM**: 2GB mínimo recomendado

## Métodos de Instalación

La aplicación puede instalarse por diferentes métodos, dependiendo de su configuración de seguridad y preferencias.

### Método 1: Instalación Estándar (Si no hay problemas con antivirus)

```batch
setup_env.bat
```

### Método 2: Instalación con Script Alternativo (Si hay bloqueos de antivirus)

Si recibe el error: **"This script contains malicious content and has been blocked by your antivirus software"** al ejecutar `python -m venv venv`, utilice nuestro script alternativo:

```batch
bypass_av_venv.bat
```

Este script utiliza métodos alternativos para crear el entorno virtual sin activar las alertas del antivirus.

### Método 3: Entrada Unificada

El método más simple para cualquier sistema es usar nuestro punto de entrada unificado:

```batch
python entry.py
```

## Solución de Problemas de Antivirus

El error "malicious content blocked by your antivirus" ocurre porque los antivirus detectan falsamente como maliciosos los scripts que crean entornos virtuales. Aquí hay varias soluciones:

### Opción 1: Agregar Exclusión al Antivirus

1. Abra la configuración de su antivirus
2. Agregue las siguientes exclusiones:
   - Proceso: `python.exe`
   - Carpeta: La ubicación de su proyecto
   - Archivo: `setup_env.bat`

#### Para Windows Defender:

1. Abra **Seguridad de Windows** → **Protección antivirus y contra amenazas**
2. Haga clic en **Configuración de protección contra virus y amenazas**
3. Desplácese hacia abajo hasta **Exclusiones**
4. Haga clic en **Agregar o quitar exclusiones**
5. Agregue las exclusiones mencionadas anteriormente

### Opción 2: Desactivar Temporalmente el Antivirus

1. Abra la configuración de su antivirus
2. Desactive temporalmente la protección (generalmente hay una opción para desactivarla por 10-30 minutos)
3. Ejecute los scripts de instalación
4. Vuelva a activar el antivirus una vez completada la instalación

### Opción 3: Instalar sin Entorno Virtual

Si todo lo demás falla, puede instalar las dependencias directamente en su sistema:

```batch
python -m pip install --user ttkbootstrap pillow numpy pandas
```

Y luego ejecutar la aplicación con:

```batch
python main.py
```

## Problemas Comunes y Soluciones

### Error: "python no se reconoce como un comando interno o externo"

**Solución**: Asegúrese de que Python esté instalado y agregado al PATH del sistema.

1. Descargue Python desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, marque la opción "Add Python to PATH"
3. Si ya está instalado, agregue manualmente Python al PATH:
   - Busque la ubicación de su instalación de Python
   - Panel de control → Sistema → Configuración avanzada del sistema → Variables de entorno
   - Edite la variable PATH y agregue la ruta a Python

### Error: "No module named 'ttkbootstrap'"

**Solución**: Instale ttkbootstrap manualmente:

```batch
python -m pip install ttkbootstrap
```

### Error: "El archivo de activación no se puede cargar porque la ejecución de scripts está deshabilitada"

**Solución**: Cambie la política de ejecución de PowerShell:

1. Abra PowerShell como administrador
2. Ejecute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Confirme con "Y" cuando se le solicite

## Ejecución de la Aplicación

Una vez completada la instalación correctamente:

### Con Entorno Virtual:
```batch
call venv\Scripts\activate.bat
python main.py
```

### Sin Entorno Virtual:
```batch
python main.py
```

## Verificación de Instalación

Para verificar que todo está correctamente instalado:

```batch
python -c "import tkinter; import ttkbootstrap; print('Todo instalado correctamente')"
```

Si no hay errores, la instalación es correcta.

## Desinstalación

Para desinstalar la aplicación, simplemente elimine la carpeta del proyecto. Si desea conservar sus datos:

1. Respalde la carpeta `data/` antes de eliminar
2. Eliminación del entorno virtual (si corresponde):
   ```batch
   rmdir /s /q venv
   ```

## Soporte

Si encuentra problemas adicionales, consulte los archivos de registro en la carpeta `logs/` o contáctenos a través de:

- Correo electrónico: soporte@ejemplo.com
- Sitio web: https://ejemplo.com/soporte

---

© 2024 Fuerza Aérea Colombiana 