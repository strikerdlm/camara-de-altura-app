#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from PIL import Image, ImageTk
import os
import webbrowser

class AboutTab(ttkb.Frame):
    """Tab for showing information about the application."""
    
    def __init__(self, parent, data_manager, main_app=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.data_manager = data_manager
        self.main_app = main_app
        
        # Create the layout
        self.create_widgets()
        
    def create_widgets(self):
        """Create the tab UI widgets."""
        # Configure grid for the main frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  # Main content will expand
        
        # Header with padding to avoid overlap with tab navigation
        header = ttkb.Label(
            self,
            text="Acerca de la aplicación",
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        header.grid(row=0, column=0, sticky="w", pady=(15, 20))
        
        # Main content frame with scrolling capability
        content_frame = ttkb.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        
        # Create a scrollable frame for content
        scrolled_frame = ttkb.ScrolledFrame(content_frame)
        scrolled_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main content container
        main_container = ttkb.Frame(scrolled_frame.container, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        main_container.columnconfigure(0, weight=1)
        
        # Current row for grid layout
        current_row = 0
        
        # Application icon at the top
        self.load_app_icon(main_container, current_row)
        current_row += 1
        
        # Application title
        app_title = ttkb.Label(
            main_container,
            text="Registro Entrenamiento en Cámara de Altura",
            font=('Segoe UI', 16, 'bold'),
            bootstyle="primary"
        )
        app_title.grid(row=current_row, column=0, sticky="n", pady=10)
        current_row += 1
        
        # Version
        version_label = ttkb.Label(
            main_container,
            text="Versión 1.0.3",
            font=('Segoe UI', 12),
            bootstyle="secondary"
        )
        version_label.grid(row=current_row, column=0, sticky="n", pady=5)
        current_row += 1
        
        # Separator
        separator = ttkb.Separator(main_container)
        separator.grid(row=current_row, column=0, sticky="ew", pady=15)
        current_row += 1
        
        # Development information
        dev_info_frame = ttkb.Frame(main_container)
        dev_info_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        dev_info_frame.columnconfigure(0, weight=1)
        
        dev_title = ttkb.Label(
            dev_info_frame,
            text="Información de desarrollo",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        dev_title.grid(row=0, column=0, sticky="w", pady=5)
        
        dev_text = (
            "Este software ha sido desarrollado por la Subdirección Científica Aeroespacial "
            "de la Fuerza Aérea Colombiana con la colaboración del personal en 2025 y el "
            "personal de la Cámara de Altura."
        )
        
        dev_label = ttkb.Label(
            dev_info_frame,
            text=dev_text,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        dev_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        # Lead developer
        lead_dev_label = ttkb.Label(
            dev_info_frame,
            text="Desarrollador principal: Dr. Diego Malpica, Especialista en Medicina Aeroespacial",
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        lead_dev_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # Repository link
        repo_frame = ttkb.Frame(main_container)
        repo_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        repo_frame.columnconfigure(0, weight=1)
        
        repo_title = ttkb.Label(
            repo_frame,
            text="Repositorio del proyecto",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        repo_title.grid(row=0, column=0, sticky="w", pady=5)
        
        repo_link_text = "https://github.com/strikerdlm/camara-de-altura-app"
        repo_link = ttkb.Label(
            repo_frame,
            text=repo_link_text,
            font=('Segoe UI', 11, 'underline'),
            foreground="blue",
            cursor="hand2"
        )
        repo_link.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        # Bind click event to open browser
        repo_link.bind("<Button-1>", lambda e: webbrowser.open_new(repo_link_text))
        
        repo_info = ttkb.Label(
            repo_frame,
            text="Visite el repositorio para actualizaciones y nuevas versiones.",
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        repo_info.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # Version history
        version_frame = ttkb.Frame(main_container)
        version_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        version_frame.columnconfigure(0, weight=1)
        
        version_title = ttkb.Label(
            version_frame,
            text="Historial de versiones",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        version_title.grid(row=0, column=0, sticky="w", pady=5)
        
        version_history = (
            "• Versión 1.0.3 (Marzo 2025):\n"
            "  - Mejoras en la gestión de datos y funcionalidad de botones\n"
            "  - Nuevo sistema de limpieza individual para registros de tiempo\n"
            "  - Optimización del manejo de Observadores Internos (OI)\n"
            "  - Implementación de guardado automático cada 10 segundos\n"
            "  - Mejoras en cálculos de tiempos de vuelo y registro de eventos\n"
            "  - Actualización de la interfaz para mejor organización visual\n"
            "  - Nuevo selector para Director Médico con opciones predefinidas\n"
            "  - Sistema mejorado de carga silenciosa de datos\n\n"
            "• Versión 1.0.2 (Enero 2025):\n"
            "  - Mejoras en la interfaz y nuevas funcionalidades\n"
            "  - Implementación inicial del sistema de exportación\n"
            "  - Optimización del manejo de datos de alumnos\n\n"
            "• Versión 1.0.1 (Noviembre 2024):\n"
            "  - Corrección de errores y optimizaciones\n"
            "  - Mejoras en la estabilidad general\n\n"
            "• Versión 1.0.0 (Agosto 2024):\n"
            "  - Lanzamiento inicial de la aplicación\n"
            "  - Funcionalidades básicas de registro y gestión"
        )
        
        version_info = ttkb.Label(
            version_frame,
            text=version_history,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        version_info.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # Copyright and legal
        copyright_frame = ttkb.Frame(main_container)
        copyright_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        copyright_frame.columnconfigure(0, weight=1)
        
        copyright_info = ttkb.Label(
            copyright_frame,
            text="© 2025 Fuerza Aérea Colombiana - Subdirección Científica Aeroespacial.\nTodos los derechos reservados.",
            font=('Segoe UI', 10),
            wraplength=600,
            justify=tk.CENTER
        )
        copyright_info.grid(row=0, column=0, pady=20)
        
    def load_app_icon(self, parent, row):
        """Load and display the application icon."""
        try:
            # Get the path to the icon image
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
            
            if os.path.exists(icon_path):
                # Load and resize the image
                icon_img = Image.open(icon_path)
                icon_img = icon_img.resize((150, 150), Image.LANCZOS)
                
                # Convert to Tkinter PhotoImage
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                
                # Create and place the image label
                icon_label = ttkb.Label(
                    parent,
                    image=self.icon_photo,
                    bootstyle="light"
                )
                icon_label.grid(row=row, column=0, pady=20)
            else:
                print(f"Icon file not found at {icon_path}")
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    def load_data(self):
        """Empty implementation to conform to tab interface pattern."""
        pass  # No data to load for About tab 