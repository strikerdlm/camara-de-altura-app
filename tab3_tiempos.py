#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from tkinter import messagebox
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox # For dialogs

class TiemposTab(ttkb.Frame):
    """Tab for flight time recording and calculations, aligned with rules."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Constants
        self.num_students = 8
        
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
        
        self.initialize_data()
        self.create_widgets()
        self.load_data() # Load after widgets exist
        
    def initialize_data(self):
        """Initialize or load time event and symptom data."""
        # Load event times
        loaded_times = self.data_manager.current_data.get('event_times', {})
        self.event_times = {key: loaded_times.get(key) for key in self.event_keys}

    def create_widgets(self):
        """Create the main tab layout with scrollable frame."""
        # Use a ScrolledFrame for content
        scrolled_frame = ScrolledFrame(self, autohide=True)
        scrolled_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        container = scrolled_frame.container

        # Main content frame inside scrollable area
        # Configure container grid with 2 columns
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        # Configure row weights
        container.rowconfigure(0, weight=1) # Event times
        container.rowconfigure(1, weight=1) # Calculated totals

        # --- Top Row --- 
        # --- Column 0: Event Times --- 
        event_frame = ttkb.LabelFrame(
            container, 
            text="Registro de Tiempos de Eventos", 
            padding=10,
            bootstyle="primary"
        )
        event_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", rowspan=2)
        self.create_event_times_section(event_frame)

        # --- Column 1: Student Hypoxia Times --- 
        student_hypoxia_frame = ttkb.LabelFrame(
            container, 
            text="Tiempo Transcurrido Hipoxia (Alumnos)", 
            padding=10,
            bootstyle="warning"
        )
        student_hypoxia_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.create_student_hypoxia_section(student_hypoxia_frame)

        # --- Column 1, Row 1: Calculated Totals --- 
        totals_frame = ttkb.LabelFrame(
            container, 
            text="Tiempos Calculados", 
            padding=10,
            bootstyle="info"
        )
        totals_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.create_calculated_totals_section(totals_frame)

        # --- Action Buttons (Outside Scrollable Frame) --- 
        button_frame = ttkb.Frame(self)
        button_frame.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        
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
        if not start_hypoxia_time_str:
            print("Error: 'Inicio Ejercicio de hipoxia' time not recorded.")
            # Optionally show message to user via toast or status bar
            return
            
        try:
            start_time = datetime.strptime(start_hypoxia_time_str, '%H:%M:%S')
            current_time = datetime.now()
            
            # Convert start_time to datetime object with today's date for comparison
            now = datetime.now()
            start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, \
                                         second=start_time.second, microsecond=0)
            
            # Handle case where start time is tomorrow relative to now (e.g., past midnight)
            if start_datetime > now: 
                 # This indicates start time was likely yesterday, adjust date
                 start_datetime -= timedelta(days=1)

            elapsed_delta = now - start_datetime
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
        ]
        
        for i, (key, label_text) in enumerate(total_definitions):
            # Label
            label = ttkb.Label(parent, text=label_text, anchor='w')
            label.grid(row=i, column=0, padx=5, pady=3, sticky='w')
            
            # Display Label
            time_var = tk.StringVar(value="00:00:00")
            self.calculated_total_time_vars[key] = time_var
            display_label = ttkb.Label(
                parent,
                textvariable=time_var,
                font=('Consolas', 11, 'bold'), # Make it stand out
                bootstyle="info", # Use info color
                anchor='w'
            )
            display_label.grid(row=i, column=1, padx=5, pady=3, sticky='w')

    def update_calculated_totals(self):
        """Calculates and updates the display labels for total times."""
        total_vuelo_str = "--:--:--"
        total_hipoxia_str = "--:--:--"
        total_vision_str = "--:--:--"

        # Helper to parse time string safely
        def parse_time(time_str: Optional[str]) -> Optional[datetime]:
            if not time_str: return None
            try:
                 return datetime.strptime(time_str, '%H:%M:%S')
            except ValueError:
                 return None

        # Helper to format timedelta
        def format_delta(delta: Optional[timedelta]) -> str:
             if delta is None or delta.total_seconds() < 0: return "00:00:00"
             total_seconds = int(delta.total_seconds())
             hours, remainder = divmod(total_seconds, 3600)
             minutes, seconds = divmod(remainder, 60)
             return f"{hours:02}:{minutes:02}:{seconds:02}"
        
        # Helper for timedelta calculation (handles None and date crossing)
        def calculate_delta(start_str: Optional[str], end_str: Optional[str]) -> Optional[timedelta]:
            start = parse_time(start_str)
            end = parse_time(end_str)
            if not start or not end: return None
            
            # Assume same day unless end time is earlier than start time
            delta = end - start
            if delta.total_seconds() < 0:
                 # Assumes end time is on the next day
                 delta += timedelta(days=1)
            return delta

        # Calculate Total Flight Time
        start_vuelo = self.event_times.get('ingreso_alumnos')
        end_vuelo = self.event_times.get('finalizacion_perfil')
        delta_vuelo = calculate_delta(start_vuelo, end_vuelo)
        total_vuelo_str = format_delta(delta_vuelo)
        
        # Calculate Total Hypoxia Time
        start_hipoxia = self.event_times.get('inicio_hipoxia')
        end_hipoxia = self.event_times.get('fin_hipoxia')
        delta_hipoxia = calculate_delta(start_hipoxia, end_hipoxia)
        total_hipoxia_str = format_delta(delta_hipoxia)

        # Calculate Total Night Vision Time
        start_vision = self.event_times.get('inicio_vision_nocturna')
        end_vision = self.event_times.get('fin_vision_nocturna')
        delta_vision = calculate_delta(start_vision, end_vision)
        total_vision_str = format_delta(delta_vision)
        
        # Update UI variables
        if "total_vuelo" in self.calculated_total_time_vars:
             self.calculated_total_time_vars["total_vuelo"].set(total_vuelo_str)
        if "total_hipoxia" in self.calculated_total_time_vars:
             self.calculated_total_time_vars["total_hipoxia"].set(total_hipoxia_str)
        if "total_vision" in self.calculated_total_time_vars:
             self.calculated_total_time_vars["total_vision"].set(total_vision_str)
             
    def load_data(self):
        """Load event times and update UI elements."""
        # Load event times
        for key, time_str in self.event_times.items():
            if key in self.event_time_vars:
                display_val = time_str if time_str else "--:--:--"
                self.event_time_vars[key].set(display_val)
                label_widget = self.event_time_vars.get(f"{key}_label")
                if label_widget:
                     label_widget.configure(bootstyle="success" if time_str else "secondary")
        self.update_calculated_totals()
        
        # Clear student hypoxia times on load
        for var in self.student_hypoxia_time_vars.values():
             var.set("00:00:00")

    def save_data(self):
        """Save current event times to data manager."""
        self.data_manager.current_data['event_times'] = self.event_times
             
        try:
            self.data_manager.save_data()
            print("Event times saved.")
        except Exception as e:
            print(f"Error saving event times: {e}")

    def clear_form(self):
        """Clear all recorded event times and calculated displays."""
        confirm = messagebox.askyesno(
            "Confirmar Limpieza",
            "¿Está seguro que desea limpiar TODOS los tiempos registrados en esta pestaña?",
            icon="warning",
            parent=self
        )
        if not confirm: return

        # Clear event times
        for key in self.event_keys:
            self.event_times[key] = None
        
        # Clear UI variables and styles for events
        for key, var in self.event_time_vars.items():
             if not key.endswith("_label"): # Only clear time vars, not label refs
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

        self.save_data() # Save the cleared state
        print("Formulario de Tiempos limpiado.") 