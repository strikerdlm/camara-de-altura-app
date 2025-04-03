#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any, List
from ttkbootstrap.scrolled import ScrolledFrame

class AlumnosTab(ttkb.Frame):
    """Tab for student and OI data, aligned with camara.mdc rules."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Constants from rules
        self.max_students = 8
        self.max_oi = 2
        self.participant_keys = [str(i) for i in range(1, self.max_students + 1)] + \
                                [f"OI{i}" for i in range(1, self.max_oi + 1)]
        self.gender_options = ["M", "F", "-"] # Added default/unknown

        # Data structure to hold tk variables for all entries
        self.participant_vars: Dict[str, Dict[str, tk.StringVar]] = {}
        
        # Define headers and corresponding variable keys (must match rules)
        self.headers = ["Silla", "Grado", "Apellido y Nombre", "Edad", "Genero", 
                        "Unidad", "Email", "Mask", "Helmet"]
        self.var_keys = ["grado", "apellido_nombre", "edad", "genero", 
                         "unidad", "email", "mask", "helmet"]
        # Define approximate widths for columns
        self.col_widths = [6, 10, 25, 5, 7, 15, 20, 8, 8]

        # Create the layout
        self.create_widgets()
        self.load_data() # Load data after widgets are created
    
    def create_widgets(self):
        """Create the main tab layout with scrollable frame."""
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

        # --- OI Section --- 
        oi_frame = ttkb.LabelFrame(
            container,
            text="Datos de Operadores Internos (OI)",
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
            text="Guardar Datos Alumnos/OI",
            command=self.save_data,
            bootstyle="success", # Use success style
            width=25
        )
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        clear_btn = ttkb.Button(
            button_frame,
            text="Limpiar Datos Alumnos/OI",
            command=self.clear_form,
            bootstyle="warning", # Use warning style
            width=25
        )
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def _create_participant_table(self, parent_frame, participant_ids: List[str], is_oi_section: bool):
        """Creates the header and rows for a list of participants (students or OIs)."""
        header_bootstyle = "primary" if not is_oi_section else "info"

        # Create header row using self.headers and self.col_widths
        for col, (header, width) in enumerate(zip(self.headers, self.col_widths)):
            # Configure column weight for resizing? Maybe not needed if width is fixed.
            # parent_frame.columnconfigure(col, weight=1 if col == 2 else 0) # Example: make name expand
            
            header_label = ttkb.Label(
                parent_frame,
                text=header,
                font=('Segoe UI', 10, 'bold'),
                bootstyle=header_bootstyle,
                width=width,
                anchor='w' # Anchor text to the west (left)
            )
            header_label.grid(row=0, column=col, padx=5, pady=(5, 2), sticky='w')
        
        # Add separator below header
        separator = ttkb.Separator(parent_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=len(self.headers), sticky="ew", pady=(0, 5))

        # Create rows for each participant
        for i, participant_id in enumerate(participant_ids):
            current_row = i + 2 # Offset for header and separator
            self._create_person_row(parent_frame, current_row, participant_id)
    
    def _create_person_row(self, parent_frame, row, participant_id: str):
        """Creates the widgets for a single participant row."""
        self.participant_vars[participant_id] = {}
        
        # Column 0: Silla/Identifier
        id_label = ttkb.Label(parent_frame, text=participant_id, width=self.col_widths[0])
        id_label.grid(row=row, column=0, padx=5, pady=2, sticky='w')

        # Create widgets for other columns based on self.var_keys
        for col_idx, key in enumerate(self.var_keys):
            actual_col = col_idx + 1 # Offset by 1 because Silla is col 0
            width = self.col_widths[actual_col]
            var = tk.StringVar()
            self.participant_vars[participant_id][key] = var

            if key == "genero":
                widget = ttkb.Combobox(
                    parent_frame,
                    textvariable=var,
                    values=self.gender_options,
                    width=width - 2, # Adjust combobox width
                    state="readonly"
                )
                var.set(self.gender_options[-1]) # Default to '-'
            else:
                widget = ttkb.Entry(
                    parent_frame,
                    textvariable=var,
                    width=width
                )
            
            widget.grid(row=row, column=actual_col, padx=5, pady=2, sticky='we') # Sticky west-east

    def load_data(self):
        """Load existing participant data from data_manager."""
        # Use a consistent key, e.g., 'participantes'
        all_data = self.data_manager.current_data.get('participantes', {}) 
        
        for participant_id, person_data in all_data.items():
            # Check if this participant_id exists in our UI structure
            if participant_id in self.participant_vars: 
                for field_key, value in person_data.items():
                    # Check if the field key exists for this participant
                    if field_key in self.participant_vars[participant_id]:
                        self.participant_vars[participant_id][field_key].set(value)
                    else:
                         print(f"Warning: Field '{field_key}' from loaded data not found in UI for {participant_id}")
            else:
                print(f"Warning: Participant ID '{participant_id}' from loaded data not found in UI.")

    def save_data(self):
        """Save participant data to data_manager."""
        all_data = {}
        for participant_id, fields_dict in self.participant_vars.items():
            person_data = {}
            has_data = False # Flag to check if row has any meaningful data
            for field_key, var in fields_dict.items():
                value = var.get().strip()
                person_data[field_key] = value
                # Consider a row non-empty if at least the name has content
                if field_key == 'apellido_nombre' and value:
                    has_data = True
            
            # Only save rows that have at least a name
            if has_data:
                all_data[participant_id] = person_data
        
        # Update data manager under the consistent key 'participantes'
        self.data_manager.current_data['participantes'] = all_data
        try:
            self.data_manager.save_data()
            print("Datos de Alumnos/OI guardados.")
            # self.show_toast("Datos guardados correctamente") # Optional Toast
        except Exception as e:
            print(f"Error saving participant data: {e}")
            # self.show_toast("Error al guardar datos") # Optional Toast
    
    def clear_form(self):
        """Clear all participant data fields after confirmation."""
        confirm = messagebox.askyesno(
            "Confirmar Limpieza",
            "¿Está seguro que desea limpiar TODOS los datos de Alumnos y OI?",
            icon="warning",
            parent=self # Ensure messagebox is modal to this tab/window
        )
        
        if not confirm:
            return
        
        # Clear all variables
        for participant_id, fields_dict in self.participant_vars.items():
            for field_key, var in fields_dict.items():
                 if field_key == 'genero':
                     var.set(self.gender_options[-1]) # Reset combobox to default '-'
                 else:
                     var.set('')
        
        print("Formulario Alumnos/OI limpiado.")
        # self.show_toast("Formulario limpiado") # Optional Toast
    
    # --- Removed show_toast method if not needed or handled globally --- 