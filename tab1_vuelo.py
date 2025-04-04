#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from datetime import datetime
import locale
from typing import Dict, Any
import json
import os
from tkinter import messagebox

class VueloTab(ttkb.Frame):
    """Tab for flight data, aligned with camara.mdc rules."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Data variables
        self.variables: Dict[str, tk.StringVar] = {}
        
        # Training archives data
        self.training_archives = {}
        self.load_training_archives()
        
        # Create the layout
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create the tab UI widgets based on rules."""
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        current_row = 0

        # Header
        header = ttkb.Label(
            self,
            text="Información del Entrenamiento",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=current_row, column=0, columnspan=4, sticky="w", pady=(0, 10))
        current_row += 1

        # Fecha
        self._create_field(current_row, 0, "Fecha:", "fecha")
        date_btn = ttkb.Button(
            self,
            text="Hoy",
            command=self.set_current_date,
            bootstyle="secondary-outline",
            width=5
        )
        date_btn.grid(row=current_row, column=2, padx=(0, 5), pady=5, sticky="w")
        
        # Vuelo del Año 
        self._create_field(current_row, 2, "Entrenamiento del Año:", "vuelo_del_ano", label_col_offset=1)
        current_row += 1

        # Vuelo Total
        self._create_field(current_row, 0, "Entrenamientos Totales:", "vuelo_total")
        # Curso
        self._create_field(current_row, 2, "Curso:", "curso", label_col_offset=1,
                           widget_type="combobox", 
                           values=["Primera vez", "Recurrente"])
        current_row += 1

        # Operador de Cámara
        self._create_field(current_row, 0, "Op. Cámara:", "operador_camara")
        # Operador RD
        self._create_field(current_row, 2, "Op. RD:", "operador_rd", label_col_offset=1)
        current_row += 1

        # Lector
        self._create_field(current_row, 0, "Lector:", "lector")
        # Observador de Registro
        self._create_field(current_row, 2, "Obs. Registro:", "observador_registro", label_col_offset=1)
        current_row += 1

        # Perfil de Cámara
        self._create_field(current_row, 0, "Perfil Cámara:", "perfil_camara",
                           widget_type="combobox", 
                           values=["IV-A", "Descompresión lenta"])
        # Alumnos (Number)
        self._create_field(current_row, 2, "Alumnos (No.):", "alumnos", label_col_offset=1)
        current_row += 1

        # Director Médico
        self._create_field(current_row, 0, "Director Médico:", "director_medico")
        # OE-4
        self._create_field(current_row, 2, "OE-4:", "oe_4", label_col_offset=1)
        current_row += 1
        
        # Jefe Técnico
        self._create_field(current_row, 0, "Jefe Técnico:", "jefe_tecnico")
        # OE-5
        self._create_field(current_row, 2, "OE-5:", "oe_5", label_col_offset=1)
        current_row += 1

        # Add a separator
        separator = ttkb.Separator(self, orient="horizontal")
        separator.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=10)
        current_row += 1

        # Add Training Archive section
        archive_frame = ttkb.LabelFrame(
            self,
            text="Archivo de Entrenamientos",
            padding=10,
            bootstyle="info"
        )
        archive_frame.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=5)
        self.create_archive_widgets(archive_frame)
        current_row += 1

        # Add padding below fields before buttons
        self.rowconfigure(current_row, weight=1)
        current_row += 1

        # Buttons section
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        
        save_btn = ttkb.Button(
            button_frame,
            text="Guardar Datos",
            command=self.save_data,
            bootstyle="success",
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        save_as_new_btn = ttkb.Button(
            button_frame,
            text="Guardar Como Nuevo",
            command=self.save_as_new_training,
            bootstyle="primary",
            width=20
        )
        save_as_new_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        clear_btn = ttkb.Button(
            button_frame,
            text="Limpiar Campos",
            command=self.clear_form,
            bootstyle="warning",
            width=15
        )
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def _create_field(self, row, label_column, label_text, var_name, 
                   widget_type="entry", values=None, width=25, label_col_offset=0):
        """Helper method to create a labeled field."""
        # Create label
        label = ttkb.Label(self, text=label_text)
        label.grid(row=row, column=label_column + label_col_offset, sticky="e", padx=5, pady=5)
        
        # Create variable
        self.variables[var_name] = tk.StringVar()
        
        # Create widget based on type
        if widget_type == "entry":
            widget = ttkb.Entry(self, textvariable=self.variables[var_name], width=width)
        elif widget_type == "combobox":
            widget = ttkb.Combobox(self, textvariable=self.variables[var_name], 
                                  values=values, width=width-3)
            widget.state(['readonly'])
        
        # Grid the widget
        widget.grid(row=row, column=label_column + label_col_offset + 1, sticky="ew", padx=5, pady=5)
        
        return widget
    
    def set_current_date(self):
        """Set the date field to today's date."""
        try:
            # Try to use Spanish locale for date format
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'es_ES')
            except locale.Error:
                pass
        
        # Get today's date
        today = datetime.now()
        
        # Format date based on locale
        try:
            date_str = today.strftime("%d de %B de %Y")
        except:
            # Fallback to basic format if locale formatting fails
            date_str = today.strftime("%d/%m/%Y")
        
        # Set the date variable
        self.variables['fecha'].set(date_str)
    
    def load_data(self):
        """Load data into the form fields."""
        # Get flight data from data manager
        flight_data = self.data_manager.current_data.get('vuelo', {})
        
        # Set values for each field
        for var_name, variable in self.variables.items():
            value = flight_data.get(var_name, '')
            variable.set(str(value))
        
        # If no date is set, set current date
        if not self.variables['fecha'].get():
            self.set_current_date()
    
    def save_data(self):
        """Save form data."""
        # Collect data from all variables
        flight_data = {}
        for var_name, variable in self.variables.items():
            flight_data[var_name] = variable.get()
        
        # Add timestamp
        flight_data['last_modified'] = datetime.now().isoformat()
        
        # Save to data manager
        self.data_manager.current_data['vuelo'] = flight_data
        self.data_manager.save_data()
        
        # Show success message
        messagebox.showinfo("Guardado", "Datos guardados exitosamente")
    
    def save_as_new_training(self):
        """Save current data as a new training record."""
        # First save current data
        self.save_data()
        
        # Get current data
        flight_data = self.data_manager.current_data.get('vuelo', {})
        
        # Update training numbers
        flight_data['vuelo_del_ano'] = str(self.get_next_training_year())
        flight_data['vuelo_total'] = str(self.get_next_total_trainings())
        
        # Save to archives
        self.save_to_training_archive(flight_data)
        
        # Update current form
        self.variables['vuelo_del_ano'].set(flight_data['vuelo_del_ano'])
        self.variables['vuelo_total'].set(flight_data['vuelo_total'])
        
        # Save updated data
        self.save_data()
        
        # Refresh the training list
        self.refresh_training_list()
        
        # Show success message
        messagebox.showinfo(
            "Nuevo Entrenamiento", 
            f"Entrenamiento guardado como:\nNº {flight_data['vuelo_total']} (Nº {flight_data['vuelo_del_ano']} del año)"
        )
    
    def get_next_training_year(self) -> int:
        """Calculate the next training number for the current year."""
        current_year = datetime.now().year
        max_number = 0
        
        # Check archives for trainings this year
        for training in self.training_archives.values():
            try:
                training_date = datetime.strptime(training['fecha'], "%d de %B de %Y")
            except ValueError:
                try:
                    training_date = datetime.strptime(training['fecha'], "%d/%m/%Y")
                except ValueError:
                    continue
                    
            if training_date.year == current_year:
                try:
                    number = int(training['vuelo_del_ano'])
                    max_number = max(max_number, number)
                except (ValueError, KeyError):
                    continue
        
        return max_number + 1
    
    def get_next_total_trainings(self) -> int:
        """Calculate the next total training number."""
        max_number = 0
        
        # Check all archives
        for training in self.training_archives.values():
            try:
                number = int(training['vuelo_total'])
                max_number = max(max_number, number)
            except (ValueError, KeyError):
                continue
        
        return max_number + 1
    
    def clear_form(self):
        """Clear all form fields."""
        # Ask for confirmation
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea limpiar todos los campos?"):
            # Clear all variables except date
            current_date = self.variables['fecha'].get()
            
            for var_name, variable in self.variables.items():
                if var_name != 'fecha':
                    variable.set('')
            
            # Restore date
            self.variables['fecha'].set(current_date)
            
            # Show confirmation
            messagebox.showinfo("Limpieza", "Campos limpiados exitosamente")
    
    def load_training_archives(self):
        """Load archived training data."""
        archive_path = os.path.join(os.path.dirname(__file__), 'data', 'training_archives.json')
        
        if os.path.exists(archive_path):
            try:
                with open(archive_path, 'r', encoding='utf-8') as f:
                    self.training_archives = json.load(f)
            except Exception as e:
                print(f"Error loading training archives: {e}")
                self.training_archives = {}
        else:
            self.training_archives = {}
    
    def save_to_training_archive(self, training_data: Dict[str, Any]) -> None:
        """Save a training record to the archives."""
        # Create a unique ID for the training
        training_id = f"training_{len(self.training_archives) + 1}"
        
        # Add metadata
        training_data['id'] = training_id
        training_data['archived_at'] = datetime.now().isoformat()
        
        # Add to archives
        self.training_archives[training_id] = training_data
        
        # Save archives
        self.save_training_archives()
    
    def save_training_archives(self):
        """Save the training archives to file."""
        archive_path = os.path.join(os.path.dirname(__file__), 'data', 'training_archives.json')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        try:
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(self.training_archives, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving training archives: {e}")
            messagebox.showerror(
                "Error", 
                "No se pudieron guardar los archivos de entrenamiento"
            )
    
    def refresh_training_list(self):
        """Refresh the list of trainings in the archive section."""
        # Clear existing widgets in trainings container
        for widget in self.trainings_container.winfo_children():
            widget.destroy()
        
        # Sort trainings by date (newest first)
        sorted_trainings = sorted(
            self.training_archives.items(),
            key=lambda x: x[1].get('archived_at', ''),
            reverse=True
        )
        
        # Create a frame for each training
        for training_id, training_data in sorted_trainings:
            training_frame = ttkb.Frame(self.trainings_container)
            training_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Format date for display
            try:
                date = training_data.get('fecha', 'Fecha desconocida')
                training_num = training_data.get('vuelo_total', 'N/A')
                year_num = training_data.get('vuelo_del_ano', 'N/A')
                
                display_text = f"Entrenamiento Nº {training_num} ({year_num} del año) - {date}"
            except Exception:
                display_text = f"Entrenamiento {training_id}"
            
            # Add label
            label = ttkb.Label(
                training_frame,
                text=display_text,
                cursor="hand2"
            )
            label.pack(side=tk.LEFT, padx=5)
            
            # Bind click event
            label.bind('<Button-1>', lambda e, tid=training_id: self.load_training(tid))
            
            # Add hover effect
            def on_enter(e):
                e.widget.configure(font=('Segoe UI', 9, 'underline'))
            
            def on_leave(e):
                e.widget.configure(font=('Segoe UI', 9))
            
            label.bind('<Enter>', on_enter)
            label.bind('<Leave>', on_leave)
    
    def load_training(self, training_id):
        """Load a training record from the archives."""
        # Ask for confirmation if current data exists
        current_data = any(var.get() for var in self.variables.values())
        if current_data:
            if not messagebox.askyesno(
                "Confirmar",
                "¿Está seguro de que desea cargar este entrenamiento? " +
                "Los datos actuales serán reemplazados."
            ):
                return
        
        # Get training data
        training_data = self.training_archives.get(training_id)
        if not training_data:
            messagebox.showerror(
                "Error",
                "No se pudo encontrar el entrenamiento seleccionado"
            )
            return
        
        # Load data into form
        for var_name, variable in self.variables.items():
            value = training_data.get(var_name, '')
            variable.set(str(value))
        
        # Save to current data
        self.save_data()
        
        # Show confirmation
        messagebox.showinfo(
            "Carga Exitosa",
            "Entrenamiento cargado exitosamente"
        )
    
    def search_by_date(self):
        """Search trainings by date."""
        search_date = self.date_search_var.get().strip()
        if not search_date:
            messagebox.showwarning(
                "Búsqueda",
                "Por favor ingrese una fecha para buscar"
            )
            return
        
        # Try different date formats
        found_trainings = []
        for training_id, training in self.training_archives.items():
            training_date = training.get('fecha', '').strip().lower()
            
            # Try exact match first
            if search_date.lower() in training_date:
                found_trainings.append((training_id, training))
                continue
            
            # Try to parse and compare dates
            try:
                # Parse search date (assuming dd/mm/yyyy format)
                search_dt = datetime.strptime(search_date, "%d/%m/%Y")
                
                # Try parsing training date in different formats
                for fmt in ["%d de %B de %Y", "%d/%m/%Y"]:
                    try:
                        training_dt = datetime.strptime(training_date, fmt)
                        if training_dt.date() == search_dt.date():
                            found_trainings.append((training_id, training))
                            break
                    except ValueError:
                        continue
            except ValueError:
                # If search date can't be parsed, continue with text search
                continue
        
        if not found_trainings:
            messagebox.showinfo(
                "Búsqueda",
                "No se encontraron entrenamientos para la fecha especificada"
            )
            return
        
        # Clear and show results
        for widget in self.trainings_container.winfo_children():
            widget.destroy()
        
        # Sort found trainings by date (newest first)
        found_trainings.sort(key=lambda x: x[1].get('archived_at', ''), reverse=True)
        
        # Show results
        for training_id, training in found_trainings:
            training_frame = ttkb.Frame(self.trainings_container)
            training_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Format display text
            date = training.get('fecha', 'Fecha desconocida')
            training_num = training.get('vuelo_total', 'N/A')
            year_num = training.get('vuelo_del_ano', 'N/A')
            
            display_text = f"Entrenamiento Nº {training_num} ({year_num} del año) - {date}"
            
            # Add label
            label = ttkb.Label(
                training_frame,
                text=display_text,
                cursor="hand2"
            )
            label.pack(side=tk.LEFT, padx=5)
            
            # Bind click event
            label.bind('<Button-1>', lambda e, tid=training_id: self.load_training(tid))
            
            # Add hover effect
            def on_enter(e):
                e.widget.configure(font=('Segoe UI', 9, 'underline'))
            
            def on_leave(e):
                e.widget.configure(font=('Segoe UI', 9))
            
            label.bind('<Enter>', on_enter)
            label.bind('<Leave>', on_leave)
    
    def search_by_training(self):
        """Search trainings by training number."""
        search_num = self.training_search_var.get().strip()
        if not search_num:
            messagebox.showwarning(
                "Búsqueda",
                "Por favor ingrese un número de entrenamiento para buscar"
            )
            return
        
        # Search in both total and year numbers
        found_trainings = []
        for training_id, training in self.training_archives.items():
            total_num = str(training.get('vuelo_total', '')).strip()
            year_num = str(training.get('vuelo_del_ano', '')).strip()
            
            if search_num in total_num or search_num in year_num:
                found_trainings.append((training_id, training))
        
        if not found_trainings:
            messagebox.showinfo(
                "Búsqueda",
                "No se encontraron entrenamientos con el número especificado"
            )
            return
        
        # Clear and show results
        for widget in self.trainings_container.winfo_children():
            widget.destroy()
        
        # Sort found trainings by date (newest first)
        found_trainings.sort(key=lambda x: x[1].get('archived_at', ''), reverse=True)
        
        # Show results
        for training_id, training in found_trainings:
            training_frame = ttkb.Frame(self.trainings_container)
            training_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Format display text
            date = training.get('fecha', 'Fecha desconocida')
            training_num = training.get('vuelo_total', 'N/A')
            year_num = training.get('vuelo_del_ano', 'N/A')
            
            display_text = f"Entrenamiento Nº {training_num} ({year_num} del año) - {date}"
            
            # Add label
            label = ttkb.Label(
                training_frame,
                text=display_text,
                cursor="hand2"
            )
            label.pack(side=tk.LEFT, padx=5)
            
            # Bind click event
            label.bind('<Button-1>', lambda e, tid=training_id: self.load_training(tid))
            
            # Add hover effect
            def on_enter(e):
                e.widget.configure(font=('Segoe UI', 9, 'underline'))
            
            def on_leave(e):
                e.widget.configure(font=('Segoe UI', 9))
            
            label.bind('<Enter>', on_enter)
            label.bind('<Leave>', on_leave)