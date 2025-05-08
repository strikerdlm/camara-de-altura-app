# Cámara de Altura - Sistema de Registro

## Descripción
Sistema de registro y gestión para entrenamiento en cámara de altura, desarrollado para la Fuerza Aérea Colombiana. Esta aplicación está diseñada para funcionar en todas las versiones de Windows (XP a 11) y proporciona una interfaz moderna y eficiente para el registro de datos de entrenamiento.

## Características Principales

### Compatibilidad
- Compatible con Windows XP hasta Windows 11
- Soporte para diferentes resoluciones de pantalla
- Manejo optimizado de DPI en pantallas modernas
- Almacenamiento de datos compatible con todas las versiones de Windows

### Interfaz de Usuario
- Diseño moderno y minimalista
- Interfaz amigable y fácil de usar
- Navegación intuitiva por pestañas
- Soporte para temas visuales
- Iconos de alta resolución

### Funcionalidades
1. **Datos Generales (Tab 1): Datos del vuelo**
   - **Fecha**: Botón para mostrar la fecha actual.
   - **Vuelo del año**: Número secuencial de vuelos en el año actual.
   - **Vuelo total**: Número consecutivo total de vuelos.
   - **Operador de cámara**: Campo para ingresar el nombre del operador.
   - **Operador RD**: Campo para ingresar el nombre del operador de RD.
   - **Lector**: Campo para ingresar el nombre del lector.
   - **Observador de Registro**: Campo para ingresar el nombre del recolector de datos.
   - **Perfil de cámara**: Selección entre "IV-A" y "Descompresión lenta".
   - **Alumnos**: Campo para ingresar el número de participantes.
   - **Director Médico**: Campo para ingresar el nombre del director médico (ej. MY LUIS EDUARDO JEREZ PALACIOS, SMSM DIEGO L MALPICA H).
   - **OE-4**: Campo para ingresar el nombre del OE-4.
   - **Jefe Técnico**: Campo para ingresar el nombre del jefe técnico.
   - **OE-5**: Campo para ingresar el nombre del OE-5.
   - **Curso**: Selección entre "Primera vez" o "Recurrente".

2. **Gestión de Alumnos (Tab 2): Información de Alumnos**
   - Registro de datos para hasta 8 alumnos y 2 OI (Oficiales de Instrucción).
   - Campos por cada participante:
     - **Silla**: Selección (1 - 8, OI1, OI2).
     - **Grado**: Campo de texto para el rango.
     - **Apellido y nombre**: Campo de texto.
     - **Edad**: Campo numérico.
     - **Género**: Selección (F o M).
     - **Unidad**: Campo de texto.
     - **Email**: Campo de texto.
     - **Número de máscara**: Campo numérico.
     - **Número de casco**: Campo numérico.

3. **Control de Tiempos (Tab 3): Informe de tiempos de vuelo**
   - **Cronómetro integrado**: Visible en toda la aplicación (HH:MM:SS) con botones de Iniciar, Detener y Reiniciar.
   - **Registro automático de tiempos**: Botones para registrar los siguientes eventos y guardar la hora actual:
     - Ingreso de alumnos a cámara
     - Inicio tiempo DNIT
     - Inicio de perfil de chequeo de oídos y SPN
     - Finalización de perfil de chequeo de oídos y SPN
     - Terminación DNIT
     - Inicio ascenso
     - Inicio ejercicio de hipoxia
     - Finalización de ejercicio de hipoxia
     - Inicio de ejercicio de visión nocturna
     - Terminación de ejercicio de visión nocturna
     - Finalización de perfil
     - Inicio ascenso RD1
     - RD1 e inicio descenso
     - Inicio ascenso RD2
     - RD2 e inicio descenso
   - **Hora de terminación de vuelo**: Cálculo automático del tiempo transcurrido desde "Ingreso de alumnos a la cámara".
   - **Seguimiento de tiempos por alumno**:
     - Botones individuales para cada alumno (Alumno 1 a Alumno 8).
     - Cálculo y visualización del tiempo transcurrido desde "Inicio ejercicio de hipoxia" para cada alumno.
   - **Cálculos de TIEMPOS**:
     - Botones para calcular y mostrar:
       - Tiempo total de vuelo (HH:MM)
       - Tiempo de hipoxia (HH:MM)
       - Tiempo de visión nocturna (HH:MM)

4. **Gestión RD (Tab 4): Perfil RD**
   - Registro de variables para 2 perfiles de Descompresión Rápida (RD).
   - Campos por perfil RD:
     - **OI**: Selección (OI1 o OI2).
     - **Silla**: Posición original del alumno (1 - 8).
     - **Nueva posición**: Nueva posición del alumno (7 u 8).
     - **Novedad**: Descripción de cualquier emergencia ocurrida durante la RD.

5. **Reactores (Tab 5): Reactores en entrenamiento de hipoxia hipobárica / descompresión rápida**
   - Botón para registrar la hora del evento.
   - **Selección de Código CIE-10 (ICD-10)**:
     - T700 BAROTITIS
     - R064 HIPERVENTILACION
     - T702 HIPOXIA
     - T701 BAROSINUSITIS
     - K040 BARODONTALGIA
     - T703 ENF. POR DESCOMPRESION
     - F402 CLAUSTROFOBIA
     - F409 APREHENSION
   - **Campos adicionales**:
     - **Severidad**: Selección (Leve, Moderado, Severo).
     - **Perfil**: Selección (IV-A, Descompresión Lenta, Descompresión rápida).
     - **Manejo**: Descripción del manejo médico.
     - **Mejora**: Selección (Sí, No).
     - **Altitud (ft)**: Altitud del evento.
     - **Removido**: Selección (Sí, No).
     - **Tratamiento**: Descripción del tratamiento médico.
     - **Remisión**: Selección (Sí, No).
     - **Teléfono**: Número de teléfono del alumno.
     - **Número de máscara**.
     - **Número de casco**.

6. **Síntomas (Tab 6): Registro de Síntomas por Alumno**
   - Espacio para que cada alumno registre hasta 3 síntomas.
   - Interfaz de selección intuitiva.

7. **Exportación (Tab 7): Exportar Datos**
   - Funcionalidad para exportar datos.
   - Soporte para múltiples formatos de exportación (CSV, Excel).
   - Validación de datos antes de la exportación.
   - Generación de reportes.
   - Historial de exportaciones.

8. **Información (Tab 8): Acerca de**
   - Muestra información de la aplicación.

### Almacenamiento y Seguridad
- Guardado automático cada 10 segundos
- Sistema de respaldo integrado
- Almacenamiento en AppData (Windows)
- Protección contra pérdida de datos

## Requisitos del Sistema

### Mínimos
- Windows XP SP3 o superior
- Python 3.7+
- 2GB RAM
- 500MB espacio en disco
- Resolución mínima: 800x600

### Recomendados
- Windows 10/11
- Python 3.9+
- 4GB RAM
- 1GB espacio en disco
- Resolución 1024x768 o superior

## Instalación

1. **Preparación del Entorno**
   ```bash
   # Clonar el repositorio
   git clone https://github.com/strikerdlm/camara-de-altura-app.git
   cd a_camara

   # Crear entorno virtual
   python -m venv registry

   # Activar entorno virtual
   # Windows:
   registry\Scripts\activate
   ```

2. **Instalación de Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuración Inicial**
   ```bash
   # Ejecutar script de configuración
   python setup.py
   ```

## Uso

1. **Iniciar la Aplicación**
   ```bash
   # Windows
   python main.py
   # O usar el acceso directo creado durante la instalación
   ```

2. **Primer Uso**
   - Configurar datos generales en la primera pestaña
   - Verificar la configuración de almacenamiento
   - Realizar una prueba de exportación

## Estructura de Archivos
```
a_camara/
├── assets/           # Recursos gráficos
├── backup/          # Copias de seguridad
├── data/            # Datos de la aplicación
├── exports/         # Archivos exportados
├── logs/            # Registros del sistema
├── tab1_vuelo.py    # Módulo de datos generales
├── tab2_alumnos.py  # Módulo de alumnos
├── tab3_tiempos.py  # Módulo de tiempos
├── tab4_rd.py       # Módulo de RD
├── tab5_reactores.py # Módulo de reactores
├── tab6_sintomas.py # Módulo de síntomas
├── tab7_exportar.py # Módulo de exportación
├── tab8_about.py    # Módulo de información
├── main.py          # Punto de entrada
└── README.md        # Este archivo
```

## Soporte

Para reportar problemas o solicitar ayuda:
1. Abrir un issue en el repositorio
2. Contactar al equipo de soporte técnico
3. Consultar la documentación en línea

## Licencia
© 2025 Fuerza Aérea Colombiana - Subdirección Científica Aeroespacial.
Todos los derechos reservados.

## Créditos
Desarrollado por la Subdirección Científica Aeroespacial de la Fuerza Aérea Colombiana
- Desarrollador Principal: Dr. Diego Malpica, Especialista en Medicina Aeroespacial
- Colaboración: Personal de la Cámara de Altura

# Notas para Windows

Para mejorar la compatibilidad con Windows, se han realizado los siguientes ajustes:

1. **Iconos**: El sistema intentará usar archivos `.ico` en Windows si están disponibles. Para habilitar esta característica, coloque un archivo llamado `icon.ico` en la carpeta `assets/`.

2. **Locale**: Se han añadido opciones adicionales para configurar el locale en español en sistemas Windows.

3. **Rutas de archivos**: Se han actualizado todas las rutas para asegurar la compatibilidad entre sistemas operativos.

4. **Scripts de inicio**: El script `lanzar.bat` ha sido actualizado para funcionar correctamente en Windows.

5. **Compatibilidad de PIL/Pillow**: Se ha mejorado la configuración de Pillow para una mejor compatibilidad en Windows. 
