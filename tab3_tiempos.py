#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
from datetime import datetime

class TiemposTab(ttkb.Frame):
    """Tab for managing time records."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Create variables for form fields
        self.variables = {}
        self.create_variables()
        
<<<<<<< HEAD
        # Time Event Definitions (key, display_text)
        self.time_event_definitions = [
            ('ingreso_alumnos', 'Ingreso alumnos a la cámara'),
            ('inicio_dnit', 'Inicio tiempo DNIT'),
            ('inicio_chequeo_oidos', 'Inicio perfil chequeo de oidos y SPN'),
            ('fin_chequeo_oidos', 'Finalización de perfil chequeo de oidos y SPN'),
            ('terminacion_dnit', 'Terminación tiempo DNIT'),
            ('inicio_ascenso', 'Inicio ascenso'),
            ('inicio_hipoxia', 'Inicio Ejercicio de hipoxia'),
            ('fin_hipoxia', 'Finalización ejercicio de hipoxia'),
            ('inicio_vision_nocturna', 'Inicio ejercicio de visión nocturna'),
            ('fin_vision_nocturna', 'Terminación ejercicio de visión nocturna'),
            ('finalizacion_perfil', 'Finalización de perfil'),
            ('inicio_ascenso_rd1', 'Inicio ascenso RD1'),
            ('rd1_inicio_descenso', 'RD1 e inicio descenso'),
            ('inicio_ascenso_rd2', 'Inicio ascenso RD2'),
            ('rd2_inicio_descenso', 'RD2 e inicio descenso'),
        ]
        self.event_keys = [key for key, _ in self.time_event_definitions]

        # Tk Variables Storage
        self.event_time_vars: Dict[str, tk.StringVar] = {}
        self.student_hypoxia_time_vars: Dict[str, tk.StringVar] = {}
        self.calculated_total_time_vars: Dict[str, tk.StringVar] = {}

        # Internal data storage
        self.event_times: Dict[str, Optional[str]] = {}
        
        # Timer for auto-updating
        self.auto_update_timer = None
        
        self.initialize_data()
=======
        # Create the layout
>>>>>>> 05623bafcb4dd46d5d368abaece58d4cebd092c3
        self.create_widgets()
        self.load_data()
    
    def create_variables(self):
        """Create variables for form fields."""
        # Time data
        self.variables['fecha'] = tk.StringVar()
        self.variables['hora_inicio'] = tk.StringVar()
        self.variables['hora_fin'] = tk.StringVar()
        self.variables['tipo_tiempo'] = tk.StringVar()
        self.variables['descripcion'] = tk.StringVar()
        self.variables['observaciones'] = tk.StringVar()
        
<<<<<<< HEAD
        # Start auto-update timer for real-time displays
        self.start_auto_update_timer()
        
    def initialize_data(self):
        """Initialize or load time event and symptom data."""
        # Load event times
        loaded_times = self.data_manager.current_data.get('event_times', {})
        self.event_times = {key: loaded_times.get(key) for key in self.event_keys}

=======
        # Operator data
        self.variables['operador_nombre'] = tk.StringVar()
        self.variables['operador_grado'] = tk.StringVar()
        self.variables['operador_unidad'] = tk.StringVar()
    
>>>>>>> 05623bafcb4dd46d5d368abaece58d4cebd092c3
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Header
        header = ttkb.Label(
            self,
            text="Registro de Tiempos",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Time data section
        time_frame = ttkb.Labelframe(
            self,
            text="Datos del Tiempo",
            padding=10
        )
        time_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        time_frame.columnconfigure(1, weight=1)
        
<<<<<<< HEAD
        save_btn = ttkb.Button(
            button_frame, 
            text="Guardar Tiempos", 
            command=self.save_data,
            bootstyle='success',
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        clear_btn = ttkb.Button(
            button_frame, 
            text="Limpiar Tiempos", 
            command=self.clear_form,
            bootstyle='danger',
            width=15
        )
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        clear_display_btn = ttkb.Button(
            button_frame, 
            text="Limpiar Pantalla", 
            command=self.clear_display,
            bootstyle='warning',
            width=15
        )
        clear_display_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def create_event_times_section(self, parent):
        """Creates the section for recording main flight event times."""
        parent.columnconfigure(1, weight=0) # Button column
        parent.columnconfigure(2, weight=1) # Time label column

        for i, (key, label_text) in enumerate(self.time_event_definitions):
            # Label for the event
            label = ttkb.Label(parent, text=label_text, anchor='w')
            label.grid(row=i, column=0, padx=5, pady=3, sticky='w')

            # Button to record time
            record_btn = ttkb.Button(
                parent,
                text="Registrar",
                command=lambda k=key: self.record_event_time(k),
                bootstyle="primary-outline",
                width=10
            )
            record_btn.grid(row=i, column=1, padx=5, pady=3, sticky='ew')

            # Label to display the recorded time
            time_var = tk.StringVar(value="--:--:--")
            self.event_time_vars[key] = time_var
            time_label = ttkb.Label(
                parent,
                textvariable=time_var,
                font=('Consolas', 10, 'bold'),
                anchor='w', # Align time to the left
                bootstyle="secondary" # Default style
            )
            time_label.grid(row=i, column=2, padx=5, pady=3, sticky='w')
            self.event_time_vars[f"{key}_label"] = time_label # Store ref to label for style changes
    
    def record_event_time(self, event_key: str):
        """Records the current time for a specific event and updates UI."""
        current_time_str = datetime.now().strftime('%H:%M:%S')
        self.event_times[event_key] = current_time_str
        
        if event_key in self.event_time_vars:
            self.event_time_vars[event_key].set(current_time_str)
            # Update label style to indicate recorded
            label_widget = self.event_time_vars.get(f"{event_key}_label")
            if label_widget:
                 label_widget.configure(bootstyle="success") # Change style e.g., to success
        else:
            print(f"Warning: Time variable for key '{event_key}' not found.")
            return # Exit if var doesn't exist

        print(f"Recorded time for {event_key}: {current_time_str}")
        self.save_data() # Save immediately after recording
        self.update_calculated_totals() # Update totals whenever an event time changes

    def create_student_hypoxia_section(self, parent):
        """Creates the section for calculating student elapsed hypoxia time."""
        parent.columnconfigure(1, weight=0) # Button column
        parent.columnconfigure(2, weight=1) # Time label column
        
        for i in range(1, self.num_students + 1):
            student_id = str(i)
            # Label
            label = ttkb.Label(parent, text=f"Alumno {student_id}:", anchor='w')
            label.grid(row=i-1, column=0, padx=5, pady=3, sticky='w')
            
            # Button
            calc_btn = ttkb.Button(
                parent,
                text="Calcular",
                command=lambda s_id=student_id: self.calculate_student_hypoxia_time(s_id),
                bootstyle="warning-outline",
                width=8
            )
            calc_btn.grid(row=i-1, column=1, padx=5, pady=3, sticky='ew')
            
            # Time Display Label
            time_var = tk.StringVar(value="00:00:00")
            self.student_hypoxia_time_vars[student_id] = time_var
            time_label = ttkb.Label(
                parent,
                textvariable=time_var,
                font=('Consolas', 10),
                anchor='w'
            )
            time_label.grid(row=i-1, column=2, padx=5, pady=3, sticky='w')

    def calculate_student_hypoxia_time(self, student_id: str):
        """Calculates elapsed time since 'inicio_hipoxia' for a student."""
        start_hypoxia_time_str = self.event_times.get('inicio_hipoxia')
        end_hypoxia_time_str = self.event_times.get('fin_hipoxia')
        
        if not start_hypoxia_time_str:
            print("Error: 'Inicio Ejercicio de hipoxia' time not recorded.")
            # Optionally show message to user via toast or status bar
            return
            
        try:
            start_time = datetime.strptime(start_hypoxia_time_str, '%H:%M:%S')
            
            # If hypoxia has ended, use the end time instead of current time
            if end_hypoxia_time_str:
                end_time = datetime.strptime(end_hypoxia_time_str, '%H:%M:%S')
                current_time = end_time
            else:
                current_time = datetime.now()
            
            # Convert start_time to datetime object with today's date for comparison
            now = datetime.now()
            start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, \
                                         second=start_time.second, microsecond=0)
            
            # If using end_hypoxia time, convert it to today's date
            if end_hypoxia_time_str:
                end_datetime = now.replace(hour=current_time.hour, minute=current_time.minute, \
                                          second=current_time.second, microsecond=0)
            else:
                end_datetime = now
            
            # Handle case where start time is tomorrow relative to now (e.g., past midnight)
            if start_datetime > end_datetime: 
                 # This indicates start time was likely yesterday, adjust date
                 start_datetime -= timedelta(days=1)

            elapsed_delta = end_datetime - start_datetime
            elapsed_seconds = int(elapsed_delta.total_seconds())
            
            if elapsed_seconds < 0: elapsed_seconds = 0 # Don't show negative time
            
            # Format as HH:MM:SS
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            if student_id in self.student_hypoxia_time_vars:
                 self.student_hypoxia_time_vars[student_id].set(elapsed_str)
            else:
                 print(f"Warning: Variable for student {student_id} hypoxia time not found.")
                 
        except ValueError:
            print(f"Error parsing inicio_hipoxia time: {start_hypoxia_time_str}")
        except Exception as e:
             print(f"Error calculating student hypoxia time: {e}")

    def create_calculated_totals_section(self, parent):
        """Creates the section to display calculated total times."""
        parent.columnconfigure(1, weight=1)
        
        total_definitions = [
            ("total_vuelo", "Tiempo Total de Vuelo:"),
            ("total_hipoxia", "Tiempo de Hipoxia:"),
            ("total_vision", "Tiempo de Visión Nocturna:")
=======
        # Time data fields
        fields = [
            ('Fecha:', 'fecha'),
            ('Hora Inicio:', 'hora_inicio'),
            ('Hora Fin:', 'hora_fin'),
            ('Tipo de Tiempo:', 'tipo_tiempo'),
            ('Descripción:', 'descripcion'),
            ('Observaciones:', 'observaciones')
>>>>>>> 05623bafcb4dd46d5d368abaece58d4cebd092c3
        ]
        
        for i, (label_text, var_name) in enumerate(fields):
            label = ttkb.Label(time_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            if var_name in ['descripcion', 'observaciones']:
                entry = ttkb.Entry(
                    time_frame,
                    textvariable=self.variables[var_name]
                )
                entry.grid(
                    row=i, column=1, columnspan=3, sticky="ew", padx=5, pady=2
                )
            else:
                entry = ttkb.Entry(
                    time_frame,
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
            
<<<<<<< HEAD
        # Clear calculated totals display
        for var in self.calculated_total_time_vars.values():
             var.set("00:00:00")

        self.save_data() # Save the cleared state
        print("Formulario de Tiempos limpiado.") 
        
    def clear_display(self):
        """Clear only the displayed times on screen without affecting stored data."""
        confirm = messagebox.askyesno(
            "Confirmar Limpieza de Pantalla",
            "¿Está seguro que desea limpiar SOLO los tiempos mostrados en pantalla?\nLos datos almacenados no se eliminarán.",
            icon="info",
            parent=self
        )
        if not confirm: return
        
        # Clear UI variables for events without changing stored data
        for key, var in self.event_time_vars.items():
            if not key.endswith("_label"):  # Only clear time vars, not label refs
                var.set("--:--:--")
            label_widget = self.event_time_vars.get(f"{key}_label")
            if label_widget:
                label_widget.configure(bootstyle="secondary")
                
        # Clear student hypoxia display
        for var in self.student_hypoxia_time_vars.values():
            var.set("00:00:00")
            
        # Clear calculated totals display
        for var in self.calculated_total_time_vars.values():
            var.set("00:00:00")
            
        print("Pantalla de Tiempos limpiada. Datos almacenados intactos.")
        
        # Optionally show a message to the user
        Messagebox.show_info(
            "Pantalla limpiada con éxito. Los datos almacenados permanecen intactos.",
            "Pantalla Limpiada",
            parent=self
        ) 

    def start_auto_update_timer(self):
        """Start a timer to periodically update time displays"""
        # Update every 1 second for real-time display
        self.auto_update_timer = self.after(1000, self.update_time_displays)
    
    def update_time_displays(self):
        """Update all dynamic time displays"""
        # Update calculated totals
        self.update_calculated_totals()
        
        # Update student hypoxia times if hypoxia exercise is ongoing
        start_hypoxia = self.event_times.get('inicio_hipoxia')
        end_hypoxia = self.event_times.get('fin_hipoxia')
        
        if start_hypoxia and not end_hypoxia:
            # Hypoxia exercise is ongoing - update all student times
            for student_id in range(1, self.num_students + 1):
                self.calculate_student_hypoxia_time(str(student_id))
        
        # Schedule next update
        self.auto_update_timer = self.after(1000, self.update_time_displays)

    def on_destroy(self, event=None):
        """Clean up resources when tab is destroyed."""
        # Cancel the auto-update timer if it's running
        if self.auto_update_timer:
            self.after_cancel(self.auto_update_timer)
            self.auto_update_timer = None

# Bind the destroy event to clean up resources
if __name__ != "__main__":
    def setup_destroy_handler(self):
        """Set up the destroy event handler."""
        self.bind("<Destroy>", self.on_destroy)
    
    # Add method to TiemposTab class
    TiemposTab.setup_destroy_handler = setup_destroy_handler
    
    # Patch the __init__ method to call setup_destroy_handler
    original_init = TiemposTab.__init__
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.setup_destroy_handler()
    TiemposTab.__init__ = patched_init 
=======
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
        """Load time data into the form fields."""
        # Get time data from data manager
        time_data = self.data_manager.current_data.get('tiempos', {})
        
        # Load data into variables
        for var_name, var in self.variables.items():
            var.set(time_data.get(var_name, ''))
    
    def save_data(self):
        """Save form data."""
        # Collect data from all variables
        time_data = {}
        for var_name, var in self.variables.items():
            time_data[var_name] = var.get()
        
        # Save to data manager
        self.data_manager.current_data['tiempos'] = time_data
        self.data_manager.save_data()
        
        # Show success message
        messagebox.showinfo(
            "Guardado",
            "Datos de tiempos guardados exitosamente"
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
>>>>>>> 05623bafcb4dd46d5d368abaece58d4cebd092c3
