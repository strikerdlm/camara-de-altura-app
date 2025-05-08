#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
from typing import Dict, Any
import json
import os
from datetime import datetime

class RDTab(ttkb.Frame):
    """Tab for managing RD records."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        self.main_app = main_app
        self.rd_data = {}
        self.prevent_load_overwrite = False
        
        # Create variables for form fields
        self.variables = {}
        self.create_variables()
        
        # Create the layout
        self.create_widgets()
        self.load_data()
        
        # Set up binding cleanup
        self.bind("<Destroy>", self.cleanup_bindings)
    
    def _on_data_changed(self, *args):
        """Callback when any traced StringVar in this tab is written to."""
        if not self.prevent_load_overwrite:
            print(f"RDTab: Data changed, setting prevent_load_overwrite = True")
            self.prevent_load_overwrite = True

    def create_variables(self):
        """Create variables for form fields."""
        # Common data
        self.variables['fecha'] = tk.StringVar()
        
        # RD1 data
        self.variables['observador_interno_rd1'] = tk.StringVar()
        self.variables['alumno1_rd1'] = tk.StringVar()
        self.variables['alumno2_rd1'] = tk.StringVar()
        self.variables['silla1_rd1'] = tk.StringVar()
        self.variables['silla2_rd1'] = tk.StringVar()
        self.variables['evento_adverso_rd1'] = tk.StringVar()
        self.variables['descripcion_rd1'] = tk.StringVar()
        self.variables['observaciones_rd1'] = tk.StringVar()
        
        # RD2 data
        self.variables['observador_interno_rd2'] = tk.StringVar()
        self.variables['alumno1_rd2'] = tk.StringVar()
        self.variables['alumno2_rd2'] = tk.StringVar()
        self.variables['silla1_rd2'] = tk.StringVar()
        self.variables['silla2_rd2'] = tk.StringVar()
        self.variables['evento_adverso_rd2'] = tk.StringVar()
        self.variables['descripcion_rd2'] = tk.StringVar()
        self.variables['observaciones_rd2'] = tk.StringVar()
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Title row
        self.rowconfigure(1, weight=1)  # Content row
        self.rowconfigure(2, weight=0)  # Button row
        
        # Title
        title_label = ttkb.Label(
            self, 
            text="Perfil de Descompresión Rápida", 
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Create a frame for the main content with scrolling
        main_content_frame = ttkb.Frame(self)
        main_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.rowconfigure(0, weight=1)
        
        # Create a canvas with scrollbars for the main content
        self.main_canvas = tk.Canvas(main_content_frame)
        y_scrollbar = ttkb.Scrollbar(main_content_frame, orient="vertical", command=self.main_canvas.yview)
        x_scrollbar = ttkb.Scrollbar(main_content_frame, orient="horizontal", command=self.main_canvas.xview)
        
        # Configure the canvas scrolling
        self.main_canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid layout for canvas and scrollbars
        self.main_canvas.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Create a frame inside the canvas to hold the form content
        self.content_frame = ttkb.Frame(self.main_canvas)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Configure the content frame grid
        self.content_frame.columnconfigure(0, weight=1)
        
        # Make the content frame expand to fill the canvas width
        def on_canvas_configure(event):
            self.main_canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.main_canvas.bind("<Configure>", on_canvas_configure)
        
        # Update the scroll region when the size of the content frame changes
        def on_frame_configure(event):
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        
        self.content_frame.bind("<Configure>", on_frame_configure)
        
        # Add mousewheel scrolling for the main canvas
        def _on_mousewheel(event):
            # Handle different platform scroll events
            if event.delta:
                # Windows
                self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # Linux, macOS
                if event.num == 4:
                    self.main_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.main_canvas.yview_scroll(1, "units")
        
        # Bind mousewheel events to the canvas
        self.main_canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        self.main_canvas.bind("<Button-4>", _on_mousewheel)    # Linux up
        self.main_canvas.bind("<Button-5>", _on_mousewheel)    # Linux down
        
        # Store references for cleanup
        self.main_bindings = [
            (self.main_canvas, "<Configure>", on_canvas_configure),
            (self.content_frame, "<Configure>", on_frame_configure),
            (self.main_canvas, "<MouseWheel>", _on_mousewheel),
            (self.main_canvas, "<Button-4>", _on_mousewheel),
            (self.main_canvas, "<Button-5>", _on_mousewheel)
        ]
        
        # Date frame (common for both RDs)
        date_frame = ttkb.Frame(self.content_frame, padding=10)
        date_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Date field with Today button
        date_label = ttkb.Label(date_frame, text="Fecha:")
        date_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        date_entry = ttkb.Entry(
            date_frame,
            textvariable=self.variables['fecha'],
            width=15
        )
        date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.variables['fecha'].trace_add("write", self._on_data_changed)
        
        # Add today button
        today_btn = ttkb.Button(
            date_frame,
            text="Hoy",
            command=self.set_current_date,
            bootstyle="info-outline",
            width=6
        )
        today_btn.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        # Format label
        format_label = ttkb.Label(
            date_frame,
            text="(DD-MM-AAAA)",
            font=('Segoe UI', 9),
            bootstyle="secondary"
        )
        format_label.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # First RD section
        rd1_frame = ttkb.Labelframe(
            self.content_frame,
            text="Primera Descompresión Rápida (RD1)",
            padding=10,
            bootstyle="info"
        )
        rd1_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        rd1_frame.columnconfigure(1, weight=1)
        
        # RD1 fields
        # Observador Interno RD1
        ttkb.Label(rd1_frame, text="Observador Interno:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        observador_combo1 = ttkb.Combobox(
            rd1_frame,
            textvariable=self.variables['observador_interno_rd1'],
            values=["OI1", "OI2"],
            state="readonly"
        )
        observador_combo1.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.variables['observador_interno_rd1'].trace_add("write", self._on_data_changed)
        
        # Alumno 1 RD1
        ttkb.Label(rd1_frame, text="Alumno 1:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        alumno_combo1 = ttkb.Combobox(
            rd1_frame,
            textvariable=self.variables['alumno1_rd1'],
            values=["1", "2", "3", "4", "5", "6", "7", "8"],
            state="readonly"
        )
        alumno_combo1.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.variables['alumno1_rd1'].trace_add("write", self._on_data_changed)
        
        # Silla 1 RD1
        ttkb.Label(rd1_frame, text="Silla 1:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        silla_combo1 = ttkb.Combobox(
            rd1_frame,
            textvariable=self.variables['silla1_rd1'],
            values=["7", "8"],
            state="readonly"
        )
        silla_combo1.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.variables['silla1_rd1'].trace_add("write", self._on_data_changed)
        
        # Alumno 2 RD1
        ttkb.Label(rd1_frame, text="Alumno 2:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        alumno2_combo1 = ttkb.Combobox(
            rd1_frame,
            textvariable=self.variables['alumno2_rd1'],
            values=["1", "2", "3", "4", "5", "6", "7", "8"],
            state="readonly"
        )
        alumno2_combo1.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.variables['alumno2_rd1'].trace_add("write", self._on_data_changed)
        
        # Silla 2 RD1
        ttkb.Label(rd1_frame, text="Silla 2:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        silla2_combo1 = ttkb.Combobox(
            rd1_frame,
            textvariable=self.variables['silla2_rd1'],
            values=["7", "8"],
            state="readonly"
        )
        silla2_combo1.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.variables['silla2_rd1'].trace_add("write", self._on_data_changed)
        
        # Evento Adverso RD1
        ttkb.Label(rd1_frame, text="Evento Adverso:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        evento_frame1 = ttkb.Frame(rd1_frame)
        evento_frame1.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        
        # Radio buttons for Evento Adverso RD1
        si_radio1 = ttkb.Radiobutton(
            evento_frame1,
            text="Sí",
            variable=self.variables['evento_adverso_rd1'],
            value="Sí"
        )
        si_radio1.pack(side=tk.LEFT, padx=(0, 10))
        
        no_radio1 = ttkb.Radiobutton(
            evento_frame1,
            text="No",
            variable=self.variables['evento_adverso_rd1'],
            value="No"
        )
        no_radio1.pack(side=tk.LEFT)
        self.variables['evento_adverso_rd1'].trace_add("write", self._on_data_changed)
        
        # Set default value for evento_adverso_rd1
        if not self.variables['evento_adverso_rd1'].get():
            self.variables['evento_adverso_rd1'].set("No")
        
        # Description and Observations RD1
        ttkb.Label(rd1_frame, text="Descripción:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        ttkb.Entry(
            rd1_frame,
            textvariable=self.variables['descripcion_rd1']
        ).grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        self.variables['descripcion_rd1'].trace_add("write", self._on_data_changed)
        
        ttkb.Label(rd1_frame, text="Observaciones:").grid(row=7, column=0, sticky="w", padx=5, pady=2)
        ttkb.Entry(
            rd1_frame,
            textvariable=self.variables['observaciones_rd1']
        ).grid(row=7, column=1, sticky="ew", padx=5, pady=2)
        self.variables['observaciones_rd1'].trace_add("write", self._on_data_changed)
        
        # Second RD section
        rd2_frame = ttkb.Labelframe(
            self.content_frame,
            text="Segunda Descompresión Rápida (RD2)",
            padding=10,
            bootstyle="info"
        )
        rd2_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        rd2_frame.columnconfigure(1, weight=1)
        
        # RD2 fields
        # Observador Interno RD2
        ttkb.Label(rd2_frame, text="Observador Interno:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        observador_combo2 = ttkb.Combobox(
            rd2_frame,
            textvariable=self.variables['observador_interno_rd2'],
            values=["OI1", "OI2"],
            state="readonly"
        )
        observador_combo2.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.variables['observador_interno_rd2'].trace_add("write", self._on_data_changed)
        
        # Alumno 1 RD2
        ttkb.Label(rd2_frame, text="Alumno 1:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        alumno_combo1 = ttkb.Combobox(
            rd2_frame,
            textvariable=self.variables['alumno1_rd2'],
            values=["1", "2", "3", "4", "5", "6", "7", "8"],
            state="readonly"
        )
        alumno_combo1.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.variables['alumno1_rd2'].trace_add("write", self._on_data_changed)
        
        # Silla 1 RD2
        ttkb.Label(rd2_frame, text="Silla 1:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        silla_combo1 = ttkb.Combobox(
            rd2_frame,
            textvariable=self.variables['silla1_rd2'],
            values=["7", "8"],
            state="readonly"
        )
        silla_combo1.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.variables['silla1_rd2'].trace_add("write", self._on_data_changed)
        
        # Alumno 2 RD2
        ttkb.Label(rd2_frame, text="Alumno 2:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        alumno2_combo2 = ttkb.Combobox(
            rd2_frame,
            textvariable=self.variables['alumno2_rd2'],
            values=["1", "2", "3", "4", "5", "6", "7", "8"],
            state="readonly"
        )
        alumno2_combo2.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.variables['alumno2_rd2'].trace_add("write", self._on_data_changed)
        
        # Silla 2 RD2
        ttkb.Label(rd2_frame, text="Silla 2:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        silla2_combo2 = ttkb.Combobox(
            rd2_frame,
            textvariable=self.variables['silla2_rd2'],
            values=["7", "8"],
            state="readonly"
        )
        silla2_combo2.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.variables['silla2_rd2'].trace_add("write", self._on_data_changed)
        
        # Evento Adverso RD2
        ttkb.Label(rd2_frame, text="Evento Adverso:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        evento_frame2 = ttkb.Frame(rd2_frame)
        evento_frame2.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        
        # Radio buttons for Evento Adverso RD2
        si_radio2 = ttkb.Radiobutton(
            evento_frame2,
            text="Sí",
            variable=self.variables['evento_adverso_rd2'],
            value="Sí"
        )
        si_radio2.pack(side=tk.LEFT, padx=(0, 10))
        
        no_radio2 = ttkb.Radiobutton(
            evento_frame2,
            text="No",
            variable=self.variables['evento_adverso_rd2'],
            value="No"
        )
        no_radio2.pack(side=tk.LEFT)
        self.variables['evento_adverso_rd2'].trace_add("write", self._on_data_changed)
        
        # Set default value for evento_adverso_rd2
        if not self.variables['evento_adverso_rd2'].get():
            self.variables['evento_adverso_rd2'].set("No")
        
        # Description and Observations RD2
        ttkb.Label(rd2_frame, text="Descripción:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        ttkb.Entry(
            rd2_frame,
            textvariable=self.variables['descripcion_rd2']
        ).grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        self.variables['descripcion_rd2'].trace_add("write", self._on_data_changed)
        
        ttkb.Label(rd2_frame, text="Observaciones:").grid(row=7, column=0, sticky="w", padx=5, pady=2)
        ttkb.Entry(
            rd2_frame,
            textvariable=self.variables['observaciones_rd2']
        ).grid(row=7, column=1, sticky="ew", padx=5, pady=2)
        self.variables['observaciones_rd2'].trace_add("write", self._on_data_changed)
        
        # Buttons
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        save_btn = ttkb.Button(
            button_frame,
            text="Guardar Datos",
            command=self.save_data,
            bootstyle="success",
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        clear_btn = ttkb.Button(
            button_frame,
            text="Limpiar Campos",
            command=self.clear_form,
            bootstyle="warning",
            width=15
        )
        clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def set_current_date(self):
        """Set current date in the date field using format DD-MM-AAAA."""
        today_str = datetime.now().strftime("%d-%m-%Y")
        self.variables["fecha"].set(today_str)
        self._on_data_changed() # Mark data as changed
    
    def load_data(self):
        print(f"[DEBUG] tab4_rd: load_data called, prevent_load_overwrite={self.prevent_load_overwrite}")
        if getattr(self, 'prevent_load_overwrite', False):
            return
        """Load RD data into the form fields."""
        # Get session number from data manager
        session_id = self.data_manager.current_data.get('vuelo', {}).get('numero_entrenamiento', '')
        # If no specific session ID, use vuelo_del_ano with year format
        if not session_id:
            # Get training number and format as X-YY
            vuelo_del_ano = self.data_manager.current_data.get('vuelo', {}).get('vuelo_del_ano', '')
            if vuelo_del_ano:
                # Get current year's last two digits
                year_suffix = datetime.now().strftime("%y")
                session_id = f"{vuelo_del_ano}-{year_suffix}"
        
        # Get RD data from data manager
        rd_data = {}
        
        # Try to load data specific to this session ID first
        sessions_data = self.data_manager.current_data.get('sessions_data', {})
        if session_id and session_id in sessions_data:
            session_data = sessions_data.get(session_id, {})
            rd_data = session_data.get('rd', {})
        else:
            # Fallback to legacy format
            rd_data = self.data_manager.current_data.get('rd', {})
        
        # Load data into variables, handling both legacy format and new format
        for var_name, var in self.variables.items():
            # Handle legacy data format
            if var_name == 'observador_interno_rd1' and 'observador_interno' in rd_data:
                var.set(rd_data.get('observador_interno', ''))
            elif var_name == 'alumno1_rd1' and 'alumno' in rd_data:
                var.set(rd_data.get('alumno', ''))
            elif var_name == 'silla1_rd1' and 'silla' in rd_data:
                var.set(rd_data.get('silla', ''))
            elif var_name == 'evento_adverso_rd1' and 'evento_adverso' in rd_data:
                var.set(rd_data.get('evento_adverso', 'No'))
            elif var_name == 'descripcion_rd1' and 'descripcion' in rd_data:
                var.set(rd_data.get('descripcion', ''))
            elif var_name == 'observaciones_rd1' and 'observaciones' in rd_data:
                var.set(rd_data.get('observaciones', ''))
            # Handle renamed fields for backward compatibility
            elif var_name == 'alumno1_rd1' and 'alumno_rd1' in rd_data:
                var.set(rd_data.get('alumno_rd1', ''))
            elif var_name == 'silla1_rd1' and 'silla_rd1' in rd_data:
                var.set(rd_data.get('silla_rd1', ''))
            elif var_name == 'alumno1_rd2' and 'alumno_rd2' in rd_data:
                var.set(rd_data.get('alumno_rd2', ''))
            elif var_name == 'silla1_rd2' and 'silla_rd2' in rd_data:
                var.set(rd_data.get('silla_rd2', ''))
            else:
                # Load directly from new format
                var.set(rd_data.get(var_name, ''))
                
            # Set default No for evento_adverso if empty
            if var_name in ['evento_adverso_rd1', 'evento_adverso_rd2'] and not var.get():
                var.set('No')
        
        self.rd_data = rd_data
    
    def _update_datamanager_with_own_data(self):
        """Helper method to update DataManager with this tab's data."""
        rd_data = {}
        for key, var in self.variables.items():
            rd_data[key] = var.get()
        
        self.data_manager.current_data['rd'] = rd_data
        
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
            self.data_manager.current_data['sessions_data'][session_id]['rd'] = rd_data
        print(f"Tab4: Updated RD data in DataManager for session {session_id}")

    def save_data(self, triggered_by_user=True):
        print(f"Tab4 save_data called, triggered_by_user={triggered_by_user}")
        self._update_datamanager_with_own_data()

        if triggered_by_user:
            if self.main_app:
                tabs_to_call = {
                    'tab1': getattr(self.main_app, 'tab1', None),
                    'tab2': getattr(self.main_app, 'tab2', None),
                    'tab3': getattr(self.main_app, 'tab3', None),
                    'tab6': getattr(self.main_app, 'tab6', None)
                }
                for tab_name, tab_instance in tabs_to_call.items():
                    if tab_instance and hasattr(tab_instance, 'save_data'):
                        print(f"Tab4 orchestrator: Calling save_data on {tab_name}")
                        tab_instance.save_data(triggered_by_user=False)

            self.data_manager.save_data()
            
            if self.main_app and hasattr(self.main_app, 'refresh_all_tabs'):
                self.main_app.refresh_all_tabs()
            
            messagebox.showinfo("Guardado", "Todos los datos han sido guardados exitosamente.", parent=self)
            self.prevent_load_overwrite = False
        else:
            self.prevent_load_overwrite = False
    
    def clear_form(self, confirm=True):
        """Clear all fields in this tab. Only show confirmation if confirm=True."""
        if confirm:
            if not messagebox.askyesno(
                "Confirmar",
                "¿Está seguro de limpiar los campos de perfil RD?\n\nEsta acción borrará los datos en esta pestaña."
            ):
                return
        # Clear all entry fields for RD
        for var in self.variables.values():
            var.set('')
        self.update_idletasks()
        self._on_data_changed() # Mark data as changed after clearing
    
    def cleanup_bindings(self, event=None):
        """Clean up event bindings to prevent errors when tab is destroyed."""
        try:
            # Only clean up if the event is for this widget being destroyed
            if event and event.widget != self:
                return
                
            # Clean up main canvas bindings
            if hasattr(self, 'main_bindings'):
                for widget, event_name, func in self.main_bindings:
                    try:
                        widget.unbind(event_name)
                    except:
                        pass
                        
            # Explicitly clean up canvas references
            if hasattr(self, 'main_canvas'):
                try:
                    self.main_canvas.delete("all")
                except:
                    pass
                    
            print("RDTab bindings cleaned up successfully")
        except Exception as e:
            print(f"Error cleaning up bindings: {e}")
