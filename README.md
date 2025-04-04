# Cámara Hiperbárica - Sistema de Registro

Sistema integrado para el registro de entrenamiento en cámara hiperbárica desarrollado para la Fuerza Aérea Colombiana.

## Descripción

Esta aplicación permite el registro y seguimiento de entrenamientos en cámara de altura, incluyendo datos de vuelo, alumnos, tiempos, reactores y descompresión rápida.

## Requisitos del Sistema

- **Python 3.8 o superior** con soporte para Tkinter
- Espacio en disco: Aproximadamente 500 MB (incluyendo entorno virtual)
- RAM mínima: 2 GB

## Ejecución Rápida (Todas las Plataformas)

El método más sencillo para ejecutar la aplicación es usar el script unificado `entry.py`:

```
python entry.py
```

Este script detectará automáticamente su sistema operativo, realizará la configuración necesaria y ejecutará la aplicación.

### Opciones de Ejecución

```
python entry.py setup    # Solo configura el entorno
python entry.py run      # Solo ejecuta la aplicación (requiere configuración previa)
```

## Ejecución Manual

### Windows

1. **Configuración inicial (primera vez):**
   ```
   setup_env.bat
   ```

2. **Ejecución normal:**
   ```
   run.bat
   ```

### Linux/macOS

1. **Primera vez (permiso de ejecución):**
   ```
   chmod +x setup_env.sh
   chmod +x run.sh
   ```

2. **Configuración inicial:**
   ```
   ./setup_env.sh
   ```

3. **Ejecución normal:**
   ```
   ./run.sh
   ```

#### Para sistemas Linux sin el módulo venv

Si recibe el error "Módulo venv no disponible" y no tiene permisos de administrador, use el método de configuración manual:

1. **Dar permisos de ejecución:**
   ```
   chmod +x setup_manual_venv.sh
   ```

2. **Ejecutar la configuración manual:**
   ```
   ./setup_manual_venv.sh
   ```

Este método utiliza `virtualenv` en lugar de `venv` y no requiere permisos de administrador.

## Estructura de Directorios

```
.
├── assets/          # Recursos gráficos (logos, iconos)
├── backup/          # Copias de seguridad automáticas
├── data/            # Archivos de datos
├── logs/            # Registros y reportes de errores
├── registry/        # Entorno virtual (Windows)
├── venv/            # Entorno virtual (Linux/macOS)
├── main.py          # Punto de entrada principal
├── error_handler.py # Sistema de manejo de errores
├── tab*_*.py        # Módulos de la interfaz
└── config.py        # Configuración de la aplicación
```

## Sistema de Manejo de Errores

La aplicación incluye un robusto sistema de manejo de errores que proporciona:

1. **Mecanismos de Recuperación Automática**: La aplicación intenta solucionar problemas comunes sin intervención del usuario.

2. **Fallbacks para Dependencias**: Si una dependencia no está disponible, el sistema intenta alternativas compatibles.

3. **Adaptación al Entorno**: El sistema se adapta automáticamente a Windows, Linux o macOS.

4. **Registro Detallado**: Todos los eventos importantes se registran en archivos de logs para diagnóstico.

## Resolución de Problemas

### Problemas de Instalación

- **Windows**: Si encuentra errores durante la instalación, ejecute `setup_env.bat` con derechos de administrador.

- **Linux/macOS**: Si encuentra problemas de permisos, asegúrese de que los scripts sean ejecutables:
  ```
  chmod +x setup_env.sh run.sh
  ```

- **Error de tkinter**: Si aparece un error sobre tkinter, instálelo según su sistema:
  - Ubuntu/Debian: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - Arch: `sudo pacman -S tk`
  - macOS: Reinstale Python desde python.org con soporte para tkinter

### Problemas durante la Ejecución

1. **Cierres inesperados**: Verifique los archivos de log en la carpeta `logs/`

2. **Errores de dependencias**: Ejecute el script de configuración nuevamente para reinstalar las dependencias.

3. **Errores de permisos de directorio**: Asegúrese de que la aplicación tenga permisos de escritura en los directorios `data/`, `logs/` y `backup/`.

## Desarrollo y Adaptación

Para desarrolladores que deseen extender o modificar la aplicación:

1. Todos los módulos están organizados por función (pestaña)
2. Las extensiones deben seguir el mismo patrón de manejo de errores
3. El archivo `error_handler.py` contiene utilidades para el manejo robusto de errores

## Licencia

Todos los derechos reservados - Fuerza Aérea Colombiana.

---

© 2024 Fuerza Aérea Colombiana