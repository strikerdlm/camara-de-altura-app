#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
from datetime import datetime

class VueloTab(ttkb.Frame):
    """Tab for managing flight data."""
    
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
        # Flight data
        self.variables['fecha'] = tk.StringVar()
        self.variables['hora_inicio'] = tk.StringVar()
        self.variables['hora_fin'] = tk.StringVar()
        self.variables['tipo_vuelo'] = tk.StringVar()
        self.variables['altura_inicial'] = tk.StringVar()
        self.variables['altura_final'] = tk.StringVar()
        self.variables['tiempo_ascenso'] = tk.StringVar()
        self.variables['tiempo_estadia'] = tk.StringVar()
        self.variables['tiempo_descenso'] = tk.StringVar()
        self.variables['tiempo_total'] = tk.StringVar()
        self.variables['observaciones'] = tk.StringVar()
        
        # Pilot data
        self.variables['piloto_nombre'] = tk.StringVar()
        self.variables['piloto_grado'] = tk.StringVar()
        self.variables['piloto_unidad'] = tk.StringVar()
        
        # Operator data
        self.variables['operador_nombre'] = tk.StringVar()
        self.variables['operador_grado'] = tk.StringVar()
        self.variables['operador_unidad'] = tk.StringVar()
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Header
        header = ttkb.Label(
            self,
            text="Registro de Vuelo",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Flight data section
        flight_frame = ttkb.Labelframe(
            self,
            text="Datos del Vuelo",
            padding=10
        )
        flight_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        flight_frame.columnconfigure(1, weight=1)
        flight_frame.columnconfigure(3, weight=1)
        
        # Flight data fields
        fields = [
            ('Fecha:', 'fecha', 0),
            ('Hora Inicio:', 'hora_inicio', 0),
            ('Hora Fin:', 'hora_fin', 0),
            ('Tipo de Vuelo:', 'tipo_vuelo', 0),
            ('Altura Inicial (ft):', 'altura_inicial', 2),
            ('Altura Final (ft):', 'altura_final', 2),
            ('Tiempo de Ascenso:', 'tiempo_ascenso', 4),
            ('Tiempo de Estadía:', 'tiempo_estadia', 4),
            ('Tiempo de Descenso:', 'tiempo_descenso', 4),
            ('Tiempo Total:', 'tiempo_total', 4)
        ]
        
        for i, (label_text, var_name, col) in enumerate(fields):
            label = ttkb.Label(flight_frame, text=label_text)
            label.grid(row=i, column=col, sticky="w", padx=5, pady=2)
            
            entry = ttkb.Entry(
                flight_frame,
                textvariable=self.variables[var_name]
            )
            entry.grid(
                row=i, column=col+1, sticky="ew", padx=5, pady=2
            )
        
        # Observations
        obs_label = ttkb.Label(flight_frame, text="Observaciones:")
        obs_label.grid(row=10, column=0, sticky="w", padx=5, pady=2)
        
        obs_entry = ttkb.Entry(
            flight_frame,
            textvariable=self.variables['observaciones']
        )
        obs_entry.grid(
            row=10, column=1, columnspan=3, sticky="ew", padx=5, pady=2
        )
        
        # Pilot section
        pilot_frame = ttkb.Labelframe(
            self,
            text="Datos del Piloto",
            padding=10
        )
        pilot_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10)
        )
        pilot_frame.columnconfigure(1, weight=1)
        
        # Pilot fields
        pilot_fields = [
            ('Nombre:', 'piloto_nombre'),
            ('Grado:', 'piloto_grado'),
            ('Unidad:', 'piloto_unidad')
        ]
        
        for i, (label_text, var_name) in enumerate(pilot_fields):
            label = ttkb.Label(pilot_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            entry = ttkb.Entry(
                pilot_frame,
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
            row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10)
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
        """Load flight data into the form fields."""
        # Get flight data from data manager
        flight_data = self.data_manager.current_data.get('vuelo', {})
        
        # Load data into variables
        for var_name, var in self.variables.items():
            var.set(flight_data.get(var_name, ''))
    
    def save_data(self):
        """Save form data."""
        # Collect data from all variables
        flight_data = {}
        for var_name, var in self.variables.items():
            flight_data[var_name] = var.get()
        
        # Save to data manager
        self.data_manager.current_data['vuelo'] = flight_data
        self.data_manager.save_data()
        
        # Show success message
        messagebox.showinfo(
            "Guardado",
            "Datos de vuelo guardados exitosamente"
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
