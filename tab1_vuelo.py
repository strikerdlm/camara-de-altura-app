#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from datetime import datetime
import locale
from typing import Dict, Any

class VueloTab(ttkb.Frame):
    """Tab for flight data, aligned with camara.mdc rules."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10) # Add padding directly to frame
        self.parent = parent
        self.data_manager = data_manager
        
        # Data variables
        self.variables: Dict[str, tk.StringVar] = {}
        
        # Create the layout
        self.create_widgets()
        self.load_data() # Load data after widgets are created
        
    def create_widgets(self):
        """Create the tab UI widgets based on rules."""
        
        # Use grid layout directly on self for simplicity
        self.columnconfigure(1, weight=1) # Column for entry fields
        self.columnconfigure(3, weight=1) # Column for entry fields
        current_row = 0

        # Header
        header = ttkb.Label(
            self,
            text="Datos del Vuelo",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=current_row, column=0, columnspan=4, sticky="w", pady=(0, 10))
        current_row += 1

        # -- Row 1 --
        # Fecha
        self._create_field(current_row, 0, "Fecha:", "fecha")
        date_btn = ttkb.Button(
            self,
            text="Hoy",
            command=self.set_current_date,
            bootstyle="secondary-outline",
            width=5 # Smaller button
        )
        date_btn.grid(row=current_row, column=2, padx=(0, 5), pady=5, sticky="w")
        
        # Vuelo del Año 
        self._create_field(current_row, 2, "Vuelo del Año:", "vuelo_del_ano", label_col_offset=1)
        current_row += 1

        # -- Row 2 --
        # Vuelo Total
        self._create_field(current_row, 0, "Vuelo Total:", "vuelo_total")
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

        # --- Removed old fields/layout --- 
        # --- Removed Observaciones Text Area --- 

        # Add padding below fields before buttons
        self.rowconfigure(current_row, weight=1) # Add spacer row
        current_row += 1

        # Buttons section (using pack at the bottom for simplicity)
        button_frame = ttkb.Frame(self)
        # Pack below the grid content
        button_frame.grid(row=current_row, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        
        save_btn = ttkb.Button(
            button_frame,
            text="Guardar Datos",
            command=self.save_data,
            bootstyle="success", # Changed style
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        clear_btn = ttkb.Button(
            button_frame,
            text="Limpiar Campos",
            command=self.clear_form,
            bootstyle="warning", # Changed style
            width=15
        )
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
    def _create_field(self, row, label_column, label_text, var_name, 
                   widget_type="entry", values=None, width=25, label_col_offset=0):
        """Helper to create a label and input widget in the grid."""
        # Create label
        label = ttkb.Label(self, text=label_text)
        # Adjust label column if offset is specified
        actual_label_column = label_column + label_col_offset 
        label.grid(row=row, column=actual_label_column, padx=(15,5), pady=5, sticky="e")
        
        # Create variable
        var = tk.StringVar()
        self.variables[var_name] = var
        
        # Determine widget column
        widget_column = actual_label_column + 1

        # Create input widget
        if widget_type == "entry":
            widget = ttkb.Entry(self, textvariable=var, width=width)
        elif widget_type == "combobox":
            widget = ttkb.Combobox(
                self,
                textvariable=var,
                values=values if values else [],
                width=width - 2, # Combobox width is slightly different
                state="readonly"
            )
            if values: # Set default value for combobox
                var.set(values[0]) 
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
        """Load existing flight data for the fields defined in self.variables."""
        # Ensure data is loaded under a consistent key, e.g., 'datos_vuelo'
        vuelo_data = self.data_manager.current_data.get('datos_vuelo', {})
        
        for field_name, var in self.variables.items():
            # Handle potential missing keys gracefully
            value = vuelo_data.get(field_name, '') 
            var.set(value)
        
        # Handle combobox defaults if loaded value is empty/invalid
        if not self.variables['perfil_camara'].get():
             self.variables['perfil_camara'].set("IV-A")
        if not self.variables['curso'].get():
            self.variables['curso'].set("Primera vez")
    
    def save_data(self):
        """Save flight data from the fields defined in self.variables."""
        vuelo_data = {}
        for field_name, var in self.variables.items():
            vuelo_data[field_name] = var.get()
        
        # Save under the consistent key 'datos_vuelo'
        self.data_manager.current_data['datos_vuelo'] = vuelo_data
        # Assume data_manager.save_data() saves the entire current_data structure
        try:
            self.data_manager.save_data()
            print("Datos del vuelo guardados.")
            # self.show_toast("Datos del vuelo guardados") # Optional: re-enable toast if desired
        except Exception as e:
             print(f"Error saving flight data: {e}")
             # self.show_toast("Error al guardar datos") # Optional: error toast
    
    def clear_form(self):
        """Clear all fields managed by self.variables."""
        for field_name, var in self.variables.items():
            # Reset to empty string, except for comboboxes which get default
            if field_name == 'perfil_camara':
                 var.set("IV-A")
            elif field_name == 'curso':
                 var.set("Primera vez")
            else:
                 var.set('')
        
        # Optionally clear the date field or set to today?
        # self.variables['fecha'].set('') 
        self.set_current_date() # Set date to today on clear
        
        print("Formulario de Vuelo limpiado.")
        # self.show_toast("Formulario limpiado") # Optional: re-enable toast
    
    # --- Removed show_toast method if not needed or handled globally ---

# Ensure imports are correct
# Ensure AppConfig/DataManager are passed correctly during instantiation
# Ensure ttkbootstrap is installed 