#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
<<<<<<< HEAD
from tkinter import messagebox, filedialog
from typing import Dict, Any, List
from ttkbootstrap.scrolled import ScrolledFrame
import pandas as pd
=======
from tkinter import messagebox
from typing import Dict, List, Any
import json
>>>>>>> 05623bafcb4dd46d5d368abaece58d4cebd092c3
import os

class AlumnosTab(ttkb.Frame):
    """Tab for managing student data."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Student data structure
        self.student_data: List[Dict[str, tk.StringVar]] = []
        
        # Create the layout
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(tuple(range(8)), weight=1)
        
        # Header
        header = ttkb.Label(
            self,
            text="Registro de Alumnos",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))
        
        # Create headers
        headers = [
            "Puesto", "Grado", "Nombre", "Edad", "Sexo",
            "Unidad", "Correo", "No. Equipo"
        ]
        
        for i, header_text in enumerate(headers):
            header = ttkb.Label(
                self,
                text=header_text,
                font=('Segoe UI', 10, 'bold')
            )
            header.grid(row=1, column=i, padx=5, pady=5, sticky="w")
        
        # Create student rows
        for i in range(8):  # 8 students
            self.create_student_row(i + 2, f"Alumno {i + 1}")
        
        # Add separator
        separator = ttkb.Separator(self, orient="horizontal")
        separator.grid(row=10, column=0, columnspan=8, sticky="ew", pady=10)
        
        # Create operator rows
        self.create_student_row(11, "Operador Interno 1")
        self.create_student_row(12, "Operador Interno 2")
        
        # Add buttons at the bottom
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=13, column=0, columnspan=8, sticky="ew", pady=(10, 0))
        
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
<<<<<<< HEAD
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        import_btn = ttkb.Button(
            button_frame,
            text="Importar Alumnos desde Excel",
            command=self.import_from_excel,
            bootstyle="info",
            width=25
        )
        import_btn.pack(side=tk.RIGHT, padx=5, pady=5)

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
=======
        clear_btn.pack(side=tk.RIGHT, padx=5)
>>>>>>> 05623bafcb4dd46d5d368abaece58d4cebd092c3
    
    def create_student_row(self, row: int, position: str):
        """Create a row of entry fields for a student."""
        # Create a dictionary to store the variables for this student
        student_vars = {}
        
        # Position (read-only)
        position_var = tk.StringVar(value=position)
        position_entry = ttkb.Entry(
            self,
            textvariable=position_var,
            state='readonly',
            width=15
        )
        position_entry.grid(row=row, column=0, padx=2, pady=2, sticky="ew")
        student_vars['position'] = position_var
        
        # Rank (Combobox)
        rank_var = tk.StringVar()
        rank_combo = ttkb.Combobox(
            self,
            textvariable=rank_var,
            values=[
                "CT", "MY", "TC", "TE", "ST", "SV", "CP", "T1", "T2", "T3",
                "T4", "AT", "AM", "AS", "AE", "AB", "TSD", "TJC", "ING", "DR"
            ],
            width=8
        )
        rank_combo.grid(row=row, column=1, padx=2, pady=2, sticky="ew")
        student_vars['rank'] = rank_var
        
        # Name
        name_var = tk.StringVar()
        name_entry = ttkb.Entry(self, textvariable=name_var)
        name_entry.grid(row=row, column=2, padx=2, pady=2, sticky="ew")
        student_vars['name'] = name_var
        
        # Age
        age_var = tk.StringVar()
        age_entry = ttkb.Entry(self, textvariable=age_var, width=8)
        age_entry.grid(row=row, column=3, padx=2, pady=2, sticky="ew")
        student_vars['age'] = age_var
        
        # Sex (Combobox)
        sex_var = tk.StringVar()
        sex_combo = ttkb.Combobox(
            self,
            textvariable=sex_var,
            values=["M", "F"],
            width=5
        )
        sex_combo.grid(row=row, column=4, padx=2, pady=2, sticky="ew")
        student_vars['sex'] = sex_var
        
        # Unit
        unit_var = tk.StringVar()
        unit_entry = ttkb.Entry(self, textvariable=unit_var)
        unit_entry.grid(row=row, column=5, padx=2, pady=2, sticky="ew")
        student_vars['unit'] = unit_var
        
        # Email
        email_var = tk.StringVar()
        email_entry = ttkb.Entry(self, textvariable=email_var)
        email_entry.grid(row=row, column=6, padx=2, pady=2, sticky="ew")
        student_vars['email'] = email_var
        
        # Equipment number
        equip_var = tk.StringVar()
        equip_entry = ttkb.Entry(self, textvariable=equip_var, width=8)
        equip_entry.grid(row=row, column=7, padx=2, pady=2, sticky="ew")
        student_vars['equipment'] = equip_var
        
        # Add to student data list
        self.student_data.append(student_vars)
    
    def load_data(self):
        """Load student data into the form fields."""
        # Get student data from data manager
        students_data = self.data_manager.current_data.get('alumnos', [])
        
        # Load data for each student
        for i, student_vars in enumerate(self.student_data):
            if i < len(students_data):
                student = students_data[i]
                # Map data to variables
                student_vars['position'].set(student.get('position', ''))
                student_vars['rank'].set(student.get('rank', ''))
                student_vars['name'].set(student.get('name', ''))
                student_vars['age'].set(student.get('age', ''))
                student_vars['sex'].set(student.get('sex', ''))
                student_vars['unit'].set(student.get('unit', ''))
                student_vars['email'].set(student.get('email', ''))
                student_vars['equipment'].set(student.get('equipment', ''))
    
    def save_data(self):
        """Save form data."""
        # Collect data from all students
        students_data = []
        for student_vars in self.student_data:
            student = {
                'position': student_vars['position'].get(),
                'rank': student_vars['rank'].get(),
                'name': student_vars['name'].get(),
                'age': student_vars['age'].get(),
                'sex': student_vars['sex'].get(),
                'unit': student_vars['unit'].get(),
                'email': student_vars['email'].get(),
                'equipment': student_vars['equipment'].get()
            }
            students_data.append(student)
        
        # Save to data manager
        self.data_manager.current_data['alumnos'] = students_data
        self.data_manager.save_data()
        
        # Show success message
        messagebox.showinfo("Guardado", "Datos de alumnos guardados exitosamente")
    
    def clear_form(self):
<<<<<<< HEAD
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
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar desde Excel: {str(e)}", parent=self)

    def load_students_from_excel(self, file_path):
        """Load student data from Excel file using pandas."""
        try:
            # Read Excel file
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
                            value = str(int(value)) if pd.notna(value) else ""
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

    def show_student_selection_dialog(self, students_data):
        """Show dialog to let user select which students to import."""
        # Create a dialog window
        dialog = ttkb.Toplevel(self)
        dialog.title("Seleccionar Estudiantes para Importar")
        dialog.geometry("700x500")  # Larger size for better readability
        dialog.transient(self)
        dialog.grab_set()  # Modal dialog
        
        # Instructions label
        instructions = ttkb.Label(
            dialog,
            text="Seleccione los estudiantes que desea importar:",
            font=('Segoe UI', 11),
            bootstyle="info",
            padding=10
        )
        instructions.pack(fill=tk.X)
        
        # Use a simple Canvas with Scrollbar instead of ScrolledFrame
        # Create a frame to contain the canvas and scrollbar
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
        ttkb.Label(header_frame, text="Grado", width=10, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Nombre", width=30, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttkb.Label(header_frame, text="Unidad", width=15, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttkb.Separator(container, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # Create a frame to hold all student entries for better scrolling
        students_container = ttkb.Frame(container)
        students_container.pack(fill=tk.BOTH, expand=True)
        
        # Add checkboxes for each student
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
            width=15
        )
        select_all_btn.pack(side=tk.LEFT, padx=5)
        
        deselect_all_btn = ttkb.Button(
            button_frame,
            text="Deseleccionar Todos",
            command=deselect_all,
            bootstyle="warning-outline",
            width=15
        )
        deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttkb.Frame(dialog)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def import_selected():
            selected_students = [students_data[i] for i, var in checkboxes.items() if var.get()]
            if selected_students:
                self.apply_selected_students(selected_students)
                canvas.unbind_all("<MouseWheel>")  # Clean up binding
                dialog.destroy()
                messagebox.showinfo("Importación Exitosa", 
                                  f"Se importaron {len(selected_students)} estudiantes.", 
                                  parent=self)
            else:
                messagebox.showinfo("Importación", 
                                  "No se seleccionaron estudiantes para importar.", 
                                  parent=dialog)
        
        import_btn = ttkb.Button(
            action_frame,
            text="Importar Seleccionados",
            command=import_selected,
            bootstyle="success",
            width=20
        )
        import_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttkb.Button(
            action_frame,
            text="Cancelar",
            command=on_dialog_close,  # Use the cleanup function
            bootstyle="danger-outline",
            width=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def apply_selected_students(self, selected_students):
        """Apply selected student data to the form."""
        # Get available student slots (those without names)
        available_slots = []
        for slot_id in [str(i) for i in range(1, self.max_students + 1)]:
            if not self.participant_vars[slot_id]["apellido_nombre"].get().strip():
                available_slots.append(slot_id)
        
        # Import students into available slots
        imported_count = 0
        for student in selected_students:
            if imported_count >= len(available_slots):
                # No more slots available
                messagebox.showwarning(
                    "Límite alcanzado",
                    f"Solo se importaron {imported_count} de {len(selected_students)} estudiantes porque no hay más espacios disponibles.",
                    parent=self
                )
                break
            
            slot_id = available_slots[imported_count]
            for field, value in student.items():
                if field in self.participant_vars[slot_id]:
                    self.participant_vars[slot_id][field].set(value)
            
            imported_count += 1
        
        # Save data after import
        self.save_data()
    
    # --- Removed show_toast method if not needed or handled globally --- 
=======
        """Clear all form fields."""
        # Ask for confirmation
        if messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de que desea limpiar todos los campos?"
        ):
            # Clear all variables except positions
            for student_vars in self.student_data:
                for key, var in student_vars.items():
                    if key != 'position':
                        var.set('')
            
            # Show confirmation
            messagebox.showinfo("Limpieza", "Campos limpiados exitosamente")
>>>>>>> 05623bafcb4dd46d5d368abaece58d4cebd092c3
