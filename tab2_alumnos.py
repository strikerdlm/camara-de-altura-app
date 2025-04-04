#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, List, Any
import json
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
        clear_btn.pack(side=tk.RIGHT, padx=5)
    
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
