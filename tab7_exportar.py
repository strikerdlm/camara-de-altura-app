import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import datetime, timedelta
import csv
import pandas as pd
import os
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import unicodedata
import openpyxl
import sys

class ExportarTab(ttk.Frame):
    """Tab for exporting session data in various formats."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.main_app = main_app
        self.setup_ui()
        self.export_history = []
        self.load_export_history()

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
            font=("Segoe UI", 14, "bold"),
            bootstyle="primary"
        )
        self.title_label.pack(anchor="center")

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
        
        # Use exports directory with absolute path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.exports_dir = os.path.join(script_dir, "exports")
        self.history_file = os.path.join(self.exports_dir, "export_history.json")
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
        
        # History title - centered
        history_title = ttk.Label(
            self.history_frame,
            text="Registro de Exportaciones Realizadas",
            font=("Segoe UI", 11, "bold")
        )
        history_title.pack(pady=(5, 10), anchor="center")
        
        # Create a TreeView for export history
        columns = ("timestamp", "format", "filename", "status")
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show="headings")
        
        # Define columns
        self.history_tree.heading("timestamp", text="Fecha/Hora")
        self.history_tree.heading("format", text="Formato")
        self.history_tree.heading("filename", text="Archivo")
        self.history_tree.heading("status", text="Estado")
        
        # Set column widths
        self.history_tree.column("timestamp", width=150, anchor="center")
        self.history_tree.column("format", width=80, anchor="center")
        self.history_tree.column("filename", width=300)
        self.history_tree.column("status", width=100, anchor="center")
        
        # Add a scrollbar
        history_scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=history_scrollbar.set)
        
        # Pack the TreeView and scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to open file
        self.history_tree.bind("<Double-1>", self.open_export_file)
        
        # Open folder button
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.folder_btn = ttk.Button(
            button_frame,
            text="Abrir Carpeta de Exportaciones",
            command=self.open_export_folder,
            width=25
        )
        self.folder_btn.pack(side=tk.RIGHT, padx=5)

    def load_data(self):
        """Load session data and update UI - required by the tab refresh system."""
        self.update_session_info()
        self.load_export_history()
        self.update_history_display()

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
        
        # Add to treeview
        self.history_tree.insert(
            "",
            0,  # Insert at the top
            values=(timestamp, format_type, filename, status)
        )
        
        # Add to history list
        self.export_history.append({
            "timestamp": timestamp,
            "format": format_type,
            "filename": filename,
            "status": status
        })
        
        # Save updated history
        self.save_export_history()

    def load_export_history(self):
        """Load export history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.export_history = json.load(f)
            else:
                self.export_history = []
        except Exception as e:
            messagebox.showwarning(
                "Error",
                f"No se pudo cargar el historial de exportaciones: {str(e)}"
            )
            self.export_history = []
    
    def save_export_history(self):
        """Save export history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.export_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showwarning(
                "Error",
                f"No se pudo guardar el historial de exportaciones: {str(e)}"
            )
    
    def update_history_display(self):
        """Update the history treeview with current history data."""
        # Clear current display
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add all history items
        for item in self.export_history:
            self.history_tree.insert(
                "",
                0,  # Insert at the top
                values=(
                    item.get("timestamp", ""),
                    item.get("format", ""),
                    item.get("filename", ""),
                    item.get("status", "")
                )
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
            
        # Open the file with default application using a more compatible approach
        try:
            if sys.platform == 'win32':
                # Use shell execute for better compatibility across Windows versions
                import subprocess
                subprocess.run(['cmd', '/c', 'start', '', filename], shell=True)
            else:
                # Non-Windows platforms
                if sys.platform == 'darwin':  # macOS
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
        
        # Get absolute path and normalize for Windows
        folder_path = os.path.abspath(self.exports_dir)
        folder_path = os.path.normpath(folder_path)
        
        # Open folder with default file explorer using a more compatible approach
        try:
            if sys.platform == 'win32':
                # Use shell execute for better compatibility across Windows versions
                import subprocess
                subprocess.run(['cmd', '/c', 'start', '', folder_path], shell=True)
            else:
                # Non-Windows platforms
                if sys.platform == 'darwin':  # macOS
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

    def remove_accents(self, text):
        """Remove accents from text for consistent CSV column names."""
        if not isinstance(text, str):
            return text
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')
    
    def normalize_column_name(self, name):
        """Normalize column names for export by removing accents and special characters."""
        # Remove accents
        normalized = self.remove_accents(name)
        # Replace spaces with underscores
        normalized = normalized.replace(' ', '_')
        # Make lowercase
        normalized = normalized.lower()
        return normalized

    def _format_vuelo_data(self, vuelo_data):
        """Format flight data for display in exports."""
        # Define the order and grouping of fields
        field_groups = {
            'Información General': [
                ('fecha', 'Fecha'),
                ('vuelo_del_ano', 'Entrenamiento del Año'),
                ('vuelo_total', 'Entrenamiento Total'),
                ('numero_entrenamiento', 'Número de Entrenamiento'),
                ('curso', 'Curso'),
                ('perfil_camara', 'Perfil de Cámara'),
                ('alumnos', 'Número de Alumnos')
            ],
            'Tiempos de Vuelo': [
                ('hora_inicio', 'Hora de Inicio'),
                ('hora_fin', 'Hora de Fin'),
                ('tiempo_ascenso', 'Tiempo de Ascenso'),
                ('tiempo_estadia', 'Tiempo de Estadía'),
                ('tiempo_descenso', 'Tiempo de Descenso'),
                ('tiempo_total', 'Tiempo Total')
            ],
            'Datos Técnicos': [
                ('tipo_vuelo', 'Tipo de Vuelo'),
                ('altura_inicial', 'Altura Inicial'),
                ('altura_final', 'Altura Final')
            ],
            'Personal': [
                ('director_medico', 'Director Médico'),
                ('jefe_tecnico', 'Jefe Técnico'),
                ('operador_camara', 'Operador de Cámara'),
                ('operador_rd', 'Operador RD'),
                ('lector', 'Lector'),
                ('observador_registro', 'Observador de Registro'),
                ('oe_4', 'OE-4'),
                ('oe_5', 'OE-5')
            ],
            'Observaciones': [
                ('observaciones', 'Observaciones')
            ]
        }

        formatted_data = []
        for group_title, fields in field_groups.items():
            # Add group header
            formatted_data.append(['', ''])  # Empty row for spacing
            formatted_data.append([group_title, ''])  # Group header
            
            # Add fields
            for field_key, field_label in fields:
                value = vuelo_data.get(field_key, '')
                formatted_data.append([field_label, value])

        return formatted_data

    def export_csv(self):
        """Export all data to a single CSV file, with each section separated by headers and blank lines (mimicking Excel sheets)."""
        try:
            # Get all session data
            session_data = self.get_current_session_data()
            if not session_data:
                messagebox.showwarning(
                    "Sin datos",
                    "No hay datos de sesión para exportar."
                )
                return

            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = self.data_manager.get_current_session_id() or "session"

            # Create filename
            filename = os.path.join(self.exports_dir, f"{session_id}_{timestamp}.csv")

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # --- Tab 1: Datos Generales (Vuelo) ---
                vuelo_data = self.data_manager.current_data.get('vuelo', {})
                writer.writerow(["Datos Generales del Vuelo"])
                if vuelo_data:
                    formatted_vuelo_data = self._format_vuelo_data(vuelo_data)
                    # Filter out empty fields and empty group titles
                    filtered_vuelo_data = []
                    group_buffer = []
                    group_has_data = False
                    for row in formatted_vuelo_data:
                        if row[0] and not row[1]:
                            if group_has_data and group_buffer:
                                filtered_vuelo_data.extend(group_buffer)
                            group_buffer = [row]
                            group_has_data = False
                        else:
                            if row[1] not in (None, '', [], {}):
                                group_buffer.append(row)
                                group_has_data = True
                    if group_has_data and group_buffer:
                        filtered_vuelo_data.extend(group_buffer)
                    if not filtered_vuelo_data:
                        writer.writerow(["Sin datos", ""])
                    else:
                        writer.writerow(["Campo", "Valor"])
                        writer.writerows(filtered_vuelo_data)
                else:
                    writer.writerow(["Sin datos", ""])
                writer.writerow([])  # Blank line

                # --- Tab 2: Alumnos (Students) ---
                alumnos_data = self.data_manager.current_data.get('participantes') or \
                               self.data_manager.current_data.get('alumnos') or \
                               self.data_manager.current_data.get('alumnos_data')
                writer.writerow(["Datos de Alumnos"])
                if alumnos_data:
                    records = []
                    for student_id, student_info in alumnos_data.items():
                        if isinstance(student_info, dict):
                            record = {'ID': student_id}
                            record.update(student_info)
                            records.append(record)
                    if records:
                        df_students = pd.DataFrame(records)
                        cols = df_students.columns.tolist()
                        if 'ID' in cols:
                            cols.remove('ID')
                            cols = ['ID'] + cols
                            df_students = df_students[cols]
                        writer.writerow(df_students.columns.tolist())
                        for row in df_students.itertuples(index=False):
                            writer.writerow(list(row))
                    else:
                        writer.writerow(["Sin datos"])
                else:
                    writer.writerow(["Sin datos"])
                writer.writerow([])

                # --- Tab 3: Tiempos (tab3_tiempos.py) ---
                event_times = self.data_manager.current_data.get('event_times', {})
                student_hypoxia_end_times = self.data_manager.current_data.get('student_hypoxia_end_times', {})
                writer.writerow(["Tiempos de Hipoxia"])
                hipoxia_rows = []
                inicio_hipoxia_str = event_times.get('inicio_hipoxia', '')
                for i in range(1, 9):
                    alumno_id = str(i)
                    hora_fin = student_hypoxia_end_times.get(alumno_id, '')
                    tiempo_hipoxia = ''
                    if inicio_hipoxia_str and hora_fin:
                        try:
                            t_inicio = datetime.strptime(inicio_hipoxia_str, '%H:%M:%S')
                            t_fin = datetime.strptime(hora_fin, '%H:%M:%S')
                            if t_fin < t_inicio:
                                t_fin += timedelta(days=1)
                            delta = t_fin - t_inicio
                            total_seconds = int(delta.total_seconds())
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            tiempo_hipoxia = f"{hours:02}:{minutes:02}:{seconds:02}"
                        except Exception:
                            tiempo_hipoxia = ''
                    hipoxia_rows.append({
                        'Alumno ID': alumno_id,
                        'Hora Fin Hipoxia': hora_fin,
                        'Tiempo de Hipoxia': tiempo_hipoxia
                    })
                df_hipoxia = pd.DataFrame(hipoxia_rows, columns=['Alumno ID', 'Hora Fin Hipoxia', 'Tiempo de Hipoxia'])
                writer.writerow(df_hipoxia.columns.tolist())
                for row in df_hipoxia.itertuples(index=False):
                    writer.writerow(list(row))
                writer.writerow([])

                # Eventos principales (Tiempos_Eventos)
                writer.writerow(["Tiempos de Eventos"])
                if event_times:
                    writer.writerow(["Evento", "Hora"])
                    for k, v in event_times.items():
                        writer.writerow([k, v])
                else:
                    writer.writerow(["Sin datos"])
                writer.writerow([])

                # Totales Calculados
                writer.writerow(["Totales Calculados"])
                # Fetch displayed_calculated_totals from data_manager
                displayed_totals = self.data_manager.current_data.get('displayed_calculated_totals', {})
                
                writer.writerow(["Tipo", "Duración"])
                writer.writerow(["Tiempo Total de Vuelo", displayed_totals.get('total_vuelo', 'N/A')])
                writer.writerow(["Tiempo de Hipoxia", displayed_totals.get('total_hipoxia', 'N/A')])
                writer.writerow(["Tiempo de Visión Nocturna", displayed_totals.get('total_vision', 'N/A')])
                writer.writerow(["Tiempo de DNIT", displayed_totals.get('total_dnit', 'N/A')])
                writer.writerow(["Tiempo de Ascenso", displayed_totals.get('total_ascenso', 'N/A')])
                writer.writerow(["Tiempo de Descenso", displayed_totals.get('total_descenso', 'N/A')])
                writer.writerow(["Tiempo Total de entrenamiento", displayed_totals.get('total_entrenamiento', 'N/A')])
                writer.writerow([])

                # --- Tab 4: RD (tab4_rd.py) ---
                rd_data = self.data_manager.current_data.get('rd', {})
                writer.writerow(["Datos de Descompresión Rápida"])
                if rd_data:
                    df_rd = pd.DataFrame({
                        'Campo': list(rd_data.keys()),
                        'Valor': list(rd_data.values())
                    })
                    writer.writerow(df_rd.columns.tolist())
                    for row in df_rd.itertuples(index=False):
                        writer.writerow(list(row))
                else:
                    writer.writerow(["Sin datos"])
                writer.writerow([])

                # --- Tab 5: Reactores (tab5_reactores.py) ---
                reactions = self.data_manager.current_data.get('reactions_data', [])
                writer.writerow(["Reactores"])
                if reactions and isinstance(reactions, list):
                    df_reactions = pd.DataFrame(reactions)
                    writer.writerow(df_reactions.columns.tolist())
                    for row in df_reactions.itertuples(index=False):
                        writer.writerow(list(row))
                else:
                    writer.writerow(["Sin datos"])
                writer.writerow([])

                # --- Tab 6: Sintomas (tab6_sintomas.py) ---
                symptoms = self.data_manager.current_data.get('student_symptoms', {})
                writer.writerow(["Síntomas"])
                if symptoms:
                    student_symptoms = {}
                    for key, value in symptoms.items():
                        student_id = key.split('[')[0] if '[' in key else key
                        if student_id not in student_symptoms:
                            student_symptoms[student_id] = []
                        student_symptoms[student_id].append(value)
                    symptoms_data = []
                    for student_id, symptom_list in student_symptoms.items():
                        flat_symptoms = []
                        for s in symptom_list:
                            if isinstance(s, list):
                                flat_symptoms.extend([str(item) for item in s])
                            else:
                                flat_symptoms.append(str(s))
                        symptoms_data.append({
                            'Alumno ID': student_id,
                            'Síntomas': ', '.join(flat_symptoms)
                        })
                    if symptoms_data:
                        df_symptoms = pd.DataFrame(symptoms_data)
                        writer.writerow(df_symptoms.columns.tolist())
                        for row in df_symptoms.itertuples(index=False):
                            writer.writerow(list(row))
                    else:
                        writer.writerow(["Sin datos"])
                else:
                    writer.writerow(["Sin datos"])
                writer.writerow([])

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

    def export_excel(self):
        """Export data to Excel with one sheet per tab (Tabs 1-6, now all tabs)."""
        try:
            # Get all session data
            session_data = self.get_current_session_data()
            if not session_data:
                messagebox.showwarning(
                    "Sin datos",
                    "No hay datos de sesión para exportar."
                )
                return

            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = self.data_manager.get_current_session_id() or "session"

            # Create filename
            filename = os.path.join(self.exports_dir, f"{session_id}_{timestamp}.xlsx")

            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # --- Tab 1: Datos Generales (Vuelo) ---
                vuelo_data = self.data_manager.current_data.get('vuelo', {})
                if vuelo_data:
                    formatted_vuelo_data = self._format_vuelo_data(vuelo_data)
                    # Filter out empty fields and empty group titles
                    filtered_vuelo_data = []
                    group_buffer = []
                    group_has_data = False
                    for row in formatted_vuelo_data:
                        # If this is a group title (row[0] and not row[1])
                        if row[0] and not row[1]:
                            # If previous group had data, add it
                            if group_has_data and group_buffer:
                                filtered_vuelo_data.extend(group_buffer)
                            # Start new group
                            group_buffer = [row]
                            group_has_data = False
                        else:
                            # Only add non-empty fields
                            if row[1] not in (None, '', [], {}):
                                group_buffer.append(row)
                                group_has_data = True
                    # Add the last group if it had data
                    if group_has_data and group_buffer:
                        filtered_vuelo_data.extend(group_buffer)
                    # If nothing left, export 'Sin datos'
                    if not filtered_vuelo_data:
                        pd.DataFrame([['Sin datos', '']]).to_excel(writer, sheet_name='Datos Generales', index=False)
                    else:
                        df_vuelo = pd.DataFrame(filtered_vuelo_data, columns=['Campo', 'Valor'])
                        df_vuelo.to_excel(writer, sheet_name='Datos Generales', index=False)
                        worksheet = writer.sheets['Datos Generales']
                        for idx, row in enumerate(filtered_vuelo_data, start=2):
                            if row[0] and not row[1]:
                                cell = worksheet.cell(row=idx, column=1)
                                cell.font = openpyxl.styles.Font(bold=True)
                else:
                    pd.DataFrame([['Sin datos', '']]).to_excel(writer, sheet_name='Datos Generales', index=False)

                # --- Tab 2: Alumnos (Students) ---
                alumnos_data = self.data_manager.current_data.get('participantes') or \
                               self.data_manager.current_data.get('alumnos') or \
                               self.data_manager.current_data.get('alumnos_data')
                if alumnos_data:
                    records = []
                    for student_id, student_info in alumnos_data.items():
                        if isinstance(student_info, dict):
                            record = {'ID': student_id}
                            record.update(student_info)
                            records.append(record)
                    if records:
                        df_students = pd.DataFrame(records)
                        cols = df_students.columns.tolist()
                        if 'ID' in cols:
                            cols.remove('ID')
                            cols = ['ID'] + cols
                            df_students = df_students[cols]
                        df_students.to_excel(writer, sheet_name='Alumnos', index=False)
                    else:
                        pd.DataFrame([['Sin datos']]).to_excel(writer, sheet_name='Alumnos', index=False)
                else:
                    pd.DataFrame([['Sin datos']]).to_excel(writer, sheet_name='Alumnos', index=False)

                # --- Tab 3: Tiempos (tab3_tiempos.py) ---
                event_times = self.data_manager.current_data.get('event_times', {})
                student_hypoxia_end_times = self.data_manager.current_data.get('student_hypoxia_end_times', {})
                hipoxia_rows = []
                inicio_hipoxia_str = event_times.get('inicio_hipoxia', '')
                for i in range(1, 9):
                    alumno_id = str(i)
                    hora_fin = student_hypoxia_end_times.get(alumno_id, '')
                    tiempo_hipoxia = ''
                    # Calculate tiempo de hipoxia if both times are available
                    if inicio_hipoxia_str and hora_fin:
                        try:
                            t_inicio = datetime.strptime(inicio_hipoxia_str, '%H:%M:%S')
                            t_fin = datetime.strptime(hora_fin, '%H:%M:%S')
                            # Handle overnight case
                            if t_fin < t_inicio:
                                t_fin += timedelta(days=1)
                            delta = t_fin - t_inicio
                            total_seconds = int(delta.total_seconds())
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            tiempo_hipoxia = f"{hours:02}:{minutes:02}:{seconds:02}"
                        except Exception:
                            tiempo_hipoxia = ''
                    hipoxia_rows.append({
                        'Alumno ID': alumno_id,
                        'Hora Fin Hipoxia': hora_fin,
                        'Tiempo de Hipoxia': tiempo_hipoxia
                    })
                df_hipoxia = pd.DataFrame(hipoxia_rows, columns=['Alumno ID', 'Hora Fin Hipoxia', 'Tiempo de Hipoxia'])
                df_hipoxia.to_excel(writer, sheet_name='Tiempos_Hipoxia', index=False)

                # Eventos principales (Tiempos_Eventos)
                if event_times:
                    df_events = pd.DataFrame({
                        'Evento': list(event_times.keys()),
                        'Hora': list(event_times.values())
                    })
                    df_events.to_excel(writer, sheet_name='Tiempos_Eventos', index=False)
                else:
                    pd.DataFrame([['Sin datos']]).to_excel(writer, sheet_name='Tiempos_Eventos', index=False)

                # Totales Calculados (including new times)
                # Fetch displayed_calculated_totals from data_manager
                displayed_totals = self.data_manager.current_data.get('displayed_calculated_totals', {})
                
                df_totals = pd.DataFrame([
                    ['Tiempo Total de Vuelo', displayed_totals.get('total_vuelo', 'N/A')],
                    ['Tiempo de Hipoxia', displayed_totals.get('total_hipoxia', 'N/A')],
                    ['Tiempo de Visión Nocturna', displayed_totals.get('total_vision', 'N/A')],
                    ['Tiempo de DNIT', displayed_totals.get('total_dnit', 'N/A')],
                    ['Tiempo de Ascenso', displayed_totals.get('total_ascenso', 'N/A')],
                    ['Tiempo de Descenso', displayed_totals.get('total_descenso', 'N/A')],
                    ['Tiempo Total de entrenamiento', displayed_totals.get('total_entrenamiento', 'N/A')],
                ], columns=['Tipo', 'Duración'])
                df_totals.to_excel(writer, sheet_name='Totales_Calculados', index=False)

                # --- Tab 4: RD (tab4_rd.py) ---
                rd_data = self.data_manager.current_data.get('rd', {})
                if rd_data:
                    df_rd = pd.DataFrame({
                        'Campo': list(rd_data.keys()),
                        'Valor': list(rd_data.values())
                    })
                    df_rd.to_excel(writer, sheet_name='RD', index=False)
                else:
                    pd.DataFrame([['Sin datos']]).to_excel(writer, sheet_name='RD', index=False)

                # --- Tab 5: Reactores (tab5_reactores.py) ---
                reactions = self.data_manager.current_data.get('reactions_data', [])
                if reactions and isinstance(reactions, list):
                    df_reactions = pd.DataFrame(reactions)
                    df_reactions.to_excel(writer, sheet_name='Reactores', index=False)
                else:
                    pd.DataFrame([['Sin datos']]).to_excel(writer, sheet_name='Reactores', index=False)

                # --- Tab 6: Sintomas (tab6_sintomas.py) ---
                symptoms = self.data_manager.current_data.get('student_symptoms', {})
                if symptoms:
                    # Reorganize symptoms by student
                    student_symptoms = {}
                    for key, value in symptoms.items():
                        student_id = key.split('[')[0] if '[' in key else key
                        if student_id not in student_symptoms:
                            student_symptoms[student_id] = []
                        student_symptoms[student_id].append(value)
                    symptoms_data = []
                    for student_id, symptom_list in student_symptoms.items():
                        # Ensure all items are strings and flatten if any are lists
                        flat_symptoms = []
                        for s in symptom_list:
                            if isinstance(s, list):
                                flat_symptoms.extend([str(item) for item in s])
                            else:
                                flat_symptoms.append(str(s))
                        symptoms_data.append({
                            'Alumno ID': student_id,
                            'Síntomas': ', '.join(flat_symptoms)
                        })
                    if symptoms_data:
                        df_symptoms = pd.DataFrame(symptoms_data)
                        df_symptoms.to_excel(writer, sheet_name='Sintomas', index=False)
                    else:
                        pd.DataFrame([['Sin datos']]).to_excel(writer, sheet_name='Sintomas', index=False)
                else:
                    pd.DataFrame([['Sin datos']]).to_excel(writer, sheet_name='Sintomas', index=False)

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

    def export_pdf(self):
        """Export all data to a professional, executive-style PDF report in Spanish, matching the Excel export."""
        try:
            from reportlab.lib.units import mm
            # Get all session data
            session_data = self.get_current_session_data()
            if not session_data:
                messagebox.showwarning(
                    "Sin datos",
                    "No hay datos de sesión para exportar."
                )
                return

            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = self.data_manager.get_current_session_id() or "session"
            filename = os.path.join(self.exports_dir, f"{session_id}_{timestamp}.pdf")

            # Prepare PDF document
            doc = SimpleDocTemplate(
                filename,
                pagesize=letter,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            styles = getSampleStyleSheet()
            elements = []

            # --- Cover Page ---
            cover_style = styles['Title']
            cover_style.fontName = 'Helvetica-Bold'
            cover_style.fontSize = 22
            cover_style.leading = 28
            elements.append(Paragraph("<b>Reporte Ejecutivo de Entrenamiento en Cámara Hipobárica</b>", cover_style))
            elements.append(Spacer(1, 18))
            elements.append(Paragraph(f"<b>Sesión:</b> {session_id}", styles['Heading2']))
            fecha = session_data.get('vuelo', {}).get('fecha', 'No disponible')
            elements.append(Paragraph(f"<b>Fecha de Entrenamiento:</b> {fecha}", styles['Normal']))
            elements.append(Paragraph(f"<b>Fecha de Exportación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(
                "Este informe ejecutivo presenta un resumen detallado de la sesión de entrenamiento en cámara hipobárica, incluyendo los datos generales del vuelo, información de los participantes, tiempos críticos, eventos de descompresión rápida, reacciones observadas y síntomas reportados. El objetivo es proporcionar una visión integral y profesional para la toma de decisiones y el análisis institucional.",
                styles['BodyText']
            ))
            elements.append(PageBreak())

            # --- Section Templates ---
            section_templates = [
                {
                    'title': 'Datos Generales del Vuelo',
                    'desc': 'Esta sección contiene la información principal del vuelo de entrenamiento, incluyendo fecha, número de vuelo, perfil de cámara, personal responsable y observaciones relevantes.',
                    'data_func': lambda: self.data_manager.current_data.get('vuelo', {}),
                    'table_func': self._format_vuelo_data,
                    'columns': ['Campo', 'Valor']
                },
                {
                    'title': 'Datos de Alumnos',
                    'desc': 'A continuación se presenta la información de los participantes, incluyendo identificación, grado, nombre, edad, género, unidad, correo electrónico y equipo asignado.',
                    'data_func': lambda: self.data_manager.current_data.get('participantes') or self.data_manager.current_data.get('alumnos') or self.data_manager.current_data.get('alumnos_data'),
                    'table_func': None,
                    'columns': None
                },
                {
                    'title': 'Tiempos de Hipoxia',
                    'desc': 'Se detallan los tiempos de hipoxia para cada alumno, calculados a partir del registro de inicio y finalización del ejercicio correspondiente.',
                    'data_func': lambda: (self.data_manager.current_data.get('event_times', {}), self.data_manager.current_data.get('student_hypoxia_end_times', {})),
                    'table_func': None,
                    'columns': ['Alumno ID', 'Hora Fin Hipoxia', 'Tiempo de Hipoxia']
                },
                {
                    'title': 'Tiempos de Eventos',
                    'desc': 'Registro cronológico de los principales eventos durante la sesión, con sus respectivos horarios.',
                    'data_func': lambda: self.data_manager.current_data.get('event_times', {}),
                    'table_func': None,
                    'columns': ['Evento', 'Hora']
                },
                {
                    'title': 'Totales Calculados',
                    'desc': 'Resumen de los tiempos totales calculados para las diferentes fases del entrenamiento, proporcionando una visión global de la duración de cada etapa.',
                    'data_func': lambda: self.data_manager.current_data.get('event_times', {}),
                    'table_func': None,
                    'columns': ['Tipo', 'Duración']
                },
                {
                    'title': 'Datos de Descompresión Rápida',
                    'desc': 'Información relevante sobre los eventos de descompresión rápida (RD) ocurridos durante la sesión, incluyendo posiciones, novedades y observaciones.',
                    'data_func': lambda: self.data_manager.current_data.get('rd', {}),
                    'table_func': None,
                    'columns': None
                },
                {
                    'title': 'Reactores',
                    'desc': 'Registro de reacciones observadas en los participantes, con detalles sobre el evento, severidad, manejo y resultados.',
                    'data_func': lambda: self.data_manager.current_data.get('reactions_data', []),
                    'table_func': None,
                    'columns': None
                },
                {
                    'title': 'Síntomas',
                    'desc': 'Síntomas reportados por los alumnos durante o después del entrenamiento, agrupados por participante.',
                    'data_func': lambda: self.data_manager.current_data.get('student_symptoms', {}),
                    'table_func': None,
                    'columns': None
                },
            ]

            # --- Section Rendering ---
            for idx, section in enumerate(section_templates):
                # Section Title
                section_title_style = styles['Heading1']
                section_title_style.fontName = 'Helvetica-Bold'
                section_title_style.fontSize = 16
                section_title_style.leading = 22
                elements.append(Paragraph(section['title'], section_title_style))
                elements.append(Spacer(1, 6))
                # Section Description
                desc_style = styles['BodyText']
                desc_style.fontSize = 11
                desc_style.leading = 15
                elements.append(Paragraph(section['desc'], desc_style))
                elements.append(Spacer(1, 8))

                # Section Data
                data = section['data_func']()
                if section['title'] == 'Datos Generales del Vuelo':
                    # Use formatted table
                    formatted = section['table_func'](data) if data else []
                    if formatted:
                        table_data = [section['columns']]
                        for row in formatted:
                            if row[0] and not row[1]:
                                table_data.append([Paragraph(f'<b>{row[0]}</b>', styles['Heading3']), ''])
                            else:
                                table_data.append(row)
                        t = Table(table_data, colWidths=[80*mm, 80*mm])
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 12),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e6f2ff')]),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ]))
                        elements.append(t)
                    else:
                        elements.append(Paragraph("Sin datos", styles['Normal']))
                elif section['title'] == 'Datos de Alumnos':
                    if data:
                        records = []
                        for student_id, student_info in data.items():
                            if isinstance(student_info, dict):
                                record = {'ID': student_id}
                                record.update(student_info)
                                records.append(record)
                        if records:
                            df = pd.DataFrame(records)
                            cols = df.columns.tolist()
                            if 'ID' in cols:
                                cols.remove('ID')
                                cols = ['ID'] + cols
                                df = df[cols]
                            table_data = [df.columns.tolist()] + df.values.tolist()
                            t = Table(table_data, repeatRows=1)
                            t.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 11),
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e6f2ff')]),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ]))
                            elements.append(t)
                        else:
                            elements.append(Paragraph("Sin datos", styles['Normal']))
                    else:
                        elements.append(Paragraph("Sin datos", styles['Normal']))
                elif section['title'] == 'Tiempos de Hipoxia':
                    event_times, student_hypoxia_end_times = data
                    hipoxia_rows = []
                    inicio_hipoxia_str = event_times.get('inicio_hipoxia', '')
                    for i in range(1, 9):
                        alumno_id = str(i)
                        hora_fin = student_hypoxia_end_times.get(alumno_id, '')
                        tiempo_hipoxia = ''
                        if inicio_hipoxia_str and hora_fin:
                            try:
                                t_inicio = datetime.strptime(inicio_hipoxia_str, '%H:%M:%S')
                                t_fin = datetime.strptime(hora_fin, '%H:%M:%S')
                                if t_fin < t_inicio:
                                    t_fin += timedelta(days=1)
                                delta = t_fin - t_inicio
                                total_seconds = int(delta.total_seconds())
                                hours, remainder = divmod(total_seconds, 3600)
                                minutes, seconds = divmod(remainder, 60)
                                tiempo_hipoxia = f"{hours:02}:{minutes:02}:{seconds:02}"
                            except Exception:
                                tiempo_hipoxia = ''
                        hipoxia_rows.append([alumno_id, hora_fin, tiempo_hipoxia])
                    table_data = [section['columns']] + hipoxia_rows
                    t = Table(table_data, repeatRows=1)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e6f2ff')]),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ]))
                    elements.append(t)
                elif section['title'] == 'Tiempos de Eventos':
                    if data:
                        table_data = [section['columns']]
                        for k, v in data.items():
                            table_data.append([k, v])
                        t = Table(table_data, repeatRows=1)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e6f2ff')]),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ]))
                        elements.append(t)
                    else:
                        elements.append(Paragraph("Sin datos", styles['Normal']))
                elif section['title'] == 'Totales Calculados':
                    # Fetch displayed_calculated_totals from data_manager
                    displayed_totals = self.data_manager.current_data.get('displayed_calculated_totals', {})
                    
                    pdf_calculated_totals_data = [
                        ['Tiempo Total de Vuelo', displayed_totals.get('total_vuelo', 'N/A')],
                        ['Tiempo de Hipoxia', displayed_totals.get('total_hipoxia', 'N/A')],
                        ['Tiempo de Visión Nocturna', displayed_totals.get('total_vision', 'N/A')],
                        ['Tiempo de DNIT', displayed_totals.get('total_dnit', 'N/A')],
                        ['Tiempo de Ascenso', displayed_totals.get('total_ascenso', 'N/A')],
                        ['Tiempo de Descenso', displayed_totals.get('total_descenso', 'N/A')],
                        ['Tiempo Total de entrenamiento', displayed_totals.get('total_entrenamiento', 'N/A')],
                    ]
                    table_data = [section['columns']] + pdf_calculated_totals_data
                    t = Table(table_data, repeatRows=1)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e6f2ff')]),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ]))
                    elements.append(t)
                elif section['title'] == 'Datos de Descompresión Rápida':
                    if data:
                        df = pd.DataFrame({'Campo': list(data.keys()), 'Valor': list(data.values())})
                        table_data = [df.columns.tolist()] + df.values.tolist()
                        t = Table(table_data, repeatRows=1)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e6f2ff')]),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ]))
                        elements.append(t)
                    else:
                        elements.append(Paragraph("Sin datos", styles['Normal']))
                elif section['title'] == 'Reactores':
                    if data and isinstance(data, list):
                        df = pd.DataFrame(data)
                        if not df.empty:
                            table_data = [df.columns.tolist()] + df.values.tolist()
                            t = Table(table_data, repeatRows=1)
                            t.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 10),
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e6f2ff')]),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ]))
                            elements.append(t)
                        else:
                            elements.append(Paragraph("Sin datos", styles['Normal']))
                    else:
                        elements.append(Paragraph("Sin datos", styles['Normal']))
                elif section['title'] == 'Síntomas':
                    if data:
                        student_symptoms = {}
                        for key, value in data.items():
                            student_id = key.split('[')[0] if '[' in key else key
                            if student_id not in student_symptoms:
                                student_symptoms[student_id] = []
                            student_symptoms[student_id].append(value)
                        symptoms_data = []
                        for student_id, symptom_list in student_symptoms.items():
                            flat_symptoms = []
                            for s in symptom_list:
                                if isinstance(s, list):
                                    flat_symptoms.extend([str(item) for item in s])
                                else:
                                    flat_symptoms.append(str(s))
                            symptoms_data.append({
                                'Alumno ID': student_id,
                                'Síntomas': ', '.join(flat_symptoms)
                            })
                        if symptoms_data:
                            df = pd.DataFrame(symptoms_data)
                            table_data = [df.columns.tolist()] + df.values.tolist()
                            t = Table(table_data, repeatRows=1)
                            t.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 10),
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#e6f2ff')]),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ]))
                            elements.append(t)
                        else:
                            elements.append(Paragraph("Sin datos", styles['Normal']))
                    else:
                        elements.append(Paragraph("Sin datos", styles['Normal']))
                # Add a page break after each section except the last
                if idx < len(section_templates) - 1:
                    elements.append(PageBreak())

            # --- Footer and Page Numbers ---
            def add_footer(canvas, doc):
                canvas.saveState()
                footer_text = f"Exportado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | CamaraApp"
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.grey)
                canvas.drawString(20*mm, 10*mm, footer_text)
                canvas.drawRightString(200*mm, 10*mm, f"Página {doc.page}")
                canvas.restoreState()

            # Build PDF
            doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

            # Add to history
            self.add_to_history("PDF", filename, "Completado")

            # Show success message
            messagebox.showinfo(
                "Exportación Exitosa",
                f"Datos exportados a PDF: {filename}"
            )

        except Exception as e:
            error_msg = f"Error al exportar a PDF: {str(e)}"
            self.add_to_history("PDF", "", f"Error: {str(e)}")
            messagebox.showerror("Error de Exportación", error_msg)