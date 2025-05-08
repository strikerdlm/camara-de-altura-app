#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
from datetime import datetime

class EntrenamientoTab(ttkb.Frame):
    """Tab for managing training data."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        self.main_app = main_app
        
        # Create variables for form fields
        self.variables = {}
        self.time_entries = {}  # Store entry widgets
        self.create_variables()
        
        # Create the layout
        self.create_widgets()
        self.load_data()
    
    def create_variables(self):
        """Create variables for form fields."""
        # Time recording variables
        time_fields = [
            'ingreso_alumnos',
            'inicio_dnit',
            'inicio_chequeo_oidos',
            'fin_chequeo_oidos',
            'terminacion_dnit',
            'inicio_ascenso',
            'inicio_hipoxia',
            'fin_hipoxia',
            'inicio_vision_nocturna',
            'fin_vision_nocturna',
            'fin_perfil',
            'inicio_rd1',
            'rd1_inicio_descenso',
            'inicio_rd2',
            'rd2_inicio_descenso',
            'hora_terminacion'
        ]
        
        for field in time_fields:
            self.variables[field] = tk.StringVar()
            self.variables[field].trace_add('write', self.on_variable_change)
        
        # Student time variables
        for i in range(1, 9):  # 8 students
            self.variables[f'tiempo_alumno_{i}'] = tk.StringVar()
        
        # Total times
        self.variables['tiempo_total_vuelo'] = tk.StringVar()
        self.variables['tiempo_hipoxia'] = tk.StringVar()
        self.variables['tiempo_vision_nocturna'] = tk.StringVar()
    
    def on_variable_change(self, *args):
        """Handle variable changes."""
        # Save data when variables change
        self._update_datamanager_with_own_data()
        self.data_manager.save_data()
    
    def record_time(self, var_name):
        """Record current time for a specific field."""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.variables[var_name].set(current_time)
            
            # Update entry appearance
            if var_name in self.time_entries:
                entry = self.time_entries[var_name]
                entry.configure(bootstyle="success")
            
            print(f"Time recorded for {var_name}: {current_time}")  # Debug print
            
            # Save immediately
            self.save_specific_time(var_name, current_time)
            
        except Exception as e:
            print(f"Error recording time: {e}")
            messagebox.showerror("Error", f"Error al registrar el tiempo: {str(e)}")
    
    def save_specific_time(self, var_name, time_value):
        """Save a specific time variable to the data manager."""
        try:
            if 'tiempos_entrenamiento' not in self.data_manager.current_data:
                self.data_manager.current_data['tiempos_entrenamiento'] = {}
            
            self.data_manager.current_data['tiempos_entrenamiento'][var_name] = time_value
            self._update_datamanager_with_own_data()
            self.data_manager.save_data()
            print(f"Time saved for {var_name}: {time_value}")  # Debug print
            
        except Exception as e:
            print(f"Error saving time: {e}")
            messagebox.showerror("Error", f"Error al guardar el tiempo: {str(e)}")
    
    def clear_field(self, var_name):
        """Clear a specific field."""
        try:
            self.variables[var_name].set('')
            
            # Update entry appearance
            if var_name in self.time_entries:
                entry = self.time_entries[var_name]
                entry.configure(bootstyle="default")
            
            # Clear from saved data
            if 'tiempos_entrenamiento' in self.data_manager.current_data:
                if var_name in self.data_manager.current_data['tiempos_entrenamiento']:
                    del self.data_manager.current_data['tiempos_entrenamiento'][var_name]
                    self.data_manager.save_data()
            
            print(f"Field cleared: {var_name}")  # Debug print
            
        except Exception as e:
            print(f"Error clearing field: {e}")
            messagebox.showerror("Error", f"Error al limpiar el campo: {str(e)}")
    
    def create_time_field(self, parent, label_text, var_name, row):
        """Create a time field with record and clear buttons."""
        try:
            # Label
            label = ttkb.Label(parent, text=label_text)
            label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            # Frame for entry and buttons
            field_frame = ttkb.Frame(parent)
            field_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            field_frame.columnconfigure(0, weight=1)
            
            # Entry - Now allowing manual editing
            entry = ttkb.Entry(
                field_frame,
                textvariable=self.variables[var_name],
                width=10,
                bootstyle="default"  # Default style for empty entries
            )
            entry.grid(row=0, column=0, sticky="ew")
            self.time_entries[var_name] = entry
            
            # Add validation for manual time entry
            entry.bind('<FocusOut>', lambda e, v=var_name: self.validate_time_entry(v))
            
            # Record button
            record_btn = ttkb.Button(
                field_frame,
                text="⏱",
                command=lambda v=var_name: self.record_time(v),
                width=3,
                bootstyle="info"
            )
            record_btn.grid(row=0, column=1, padx=(5, 0))
            
            # Clear button
            clear_btn = ttkb.Button(
                field_frame,
                text="✕",
                command=lambda v=var_name: self.clear_field(v),
                width=3,
                bootstyle="danger"
            )
            clear_btn.grid(row=0, column=2, padx=(2, 0))
            
        except Exception as e:
            print(f"Error creating time field: {e}")
            messagebox.showerror("Error", f"Error al crear campo de tiempo: {str(e)}")

    def validate_time_entry(self, var_name):
        """Validate manually entered time."""
        try:
            time_str = self.variables[var_name].get().strip()
            if not time_str:  # Empty is allowed
                if var_name in self.time_entries:
                    self.time_entries[var_name].configure(bootstyle="default")
                return True
                
            # Try to parse the time
            datetime.strptime(time_str, '%H:%M:%S')
            
            # If successful, update the entry style and save
            if var_name in self.time_entries:
                self.time_entries[var_name].configure(bootstyle="success")
            self.save_specific_time(var_name, time_str)
            return True
            
        except ValueError:
            # Invalid time format
            messagebox.showerror(
                "Error", 
                "Formato de tiempo inválido. Use HH:MM:SS"
            )
            # Reset to previous valid value or clear
            if 'tiempos_entrenamiento' in self.data_manager.current_data:
                saved_times = self.data_manager.current_data['tiempos_entrenamiento']
                if var_name in saved_times:
                    self.variables[var_name].set(saved_times[var_name])
                else:
                    self.variables[var_name].set('')
            return False
    
    def calculate_student_time(self, student_num):
        """Calculate elapsed time for a student since inicio_hipoxia."""
        inicio = self.variables['inicio_hipoxia'].get()
        if not inicio:
            messagebox.showwarning(
                "Advertencia",
                "No se ha registrado el tiempo de inicio de hipoxia"
            )
            return
        
        try:
            inicio_time = datetime.strptime(inicio, "%H:%M:%S")
            current_time = datetime.now()
            elapsed = current_time - inicio_time
            elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
            self.variables[f'tiempo_alumno_{student_num}'].set(elapsed_str)
        except ValueError:
            messagebox.showerror(
                "Error",
                "Error al calcular el tiempo. Verifique el formato de la hora de inicio."
            )
    
    def calculate_total_times(self):
        """Calculate total flight times."""
        try:
            # Total flight time
            inicio = datetime.strptime(self.variables['ingreso_alumnos'].get(), "%H:%M:%S")
            fin = datetime.strptime(self.variables['hora_terminacion'].get(), "%H:%M:%S")
            total = fin - inicio
            self.variables['tiempo_total_vuelo'].set(str(total).split('.')[0])
            
            # Hypoxia time
            inicio_h = datetime.strptime(self.variables['inicio_hipoxia'].get(), "%H:%M:%S")
            fin_h = datetime.strptime(self.variables['fin_hipoxia'].get(), "%H:%M:%S")
            total_h = fin_h - inicio_h
            self.variables['tiempo_hipoxia'].set(str(total_h).split('.')[0])
            
            # Night vision time
            inicio_v = datetime.strptime(self.variables['inicio_vision_nocturna'].get(), "%H:%M:%S")
            fin_v = datetime.strptime(self.variables['fin_vision_nocturna'].get(), "%H:%M:%S")
            total_v = fin_v - inicio_v
            self.variables['tiempo_vision_nocturna'].set(str(total_v).split('.')[0])
            
        except ValueError as e:
            messagebox.showerror(
                "Error",
                "Error al calcular los tiempos totales. Verifique que todos los tiempos necesarios estén registrados."
            )
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        try:
            # Configure grid
            self.columnconfigure(1, weight=1)
            
            # Header
            header = ttkb.Label(
                self,
                text="Registro de Tiempos de Entrenamiento",
                font=('Segoe UI', 14, 'bold'),
                bootstyle="primary"
            )
            header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
            
            # Time recording section
            time_frame = ttkb.Labelframe(
                self,
                text="Registro de Tiempos",
                padding=10
            )
            time_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
            
            # Time recording fields
            time_fields = [
                ('Ingreso de alumnos a cámara:', 'ingreso_alumnos'),
                ('Inicio tiempo DNIT:', 'inicio_dnit'),
                ('Inicio de perfil de chequeo de oidos y SPN:', 'inicio_chequeo_oidos'),
                ('Finalización de perfil de chequeo de oidos y SPN:', 'fin_chequeo_oidos'),
                ('Terminación DNIT:', 'terminacion_dnit'),
                ('Inicio ascenso:', 'inicio_ascenso'),
                ('Inicio ejercicio de hipoxia:', 'inicio_hipoxia'),
                ('Finalización de ejercicio de hipoxia:', 'fin_hipoxia'),
                ('Inicio de ejercicio de visión nocturna:', 'inicio_vision_nocturna'),
                ('Terminación de ejercicio de visión nocturna:', 'fin_vision_nocturna'),
                ('Finalización de perfil:', 'fin_perfil'),
                ('Inicio ascenso RD1:', 'inicio_rd1'),
                ('RD1 e inicio descenso:', 'rd1_inicio_descenso'),
                ('Inicio ascenso RD2:', 'inicio_rd2'),
                ('RD2 e inicio descenso:', 'rd2_inicio_descenso'),
                ('Hora de terminación de vuelo:', 'hora_terminacion')
            ]
            
            for i, (label_text, var_name) in enumerate(time_fields):
                self.create_time_field(time_frame, label_text, var_name, i)
            
            # Student times section
            student_frame = ttkb.Labelframe(
                self,
                text="Tiempos de Alumnos",
                padding=10
            )
            student_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
            
            for i in range(8):
                student_num = i + 1
                row = i // 2
                col = i % 2 * 2
                
                # Student label
                label = ttkb.Label(
                    student_frame,
                    text=f"Alumno {student_num}:"
                )
                label.grid(row=row, column=col, sticky="w", padx=5, pady=2)
                
                # Time display frame
                time_frame = ttkb.Frame(student_frame)
                time_frame.grid(row=row, column=col+1, sticky="ew", padx=5, pady=2)
                
                # Time entry
                entry = ttkb.Entry(
                    time_frame,
                    textvariable=self.variables[f'tiempo_alumno_{student_num}'],
                    width=10
                )
                entry.pack(side="left", padx=(0, 5))
                
                # Calculate button
                calc_btn = ttkb.Button(
                    time_frame,
                    text="Calcular",
                    command=lambda n=student_num: self.calculate_student_time(n),
                    width=8,
                    bootstyle="info"
                )
                calc_btn.pack(side="left")
            
            # Total times section
            totals_frame = ttkb.Labelframe(
                self,
                text="TIEMPOS",
                padding=10
            )
            totals_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
            
            # Total times fields
            total_fields = [
                ('Tiempo total de vuelo:', 'tiempo_total_vuelo'),
                ('Tiempo de hipoxia:', 'tiempo_hipoxia'),
                ('Tiempo de visión nocturna:', 'tiempo_vision_nocturna')
            ]
            
            for i, (label_text, var_name) in enumerate(total_fields):
                label = ttkb.Label(totals_frame, text=label_text)
                label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
                
                entry = ttkb.Entry(
                    totals_frame,
                    textvariable=self.variables[var_name],
                    width=10
                )
                entry.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            
            # Calculate totals button
            calc_totals_btn = ttkb.Button(
                totals_frame,
                text="Calcular Tiempos Totales",
                command=self.calculate_total_times,
                bootstyle="success"
            )
            calc_totals_btn.grid(row=len(total_fields), column=0, columnspan=2, pady=10)
            
            # Buttons frame
            button_frame = ttkb.Frame(self)
            button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
            
            # Save button
            save_btn = ttkb.Button(
                button_frame,
                text="Guardar Datos",
                command=lambda: self.save_data(triggered_by_user=True),
                bootstyle="success",
                width=15
            )
            save_btn.pack(side=tk.RIGHT, padx=5)
            
            # Clear all button
            clear_btn = ttkb.Button(
                button_frame,
                text="Limpiar Todo",
                command=self.clear_form,
                bootstyle="warning",
                width=15
            )
            clear_btn.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            print(f"Error creating widgets: {e}")
            messagebox.showerror("Error", f"Error al crear widgets: {str(e)}")
    
    def load_data(self):
        """Load training data into the form fields."""
        try:
            saved_times = self.data_manager.current_data.get('tiempos_entrenamiento', {})
            for var_name, var in self.variables.items():
                if var_name in saved_times and saved_times[var_name].strip():
                    var.set(saved_times[var_name])
                    # Update entry appearance if time exists
                    if var_name in self.time_entries:
                        self.time_entries[var_name].configure(bootstyle="success")
                else:
                    var.set('')  # Clear any previous value
                    if var_name in self.time_entries:
                        self.time_entries[var_name].configure(bootstyle="default")
            
            print("Data loaded successfully")  # Debug print
            
        except Exception as e:
            print(f"Error loading data: {e}")
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def _update_datamanager_with_own_data(self):
        """Helper method to update DataManager with this tab's data."""
        time_data = {}
        for var_name, var in self.variables.items():
            value = var.get().strip()
            if value and value != '--:--:--' and value != '00:00:00': 
                time_data[var_name] = value
        
        self.data_manager.current_data['tiempos_entrenamiento'] = time_data
        print(f"Tab3: Updated tiempos_entrenamiento in DataManager: {time_data}")

    def save_data(self, triggered_by_user=True):
        """Save all form data, orchestrating other tabs if triggered by user."""
        print(f"Tab3 save_data called, triggered_by_user={triggered_by_user}")
        self._update_datamanager_with_own_data()
        
        if triggered_by_user:
            if self.main_app:
                tabs_to_save = {
                    'tab1': getattr(self.main_app, 'tab1', None),
                    'tab2': getattr(self.main_app, 'tab2', None),
                    'tab4': getattr(self.main_app, 'tab4', None),
                    'tab6': getattr(self.main_app, 'tab6', None)
                }
                for tab_name, tab_instance in tabs_to_save.items():
                    if tab_instance and hasattr(tab_instance, 'save_data'):
                        print(f"Tab3 orchestrator: Calling save_data on {tab_name}")
                        tab_instance.save_data(triggered_by_user=False)
            
            # After all tabs have updated current_data, call the main save method from DataManager
            self.data_manager.save_data()
            
            messagebox.showinfo(
                "Guardado",
                "Todos los datos han sido guardados exitosamente.",
                parent=self
            )
        # If not triggered_by_user, _update_datamanager_with_own_data was sufficient.
        # The orchestrating tab will handle the final save_data() call and message.
    
    def clear_form(self, confirm=True):
        """Clear all fields in this tab. Only show confirmation if confirm=True."""
        if confirm:
            if not messagebox.askyesno(
                "Confirmar",
                "¿Está seguro de limpiar los campos de entrenamiento?\n\nEsta acción borrará los datos en esta pestaña."
            ):
                return
        # Clear all entry fields for entrenamiento
        for var in self.variables.values():
            var.set('')
        self.update_idletasks()
