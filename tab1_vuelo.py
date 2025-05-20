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
import inspect

class VueloTab(ttkb.Frame):
    """Tab for managing flight data."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        self.main_app = main_app
        
        # Create variables for form fields
        self.variables = {}
        self.create_variables()
        
        # Training archives data
        self.training_archives = {}
        self.load_training_archives()
        
        # Create the layout
        self.create_widgets()
        
        # Add flag to prevent load_data from overwriting user input after new record
        self.prevent_load_overwrite = False
        
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
        self.variables['numero_entrenamiento'] = tk.StringVar()  # Session ID in X-YY format
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
        self.rowconfigure(1, weight=1)  # Main content - will expand with window
        
        # Header - moved down with more padding to avoid overlap with tab navigation
        header = ttkb.Label(
            self,
            text="Datos del entrenamiento de hipoxia hipobárica",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(15, 20))
        
        # Create a frame for the main content
        main_content_frame = ttkb.Frame(self)
        main_content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
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
        
        # -- Row 0 --
        # Fecha del entrenamiento (moved to first row in main form)
        date_entry = self._create_field(self.main_frame, current_row, 0, "Fecha del entrenamiento:", "fecha", width=15)
        
        # Add a small instruction label about date format right next to the entry field
        format_label = ttkb.Label(
            self.main_frame,
            text="(DD-MM-AAAA)",
            font=('Segoe UI', 9),
            bootstyle="secondary"
        )
        format_label.grid(row=current_row, column=2, padx=(0, 5), pady=5, sticky="w")
        
        # Add button for setting current date next to the format label
        set_date_btn = ttkb.Button(
            self.main_frame,
            text="Hoy",
            command=self.set_current_date,
            bootstyle="info-outline",
            width=6
        )
        set_date_btn.grid(row=current_row, column=3, padx=5, pady=5, sticky="w")
        current_row += 1
        
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
        # Director Médico - Changed to combobox with specific values
        self._create_field(self.main_frame, current_row, 0, "Director Médico:", "director_medico", 
                          widget_type="combobox", 
                          values=["MY LUIS EDUARDO JEREZ PALACIOS", "SMSM DIEGO L MALPICA H"],
                          width=35)
        # Jefe Técnico - Changed to combobox with specific list
        self._create_field(self.main_frame, current_row, 2, "Jefe Técnico:", "jefe_tecnico",
                          widget_type="combobox",
                          values=[
                              "CT DULZURA ANGELA MARIA RODRIGUEZ",
                              "ST JHEIMY KATERINE HUERTAS GIL",
                              "T1 CAÑON PÁEZ NIDIA",
                              "T2 JEISON JESUS ALTAMAR",
                              "T2 JULIAN SNAIDER OSORIO VANEGAS",
                              "Otro"
                          ],
                          width=35,
                          label_col_offset=1)
        current_row += 1
        
        # -- Row 6 --
        # Operador de Cámara with specific list and manual entry
        self._create_field(self.main_frame, current_row, 0, "Operador de Cámara:", "operador_camara",
                          widget_type="combobox",
                          values=[
                              "CT DULZURA ANGELA MARIA RODRIGUEZ",
                              "TS CARDONA ECHEVERRI BERNABE",
                              "T1 CAÑON PÁEZ NIDIA",
                              "T1 SALAMANCA LÓPEZ RAFAEL",
                              "T1 ALVARADO YEPES ANGIE CATHERINE",
                              "T2 JEISON JESUS ALTAMAR",
                              "Otro"
                          ],
                          width=35)
        # Registro with full list and manual entry
        self._create_field(self.main_frame, current_row, 2, "Registro:", "observador_registro", 
                          widget_type="combobox",
                          values=[
                              "MY LUIS EDUARDO JEREZ",
                              "CT PEDRO JOSE DIAZ BEDOYA",
                              "CT JORGE ELIECER GOMEZ",
                              "CT JAIME JUNIOR OSORIO",
                              "CT NATALY CALIMAN",
                              "CT DULZURA ANGELA MARIA RODRIGUEZ",
                              "CT DIANA MARIA HUERTAS",
                              "TE JOHANNA ROMERO",
                              "TE HASBLEIDY GISETH ALMANSA HERRERA",
                              "TE ASTRID VANESSA GUERRERO",
                              "ST JHEIMY KATERINE HUERTAS GIL",
                              "TS CARDONA ECHEVERRI BERNABE",
                              "T1 BUITRAGO BEDOYA EVER JONNY",
                              "T1 CAÑON PÁEZ NIDIA",
                              "T1 MUÑOZ BOCANEGRA JORGE ELIECER",
                              "T1 SALAMANCA LÓPEZ RAFAEL",
                              "T1 ALVARADO YEPES ANGIE CATHERINE",
                              "T1 SANDRA MILENA HERRERA CHAVEZ",
                              "T1 MARLEN ALEXANDRA QUIÑONES PAEZ",
                              "T1 CAROLINA CASTRO PUENTES",
                              "T2 JULIAN SNAIDER OSORIO VANEGAS",
                              "T2 SOCORRO MEJIA CARREÑO",
                              "T2 RICHARD MCLAREN SANCHEZ PEINADO",
                              "T2 JEISON JESUS ALTAMAR",
                              "T2 HANNELY DIAZ MEDINA",
                              "T2 DANIEL ORLANDO PINTO CORREAL",
                              "T3 VALERIA HINOJOSA",
                              "AT YORLENIS GISSEL CUESTA MORALES",
                              "AT EDGAR ESNEIDER CRUZ SALCEDO",
                              "SMSM DIEGO L MALPICA H",
                              "Otro"
                          ],
                          width=35,
                          label_col_offset=1)
        current_row += 1

        # -- Row 7 --
        # Lector with full list and manual entry
        self._create_field(self.main_frame, current_row, 0, "Lector:", "lector",
                          widget_type="combobox",
                          values=[
                              "MY LUIS EDUARDO JEREZ",
                              "CT PEDRO JOSE DIAZ BEDOYA",
                              "CT JORGE ELIECER GOMEZ",
                              "CT JAIME JUNIOR OSORIO",
                              "CT NATALY CALIMAN",
                              "CT DULZURA ANGELA MARIA RODRIGUEZ",
                              "CT DIANA MARIA HUERTAS",
                              "TE JOHANNA ROMERO",
                              "TE HASBLEIDY GISETH ALMANSA HERRERA",
                              "TE ASTRID VANESSA GUERRERO",
                              "ST JHEIMY KATERINE HUERTAS GIL",
                              "TS CARDONA ECHEVERRI BERNABE",
                              "T1 BUITRAGO BEDOYA EVER JONNY",
                              "T1 CAÑON PÁEZ NIDIA",
                              "T1 MUÑOZ BOCANEGRA JORGE ELIECER",
                              "T1 SALAMANCA LÓPEZ RAFAEL",
                              "T1 ALVARADO YEPES ANGIE CATHERINE",
                              "T1 SANDRA MILENA HERRERA CHAVEZ",
                              "T1 MARLEN ALEXANDRA QUIÑONES PAEZ",
                              "T1 CAROLINA CASTRO PUENTES",
                              "T2 JULIAN SNAIDER OSORIO VANEGAS",
                              "T2 SOCORRO MEJIA CARREÑO",
                              "T2 RICHARD MCLAREN SANCHEZ PEINADO",
                              "T2 JEISON JESUS ALTAMAR",
                              "T2 HANNELY DIAZ MEDINA",
                              "T2 DANIEL ORLANDO PINTO CORREAL",
                              "T3 VALERIA HINOJOSA",
                              "AT YORLENIS GISSEL CUESTA MORALES",
                              "AT EDGAR ESNEIDER CRUZ SALCEDO",
                              "SMSM DIEGO L MALPICA H",
                              "Otro"
                          ],
                          width=35)
        # Operador RD with specific list and manual entry
        self._create_field(self.main_frame, current_row, 2, "Operador RD:", "operador_rd",
                          widget_type="combobox",
                          values=[
                              "CT DULZURA ANGELA MARIA RODRIGUEZ",
                              "TS CARDONA ECHEVERRI BERNABE",
                              "T1 CAÑON PÁEZ NIDIA",
                              "T1 SALAMANCA LÓPEZ RAFAEL",
                              "T1 ALVARADO YEPES ANGIE CATHERINE",
                              "T2 JEISON JESUS ALTAMAR",
                              "Otro"
                          ],
                          width=35,
                          label_col_offset=1)
        current_row += 1

        # -- Row 8 --
        # OE-4 with full list and manual entry
        self._create_field(self.main_frame, current_row, 0, "OE-4:", "oe_4",
                          widget_type="combobox",
                          values=[
                              "MY LUIS EDUARDO JEREZ",
                              "CT PEDRO JOSE DIAZ BEDOYA",
                              "CT JORGE ELIECER GOMEZ",
                              "CT JAIME JUNIOR OSORIO",
                              "CT NATALY CALIMAN",
                              "CT DULZURA ANGELA MARIA RODRIGUEZ",
                              "CT DIANA MARIA HUERTAS",
                              "TE JOHANNA ROMERO",
                              "TE HASBLEIDY GISETH ALMANSA HERRERA",
                              "TE ASTRID VANESSA GUERRERO",
                              "ST JHEIMY KATERINE HUERTAS GIL",
                              "TS CARDONA ECHEVERRI BERNABE",
                              "T1 BUITRAGO BEDOYA EVER JONNY",
                              "T1 CAÑON PÁEZ NIDIA",
                              "T1 MUÑOZ BOCANEGRA JORGE ELIECER",
                              "T1 SALAMANCA LÓPEZ RAFAEL",
                              "T1 ALVARADO YEPES ANGIE CATHERINE",
                              "T1 SANDRA MILENA HERRERA CHAVEZ",
                              "T1 MARLEN ALEXANDRA QUIÑONES PAEZ",
                              "T1 CAROLINA CASTRO PUENTES",
                              "T2 JULIAN SNAIDER OSORIO VANEGAS",
                              "T2 SOCORRO MEJIA CARREÑO",
                              "T2 RICHARD MCLAREN SANCHEZ PEINADO",
                              "T2 JEISON JESUS ALTAMAR",
                              "T2 HANNELY DIAZ MEDINA",
                              "T2 DANIEL ORLANDO PINTO CORREAL",
                              "T3 VALERIA HINOJOSA",
                              "AT YORLENIS GISSEL CUESTA MORALES",
                              "AT EDGAR ESNEIDER CRUZ SALCEDO",
                              "SMSM DIEGO L MALPICA H",
                              "Otro"
                          ],
                          width=35)
        # OE-5 with full list and manual entry
        self._create_field(self.main_frame, current_row, 2, "OE-5:", "oe_5",
                          widget_type="combobox",
                          values=[
                              "MY LUIS EDUARDO JEREZ",
                              "CT PEDRO JOSE DIAZ BEDOYA",
                              "CT JORGE ELIECER GOMEZ",
                              "CT JAIME JUNIOR OSORIO",
                              "CT NATALY CALIMAN",
                              "CT DULZURA ANGELA MARIA RODRIGUEZ",
                              "CT DIANA MARIA HUERTAS",
                              "TE JOHANNA ROMERO",
                              "TE HASBLEIDY GISETH ALMANSA HERRERA",
                              "TE ASTRID VANESSA GUERRERO",
                              "ST JHEIMY KATERINE HUERTAS GIL",
                              "TS CARDONA ECHEVERRI BERNABE",
                              "T1 BUITRAGO BEDOYA EVER JONNY",
                              "T1 CAÑON PÁEZ NIDIA",
                              "T1 MUÑOZ BOCANEGRA JORGE ELIECER",
                              "T1 SALAMANCA LÓPEZ RAFAEL",
                              "T1 ALVARADO YEPES ANGIE CATHERINE",
                              "T1 SANDRA MILENA HERRERA CHAVEZ",
                              "T1 MARLEN ALEXANDRA QUIÑONES PAEZ",
                              "T1 CAROLINA CASTRO PUENTES",
                              "T2 JULIAN SNAIDER OSORIO VANEGAS",
                              "T2 SOCORRO MEJIA CARREÑO",
                              "T2 RICHARD MCLAREN SANCHEZ PEINADO",
                              "T2 JEISON JESUS ALTAMAR",
                              "T2 HANNELY DIAZ MEDINA",
                              "T2 DANIEL ORLANDO PINTO CORREAL",
                              "T3 VALERIA HINOJOSA",
                              "AT YORLENIS GISSEL CUESTA MORALES",
                              "AT EDGAR ESNEIDER CRUZ SALCEDO",
                              "SMSM DIEGO L MALPICA H",
                              "Otro"
                          ],
                          width=35,
                          label_col_offset=1)
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
        
        new_record_btn = ttkb.Button(
            button_frame,
            text="Crear nuevo registro",
            command=self.create_new_record,
            bootstyle="primary",
            width=20
        )
        new_record_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
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
            command=self.load_training_archives,
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
                width=width - 2  # Combobox width is slightly different
            )
        else:
            # Fallback for unknown types
            widget = ttkb.Label(parent, text=f"Unknown widget: {widget_type}")

        widget.grid(row=row, column=widget_column, padx=5, pady=5, sticky="we") # Use sticky 'we' to expand
        
        # Add trace to update prevent_load_overwrite flag when data changes
        self.variables[var_name].trace_add("write", self._on_data_changed)
        
        return widget
    
    def _on_data_changed(self, *args):
        """Callback when any StringVar in this tab is written to."""
        if not self.prevent_load_overwrite:
            print(f"VueloTab: Data changed, setting prevent_load_overwrite = True")
            self.prevent_load_overwrite = True
    
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
        # Prevent overwriting user input if flag is set
        if getattr(self, 'prevent_load_overwrite', False):
            return False
        # Get flight data from data manager
        flight_data = self.data_manager.current_data.get('vuelo', {})
        # Load data into variables
        for var_name, var in self.variables.items():
            var.set(flight_data.get(var_name, ''))
        return bool(flight_data)
    
    def _update_datamanager_with_own_data(self):
        """Helper method to update DataManager with this tab's data."""
        vuelo_data = {}
        for var_name, var in self.variables.items():
            vuelo_data[var_name] = var.get()
        
        if not vuelo_data.get('numero_entrenamiento'):
            vuelo_del_ano = vuelo_data.get('vuelo_del_ano', '')
            if vuelo_del_ano:
                try:
                    # Ensure vuelo_del_ano is a number before formatting
                    int(vuelo_del_ano) 
                    year_suffix = datetime.now().strftime("%y")
                    vuelo_data['numero_entrenamiento'] = f"{vuelo_del_ano}-{year_suffix}"
                    if 'numero_entrenamiento' in self.variables:
                        self.variables['numero_entrenamiento'].set(vuelo_data['numero_entrenamiento'])
                    print(f"Generando número de entrenamiento: {vuelo_data['numero_entrenamiento']}")
                except ValueError:
                    print(f"Error: vuelo_del_ano '{vuelo_del_ano}' no es un número válido para generar numero_entrenamiento.")
        
        session_id = vuelo_data.get('numero_entrenamiento', '')
        
        self.data_manager.current_data['vuelo'] = vuelo_data.copy()
        
        if 'sessions_data' not in self.data_manager.current_data:
            self.data_manager.current_data['sessions_data'] = {}
            
        if session_id:
            if session_id not in self.data_manager.current_data['sessions_data']:
                self.data_manager.current_data['sessions_data'][session_id] = {}
            if 'vuelo' not in self.data_manager.current_data['sessions_data'][session_id]:
                 self.data_manager.current_data['sessions_data'][session_id]['vuelo'] = {}
            self.data_manager.current_data['sessions_data'][session_id]['vuelo'].update(vuelo_data)
        print(f"Tab1: Updated vuelo data in DataManager: {vuelo_data.get('numero_entrenamiento')}")
        return vuelo_data # Return for archive purposes

    def save_data(self, triggered_by_user=True):
        """Save form data, orchestrating other tabs if triggered by user."""
        print(f"Tab1 save_data called, triggered_by_user={triggered_by_user}")
        vuelo_data_for_archive = self._update_datamanager_with_own_data()
        
        if triggered_by_user:
            if self.main_app:
                tabs_to_call = {
                    'tab2': getattr(self.main_app, 'tab2', None),
                    'tab3': getattr(self.main_app, 'tab3', None),
                    'tab4': getattr(self.main_app, 'tab4', None),
                    'tab6': getattr(self.main_app, 'tab6', None)
                }
                for tab_name, tab_instance in tabs_to_call.items():
                    if tab_instance and hasattr(tab_instance, 'save_data'):
                        print(f"Tab1 orchestrator: Calling save_data on {tab_name}")
                        tab_instance.save_data(triggered_by_user=False)
            
            self.data_manager.save_data()
            
            # Save to training archive after all data is potentially updated in current_data
            self.save_to_training_archive(vuelo_data_for_archive)
            
            messagebox.showinfo("Guardado", "Todos los datos han sido guardados exitosamente.", parent=self)
            self.prevent_load_overwrite = False
        else:
            # This call is from another tab.
            # _update_datamanager_with_own_data has already run.
            # The orchestrating tab will call self.data_manager.save_data() and show the message.
            # The archive is handled by _update_datamanager_with_own_data -> save_to_training_archive for now, though might be revisited.
            self.prevent_load_overwrite = False
    
    def create_new_record(self):
        """Create a new record and clear all fields, set flag to prevent load_data from overwriting user input."""
        # Reset the data manager's current data to a clean state
        self.data_manager.clear_data()

        # Ensure a minimal structure is present after clearing if necessary,
        # or rely on individual tabs/DataManager to handle missing keys gracefully.
        # For example, ensure essential keys for saving/loading are initialized if clear_data() makes current_data strictly {}.
        # Most tab load_data methods use .get('key', {}) which handles missing keys.
        # The save_data in DataManager also initializes 'sessions_data' if missing.

        # Clear all tabs (no confirmation in sub-tabs)
        if self.main_app:
            if hasattr(self.main_app, 'tab2') and hasattr(self.main_app.tab2, 'clear_form'):
                self.main_app.tab2.clear_form(confirm=False)
                self.main_app.tab2.prevent_load_overwrite = True
            if hasattr(self.main_app, 'tab3') and hasattr(self.main_app.tab3, 'clear_form'):
                self.main_app.tab3.clear_form(confirm=False)
                self.main_app.tab3.prevent_load_overwrite = True
            if hasattr(self.main_app, 'tab3') and hasattr(self.main_app.tab3, 'clear_display'):
                sig = inspect.signature(self.main_app.tab3.clear_display)
                if 'confirm' in sig.parameters:
                    self.main_app.tab3.clear_display(confirm=False)
                else:
                    self.main_app.tab3.clear_display()
            if hasattr(self.main_app, 'tab4') and hasattr(self.main_app.tab4, 'clear_form'):
                self.main_app.tab4.clear_form(confirm=False)
                self.main_app.tab4.prevent_load_overwrite = True
            if hasattr(self.main_app, 'tab5') and hasattr(self.main_app.tab5, 'clear_form'):
                self.main_app.tab5.clear_form(confirm=False)
                self.main_app.tab5.prevent_load_overwrite = True
            if hasattr(self.main_app, 'tab5') and hasattr(self.main_app.tab5, 'clear_display'):
                sig = inspect.signature(self.main_app.tab5.clear_display)
                if 'confirm' in sig.parameters:
                    self.main_app.tab5.clear_display(confirm=False)
                else:
                    self.main_app.tab5.clear_display()
            if hasattr(self.main_app, 'tab6') and hasattr(self.main_app.tab6, 'clear_all_symptoms'):
                sig = inspect.signature(self.main_app.tab6.clear_all_symptoms)
                if 'confirm' in sig.parameters:
                    self.main_app.tab6.clear_all_symptoms(confirm=False)
                else:
                    self.main_app.tab6.clear_all_symptoms()
                self.main_app.tab6.prevent_load_overwrite = True
        # Clear this tab's fields (no confirmation)
        self.clear_form(confirm=False)
        # Set new training numbers and date
        training_year = self.get_next_training_year()
        total_trainings = self.get_next_total_trainings()
        self.variables['vuelo_del_ano'].set(str(training_year))
        self.variables['vuelo_total'].set(str(total_trainings))
        year_suffix = datetime.now().strftime("%y")
        if 'numero_entrenamiento' not in self.variables:
            self.variables['numero_entrenamiento'] = tk.StringVar()
        self.variables['numero_entrenamiento'].set(f"{training_year}-{year_suffix}")
        self.set_current_date()
        # Set the flag to prevent load_data from overwriting user input
        self.prevent_load_overwrite = True
        messagebox.showinfo("Nuevo Registro", "Nuevo registro creado exitosamente")
    
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
    
    def clear_form(self, confirm=True):
        """Clear all fields in this tab. Only show confirmation if confirm=True."""
        if confirm:
            if not messagebox.askyesno(
                "Confirmar",
                "¿Está seguro de limpiar los campos del presente registro? Esta acción borrará los datos en esta pestaña."
            ):
                return
        # Clear all variables in this tab
        for field_name, var in self.variables.items():
            if field_name == 'perfil_camara':
                var.set("IV-A")
            elif field_name == 'curso':
                var.set("Primera vez")
            else:
                var.set('')
        self.set_current_date()
        # Do NOT reset data_manager.current_data here
        self.update_idletasks()
    
    def load_training_archives(self):
        """Load saved training archives from JSON file(s) in data/.
           Primarily looks for current_session.json and treats it as an archive item.
        """
        self.training_archives = {} # Clear existing in-memory archives
        print("VueloTab: Cleared in-memory training_archives.")

        try:
            # Define the path to current_session.json directly in the data directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Assuming tab1_vuelo.py is in the project root, so data/ is a subdirectory
            # If tab1_vuelo.py is itself in a subdirectory, adjust os.path.dirname count
            data_dir = os.path.join(base_dir, 'data')
            current_session_file_path = os.path.join(data_dir, 'current_session.json')

            print(f"VueloTab: Attempting to load archive from: {current_session_file_path}")

            if os.path.exists(current_session_file_path):
                with open(current_session_file_path, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                print(f"VueloTab: Successfully loaded and parsed {current_session_file_path}")

                # Extract necessary info to display this session in the archive list
                datos_vuelo = session_data.get('datos_vuelo', {})
                fecha = datos_vuelo.get('fecha', 'Fecha Desconocida')
                vuelo_del_ano = datos_vuelo.get('vuelo_del_ano', 'N/A')
                
                # Create a unique ID for this archive entry
                # If datos_vuelo has numero_entrenamiento, use that, otherwise create one.
                training_id = datos_vuelo.get('numero_entrenamiento')
                if not training_id:
                    year_suffix = 'XX' # Default if date parsing fails
                    if fecha != 'Fecha Desconocida':
                        try:
                            date_obj = datetime.strptime(fecha, "%d-%m-%Y") # Assuming DD-MM-YYYY
                            year_suffix = date_obj.strftime("%y")
                        except ValueError:
                            try: 
                                date_obj = datetime.strptime(fecha, "%d/%m/%Y")
                                year_suffix = date_obj.strftime("%y")
                            except ValueError:
                                 print(f"VueloTab: Could not parse date '{fecha}' to get year for training_id.")
                    training_id = f"{vuelo_del_ano}-{year_suffix}_current_session"
                else:
                    training_id = f"{training_id}_current_session" # Ensure it's unique if it might clash


                self.training_archives[training_id] = {
                    'fecha': fecha,
                    'vuelo_del_ano': vuelo_del_ano,
                    'source_file': 'current_session.json', # Mark its origin
                    'display_name': f"Sesión Actual Guardada ({fecha} - Vuelo {vuelo_del_ano})",
                    'numero_entrenamiento': datos_vuelo.get('numero_entrenamiento') # Store original if present
                }
                print(f"VueloTab: Added '{training_id}' to in-memory training_archives.")
            else:
                print(f"VueloTab: Archive file not found: {current_session_file_path}. No archives loaded from it.")
                # self.training_archives remains empty or only contains other sources if any were added
            
            # Refresh the UI list based on what was found (or not found)
            if hasattr(self, 'trainings_container'):
                self.refresh_training_list()
                
        except json.JSONDecodeError as e_json:
            print(f"VueloTab: Error decoding JSON from {current_session_file_path}: {e_json}")
            messagebox.showerror("Error de Archivo", 
                                 f"El archivo 'current_session.json' está corrupto o no es un JSON válido.\n"
                                 f"Verifique el archivo en la carpeta 'data'.\nDetalle: {e_json}", parent=self)
            self.training_archives = {} # Reset to empty on error
            if hasattr(self, 'trainings_container'):
                self.refresh_training_list()
        except Exception as e:
            print(f"VueloTab: General error loading training archives: {e}")
            messagebox.showerror("Error de Carga", 
                                 f"No se pudieron cargar los archivos de entrenamiento desde 'data/current_session.json'.\nDetalle: {e}", parent=self)
            self.training_archives = {} # Reset to empty on error
            if hasattr(self, 'trainings_container'):
                self.refresh_training_list()
    
    def save_to_training_archive(self, training_data):
        """Save the current training data to the archives (current_session.json and training_archives.json)."""
        # This method might need revision if we are no longer primarily using training_archives.json
        # For now, it will attempt to save to training_archives.json in data/archives (legacy path)
        # and also update current_session.json in data/
        try:
            # --- Save to current_session.json (in data/) ---
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, 'data')
            current_session_file_path = os.path.join(data_dir, 'current_session.json')
            
            # We need to save the *entire current state* from DataManager to current_session.json
            # This reflects what would be loaded if this session is chosen from the archive list.
            data_to_save_in_current_session = {}
            if self.data_manager and hasattr(self.data_manager, 'current_data'):
                # Create a structured dict similar to what current_session.json looks like
                # or directly dump parts of current_data.
                # The user provided current_session.json seems to be a flat structure of the *active* session data.
                # So, we replicate that.
                full_current_data = self.data_manager.current_data
                data_to_save_in_current_session['event_times'] = full_current_data.get('event_times', {})
                data_to_save_in_current_session['last_saved'] = datetime.now().isoformat()
                data_to_save_in_current_session['reactions_data'] = full_current_data.get('reactions_data', [])
                data_to_save_in_current_session['datos_vuelo'] = full_current_data.get('vuelo', {})
                data_to_save_in_current_session['participantes'] = full_current_data.get('participantes', {})
                data_to_save_in_current_session['student_symptoms'] = full_current_data.get('student_symptoms', {})
                data_to_save_in_current_session['rd'] = full_current_data.get('rd', {})
                data_to_save_in_current_session['student_hypoxia_end_times'] = full_current_data.get('student_hypoxia_end_times', {})
                data_to_save_in_current_session['displayed_calculated_totals'] = full_current_data.get('displayed_calculated_totals', {})

            with open(current_session_file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save_in_current_session, f, ensure_ascii=False, indent=4)
            print(f"VueloTab: Saved current session details to {current_session_file_path}")

            # --- Legacy: Attempt to save to training_archives.json in data/archives/ ---
            # This part maintains the old behavior for training_archives.json but it's now secondary.
            # The primary load mechanism for the list is now from current_session.json.
            date = training_data.get('fecha', datetime.now().strftime("%d-%m-%Y"))
            training_year_num = training_data.get('vuelo_del_ano', '0')
            training_id_legacy = f"{date}_{training_year_num}" # Legacy ID format
            
            # Add timestamp for sorting (for the legacy file)
            training_data_for_legacy_archive = training_data.copy()
            training_data_for_legacy_archive['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Load existing legacy archives if any
            legacy_archives_dir = os.path.join(base_dir, 'data', 'archives')
            os.makedirs(legacy_archives_dir, exist_ok=True)
            legacy_archives_file = os.path.join(legacy_archives_dir, 'training_archives.json')
            
            current_legacy_archives = {}
            if os.path.exists(legacy_archives_file):
                try:
                    with open(legacy_archives_file, 'r', encoding='utf-8') as f:
                        current_legacy_archives = json.load(f)
                except json.JSONDecodeError:
                    print(f"VueloTab: Legacy training_archives.json is corrupt. Overwriting.")
            
            current_legacy_archives[training_id_legacy] = training_data_for_legacy_archive
            
            with open(legacy_archives_file, 'w', encoding='utf-8') as f:
                json.dump(current_legacy_archives, f, ensure_ascii=False, indent=4)
            print(f"VueloTab: Updated legacy training_archives.json at {legacy_archives_file}")

            # Also save full data from all tabs to a separate archive file (training_full_data.json in data/archives/)
            # This uses the legacy training_id
            self.save_full_training_data(training_id_legacy)
            
            # Refresh the training list UI (which now primarily reflects current_session.json)
            self.load_training_archives() # Reload to ensure UI consistency
            
        except Exception as e:
            print(f"VueloTab: Error saving to training archive (current_session.json or legacy): {e}")
            messagebox.showerror("Error de Guardado", f"No se pudo guardar el archivo de la sesión actual.\nDetalle: {e}", parent=self)
            
    def save_full_training_data(self, training_id_legacy):
        """Save data from all tabs to training_full_data.json using a legacy training_id."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            archives_dir = os.path.join(base_dir, 'data', 'archives') # Path to data/archives/
            os.makedirs(archives_dir, exist_ok=True)
            
            full_data_file = os.path.join(archives_dir, 'training_full_data.json')
            
            all_training_data_legacy = {}
            if os.path.exists(full_data_file):
                try:
                    with open(full_data_file, 'r', encoding='utf-8') as f:
                        all_training_data_legacy = json.load(f)
                except json.JSONDecodeError:
                    print(f"VueloTab: Legacy training_full_data.json is corrupt. Overwriting with current session.")
            
            # Get current data from DataManager to save for this legacy training_id
            current_data_snapshot = {}
            if self.data_manager and hasattr(self.data_manager, 'current_data'):
                full_current_data = self.data_manager.current_data
                # Replicate structure expected by load_archived_data if needed, or just dump current_data directly
                # For training_full_data.json, the structure is usually a direct dump of the relevant parts of current_data.
                current_data_snapshot['vuelo'] = full_current_data.get('vuelo', {})
                current_data_snapshot['participantes'] = full_current_data.get('participantes', {})
                current_data_snapshot['event_times'] = full_current_data.get('event_times', {})
                current_data_snapshot['student_hypoxia_end_times'] = full_current_data.get('student_hypoxia_end_times', {})
                current_data_snapshot['rd'] = full_current_data.get('rd', {})
                current_data_snapshot['reactions_data'] = full_current_data.get('reactions_data', [])
                current_data_snapshot['student_symptoms'] = full_current_data.get('student_symptoms', {})
                current_data_snapshot['displayed_calculated_totals'] = full_current_data.get('displayed_calculated_totals', {})
                # Note: 'sessions_data' from current_data is generally not saved into a specific training's full data bundle.

            all_training_data_legacy[training_id_legacy] = current_data_snapshot
            
            with open(full_data_file, 'w', encoding='utf-8') as f:
                json.dump(all_training_data_legacy, f, ensure_ascii=False, indent=4)
                
            print(f"VueloTab: Full data for legacy training ID {training_id_legacy} saved to {full_data_file}")
                
        except Exception as e:
            print(f"VueloTab: Error saving full training data for legacy ID {training_id_legacy}: {e}")
    
    def save_training_archives(self):
        """Save the training archives to JSON file (legacy: data/archives/training_archives.json)."""
        # This method is now mostly for the legacy training_archives.json
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            archives_dir = os.path.join(base_dir, 'data', 'archives')
            os.makedirs(archives_dir, exist_ok=True)
            
            archives_file_path = os.path.join(archives_dir, 'training_archives.json')
            
            # self.training_archives here might be the one populated by load_training_archives,
            # which would only contain the current_session.json entry. This is not what we want for the *legacy* file.
            # This needs to be rethought or this function deprecated if current_session.json is the sole archive source.
            # For now, let it save whatever is in self.training_archives, which might be just the current_session view.
            # To truly maintain legacy training_archives.json, it would need to load it, update it, then save.
            # However, the primary load is from current_session.json, so this legacy file is less critical for loading.
            
            # Let's try to load existing legacy archives first to merge, to be safer.
            legacy_archives_data = {}
            if os.path.exists(archives_file_path):
                try:
                    with open(archives_file_path, 'r', encoding='utf-8') as f:
                        legacy_archives_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Legacy training_archives.json at {archives_file_path} is corrupt. It may be overwritten.")
            
            # Merge self.training_archives (which might just be the current_session view)
            # into the loaded legacy_archives_data. This is imperfect.
            # A better approach would be needed if both systems must coexist perfectly.
            for key, value in self.training_archives.items():
                # If the key is the one generated for current_session.json, 
                # we might want to map it to a legacy-style key if it's going into training_archives.json
                if value.get('source_file') == 'current_session.json':
                    original_numero_entrenamiento = value.get('numero_entrenamiento')
                    original_fecha = value.get('fecha')
                    if original_numero_entrenamiento: # Use if available
                        legacy_key = f"{original_fecha}_{original_numero_entrenamiento.split('-')[0] if original_numero_entrenamiento else value.get('vuelo_del_ano','0')}"
                    else:
                        legacy_key = f"{original_fecha}_{value.get('vuelo_del_ano','0')}"
                    legacy_archives_data[legacy_key] = value # Save the summary from current_session
                else:
                    legacy_archives_data[key] = value # For any other types of archive entries if they exist

            with open(archives_file_path, 'w', encoding='utf-8') as f:
                json.dump(legacy_archives_data, f, ensure_ascii=False, indent=4)
            print(f"VueloTab: Saved/Updated legacy training_archives.json at {archives_file_path}")
                
        except Exception as e:
            print(f"VueloTab: Error saving legacy training_archives.json: {e}")
    
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
            # Use display_name if available (for current_session.json entry), else construct.
            display_name = training_data.get('display_name')
            if not display_name:
                total_num = training_data.get('vuelo_total', '?') # This might not be in current_session entry
                display_name = f"Fecha: {date} | Entrenamiento: #{training_num}"
                if total_num != '?':
                    display_name += f" | Total: #{total_num}"

            # Load additional information from the full data archive if available
            # This part needs to be adapted if we are loading from current_session.json directly
            additional_info = ""
            student_count = 0
            
            try:
                # Check if full data exists for this training
                archives_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'archives')
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
            
            # Simplified display text: only show date and training number
            display_text = f"Fecha: {date} | Entrenamiento: #{training_num}"
            
            training_label = ttkb.Label(
                training_frame,
                text=display_name, # Use the prepared display_name
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

            # Add delete button
            delete_btn = ttkb.Button(
                training_frame,
                text="Eliminar",
                command=lambda t_id=training_id: self.delete_training(t_id),
                bootstyle="danger-outline",
                width=8
            )
            delete_btn.grid(row=0, column=2, sticky="e", padx=5, pady=3)
            
            # Add divider
            ttkb.Separator(self.trainings_container, orient="horizontal").pack(fill=tk.X, padx=5, pady=1, expand=True)
    
    def load_training(self, training_id):
        """Load a specific training into the form and all other tabs."""
        
        if training_id not in self.training_archives:
            messagebox.showerror("Error", f"No se encontró el entrenamiento con ID interno {training_id}", parent=self)
            return
        
        archive_entry_info = self.training_archives[training_id]
        source_file = archive_entry_info.get('source_file')

        confirm = messagebox.askyesno(
            "Confirmar Carga de Entrenamiento",
            "ADVERTENCIA: Esta acción reemplazará todos los datos de la sesión actual en todas las pestañas con los datos del entrenamiento seleccionado."
            "Los cambios NO se guardarán permanentemente en el archivo de configuración principal (current_data.json) hasta que usted presione 'Guardar Datos' explícitamente en alguna pestaña."
            "¿Desea continuar y cargar el entrenamiento en su sesión de trabajo actual?",
            icon="warning",
            parent=self
        )
        
        if not confirm:
            return

        # 1. Clear DataManager's current working data
        self.data_manager.clear_data() # self.data_manager.current_data is now {}
        print("VueloTab: DataManager current_data cleared.")

        loaded_successfully = False
        actual_session_id_for_datamanager = None

        if source_file == 'current_session.json':
            print(f"VueloTab: Loading from source file: {source_file}")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, 'data')
            file_to_load_path = os.path.join(data_dir, source_file)
            
            if os.path.exists(file_to_load_path):
                try:
                    with open(file_to_load_path, 'r', encoding='utf-8') as f:
                        loaded_json_data = json.load(f)
                    print(f"VueloTab: Successfully parsed {file_to_load_path}")

                    # Map data from current_session.json structure to DataManager.current_data
                    self.data_manager.current_data['vuelo'] = loaded_json_data.get('datos_vuelo', {})
                    self.data_manager.current_data['participantes'] = loaded_json_data.get('participantes', {})
                    self.data_manager.current_data['event_times'] = loaded_json_data.get('event_times', {})
                    self.data_manager.current_data['student_hypoxia_end_times'] = loaded_json_data.get('student_hypoxia_end_times', {})
                    self.data_manager.current_data['rd'] = loaded_json_data.get('rd', {})
                    self.data_manager.current_data['reactions_data'] = loaded_json_data.get('reactions_data', [])
                    self.data_manager.current_data['student_symptoms'] = loaded_json_data.get('student_symptoms', {})
                    self.data_manager.current_data['displayed_calculated_totals'] = loaded_json_data.get('displayed_calculated_totals', {})
                    # Ensure 'sessions_data' exists, though it might be empty after clear_data()
                    self.data_manager.current_data.setdefault('sessions_data', {}) 

                    # Determine/ensure numero_entrenamiento (session_id for DataManager)
                    vuelo_data = self.data_manager.current_data['vuelo']
                    actual_session_id_for_datamanager = vuelo_data.get('numero_entrenamiento')
                    if not actual_session_id_for_datamanager:
                        vuelo_del_ano = vuelo_data.get('vuelo_del_ano', 'N/A')
                        fecha_str = vuelo_data.get('fecha', '')
                        year_suffix = 'XX'
                        if fecha_str:
                            try:
                                date_obj = datetime.strptime(fecha_str, "%d-%m-%Y")
                                year_suffix = date_obj.strftime("%y")
                            except ValueError:
                                try: 
                                    date_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
                                    year_suffix = date_obj.strftime("%y")
                                except ValueError:
                                     print(f"VueloTab: Could not parse date '{fecha_str}' from loaded vuelo_data.")
                        actual_session_id_for_datamanager = f"{vuelo_del_ano}-{year_suffix}"
                        vuelo_data['numero_entrenamiento'] = actual_session_id_for_datamanager
                    
                    # If a session ID was determined, place this loaded data into current_data.sessions_data[session_id]
                    if actual_session_id_for_datamanager:
                        snapshot_of_loaded_data = {
                            'vuelo': self.data_manager.current_data['vuelo'],
                            'participantes': self.data_manager.current_data['participantes'],
                            'event_times': self.data_manager.current_data['event_times'],
                            'student_hypoxia_end_times': self.data_manager.current_data['student_hypoxia_end_times'],
                            'rd': self.data_manager.current_data['rd'],
                            'reactions_data': self.data_manager.current_data['reactions_data'],
                            'student_symptoms': self.data_manager.current_data['student_symptoms'],
                            'displayed_calculated_totals': self.data_manager.current_data['displayed_calculated_totals']
                        }
                        self.data_manager.current_data['sessions_data'][actual_session_id_for_datamanager] = snapshot_of_loaded_data
                        print(f"VueloTab: Populated sessions_data for ID '{actual_session_id_for_datamanager}'")

                    loaded_successfully = True
                except json.JSONDecodeError as e_json:
                    messagebox.showerror("Error de Carga", f"No se pudo decodificar el archivo JSON: {file_to_load_path}.\\nDetalle: {e_json}", parent=self)
                except Exception as e_load:
                    messagebox.showerror("Error de Carga", f"Error al cargar el archivo: {file_to_load_path}.\\nDetalle: {e_load}", parent=self)
            else:
                messagebox.showerror("Error de Carga", f"El archivo de sesión especificado no existe: {file_to_load_path}", parent=self)
        else:
            # This branch would be for the old archive system, which is likely not being populated if data/archives is empty.
            # Fallback or error if training_id is not from current_session.json
            messagebox.showerror("Error de Carga", f"Tipo de archivo de origen no reconocido o no implementado para ID: {training_id}", parent=self)
            return # Exit if not loading from current_session.json for now

        if loaded_successfully:
            # Update VueloTab's own UI fields (self.variables) from the newly populated self.data_manager.current_data['vuelo']
            vuelo_data_for_ui = self.data_manager.current_data.get('vuelo', {})
            for field_name, var_tk in self.variables.items():
                var_tk.set(vuelo_data_for_ui.get(field_name, ''))
            print("VueloTab: UI fields updated from loaded data.")

            # Reset prevent_load_overwrite to False for all relevant tabs to allow them to load new current_data
            if self.main_app:
                tabs_to_update = ['tab1', 'tab2', 'tab3', 'tab4', 'tab5', 'tab6', 'tab7']
                for tab_attr_name in tabs_to_update:
                    if hasattr(self.main_app, tab_attr_name):
                        tab_instance = getattr(self.main_app, tab_attr_name)
                        if hasattr(tab_instance, 'prevent_load_overwrite'):
                            tab_instance.prevent_load_overwrite = False
                            print(f"VueloTab: Reset prevent_load_overwrite for {tab_attr_name}.")
            
            messagebox.showinfo(
                "Carga Completada en Sesión Actual",
                "El entrenamiento ha sido cargado en su sesión de trabajo actual desde 'current_session.json'."
                "Revise los datos en todas las pestañas."
                "Para hacer estos cambios permanentes en el archivo de configuración principal (current_data.json), presione 'Guardar Datos' en la pestaña correspondiente.",
                parent=self
            )
            
            if self.main_app and hasattr(self.main_app, 'refresh_all_tabs'):
                self.main_app.refresh_all_tabs()
                print("VueloTab: main_app.refresh_all_tabs() called.")
        else:
            # If loading failed, potentially reload original state or inform user further.
            # For now, DataManager might be in a cleared state if loading didn't repopulate it.
            # It might be better to reload previous state or default state if load fails mid-way.
            print("VueloTab: Loading from current_session.json failed. DataManager might be empty or partially loaded.")
            # Optionally, re-trigger a load of current_data.json or default state if robust error recovery is needed here.
            # self.data_manager.load_data() # This would reload current_data.json
    
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
                    archives_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'archives')
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
                    archives_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'archives')
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

    def delete_training(self, training_id):
        """Delete a specific training from the archives and full data."""
        if training_id not in self.training_archives:
            messagebox.showerror("Error", f"No se encontró el entrenamiento con ID {training_id}")
            return
        confirm = messagebox.askyesno(
            "Eliminar Entrenamiento",
            "¿Está seguro que desea eliminar este entrenamiento? Esta acción no se puede deshacer.",
            icon="warning"
        )
        if not confirm:
            return
        try:
            # Remove from training_archives and save
            del self.training_archives[training_id]
            self.save_training_archives()
            # Remove from training_full_data.json if exists
            archives_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'archives')
            full_data_file = os.path.join(archives_dir, 'training_full_data.json')
            if os.path.exists(full_data_file):
                with open(full_data_file, 'r', encoding='utf-8') as f:
                    all_training_data = json.load(f)
                if training_id in all_training_data:
                    del all_training_data[training_id]
                    with open(full_data_file, 'w', encoding='utf-8') as f:
                        json.dump(all_training_data, f, ensure_ascii=False, indent=4)
            self.refresh_training_list()
            messagebox.showinfo("Eliminado", "El entrenamiento ha sido eliminado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar el entrenamiento: {e}")

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
