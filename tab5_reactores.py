#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox # Use ttk for Treeview
import ttkbootstrap as ttkb
from datetime import datetime
from typing import Dict, Any, List, Optional

class ReactoresTab(ttkb.Frame):
    """Tab for recording Adverse Reactions during training, aligned with rules."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Constants from Rules
        self.max_students = 8
        self.max_oi = 2
        self.participant_ids = [str(i) for i in range(1, self.max_students + 1)] + \
                               [f"OI{i}" for i in range(1, self.max_oi + 1)]
        self.cie10_options = [
            "T700 BAROTITIS", "R064 HIPERVENTILACION", "T702 HIPOXIA", 
            "T701 BAROSINUSITIS", "K040 BARODONTALGIA", 
            "T703 ENF. POR DESCOMPRESION", "F402 CLAUSTROFOBIA", 
            "F409 APREHENSION", "OTRO" # Added OTRO as fallback
        ]
        self.severidad_options = ["Leve", "Moderado", "Severo"]
        self.perfil_options = ["IV-A", "Descompresión Lenta", "Descompresión rápida"]
        self.si_no_options = ["Si", "No"]

        # Data structure for reactions list
        self.reactions_list: List[Dict[str, Any]] = []
        # Variables for the current reaction entry form
        self.current_reaction_vars: Dict[str, tk.StringVar] = {}

        self.initialize_data()
        self.create_widgets()
        self.load_data() # Load after widgets are created
    
    def initialize_data(self):
        """Initialize or load the list of reactions."""
        # Load from data manager if exists, using a new key like 'reactions_data'
        self.reactions_list = self.data_manager.current_data.get('reactions_data', [])
        # Ensure it's a list
        if not isinstance(self.reactions_list, list):
            print("Warning: Loaded reactions_data is not a list. Initializing as empty.")
            self.reactions_list = []

    def create_widgets(self):
        """Create the new UI layout for recording reactions."""
        # Configure main grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1) # Allow reaction list to expand

        # Frame for entering a new reaction
        entry_frame = ttkb.LabelFrame(self, text="Registrar Nueva Reacción Adversas", padding=15, bootstyle="danger")
        entry_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.create_entry_form(entry_frame)

        # Frame for displaying the list of recorded reactions
        list_frame = ttkb.LabelFrame(self, text="Reacciones Registradas", padding=10, bootstyle="info")
        list_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.create_reaction_list_display(list_frame)

        # Buttons are now inside the entry_frame

    def create_entry_form(self, parent):
        """Creates the form widgets for entering a single reaction."""
        form_grid = ttkb.Frame(parent)
        form_grid.pack(fill=tk.BOTH, expand=True)
        # Configure grid columns (Label, Widget, Label, Widget)
        form_grid.columnconfigure(1, weight=1)
        form_grid.columnconfigure(3, weight=1)
        
        row_idx = 0
        # --- Row 0: Participant & Time --- 
        # Participant Selection
        self._create_form_field(form_grid, row_idx, 0, "Participante:", "participant_id", 
                                widget_type="combobox", values=self.participant_ids)
        # Event Time
        event_time_label = ttkb.Label(form_grid, text="Hora Evento:")
        event_time_label.grid(row=row_idx, column=2, padx=(10, 5), pady=5, sticky='e')
        self.current_reaction_vars['event_time'] = tk.StringVar()
        event_time_entry = ttkb.Entry(form_grid, textvariable=self.current_reaction_vars['event_time'], width=10, state='readonly')
        event_time_entry.grid(row=row_idx, column=3, padx=5, pady=5, sticky='w')
        event_time_btn = ttkb.Button(form_grid, text="Ahora", 
                                     command=lambda: self.current_reaction_vars['event_time'].set(datetime.now().strftime('%H:%M:%S')),
                                     bootstyle="secondary-outline", width=6)
        event_time_btn.grid(row=row_idx, column=4, padx=5, pady=5, sticky='w')
        row_idx += 1

        # --- Row 1: CIE10 & Severidad --- 
        self._create_form_field(form_grid, row_idx, 0, "CIE 10:", "cie10", 
                                widget_type="combobox", values=self.cie10_options, width=30)
        self._create_form_field(form_grid, row_idx, 2, "Severidad:", "severidad", 
                                widget_type="combobox", values=self.severidad_options)
        row_idx += 1

        # --- Row 2: Perfil & Altitud --- 
        self._create_form_field(form_grid, row_idx, 0, "Perfil:", "perfil", 
                                widget_type="combobox", values=self.perfil_options, width=20)
        self._create_form_field(form_grid, row_idx, 2, "Altitud (ft):", "altitud", widget_type="entry", width=10)
        row_idx += 1

        # --- Row 3: Mejora & Removido --- 
        self._create_form_field(form_grid, row_idx, 0, "Mejora:", "mejora", 
                                widget_type="combobox", values=self.si_no_options, width=6)
        self._create_form_field(form_grid, row_idx, 2, "Removido:", "removido", 
                                widget_type="combobox", values=self.si_no_options, width=6)
        row_idx += 1

        # --- Row 4: Remision & Telefono (Display Only?) --- 
        self._create_form_field(form_grid, row_idx, 0, "Remisión:", "remision", 
                                widget_type="combobox", values=self.si_no_options, width=6)
        self._create_form_field(form_grid, row_idx, 2, "Teléfono:", "telefono", widget_type="entry", width=15)
        row_idx += 1
        
        # --- Row 5: Mask & Helmet (Display Only?) ---
        self._create_form_field(form_grid, row_idx, 0, "No. Máscara:", "mask", widget_type="entry", width=10)
        self._create_form_field(form_grid, row_idx, 2, "No. Casco:", "helmet", widget_type="entry", width=10)
        row_idx += 1

        # --- Row 6: Manejo (Text Area) ---
        manejo_label = ttkb.Label(form_grid, text="Manejo:")
        manejo_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky='nw')
        self.manejo_text = tk.Text(form_grid, height=3, width=40, wrap=tk.WORD)
        self.manejo_text.grid(row=row_idx, column=1, columnspan=4, padx=5, pady=5, sticky='ew')
        # Add scrollbar? Maybe not needed for height=3
        row_idx += 1

        # --- Row 7: Tratamiento (Text Area) ---
        tratamiento_label = ttkb.Label(form_grid, text="Tratamiento:")
        tratamiento_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky='nw')
        self.tratamiento_text = tk.Text(form_grid, height=3, width=40, wrap=tk.WORD)
        self.tratamiento_text.grid(row=row_idx, column=1, columnspan=4, padx=5, pady=5, sticky='ew')
        row_idx += 1

        # --- Action Buttons --- 
        button_frame = ttkb.Frame(form_grid)
        button_frame.grid(row=row_idx, column=0, columnspan=5, pady=10, sticky='e')

        add_btn = ttkb.Button(
            button_frame,
            text="Añadir Reacción",
            command=self.add_reaction,
            bootstyle="success",
            width=15
        )
        add_btn.pack(side=tk.RIGHT, padx=5)

        clear_entry_btn = ttkb.Button(
            button_frame,
            text="Limpiar Entrada",
            command=self.clear_entry_form,
            bootstyle="warning",
            width=15
        )
        clear_entry_btn.pack(side=tk.RIGHT, padx=5)

    def _create_form_field(self, parent, row, col_label, label_text, var_key, 
                           widget_type="entry", values=None, width=20):
        """Helper to create label and widget for the entry form."""
        label = ttkb.Label(parent, text=label_text)
        label.grid(row=row, column=col_label, padx=(10, 5), pady=5, sticky='e')
        
        var = tk.StringVar()
        self.current_reaction_vars[var_key] = var
        
        widget_col = col_label + 1
        if widget_type == "entry":
            widget = ttkb.Entry(parent, textvariable=var, width=width)
        elif widget_type == "combobox":
            widget = ttkb.Combobox(parent, textvariable=var, values=values or [], 
                                   width=width - 2, state="readonly")
            # Set default for comboboxes
            if values:
                if var_key == 'participant_id':
                     var.set(values[0]) # Default to first participant
                elif var_key == 'cie10':
                     var.set(values[0]) # Default to first CIE10
                elif var_key in ['severidad', 'perfil', 'mejora', 'removido', 'remision']:
                     var.set(values[0]) # Default to first option

        else:
            widget = ttkb.Label(parent, text=f"Unknown type: {widget_type}")
            
        widget.grid(row=row, column=widget_col, padx=5, pady=5, sticky='w')
        return widget

    def create_reaction_list_display(self, parent):
        """Creates the Treeview to display recorded reactions."""
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        cols = ["participant_id", "event_time", "cie10", "severidad", "altitud"]
        col_display = ["Participante", "Hora", "CIE10", "Severidad", "Altitud(ft)"]
        col_widths = [80, 70, 150, 80, 70] # Adjust widths

        self.tree = ttk.Treeview(parent, columns=cols, show='headings', height=5)
        
        for i, col_key in enumerate(cols):
            self.tree.heading(col_key, text=col_display[i])
            self.tree.column(col_key, width=col_widths[i], anchor=tk.W)

        # Add scrollbar
        scrollbar = ttkb.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Add button frame below the Treeview
        button_frame = ttkb.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky='e')
        
        # Add button to remove selected reaction
        remove_btn = ttkb.Button(
            button_frame, 
            text="Eliminar Seleccionada", 
            command=self.delete_selected_reaction,
            bootstyle="danger-outline",
            width=20
        )
        remove_btn.pack(side=tk.RIGHT, padx=5)

    def delete_selected_reaction(self):
        """Delete the selected reaction from the list."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Selección Vacía", "Por favor, seleccione una reacción para eliminar.", parent=self)
            return
        
        # Get the index of the selected item
        selected_index = self.tree.index(selected_item[0])
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            "¿Está seguro que desea eliminar la reacción seleccionada?",
            icon="warning",
            parent=self
        )
        
        if not confirm:
            return
        
        # Remove from internal list
        if 0 <= selected_index < len(self.reactions_list):
            del self.reactions_list[selected_index]
            
            # Update display
            self.update_reaction_list_display()
            
            # Save changes
            self.save_data()
            
            print(f"Reacción en posición {selected_index+1} eliminada.")
        else:
            print(f"Error: Índice fuera de rango ({selected_index}).")

    def add_reaction(self):
        """Collects data from the form and adds it to the reactions list."""
        new_reaction = {}
        # Collect from StringVars
        for key, var in self.current_reaction_vars.items():
            new_reaction[key] = var.get()
        
        # Collect from Text widgets
        new_reaction['manejo'] = self.manejo_text.get("1.0", tk.END).strip()
        new_reaction['tratamiento'] = self.tratamiento_text.get("1.0", tk.END).strip()
        
        # Basic validation (at least participant and cie10 should be selected)
        if not new_reaction.get('participant_id') or not new_reaction.get('cie10'):
             messagebox.showwarning("Faltan Datos", "Por favor, seleccione el participante y el código CIE 10.", parent=self)
             return
        if not new_reaction.get('event_time'):
             new_reaction['event_time'] = datetime.now().strftime('%H:%M:%S') # Add time if missing
             self.current_reaction_vars['event_time'].set(new_reaction['event_time'])

        # Add to internal list
        self.reactions_list.append(new_reaction)
        
        # Update display list (Treeview)
        self.update_reaction_list_display()
        
        # Save data
        self.save_data()
        
        # Clear the entry form for the next reaction
        self.clear_entry_form()
        print("Reacción añadida.")

    def update_reaction_list_display(self):
        """Clears and repopulates the Treeview with current reactions."""
        # Delete existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert data from self.reactions_list
        for reaction in self.reactions_list:
             # Extract values for the visible columns
             values = (
                 reaction.get('participant_id', '?'),
                 reaction.get('event_time', '--:--:--'),
                 reaction.get('cie10', ''),
                 reaction.get('severidad', ''),
                 reaction.get('altitud', '')
             )
             self.tree.insert('', tk.END, values=values)

    def clear_entry_form(self):
        """Clears the widgets in the reaction entry form."""
        # Clear StringVars, reset comboboxes to default
        for key, var in self.current_reaction_vars.items():
             if key == 'participant_id':
                 var.set(self.participant_ids[0])
             elif key == 'cie10':
                 var.set(self.cie10_options[0])
             elif key in ['severidad', 'perfil', 'mejora', 'removido', 'remision']:
                  # Find the default value for the combobox
                  options_map = {
                      'severidad': self.severidad_options,
                      'perfil': self.perfil_options,
                      'mejora': self.si_no_options,
                      'removido': self.si_no_options,
                      'remision': self.si_no_options
                  }
                  if key in options_map:
                     var.set(options_map[key][0])
             else:
                 var.set('') # Clear entries like altitud, telefono, etc.
                 
        # Clear Text widgets
        self.manejo_text.delete("1.0", tk.END)
        self.tratamiento_text.delete("1.0", tk.END)
        print("Formulario de entrada limpiado.")

    def load_data(self):
        """Load reaction list and update display."""
        # Data loaded into self.reactions_list during initialize_data
        self.update_reaction_list_display()
        # Clear entry form on initial load
        self.clear_entry_form() 
    
    def save_data(self):
        """Save the list of reactions to the data manager."""
        self.data_manager.current_data['reactions_data'] = self.reactions_list
        
        # Remove old reactor data if present
        if 'reactors_data' in self.data_manager.current_data:
            del self.data_manager.current_data['reactors_data']
        if 'reactors_summary' in self.data_manager.current_data:
             del self.data_manager.current_data['reactors_summary']
             
        try:
            self.data_manager.save_data()
            print("Lista de reacciones guardada.")
        except Exception as e:
            print(f"Error saving reactions data: {e}")

    def clear_form(self):
        """Clears the entire tab: the entry form AND the reactions list."""
        confirm = messagebox.askyesno(
            "Confirmar Limpieza Total",
            "¿Está seguro que desea limpiar la entrada actual Y BORRAR TODAS las reacciones registradas?",
            icon="warning",
            parent=self
        )
        if not confirm: return
        
        self.clear_entry_form()
        self.reactions_list = []
        self.update_reaction_list_display()
        self.save_data() # Save the cleared list
        print("Tab de Reacciones limpiado completamente.")