#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox, filedialog
from typing import Dict, Any
import json
import os
from datetime import datetime
import pandas as pd

class ReportesTab(ttkb.Frame):
    """Tab for generating and managing reports."""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        
        # Create variables
        self.variables = {}
        self.create_variables()
        
        # Create the layout
        self.create_widgets()
    
    def create_variables(self):
        """Create variables for form fields."""
        self.variables['fecha_inicio'] = tk.StringVar()
        self.variables['fecha_fin'] = tk.StringVar()
        self.variables['tipo_reporte'] = tk.StringVar(value='vuelo')
        self.variables['formato_salida'] = tk.StringVar(value='excel')
    
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Header
        header = ttkb.Label(
            self,
            text="Generación de Reportes",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Report criteria frame
        criteria_frame = ttkb.Labelframe(
            self,
            text="Criterios del Reporte",
            padding=10
        )
        criteria_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        criteria_frame.columnconfigure(1, weight=1)
        
        # Date range
        date_label = ttkb.Label(criteria_frame, text="Rango de Fechas:")
        date_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        date_frame = ttkb.Frame(criteria_frame)
        date_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        start_date = ttkb.DateEntry(
            date_frame,
            textvariable=self.variables['fecha_inicio'],
            width=12,
            bootstyle="primary"
        )
        start_date.pack(side=tk.LEFT, padx=5)
        
        ttkb.Label(date_frame, text="hasta").pack(side=tk.LEFT, padx=5)
        
        end_date = ttkb.DateEntry(
            date_frame,
            textvariable=self.variables['fecha_fin'],
            width=12,
            bootstyle="primary"
        )
        end_date.pack(side=tk.LEFT, padx=5)
        
        # Report type
        type_label = ttkb.Label(criteria_frame, text="Tipo de Reporte:")
        type_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        type_frame = ttkb.Frame(criteria_frame)
        type_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        report_types = [
            ('Vuelo', 'vuelo'),
            ('Alumnos', 'alumnos'),
            ('Entrenamiento', 'entrenamiento'),
            ('Mantenimiento', 'mantenimiento')
        ]
        
        for text, value in report_types:
            rb = ttkb.Radiobutton(
                type_frame,
                text=text,
                value=value,
                variable=self.variables['tipo_reporte']
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Output format
        format_label = ttkb.Label(criteria_frame, text="Formato de Salida:")
        format_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        format_frame = ttkb.Frame(criteria_frame)
        format_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        formats = [
            ('Excel', 'excel'),
            ('CSV', 'csv'),
            ('PDF', 'pdf')
        ]
        
        for text, value in formats:
            rb = ttkb.Radiobutton(
                format_frame,
                text=text,
                value=value,
                variable=self.variables['formato_salida']
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Preview frame
        preview_frame = ttkb.Labelframe(
            self,
            text="Vista Previa de Datos",
            padding=10
        )
        preview_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Create treeview for data preview
        self.preview_tree = ttkb.Treeview(
            preview_frame,
            selectmode='browse',
            show='headings'
        )
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbars
        y_scroll = ttkb.Scrollbar(
            preview_frame,
            orient="vertical",
            command=self.preview_tree.yview
        )
        y_scroll.grid(row=0, column=1, sticky="ns")
        
        x_scroll = ttkb.Scrollbar(
            preview_frame,
            orient="horizontal",
            command=self.preview_tree.xview
        )
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        self.preview_tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        # Buttons frame
        button_frame = ttkb.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        preview_btn = ttkb.Button(
            button_frame,
            text="Vista Previa",
            command=self.preview_data,
            bootstyle="info",
            width=15
        )
        preview_btn.pack(side=tk.RIGHT, padx=5)
        
        generate_btn = ttkb.Button(
            button_frame,
            text="Generar Reporte",
            command=self.generate_report,
            bootstyle="success",
            width=15
        )
        generate_btn.pack(side=tk.RIGHT, padx=5)
    
    def preview_data(self):
        """Preview the data based on selected criteria."""
        try:
            # Get selected report type
            report_type = self.variables['tipo_reporte'].get()
            
            # Get data from data manager
            data = self.data_manager.current_data.get(report_type, [])
            
            if not data:
                messagebox.showwarning(
                    "Sin Datos",
                    "No hay datos disponibles para mostrar."
                )
                return
            
            # Clear existing items
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # Configure columns based on data
            if isinstance(data, list):
                # For list of dictionaries
                columns = list(data[0].keys())
            else:
                # For single dictionary
                columns = list(data.keys())
            
            self.preview_tree['columns'] = columns
            
            # Configure column headings
            for col in columns:
                self.preview_tree.heading(col, text=col.title())
                self.preview_tree.column(col, width=100)
            
            # Insert data
            if isinstance(data, list):
                for item in data:
                    values = [str(item.get(col, '')) for col in columns]
                    self.preview_tree.insert('', 'end', values=values)
            else:
                values = [str(data.get(col, '')) for col in columns]
                self.preview_tree.insert('', 'end', values=values)
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al cargar la vista previa: {str(e)}"
            )
    
    def generate_report(self):
        """Generate and save the report based on selected criteria."""
        try:
            # Get selected options
            report_type = self.variables['tipo_reporte'].get()
            output_format = self.variables['formato_salida'].get()
            
            # Get data
            data = self.data_manager.current_data.get(report_type, [])
            
            if not data:
                messagebox.showwarning(
                    "Sin Datos",
                    "No hay datos disponibles para generar el reporte."
                )
                return
            
            # Convert data to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame([data])
            
            # Get save location
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_name = f"reporte_{report_type}_{timestamp}"
            
            if output_format == 'excel':
                file_path = filedialog.asksaveasfilename(
                    defaultextension='.xlsx',
                    filetypes=[('Excel files', '*.xlsx')],
                    initialfile=default_name
                )
                if file_path:
                    df.to_excel(file_path, index=False)
            
            elif output_format == 'csv':
                file_path = filedialog.asksaveasfilename(
                    defaultextension='.csv',
                    filetypes=[('CSV files', '*.csv')],
                    initialfile=default_name
                )
                if file_path:
                    df.to_csv(file_path, index=False)
            
            elif output_format == 'pdf':
                file_path = filedialog.asksaveasfilename(
                    defaultextension='.pdf',
                    filetypes=[('PDF files', '*.pdf')],
                    initialfile=default_name
                )
                if file_path:
                    # Convert DataFrame to PDF using a styling template
                    styled_df = df.style.set_properties(**{
                        'background-color': '#f0f0f0',
                        'border-color': 'black',
                        'border-style': 'solid',
                        'border-width': '1px'
                    })
                    styled_df.to_pdf(file_path)
            
            if file_path:
                messagebox.showinfo(
                    "Reporte Generado",
                    f"El reporte ha sido guardado exitosamente en:\n{file_path}"
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al generar el reporte: {str(e)}"
            )
