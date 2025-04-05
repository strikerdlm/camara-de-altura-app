#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
import locale
from datetime import datetime

class VueloTab(ttkb.Frame):
    """Tab for managing flight data."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Create variables for form fields
        self.variables = {}
        self.create_variables()
        
        # Training archives data
        self.training_archives = {}
        self.load_training_archives()
        
        # Create the layout
        self.create_widgets()
        self.load_data()
    
    def create_variables(self):
        """Create variables for form fields."""
        # Flight data
        self.variables['fecha'] = tk.StringVar()
        self.variables['hora_inicio'] = tk.StringVar()
        self.variables['hora_fin'] = tk.StringVar()
        self.variables['tipo_vuelo'] = tk.StringVar()
        self.variables['altura_inicial'] = tk.StringVar()
        self.variables['altura_final'] = tk.StringVar()
        self.variables['tiempo_ascenso'] = tk.StringVar()
        self.variables['tiempo_estadia'] = tk.StringVar()
        self.variables['tiempo_descenso'] = tk.StringVar()
        self.variables['tiempo_total'] = tk.StringVar()
        self.variables['observaciones'] = tk.StringVar()
        
        # Pilot data
        self.variables['piloto_nombre'] = tk.StringVar()
        self.variables['piloto_grado'] = tk.StringVar()
        self.variables['piloto_unidad'] = tk.StringVar()
        
        # Operator data
        self.variables['operador_nombre'] = tk.StringVar()
        self.variables['operador_grado'] = tk.StringVar()
        self.variables['operador_unidad'] = tk.StringVar()
        
        # Additional variables for advanced functionality
        self.variables['vuelo_del_ano'] = tk.StringVar()
        self.variables['vuelo_total'] = tk.StringVar()
        self.variables['curso'] = tk.StringVar()
        self.variables['operador_camara'] = tk.StringVar()
        self.variables['operador_rd'] = tk.StringVar()
        self.variables['lector'] = tk.StringVar()
        self.variables['observador_registro'] = tk.StringVar()
        self.variables['perfil_camara'] = tk.StringVar()
        self.variables['alumnos'] = tk.StringVar()
        self.variables['director_medico'] = tk.StringVar()
        self.variables['oe_4'] = tk.StringVar()
        self.variables['jefe_tecnico'] = tk.StringVar()
        self.variables['oe_5'] = tk.StringVar()
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Header
        header = ttkb.Label(
            self,
            text="Información del Entrenamiento",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Flight data section
        flight_frame = ttkb.Labelframe(
            self,
            text="Datos del Vuelo",
            padding=10
        )
        flight_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        flight_frame.columnconfigure(1, weight=1)
        flight_frame.columnconfigure(3, weight=1)
        
        # Setup row counters
        current_row = 0
        
        # Vuelo del Año 
        self._create_field(current_row, 2, "Entrenamiento del Año:", "vuelo_del_ano", label_col_offset=1)
        current_row += 1

        # -- Row 2 --
        # Vuelo Total
        self._create_field(current_row, 0, "Entrenamientos Totales:", "vuelo_total")
        # Curso
        self._create_field(current_row, 2, "Curso:", "curso", label_col_offset=1,
                           widget_type="combobox", 
                           values=["Primera vez", "Recurrente"])
        current_row += 1

        # -- Row 3 --
        # Operador de Cámara
        self._create_field(current_row, 0, "Op. Cámara:", "operador_camara")
        # Operador RD
        self._create_field(current_row, 2, "Op. RD:", "operador_rd", label_col_offset=1)
        current_row += 1

        # -- Row 4 --
        # Lector
        self._create_field(current_row, 0, "Lector:", "lector")
        # Observador de Registro
        self._create_field(current_row, 2, "Obs. Registro:", "observador_registro", label_col_offset=1)
        current_row += 1

        # -- Row 5 --
        # Perfil de Cámara
        self._create_field(current_row, 0, "Perfil Cámara:", "perfil_camara",
                           widget_type="combobox", 
                           values=["IV-A", "Descompresión lenta"])
        # Alumnos (Number)
        # For simplicity, using Entry. Add validation later if needed.
        self._create_field(current_row, 2, "Alumnos (No.):", "alumnos", label_col_offset=1)
        current_row += 1

        # -- Row 6 --
        # Director Médico
        self._create_field(current_row, 0, "Director Médico:", "director_medico")
        # OE-4
        self._create_field(current_row, 2, "OE-4:", "oe_4", label_col_offset=1)
        current_row += 1
        
        # -- Row 7 --
        # Jefe Técnico
        self._create_field(current_row, 0, "Jefe Técnico:", "jefe_tecnico")
        # OE-5
        self._create_field(current_row, 2, "OE-5:", "oe_5", label_col_offset=1)
        current_row += 1

        # Add a separator for visual clarity before the archive section
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
        self.rowconfigure(current_row, weight=1) # Add spacer row
        current_row += 1

        # Buttons section
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew")
        
        save_btn = ttkb.Button(
            button_frame,
            text="Guardar Datos",
            command=self.save_data,
            bootstyle="success",
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
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
        
    def create_archive_widgets(self, parent):
        """Create widgets for browsing and loading past trainings."""
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        
        # Row 0: Search options
        search_frame = ttkb.Frame(parent)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        
        # By Date
        date_label = ttkb.Label(search_frame, text="Buscar por Fecha:")
        date_label.pack(side=tk.LEFT, padx=5)
        
        self.date_search_var = tk.StringVar()
        date_entry = ttkb.Entry(search_frame, textvariable=self.date_search_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        date_search_btn = ttkb.Button(
            search_frame,
            text="Buscar",
            command=self.search_by_date,
            bootstyle="info-outline",
            width=8
        )
        date_search_btn.pack(side=tk.LEFT, padx=5)
        
        # By Training Number
        training_label = ttkb.Label(search_frame, text="Buscar por Entrenamiento Nº:")
        training_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.training_search_var = tk.StringVar()
        training_entry = ttkb.Entry(search_frame, textvariable=self.training_search_var, width=5)
        training_entry.pack(side=tk.LEFT, padx=5)
        
        training_search_btn = ttkb.Button(
            search_frame,
            text="Buscar",
            command=self.search_by_training,
            bootstyle="info-outline",
            width=8
        )
        training_search_btn.pack(side=tk.LEFT, padx=5)
        
        # Row 1: Training List
        list_frame = ttkb.Frame(parent)
        list_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        list_label = ttkb.Label(list_frame, text="Entrenamientos Guardados:", font=('Segoe UI', 10, 'bold'))
        list_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        # Create a frame with scrollbar for the training list
        training_list_frame = ttkb.Frame(parent)
        training_list_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
        training_list_frame.columnconfigure(0, weight=1)
        training_list_frame.rowconfigure(0, weight=1)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(training_list_frame, height=150)
        scrollbar = ttkb.Scrollbar(training_list_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Create a frame inside the canvas to hold the training entries
        self.trainings_container = ttkb.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.trainings_container, anchor="nw")
        
        # Make the training container frame expand to the width of the canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Update the scroll region when the size of the trainings_container changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.trainings_container.bind("<Configure>", on_frame_configure)
        
        # Row 3: Action buttons
        action_frame = ttkb.Frame(parent)
        action_frame.grid(row=3, column=0, columnspan=2, sticky="e", pady=5)
        
        refresh_btn = ttkb.Button(
            action_frame,
            text="Actualizar Lista",
            command=self.refresh_training_list,
            bootstyle="secondary",
            width=15
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
    def _create_field(self, row, label_column, label_text, var_name, 
                   widget_type="entry", values=None, width=25, label_col_offset=0):
        """Helper to create a label and input widget in the grid."""
        # Create label
        label = ttkb.Label(self, text=label_text)
        # Adjust label column if offset is specified
        actual_label_column = label_column + label_col_offset 
        label.grid(row=row, column=actual_label_column, padx=(15,5), pady=5, sticky="e")
        
        # Create variable if not already created
        if var_name not in self.variables:
            self.variables[var_name] = tk.StringVar()
        
        # Determine widget column
        widget_column = actual_label_column + 1

        # Create input widget
        if widget_type == "entry":
            widget = ttkb.Entry(self, textvariable=self.variables[var_name], width=width)
        elif widget_type == "combobox":
            widget = ttkb.Combobox(
                self,
                textvariable=self.variables[var_name],
                values=values if values else [],
                width=width - 2, # Combobox width is slightly different
                state="readonly"
            )
            if values and not self.variables[var_name].get(): # Set default value for combobox if empty
                self.variables[var_name].set(values[0]) 
        else:
            # Fallback for unknown types
            widget = ttkb.Label(self, text=f"Unknown widget: {widget_type}")

        widget.grid(row=row, column=widget_column, padx=5, pady=5, sticky="we") # Use sticky 'we' to expand
        
        return widget
    
    def set_current_date(self):
        """Set current date in the date field using Spanish locale format if possible."""
        try:
            # Attempt to use Spanish locale for format DD/MM/YYYY
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8') # Or 'es_ES' or appropriate Spanish locale
            today_str = datetime.now().strftime("%d/%m/%Y")
        except locale.Error:
            # Fallback to ISO format if locale fails
             today_str = datetime.now().strftime("%Y-%m-%d")
        finally:
             # Reset locale to default if needed, though often not necessary per field
             # locale.setlocale(locale.LC_TIME, '') 
             pass

        if "fecha" in self.variables:
             self.variables["fecha"].set(today_str)
        else:
             print("Error: 'fecha' variable not found.")
    
    def load_data(self):
        """Load flight data into the form fields."""
        # Get flight data from data manager
        flight_data = self.data_manager.current_data.get('vuelo', {})
        
        # Load data into variables
        for var_name, var in self.variables.items():
            var.set(flight_data.get(var_name, ''))
    
    def save_data(self):
        """Save form data."""
        # Collect data from all variables
        vuelo_data = {}
        for var_name, var in self.variables.items():
            vuelo_data[var_name] = var.get()
        
        # Save under the consistent key 'vuelo'
        self.data_manager.current_data['vuelo'] = vuelo_data
        # Assume data_manager.save_data() saves the entire current_data structure
        try:
            self.data_manager.save_data()
            
            # Also save to the archives
            self.save_to_training_archive(vuelo_data)
            
            print("Datos del vuelo guardados.")
            messagebox.showinfo("Guardado Exitoso", "Datos del entrenamiento guardados correctamente.")
        except Exception as e:
             print(f"Error saving flight data: {e}")
             messagebox.showerror("Error", f"Error al guardar datos: {e}")
    
    def save_as_new_training(self):
        """Save the current data as a new training entry."""
        # Increment the training numbers
        training_year = self.get_next_training_year()
        total_trainings = self.get_next_total_trainings()
        
        # Update the UI
        self.variables['vuelo_del_ano'].set(str(training_year))
        self.variables['vuelo_total'].set(str(total_trainings))
        
        # Save with new numbers
        self.save_data()
        
    def get_next_training_year(self):
        """Get the next training number for the current year."""
        current_year = datetime.now().year
        max_num = 0
        
        for training_id, training in self.training_archives.items():
            try:
                # Extract year from the date
                training_date = training.get('fecha', '')
                # Try different date formats to get the year
                try:
                    # Try DD/MM/YYYY format
                    training_year = datetime.strptime(training_date, "%d/%m/%Y").year
                except ValueError:
                    try:
                        # Try YYYY-MM-DD format
                        training_year = datetime.strptime(training_date, "%Y-%m-%d").year
                    except ValueError:
                        # Skip if date format is invalid
                        continue
                
                # If it's for the current year, check its number
                if training_year == current_year:
                    try:
                        training_num = int(training.get('vuelo_del_ano', '0'))
                        max_num = max(max_num, training_num)
                    except ValueError:
                        continue
            except:
                continue
                
        return max_num + 1
    
    def get_next_total_trainings(self):
        """Get the next total training number."""
        max_num = 0
        
        for training_id, training in self.training_archives.items():
            try:
                training_num = int(training.get('vuelo_total', '0'))
                max_num = max(max_num, training_num)
            except ValueError:
                continue
                
        return max_num + 1
    
    def clear_form(self):
        """Clear all fields managed by self.variables."""
        # Ask for confirmation
        if messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de que desea limpiar todos los campos?"
        ):
            for field_name, var in self.variables.items():
                # Reset to empty string, except for comboboxes which get default
                if field_name == 'perfil_camara':
                    var.set("IV-A")
                elif field_name == 'curso':
                    var.set("Primera vez")
                else:
                    var.set('')
            
            # Set date to today on clear
            self.set_current_date()
            
            # Show confirmation
            messagebox.showinfo("Limpieza", "Campos limpiados exitosamente")
        
    def load_training_archives(self):
        """Load saved training archives from JSON file."""
        try:
            # Check if archives directory exists, create if not
            archives_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'archives')
            os.makedirs(archives_dir, exist_ok=True)
            
            # Path to the training archives file
            archives_file = os.path.join(archives_dir, 'training_archives.json')
            
            # If file exists, load data
            if os.path.exists(archives_file):
                with open(archives_file, 'r', encoding='utf-8') as f:
                    self.training_archives = json.load(f)
            else:
                self.training_archives = {}
                
            # Refresh the UI if it's been created
            if hasattr(self, 'trainings_container'):
                self.refresh_training_list()
                
        except Exception as e:
            print(f"Error loading training archives: {e}")
            self.training_archives = {}
    
    def save_to_training_archive(self, training_data):
        """Save the current training data to the archives."""
        try:
            # Get date and training number to generate a unique ID
            date = training_data.get('fecha', datetime.now().strftime("%d/%m/%Y"))
            training_year = training_data.get('vuelo_del_ano', '0')
            
            # Create a unique ID for this training
            training_id = f"{date}_{training_year}"
            
            # Add timestamp for sorting
            training_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to archives dictionary
            self.training_archives[training_id] = training_data
            
            # Save archives to JSON file
            self.save_training_archives()
            
            # Refresh the training list
            self.refresh_training_list()
            
        except Exception as e:
            print(f"Error saving to training archive: {e}")
    
    def save_training_archives(self):
        """Save the training archives to JSON file."""
        try:
            # Check if archives directory exists, create if not
            archives_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'archives')
            os.makedirs(archives_dir, exist_ok=True)
            
            # Path to the training archives file
            archives_file = os.path.join(archives_dir, 'training_archives.json')
            
            # Save data to JSON file
            with open(archives_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_archives, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"Error saving training archives: {e}")
    
    def refresh_training_list(self):
        """Refresh the training list in the UI."""
        # Clear all existing entries in the container
        for widget in self.trainings_container.winfo_children():
            widget.destroy()
        
        # If no archives, show message
        if not self.training_archives:
            empty_label = ttkb.Label(
                self.trainings_container,
                text="No hay entrenamientos guardados",
                font=('Segoe UI', 10, 'italic'),
                foreground="gray"
            )
            empty_label.pack(pady=10)
            return
            
        # Sort trainings by timestamp (newest first)
        sorted_trainings = []
        for training_id, training_data in self.training_archives.items():
            sorted_trainings.append((training_id, training_data))
            
        # Sort by timestamp or date if available
        sorted_trainings.sort(
            key=lambda x: x[1].get('timestamp', x[1].get('fecha', '')), 
            reverse=True
        )
        
        # Add each training to the list
        for training_id, training_data in sorted_trainings:
            training_frame = ttkb.Frame(self.trainings_container)
            training_frame.pack(fill="x", padx=5, pady=2)
            
            # Format the display text
            date = training_data.get('fecha', 'Sin fecha')
            training_num = training_data.get('vuelo_del_ano', '?')
            total_num = training_data.get('vuelo_total', '?')
            
            display_text = f"Fecha: {date} | Entrenamiento: #{training_num} | Total: #{total_num}"
            
            # Add operador_camara if available
            if 'operador_camara' in training_data and training_data['operador_camara']:
                display_text += f" | Op. Cámara: {training_data['operador_camara']}"
            
            training_label = ttkb.Label(
                training_frame,
                text=display_text,
                font=('Segoe UI', 9)
            )
            training_label.pack(side=tk.LEFT, fill="x", expand=True, anchor="w")
            
            # Add load button
            load_btn = ttkb.Button(
                training_frame,
                text="Cargar",
                command=lambda t_id=training_id: self.load_training(t_id),
                bootstyle="info-outline",
                width=8
            )
            load_btn.pack(side=tk.RIGHT, padx=5)
    
    def load_training(self, training_id):
        """Load a specific training from the archives into the form."""
        # Check if training exists
        if training_id not in self.training_archives:
            messagebox.showerror("Error", f"No se encontró el entrenamiento con ID {training_id}")
            return
            
        # Get the training data
        training_data = self.training_archives[training_id]
        
        # Confirm loading
        confirm = messagebox.askyesno(
            "Cargar Entrenamiento",
            "¿Está seguro que desea cargar este entrenamiento? Se perderán los datos no guardados.",
            icon="question"
        )
        
        if not confirm:
            return
            
        # Update form fields
        for field_name, var in self.variables.items():
            if field_name in training_data:
                var.set(training_data[field_name])
        
        # Update current data in data_manager
        self.data_manager.current_data['vuelo'] = training_data.copy()
        
        # Save to current file
        try:
            self.data_manager.save_data()
            messagebox.showinfo("Carga Exitosa", "Entrenamiento cargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar los datos cargados: {e}")
    
    def search_by_date(self):
        """Search for trainings by date."""
        search_date = self.date_search_var.get().strip()
        if not search_date:
            messagebox.showinfo("Búsqueda", "Por favor ingrese una fecha para buscar.")
            return
            
        # Clear all existing entries in the container
        for widget in self.trainings_container.winfo_children():
            widget.destroy()
            
        # Filter trainings by date
        found = False
        for training_id, training_data in self.training_archives.items():
            date = training_data.get('fecha', '')
            if search_date in date:
                found = True
                
                # Create frame for this training
                training_frame = ttkb.Frame(self.trainings_container)
                training_frame.pack(fill="x", padx=5, pady=2)
                
                # Format the display text
                training_num = training_data.get('vuelo_del_ano', '?')
                total_num = training_data.get('vuelo_total', '?')
                
                display_text = f"Fecha: {date} | Entrenamiento: #{training_num} | Total: #{total_num}"
                
                # Add operador_camara if available
                if 'operador_camara' in training_data and training_data['operador_camara']:
                    display_text += f" | Op. Cámara: {training_data['operador_camara']}"
                
                training_label = ttkb.Label(
                    training_frame,
                    text=display_text,
                    font=('Segoe UI', 9)
                )
                training_label.pack(side=tk.LEFT, fill="x", expand=True, anchor="w")
                
                # Add load button
                load_btn = ttkb.Button(
                    training_frame,
                    text="Cargar",
                    command=lambda t_id=training_id: self.load_training(t_id),
                    bootstyle="info-outline",
                    width=8
                )
                load_btn.pack(side=tk.RIGHT, padx=5)
        
        if not found:
            empty_label = ttkb.Label(
                self.trainings_container,
                text=f"No se encontraron entrenamientos con fecha '{search_date}'",
                font=('Segoe UI', 10, 'italic'),
                foreground="gray"
            )
            empty_label.pack(pady=10)
    
    def search_by_training(self):
        """Search for trainings by training number."""
        search_num = self.training_search_var.get().strip()
        if not search_num:
            messagebox.showinfo("Búsqueda", "Por favor ingrese un número de entrenamiento para buscar.")
            return
            
        # Clear all existing entries in the container
        for widget in self.trainings_container.winfo_children():
            widget.destroy()
            
        # Filter trainings by number
        found = False
        for training_id, training_data in self.training_archives.items():
            training_num = str(training_data.get('vuelo_del_ano', ''))
            if search_num == training_num:
                found = True
                
                # Create frame for this training
                training_frame = ttkb.Frame(self.trainings_container)
                training_frame.pack(fill="x", padx=5, pady=2)
                
                # Format the display text
                date = training_data.get('fecha', 'Sin fecha')
                total_num = training_data.get('vuelo_total', '?')
                
                display_text = f"Fecha: {date} | Entrenamiento: #{training_num} | Total: #{total_num}"
                
                # Add operador_camara if available
                if 'operador_camara' in training_data and training_data['operador_camara']:
                    display_text += f" | Op. Cámara: {training_data['operador_camara']}"
                
                training_label = ttkb.Label(
                    training_frame,
                    text=display_text,
                    font=('Segoe UI', 9)
                )
                training_label.pack(side=tk.LEFT, fill="x", expand=True, anchor="w")
                
                # Add load button
                load_btn = ttkb.Button(
                    training_frame,
                    text="Cargar",
                    command=lambda t_id=training_id: self.load_training(t_id),
                    bootstyle="info-outline",
                    width=8
                )
                load_btn.pack(side=tk.RIGHT, padx=5)
        
        if not found:
            empty_label = ttkb.Label(
                self.trainings_container,
                text=f"No se encontraron entrenamientos con número '{search_num}'",
                font=('Segoe UI', 10, 'italic'),
                foreground="gray"
            )
            empty_label.pack(pady=10)

# Ensure imports are correct
# Ensure AppConfig/DataManager are passed correctly during instantiation
# Ensure ttkbootstrap is installed 
