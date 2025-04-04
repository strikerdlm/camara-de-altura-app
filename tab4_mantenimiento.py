#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
from datetime import datetime

class MantenimientoTab(ttkb.Frame):
    """Tab for managing maintenance records."""
    
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
        # Maintenance data
        self.variables['fecha'] = tk.StringVar()
        self.variables['hora_inicio'] = tk.StringVar()
        self.variables['hora_fin'] = tk.StringVar()
        self.variables['tipo_mantenimiento'] = tk.StringVar()
        self.variables['descripcion'] = tk.StringVar()
        self.variables['piezas_cambiadas'] = tk.StringVar()
        self.variables['observaciones'] = tk.StringVar()
        
        # Technician data
        self.variables['tecnico_nombre'] = tk.StringVar()
        self.variables['tecnico_grado'] = tk.StringVar()
        self.variables['tecnico_unidad'] = tk.StringVar()
        
        # Supervisor data
        self.variables['supervisor_nombre'] = tk.StringVar()
        self.variables['supervisor_grado'] = tk.StringVar()
        self.variables['supervisor_unidad'] = tk.StringVar()
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Header
        header = ttkb.Label(
            self,
            text="Registro de Mantenimiento",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Maintenance data section
        maint_frame = ttkb.Labelframe(
            self,
            text="Datos del Mantenimiento",
            padding=10
        )
        maint_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        maint_frame.columnconfigure(1, weight=1)
        
        # Maintenance data fields
        fields = [
            ('Fecha:', 'fecha'),
            ('Hora Inicio:', 'hora_inicio'),
            ('Hora Fin:', 'hora_fin'),
            ('Tipo de Mantenimiento:', 'tipo_mantenimiento'),
            ('Descripción:', 'descripcion'),
            ('Piezas Cambiadas:', 'piezas_cambiadas'),
            ('Observaciones:', 'observaciones')
        ]
        
        for i, (label_text, var_name) in enumerate(fields):
            label = ttkb.Label(maint_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            if var_name in ['descripcion', 'piezas_cambiadas', 'observaciones']:
                entry = ttkb.Entry(
                    maint_frame,
                    textvariable=self.variables[var_name]
                )
                entry.grid(
                    row=i, column=1, columnspan=3, sticky="ew", padx=5, pady=2
                )
            else:
                entry = ttkb.Entry(
                    maint_frame,
                    textvariable=self.variables[var_name]
                )
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
        
        # Technician section
        tech_frame = ttkb.Labelframe(
            self,
            text="Datos del Técnico",
            padding=10
        )
        tech_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tech_frame.columnconfigure(1, weight=1)
        
        # Technician fields
        tech_fields = [
            ('Nombre:', 'tecnico_nombre'),
            ('Grado:', 'tecnico_grado'),
            ('Unidad:', 'tecnico_unidad')
        ]
        
        for i, (label_text, var_name) in enumerate(tech_fields):
            label = ttkb.Label(tech_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            entry = ttkb.Entry(
                tech_frame,
                textvariable=self.variables[var_name]
            )
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
        
        # Supervisor section
        super_frame = ttkb.Labelframe(
            self,
            text="Datos del Supervisor",
            padding=10
        )
        super_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        super_frame.columnconfigure(1, weight=1)
        
        # Supervisor fields
        super_fields = [
            ('Nombre:', 'supervisor_nombre'),
            ('Grado:', 'supervisor_grado'),
            ('Unidad:', 'supervisor_unidad')
        ]
        
        for i, (label_text, var_name) in enumerate(super_fields):
            label = ttkb.Label(super_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            entry = ttkb.Entry(
                super_frame,
                textvariable=self.variables[var_name]
            )
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
        
        # Buttons
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        
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
        """Load maintenance data into the form fields."""
        # Get maintenance data from data manager
        maint_data = self.data_manager.current_data.get('mantenimiento', {})
        
        # Load data into variables
        for var_name, var in self.variables.items():
            var.set(maint_data.get(var_name, ''))
    
    def save_data(self):
        """Save form data."""
        # Collect data from all variables
        maint_data = {}
        for var_name, var in self.variables.items():
            maint_data[var_name] = var.get()
        
        # Save to data manager
        self.data_manager.current_data['mantenimiento'] = maint_data
        self.data_manager.save_data()
        
        # Show success message
        messagebox.showinfo(
            "Guardado",
            "Datos de mantenimiento guardados exitosamente"
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
