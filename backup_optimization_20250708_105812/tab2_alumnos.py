#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox, filedialog
from typing import Dict, Any, List
from ttkbootstrap.scrolled import ScrolledFrame
import pandas as pd
import os
import datetime
import re

class AlumnosTab(ttkb.Frame):
    """Tab for student and OI data, aligned with camara.mdc rules."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        self.main_app = main_app
        self.prevent_load_overwrite = False
        
        # Date variable for filtering imports and display
        self.training_date_var = tk.StringVar()
        self._init_training_date()
        
        # Constants from rules
        self.max_students = 8
        self.max_oi = 2
        self.participant_keys = [str(i) for i in range(1, self.max_students + 1)] + \
                                [f"OI{i}" for i in range(1, self.max_oi + 1)]
        self.gender_options = ["M", "F", "-"] # Added default/unknown
        
        # Create chair options
        self.student_chair_options = [str(i) for i in range(1, self.max_students + 1)]
        self.oi_chair_options = [f"OI{i}" for i in range(1, self.max_oi + 1)]

        # Data structure to hold tk variables for all entries
        self.participant_vars: Dict[str, Dict[str, tk.StringVar]] = {}
        self.chair_vars: Dict[str, tk.StringVar] = {}  # Dict for chair variables
        self.training_completed_vars: Dict[str, tk.BooleanVar] = {}  # Dict for training completion checkboxes
        
        # Define headers and corresponding variable keys (must match rules)
        self.headers = ["Silla", "Grado", "Apellido y Nombre", "Edad", "Genero", 
                        "Unidad", "Email", "Máscara", "Casco"]
        self.var_keys = ["grado", "apellido_nombre", "edad", "genero", 
                         "unidad", "email", "mask", "helmet"]
        # Define precise widths for columns to match entry fields
        self.col_widths = [6, 12, 30, 6, 8, 15, 25, 8, 8]  # Adjusted widths

        # Create the layout
        self.create_widgets()
        self.load_data() # Load data after widgets are created
    
    def _on_data_changed(self, *args):
        """Callback when any traced StringVar in this tab is written to."""
        if not self.prevent_load_overwrite:
            print(f"AlumnosTab: Data changed, setting prevent_load_overwrite = True")
            self.prevent_load_overwrite = True

    def _init_training_date(self):
        """Initialize the training date field from tab1_vuelo.py if available, else blank."""
        # Try to get the date from data_manager (tab1_vuelo.py)
        vuelo_data = self.data_manager.current_data.get('vuelo', {})
        date_str = vuelo_data.get('fecha', '')
        if date_str:
            self.training_date_var.set(date_str)
        else:
            self.training_date_var.set('')

    def create_widgets(self):
        """Create the main tab layout with scrollable frame."""
        # --- Date Row at the top ---
        date_frame = ttkb.Frame(self)
        date_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        date_label = ttkb.Label(date_frame, text="Fecha del entrenamiento:", font=('Segoe UI', 10, 'bold'))
        date_label.pack(side=tk.LEFT, padx=(0, 5))
        date_entry = ttkb.Entry(date_frame, textvariable=self.training_date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=(0, 5))
        format_label = ttkb.Label(date_frame, text="(DD-MM-AAAA)", font=('Segoe UI', 9), bootstyle="secondary")
        format_label.pack(side=tk.LEFT, padx=(0, 5))
        set_date_btn = ttkb.Button(date_frame, text="Hoy", command=self.set_current_date, bootstyle="info-outline", width=6)
        set_date_btn.pack(side=tk.LEFT, padx=5)
        
        # Create scrollable content
        # Use autohide=False if scrollbar visibility is preferred
        scrolled_frame = ScrolledFrame(self, autohide=True)
        scrolled_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # This is the frame inside the ScrolledFrame where widgets go
        container = scrolled_frame.container 
        
        # --- Students Section --- 
        student_frame = ttkb.LabelFrame(
            container,
            text="Datos de Alumnos",
            padding=10,
            bootstyle="primary"
        )
        student_frame.pack(fill=tk.X, expand=True, pady=5, padx=5)
        self._create_participant_table(student_frame, 
                                       participant_ids=[str(i) for i in range(1, self.max_students + 1)],
                                       is_oi_section=False)

        # --- OI Section --- (Updated title to "Observadores Internos")
        oi_frame = ttkb.LabelFrame(
            container,
            text="Datos de Observadores Internos",
            padding=10,
            bootstyle="info"
        )
        oi_frame.pack(fill=tk.X, expand=True, pady=5, padx=5)
        self._create_participant_table(oi_frame, 
                                       participant_ids=[f"OI{i}" for i in range(1, self.max_oi + 1)],
                                       is_oi_section=True)
        
        # Action buttons (Packed outside the scrollable frame)
        button_frame = ttkb.Frame(self)
        button_frame.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        
        save_btn = ttkb.Button(
            button_frame,
            text="Guardar Datos",
            command=self.save_data,
            bootstyle="success", # Use success style
            width=18
        )
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        clear_btn = ttkb.Button(
            button_frame,
            text="Limpiar Datos",
            command=self.clear_form,
            bootstyle="warning", # Use warning style
            width=18
        )
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        import_btn = ttkb.Button(
            button_frame,
            text="Importar Alumnos",
            command=self.import_from_excel,
            bootstyle="info",
            width=18
        )
        import_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # New button for importing Observadores Internos
        import_oi_btn = ttkb.Button(
            button_frame,
            text="Importar OIs",
            command=self.import_observadores_internos,
            bootstyle="info",
            width=18
        )
        import_oi_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def _create_participant_table(self, parent_frame, participant_ids: List[str], is_oi_section: bool):
        """Creates the header and rows for a list of participants (students or OIs)."""
        header_bootstyle = "primary" if not is_oi_section else "info"

        # Create header row using self.headers and self.col_widths
        for col, (header, width) in enumerate(zip(self.headers, self.col_widths)):
            header_label = ttkb.Label(
                parent_frame,
                text=header,
                font=('Segoe UI', 10, 'bold'),
                bootstyle=header_bootstyle,
                width=width,
                anchor='center'  # Center align headers
            )
            header_label.grid(row=0, column=col, padx=5, pady=(5, 2), sticky='ew')
        
        # Add header for clear button column
        clear_header = ttkb.Label(
            parent_frame,
            text="Limpiar",
            font=('Segoe UI', 10, 'bold'),
            bootstyle=header_bootstyle,
            width=6,
            anchor='center'  # Center align header
        )
        clear_header.grid(row=0, column=len(self.headers), padx=5, pady=(5, 2), sticky='ew')
        
        # Add header for training completed column
        completed_header = ttkb.Label(
            parent_frame,
            text="Termina\nentrenamiento",
            font=('Segoe UI', 10, 'bold'),
            bootstyle=header_bootstyle,
            width=12,
            anchor='center',  # Center align header
            justify='center'
        )
        completed_header.grid(row=0, column=len(self.headers) + 1, padx=5, pady=(5, 2), sticky='ew')
        
        # Configure column weights to maintain alignment
        for i in range(len(self.headers) + 2):  # +2 for clear button and completed checkbox
            parent_frame.grid_columnconfigure(i, weight=1)
        
        # Add separator below header
        separator = ttkb.Separator(parent_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=len(self.headers) + 2, sticky="ew", pady=(0, 5))

        # Create rows for each participant
        for i, participant_id in enumerate(participant_ids):
            current_row = i + 2  # Offset for header and separator
            self._create_person_row(parent_frame, current_row, participant_id, is_oi_section)

    def _create_person_row(self, parent_frame, row, participant_id: str, is_oi_section: bool):
        """Creates the widgets for a single participant row."""
        self.participant_vars[participant_id] = {}
        
        # Create a frame for this row to hold all widgets
        row_frame = ttkb.Frame(parent_frame)
        row_frame.grid(row=row, column=0, columnspan=len(self.headers) + 2, sticky='ew')
        
        # Configure column weights in row_frame to match parent
        for i in range(len(self.headers) + 2):
            row_frame.grid_columnconfigure(i, weight=1)
        
        # Create chair selection dropdown
        chair_var = tk.StringVar()
        self.chair_vars[participant_id] = chair_var
        
        # Set available options based on section
        chair_options = self.oi_chair_options if is_oi_section else self.student_chair_options
        
        chair_dropdown = ttkb.Combobox(
            row_frame,
            textvariable=chair_var,
            values=chair_options,
            width=self.col_widths[0] - 2,  # Adjusted width
            state="readonly"
        )
        chair_dropdown.grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        
        # Set default value
        chair_var.set(participant_id)
        
        # Bind the chair selection change event
        chair_var.trace_add("write", lambda name, index, mode, pid=participant_id: self.on_chair_var_changed(pid))

        # Create widgets for other columns based on self.var_keys
        for col_idx, key in enumerate(self.var_keys):
            actual_col = col_idx + 1  # Offset by 1 because Silla is col 0
            width = self.col_widths[actual_col]
            var = tk.StringVar()
            self.participant_vars[participant_id][key] = var

            if key == "genero":
                widget = ttkb.Combobox(
                    row_frame,
                    textvariable=var,
                    values=self.gender_options,
                    width=width - 2,  # Adjusted for combobox
                    state="readonly"
                )
                var.set(self.gender_options[-1])
            else:
                widget = ttkb.Entry(
                    row_frame,
                    textvariable=var,
                    width=width
                )
            
            widget.grid(row=0, column=actual_col, padx=5, pady=2, sticky='ew')
            var.trace_add("write", self._on_data_changed) # Add trace here
        
        # Add clear button for this row
        clear_btn = ttkb.Button(
            row_frame,
            text="✕",
            command=lambda pid=participant_id: self.clear_single_record(pid),
            bootstyle="danger-outline",
            width=3
        )
        clear_btn.grid(row=0, column=len(self.headers), padx=5, pady=2, sticky='ew')
        
        # Add training completed checkbox
        completed_var = tk.BooleanVar(value=False)
        self.training_completed_vars[participant_id] = completed_var
        
        # Create a frame to center the checkbox
        checkbox_frame = ttkb.Frame(row_frame)
        checkbox_frame.grid(row=0, column=len(self.headers) + 1, padx=5, pady=2, sticky='ew')
        
        completed_checkbox = ttkb.Checkbutton(
            checkbox_frame,
            variable=completed_var,
            bootstyle="success-round-toggle"
        )
        completed_checkbox.pack(anchor='center')
        completed_var.trace_add("write", self._on_data_changed)  # Add trace to track changes

    def clear_single_record(self, participant_id: str):
        """Clear a single participant record."""
        try:
            # Reset all fields for this participant
            for field_key, var in self.participant_vars[participant_id].items():
                if field_key == 'genero':
                    var.set(self.gender_options[-1])
                else:
                    var.set('')
            
            # Reset chair to original position
            self.chair_vars[participant_id].set(participant_id)
            
            # Reset training completed checkbox
            if participant_id in self.training_completed_vars:
                self.training_completed_vars[participant_id].set(False)
            
            # Sort after clearing
            is_oi = participant_id.startswith("OI")
            self.sort_participants(is_oi)
            self._on_data_changed() # Mark as changed after clearing a row
            
        except Exception as e:
            print(f"Error clearing record for {participant_id}: {e}")

    def on_chair_var_changed(self, participant_id, *args):
        """Handle chair variable change. This combines on_chair_changed and marks data as dirty."""
        # Original on_chair_changed logic:
        new_chair = self.chair_vars[participant_id].get()
        # Check if the new chair is already assigned to another participant
        for other_id, other_chair_var in self.chair_vars.items():
            if other_id != participant_id and other_chair_var.get() == new_chair:
                # If new_chair is taken, find the original chair of participant_id
                original_chair_of_participant_id = participant_id # Assuming chair var was set to its own ID initially or last known good chair
                
                # Find who currently occupies participant_id's original chair spot
                # This logic is complex if chairs are freely assignable and not just simple swaps.
                # For now, let's assume we might need to clear the other participant's chair if it's a direct conflict.
                # A more robust solution would involve finding an empty chair or handling complex swaps.
                
                # Simplistic approach: if new_chair is taken by other_id, clear other_id's chair_var or swap
                # For now, just clear the conflicting one. A better UX might be to prevent this or auto-swap.
                # Let's find what chair other_id *was* in before it took new_chair (if that's what happened)
                # This can get complicated quickly. Let's stick to a simple deconfliction:
                # If 'other_id' is now in 'new_chair', and 'participant_id' wants 'new_chair',
                # we need to decide what happens to 'other_id'.
                # A simple approach: if participant_id takes a chair, and that chair was occupied,
                # the previous occupant of that chair must be moved or their chair cleared.
                # This current logic below just clears the other person's chair if they had the new_chair.
                # This is not a full swap, it just frees up the new_chair.
                other_chair_var.set("") # Clear the chair of the other participant who had new_chair
                # Potentially, we'd want to set other_chair_var to the old chair of participant_id
                # but that old chair value isn't readily available here without more state.

        # Auto-sort after chair change
        is_oi = participant_id.startswith("OI")
        self.sort_participants(is_oi)
        self._on_data_changed() # Mark data as changed

    def sort_participants(self, is_oi_section: bool):
        """Sort participants based on their chair numbers."""
        try:
            # Get relevant participant IDs and frame
            if is_oi_section:
                participant_range = self.oi_chair_options
            else:
                participant_range = self.student_chair_options

            # Create a mapping of current chair assignments to participant data
            chair_mapping = {}
            for participant_id in participant_range:
                # Find who is currently in this chair
                for pid, chair_var in self.chair_vars.items():
                    if chair_var.get() == participant_id:
                        # Store all data for this participant
                        participant_data = {
                            'id': pid,
                            'data': {field_key: var.get() for field_key, var in self.participant_vars[pid].items()}
                        }
                        chair_mapping[participant_id] = participant_data
                        break

            # Sort the chairs
            sorted_chairs = sorted(participant_range)
            
            # Reorder the data in memory
            for chair_id in sorted_chairs:
                if chair_id in chair_mapping:
                    source_data = chair_mapping[chair_id]
                    source_id = source_data['id']
                    
                    # Update the display order by updating the variables
                    for field_key, value in source_data['data'].items():
                        self.participant_vars[source_id][field_key].set(value)
            
            print(f"{'OIs' if is_oi_section else 'Students'} sorted successfully")
            
        except Exception as e:
            print(f"Error sorting participants: {e}")
        self.update_idletasks()
    
    def load_data(self):
        print(f"[DEBUG] tab2_alumnos: load_data called, prevent_load_overwrite={self.prevent_load_overwrite}")
        if getattr(self, 'prevent_load_overwrite', False):
            return
        all_data = self.data_manager.current_data.get('participantes', {}) 
        for participant_id, person_data in all_data.items():
            if participant_id in self.participant_vars: 
                for field_key in self.participant_vars[participant_id]:
                    value = person_data.get(field_key, None)
                    if value is not None:
                        self.participant_vars[participant_id][field_key].set(value)
                    else:
                        # Only set default if missing in loaded data
                        if field_key == 'genero':
                            self.participant_vars[participant_id][field_key].set(self.gender_options[-1])
                        else:
                            self.participant_vars[participant_id][field_key].set('')
                # Load training completed status
                training_completed = person_data.get('training_completed', False)
                if participant_id in self.training_completed_vars:
                    self.training_completed_vars[participant_id].set(training_completed)
                
                # Debug print for gender, mask, helmet
                g = person_data.get('genero', None)
                m = person_data.get('mask', None)
                h = person_data.get('helmet', None)
                print(f"[DEBUG] load_data: {participant_id} genero={g}, mask={m}, helmet={h}")
            else:
                print(f"Warning: Participant ID '{participant_id}' from loaded data not found in UI.")

    def _update_datamanager_with_own_data(self):
        """Helper method to update DataManager with this tab's data."""
        all_data = {}
        for participant_id, fields_dict in self.participant_vars.items():
            person_data = {}
            current_chair = self.chair_vars[participant_id].get()
            person_data['silla'] = current_chair
            for field_key, var in fields_dict.items():
                value = var.get().strip()
                person_data[field_key] = value
            # Add training completed status
            if participant_id in self.training_completed_vars:
                person_data['training_completed'] = self.training_completed_vars[participant_id].get()
            all_data[participant_id] = person_data

        session_id = self.data_manager.current_data.get('vuelo', {}).get('numero_entrenamiento', '')
        training_date_str = self.data_manager.current_data.get('vuelo', {}).get('fecha', '')

        if session_id and training_date_str: 
            training_key = f"{training_date_str}_{session_id}"
            if 'training_sessions' not in self.data_manager.current_data:
                self.data_manager.current_data['training_sessions'] = {}
            if training_key not in self.data_manager.current_data['training_sessions']:
                self.data_manager.current_data['training_sessions'][training_key] = {
                    'fecha': training_date_str,
                    'numero_entrenamiento': session_id,
                    'timestamp': datetime.datetime.now().isoformat() # Ensure datetime is imported
                }
            self.data_manager.current_data['training_sessions'][training_key]['participantes'] = all_data
        
        self.data_manager.current_data['participantes'] = all_data
        print(f"Tab2: Updated participantes data in DataManager for session {session_id}")

    def save_data(self, triggered_by_user=True):
        print(f"Tab2 save_data called, triggered_by_user={triggered_by_user}")
        self._update_datamanager_with_own_data()
        
        if triggered_by_user:
            if self.main_app:
                tabs_to_call = {
                    'tab1': getattr(self.main_app, 'tab1', None),
                    'tab3': getattr(self.main_app, 'tab3', None),
                    'tab4': getattr(self.main_app, 'tab4', None),
                    'tab6': getattr(self.main_app, 'tab6', None)
                }
                for tab_name, tab_instance in tabs_to_call.items():
                    if tab_instance and hasattr(tab_instance, 'save_data'):
                        print(f"Tab2 orchestrator: Calling save_data on {tab_name}")
                        tab_instance.save_data(triggered_by_user=False)
            
            self.data_manager.save_data()
            messagebox.showinfo("Guardado", "Todos los datos han sido guardados exitosamente.", parent=self)
            self.prevent_load_overwrite = False
        else:
            self.prevent_load_overwrite = False
    
    def clear_form(self, confirm=True):
        """Clear all fields in this tab. Only show confirmation if confirm=True."""
        if confirm:
            if not messagebox.askyesno(
                "Confirmar",
                "¿Está seguro de limpiar los campos de alumnos?\n\nEsta acción borrará los datos en esta pestaña."
            ):
                return
        # Clear all participant entry fields (students and OI)
        for participant_id, fields_dict in self.participant_vars.items():
            for field_key, var in fields_dict.items():
                if field_key == 'genero':
                    var.set(self.gender_options[-1])  # Reset combobox to default '-'
                else:
                    var.set('')
            # Reset chair to original position
            if participant_id in self.chair_vars:
                self.chair_vars[participant_id].set(participant_id)
            # Reset training completed checkbox
            if participant_id in self.training_completed_vars:
                self.training_completed_vars[participant_id].set(False)
        self.update_idletasks()
    
    def import_from_excel(self):
        """Open file dialog to import student data from Excel."""
        # Open file dialog to select Excel file
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            parent=self
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Load Excel file with pandas
            students_data = self.load_students_from_excel(file_path)
            if not students_data:
                messagebox.showinfo("Importación", "No se encontraron datos de estudiantes en el archivo.", parent=self)
                return
            
            # Show selection dialog
            self.show_student_selection_dialog(students_data)
            
            # Save data after import
            # self.save_data() # Save is too aggressive here, let user save explicitly or rely on autosave
            self._on_data_changed() # Mark as changed after import
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar desde Excel: {str(e)}", parent=self)
            # Save data after import
            # self.save_data()
            self._on_data_changed() # Mark as changed after import

    def import_observadores_internos(self):
        """Open file dialog to import Observadores Internos data from Excel."""
        # Open file dialog to select Excel file
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            parent=self
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Get training date from VueloTab
            training_date = self.get_training_date()
            if not training_date:
                messagebox.showinfo("Importación", 
                                  "No se pudo determinar la fecha de entrenamiento. Por favor, configure la fecha en la pestaña Datos Generales.", 
                                  parent=self)
                return
            
            # Load Excel file with pandas - specific for Observadores Internos
            observadores_data = self.load_observadores_from_excel(file_path, training_date)
            if not observadores_data:
                messagebox.showinfo("Importación", 
                                  "No se encontraron Observadores Internos disponibles en el archivo para la fecha del entrenamiento.", 
                                  parent=self)
                return
            
            # Show selection dialog
            self.show_observadores_selection_dialog(observadores_data)
            
            # Save data after import
            # self.save_data()
            self._on_data_changed() # Mark as changed after import
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar Observadores Internos: {str(e)}", parent=self)
            # Save data after import
            # self.save_data()
            self._on_data_changed() # Mark as changed after import
    
    def get_training_date(self):
        """Get the training date from the date field at the top of the tab."""
        date_str = self.training_date_var.get().strip()
        if not date_str:
            # Fallback to Vuelo tab
            vuelo_data = self.data_manager.current_data.get('vuelo', {})
            date_str = vuelo_data.get('fecha', '')
        if not date_str:
            return None
        # Try to parse the date (handle different formats)
        try:
            date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
            return date
        except ValueError:
            try:
                date = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
                return date
            except ValueError:
                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    return date
                except ValueError:
                    return None

    def load_students_from_excel(self, file_path):
        """Load student data from Excel file using pandas, filter by date +/- 5 days if possible."""
        try:
            df = pd.read_excel(file_path)
            
            # Map Excel columns to app field names based on the actual structure
            # of 'EVALUACIÓN MEDICA PRE VUELO DE LA CAMARA DE ALTURA.xlsx'
            field_mapping = {
                # Remove GRADO mapping as we'll handle it separately
                "APELLIDOS Y NOMBRES": "apellido_nombre",
                "EDAD": "edad", 
                "UNIDAD OPERATIVA": "unidad",
                "CORREO INSTITUCIONAL": "email",
                "CELULAR": "telefono"  # Extra field that might be useful
            }
            
            # Try to filter by date +/- 5 days if a date is set and a date column exists
            training_date = self.get_training_date()
            date_column = None
            for col in df.columns:
                if 'fecha' in col.lower():
                    date_column = col
                    break
            if training_date and date_column:
                def parse_excel_date(val):
                    if isinstance(val, datetime.datetime):
                        return val.date()
                    if isinstance(val, str):
                        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
                            try:
                                return datetime.datetime.strptime(val, fmt).date()
                            except Exception:
                                continue
                    return None
                df['__parsed_date'] = df[date_column].apply(parse_excel_date)
                df = df[df['__parsed_date'].notnull()]
                df = df[df['__parsed_date'].apply(lambda d: abs((d - training_date).days) <= 5)]
            
            # Convert DataFrame to list of dictionaries
            students = []
            for _, row in df.iterrows():
                student = {}
                
                # Special handling for GRADO - check OFICIAL or SUBOFICIAL columns
                grado = None
                if "OFICIAL" in df.columns and not pd.isna(row["OFICIAL"]) and str(row["OFICIAL"]).strip():
                    grado = str(row["OFICIAL"]).strip()
                elif "SUBOFICIAL" in df.columns and not pd.isna(row["SUBOFICIAL"]) and str(row["SUBOFICIAL"]).strip():
                    grado = str(row["SUBOFICIAL"]).strip()
                
                # Set grado value
                if grado:
                    student["grado"] = grado
                else:
                    student["grado"] = ""
                
                # Process other fields
                for excel_col, app_field in field_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        # Handle NaN values
                        if pd.isna(value):
                            value = ""
                        elif app_field == "edad":
                            # Extract digits from the value, ignore non-numeric characters
                            if pd.notna(value):
                                digits = re.findall(r'\d+', str(value))
                                value = digits[0] if digits else ""
                            else:
                                value = ""
                        else:
                            value = str(value).strip()
                        
                        # Map to our app fields
                        if app_field in self.var_keys:
                            student[app_field] = value
                        elif app_field == "telefono":
                            # Store phone number but don't map directly
                            # (useful for emergency contact)
                            pass
                
                # Initialize empty values for fields not in the Excel
                for key in self.var_keys:
                    if key not in student:
                        student[key] = ""
                
                # Default gender to '-' if not specified
                if "genero" in student and not student["genero"]:
                    student["genero"] = "-"
                
                # Only add if there's at least a name
                if student.get("apellido_nombre", "").strip():
                    students.append(student)
            
            return students
        except Exception as e:
            print(f"Error loading Excel: {e}")
            raise

    def load_observadores_from_excel(self, file_path, training_date):
        """Load Observadores Internos from Excel file that are available on or after the training date, within +/- 5 days."""
        try:
            df = pd.read_excel(file_path)
            
            # Debug: Print column names to help identify issues
            print("Excel columns available:")
            for i, col in enumerate(df.columns):
                print(f"  {i}: {col}")
            
            # Map Excel columns to app field names
            field_mapping = {
                # Remove GRADO mapping as we'll handle it separately
                "APELLIDOS Y NOMBRES": "apellido_nombre",
                "EDAD": "edad", 
                "UNIDAD OPERATIVA": "unidad",
                "CORREO INSTITUCIONAL": "email",
                "CELULAR": "telefono"  # Extra field that might be useful
            }
            
            # Helper function to find a column by partial match
            def find_column(search_terms, columns):
                for term in search_terms:
                    for col in columns:
                        if term.lower() in col.lower():
                            return col
                return None
            
            # Try to find the correct columns using flexible matching
            observer_column = find_column(["INSTRUCTOR", "HIPOXIA", "ALUMNO"], df.columns)
            date_column = find_column(["FECHA", "EVALUACION"], df.columns)
            responsible_column = find_column(["RESPONSABLE", "RESP"], df.columns)
            
            print(f"Using columns: Observer={observer_column}, Date={date_column}, Responsible={responsible_column}")
            
            if not observer_column:
                print("WARNING: Could not find the column for 'Observador Interno' identification")
                observer_column = "ES USTED ALUMNO O INSTRUCTOR DE ENTRENAMIENTO EN HIPOXIA HIPOBÁRICA ?"
            
            if not date_column:
                print("WARNING: Could not find the date column")
                date_column = "FECHA EVALUACION" 
            
            if not responsible_column:
                print("WARNING: Could not find the Responsable column")
                responsible_column = "Responsable"
            
            # Try to filter by date +/- 5 days if a date is set and a date column exists
            if training_date and date_column:
                def parse_excel_date(val):
                    if isinstance(val, datetime.datetime):
                        return val.date()
                    if isinstance(val, str):
                        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
                            try:
                                return datetime.datetime.strptime(val, fmt).date()
                            except Exception:
                                continue
                    return None
                df['__parsed_date'] = df[date_column].apply(parse_excel_date)
                df = df[df['__parsed_date'].notnull()]
                df = df[df['__parsed_date'].apply(lambda d: abs((d - training_date).days) <= 5)]
            
            # Filter for Observadores Internos (column G)
            observadores = []
            total_rows = len(df)
            print(f"Processing {total_rows} rows from Excel")
            filtered_counter = 0
            
            for _, row in df.iterrows():
                # Check if column G contains "Observador Interno"
                col_g_value = str(row.get(observer_column, "")).strip()
                # Check for "Observador Interno" (case insensitive)
                if "observador interno" not in col_g_value.lower():
                    # Debug: Uncomment to see all values
                    # print(f"Skipping: '{col_g_value}' is not 'Observador Interno'")
                    continue
                filtered_counter += 1
                
                # Check availability date (must be >= training date)
                if date_column in df.columns and pd.notna(row[date_column]):
                    try:
                        # Try to parse the date from Excel
                        if isinstance(row[date_column], datetime.datetime):
                            excel_date = row[date_column].date()
                        elif isinstance(row[date_column], str):
                            try:
                                excel_date = datetime.datetime.strptime(row[date_column], "%Y-%m-%d").date()
                            except ValueError:
                                try:
                                    excel_date = datetime.datetime.strptime(row[date_column], "%d/%m/%Y").date()
                                except ValueError:
                                    # If parsing fails, skip this row
                                    print(f"Warning: Could not parse date '{row[date_column]}'")
                                    continue
                        else:
                            # Skip rows where date can't be parsed
                            print(f"Warning: Unsupported date format: {type(row[date_column])}")
                            continue
                            
                        # Skip if date is before training date
                        if excel_date < training_date:
                            print(f"Skipping: Date {excel_date} is before training date {training_date}")
                            continue
                    except Exception as e:
                        print(f"Error parsing date: {e}")
                        continue
                
                # Check column AZ (should not be "REGISTRO INVALIDO")
                if responsible_column in df.columns:
                    az_value = str(row.get(responsible_column, "")).strip()
                    if not az_value:  # Only check if the value is empty
                        print(f"Skipping: Responsable column is empty")
                        continue  # Skip if invalid or empty
                
                # If we got here, the Observador Interno meets the criteria
                observador = {}
                
                # Special handling for GRADO - check OFICIAL or SUBOFICIAL columns
                grado = None
                if "OFICIAL" in df.columns and not pd.isna(row["OFICIAL"]) and str(row["OFICIAL"]).strip():
                    grado = str(row["OFICIAL"]).strip()
                elif "SUBOFICIAL" in df.columns and not pd.isna(row["SUBOFICIAL"]) and str(row["SUBOFICIAL"]).strip():
                    grado = str(row["SUBOFICIAL"]).strip()
                
                # Set grado value
                if grado:
                    observador["grado"] = grado
                else:
                    observador["grado"] = ""
                
                # Process other fields
                for excel_col, app_field in field_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        # Handle NaN values
                        if pd.isna(value):
                            value = ""
                        elif app_field == "edad":
                            # Extract digits from the value, ignore non-numeric characters
                            if pd.notna(value):
                                digits = re.findall(r'\d+', str(value))
                                value = digits[0] if digits else ""
                            else:
                                value = ""
                        else:
                            value = str(value).strip()
                        
                        # Map to our app fields
                        if app_field in self.var_keys:
                            observador[app_field] = value
                        elif app_field == "telefono":
                            # Store phone number but don't map directly
                            pass
                
                # Initialize empty values for fields not in the Excel
                for key in self.var_keys:
                    if key not in observador:
                        observador[key] = ""
                
                # Default gender to '-' if not specified
                if "genero" in observador and not observador["genero"]:
                    observador["genero"] = "-"
                
                # Add additional metadata about the Observador Interno
                if responsible_column in df.columns:
                    observador["estado_medico"] = str(row.get(responsible_column, "")).strip()
                
                # Only add if there's at least a name
                if observador.get("apellido_nombre", "").strip():
                    observadores.append(observador)
                else:
                    print("Warning: Found Observador Interno without name, skipping")
            
            print(f"Found {filtered_counter} 'Observador Interno' entries")
            print(f"Final filtered observadores count: {len(observadores)}")
            
            # FALLBACK: If no observadores were found with the strict criteria, try simpler approach
            if not observadores:
                print("No observadores found with strict criteria. Using fallback approach...")
                
                # Look for any rows that contain "Observador Interno" anywhere
                for _, row in df.iterrows():
                    is_observador = False
                    
                    # Check all string columns for "Observador Interno"
                    for col in df.columns:
                        if pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
                            value = str(row.get(col, "")).strip().lower()
                            if "observador interno" in value:
                                is_observador = True
                                break
                    
                    if not is_observador:
                        continue
                        
                    # If it's an observador, process data similar to students
                    observador = {}
                    
                    # Special handling for GRADO - check OFICIAL or SUBOFICIAL columns
                    grado = None
                    if "OFICIAL" in df.columns and not pd.isna(row["OFICIAL"]) and str(row["OFICIAL"]).strip():
                        grado = str(row["OFICIAL"]).strip()
                    elif "SUBOFICIAL" in df.columns and not pd.isna(row["SUBOFICIAL"]) and str(row["SUBOFICIAL"]).strip():
                        grado = str(row["SUBOFICIAL"]).strip()
                    
                    # Set grado value
                    if grado:
                        observador["grado"] = grado
                    else:
                        observador["grado"] = ""
                    
                    # Process other fields
                    for excel_col, app_field in field_mapping.items():
                        if excel_col in df.columns:
                            value = row[excel_col]
                            # Handle NaN values
                            if pd.isna(value):
                                value = ""
                            elif app_field == "edad":
                                # Extract digits from the value, ignore non-numeric characters
                                if pd.notna(value):
                                    digits = re.findall(r'\d+', str(value))
                                    value = digits[0] if digits else ""
                                else:
                                    value = ""
                            else:
                                value = str(value).strip()
                            
                            # Map to our app fields
                            if app_field in self.var_keys:
                                observador[app_field] = value
                            elif app_field == "telefono":
                                # Store phone number but don't map directly
                                pass
                    
                    # Initialize empty values for fields not in the Excel
                    for key in self.var_keys:
                        if key not in observador:
                            observador[key] = ""
                    
                    # Default gender to '-' if not specified
                    if "genero" in observador and not observador["genero"]:
                        observador["genero"] = "-"
                        
                    # Add metadata about estado medico if responsible column exists
                    if responsible_column in df.columns:
                        observador["estado_medico"] = str(row.get(responsible_column, "")).strip()
                    else:
                        observador["estado_medico"] = "Sin información"
                    
                    # Only add if there's at least a name
                    if observador.get("apellido_nombre", "").strip():
                        observadores.append(observador)
                
                print(f"Fallback search found {len(observadores)} potential Observadores Internos")
            
            return observadores
            
        except Exception as e:
            import traceback
            print(f"Error loading Observadores Internos from Excel: {str(e)}")
            traceback.print_exc()
            raise

    def show_student_selection_dialog(self, students_data):
        """Show dialog to let user select which students to import."""
        # Create a dialog window
        dialog = ttkb.Toplevel(self)
        dialog.title("Seleccionar Estudiantes para Importar")
        dialog.geometry("800x500")  # Larger size for better readability
        dialog.transient(self)
        dialog.grab_set()  # Modal dialog
        
        # Instructions label
        instructions = ttkb.Label(
            dialog,
            text="Seleccione los estudiantes que desea importar y asigne sus sillas:",
            font=('Segoe UI', 11),
            bootstyle="info",
            padding=10
        )
        instructions.pack(fill=tk.X)
        
        # Use a simple Canvas with Scrollbar instead of ScrolledFrame
        frame = ttkb.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar to the canvas
        scrollbar = ttkb.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create a frame inside the canvas to hold the content
        container = ttkb.Frame(canvas)
        
        # Add the container frame to a window in the canvas
        canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")
        
        # Make sure the frame takes the full width of the canvas
        def configure_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas_window)
        
        # Update scrollregion when the container size changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        container.bind('<Configure>', configure_scroll_region)
        
        # Bind mousewheel event for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Ensure proper cleanup when dialog is closed
        def on_dialog_close():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Table header
        header_frame = ttkb.Frame(container)
        header_frame.pack(fill=tk.X, pady=5)
        
        # Headers
        ttkb.Label(header_frame, text="Seleccionar", width=10, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Silla", width=8, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Grado", width=10, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Nombre", width=30, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Unidad", width=15, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttkb.Separator(container, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # Create a frame to hold all student entries for better scrolling
        students_container = ttkb.Frame(container)
        students_container.pack(fill=tk.BOTH, expand=True)
        
        # Track used chairs
        used_chairs = set()
        chair_vars = {}
        
        # Add checkboxes and chair selection for each student
        checkboxes = {}
        for i, student in enumerate(students_data):
            var = tk.BooleanVar(value=False)  # Default unselected
            checkboxes[i] = var
            
            # Create frame for each student with checkbox and info
            student_frame = ttkb.Frame(students_container)
            student_frame.pack(fill=tk.X, pady=2)
            
            # Checkbox
            checkbox = ttkb.Checkbutton(
                student_frame, 
                variable=var,
                bootstyle="primary-round-toggle"
            )
            checkbox.pack(side=tk.LEFT, padx=(5, 10), pady=2)
            
            # Chair selection dropdown
            chair_var = tk.StringVar()
            chair_vars[i] = chair_var
            available_chairs = [str(x) for x in range(1, self.max_students + 1)]
            
            def on_chair_selected(event, current_i):
                # Update used chairs
                new_chair = chair_vars[current_i].get()
                # Check if this chair is used by another student
                for other_i, other_var in chair_vars.items():
                    if other_i != current_i and other_var.get() == new_chair:
                        # Swap chairs
                        other_var.set("")
            
            chair_dropdown = ttkb.Combobox(
                student_frame,
                textvariable=chair_var,
                values=available_chairs,
                width=6,
                state="readonly"
            )
            chair_dropdown.pack(side=tk.LEFT, padx=5)
            chair_dropdown.bind('<<ComboboxSelected>>', lambda e, i=i: on_chair_selected(e, i))
            
            # Student info - in columns
            grado = student.get("grado", "")
            name = student.get("apellido_nombre", "")
            unidad = student.get("unidad", "")
            
            grado_label = ttkb.Label(student_frame, text=grado, width=10)
            grado_label.pack(side=tk.LEFT, padx=5)
            
            name_label = ttkb.Label(student_frame, text=name, width=30, anchor="w")
            name_label.pack(side=tk.LEFT, padx=5)
            
            unidad_label = ttkb.Label(student_frame, text=unidad, width=15)
            unidad_label.pack(side=tk.LEFT, padx=5)
        
        # Add Select All / Deselect All buttons
        button_frame = ttkb.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def select_all():
            for var in checkboxes.values():
                var.set(True)
        
        def deselect_all():
            for var in checkboxes.values():
                var.set(False)
        
        select_all_btn = ttkb.Button(
            button_frame,
            text="Seleccionar Todos",
            command=select_all,
            bootstyle="info-outline",
            width=20
        )
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        deselect_all_btn = ttkb.Button(
            button_frame,
            text="Deseleccionar Todos",
            command=deselect_all,
            bootstyle="warning-outline",
            width=20
        )
        deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttkb.Frame(dialog)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def import_selected():
            selected_data = []
            for i, var in checkboxes.items():
                if var.get():
                    chair = chair_vars[i].get()
                    if not chair:
                        messagebox.showwarning(
                            "Advertencia",
                            "Por favor asigne una silla a todos los estudiantes seleccionados.",
                            parent=dialog
                        )
                        return
                    student_data = students_data[i].copy()
                    student_data['assigned_chair'] = chair
                    selected_data.append(student_data)
            
            if selected_data:
                # Sort by assigned chair
                selected_data.sort(key=lambda x: int(x['assigned_chair']))
                self.apply_selected_students(selected_data)
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()
                messagebox.showinfo(
                    "Importación Exitosa", 
                    f"Se importaron {len(selected_data)} estudiantes.", 
                    parent=self
                )
            else:
                messagebox.showinfo(
                    "Importación", 
                    "No se seleccionaron estudiantes para importar.", 
                    parent=dialog
                )
        
        import_btn = ttkb.Button(
            action_frame,
            text="Importar Seleccionados",
            command=import_selected,
            bootstyle="success",
            width=25
        )
        import_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttkb.Button(
            action_frame,
            text="Cancelar",
            command=on_dialog_close,
            bootstyle="danger-outline",
            width=15
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def show_observadores_selection_dialog(self, observadores_data):
        """Show dialog to let user select which Observadores Internos to import."""
        # Create a dialog window
        dialog = ttkb.Toplevel(self)
        dialog.title("Seleccionar Observadores Internos para Importar")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Instructions label
        instructions = ttkb.Label(
            dialog,
            text="Seleccione los observadores internos que desea importar y asigne sus posiciones:",
            font=('Segoe UI', 11),
            bootstyle="info",
            padding=10
        )
        instructions.pack(fill=tk.X)
        
        # Show count of found observadores
        count_label = ttkb.Label(
            dialog,
            text=f"Se encontraron {len(observadores_data)} observadores internos",
            font=('Segoe UI', 10),
            bootstyle="secondary"
        )
        count_label.pack(pady=(0, 10))
        
        # Create scrollable frame
        frame = ttkb.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttkb.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        container = ttkb.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")
        
        def configure_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas_window)
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        container.bind('<Configure>', configure_scroll_region)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def on_dialog_close():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Table header
        header_frame = ttkb.Frame(container)
        header_frame.pack(fill=tk.X, pady=5)
        
        # Headers
        ttkb.Label(header_frame, text="Seleccionar", width=10, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Posición", width=8, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Grado", width=10, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Nombre", width=30, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Estado Médico", width=15, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttkb.Separator(container, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # Create container for observadores
        observadores_container = ttkb.Frame(container)
        observadores_container.pack(fill=tk.BOTH, expand=True)
        
        # Track position assignments
        position_vars = {}
        checkboxes = {}
        
        for i, observador in enumerate(observadores_data):
            var = tk.BooleanVar(value=False)
            checkboxes[i] = var
            
            observador_frame = ttkb.Frame(observadores_container)
            observador_frame.pack(fill=tk.X, pady=2)
            
            # Checkbox
            checkbox = ttkb.Checkbutton(
                observador_frame, 
                variable=var,
                bootstyle="info-round-toggle"
            )
            checkbox.pack(side=tk.LEFT, padx=(5, 10), pady=2)
            
            # Position selection dropdown
            position_var = tk.StringVar()
            position_vars[i] = position_var
            
            def on_position_selected(event, current_i):
                new_pos = position_vars[current_i].get()
                for other_i, other_var in position_vars.items():
                    if other_i != current_i and other_var.get() == new_pos:
                        other_var.set("")
            
            position_dropdown = ttkb.Combobox(
                observador_frame,
                textvariable=position_var,
                values=["OI1", "OI2"],
                width=6,
                state="readonly"
            )
            position_dropdown.pack(side=tk.LEFT, padx=5)
            position_dropdown.bind('<<ComboboxSelected>>', lambda e, i=i: on_position_selected(e, i))
            
            # Observador info
            grado = observador.get("grado", "")
            name = observador.get("apellido_nombre", "")
            estado_medico = observador.get("estado_medico", "")
            
            grado_label = ttkb.Label(observador_frame, text=grado, width=10)
            grado_label.pack(side=tk.LEFT, padx=5)
            
            name_label = ttkb.Label(observador_frame, text=name, width=30, anchor="w")
            name_label.pack(side=tk.LEFT, padx=5)
            
            estado_label = ttkb.Label(observador_frame, text=estado_medico, width=15)
            estado_label.pack(side=tk.LEFT, padx=5)
        
        # Add Deselect All button before action buttons
        selection_frame = ttkb.Frame(dialog)
        selection_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        def deselect_all():
            for var in checkboxes.values():
                var.set(False)
        
        deselect_all_btn = ttkb.Button(
            selection_frame,
            text="Deseleccionar Todos",
            command=deselect_all,
            bootstyle="warning-outline",
            width=20
        )
        deselect_all_btn.pack(side=tk.LEFT, padx=5)

        # Action buttons
        action_frame = ttkb.Frame(dialog)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def import_selected():
            selected_data = []
            for i, var in checkboxes.items():
                if var.get():
                    position = position_vars[i].get()
                    if not position:
                        messagebox.showwarning(
                            "Advertencia",
                            "Por favor asigne una posición (OI1/OI2) a todos los observadores seleccionados.",
                            parent=dialog
                        )
                        return
                    observador_data = observadores_data[i].copy()
                    observador_data['assigned_position'] = position
                    selected_data.append(observador_data)
            
            if selected_data:
                # Sort by position (OI1 before OI2)
                selected_data.sort(key=lambda x: x['assigned_position'])
                self.apply_selected_observadores(selected_data)
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()
                messagebox.showinfo(
                    "Importación Exitosa", 
                    f"Se importaron {len(selected_data)} observadores internos.", 
                    parent=self
                )
            else:
                messagebox.showinfo(
                    "Importación", 
                    "No se seleccionaron observadores internos para importar.", 
                    parent=dialog
                )
        
        import_btn = ttkb.Button(
            action_frame,
            text="Importar Seleccionados",
            command=import_selected,
            bootstyle="success",
            width=25
        )
        import_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttkb.Button(
            action_frame,
            text="Cancelar",
            command=on_dialog_close,
            bootstyle="danger-outline",
            width=15
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def apply_selected_students(self, selected_students):
        """Apply selected student data to the form."""
        try:
            # Clear existing data first
            for slot_id in [str(i) for i in range(1, self.max_students + 1)]:
                for field_key, var in self.participant_vars[slot_id].items():
                    if field_key == 'genero':
                        var.set(self.gender_options[-1])
                    else:
                        var.set('')
                self.chair_vars[slot_id].set(slot_id)
            
            # Import students into their assigned chairs
            for student in selected_students:
                assigned_chair = student.pop('assigned_chair')  # Remove from dict after getting value
                slot_id = str(assigned_chair)
                
                # Set chair
                self.chair_vars[slot_id].set(assigned_chair)
                
                # Set other fields
                for field, value in student.items():
                    if field in self.participant_vars[slot_id]:
                        self.participant_vars[slot_id][field].set(value)
            
            # Save data after import
            self.save_data()
            
        except Exception as e:
            print(f"Error applying selected students: {e}")
            messagebox.showerror(
                "Error",
                f"Error al importar estudiantes: {str(e)}",
                parent=self
            )

    def apply_selected_observadores(self, selected_observadores):
        """Apply selected Observadores Internos data to the OI slots."""
        try:
            # Clear existing OI data first
            for slot_id in [f"OI{i}" for i in range(1, self.max_oi + 1)]:
                for field_key, var in self.participant_vars[slot_id].items():
                    if field_key == 'genero':
                        var.set(self.gender_options[-1])
                    else:
                        var.set('')
                self.chair_vars[slot_id].set(slot_id)
            
            # Import observadores into their assigned positions
            for observador in selected_observadores:
                assigned_position = observador.pop('assigned_position')  # Remove from dict after getting value
                slot_id = assigned_position
                
                # Set position
                self.chair_vars[slot_id].set(assigned_position)
                
                # Set other fields
                for field, value in observador.items():
                    if field in self.participant_vars[slot_id]:
                        self.participant_vars[slot_id][field].set(value)
            
            # Save data after import
            self.save_data()
            
        except Exception as e:
            print(f"Error applying selected observadores: {e}")
            messagebox.showerror(
                "Error",
                f"Error al importar observadores internos: {str(e)}",
                parent=self
            )
    
    def set_current_date(self):
        """Set current date in the date field using format DD-MM-AAAA."""
        today_str = datetime.datetime.now().strftime("%d-%m-%Y")
        self.training_date_var.set(today_str)
        self.update_idletasks()
    
    # --- Removed show_toast method if not needed or handled globally --- 