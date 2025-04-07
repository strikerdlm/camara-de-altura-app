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
from ttkbootstrap.scrolled import ScrolledFrame

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
        
        # Load data or set default date if no data
        if not self.load_data():
            # If no data was loaded, set the current date
            self.set_current_date()
    
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
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Header row
        self.rowconfigure(1, weight=0)  # Date display row
        self.rowconfigure(2, weight=1)  # Main content - will expand with window
        
        # Header - moved down with more padding to avoid overlap with tab navigation
        header = ttkb.Label(
            self,
            text="Datos del entrenamiento de hipoxia hipobárica",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(15, 20))
        
        # Add date display prominently at the top
        date_frame = ttkb.Frame(self, padding=10)
        date_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        date_label = ttkb.Label(
            date_frame,
            text="Fecha del entrenamiento:",
            font=('Segoe UI', 11),  # Match font size with other fields
            bootstyle="info"
        )
        date_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create date display field
        if "fecha" not in self.variables:
            self.variables['fecha'] = tk.StringVar()
        
        date_display = ttkb.Entry(
            date_frame,
            textvariable=self.variables['fecha'],
            font=('Segoe UI', 11),  # Match font size with other fields
            width=15
        )
        date_display.pack(side=tk.LEFT, padx=5)
        
        # Add a small instruction label about date format
        format_label = ttkb.Label(
            date_frame,
            text="(DD-MM-AAAA)",
            font=('Segoe UI', 9),
            bootstyle="secondary"
        )
        format_label.pack(side=tk.LEFT, padx=5)
        
        # Add button to set current date
        set_date_btn = ttkb.Button(
            date_frame,
            text="Hoy",
            command=self.set_current_date,
            bootstyle="info-outline",
            width=6
        )
        set_date_btn.pack(side=tk.LEFT, padx=10)

        # Create a frame for the main content
        main_content_frame = ttkb.Frame(self)
        main_content_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.rowconfigure(0, weight=1)
        
        # Create a canvas with scrollbars for the main content instead of using ScrolledFrame
        main_canvas = tk.Canvas(main_content_frame)
        y_scrollbar = ttkb.Scrollbar(main_content_frame, orient="vertical", command=main_canvas.yview)
        x_scrollbar = ttkb.Scrollbar(main_content_frame, orient="horizontal", command=main_canvas.xview)
        
        # Configure the canvas scrolling
        main_canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid layout for canvas and scrollbars
        main_canvas.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Create a frame inside the canvas to hold the form content
        self.main_frame = ttkb.Frame(main_canvas, padding=10)
        self.canvas_window = main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        # Configure the main_frame grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.columnconfigure(3, weight=1)
        
        # Make the content frame expand to fill the canvas width
        def on_canvas_configure(event):
            main_canvas.itemconfig(self.canvas_window, width=event.width)
        
        main_canvas.bind("<Configure>", on_canvas_configure)
        
        # Update the scroll region when the size of the main_frame changes
        def on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        self.main_frame.bind("<Configure>", on_frame_configure)
        
        # Add mousewheel scrolling for the main canvas
        def _on_mousewheel(event):
            # Handle different platform scroll events
            if event.delta:
                # Windows
                main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # Linux, macOS
                if event.num == 4:
                    main_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    main_canvas.yview_scroll(1, "units")
        
        # Bind mousewheel events to the canvas
        main_canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        main_canvas.bind("<Button-4>", _on_mousewheel)    # Linux up
        main_canvas.bind("<Button-5>", _on_mousewheel)    # Linux down
        
        # Store references for cleanup
        self.main_canvas = main_canvas
        self.main_bindings = [
            (main_canvas, "<Configure>", on_canvas_configure),
            (self.main_frame, "<Configure>", on_frame_configure),
            (main_canvas, "<MouseWheel>", _on_mousewheel),
            (main_canvas, "<Button-4>", _on_mousewheel),
            (main_canvas, "<Button-5>", _on_mousewheel)
        ]
        
        # Setup row counter for main_frame
        current_row = 0
        
        # -- Row 1 --
        # Entrenamientos Totales (number field, smaller width)
        self._create_field(self.main_frame, current_row, 0, "Entrenamientos Totales:", "vuelo_total", width=15)
        # Entrenamiento del Año (number field, smaller width)
        self._create_field(self.main_frame, current_row, 2, "Entrenamiento del Año:", "vuelo_del_ano", width=15, label_col_offset=1)
        current_row += 1

        # -- Row 2 --
        # Curso
        self._create_field(self.main_frame, current_row, 0, "Curso:", "curso", 
                           widget_type="combobox", 
                           values=["Primera vez", "Recurrente"])
        # Perfil de Cámara
        self._create_field(self.main_frame, current_row, 2, "Perfil Cámara:", "perfil_camara", 
                           widget_type="combobox", 
                           values=["IV-A", "Descompresión lenta"],
                           label_col_offset=1)
        current_row += 1

        # -- Row 3 --
        # Alumnos (Number, smaller width)
        self._create_field(self.main_frame, current_row, 0, "Alumnos (No.):", "alumnos", width=15)
        current_row += 1

        # Separator for crew section
        separator = ttkb.Separator(self.main_frame, orient="horizontal")
        separator.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=10)
        current_row += 1
        
        # Crew section header
        crew_header = ttkb.Label(
            self.main_frame,
            text="Tripulación",
            font=('Segoe UI', 11, 'bold'),
            bootstyle="info"
        )
        crew_header.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(5, 10))
        current_row += 1

        # -- Row 5 --
        # Director Médico
        self._create_field(self.main_frame, current_row, 0, "Director Médico:", "director_medico", width=35)
        # Jefe Técnico
        self._create_field(self.main_frame, current_row, 2, "Jefe Técnico:", "jefe_tecnico", width=35, label_col_offset=1)
        current_row += 1
        
        # -- Row 6 --
        # Operador de Cámara (renamed from Op. Cámara)
        self._create_field(self.main_frame, current_row, 0, "Operador de Cámara:", "operador_camara", width=35)
        # Registro (renamed from Obs. Registro)
        self._create_field(self.main_frame, current_row, 2, "Registro:", "observador_registro", width=35, label_col_offset=1)
        current_row += 1

        # -- Row 7 --
        # Lector
        self._create_field(self.main_frame, current_row, 0, "Lector:", "lector", width=35)
        # Operador RD (renamed from Op. RD)
        self._create_field(self.main_frame, current_row, 2, "Operador RD:", "operador_rd", width=35, label_col_offset=1)
        current_row += 1

        # -- Row 8 --
        # OE-4
        self._create_field(self.main_frame, current_row, 0, "OE-4:", "oe_4", width=35)
        # OE-5
        self._create_field(self.main_frame, current_row, 2, "OE-5:", "oe_5", width=35, label_col_offset=1)
        current_row += 1

        # Add a separator for visual clarity before the archive section
        separator = ttkb.Separator(self.main_frame, orient="horizontal")
        separator.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=10)
        current_row += 1

        # Add Training Archive section
        archive_frame = ttkb.LabelFrame(
            self.main_frame,
            text="Archivo de Entrenamientos",
            padding=10,
            bootstyle="info"
        )
        archive_frame.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=5)
        self.create_archive_widgets(archive_frame)
        current_row += 1

        # Add padding below fields before buttons
        self.main_frame.rowconfigure(current_row, weight=1) # Add spacer row
        current_row += 1

        # Buttons section
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        
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
        
        # Create a scrollable frame for the training list - using traditional Canvas+Scrollbar
        training_list_frame = ttkb.Frame(parent)
        training_list_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=5)
        training_list_frame.columnconfigure(0, weight=1)
        training_list_frame.rowconfigure(0, weight=1)
        
        # Create a canvas with scrollbar
        self.archive_canvas = tk.Canvas(training_list_frame, height=150)
        scrollbar = ttkb.Scrollbar(training_list_frame, orient="vertical", command=self.archive_canvas.yview)
        self.archive_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.archive_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Create a frame inside the canvas to hold the training entries
        self.trainings_container = ttkb.Frame(self.archive_canvas)
        self.canvas_window = self.archive_canvas.create_window((0, 0), window=self.trainings_container, anchor="nw")
        
        # Make the training container frame expand to the width of the canvas
        def on_canvas_configure(event):
            self.archive_canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.archive_canvas.bind("<Configure>", on_canvas_configure)
        
        # Update the scroll region when the size of the trainings_container changes
        def on_frame_configure(event):
            self.archive_canvas.configure(scrollregion=self.archive_canvas.bbox("all"))
        
        self.trainings_container.bind("<Configure>", on_frame_configure)
        
        # Add mousewheel scrolling
        def _on_mousewheel(event):
            # Handle different platform scroll events
            if event.delta:
                # Windows
                self.archive_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # Linux, macOS
                if event.num == 4:
                    self.archive_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.archive_canvas.yview_scroll(1, "units")
        
        # Bind mousewheel events to the canvas
        self.archive_canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        self.archive_canvas.bind("<Button-4>", _on_mousewheel)    # Linux up
        self.archive_canvas.bind("<Button-5>", _on_mousewheel)    # Linux down
        
        # Store reference to binding functions for cleanup
        self.archive_bindings = [
            (self.archive_canvas, "<Configure>", on_canvas_configure),
            (self.trainings_container, "<Configure>", on_frame_configure),
            (self.archive_canvas, "<MouseWheel>", _on_mousewheel),
            (self.archive_canvas, "<Button-4>", _on_mousewheel),
            (self.archive_canvas, "<Button-5>", _on_mousewheel)
        ]
        
        # Ensure we clean up bindings when tab is destroyed
        self.bind("<Destroy>", self.cleanup_bindings)
        
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
    
    def _create_field(self, parent, row, label_column, label_text, var_name, 
                   widget_type="entry", values=None, width=25, label_col_offset=0):
        """Helper to create a label and input widget in the grid."""
        # Create label
        label = ttkb.Label(parent, text=label_text)
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
            widget = ttkb.Entry(parent, textvariable=self.variables[var_name], width=width)
        elif widget_type == "combobox":
            widget = ttkb.Combobox(
                parent,
                textvariable=self.variables[var_name],
                values=values if values else [],
                width=width - 2, # Combobox width is slightly different
                state="readonly"
            )
            if values and not self.variables[var_name].get(): # Set default value for combobox if empty
                self.variables[var_name].set(values[0]) 
        else:
            # Fallback for unknown types
            widget = ttkb.Label(parent, text=f"Unknown widget: {widget_type}")

        widget.grid(row=row, column=widget_column, padx=5, pady=5, sticky="we") # Use sticky 'we' to expand
        
        return widget
    
    def set_current_date(self):
        """Set current date in the date field using format DD-MM-AAAA."""
        today_str = datetime.now().strftime("%d-%m-%Y")
        
        if "fecha" in self.variables:
            self.variables["fecha"].set(today_str)
            # Force update of the display
            self.update_idletasks()
            print(f"Date set to: {today_str}")
        else:
            print("Error: 'fecha' variable not found.")
    
    def load_data(self):
        """Load flight data into the form fields. Returns True if data was loaded."""
        # Get flight data from data manager
        flight_data = self.data_manager.current_data.get('vuelo', {})
        
        # Load data into variables
        for var_name, var in self.variables.items():
            var.set(flight_data.get(var_name, ''))
        
        return bool(flight_data)
    
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
        
        # Update the UI with new values
        self.variables['vuelo_del_ano'].set(str(training_year))
        self.variables['vuelo_total'].set(str(total_trainings))
        
        # Set the date to today
        self.set_current_date()
        
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
            date = training_data.get('fecha', datetime.now().strftime("%d-%m-%Y"))
            training_year = training_data.get('vuelo_del_ano', '0')
            
            # Create a unique ID for this training
            training_id = f"{date}_{training_year}"
            
            # Add timestamp for sorting
            training_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to archives dictionary
            self.training_archives[training_id] = training_data
            
            # Save archives to JSON file
            self.save_training_archives()
            
            # Also save full data from all tabs to a separate archive file
            self.save_full_training_data(training_id)
            
            # Refresh the training list
            self.refresh_training_list()
            
        except Exception as e:
            print(f"Error saving to training archive: {e}")
            
    def save_full_training_data(self, training_id):
        """Save data from all tabs for this training ID."""
        try:
            # Check if archives directory exists, create if not
            archives_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'archives')
            os.makedirs(archives_dir, exist_ok=True)
            
            # Path to the full training data archives file
            full_data_file = os.path.join(archives_dir, 'training_full_data.json')
            
            # Load existing full data if file exists
            all_training_data = {}
            if os.path.exists(full_data_file):
                with open(full_data_file, 'r', encoding='utf-8') as f:
                    all_training_data = json.load(f)
            
            # Update or add this training's full data
            all_training_data[training_id] = self.data_manager.current_data
            
            # Save updated full data to JSON file
            with open(full_data_file, 'w', encoding='utf-8') as f:
                json.dump(all_training_data, f, ensure_ascii=False, indent=4)
                
            print(f"Full data for training ID {training_id} saved successfully")
                
        except Exception as e:
            print(f"Error saving full training data: {e}")
    
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
            training_frame.pack(fill=tk.X, padx=5, pady=2, expand=True)
            
            # Configure the frame to be responsive
            training_frame.columnconfigure(0, weight=1)  # Text content
            training_frame.columnconfigure(1, weight=0)  # Button
            
            # Format the display text
            date = training_data.get('fecha', 'Sin fecha')
            training_num = training_data.get('vuelo_del_ano', '?')
            total_num = training_data.get('vuelo_total', '?')
            
            # Load additional information from the full data archive if available
            additional_info = ""
            student_count = 0
            
            try:
                # Check if full data exists for this training
                archives_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'archives')
                full_data_file = os.path.join(archives_dir, 'training_full_data.json')
                
                if os.path.exists(full_data_file):
                    with open(full_data_file, 'r', encoding='utf-8') as f:
                        all_training_data = json.load(f)
                        
                        if training_id in all_training_data:
                            full_data = all_training_data[training_id]
                            
                            # Get student count
                            alumnos_data = full_data.get('alumnos', [])
                            # Count non-empty student entries
                            student_count = sum(1 for s in alumnos_data if s.get('name'))
                            
                            # Get RD info
                            rd_data = full_data.get('rd', {})
                            rd_type = rd_data.get('tipo_rd', '')
                            
                            # Check for reactions
                            reactions_data = full_data.get('reactions_data', [])
                            reaction_count = len(reactions_data)
                            
                            # Build additional info string
                            additional_info = f" | Alumnos: {student_count}"
                            if rd_type:
                                additional_info += f" | RD: {rd_type}"
                            if reaction_count > 0:
                                additional_info += f" | Reacciones: {reaction_count}"
            except Exception as e:
                print(f"Error loading full data for training ID {training_id}: {e}")
            
            # Basic display text
            display_text = f"Fecha: {date} | Entrenamiento: #{training_num} | Total: #{total_num}"
            
            # Add operador_camara if available
            if 'operador_camara' in training_data and training_data['operador_camara']:
                display_text += f" | Op. Cámara: {training_data['operador_camara']}"
                
            # Add additional info from full data if available
            if additional_info:
                display_text += additional_info
            
            training_label = ttkb.Label(
                training_frame,
                text=display_text,
                font=('Segoe UI', 9),
                wraplength=600,  # Allow wrapping for longer text
                justify=tk.LEFT,
                anchor="w"
            )
            training_label.grid(row=0, column=0, sticky="w", padx=5, pady=3)
            
            # Add load button
            load_btn = ttkb.Button(
                training_frame,
                text="Cargar",
                command=lambda t_id=training_id: self.load_training(t_id),
                bootstyle="info-outline",
                width=8
            )
            load_btn.grid(row=0, column=1, sticky="e", padx=5, pady=3)
            
            # Add divider
            ttkb.Separator(self.trainings_container, orient="horizontal").pack(fill=tk.X, padx=5, pady=1, expand=True)
    
    def load_training(self, training_id):
        """Load a specific training from the archives into the form and all other tabs."""
        # Check if training exists
        if training_id not in self.training_archives:
            messagebox.showerror("Error", f"No se encontró el entrenamiento con ID {training_id}")
            return
            
        # Get the training data
        training_data = self.training_archives[training_id]
        
        # Confirm loading
        confirm = messagebox.askyesno(
            "Cargar Entrenamiento",
            "¿Está seguro que desea cargar este entrenamiento? Se perderán los datos no guardados de todas las pestañas.",
            icon="question"
        )
        
        if not confirm:
            return
            
        # Update form fields for Vuelo tab
        for field_name, var in self.variables.items():
            if field_name in training_data:
                var.set(training_data[field_name])
        
        # Update current data in data_manager for Vuelo tab
        self.data_manager.current_data['vuelo'] = training_data.copy()
        
        # Get archived data for all tabs based on this training ID
        # The archives might have different keys for different tabs
        archived_data = self.data_manager.load_archived_data(training_id)
        
        if archived_data:
            # Load data for all other tabs
            for key in archived_data:
                if key != 'vuelo':  # Skip vuelo data as it's already loaded
                    self.data_manager.current_data[key] = archived_data[key]
        
        # Save to current file
        try:
            self.data_manager.save_data()
            messagebox.showinfo("Carga Exitosa", "Entrenamiento cargado correctamente en todas las pestañas.")
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
            # If search_date is part of the date, consider it a match
            if search_date in date:
                found = True
                
                # Create frame for this training
                training_frame = ttkb.Frame(self.trainings_container)
                training_frame.pack(fill=tk.X, padx=5, pady=2, expand=True)
                
                # Configure the frame to be responsive
                training_frame.columnconfigure(0, weight=1)  # Text content
                training_frame.columnconfigure(1, weight=0)  # Button
                
                # Format the display text
                training_num = training_data.get('vuelo_del_ano', '?')
                total_num = training_data.get('vuelo_total', '?')
                
                # Load additional information from full data archive
                additional_info = ""
                try:
                    # Check if full data exists for this training
                    archives_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'archives')
                    full_data_file = os.path.join(archives_dir, 'training_full_data.json')
                    
                    if os.path.exists(full_data_file):
                        with open(full_data_file, 'r', encoding='utf-8') as f:
                            all_training_data = json.load(f)
                            
                            if training_id in all_training_data:
                                full_data = all_training_data[training_id]
                                
                                # Get student count
                                alumnos_data = full_data.get('alumnos', [])
                                student_count = sum(1 for s in alumnos_data if s.get('name'))
                                
                                # Build additional info string
                                additional_info = f" | Alumnos: {student_count}"
                except Exception as e:
                    print(f"Error loading full data for training ID {training_id}: {e}")
                
                display_text = f"Fecha: {date} | Entrenamiento: #{training_num} | Total: #{total_num}"
                
                # Add operador_camara if available
                if 'operador_camara' in training_data and training_data['operador_camara']:
                    display_text += f" | Op. Cámara: {training_data['operador_camara']}"
                    
                # Add additional info if available
                if additional_info:
                    display_text += additional_info
                
                training_label = ttkb.Label(
                    training_frame,
                    text=display_text,
                    font=('Segoe UI', 9),
                    wraplength=600,
                    justify=tk.LEFT,
                    anchor="w"
                )
                training_label.grid(row=0, column=0, sticky="w", padx=5, pady=3)
                
                # Add load button
                load_btn = ttkb.Button(
                    training_frame,
                    text="Cargar",
                    command=lambda t_id=training_id: self.load_training(t_id),
                    bootstyle="info-outline",
                    width=8
                )
                load_btn.grid(row=0, column=1, sticky="e", padx=5, pady=3)
                
                # Add divider
                ttkb.Separator(self.trainings_container, orient="horizontal").pack(fill=tk.X, padx=5, pady=1, expand=True)
        
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
                training_frame.pack(fill=tk.X, padx=5, pady=2, expand=True)
                
                # Configure the frame to be responsive
                training_frame.columnconfigure(0, weight=1)  # Text content
                training_frame.columnconfigure(1, weight=0)  # Button
                
                # Format the display text
                date = training_data.get('fecha', 'Sin fecha')
                total_num = training_data.get('vuelo_total', '?')
                
                # Load additional information from full data archive
                additional_info = ""
                try:
                    # Check if full data exists for this training
                    archives_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'archives')
                    full_data_file = os.path.join(archives_dir, 'training_full_data.json')
                    
                    if os.path.exists(full_data_file):
                        with open(full_data_file, 'r', encoding='utf-8') as f:
                            all_training_data = json.load(f)
                            
                            if training_id in all_training_data:
                                full_data = all_training_data[training_id]
                                
                                # Get student count
                                alumnos_data = full_data.get('alumnos', [])
                                student_count = sum(1 for s in alumnos_data if s.get('name'))
                                
                                # Get RD info
                                rd_data = full_data.get('rd', {})
                                rd_type = rd_data.get('tipo_rd', '')
                                
                                # Check for reactions
                                reactions_data = full_data.get('reactions_data', [])
                                reaction_count = len(reactions_data)
                                
                                # Build additional info string
                                additional_info = f" | Alumnos: {student_count}"
                                if rd_type:
                                    additional_info += f" | RD: {rd_type}"
                                if reaction_count > 0:
                                    additional_info += f" | Reacciones: {reaction_count}"
                except Exception as e:
                    print(f"Error loading full data for training ID {training_id}: {e}")
                
                display_text = f"Fecha: {date} | Entrenamiento: #{training_num} | Total: #{total_num}"
                
                # Add operador_camara if available
                if 'operador_camara' in training_data and training_data['operador_camara']:
                    display_text += f" | Op. Cámara: {training_data['operador_camara']}"
                    
                # Add additional info if available
                if additional_info:
                    display_text += additional_info
                
                training_label = ttkb.Label(
                    training_frame,
                    text=display_text,
                    font=('Segoe UI', 9),
                    wraplength=600,
                    justify=tk.LEFT,
                    anchor="w"
                )
                training_label.grid(row=0, column=0, sticky="w", padx=5, pady=3)
                
                # Add load button
                load_btn = ttkb.Button(
                    training_frame,
                    text="Cargar",
                    command=lambda t_id=training_id: self.load_training(t_id),
                    bootstyle="info-outline",
                    width=8
                )
                load_btn.grid(row=0, column=1, sticky="e", padx=5, pady=3)
                
                # Add divider
                ttkb.Separator(self.trainings_container, orient="horizontal").pack(fill=tk.X, padx=5, pady=1, expand=True)
        
        if not found:
            empty_label = ttkb.Label(
                self.trainings_container,
                text=f"No se encontraron entrenamientos con número '{search_num}'",
                font=('Segoe UI', 10, 'italic'),
                foreground="gray"
            )
            empty_label.pack(pady=10)

    def cleanup_bindings(self, event=None):
        """Clean up event bindings to prevent errors when tab is destroyed."""
        try:
            # Only clean up if the event is for this widget being destroyed
            if event and event.widget != self:
                return
                
            # Clean up archive canvas bindings
            if hasattr(self, 'archive_bindings'):
                for widget, event_name, func in self.archive_bindings:
                    try:
                        widget.unbind(event_name)
                    except:
                        pass
            
            # Clean up main canvas bindings
            if hasattr(self, 'main_bindings'):
                for widget, event_name, func in self.main_bindings:
                    try:
                        widget.unbind(event_name)
                    except:
                        pass
                        
            # Explicitly clean up canvas references
            if hasattr(self, 'archive_canvas'):
                try:
                    self.archive_canvas.delete("all")
                except:
                    pass
                    
            if hasattr(self, 'main_canvas'):
                try:
                    self.main_canvas.delete("all")
                except:
                    pass
                    
            print("VueloTab bindings cleaned up successfully")
        except Exception as e:
            print(f"Error cleaning up bindings: {e}")

# Ensure imports are correct
# Ensure AppConfig/DataManager are passed correctly during instantiation
# Ensure ttkbootstrap is installed 
