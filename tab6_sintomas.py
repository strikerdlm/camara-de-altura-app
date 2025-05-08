#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any, List, Optional
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime

# --- Symptom Selection Dialog ---
class SymptomDialog(tk.Toplevel):
    """Dialog to select up to 3 symptoms."""
    def __init__(self, parent, title, symptoms_list, current_symptoms):
        super().__init__(parent)
        self.title(title)
        self.transient(parent) # Make it modal relative to parent
        self.grab_set() # Grab focus
        self.result = None # Store selected symptoms
        self.max_select = 3
        self.symptoms_list = symptoms_list
        
        self.vars = {}
        self.checkbuttons = []

        # --- UI Layout --- 
        main_frame = ttkb.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header = ttkb.Label(main_frame, text="Seleccione hasta 3 síntomas:", bootstyle="info")
        header.pack(pady=(0, 10))
        
        # Scrollable frame for checkboxes - increased height and width
        list_frame = ScrolledFrame(main_frame, autohide=True, height=500, width=400)
        list_frame.pack(fill=tk.BOTH, expand=True)
        container = list_frame.container

        for symptom in self.symptoms_list:
             var = tk.BooleanVar()
             # Pre-select if it's in current symptoms
             if symptom in current_symptoms:
                 var.set(True)
                 
             cb = ttkb.Checkbutton(container, text=symptom, variable=var, 
                                   bootstyle="round-toggle", command=self.check_limit)
             cb.pack(anchor='w', padx=10, pady=2)
             self.vars[symptom] = var
             self.checkbuttons.append(cb)

        # --- Buttons --- 
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ok_btn = ttkb.Button(button_frame, text="OK", command=self.on_ok, bootstyle="success")
        ok_btn.pack(side=tk.RIGHT, padx=5)
        cancel_btn = ttkb.Button(button_frame, text="Cancelar", command=self.on_cancel, bootstyle="secondary")
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Center the dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')
        
        # Check limit initially
        self.check_limit()

    def check_limit(self):
        """Disable checkbuttons if max selection is reached."""
        selected_count = sum(var.get() for var in self.vars.values())
        if selected_count >= self.max_select:
             # Disable unchecked buttons
             for cb in self.checkbuttons:
                 symptom = cb.cget("text")
                 if not self.vars[symptom].get():
                     cb.configure(state=tk.DISABLED)
        else:
             # Enable all buttons
             for cb in self.checkbuttons:
                 cb.configure(state=tk.NORMAL)

    def on_ok(self):
        """Store selected symptoms and close."""
        self.result = [symptom for symptom, var in self.vars.items() if var.get()]
        self.destroy()

    def on_cancel(self):
        """Close without returning selections."""
        self.result = None
        self.destroy()

class SintomasTab(ttkb.Frame):
    """Tab for student symptoms management with improved layout."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        self.main_app = main_app
        self.prevent_load_overwrite = False
        
        # Constants
        self.num_students = 8
        
        # Symptom List
        self.symptom_options = [
            "Ansiedad", "Beligerancia", "Cansancio fisico", "Cansancio mental", "Dolor de cabeza",
            "Falsa Sensación de Bienestar", "Falta de aire", "Hormigueo",
            "Irritabilidad", "Lentitud para pensar", "Mareo", "Nauseas", 
            "Palpitaciones", "Pérdida de consciencia", "Reducción de fuerza", 
            "Reducción de memoria", "Sensación de calor / frío", "Sobreconfianza", 
            "Sudoración", "Sueño", "Temblor", "Visión borrosa", "Otro"
        ]

        # Variables for UI elements
        self.student_symptom_vars: Dict[str, tk.StringVar] = {}  # For display labels
        self.student_detail_labels: Dict[str, List[tk.Label]] = {}  # For detailed symptom display
        
        # Internal data storage
        self.student_symptoms: Dict[str, List[str]] = {}  # Store selected symptoms per student
        
        self.symptom_entries = {}  # Ensure this attribute always exists
        
        self.initialize_data()
        self.create_widgets()
        self.load_data()  # Load after widgets exist
        
    def _update_datamanager_with_own_data(self):
        """Helper method to update DataManager with this tab's data."""
        # self.student_symptoms is already the prepared data structure for this tab
        self.data_manager.current_data['student_symptoms'] = self.student_symptoms
        
        session_id = self.data_manager.current_data.get('vuelo', {}).get('numero_entrenamiento', '')
        if not session_id:
            vuelo_del_ano = self.data_manager.current_data.get('vuelo', {}).get('vuelo_del_ano', '')
            if vuelo_del_ano:
                year_suffix = datetime.now().strftime("%y") # Ensure datetime is imported
                session_id = f"{vuelo_del_ano}-{year_suffix}"

        if session_id:
            if 'sessions_data' not in self.data_manager.current_data:
                self.data_manager.current_data['sessions_data'] = {}
            if session_id not in self.data_manager.current_data['sessions_data']:
                self.data_manager.current_data['sessions_data'][session_id] = {}
            self.data_manager.current_data['sessions_data'][session_id]['student_symptoms'] = self.student_symptoms
        print(f"Tab6: Updated student_symptoms in DataManager for session {session_id}")
        
    def _on_data_changed(self, *args):
        """Callback for data changes. Sets the prevent_load_overwrite flag."""
        if not self.prevent_load_overwrite:
            print(f"SintomasTab: Data changed, setting prevent_load_overwrite = True")
            self.prevent_load_overwrite = True

    def initialize_data(self):
        """Initialize or load symptom data."""
        # Load student symptoms
        loaded_symptoms = self.data_manager.current_data.get('student_symptoms', {})
        self.student_symptoms = {}
        for i in range(1, self.num_students + 1):
            student_id = str(i)
            # Ensure loaded data is a list, default to empty list
            symptoms = loaded_symptoms.get(student_id, [])
            if not isinstance(symptoms, list):
                symptoms = []
            self.student_symptoms[student_id] = symptoms

    def create_widgets(self):
        """Create the tab layout with improved symptom management."""
        # Main layout - single column (removed detail view)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # --- Single column: Simple list of students with buttons --- 
        students_frame = ttkb.LabelFrame(
            self, 
            text="Listado de Alumnos", 
            padding=10,
            bootstyle="primary"
        )
        students_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.create_students_list_section(students_frame)
        
        # --- Bottom: Action buttons ---
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        save_btn = ttkb.Button(
            button_frame, 
            text="Guardar Datos", 
            command=self.save_data_with_confirmation,
            bootstyle='success',
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        clear_all_btn = ttkb.Button(
            button_frame, 
            text="Limpiar Todos", 
            command=self.clear_all_symptoms,
            bootstyle='danger',
            width=15
        )
        clear_all_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def create_students_list_section(self, parent):
        """Creates the list of students with symptom summary and edit buttons."""
        # Make the frame scrollable
        scrolled_frame = ScrolledFrame(parent, autohide=True)
        scrolled_frame.pack(fill=tk.BOTH, expand=True)
        container = scrolled_frame.container
        
        # Configure grid for student list
        container.columnconfigure(0, weight=1)  # Student label
        container.columnconfigure(1, weight=3)  # Symptoms summary
        container.columnconfigure(2, weight=0)  # Edit button
        
        # Header row
        header_student = ttkb.Label(container, text="Alumno", font=('Segoe UI', 10, 'bold'))
        header_student.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        header_symptoms = ttkb.Label(container, text="Síntomas", font=('Segoe UI', 10, 'bold'))
        header_symptoms.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        header_actions = ttkb.Label(container, text="Acciones", font=('Segoe UI', 10, 'bold'))
        header_actions.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        ttkb.Separator(container, orient='horizontal').grid(
            row=1, column=0, columnspan=3, sticky='ew', padx=5, pady=3
        )
        
        # Create a row for each student
        for i in range(1, self.num_students + 1):
            student_id = str(i)
            row_idx = i + 1  # +1 for header and separator
            
            # Student label
            student_label = ttkb.Label(
                container, 
                text=f"Alumno {student_id}:", 
                font=('Segoe UI', 10),
                anchor='w'
            )
            student_label.grid(row=row_idx, column=0, padx=5, pady=8, sticky='w')
            
            # Symptoms summary label
            symptom_var = tk.StringVar(value="Ninguno")
            self.student_symptom_vars[student_id] = symptom_var
            symptom_summary = ttkb.Label(
                container,
                textvariable=symptom_var,
                font=('Segoe UI', 9),
                anchor='w',
                wraplength=250
            )
            symptom_summary.grid(row=row_idx, column=1, padx=5, pady=8, sticky='w')
            
            # Edit button
            edit_btn = ttkb.Button(
                container,
                text="Editar",
                command=lambda s_id=student_id: self.open_symptom_dialog(s_id),
                bootstyle="primary-outline",
                width=8
            )
            edit_btn.grid(row=row_idx, column=2, padx=5, pady=8, sticky='w')
            
            # Add a separator after each student (except the last one)
            if i < self.num_students:
                ttkb.Separator(container, orient='horizontal').grid(
                    row=row_idx + 1, column=0, columnspan=3, sticky='ew', padx=5, pady=3
                )

    def open_symptom_dialog(self, student_id: str):
        """Opens the symptom selection dialog for a specific student."""
        current_symptoms = self.student_symptoms.get(student_id, [])
        dialog = SymptomDialog(self, f"Síntomas Alumno {student_id}", self.symptom_options, current_symptoms)
        self.wait_window(dialog)  # Wait for the dialog to close
        
        if dialog.result is not None:  # Check if OK was pressed
            self._on_data_changed() # Mark as changed before modifying data
            selected_symptoms = dialog.result
            self.student_symptoms[student_id] = selected_symptoms
            # Update the display label
            self.update_symptom_summary(student_id)
            # Save the changes
            self.save_data()
            print(f"Symptoms updated for student {student_id}: {', '.join(selected_symptoms) if selected_symptoms else 'None'}")

    def update_symptom_summary(self, student_id: str):
        """Updates the symptom summary label for a student."""
        if student_id in self.student_symptom_vars:
            symptoms = self.student_symptoms.get(student_id, [])
            display_text = ", ".join(symptoms) if symptoms else "Ninguno"
            self.student_symptom_vars[student_id].set(display_text)

    def load_data(self):
        print(f"[DEBUG] tab6_sintomas: load_data called, prevent_load_overwrite={self.prevent_load_overwrite}")
        if getattr(self, 'prevent_load_overwrite', False):
            return
        """Load symptoms data and update UI elements."""
        # Always refresh internal data from data_manager
        loaded_symptoms = self.data_manager.current_data.get('student_symptoms', {})
        for i in range(1, self.num_students + 1):
            student_id = str(i)
            symptoms = loaded_symptoms.get(student_id, [])
            if not isinstance(symptoms, list):
                symptoms = []
            self.student_symptoms[student_id] = symptoms
            self.update_symptom_summary(student_id)

    def save_data_with_confirmation(self):
        self.save_data(triggered_by_user=True)
        # Message is now handled by save_data if triggered_by_user

    def save_data(self, triggered_by_user=True):
        print(f"Tab6 save_data called, triggered_by_user={triggered_by_user}")
        self._update_datamanager_with_own_data()
        
        if triggered_by_user:
            if self.main_app:
                tabs_to_call = {
                    'tab1': getattr(self.main_app, 'tab1', None),
                    'tab2': getattr(self.main_app, 'tab2', None),
                    'tab3': getattr(self.main_app, 'tab3', None),
                    'tab4': getattr(self.main_app, 'tab4', None) # Corrected from tab5
                }
                for tab_name, tab_instance in tabs_to_call.items():
                    if tab_instance and hasattr(tab_instance, 'save_data'):
                        print(f"Tab6 orchestrator: Calling save_data on {tab_name}")
                        tab_instance.save_data(triggered_by_user=False)
            
            self.data_manager.save_data()
            
            if self.main_app and hasattr(self.main_app, 'refresh_all_tabs'):
                self.main_app.refresh_all_tabs()
                
            Messagebox.show_info(
                "Guardado",
                "Todos los datos han sido guardados exitosamente.",
                parent=self
            )
            self.prevent_load_overwrite = False
        else:
            self.prevent_load_overwrite = False

    def clear_all_symptoms(self, confirm=True):
        """Clear all symptom fields for all students. Only show confirmation if confirm=True."""
        if confirm:
            if not messagebox.askyesno(
                "Confirmar",
                "¿Está seguro de limpiar los síntomas de todos los alumnos?\n\nEsta acción borrará los datos en esta pestaña."
            ):
                return
        # Clear internal data structure
        self.student_symptoms = {str(i): [] for i in range(1, self.num_students + 1)}
        
        # Update UI summaries
        for i in range(1, self.num_students + 1):
            self.update_symptom_summary(str(i))
            
        # Mark as changed and save the cleared state
        self._on_data_changed()
        self.save_data()
        
        # Show confirmation message
        messagebox.showinfo("Limpieza Completada", "Se han limpiado los síntomas de todos los alumnos.", parent=self) 