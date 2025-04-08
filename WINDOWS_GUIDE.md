# Guía de Implementación para Windows

Esta guía proporciona instrucciones detalladas para configurar y ejecutar la aplicación Cámara de Altura en sistemas Windows.

## Requisitos del Sistema

- Windows 10 o superior
- Python 3.8 o superior con soporte para Tkinter
- Aproximadamente 500 MB de espacio en disco (incluyendo entorno virtual)
- Mínimo 2 GB de RAM

## Instalación

### Método 1: Instalación Automática (Recomendado)

1. Descargue o clone el repositorio
2. Haga doble clic en `setup_env.bat` para configurar el entorno automáticamente
3. Una vez completada la configuración, haga doble clic en `lanzar.bat` para iniciar la aplicación

### Método 2: Instalación Manual

Si el método automático no funciona, puede configurar el entorno manualmente:

1. Abra una ventana de comando (CMD) como administrador
2. Navegue hasta el directorio de la aplicación
3. Ejecute los siguientes comandos:

```cmd
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Mejoras de Compatibilidad con Windows

Se han realizado varias mejoras para garantizar la compatibilidad con Windows:

### 1. Iconos de Aplicación

Para una mejor integración con Windows, coloque un archivo `icon.ico` en la carpeta `assets/`. La aplicación usará automáticamente este archivo para mostrar iconos nativos de Windows.

### 2. Configuración de Locale

La aplicación ahora admite los formatos de locale específicos de Windows para español:
- `es-ES`
- `Spanish_Spain`

### 3. Rutas de Archivos

Todas las rutas de archivos ahora utilizan `os.path.join` y `os.path.abspath` para garantizar la compatibilidad entre sistemas operativos.

### 4. Configuración de PIL/Pillow

Se ha mejorado la configuración de Pillow para una mejor compatibilidad con Windows, asegurando que los codecs de imagen se encuentren correctamente.

### 5. Ajuste de Tamaño de Ventana

El tamaño de la ventana se ajusta automáticamente para tener en cuenta la barra de tareas de Windows.

## Solución de Problemas

### Problema: La aplicación no inicia

Soluciones:
1. Verifique que Python esté instalado correctamente y en el PATH del sistema
2. Ejecute `lanzar.bat` como administrador
3. Consulte los archivos de registro en la carpeta `logs/`

### Problema: Errores de tkinter

Solución: Reinstale Python asegurándose de que la opción "tk/tcl" esté seleccionada durante la instalación.

### Problema: Imágenes no se muestran correctamente

Soluciones:
1. Asegúrese de que las imágenes existan en la carpeta `assets/`
2. Reinstale Pillow con `pip install --upgrade --force-reinstall pillow`

### Problema: Errores de permisos

Solución: Ejecute scripts como administrador o asegúrese de que el usuario tenga permisos de escritura en las carpetas:
- `data/`
- `logs/`
- `backup/`

## Archivos Específicos para Windows

- `lanzar.bat`: Script para iniciar la aplicación
- `setup_env.bat`: Script para configurar el entorno
- `entry.py`: Punto de entrada alternativo (compatible con ambos sistemas)
- `windows_compatibility.py`: Funciones auxiliares para Windows

## Contacto y Soporte

Si encuentra problemas específicos de Windows, consulte los archivos de registro en la carpeta `logs/` y contacte al equipo de soporte con esta información.

---

© 2025 - Sistema de Gestión de Cámara de Altura