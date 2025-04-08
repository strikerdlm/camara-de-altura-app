import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import datetime
import csv
import pandas as pd
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ExportarTab(ttk.Frame):
    """Tab for exporting session data in various formats."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.main_app = main_app
        self.setup_ui()

    def setup_ui(self):
        # Main container with scrolling
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create scrollable frame
        self.scrolled_frame = ScrolledFrame(self.main_frame, autohide=True)
        self.scrolled_frame.pack(fill=tk.BOTH, expand=True)
        
        # Content frame
        self.content_frame = self.scrolled_frame.container

        # Title frame
        self.title_frame = ttk.Frame(self.content_frame)
        self.title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.title_label = ttk.Label(
            self.title_frame, 
            text="EXPORTACIÓN DE DATOS",
            font=("Segoe UI", 12, "bold")
        )
        self.title_label.pack(side=tk.LEFT)

        # Session info frame
        self.session_frame = ttk.LabelFrame(self.content_frame, text="Información de Sesión")
        self.session_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Display basic session info
        self.session_info = ttk.Label(
            self.session_frame,
            text="Sin sesión cargada",
            font=("Segoe UI", 10)
        )
        self.session_info.pack(pady=5)
        
        # Use exports directory at the project root
        self.exports_dir = "exports"
        os.makedirs(self.exports_dir, exist_ok=True)

        # Export formats frame
        self.format_frame = ttk.LabelFrame(self.content_frame, text='Formato de Exportación')
        self.format_frame.pack(fill=tk.X, padx=5, pady=5)

        # Export description
        ttk.Label(
            self.format_frame,
            text="Seleccione el formato para exportar todos los datos de la sesión actual:",
            wraplength=600
        ).pack(fill=tk.X, padx=5, pady=5)

        # CSV Export
        self.csv_frame = ttk.Frame(self.format_frame)
        self.csv_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.csv_icon_label = ttk.Label(
            self.csv_frame,
            text="CSV",
            font=("Segoe UI", 10, "bold"),
            width=6
        )
        self.csv_icon_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            self.csv_frame,
            text="Archivo de valores separados por comas. Útil para importar en Excel o bases de datos.",
            wraplength=500
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.csv_btn = ttk.Button(
            self.csv_frame,
            text='Exportar CSV',
            command=self.export_csv,
            style="info.TButton",
            width=15
        )
        self.csv_btn.pack(side=tk.RIGHT, padx=5)

        # Excel Export
        self.excel_frame = ttk.Frame(self.format_frame)
        self.excel_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.excel_icon_label = ttk.Label(
            self.excel_frame,
            text="XLSX",
            font=("Segoe UI", 10, "bold"),
            width=6
        )
        self.excel_icon_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            self.excel_frame,
            text="Archivo Excel con datos formateados en hojas separadas para cada sección.",
            wraplength=500
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.excel_btn = ttk.Button(
            self.excel_frame,
            text='Exportar Excel',
            command=self.export_excel,
            style="success.TButton",
            width=15
        )
        self.excel_btn.pack(side=tk.RIGHT, padx=5)

        # PDF Export
        self.pdf_frame = ttk.Frame(self.format_frame)
        self.pdf_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.pdf_icon_label = ttk.Label(
            self.pdf_frame,
            text="PDF",
            font=("Segoe UI", 10, "bold"),
            width=6
        )
        self.pdf_icon_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            self.pdf_frame,
            text="Documento PDF con un reporte completo de la sesión, formateado para su impresión.",
            wraplength=500
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.pdf_btn = ttk.Button(
            self.pdf_frame,
            text='Exportar PDF',
            command=self.export_pdf,
            style="danger.TButton",
            width=15
        )
        self.pdf_btn.pack(side=tk.RIGHT, padx=5)

        # Export options
        self.options_frame = ttk.LabelFrame(self.content_frame, text='Opciones de Exportación')
        self.options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Include options
        self.include_general_var = tk.BooleanVar(value=True)
        self.include_students_var = tk.BooleanVar(value=True)
        self.include_times_var = tk.BooleanVar(value=True)
        self.include_rd_var = tk.BooleanVar(value=True)
        self.include_reactions_var = tk.BooleanVar(value=True)
        self.include_symptoms_var = tk.BooleanVar(value=True)
        
        # Checkboxes for what to include
        ttk.Checkbutton(
            self.options_frame, 
            text="Datos Generales",
            variable=self.include_general_var
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Checkbutton(
            self.options_frame, 
            text="Alumnos",
            variable=self.include_students_var
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Checkbutton(
            self.options_frame, 
            text="Tiempos",
            variable=self.include_times_var
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Checkbutton(
            self.options_frame, 
            text="RD",
            variable=self.include_rd_var
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Checkbutton(
            self.options_frame, 
            text="Reacciones",
            variable=self.include_reactions_var
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Checkbutton(
            self.options_frame, 
            text="Síntomas",
            variable=self.include_symptoms_var
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # History frame
        self.history_frame = ttk.LabelFrame(self.content_frame, text='Historial de Exportaciones')
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a TreeView for export history
        columns = ("timestamp", "format", "filename", "status")
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show="headings")
        
        # Define columns
        self.history_tree.heading("timestamp", text="Fecha/Hora")
        self.history_tree.heading("format", text="Formato")
        self.history_tree.heading("filename", text="Archivo")
        self.history_tree.heading("status", text="Estado")
        
        # Set column widths
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("format", width=80)
        self.history_tree.column("filename", width=300)
        self.history_tree.column("status", width=100)
        
        # Add a scrollbar
        history_scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=history_scrollbar.set)
        
        # Pack the TreeView and scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to open file
        self.history_tree.bind("<Double-1>", self.open_export_file)
        
        # Open folder button
        self.folder_btn = ttk.Button(
            self.content_frame,
            text="Abrir Carpeta de Exportaciones",
            command=self.open_export_folder,
            width=25
        )
        self.folder_btn.pack(side=tk.RIGHT, padx=5, pady=10)

    def load_data(self):
        """Load session data and update UI - required by the tab refresh system."""
        self.update_session_info()

    def update_session_info(self):
        """Update the session info display with current session data."""
        # Get session ID
        session_id = self.get_current_session_id()
        # Get session data
        session_data = self.get_current_session_data()
        
        if not session_id or not session_data:
            self.session_info.config(text="Sin sesión cargada")
            return
            
        # Get basic session info
        fecha = session_data.get('vuelo', {}).get('fecha', 'No disponible')
        
        # Update display
        self.session_info.config(
            text=f"Sesión: {session_id} | Fecha: {fecha}"
        )
        
    def get_current_session_id(self):
        """Get the ID of the current session."""
        # First try to get it from vuelo data
        session_id = self.data_manager.current_data.get('vuelo', {}).get('numero_entrenamiento', '')
        
        # If no specific session ID, try to construct from vuelo_del_ano with year format
        if not session_id:
            vuelo_del_ano = self.data_manager.current_data.get('vuelo', {}).get('vuelo_del_ano', '')
            if vuelo_del_ano:
                # Get current year's last two digits
                year_suffix = datetime.now().strftime("%y")
                session_id = f"{vuelo_del_ano}-{year_suffix}"
        
        return session_id
    
    def get_current_session_data(self):
        """Get the data for the current session."""
        session_id = self.get_current_session_id()
        
        # If we have a session ID, try to get session-specific data
        if session_id:
            session_data = self.data_manager.current_data.get('sessions_data', {}).get(session_id, {})
            if session_data:
                return session_data
        
        # If no session data found, return entire current_data as a fallback
        return self.data_manager.current_data

    def add_to_history(self, format_type, filename, status):
        """Add an entry to the export history."""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.history_tree.insert(
            "",
            0,  # Insert at the top
            values=(timestamp, format_type, filename, status)
        )

    def open_export_file(self, event=None):
        """Open the selected exported file."""
        selected_items = self.history_tree.selection()
        if not selected_items:
            return
            
        # Get selected file
        filename = self.history_tree.item(selected_items[0], "values")[2]
        if not os.path.exists(filename):
            messagebox.showerror(
                "Error",
                f"El archivo {filename} ya no existe."
            )
            return
            
        # Open the file with default application
        import platform
        import subprocess
        
        try:
            if platform.system() == 'Windows':
                os.startfile(filename)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', filename))
            else:  # Linux
                subprocess.call(('xdg-open', filename))
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al abrir archivo: {str(e)}"
            )

    def open_export_folder(self):
        """Open the exports folder."""
        # Make sure folder exists
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Get absolute path
        folder_path = os.path.abspath(self.exports_dir)
        
        # Open folder with default file explorer
        import platform
        import subprocess
        
        try:
            if platform.system() == 'Windows':
                os.startfile(folder_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', folder_path))
            else:  # Linux
                subprocess.call(('xdg-open', folder_path))
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al abrir carpeta: {str(e)}"
            )

    def get_filtered_data(self):
        """Get session data filtered by user options."""
        session_data = self.get_current_session_data()
        if not session_data:
            messagebox.showwarning(
                "Sin datos",
                "No hay datos de sesión para exportar."
            )
            return None
            
        # Create a filtered copy
        filtered_data = {}
        
        # Include sections based on user options
        if self.include_general_var.get() and 'vuelo' in session_data:
            filtered_data['vuelo'] = session_data['vuelo']
            
        if self.include_students_var.get():
            if 'participantes' in session_data:  # New structure
                filtered_data['alumnos_data'] = session_data['participantes']
            elif 'alumnos_data' in session_data:  # Old structure
                filtered_data['alumnos_data'] = session_data['alumnos_data']
            
        if self.include_times_var.get():
            times_data = {}
            if 'event_times' in session_data:
                times_data['event_times'] = session_data['event_times']
            if 'student_hypoxia_end_times' in session_data:
                times_data['student_hypoxia_end_times'] = session_data['student_hypoxia_end_times']
            if times_data:
                filtered_data['times_data'] = times_data
            
        if self.include_rd_var.get() and 'rd' in session_data:
            filtered_data['rd_data'] = session_data['rd']
            
        if self.include_reactions_var.get() and 'reactions_data' in session_data:
            filtered_data['reactions_data'] = session_data['reactions_data']
            
        if self.include_symptoms_var.get() and 'student_symptoms' in session_data:
            filtered_data['symptoms_data'] = session_data['student_symptoms']
        
        return filtered_data

    def export_csv(self):
        """Export data to CSV format."""
        try:
            # Get filtered data
            filtered_data = self.get_filtered_data()
            if not filtered_data:
                return
                
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = self.data_manager.get_current_session_id() or "session"
            
            # Create filename
            filename = os.path.join(self.exports_dir, f"{session_id}_{timestamp}.csv")
            
            # Convert data to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header row
                writer.writerow(["Sección", "Clave", "Valor"])
                
                # Write data rows
                for section, section_data in filtered_data.items():
                    # For nested dictionaries, flatten them
                    self._write_flattened_data(writer, section, section_data)
                    
            # Add to history
            self.add_to_history("CSV", filename, "Completado")
            
            # Show success message
            messagebox.showinfo(
                "Exportación Exitosa",
                f"Datos exportados a CSV: {filename}"
            )
            
        except Exception as e:
            # Log error and notify user
            error_msg = f"Error al exportar a CSV: {str(e)}"
            self.add_to_history("CSV", "", f"Error: {str(e)}")
            messagebox.showerror("Error de Exportación", error_msg)

    def _write_flattened_data(self, writer, section, data, prefix=""):
        """Helper to write nested dictionaries to CSV."""
        if isinstance(data, dict):
            for key, value in data.items():
                # Create prefix for nested keys
                new_prefix = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict) or isinstance(value, list):
                    # Recursively process nested structures
                    self._write_flattened_data(writer, section, value, new_prefix)
                else:
                    # Write leaf values
                    writer.writerow([section, new_prefix, value])
        elif isinstance(data, list):
            # For lists, add index to key
            for i, item in enumerate(data):
                new_prefix = f"{prefix}[{i}]"
                if isinstance(item, dict) or isinstance(item, list):
                    self._write_flattened_data(writer, section, item, new_prefix)
                else:
                    writer.writerow([section, new_prefix, item])
        else:
            # Simple values
            writer.writerow([section, prefix, data])

    def export_excel(self):
        """Export data to Excel with multiple sheets."""
        try:
            # Get filtered data
            filtered_data = self.get_filtered_data()
            if not filtered_data:
                return
                
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = self.data_manager.get_current_session_id() or "session"
            
            # Create filename
            filename = os.path.join(self.exports_dir, f"{session_id}_{timestamp}.xlsx")
            
            # Create a new Excel workbook
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for section, section_data in filtered_data.items():
                    # Convert section data to DataFrame
                    if isinstance(section_data, dict):
                        # For dictionaries, create a 2-column DataFrame
                        df = pd.DataFrame(
                            [(k, v) for k, v in self._flatten_dict(section_data).items()],
                            columns=['Campo', 'Valor']
                        )
                    elif isinstance(section_data, list):
                        # For lists of dictionaries, create a table
                        df = pd.DataFrame(section_data)
                    else:
                        # For simple values
                        df = pd.DataFrame({'Valor': [section_data]})
                        
                    # Write to sheet
                    df.to_excel(writer, sheet_name=section, index=False)
            
            # Add to history
            self.add_to_history("Excel", filename, "Completado")
            
            # Show success message
            messagebox.showinfo(
                "Exportación Exitosa",
                f"Datos exportados a Excel: {filename}"
            )
            
        except Exception as e:
            # Log error and notify user
            error_msg = f"Error al exportar a Excel: {str(e)}"
            self.add_to_history("Excel", "", f"Error: {str(e)}")
            messagebox.showerror("Error de Exportación", error_msg)

    def _flatten_dict(self, d, parent_key='', sep='.'):
        """Flatten a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to comma separated string
                if all(isinstance(x, (int, float, str, bool)) for x in v):
                    items.append((new_key, ", ".join(str(x) for x in v)))
                else:
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            items.extend(self._flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                        else:
                            items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, v))
        return dict(items)

    def export_pdf(self):
        """Export data to a formatted PDF report."""
        try:
            # Get filtered data
            filtered_data = self.get_filtered_data()
            if not filtered_data:
                return
                
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = self.data_manager.get_current_session_id() or "session"
            
            # Create filename
            filename = os.path.join(self.exports_dir, f"{session_id}_{timestamp}.pdf")
            
            # Create a PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Title
            title_style = styles['Title']
            elements.append(Paragraph("Reporte de Sesión de Entrenamiento", title_style))
            elements.append(Spacer(1, 12))
            
            # Session ID and Date
            session_info = f"Sesión: {session_id}"
            if 'vuelo' in filtered_data and 'fecha' in filtered_data['vuelo']:
                session_info += f" | Fecha: {filtered_data['vuelo']['fecha']}"
            elements.append(Paragraph(session_info, styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            # Add each section
            for section, section_data in filtered_data.items():
                # Section header
                section_title = self._get_section_title(section)
                elements.append(Paragraph(section_title, styles['Heading2']))
                elements.append(Spacer(1, 6))
                
                # Section data
                if isinstance(section_data, dict):
                    # Format as a two-column table
                    flattened_data = self._flatten_dict(section_data)
                    table_data = [['Campo', 'Valor']]  # Header row
                    for key, value in flattened_data.items():
                        table_data.append([key, str(value)])
                        
                    # Create table
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(table)
                    
                elif isinstance(section_data, list):
                    # Format as a multi-column table if all items are dictionaries
                    if section_data and all(isinstance(item, dict) for item in section_data):
                        # Get all possible keys from dictionaries
                        all_keys = set()
                        for item in section_data:
                            all_keys.update(item.keys())
                            
                        # Create table data
                        headers = list(all_keys)
                        table_data = [headers]
                        
                        for item in section_data:
                            row = [str(item.get(key, '')) for key in headers]
                            table_data.append(row)
                            
                        # Create table
                        table = Table(table_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        
                        elements.append(table)
                    else:
                        # Format as simple list
                        for i, item in enumerate(section_data):
                            elements.append(Paragraph(f"{i+1}. {str(item)}", styles['Normal']))
                else:
                    # Simple value
                    elements.append(Paragraph(str(section_data), styles['Normal']))
                
                elements.append(Spacer(1, 12))
            
            # Build the PDF
            doc.build(elements)
            
            # Add to history
            self.add_to_history("PDF", filename, "Completado")
            
            # Show success message
            messagebox.showinfo(
                "Exportación Exitosa",
                f"Datos exportados a PDF: {filename}"
            )
            
        except Exception as e:
            # Log error and notify user
            error_msg = f"Error al exportar a PDF: {str(e)}"
            self.add_to_history("PDF", "", f"Error: {str(e)}")
            messagebox.showerror("Error de Exportación", error_msg)

    def _get_section_title(self, section_key):
        """Convert a section key to a readable title."""
        section_titles = {
            'vuelo': 'Datos Generales del Vuelo',
            'alumnos_data': 'Datos de Alumnos',
            'times_data': 'Registro de Tiempos',
            'rd_data': 'Datos de Descompresión Rápida',
            'reactions_data': 'Registro de Reacciones',
            'symptoms_data': 'Registro de Síntomas'
        }
        return section_titles.get(section_key, section_key)