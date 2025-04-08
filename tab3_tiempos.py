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
        ]
        self.event_keys = [key for key, _ in self.time_event_definitions]

        # Tk Variables Storage
        self.event_time_vars: Dict[str, tk.StringVar] = {}
        self.student_hypoxia_time_vars: Dict[str, tk.StringVar] = {}
        self.calculated_total_time_vars: Dict[str, tk.StringVar] = {}

        # Internal data storage
        self.event_times: Dict[str, Optional[str]] = {}
        
        # New: Store individual student hypoxia end times
        self.student_hypoxia_end_times: Dict[str, Optional[str]] = {}
        
        # Flag to track if student hypoxia time has been calculated
        self.student_hypoxia_calculated: Dict[str, bool] = {}
        
        # Timer for auto-updating
        self.auto_update_timer = None
        
        self.initialize_data()
        self.create_widgets()
        self.load_data()
        
        # Setup destroy handler
        self.bind("<Destroy>", self.on_destroy)
    
    def create_variables(self):
        """Create variables for form fields."""
        # Time data
        self.variables['fecha'] = tk.StringVar()
        self.variables['hora_inicio'] = tk.StringVar()
        self.variables['hora_fin'] = tk.StringVar()
        self.variables['tipo_tiempo'] = tk.StringVar()
        self.variables['descripcion'] = tk.StringVar()
        self.variables['observaciones'] = tk.StringVar()
        
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
        # Create scrollable frame for event times
        event_content_frame = ttkb.Frame(parent)
        event_content_frame.pack(fill=tk.BOTH, expand=True)
        event_content_frame.columnconfigure(0, weight=1)
        event_content_frame.rowconfigure(0, weight=1)
        
        # Create canvas with scrollbars
        self.events_canvas = tk.Canvas(event_content_frame)
        y_scrollbar = ttkb.Scrollbar(event_content_frame, orient="vertical", command=self.events_canvas.yview)
        
        # Configure canvas scrolling
        self.events_canvas.configure(yscrollcommand=y_scrollbar.set)
        
        # Grid layout
        self.events_canvas.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Create frame inside canvas
        events_container = ttkb.Frame(self.events_canvas)
        self.events_window = self.events_canvas.create_window((0, 0), window=events_container, anchor="nw")
        
        # Configure columns in the container
        events_container.columnconfigure(0, weight=2)  # Event label column
        events_container.columnconfigure(1, weight=0)  # Button column
        events_container.columnconfigure(2, weight=1)  # Time label column
        
        # Make the container expand to fill canvas width
        def on_events_canvas_configure(event):
            self.events_canvas.itemconfig(self.events_window, width=event.width)
        
        self.events_canvas.bind("<Configure>", on_events_canvas_configure)
        
        # Update scroll region when container size changes
        def on_events_frame_configure(event):
            self.events_canvas.configure(scrollregion=self.events_canvas.bbox("all"))
        
        events_container.bind("<Configure>", on_events_frame_configure)
        
        # Add mousewheel scrolling
        def _on_events_mousewheel(event):
            # Handle different platform scroll events
            if event.delta:
                # Windows
                self.events_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # Linux, macOS
                if event.num == 4:
                    self.events_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.events_canvas.yview_scroll(1, "units")
        
        # Bind mousewheel events
        self.events_canvas.bind("<MouseWheel>", _on_events_mousewheel)  # Windows
        self.events_canvas.bind("<Button-4>", _on_events_mousewheel)    # Linux up
        self.events_canvas.bind("<Button-5>", _on_events_mousewheel)    # Linux down
        
        # Store bindings for cleanup
        self.events_bindings = [
            (self.events_canvas, "<Configure>", on_events_canvas_configure),
            (events_container, "<Configure>", on_events_frame_configure),
            (self.events_canvas, "<MouseWheel>", _on_events_mousewheel),
            (self.events_canvas, "<Button-4>", _on_events_mousewheel),
            (self.events_canvas, "<Button-5>", _on_events_mousewheel)
        ]

        # Add event time entries
        for i, (key, label_text) in enumerate(self.time_event_definitions):
            # Label for the event
            label = ttkb.Label(events_container, text=label_text, anchor='w')
            label.grid(row=i, column=0, padx=5, pady=3, sticky='w')

            # Button to record time
            record_btn = ttkb.Button(
                events_container,
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
                events_container,
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
        self.save_data(show_confirmation=False) # Save without confirmation popup
        self.update_calculated_totals() # Update totals whenever an event time changes

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
            time_label = ttkb.Label(
                parent,
                textvariable=time_var,
                font=('Consolas', 10),
                anchor='w'
            )
            time_label.grid(row=row_idx, column=2, padx=5, pady=3, sticky='w')
            
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
                "No se ha registrado el tiempo de 'Inicio Ejercicio de hipoxia'.",
                parent=self
            )
            return
        
        # If the student already has a calculated time, show it
        if self.student_hypoxia_calculated.get(student_id, False):
            # Just display the previously calculated time
            if student_id in self.student_hypoxia_time_vars and student_id in self.student_hypoxia_end_times:
                return
                
        try:
            # Get the current time as the end time for this student
            current_time = datetime.now()
            current_time_str = current_time.strftime('%H:%M:%S')
            
            # Store this as the student's hypoxia end time
            self.student_hypoxia_end_times[student_id] = current_time_str
            
            # Mark this student's hypoxia time as calculated
            self.student_hypoxia_calculated[student_id] = True
            
            # Parse start time
            start_time = datetime.strptime(start_hypoxia_time_str, '%H:%M:%S')
            
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
            
            # Update display
            if student_id in self.student_hypoxia_time_vars:
                self.student_hypoxia_time_vars[student_id].set(elapsed_str)
                
            # Save the data
            self.save_data(show_confirmation=False)
                
        except ValueError as e:
            print(f"Error parsing inicio_hipoxia time: {start_hypoxia_time_str}, {e}")
        except Exception as e:
            print(f"Error calculating student hypoxia time: {e}")
    
    def reset_student_hypoxia_time(self, student_id: str):
        """Reset a student's hypoxia time calculation."""
        if student_id in self.student_hypoxia_end_times:
            del self.student_hypoxia_end_times[student_id]
        
        self.student_hypoxia_calculated[student_id] = False
        
        if student_id in self.student_hypoxia_time_vars:
            self.student_hypoxia_time_vars[student_id].set("00:00:00")
        
        self.save_data(show_confirmation=False)

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
            label.grid(row=i, column=0, padx=5, pady=5, sticky='w')
            
            # Time Display Label
            time_var = tk.StringVar(value="00:00:00")
            self.calculated_total_time_vars[key] = time_var
            
            time_label = ttkb.Label(
                parent,
                textvariable=time_var,
                font=('Consolas', 12, 'bold'),
                anchor='w',
                bootstyle="info" # Make it stand out
            )
            time_label.grid(row=i, column=1, padx=5, pady=5, sticky='w')
        
        # Add update button
        update_btn = ttkb.Button(
            parent,
            text="Actualizar Totales",
            command=self.update_calculated_totals,
            bootstyle="info",
            width=15
        )
        update_btn.grid(row=len(total_definitions), column=0, columnspan=2, pady=10, sticky='e')
    
    def update_calculated_totals(self):
        """Calculate and update the total times based on event times."""
        # Total Flight Time: desde inicio_ascenso hasta finalizacion_perfil
        start_vuelo = self.event_times.get('inicio_ascenso')
        end_vuelo = self.event_times.get('finalizacion_perfil')
        if start_vuelo and end_vuelo:
            try:
                start_time = datetime.strptime(start_vuelo, '%H:%M:%S')
                end_time = datetime.strptime(end_vuelo, '%H:%M:%S')
                
                # Convert to today's date for proper timedelta calculation
                now = datetime.now()
                start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
                end_datetime = now.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)
                
                # Handle overnight flights (if end is earlier than start)
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
                if 'total_vuelo' in self.calculated_total_time_vars:
                    self.calculated_total_time_vars['total_vuelo'].set(time_str)
            except Exception as e:
                print(f"Error calculating total flight time: {e}")
        
        # Total Hipoxia Time: desde inicio_hipoxia hasta fin_hipoxia
        self.calculate_time_range('inicio_hipoxia', 'fin_hipoxia', 'total_hipoxia')
        
        # Total Vision Nocturna Time: desde inicio_vision_nocturna hasta fin_vision_nocturna
        self.calculate_time_range('inicio_vision_nocturna', 'fin_vision_nocturna', 'total_vision')
    
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
            except Exception as e:
                print(f"Error calculating time range for {start_key} to {end_key}: {e}")
    
    def load_data(self):
        """Load saved event times and update UI."""
        # Load event times from data_manager
        event_times = self.data_manager.current_data.get('event_times', {})
        
        # Update UI with loaded times
        for key in self.event_keys:
            if key in event_times and event_times[key]:
                self.event_times[key] = event_times[key]
                if key in self.event_time_vars:
                    self.event_time_vars[key].set(event_times[key])
                    # Update label style
                    label_widget = self.event_time_vars.get(f"{key}_label")
                    if label_widget:
                        label_widget.configure(bootstyle="success")
        
        # Load student hypoxia end times
        self.student_hypoxia_end_times = self.data_manager.current_data.get('student_hypoxia_end_times', {})
        
        # Update student hypoxia time displays
        start_hypoxia_time_str = self.event_times.get('inicio_hipoxia')
        if start_hypoxia_time_str:
            for student_id, end_time_str in self.student_hypoxia_end_times.items():
                if student_id in self.student_hypoxia_time_vars:
                    try:
                        # Mark as calculated
                        self.student_hypoxia_calculated[student_id] = True
                        
                        # Calculate and display the time difference
                        start_time = datetime.strptime(start_hypoxia_time_str, '%H:%M:%S')
                        end_time = datetime.strptime(end_time_str, '%H:%M:%S')
                        
                        # Convert to today for calculation
                        now = datetime.now()
                        start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, 
                                                  second=start_time.second, microsecond=0)
                        end_datetime = now.replace(hour=end_time.hour, minute=end_time.minute, 
                                                second=end_time.second, microsecond=0)
                        
                        # Handle overnight case
                        if end_datetime < start_datetime:
                            end_datetime += timedelta(days=1)
                            
                        # Calculate difference
                        elapsed_delta = end_datetime - start_datetime
                        elapsed_seconds = int(elapsed_delta.total_seconds())
                        
                        # Format time
                        hours, remainder = divmod(elapsed_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        elapsed_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                        
                        # Update display
                        self.student_hypoxia_time_vars[student_id].set(elapsed_str)
                    except Exception as e:
                        print(f"Error loading student {student_id} hypoxia time: {e}")
        
        # Update calculated totals
        self.update_calculated_totals()
    
    def save_data(self, show_confirmation=True):
        """Save event times to data_manager."""
        # Save event times
        self.data_manager.current_data['event_times'] = self.event_times
        
        # Save student hypoxia end times
        self.data_manager.current_data['student_hypoxia_end_times'] = self.student_hypoxia_end_times
        
        # Get session number from data manager
        session_id = self.data_manager.current_data.get('vuelo', {}).get('numero_entrenamiento', '')
        # If session ID exists, also save to the session data
        if session_id:
            # Make sure sessions_data exists in current_data
            if 'sessions_data' not in self.data_manager.current_data:
                self.data_manager.current_data['sessions_data'] = {}
                
            # Make sure this session exists in sessions_data
            if session_id not in self.data_manager.current_data['sessions_data']:
                self.data_manager.current_data['sessions_data'][session_id] = {}
                
            # Save to the session data
            session_data = self.data_manager.current_data['sessions_data'][session_id]
            session_data['event_times'] = self.event_times
            session_data['student_hypoxia_end_times'] = self.student_hypoxia_end_times
        
        self.data_manager.save_data()
        
        # Refresh other tabs if needed
        if self.main_app and hasattr(self.main_app, 'refresh_all_tabs'):
            self.main_app.refresh_all_tabs()
        
        # Show success message only if requested
        if show_confirmation:
            messagebox.showinfo(
                "Guardado",
                "Datos de tiempos guardados exitosamente"
            )
    
    def clear_form(self):
        """Clear all time event data after confirmation."""
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de que desea limpiar todos los datos de tiempos?",
            icon="warning"
        )
        
        if not confirm:
            return
            
        # Clear event times
        for key in self.event_keys:
            self.event_times[key] = None
            if key in self.event_time_vars:
                self.event_time_vars[key].set("--:--:--")
                # Reset label style
                label_widget = self.event_time_vars.get(f"{key}_label")
                if label_widget:
                    label_widget.configure(bootstyle="secondary")
        
        # Clear student hypoxia times and end times
        self.student_hypoxia_end_times = {}
        self.student_hypoxia_calculated = {str(i): False for i in range(1, self.num_students + 1)}
        
        for var in self.student_hypoxia_time_vars.values():
            var.set("00:00:00")
            
        # Clear calculated totals display
        for var in self.calculated_total_time_vars.values():
            var.set("00:00:00")

        self.save_data(show_confirmation=True) # Save the cleared state
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
        messagebox.showinfo(
            "Pantalla Limpiada",
            "Pantalla limpiada con éxito. Los datos almacenados permanecen intactos.",
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
        
        # Update student hypoxia times only for students without calculated times
        # and only if hypoxia exercise has started
        start_hypoxia = self.event_times.get('inicio_hipoxia')
        
        if start_hypoxia:
            # Only display running time for students that haven't been calculated yet
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
