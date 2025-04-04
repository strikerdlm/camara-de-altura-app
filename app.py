#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import os
import sys
import datetime
from PIL import Image, ImageTk
import locale
import time

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
        """Set the application icon if available"""
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
    
    def setup_styles(self):
        """Setup custom styles for the application using self.style."""
        self.style.configure("TNotebook", tabposition="nw")
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10))
    
    def create_chronometer_frame(self):
        """Creates the frame for the global chronometer at the bottom."""
        chrono_frame = ttkb.Frame(self.main_container, padding=(10, 5), bootstyle="secondary")
        chrono_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Chronometer display label
        self.chrono_label = ttkb.Label(chrono_frame, text="00:00:00", font=("Segoe UI", 12, "bold"), bootstyle="inverse-secondary")
        self.chrono_label.pack(side=tk.LEFT, padx=(10, 20))

        # Buttons
        start_button = ttkb.Button(chrono_frame, text="Iniciar", command=self.start_timer, bootstyle="success-outline", width=8)
        start_button.pack(side=tk.LEFT, padx=5)

        stop_button = ttkb.Button(chrono_frame, text="Detener", command=self.stop_timer, bootstyle="danger-outline", width=8)
        stop_button.pack(side=tk.LEFT, padx=5)

        reset_button = ttkb.Button(chrono_frame, text="Resetear", command=self.reset_timer, bootstyle="warning-outline", width=8)
        reset_button.pack(side=tk.LEFT, padx=5)

        # Add Export Buttons
        export_csv_button = ttkb.Button(chrono_frame, text="Exportar CSV", command=self.export_csv, bootstyle="info-outline", width=12)
        export_csv_button.pack(side=tk.RIGHT, padx=(10, 5)) # Align to the right

        export_excel_button = ttkb.Button(chrono_frame, text="Exportar Excel", command=self.export_excel, bootstyle="info-outline", width=12)
        export_excel_button.pack(side=tk.RIGHT, padx=5) # Align to the right

    def _update_timer(self):
        """Updates the chronometer label every second."""
        if self._timer_running:
            # Calculate elapsed time
            current_elapsed = time.time() - self._start_time
            total_seconds = int(self._elapsed_time + current_elapsed)
            
            # Format as HH:MM:SS
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            self.chrono_label.config(text=time_str)
            
            # Schedule next update
            self._timer_job = self.root.after(1000, self._update_timer)

    def start_timer(self):
        """Starts or resumes the chronometer."""
        if not self._timer_running:
            self._start_time = time.time()
            self._timer_running = True
            self._update_timer()
            print("Timer started")

    def stop_timer(self):
        """Stops the chronometer."""
        if self._timer_running:
            # Cancel scheduled update
            if self._timer_job:
                self.root.after_cancel(self._timer_job)
                self._timer_job = None
            
            # Record elapsed time since last start
            current_elapsed = time.time() - self._start_time
            self._elapsed_time += current_elapsed
            self._timer_running = False
            print("Timer stopped")

    def reset_timer(self):
        """Stops and resets the chronometer to 00:00:00."""
        self.stop_timer() # Ensure it's stopped first
        self._elapsed_time = 0
        self._start_time = None
        self.chrono_label.config(text="00:00:00")
        print("Timer reset")

    def create_tabs(self):
        """Create all application tabs"""
        # Tab 1: Vuelo (Flight Data)
        self.tab1 = VueloTab(self.notebook, self.data_manager)
        self.notebook.add(self.tab1, text="Datos del entrenamiento de hipoxia hipobárica")
        
        # Tab 2: Alumnos (Students)
        self.tab2 = AlumnosTab(self.notebook, self.data_manager)
        self.notebook.add(self.tab2, text="Alumnos")
        
        # Tab 3: Tiempos (Times)
        self.tab3 = TiemposTab(self.notebook, self.data_manager)
        self.notebook.add(self.tab3, text="Tiempos")
        
        # Tab 4: RD (Use the actual RDTab class)
        self.tab4 = RDTab(self.notebook, self.data_manager) # Instantiate RDTab
        self.notebook.add(self.tab4, text="Descompresión Rápida")
        
        # Tab 5: Reactores (Reactors)
        self.tab5 = ReactoresTab(self.notebook, self.data_manager)
        self.notebook.add(self.tab5, text="Reactores")
        
        # Tab 6: Síntomas (Symptoms)
        self.tab6 = SintomasTab(self.notebook, self.data_manager)
        self.notebook.add(self.tab6, text="Síntomas")
    
    def setup_autosave(self):
        """Setup autosave functionality according to rules (10 seconds)."""
        autosave_interval_seconds = 10 
        autosave_interval_ms = autosave_interval_seconds * 1000
        print(f"Setting autosave interval to {autosave_interval_seconds} seconds.")
        
        def autosave():
            try:
                self.data_manager.save_data()
                print(f"Autosave successful: {datetime.datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"Error during autosave: {e}")
            finally:
                # Always reschedule the next autosave
                self._autosave_job = self.root.after(autosave_interval_ms, autosave)
        
        # Start the autosave timer
        self._autosave_job = self.root.after(autosave_interval_ms, autosave)

    def export_csv(self):
        """Handles the Export CSV button click."""
        export_path = self.data_manager.save_to_csv()
        if export_path:
            from tkinter import messagebox
            messagebox.showinfo("Exportación Exitosa", f"Datos exportados a:\n{export_path}")
        else:
            from tkinter import messagebox
            messagebox.showerror("Error de Exportación", "No se pudieron exportar los datos a CSV.")

    def export_excel(self):
        """Handles the Export Excel button click."""
        export_path = self.data_manager.save_to_excel()
        if export_path:
            from tkinter import messagebox
            messagebox.showinfo("Exportación Exitosa", f"Datos exportados a:\n{export_path}")
        else:
            from tkinter import messagebox
            messagebox.showerror("Error de Exportación", "No se pudieron exportar los datos a Excel.")