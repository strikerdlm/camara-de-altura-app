#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
from datetime import datetime
import locale

# Try to set Spanish locale
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES')
    except locale.Error:
        pass  # Fallback to system default

# Import custom modules
from config import AppConfig
from data_manager import DataManager
from tab1_vuelo import VueloTab
from tab2_alumnos import AlumnosTab 
from tab3_tiempos import TiemposTab
from tab5_reactores import ReactoresTab
from tab4_rd import RDTab # Import the actual RDTab class
from tab6_sintomas import SintomasTab # Import the new Symptoms tab

class RegistroApp:
    def __init__(self, root):
        self.root = root
        self.config = AppConfig()
        self.data_manager = DataManager()
        
        # Chronometer state variables
        self._timer_running = False
        self._start_time = None
        self._elapsed_time = 0
        self._timer_job = None
        
        # Configure the main window
        self.root.title("Registro Entrenamiento de Hipoxia y RD en Cámara Hipobárica")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set application icon
        self.set_icon()
        
        # Create and assign the style object *after* root exists
        self.style = ttkb.Style(theme=root.style.theme.name) # Use the theme passed to main_root

        # Setup styles using the created style object
        self.setup_styles()
        
        # Create main frame
        self.main_container = ttkb.Frame(self.root, bootstyle="light")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create Chronometer Frame (at the bottom)
        self.create_chronometer_frame()

        # Create notebook (tabs) - Pack *above* the chronometer
        self.notebook = ttkb.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0)) # Pad bottom 0
        
        # Create tabs
        self.create_tabs()
        
        # Set up autosave timer
        self.setup_autosave()

    def set_icon(self):
        # Implementation of set_icon method
        pass

    def setup_styles(self):
        # Implementation of setup_styles method
        pass

    def create_chronometer_frame(self):
        # Implementation of create_chronometer_frame method
        pass

    def create_tabs(self):
        # Implementation of create_tabs method
        pass

    def setup_autosave(self):
        # Implementation of setup_autosave method
        pass
