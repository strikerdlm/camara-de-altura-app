# Registro Entrenamiento en Cámara de Altura

Aplicación para registrar datos de entrenamiento en cámara de altura.

## Requisitos

- Python 3.8 o superior
- Bibliotecas Python (ver requirements.txt)

## Instalación

1. Clonar o descargar este repositorio

2. Crear un entorno virtual:
```
python -m venv registry
```

3. Activar el entorno virtual:
- Windows:
```
registry\Scripts\activate
```
- Linux/Mac:
```
source registry/bin/activate
```

4. Instalar dependencias:
```
pip install -r requirements.txt
```

## Ejecución

Para iniciar la aplicación, ejecute:
```
python main.py
```

O utilice el archivo batch incluido (en Windows):
```
run.bat
```

## Funcionalidades

La aplicación consta de seis pestañas principales:

1. **Datos del Vuelo**: Registro de información administrativa del vuelo, incluyendo:
   - Fecha y número de vuelo
   - Operadores de cámara y RD
   - Personal técnico y médico
   - Tipo de curso y perfil de cámara

2. **Datos de Alumnos**: Tabla para registrar información de:
   - 8 alumnos 
   - 2 operadores internos
   - Campos incluyen: puesto, grado, nombre, edad, sexo, unidad, correo y número de equipo

3. **Informe de Tiempos de Vuelo**:
   - Registro de tiempos de inicio/fin de vuelo
   - Tiempos de hipoxia y visión nocturna
   - Registro de tiempos de recuperación por alumno
   - Cálculo automático de tiempos totales y promedios

4. **Perfil RD**: Gestión de información para vuelos de descompresión rápida:
   - Asignación de operadores internos a puestos específicos
   - Descripción del perfil RD
   - Registro de observaciones detalladas

5. **Reactores**: Seguimiento de reacciones médicas durante los vuelos:
   - Registro de eventos médicos con códigos CIE-10
   - Selección de severidad, tipo de perfil y manejo
   - Tabla con funcionalidad de eliminación para gestionar registros

6. **Síntomas**: Gestión simplificada de síntomas por alumno:
   - Registro de hasta 3 síntomas por alumno
   - Interfaz optimizada para visualización rápida
   - Función de edición y limpieza de datos

## Crear Ejecutable

Para crear un ejecutable de Windows, con el entorno activado:
```
pip install cx_Freeze
python setup.py build
```

El ejecutable se creará en la carpeta `build`.

## Estructura de Datos

La aplicación guarda los datos en los siguientes formatos:
- JSON: `data/vuelos.json`
- CSV: `data/vuelos.csv`
- Excel: `data/vuelos.xlsx`

Además, se crean copias de seguridad automáticas en la carpeta `backup` y un registro de actividad en la carpeta `logs`.

## Personalización

### Configuración de Logo

Para personalizar el logo de la aplicación, coloque una imagen JPEG llamada `logo.jpg` en la carpeta `assets/`. Por defecto, se creará un logo genérico al iniciar la aplicación por primera vez.

### Opciones por Defecto

Las opciones predeterminadas como perfiles de cámara y rangos militares pueden modificarse en los archivos de configuración.

## Autosave

La aplicación cuenta con una función de autoguardado que ejecuta cada 10 segundos para prevenir pérdida de datos.

## Actualizaciones Recientes

### Versión 3.2 (Abril 2024)
- **UI mejorada**: Interfaz más limpia y directa para el registro de síntomas
- **Ventanas de diálogo optimizadas**: Visualización mejorada de la selección de síntomas con ventanas más grandes
- **Simplificación de la interfaz**: Eliminación de elementos visuales innecesarios como viñetas y detalles redundantes
- **Mejora en la usabilidad**: Enfoque en mostrar solo la información esencial de los síntomas

## Desarrollado por

Desarrollado para las Fuerzas Militares de Colombia - Fuerza Aeroespacial Colombiana, Dirección de Medicina Aeroespacial, Subdirección Científica Aeroespacial. 