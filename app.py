#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
from datetime import datetime

class App(ttkb.Frame):
    """Main application frame."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Create variables for form fields
        self.variables = {}
        self.create_variables()
        
        # Create the layout
        self.create_widgets()
        self.load_data()
    
    def create_variables(self):
        """Create variables for form fields."""
        # App data
        self.variables['fecha'] = tk.StringVar()
        self.variables['hora_inicio'] = tk.StringVar()
        self.variables['hora_fin'] = tk.StringVar()
        self.variables['tipo_app'] = tk.StringVar()
        self.variables['descripcion'] = tk.StringVar()
        self.variables['observaciones'] = tk.StringVar()
        
        # User data
        self.variables['usuario_nombre'] = tk.StringVar()
        self.variables['usuario_grado'] = tk.StringVar()
        self.variables['usuario_unidad'] = tk.StringVar()
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Header
        header = ttkb.Label(
            self,
            text="Registro de App",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # App data section
        app_frame = ttkb.Labelframe(
            self,
            text="Datos de la App",
            padding=10
        )
        app_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        app_frame.columnconfigure(1, weight=1)
        
        # App data fields
        fields = [
            ('Fecha:', 'fecha'),
            ('Hora Inicio:', 'hora_inicio'),
            ('Hora Fin:', 'hora_fin'),
            ('Tipo de App:', 'tipo_app'),
            ('Descripción:', 'descripcion'),
            ('Observaciones:', 'observaciones')
        ]
        
        for i, (label_text, var_name) in enumerate(fields):
            label = ttkb.Label(app_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            if var_name in ['descripcion', 'observaciones']:
                entry = ttkb.Entry(
                    app_frame,
                    textvariable=self.variables[var_name]
                )
                entry.grid(
                    row=i, column=1, columnspan=3, sticky="ew", padx=5, pady=2
                )
            else:
                entry = ttkb.Entry(
                    app_frame,
                    textvariable=self.variables[var_name]
                )
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
        
        # User section
        user_frame = ttkb.Labelframe(
            self,
            text="Datos del Usuario",
            padding=10
        )
        user_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        user_frame.columnconfigure(1, weight=1)
        
        # User fields
        user_fields = [
            ('Nombre:', 'usuario_nombre'),
            ('Grado:', 'usuario_grado'),
            ('Unidad:', 'usuario_unidad')
        ]
        
        for i, (label_text, var_name) in enumerate(user_fields):
            label = ttkb.Label(user_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            entry = ttkb.Entry(
                user_frame,
                textvariable=self.variables[var_name]
            )
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
        
        # Buttons
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        save_btn = ttkb.Button(
            button_frame,
            text="Guardar Datos",
            command=self.save_data,
            bootstyle="success",
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttkb.Button(
            button_frame,
            text="Limpiar Campos",
            command=self.clear_form,
            bootstyle="warning",
            width=15
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
    
    def load_data(self):
        """Load app data into the form fields."""
        # Get app data from data manager
        app_data = self.data_manager.current_data.get('app', {})
        
        # Load data into variables
        for var_name, var in self.variables.items():
            var.set(app_data.get(var_name, ''))
    
    def save_data(self):
        """Save form data."""
        # Collect data from all variables
        app_data = {}
        for var_name, var in self.variables.items():
            app_data[var_name] = var.get()
        
        # Save to data manager
        self.data_manager.current_data['app'] = app_data
        self.data_manager.save_data()
        
        # Show success message
        messagebox.showinfo(
            "Guardado",
            "Datos de la app guardados exitosamente"
        )
    
    def clear_form(self):
        """Clear all form fields."""
        # Ask for confirmation
        if messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de que desea limpiar todos los campos?"
        ):
            # Clear all variables
            for var in self.variables.values():
                var.set('')
            
            # Show confirmation
            messagebox.showinfo("Limpieza", "Campos limpiados exitosamente")
