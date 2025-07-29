#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from PIL import Image, ImageTk
import os
import webbrowser
import sys
import platform


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
        """Create the tab UI widgets with proper scrolling functionality."""
        # Configure the main frame to expand
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create ScrolledFrame that fills the entire tab
        scrolled_frame = ttkb.ScrolledFrame(
            self,
            autohide=True,
            bootstyle="round"
        )
        scrolled_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Use the container inside the ScrolledFrame for content
        container = scrolled_frame.container
        
        # Configure container for proper layout
        container.columnconfigure(0, weight=1)

        def create_section(parent, title, title_bootstyle="info"):
            """Helper function to create a titled section frame."""
            section_frame = ttkb.Frame(parent)
            section_frame.pack(fill="x", expand=True, pady=(10, 5), padx=5)
            
            if title:
                title_label = ttkb.Label(
                    section_frame, 
                    text=title, 
                    font=('Segoe UI', 12, 'bold'), 
                    bootstyle=title_bootstyle
                )
                title_label.pack(anchor="w", pady=(0, 5))
            
            content_frame = ttkb.Frame(section_frame)
            content_frame.pack(fill="x", expand=True, padx=10)
            return content_frame

        # --- App Header ---
        header_content = create_section(container, title=None)
        
        # Load and display app icon
        self.load_app_icon(header_content)
        
        # App title
        title_label = ttkb.Label(
            header_content, 
            text="Registro Entrenamiento en Cámara de Altura", 
            font=('Segoe UI', 16, 'bold'), 
            bootstyle="primary"
        )
        title_label.pack(pady=5)
        
        # App subtitle
        subtitle_label = ttkb.Label(
            header_content, 
            text=("Sistema de Gestión de Datos para Entrenamientos "
                  "de Hipoxia Hipobárica"), 
            font=('Segoe UI', 12), 
            bootstyle="secondary", 
            wraplength=600, 
            justify=tk.CENTER
        )
        subtitle_label.pack(pady=5)
        
        # Version info
        version_label = ttkb.Label(
            header_content, 
            text="Versión 1.0.5 (Enero 2025)", 
            font=('Segoe UI', 12, 'bold'), 
            bootstyle="info"
        )
        version_label.pack(pady=2)
        
        # Release date
        date_label = ttkb.Label(
            header_content, 
            text="Fecha de lanzamiento: Enero 2025", 
            font=('Segoe UI', 10), 
            bootstyle="secondary"
        )
        date_label.pack(pady=2)
        
        # Separator
        separator = ttkb.Separator(container)
        separator.pack(fill="x", padx=20, pady=15)
        
        # --- Description Section ---
        desc_content = create_section(container, "Descripción del Sistema")
        desc_text = (
            "El Registro de Entrenamiento en Cámara de Altura es un sistema "
            "integral diseñado para gestionar y documentar los entrenamientos "
            "de hipoxia hipobárica realizados en la Cámara de Altura de la "
            "Fuerza Aérea Colombiana. El sistema automatiza el proceso de "
            "recolección de datos, cálculo de tiempos, registro de eventos "
            "médicos y generación de reportes, garantizando la precisión y "
            "consistencia en la documentación de los entrenamientos "
            "aeromédicos."
        )
        desc_label = ttkb.Label(
            desc_content, 
            text=desc_text, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        desc_label.pack(fill="x", expand=True)
        
        # --- Features Section ---
        features_content = create_section(
            container, "Características Principales"
        )
        features_text = (
            "• Gestión completa de datos de vuelo y participantes\n"
            "• Cronómetro integrado de alta precisión\n"
            "• Registro automático de tiempos de eventos\n"
            "• Cálculo automatizado de tiempos de vuelo\n"
            "• Registro detallado de reactores y eventos médicos\n"
            "• Sistema de guardado automático cada 10 segundos\n"
            "• Generación de reportes en formato CSV y Excel\n"
            "• Interfaz moderna y adaptable a diferentes resoluciones\n"
            "• Sistema de respaldo automático de datos\n"
            "• Validación de datos y manejo de errores\n"
            "• Soporte para múltiples tipos de entrenamientos\n"
            "• Registro de síntomas por participante"
        )
        features_label = ttkb.Label(
            features_content, 
            text=features_text, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        features_label.pack(fill="x", expand=True)

        # --- Technical Specifications Section ---
        tech_content = create_section(container, "Especificaciones Técnicas")
        python_version = (f"{sys.version_info.major}."
                          f"{sys.version_info.minor}."
                          f"{sys.version_info.micro}")
        platform_info = platform.platform()
        tech_text = (
            f"• Lenguaje de programación: Python {python_version}\n"
            f"• Sistema operativo: {platform_info}\n"
            "• Framework de interfaz: Tkinter con ttkbootstrap\n"
            "• Gestión de datos: CSV y Excel (openpyxl)\n"
            "• Manejo de imágenes: PIL (Pillow)\n"
            "• Arquitectura: Modular con separación por pestañas\n"
            "• Persistencia: Archivos JSON y CSV\n"
            "• Respaldo automático: Sistema de backup integrado\n"
            "• Logging: Sistema de registro de errores"
        )
        tech_label = ttkb.Label(
            tech_content, 
            text=tech_text, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        tech_label.pack(fill="x", expand=True)

        # --- System Requirements Section ---
        req_content = create_section(container, "Requisitos del Sistema")
        req_text = (
            "• Windows 10 o superior\n"
            "• Python 3.8 o superior\n"
            "• Memoria RAM: 4 GB mínimo, 8 GB recomendado\n"
            "• Espacio en disco: 500 MB para la aplicación\n"
            "• Resolución de pantalla: 1024x768 mínimo\n"
            "• Permisos de escritura en el directorio de instalación"
        )
        req_label = ttkb.Label(
            req_content, 
            text=req_text, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        req_label.pack(fill="x", expand=True)

        # --- Development Info Section ---
        dev_content = create_section(container, "Información de Desarrollo")
        dev_text = (
            "Este software ha sido desarrollado por la Subdirección "
            "Científica Aeroespacial de la Fuerza Aérea Colombiana en "
            "colaboración con el personal especializado de la Cámara de "
            "Altura. El desarrollo se realizó siguiendo las mejores "
            "prácticas de ingeniería de software y los estándares de "
            "calidad requeridos para aplicaciones médicas y aeroespaciales."
        )
        dev_label = ttkb.Label(
            dev_content, 
            text=dev_text, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        dev_label.pack(fill="x", expand=True, pady=(0, 5))
        
        team_text = (
            "Equipo de desarrollo:\n"
            "• Desarrollador principal: Dr. Diego Malpica, "
            "Especialista en Medicina Aeroespacial\n"
            "• Especialistas en Cámara de Altura: Personal técnico FAC\n"
            "• Consultoría técnica: Subdirección Científica Aeroespacial\n"
            "• Pruebas y validación: Operadores de Cámara de Altura"
        )
        team_label = ttkb.Label(
            dev_content, 
            text=team_text, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        team_label.pack(fill="x", expand=True)

        # --- Repository Section ---
        repo_content = create_section(container, "Repositorio del Proyecto")
        repo_link_text = "https://github.com/strikerdlm/camara-de-altura-app"
        repo_link = ttkb.Label(
            repo_content, 
            text=repo_link_text, 
            font=('Segoe UI', 11, 'underline'), 
            foreground="blue", 
            cursor="hand2"
        )
        repo_link.pack(fill="x", expand=True)
        repo_link.bind("<Button-1>", 
                       lambda e: webbrowser.open_new(repo_link_text))
        
        repo_info_text = ("Visite el repositorio para actualizaciones, "
                          "documentación técnica y nuevas versiones.")
        repo_info = ttkb.Label(
            repo_content, 
            text=repo_info_text, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        repo_info.pack(fill="x", expand=True, pady=(5, 0))

        # --- Version History Section ---
        version_content = create_section(container, "Historial de Versiones")
        version_history = (
            "• Versión 1.0.5 (Enero 2025):\n"
            "  - Corrección del sistema de scroll en la pestaña 'Acerca de'\n"
            "  - Mejoras en el layout y distribución de contenido\n"
            "  - Corrección de errores de formato y estilo de código\n\n"
            "• Versión 1.0.4 (Julio 2025):\n"
            "  - Reestructuración completa de la pestaña 'Acerca de' "
            "para corregir error de scroll\n"
            "  - Actualización de la información técnica y de desarrollo\n\n"
            "• Versión 1.0.3 (Diciembre 2024):\n"
            "  - Mejoras en la gestión de datos y funcionalidad de botones\n"
            "  - Nuevo sistema de limpieza individual para registros "
            "de tiempo\n\n"
            "• Versión 1.0.2 (Noviembre 2024):\n"
            "  - Mejoras en la interfaz y nuevas funcionalidades\n"
            "  - Implementación inicial del sistema de exportación\n\n"
            "• Versión 1.0.1 (Octubre 2024):\n"
            "  - Corrección de errores críticos y optimizaciones\n"
            "  - Mejoras en la estabilidad general del sistema\n\n"
            "• Versión 1.0.0 (Agosto 2024):\n"
            "  - Lanzamiento inicial de la aplicación"
        )
        version_label = ttkb.Label(
            version_content, 
            text=version_history, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        version_label.pack(fill="x", expand=True)

        # --- Support Section ---
        support_content = create_section(container, "Soporte y Contacto")
        support_text = (
            "Para soporte técnico, reportes de errores o sugerencias "
            "de mejoras, contacte a:\n\n"
            "• Subdirección Científica Aeroespacial - "
            "Fuerza Aérea Colombiana\n"
            "• Personal de la Cámara de Altura\n"
            "• Repositorio GitHub para issues técnicos"
        )
        support_label = ttkb.Label(
            support_content, 
            text=support_text, 
            font=('Segoe UI', 11), 
            wraplength=600, 
            justify=tk.LEFT
        )
        support_label.pack(fill="x", expand=True)

        # --- Copyright Section ---
        copyright_frame = ttkb.Frame(container)
        copyright_frame.pack(fill="x", expand=True, pady=(20, 10))
        
        copyright_text = (
            "© 2024-2025 Fuerza Aérea Colombiana - "
            "Subdirección Científica Aeroespacial.\n"
            "Todos los derechos reservados."
        )
        copyright_label = ttkb.Label(
            copyright_frame, 
            text=copyright_text, 
            font=('Segoe UI', 10), 
            bootstyle="secondary", 
            justify=tk.CENTER
        )
        copyright_label.pack(pady=5)
        
        disclaimer_text = (
            "Este software es propiedad de la Fuerza Aérea Colombiana "
            "y está destinado\nexclusivamente para uso oficial en "
            "operaciones de entrenamiento aeromédico."
        )
        disclaimer_label = ttkb.Label(
            copyright_frame, 
            text=disclaimer_text, 
            font=('Segoe UI', 9), 
            bootstyle="secondary", 
            justify=tk.CENTER
        )
        disclaimer_label.pack()
    
    def load_app_icon(self, parent):
        """Load and display the application icon."""
        try:
            # Get the path to the icon image
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, "assets", "icon.png")
            
            if os.path.exists(icon_path):
                # Load and resize the image
                icon_img = Image.open(icon_path)
                icon_img = icon_img.resize((120, 120), Image.LANCZOS)
                
                # Convert to Tkinter PhotoImage
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                
                # Create and place the image label
                icon_label = ttkb.Label(
                    parent, 
                    image=self.icon_photo, 
                    bootstyle="light"
                )
                icon_label.pack(pady=(5, 10))
            else:
                # Fallback if icon not found
                icon_placeholder = ttkb.Label(
                    parent, 
                    text="📊", 
                    font=('Segoe UI', 48), 
                    bootstyle="light"
                )
                icon_placeholder.pack(pady=(5, 10))
        except Exception as e:
            print(f"Error loading icon: {e}")
            # Fallback emoji icon
            icon_placeholder = ttkb.Label(
                parent, 
                text="📊", 
                font=('Segoe UI', 48), 
                bootstyle="light"
            )
            icon_placeholder.pack(pady=(5, 10))
    
    def load_data(self):
        """Empty implementation to conform to tab interface pattern."""
        pass  # No data to load for About tab 