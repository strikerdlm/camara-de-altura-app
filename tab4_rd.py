#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
from datetime import datetime

class RDTab(ttkb.Frame):
    """Tab for managing RD records."""
    
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
        # RD data
        self.variables['fecha'] = tk.StringVar()
        self.variables['hora_inicio'] = tk.StringVar()
        self.variables['hora_fin'] = tk.StringVar()
        self.variables['tipo_rd'] = tk.StringVar()
        self.variables['descripcion'] = tk.StringVar()
        self.variables['observaciones'] = tk.StringVar()
        
        # Operator data
        self.variables['operador_nombre'] = tk.StringVar()
        self.variables['operador_grado'] = tk.StringVar()
        self.variables['operador_unidad'] = tk.StringVar()
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttkb.Label(
            self, 
            text="PERFIL DE DESCOMPRESIÓN RÁPIDA", 
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # RD data section
        rd_frame = ttkb.Labelframe(
            self,
            text="Datos del RD",
            padding=10
        )
        rd_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        rd_frame.columnconfigure(1, weight=1)
        
        # RD data fields
        fields = [
            ('Fecha:', 'fecha'),
            ('Hora Inicio:', 'hora_inicio'),
            ('Hora Fin:', 'hora_fin'),
            ('Tipo de RD:', 'tipo_rd'),
            ('Descripción:', 'descripcion'),
            ('Observaciones:', 'observaciones')
        ]
        
        for i, (label_text, var_name) in enumerate(fields):
            label = ttkb.Label(rd_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            if var_name in ['descripcion', 'observaciones']:
                entry = ttkb.Entry(
                    rd_frame,
                    textvariable=self.variables[var_name]
                )
                entry.grid(
                    row=i, column=1, columnspan=3, sticky="ew", padx=5, pady=2
                )
            else:
                entry = ttkb.Entry(
                    rd_frame,
                    textvariable=self.variables[var_name]
                )
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
        
        # Operator section
        operator_frame = ttkb.Labelframe(
            self,
            text="Datos del Operador",
            padding=10
        )
        operator_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10)
        )
        operator_frame.columnconfigure(1, weight=1)
        
        # Operator fields
        operator_fields = [
            ('Nombre:', 'operador_nombre'),
            ('Grado:', 'operador_grado'),
            ('Unidad:', 'operador_unidad')
        ]
        
        for i, (label_text, var_name) in enumerate(operator_fields):
            label = ttkb.Label(operator_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            entry = ttkb.Entry(
                operator_frame,
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
        """Load RD data into the form fields."""
        # Get RD data from data manager
        rd_data = self.data_manager.current_data.get('rd', {})
        
        # Load data into variables
        for var_name, var in self.variables.items():
            var.set(rd_data.get(var_name, ''))
    
    def save_data(self):
        """Save form data."""
        # Collect data from all variables
        rd_data = {}
        for var_name, var in self.variables.items():
            rd_data[var_name] = var.get()
        
        # Save to data manager
        self.data_manager.current_data['rd'] = rd_data
        self.data_manager.save_data()
        
        # Show success message
        messagebox.showinfo(
            "Guardado",
            "Datos de RD guardados exitosamente"
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
