#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but might need fine-tuning.
build_exe_options = {
    "packages": ["os", "tkinter", "ttkbootstrap", "PIL", "pandas", "datetime", "locale", "json", "logging"],
    "excludes": [],
    "include_files": ["assets/", "data/", "logs/", "backup/"],
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Registro Entrenamiento en Cámara de Altura",
    version="1.0.0",
    description="Aplicación de registro para entrenamiento en cámara de altura",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="Registro.exe", icon="assets/icon.ico")]
)