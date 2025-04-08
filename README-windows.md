# Notas para Windows

Para mejorar la compatibilidad con Windows, se han realizado los siguientes ajustes:

1. **Iconos**: El sistema intentará usar archivos `.ico` en Windows si están disponibles. Para habilitar esta característica, coloque un archivo llamado `icon.ico` en la carpeta `assets/`.

2. **Locale**: Se han añadido opciones adicionales para configurar el locale en español en sistemas Windows.

3. **Rutas de archivos**: Se han actualizado todas las rutas para asegurar la compatibilidad entre sistemas operativos.

4. **Scripts de inicio**: El script `lanzar.bat` ha sido actualizado para funcionar correctamente en Windows.

5. **Compatibilidad de PIL/Pillow**: Se ha mejorado la configuración de Pillow para una mejor compatibilidad en Windows.