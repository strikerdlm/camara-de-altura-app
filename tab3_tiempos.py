#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime, timedelta

class TiemposTab(ttkb.Frame):
    """Tab for managing time records."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        self.main_app = main_app
        self.prevent_load_overwrite = False
        
        # Set number of students
        self.num_students = 8
        
        # Create variables for form fields
        self.variables = {}
        self.create_variables()
        
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
            ('finalizacion_entrenamiento', 'Finalización de entrenamiento'),
        ]
        self.event_keys = [key for key, _ in self.time_event_definitions]

        # Tk Variables Storage
        self.event_time_vars: Dict[str, tk.StringVar] = {}
        self.student_hypoxia_time_vars: Dict[str, tk.StringVar] = {}
        self.calculated_total_time_vars: Dict[str, tk.StringVar] = {}
        self.event_time_entries: Dict[str, ttkb.Entry] = {} # Store Entry widgets for styling
        self.student_hypoxia_entries: Dict[str, ttkb.Entry] = {} # Store Entry widgets
        # self.calculated_total_entries: Dict[str, ttkb.Entry] = {} # Reverting to Labels

        # Definitions for calculated total times
        self.total_definitions = [
            ("total_vuelo", "Tiempo Total de Vuelo:"),
            ("total_hipoxia", "Tiempo de Hipoxia:"),
            ("total_vision", "Tiempo de Visión Nocturna:"),
            ("total_dnit", "Tiempo de DNIT:"),
            ("total_ascenso", "Tiempo de Ascenso:"),
            ("total_descenso", "Tiempo de Descenso:"),
            ("total_entrenamiento", "Tiempo Total de entrenamiento:"),
        ]

        # Internal data storage
        self.event_times: Dict[str, Optional[str]] = {}
        
        # New: Store individual student hypoxia end times
        self.student_hypoxia_end_times: Dict[str, Optional[str]] = {}
        # New: Store manually entered/calculated student elapsed hypoxia times
        self.manual_student_hypoxia_elapsed_times: Dict[str, Optional[str]] = {}
        # self.manual_overrides_for_totals: Dict[str, Optional[str]] = {} # Reverting calculated totals to display-only
        
        # Flag to track if student hypoxia time has been calculated
        self.student_hypoxia_calculated: Dict[str, bool] = {}
        
        # Timer for auto-updating
        self.auto_update_timer = None

        # --- FIX: Always initialize these dicts to avoid AttributeError ---
        self.time_entries = {}
        self.student_hypoxia_entries = {}
        # ---------------------------------------------------------------

        # Timer IDs for warning popups
        self.hipoxia_warning_timers = []
        self.vision_warning_timers = []
        self.dnit_warning_timers = []

        self.initialize_data()
        self.create_widgets()
        self.load_data()
        
        # Setup destroy handler
        self.bind("<Destroy>", self.on_destroy)
    
    def _on_data_changed(self, *args):
        """Callback for data changes. Sets the prevent_load_overwrite flag."""
        if not self.prevent_load_overwrite:
            # print(f"TiemposTab: Data changed action, setting prevent_load_overwrite = True") # Optional: very verbose
            self.prevent_load_overwrite = True

    def create_variables(self):
        """Create variables for form fields."""
        # Time data
        self.variables['fecha'] = tk.StringVar()
        self.variables['hora_inicio'] = tk.StringVar()
        self.variables['hora_fin'] = tk.StringVar()
        self.variables['tipo_tiempo'] = tk.StringVar()
        self.variables['descripcion'] = tk.StringVar()
        self.variables['observaciones'] = tk.StringVar()
        
        # Initialize new dictionaries
        self.manual_student_hypoxia_elapsed_times = {}
        # self.manual_overrides_for_totals = {} # Removed
        self.event_time_entries = {}
        self.student_hypoxia_entries = {}
        # self.calculated_total_entries = {} # Removed
        
        # Start auto-update timer for real-time displays
        self.start_auto_update_timer()
        
    def initialize_data(self):
        """Initialize or load time event and symptom data."""
        # Load event times
        loaded_times = self.data_manager.current_data.get('event_times', {})
        self.event_times = {key: loaded_times.get(key) for key in self.event_keys}
        
        # Load student hypoxia end times
        loaded_student_times = self.data_manager.current_data.get('student_hypoxia_end_times', {})
        self.student_hypoxia_end_times = loaded_student_times or {}
        
        # Load manually set student elapsed hypoxia times
        self.manual_student_hypoxia_elapsed_times = self.data_manager.current_data.get('manual_student_hypoxia_elapsed_times', {})
        
        # Load manual overrides for calculated totals - REMOVING THIS
        # self.manual_overrides_for_totals = self.data_manager.current_data.get('manual_overrides_for_totals', {})

        # Initialize calculated flags
        self.student_hypoxia_calculated = {}
        for i in range(1, self.num_students + 1):
            student_id = str(i)
            self.student_hypoxia_calculated[student_id] = student_id in self.student_hypoxia_end_times

    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Header row
        self.rowconfigure(1, weight=1)  # Main content - will expand with window
        self.rowconfigure(2, weight=0)  # Button row
        
        # Header
        header = ttkb.Label(
            self,
            text="Registro de Tiempos",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Create a frame for the main content
        main_content_frame = ttkb.Frame(self)
        main_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.rowconfigure(0, weight=1)
        
        # Create a notebook for different time tracking sections
        self.time_notebook = ttkb.Notebook(main_content_frame)
        self.time_notebook.grid(row=0, column=0, sticky="nsew", pady=5)
        
        # Tab 1: Event Times
        self.event_times_frame = ttkb.Frame(self.time_notebook, padding=10)
        self.time_notebook.add(self.event_times_frame, text="Eventos Principales")
        self.create_event_times_section(self.event_times_frame)
        
        # Tab 2: Student Hypoxia Times
        self.student_times_frame = ttkb.Frame(self.time_notebook, padding=10)
        self.time_notebook.add(self.student_times_frame, text="Tiempos de Hipoxia")
        self.create_student_hypoxia_section(self.student_times_frame)
        
        # Tab 3: Calculated Totals
        self.totals_frame = ttkb.Frame(self.time_notebook, padding=10)
        self.time_notebook.add(self.totals_frame, text="Totales Calculados")
        self.create_calculated_totals_section(self.totals_frame)
        
        # Button frame at the bottom
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        save_btn = ttkb.Button(
            button_frame, 
            text="Guardar Datos", 
            command=lambda: self.save_data(triggered_by_user=True),
            bootstyle='success',
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
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
        
        # Create a ScrolledFrame to make the content scrollable
        scrolled_events_area = ttkb.ScrolledFrame(parent, autohide=True)
        scrolled_events_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Get the child frame from ScrolledFrame to add widgets
        # This events_container will be the .child property of the ScrolledFrame
        events_container = scrolled_events_area
        
        # Configure grid columns on this events_container (the child of ScrolledFrame)
        events_container.columnconfigure(0, weight=1)  # Event label - expands
        events_container.columnconfigure(1, minsize=100)  # Time - fixed width
        events_container.columnconfigure(2, minsize=80)  # Register button - fixed width
        events_container.columnconfigure(3, minsize=40)  # Clear button - fixed width

        # Add event time entries
        for i, (key, label_text) in enumerate(self.time_event_definitions):
            # Label for the event (left-aligned)
            label = ttkb.Label(
                events_container, 
                text=label_text, 
                anchor='w',
                padding=(5, 0)
            )
            label.grid(row=i*2, column=0, sticky='w', padx=(5,0), pady=3)

            # Time display Entry (left-aligned)
            time_var = tk.StringVar(value="--:--:--")
            self.event_time_vars[key] = time_var
            time_entry = ttkb.Entry(
                events_container, 
                textvariable=time_var,
                font=('Consolas', 10, 'bold'),
                width=10, # HH:MM:SS + padding
                bootstyle="default"
            )
            time_entry.grid(row=i*2, column=1, sticky='e', padx=5, pady=3)
            self.event_time_entries[key] = time_entry # Store entry for styling
            time_entry.bind("<FocusOut>", lambda event, k=key: self.handle_manual_event_time_edit(k))

            # Button to record time (right-aligned)
            record_btn = ttkb.Button(
                events_container,
                text="Registrar",
                command=lambda k=key: self.record_event_time(k),
                width=10,
                bootstyle="primary-outline"
            )
            record_btn.grid(row=i*2, column=2, sticky='e', padx=5, pady=3)

            # Clear button (X icon) (right-aligned)
            clear_btn = ttkb.Button(
                events_container,
                text="✕",
                command=lambda k=key: self.clear_event_time(k),
                width=3,
                bootstyle="danger-outline"
            )
            clear_btn.grid(row=i*2, column=3, sticky='e', padx=5, pady=3)

            # Add separator after each row
            separator = ttkb.Separator(events_container, orient="horizontal")
            separator.grid(row=i*2+1, column=0, columnspan=4, sticky="ew", pady=(2, 5))

    def record_event_time(self, event_key: str):
        """Records the current time for a specific event and updates UI."""
        # Only record if not already recorded
        if self.event_times.get(event_key) is None:
            self._on_data_changed() # Mark as dirty before changing data
            current_time_str = datetime.now().strftime('%H:%M:%S')
            self.event_times[event_key] = current_time_str
            
            if event_key in self.event_time_vars:
                self.event_time_vars[event_key].set(current_time_str)
            if event_key in self.event_time_entries:
                self.event_time_entries[event_key].configure(bootstyle="success")
            
            # Save only this specific event time
            if 'event_times' not in self.data_manager.current_data:
                self.data_manager.current_data['event_times'] = {}
            self.data_manager.current_data['event_times'][event_key] = current_time_str
            self.data_manager.save_data()
            
            # Only update totals if relevant events are recorded
            if event_key in ['inicio_hipoxia', 'fin_hipoxia', 'inicio_vision_nocturna', 
                           'fin_vision_nocturna', 'inicio_ascenso', 'finalizacion_perfil']:
                self.update_calculated_totals()
            # Notify main_app for chronometer/topbar logic
            if self.main_app and hasattr(self.main_app, 'notify_event'):
                self.main_app.notify_event(event_key)

            # --- SCHEDULE WARNINGS FOR SPECIFIC EVENTS ---
            if event_key == 'inicio_dnit':
                # Cancel any previous DNIT timers
                for timer_id in self.dnit_warning_timers:
                    self.after_cancel(timer_id)
                self.dnit_warning_timers.clear()
                # DNIT: 10, 20, 30 minutes
                self.dnit_warning_timers.append(self.schedule_warning_popup(10*60, 'DNIT 10 min'))
                self.dnit_warning_timers.append(self.schedule_warning_popup(20*60, 'DNIT 20 min'))
                self.dnit_warning_timers.append(self.schedule_warning_popup(30*60, 'DNIT 30 min'))
            elif event_key == 'inicio_hipoxia':
                # Cancel any previous Hipoxia timers
                for timer_id in self.hipoxia_warning_timers:
                    self.after_cancel(timer_id)
                self.hipoxia_warning_timers.clear()
                # Hipoxia: 4, 6, 7, 8 minutes
                self.hipoxia_warning_timers.append(self.schedule_warning_popup(4*60, 'Hipoxia 4 min'))
                self.hipoxia_warning_timers.append(self.schedule_warning_popup(6*60, 'Hipoxia 6 min'))
                self.hipoxia_warning_timers.append(self.schedule_warning_popup(7*60, 'Hipoxia 7 min'))
                self.hipoxia_warning_timers.append(self.schedule_warning_popup(8*60, 'Hipoxia 8 min'))
            elif event_key == 'fin_hipoxia':
                # Cancel all pending Hipoxia popups
                for timer_id in self.hipoxia_warning_timers:
                    self.after_cancel(timer_id)
                self.hipoxia_warning_timers.clear()
            elif event_key == 'inicio_vision_nocturna':
                # Cancel any previous Vision Nocturna timers
                for timer_id in self.vision_warning_timers:
                    self.after_cancel(timer_id)
                self.vision_warning_timers.clear()
                # Vision nocturna: 3, 5, 8 minutes
                self.vision_warning_timers.append(self.schedule_warning_popup(3*60, 'Vision nocturna 3 min'))
                self.vision_warning_timers.append(self.schedule_warning_popup(5*60, 'Vision nocturna 5 min'))
                self.vision_warning_timers.append(self.schedule_warning_popup(8*60, 'Vision nocturna 8 min'))
            elif event_key == 'fin_vision_nocturna':
                # Cancel all pending Vision Nocturna popups
                for timer_id in self.vision_warning_timers:
                    self.after_cancel(timer_id)
                self.vision_warning_timers.clear()

    def handle_manual_event_time_edit(self, event_key: str):
        """Handles manual edit of an event time Entry."""
        time_str = self.event_time_vars[event_key].get().strip()
        entry_widget = self.event_time_entries[event_key]

        if not time_str or time_str == "--:--:--":
            self.event_times[event_key] = None
            entry_widget.configure(bootstyle="default")
            self._on_data_changed()
            self.data_manager.save_data() # Save the cleared state
            self.update_calculated_totals()
            return

        try:
            datetime.strptime(time_str, '%H:%M:%S')
            self.event_times[event_key] = time_str
            entry_widget.configure(bootstyle="success")
            self._on_data_changed()
            # Save this specific event time
            if 'event_times' not in self.data_manager.current_data:
                self.data_manager.current_data['event_times'] = {}
            self.data_manager.current_data['event_times'][event_key] = time_str
            self.data_manager.save_data()
            self.update_calculated_totals()
        except ValueError:
            messagebox.showerror("Error de Formato", "Formato de tiempo inválido. Use HH:MM:SS.", parent=self)
            # Revert to last known good value or default
            previous_value = self.event_times.get(event_key)
            if previous_value:
                self.event_time_vars[event_key].set(previous_value)
                entry_widget.configure(bootstyle="success")
            else:
                self.event_time_vars[event_key].set("--:--:--")
                entry_widget.configure(bootstyle="default")

    def create_student_hypoxia_section(self, parent):
        """Creates the section for calculating student elapsed hypoxia time."""
        parent.columnconfigure(1, weight=0) # Button column
        parent.columnconfigure(2, weight=1) # Time label column
        parent.columnconfigure(3, weight=0) # Reset button column
        
        # Header row
        header_label = ttkb.Label(parent, text="Estudiante", font=('Segoe UI', 10, 'bold'), anchor='w')
        header_label.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        
        action_label = ttkb.Label(parent, text="Registrar Tiempo", font=('Segoe UI', 10, 'bold'), anchor='w')
        action_label.grid(row=0, column=1, padx=5, pady=3, sticky='w')
        
        time_label = ttkb.Label(parent, text="Tiempo de Hipoxia", font=('Segoe UI', 10, 'bold'), anchor='w')
        time_label.grid(row=0, column=2, padx=5, pady=3, sticky='w')
        
        reset_label = ttkb.Label(parent, text="Reiniciar", font=('Segoe UI', 10, 'bold'), anchor='w')
        reset_label.grid(row=0, column=3, padx=5, pady=3, sticky='w')
        
        # Separator
        separator = ttkb.Separator(parent, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        
        for i in range(1, self.num_students + 1):
            student_id = str(i)
            row_idx = i + 1  # Offset by 2 for header and separator
            
            # Label
            label = ttkb.Label(parent, text=f"Alumno {student_id}:", anchor='w')
            label.grid(row=row_idx, column=0, padx=5, pady=3, sticky='w')
            
            # Calculate Button
            calc_btn = ttkb.Button(
                parent,
                text="Calcular",
                command=lambda s_id=student_id: self.calculate_student_hypoxia_time(s_id),
                bootstyle="warning-outline",
                width=8
            )
            calc_btn.grid(row=row_idx, column=1, padx=5, pady=3, sticky='ew')
            
            # Time Display Label
            time_var = tk.StringVar(value="00:00:00")
            self.student_hypoxia_time_vars[student_id] = time_var
            time_entry = ttkb.Entry(
                parent,
                textvariable=time_var,
                font=('Consolas', 10),
                width=10, # HH:MM:SS
                bootstyle="default"
            )
            time_entry.grid(row=row_idx, column=2, padx=5, pady=3, sticky='w')
            self.student_hypoxia_entries[student_id] = time_entry
            time_entry.bind("<FocusOut>", lambda event, s_id=student_id: self.handle_manual_student_hypoxia_edit(s_id))
            
            # Reset Button
            reset_btn = ttkb.Button(
                parent,
                text="⟲",  # Unicode refresh symbol
                command=lambda s_id=student_id: self.reset_student_hypoxia_time(s_id),
                bootstyle="secondary-outline",
                width=3
            )
            reset_btn.grid(row=row_idx, column=3, padx=5, pady=3, sticky='ew')

    def calculate_student_hypoxia_time(self, student_id: str):
        """Calculates elapsed time since 'inicio_hipoxia' for a student and saves it."""
        start_hypoxia_time_str = self.event_times.get('inicio_hipoxia')
        
        if not start_hypoxia_time_str:
            messagebox.showwarning(
                "Advertencia", 
                "No se ha registrado el tiempo de 'Inicio Ejercicio de hipoxia'. No se puede calcular el tiempo final.",
                parent=self
            )
            return
        
        # Calculate elapsed time logic remains the same, but now we store it differently
        self._on_data_changed()
        try:
            current_time = datetime.now()
            current_end_time_str = current_time.strftime('%H:%M:%S')
            
            # Store this as the student's hypoxia end time (for potential reference, though elapsed is king now)
            self.student_hypoxia_end_times[student_id] = current_end_time_str
            
            # Calculate elapsed time
            start_time_obj = datetime.strptime(start_hypoxia_time_str, '%H:%M:%S')
            # Use current_time as end_time for calculation
            start_datetime_obj = current_time.replace(
                hour=start_time_obj.hour, minute=start_time_obj.minute, 
                second=start_time_obj.second, microsecond=0
            )
            
            if start_datetime_obj > current_time: # If start_time was "yesterday" relative to now
                start_datetime_obj -= timedelta(days=1)

            elapsed_delta = current_time - start_datetime_obj
            elapsed_seconds = max(0, int(elapsed_delta.total_seconds()))
            
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            # Update UI and store this elapsed time
            if student_id in self.student_hypoxia_time_vars:
                self.student_hypoxia_time_vars[student_id].set(elapsed_str)
            self.manual_student_hypoxia_elapsed_times[student_id] = elapsed_str
            if student_id in self.student_hypoxia_entries:
                self.student_hypoxia_entries[student_id].configure(bootstyle="success")

            self.student_hypoxia_calculated[student_id] = True # Mark as calculated/set
            
            self.data_manager.current_data['student_hypoxia_end_times'] = self.student_hypoxia_end_times
            self.data_manager.current_data['manual_student_hypoxia_elapsed_times'] = self.manual_student_hypoxia_elapsed_times
            self.data_manager.save_data()
            
        except Exception as e:
            print(f"Error calculating student hypoxia time: {e}")
            messagebox.showerror("Error", f"Error al calcular tiempo de hipoxia para Alumno {student_id}: {e}", parent=self)

    def handle_manual_student_hypoxia_edit(self, student_id: str):
        """Handles manual edit of a student's elapsed hypoxia time Entry."""
        elapsed_time_str = self.student_hypoxia_time_vars[student_id].get().strip()
        entry_widget = self.student_hypoxia_entries[student_id]

        if not elapsed_time_str or elapsed_time_str == "00:00:00":
            self.manual_student_hypoxia_elapsed_times.pop(student_id, None)
            self.student_hypoxia_end_times.pop(student_id, None) # Clear associated end time if manual elapsed is cleared
            self.student_hypoxia_calculated[student_id] = False
            entry_widget.configure(bootstyle="default")
            self._on_data_changed()
            self.data_manager.save_data() # Save the cleared state
            return

        try:
            # Validate HH:MM:SS format by trying to parse it (though we don't need the object itself for storage)
            parts = list(map(int, elapsed_time_str.split(':')))
            if len(parts) != 3 or not (0 <= parts[0] <= 99 and 0 <= parts[1] <= 59 and 0 <= parts[2] <= 59) : # Basic check
                raise ValueError("Invalid time component value")

            self.manual_student_hypoxia_elapsed_times[student_id] = elapsed_time_str
            # If a manual elapsed time is set, we might not have a precise end_time,
            # or we might decide to clear/ignore student_hypoxia_end_times[student_id]
            # For now, let's keep end_times if they were set by "Calcular", but manual_elapsed takes precedence for display
            self.student_hypoxia_calculated[student_id] = True
            entry_widget.configure(bootstyle="success")
            self._on_data_changed()
            
            if 'manual_student_hypoxia_elapsed_times' not in self.data_manager.current_data:
                self.data_manager.current_data['manual_student_hypoxia_elapsed_times'] = {}
            self.data_manager.current_data['manual_student_hypoxia_elapsed_times'][student_id] = elapsed_time_str
            self.data_manager.save_data()
        except ValueError:
            messagebox.showerror("Error de Formato", "Formato de tiempo inválido. Use HH:MM:SS.", parent=self)
            previous_value = self.manual_student_hypoxia_elapsed_times.get(student_id)
            if previous_value:
                self.student_hypoxia_time_vars[student_id].set(previous_value)
                entry_widget.configure(bootstyle="success")
            else:
                self.student_hypoxia_time_vars[student_id].set("00:00:00")
                entry_widget.configure(bootstyle="default")
                self.student_hypoxia_calculated[student_id] = False

    def reset_student_hypoxia_time(self, student_id: str):
        """Reset a student's hypoxia time calculation."""
        self._on_data_changed()
        self.student_hypoxia_end_times.pop(student_id, None)
        self.manual_student_hypoxia_elapsed_times.pop(student_id, None)
        self.student_hypoxia_calculated[student_id] = False
        
        if student_id in self.student_hypoxia_time_vars:
            self.student_hypoxia_time_vars[student_id].set("00:00:00")
        if student_id in self.student_hypoxia_entries:
            self.student_hypoxia_entries[student_id].configure(bootstyle="default")
        
        self.save_data()

    def create_calculated_totals_section(self, parent):
        """Creates the section to display calculated total times."""
        parent.columnconfigure(1, weight=1)
        
        for i, (key, label_text) in enumerate(self.total_definitions):
            # Label
            label = ttkb.Label(parent, text=label_text, anchor='w')
            label.grid(row=i, column=0, padx=5, pady=5, sticky='w')
            
            # Time Display Entry
            time_var = tk.StringVar(value="00:00:00")
            self.calculated_total_time_vars[key] = time_var
            
            total_time_label = ttkb.Label( # Changed back to Label from Entry
                parent,
                textvariable=time_var,
                font=('Consolas', 12, 'bold'),
                anchor='w',
                bootstyle="info" 
            )
            total_time_label.grid(row=i, column=1, padx=5, pady=5, sticky='w')
        
        # Add update button
        update_btn = ttkb.Button(
            parent,
            text="Actualizar Totales",
            command=self.update_calculated_totals,
            bootstyle="info",
            width=15
        )
        update_btn.grid(row=len(self.total_definitions), column=0, columnspan=2, pady=10, sticky='e')
    
    def update_calculated_totals(self):
        """Calculate and update the total times based on event times."""
        # Total Flight Time: desde ingreso_alumnos hasta finalizacion_perfil
        start_vuelo = self.event_times.get('ingreso_alumnos')
        end_vuelo = self.event_times.get('finalizacion_perfil') # CHANGED to finalizacion_perfil
        
        if start_vuelo and end_vuelo:
            try:
                start_time = datetime.strptime(start_vuelo, '%H:%M:%S')
                end_time = datetime.strptime(end_vuelo, '%H:%M:%S')
                now = datetime.now()
                start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
                end_datetime = now.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)
                if end_datetime < start_datetime:
                    end_datetime += timedelta(days=1)
                delta = end_datetime - start_datetime
                total_seconds = int(delta.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                if 'total_vuelo' in self.calculated_total_time_vars:
                    self.calculated_total_time_vars['total_vuelo'].set(time_str)
                # Find the label widget to style it
                label_widget = self.totals_frame.grid_slaves(row=self.total_definitions.index(("total_vuelo", "Tiempo Total de Vuelo:")) , column=1)[0]
                if isinstance(label_widget, ttkb.Label): label_widget.configure(bootstyle="info")
            except Exception as e:
                print(f"Error calculating total flight time: {e}")
                if 'total_vuelo' in self.calculated_total_time_vars: self.calculated_total_time_vars['total_vuelo'].set("Error")
                label_widget = self.totals_frame.grid_slaves(row=self.total_definitions.index(("total_vuelo", "Tiempo Total de Vuelo:")) , column=1)[0]
                if isinstance(label_widget, ttkb.Label): label_widget.configure(bootstyle="danger")
        else: # Not enough data to calculate, check override or set default
            if 'total_vuelo' in self.calculated_total_time_vars:
                 self.calculated_total_time_vars['total_vuelo'].set("00:00:00")
                 label_widget = self.totals_frame.grid_slaves(row=self.total_definitions.index(("total_vuelo", "Tiempo Total de Vuelo:")) , column=1)[0]
                 if isinstance(label_widget, ttkb.Label): label_widget.configure(bootstyle="info")

        # Total Hipoxia Time: desde inicio_hipoxia hasta fin_hipoxia
        self.calculate_time_range('inicio_hipoxia', 'fin_hipoxia', 'total_hipoxia')
        # Total Vision Nocturna Time: desde inicio_vision_nocturna hasta fin_vision_nocturna
        self.calculate_time_range('inicio_vision_nocturna', 'fin_vision_nocturna', 'total_vision')
        # Total DNIT Time: desde inicio_dnit hasta terminacion_dnit
        self.calculate_time_range('inicio_dnit', 'terminacion_dnit', 'total_dnit')
        # Ascent Time: desde inicio_ascenso hasta inicio_hipoxia
        self.calculate_time_range('inicio_ascenso', 'inicio_hipoxia', 'total_ascenso')
        # Descent Time: desde fin_vision_nocturna hasta finalizacion_perfil
        self.calculate_time_range('fin_vision_nocturna', 'finalizacion_perfil', 'total_descenso')
        # Total Entrenamiento: desde ingreso_alumnos hasta finalizacion_entrenamiento
        self.calculate_time_range('ingreso_alumnos', 'finalizacion_entrenamiento', 'total_entrenamiento')
    
    def calculate_time_range(self, start_key, end_key, total_var_key):
        """Helper to calculate time between two events."""
        start_time_str = self.event_times.get(start_key)
        end_time_str = self.event_times.get(end_key)
        
        if start_time_str and end_time_str:
            try:
                start_time = datetime.strptime(start_time_str, '%H:%M:%S')
                end_time = datetime.strptime(end_time_str, '%H:%M:%S')
                
                # Convert to today's date for proper timedelta calculation
                now = datetime.now()
                start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
                end_datetime = now.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)
                
                # Handle overnight (if end is earlier than start)
                if end_datetime < start_datetime:
                    end_datetime += timedelta(days=1)
                
                # Calculate duration
                delta = end_datetime - start_datetime
                total_seconds = int(delta.total_seconds())
                
                # Format as HH:MM:SS
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                
                # Update the display
                if total_var_key in self.calculated_total_time_vars:
                    self.calculated_total_time_vars[total_var_key].set(time_str)
                # Find the label widget to style it
                row_index = [defn[0] for defn in self.total_definitions].index(total_var_key)
                label_widget = self.totals_frame.grid_slaves(row=row_index, column=1)[0]
                if isinstance(label_widget, ttkb.Label):
                    label_widget.configure(bootstyle="info")
            except Exception as e:
                print(f"Error calculating time range for {start_key} to {end_key}: {e}")
                if total_var_key in self.calculated_total_time_vars: self.calculated_total_time_vars[total_var_key].set("Error")
                row_index = [defn[0] for defn in self.total_definitions].index(total_var_key) # Ensure row_index is defined for error case too
                label_widget = self.totals_frame.grid_slaves(row=row_index, column=1)[0]
                if isinstance(label_widget, ttkb.Label): label_widget.configure(bootstyle="danger")
        else: # Not enough data to calculate, check override or set default
            if total_var_key in self.calculated_total_time_vars:
                self.calculated_total_time_vars[total_var_key].set("00:00:00")
                row_index = [defn[0] for defn in self.total_definitions].index(total_var_key) # Ensure row_index is defined here too
                label_widget = self.totals_frame.grid_slaves(row=row_index, column=1)[0]
                if isinstance(label_widget, ttkb.Label): label_widget.configure(bootstyle="info")

    def load_data(self):
        print(f"[DEBUG] tab3_tiempos: load_data called, prevent_load_overwrite={self.prevent_load_overwrite}")
        if getattr(self, 'prevent_load_overwrite', False):
            return
        """Load saved event times and update UI."""
        # Load event times from data_manager
        event_times = self.data_manager.current_data.get('event_times', {})
        
        # Update UI with loaded times
        for key in self.event_keys:
            if key in event_times and event_times[key]:
                self.event_times[key] = event_times[key]
                if key in self.event_time_vars:
                    self.event_time_vars[key].set(event_times[key])
                if key in self.event_time_entries:
                    self.event_time_entries[key].configure(bootstyle="success")
            else: # Ensure default state for entries not in saved data
                if key in self.event_time_vars: self.event_time_vars[key].set("--:--:--")
                if key in self.event_time_entries: self.event_time_entries[key].configure(bootstyle="default")

        # Load student hypoxia end times and manual elapsed times
        self.student_hypoxia_end_times = self.data_manager.current_data.get('student_hypoxia_end_times', {})
        self.manual_student_hypoxia_elapsed_times = self.data_manager.current_data.get('manual_student_hypoxia_elapsed_times', {})
        
        # Load manual overrides for totals - REMOVING THIS
        # self.manual_overrides_for_totals = self.data_manager.current_data.get('manual_overrides_for_totals', {})

        # NEW: Load displayed calculated totals (primarily for initial display, update_calculated_totals will still run)
        # This part can be simplified as update_calculated_totals will be the source of truth for display
        # However, keeping it won't harm if save_data stores them correctly.
        displayed_calculated_totals = self.data_manager.current_data.get('displayed_calculated_totals', {})
        for key, value in displayed_calculated_totals.items():
            if key in self.calculated_total_time_vars:
                self.calculated_total_time_vars[key].set(value)
                # Set style based on whether it was an override or calculated, if possible, or just default to info
                # Since we removed overrides, this styling logic is simpler now. 
                # The style will be set by update_calculated_totals based on successful calculation or error.
                # We can remove the direct styling here or ensure it aligns with update_calculated_totals.
                # For now, let update_calculated_totals handle the definitive styling.
                pass # Styling handled by update_calculated_totals

        # Update student hypoxia time displays
        start_hypoxia_time_str = self.event_times.get('inicio_hipoxia')
        
        for student_id_str in map(str, range(1, self.num_students + 1)):
            elapsed_to_display = "00:00:00"
            style = "default"
            is_calculated = False

            if student_id_str in self.manual_student_hypoxia_elapsed_times:
                elapsed_to_display = self.manual_student_hypoxia_elapsed_times[student_id_str]
                style = "success" # Or "warning" to indicate manual
                is_calculated = True
            elif start_hypoxia_time_str and student_id_str in self.student_hypoxia_end_times:
                end_time_str = self.student_hypoxia_end_times[student_id_str]
                try:
                    start_time = datetime.strptime(start_hypoxia_time_str, '%H:%M:%S')
                    end_time = datetime.strptime(end_time_str, '%H:%M:%S')
                    now = datetime.now()
                    start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, 
                                              second=start_time.second, microsecond=0)
                    end_datetime = now.replace(hour=end_time.hour, minute=end_time.minute, 
                                            second=end_time.second, microsecond=0)
                    if end_datetime < start_datetime: end_datetime += timedelta(days=1)
                    
                    elapsed_delta = end_datetime - start_datetime
                    elapsed_seconds = max(0, int(elapsed_delta.total_seconds()))
                    hours, remainder = divmod(elapsed_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    elapsed_to_display = f"{hours:02}:{minutes:02}:{seconds:02}"
                    style = "success"
                    is_calculated = True
                except Exception as e:
                    print(f"Error loading student {student_id_str} hypoxia time: {e}")
                    elapsed_to_display = "Error"
                    style = "danger"
            
            if student_id_str in self.student_hypoxia_time_vars:
                self.student_hypoxia_time_vars[student_id_str].set(elapsed_to_display)
            if student_id_str in self.student_hypoxia_entries:
                self.student_hypoxia_entries[student_id_str].configure(bootstyle=style)
            self.student_hypoxia_calculated[student_id_str] = is_calculated
        
        # Update calculated totals (this will respect overrides if any, or calculate)
        self.update_calculated_totals()
    
    def _update_datamanager_with_own_data(self):
        """Helper method to update DataManager with this tab's data."""
        times_to_save = {}
        for key, value in self.event_times.items():
            if value is not None and value.strip() != '' and value != '--:--:--':
                times_to_save[key] = value
        self.data_manager.current_data['event_times'] = times_to_save

        hypoxia_times_to_save = {}
        for student_id, time_val in self.student_hypoxia_end_times.items():
            if time_val and time_val.strip() != '' and time_val != '00:00:00':
                hypoxia_times_to_save[student_id] = time_val
        self.data_manager.current_data['student_hypoxia_end_times'] = hypoxia_times_to_save

        manual_elapsed_to_save = {}
        for student_id, time_val in self.manual_student_hypoxia_elapsed_times.items():
            if time_val and time_val.strip() != '' and time_val != '00:00:00':
                manual_elapsed_to_save[student_id] = time_val
        self.data_manager.current_data['manual_student_hypoxia_elapsed_times'] = manual_elapsed_to_save
        
        session_id = self.data_manager.current_data.get('vuelo', {}).get('numero_entrenamiento', '')
        if not session_id:
            vuelo_del_ano = self.data_manager.current_data.get('vuelo', {}).get('vuelo_del_ano', '')
            if vuelo_del_ano:
                try:
                    int(vuelo_del_ano) # Validate
                    year_suffix = datetime.now().strftime("%y")
                    session_id = f"{vuelo_del_ano}-{year_suffix}"
                except ValueError:
                    pass # session_id remains empty if vuelo_del_ano is not a number

        if session_id:
            if 'sessions_data' not in self.data_manager.current_data:
                self.data_manager.current_data['sessions_data'] = {}
            if session_id not in self.data_manager.current_data['sessions_data']:
                self.data_manager.current_data['sessions_data'][session_id] = {}
            
            session_data = self.data_manager.current_data['sessions_data'][session_id]
            session_data['event_times'] = times_to_save
            session_data['student_hypoxia_end_times'] = hypoxia_times_to_save
            session_data['manual_student_hypoxia_elapsed_times'] = manual_elapsed_to_save
            # Convert StringVar objects to their string values before saving
            displayed_totals_values = {
                key: var.get() for key, var in self.calculated_total_time_vars.items()
            }
            session_data['displayed_calculated_totals'] = displayed_totals_values
        print(f"Tab3_Tiempos: Updated its data in DataManager for session {session_id}")

    def save_data(self, triggered_by_user=True, show_message=True):
        print(f"Tab3_Tiempos save_data called, triggered_by_user={triggered_by_user}")
        self._update_datamanager_with_own_data()

        if triggered_by_user:
            if self.main_app:
                tabs_to_call = {
                    'tab1': getattr(self.main_app, 'tab1', None),
                    'tab2': getattr(self.main_app, 'tab2', None),
                    # 'tab3' is self, so no call to self.main_app.tab3
                    'tab4': getattr(self.main_app, 'tab4', None),
                    'tab6': getattr(self.main_app, 'tab6', None)
                }
                for tab_name, tab_instance in tabs_to_call.items():
                    if tab_instance and hasattr(tab_instance, 'save_data'):
                        print(f"Tab3_Tiempos orchestrator: Calling save_data on {tab_name}")
                        try:
                            tab_instance.save_data(triggered_by_user=False)
                        except Exception as e_call:
                            print(f"Error calling save_data on {tab_name} from Tab3_Tiempos: {e_call}")
            
            try:
                self.data_manager.save_data()
                if self.main_app and hasattr(self.main_app, 'refresh_all_tabs'):
                    self.main_app.refresh_all_tabs()
                if show_message: # Only show message if it's the primary orchestrator and successful
                    messagebox.showinfo("Guardado", "Todos los datos han sido guardados exitosamente.", parent=self)
                self.prevent_load_overwrite = False
            except Exception as e_save:
                print(f"Error during final save_data call from Tab3_Tiempos: {e_save}")
                messagebox.showerror("Error", f"Error al guardar datos finales: {str(e_save)}", parent=self)
        else:
            # Called by another tab, _update_datamanager_with_own_data is enough.
            # The orchestrating tab will handle the final save and message.
            self.prevent_load_overwrite = False

    def clear_display(self):
        """Clear only the displayed times on screen without affecting stored data."""
        confirm = messagebox.askyesno(
            "Confirmar Limpieza de Pantalla",
            "¿Está seguro que desea limpiar SOLO los tiempos mostrados en pantalla?\nLos datos almacenados no se eliminarán.",
            icon="info",
            parent=self
        )
        if not confirm: 
            return
        
        # Clear UI variables and stored event times
        self.event_times = {key: None for key in self.event_keys}
        
        # Clear time displays and reset styles for event times
        for key in self.event_keys:
            if key in self.event_time_vars:
                self.event_time_vars[key].set("--:--:--")
            if key in self.event_time_entries: # Check if entry exists
                self.event_time_entries[key].configure(bootstyle="default")
                
        # Clear student hypoxia display and data
        self.student_hypoxia_end_times = {}
        self.manual_student_hypoxia_elapsed_times = {}
        self.student_hypoxia_calculated = {str(i): False for i in range(1, self.num_students + 1)}
        for student_id_str in map(str, range(1, self.num_students + 1)):
            if student_id_str in self.student_hypoxia_time_vars:
                self.student_hypoxia_time_vars[student_id_str].set("00:00:00")
            if student_id_str in self.student_hypoxia_entries: # Check if entry exists
                self.student_hypoxia_entries[student_id_str].configure(bootstyle="default")
            
        # Clear calculated totals display and overrides
        # self.manual_overrides_for_totals = {} # Removed
        # Define total_definitions here or ensure it's accessible
        # total_definitions_local is no longer needed as self.total_definitions is available
        for i, (key, _) in enumerate(self.total_definitions): # Use self.total_definitions
            if key in self.calculated_total_time_vars:
                self.calculated_total_time_vars[key].set("00:00:00")
            # if key in self.calculated_total_entries: # Check if entry exists
            #     self.calculated_total_entries[key].configure(bootstyle="info") # Reset to default calculated style
            # Find the label widget to style it
            # This assumes totals_frame is the direct parent and structure is consistent
            try:
                label_widget = self.totals_frame.grid_slaves(row=i, column=1)[0]
                if isinstance(label_widget, ttkb.Label):
                    label_widget.configure(bootstyle="info")
            except IndexError:
                print(f"Could not find label for {key} at row {i} col 1 in clear_display")
            
        print("Pantalla de Tiempos limpiada.")
        
        messagebox.showinfo(
            "Pantalla Limpiada",
            "Pantalla limpiada con éxito.",
            parent=self
        )

    def start_auto_update_timer(self):
        """Start a timer to periodically update time displays"""
        # Update every 1 second for real-time display
        self.auto_update_timer = self.after(1000, self.update_time_displays)
    
    def update_time_displays(self):
        """Update all dynamic time displays"""
        # Only update student hypoxia times that are actively being calculated
        start_hypoxia = self.event_times.get('inicio_hipoxia')
        
        if start_hypoxia:
            for student_id in self.student_hypoxia_time_vars.keys():
                if not self.student_hypoxia_calculated.get(student_id, False):
                    self.display_running_hypoxia_time(student_id)
        
        # Reschedule the timer
        self.auto_update_timer = self.after(1000, self.update_time_displays)
    
    def display_running_hypoxia_time(self, student_id: str):
        """Display running time since inicio_hipoxia without saving it."""
        start_hypoxia_time_str = self.event_times.get('inicio_hipoxia')
        
        if not start_hypoxia_time_str:
            return
            
        try:
            # Parse start time
            start_time = datetime.strptime(start_hypoxia_time_str, '%H:%M:%S')
            
            # Current time as the end time
            current_time = datetime.now()
            
            # Convert to today's date for proper calculation
            now = datetime.now()
            start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, 
                                       second=start_time.second, microsecond=0)
            
            # Handle case where start time is tomorrow relative to now (e.g., past midnight)
            if start_datetime > current_time:
                # This indicates start time was likely yesterday, adjust date
                start_datetime -= timedelta(days=1)

            # Calculate time difference
            elapsed_delta = current_time - start_datetime
            elapsed_seconds = int(elapsed_delta.total_seconds())
            
            if elapsed_seconds < 0: 
                elapsed_seconds = 0  # Don't show negative time
            
            # Format as HH:MM:SS
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            # Update display if not already calculated
            if student_id in self.student_hypoxia_time_vars and not self.student_hypoxia_calculated.get(student_id, False):
                self.student_hypoxia_time_vars[student_id].set(elapsed_str)
                
        except Exception as e:
            print(f"Error displaying running hypoxia time: {e}")
            
    def on_destroy(self, event=None):
        """Cancel timers and perform cleanup when the tab is destroyed."""
        print("TiemposTab is being destroyed - cleaning up")
        if self.auto_update_timer:
            self.after_cancel(self.auto_update_timer)
            self.auto_update_timer = None
        # Cancel all warning popups
        for timer_id in self.hipoxia_warning_timers:
            self.after_cancel(timer_id)
        self.hipoxia_warning_timers.clear()
        for timer_id in self.vision_warning_timers:
            self.after_cancel(timer_id)
        self.vision_warning_timers.clear()
        for timer_id in self.dnit_warning_timers:
            self.after_cancel(timer_id)
        self.dnit_warning_timers.clear()
        # Clean up event bindings
        if hasattr(self, 'events_bindings'):
            for widget, event_name, func in self.events_bindings:
                try:
                    widget.unbind(event_name)
                except:
                    pass
        
        # Clean up any other bindings
        if hasattr(self, 'events_canvas'):
            try:
                self.events_canvas.delete("all")
            except:
                pass

    def clear_event_time(self, event_key: str):
        """Clear the time for a specific event."""
        if event_key in self.event_times:
            self._on_data_changed() # Mark as dirty before changing data
            self.event_times[event_key] = None
            if event_key in self.event_time_vars: # Check if var exists
                self.event_time_vars[event_key].set('--:--:--')
            if event_key in self.event_time_entries: # Check if entry exists
                self.event_time_entries[event_key].configure(bootstyle="default")
            self.data_manager.save_data()
            self.update_calculated_totals()

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
                return True
                
            # Try to parse the time
            datetime.strptime(time_str, '%H:%M:%S')
            
            # If successful, update the entry style and save
            if var_name in self.time_entries:
                self.time_entries[var_name].configure(bootstyle="success")
            self.event_times[var_name] = time_str
            self.save_data(False)
            return True
            
        except ValueError:
            # Invalid time format
            messagebox.showerror(
                "Error", 
                "Formato de tiempo inválido. Use HH:MM:SS"
            )
            # Reset to previous valid value or clear
            if var_name in self.event_times:
                self.variables[var_name].set(self.event_times.get(var_name, ''))
            else:
                self.variables[var_name].set('')
            return False

    def record_time(self, var_name):
        """Record the time for a specific event."""
        current_time_str = datetime.now().strftime('%H:%M:%S')
        # This method seems to interact with self.variables and self.time_entries,
        # which might be from an older structure or a different part of the UI.
        # The main event times now use self.event_times, self.event_time_vars, self.event_time_entries.
        # Let's assume this method is for a different context or needs to be updated/removed
        # if it's meant for the main event times.
        # For now, I'll comment out the parts that directly conflict with the new structure.

        # self.event_times[var_name] = current_time_str # Conflicts if var_name is not an event_key
        # if var_name in self.event_time_vars: # var_name might not be in event_time_vars
        #     self.event_time_vars[var_name].set(current_time_str)
        #     # Update label style to indicate recorded - this was for Labels, now Entries
        #     # label_widget = self.event_time_vars.get(f"{var_name}_label")
        #     entry_widget = self.event_time_entries.get(var_name)
        #     if entry_widget:
        #         entry_widget.configure(bootstyle="success")
        
        # Fallback to original self.variables if this is for a different section
        if var_name in self.variables:
             self.variables[var_name].set(current_time_str)
             if var_name in self.time_entries: # Assuming self.time_entries maps to these
                 self.time_entries[var_name].configure(bootstyle="success")
        
        self.data_manager.save_data() # This is general, might be okay
        self.update_calculated_totals() # This is general, might be okay

    def clear_field(self, var_name):
        """Clear the time for a specific event."""
        # Similar to record_time, this might be for a different context.
        # if var_name in self.event_times: # var_name might not be an event_key
        #     self.event_times[var_name] = None
        #     if var_name in self.event_time_vars:
        #         self.event_time_vars[var_name].set('--:--:--')
        #     entry_widget = self.event_time_entries.get(var_name)
        #     if entry_widget:
        #         entry_widget.configure(bootstyle="default")
        
        # Fallback to original self.variables
        if var_name in self.variables:
            self.variables[var_name].set('') # Or '--:--:--' if appropriate for these fields
            if var_name in self.time_entries:
                self.time_entries[var_name].configure(bootstyle="default")

        self.data_manager.save_data()
        self.update_calculated_totals()

    def clear_form(self, confirm=True):
        """Clear all fields in this tab. Only show confirmation if confirm=True."""
        if confirm:
            if not messagebox.askyesno(
                "Confirmar",
                "¿Está seguro de limpiar los campos de tiempos de vuelo?\n\nEsta acción borrará los datos en esta pestaña."
            ):
                return
        # Clear all entry fields for time events
        for entry in self.time_entries.values():
            if hasattr(entry, 'delete'):
                entry.delete(0, 'end')
            elif hasattr(entry, 'set'):
                entry.set('')
        # Clear student hypoxia times
        for entry in self.student_hypoxia_entries.values():
            if hasattr(entry, 'delete'):
                entry.delete(0, 'end')
            elif hasattr(entry, 'set'):
                entry.set('')
        self.update_idletasks()

    def schedule_warning_popup(self, delay_seconds, label=None):
        """Schedule a warning popup after a delay in seconds. Returns the timer id for cancellation."""
        return self.after(delay_seconds * 1000, self.show_warning_popup)

    def show_warning_popup(self):
        """Show the 'Comunicar tiempo a lector.' warning popup."""
        messagebox.showwarning(
            "Aviso",
            "Comunicar tiempo a lector.",
            parent=self
        )
