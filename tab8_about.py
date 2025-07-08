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
        
        # Subtitle
        subtitle = ttkb.Label(
            main_container,
            text="Sistema de Gestión de Datos para Entrenamientos de Hipoxia Hipobárica",
            font=('Segoe UI', 12),
            bootstyle="secondary",
            wraplength=600
        )
        subtitle.grid(row=current_row, column=0, sticky="n", pady=5)
        current_row += 1
        
        # Version
        version_label = ttkb.Label(
            main_container,
            text="Versión 1.0.4",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        version_label.grid(row=current_row, column=0, sticky="n", pady=5)
        current_row += 1
        
        # Release date
        release_date = ttkb.Label(
            main_container,
            text="Fecha de lanzamiento: Enero 2025",
            font=('Segoe UI', 10),
            bootstyle="secondary"
        )
        release_date.grid(row=current_row, column=0, sticky="n", pady=5)
        current_row += 1
        
        # Separator
        separator = ttkb.Separator(main_container)
        separator.grid(row=current_row, column=0, sticky="ew", pady=15)
        current_row += 1
        
        # Application description
        description_frame = ttkb.Frame(main_container)
        description_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        description_frame.columnconfigure(0, weight=1)
        
        desc_title = ttkb.Label(
            description_frame,
            text="Descripción del Sistema",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        desc_title.grid(row=0, column=0, sticky="w", pady=5)
        
        desc_text = (
            "El Registro de Entrenamiento en Cámara de Altura es un sistema integral diseñado "
            "para gestionar y documentar los entrenamientos de hipoxia hipobárica realizados "
            "en la Cámara de Altura de la Fuerza Aérea Colombiana. El sistema automatiza el "
            "proceso de recolección de datos, cálculo de tiempos, registro de eventos médicos "
            "y generación de reportes, garantizando la precisión y consistencia en la documentación "
            "de los entrenamientos aeromédicos."
        )
        
        desc_label = ttkb.Label(
            description_frame,
            text=desc_text,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        desc_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # Key features
        features_frame = ttkb.Frame(main_container)
        features_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        features_frame.columnconfigure(0, weight=1)
        
        features_title = ttkb.Label(
            features_frame,
            text="Características Principales",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        features_title.grid(row=0, column=0, sticky="w", pady=5)
        
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
            features_frame,
            text=features_text,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        features_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # Technical specifications
        tech_frame = ttkb.Frame(main_container)
        tech_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        tech_frame.columnconfigure(0, weight=1)
        
        tech_title = ttkb.Label(
            tech_frame,
            text="Especificaciones Técnicas",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        tech_title.grid(row=0, column=0, sticky="w", pady=5)
        
        # Get system information
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
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
            tech_frame,
            text=tech_text,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        tech_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # System requirements
        req_frame = ttkb.Frame(main_container)
        req_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        req_frame.columnconfigure(0, weight=1)
        
        req_title = ttkb.Label(
            req_frame,
            text="Requisitos del Sistema",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        req_title.grid(row=0, column=0, sticky="w", pady=5)
        
        req_text = (
            "• Windows 10 o superior\n"
            "• Python 3.8 o superior\n"
            "• Memoria RAM: 4 GB mínimo, 8 GB recomendado\n"
            "• Espacio en disco: 500 MB para la aplicación\n"
            "• Resolución de pantalla: 1024x768 mínimo\n"
            "• Permisos de escritura en el directorio de instalación\n"
            "• Conexión a internet para actualizaciones (opcional)"
        )
        
        req_label = ttkb.Label(
            req_frame,
            text=req_text,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        req_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # Development information
        dev_info_frame = ttkb.Frame(main_container)
        dev_info_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        dev_info_frame.columnconfigure(0, weight=1)
        
        dev_title = ttkb.Label(
            dev_info_frame,
            text="Información de Desarrollo",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        dev_title.grid(row=0, column=0, sticky="w", pady=5)
        
        dev_text = (
            "Este software ha sido desarrollado por la Subdirección Científica Aeroespacial "
            "de la Fuerza Aérea Colombiana en colaboración con el personal especializado "
            "de la Cámara de Altura. El desarrollo se realizó siguiendo las mejores prácticas "
            "de ingeniería de software y los estándares de calidad requeridos para aplicaciones "
            "médicas y aeroespaciales."
        )
        
        dev_label = ttkb.Label(
            dev_info_frame,
            text=dev_text,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        dev_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        # Development team
        team_text = (
            "Equipo de desarrollo:\n"
            "• Desarrollador principal: Dr. Diego Malpica, Especialista en Medicina Aeroespacial\n"
            "• Especialistas en Cámara de Altura: Personal técnico FAC\n"
            "• Consultoría técnica: Subdirección Científica Aeroespacial\n"
            "• Pruebas y validación: Operadores de Cámara de Altura"
        )
        
        team_label = ttkb.Label(
            dev_info_frame,
            text=team_text,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        team_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # Repository link
        repo_frame = ttkb.Frame(main_container)
        repo_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        repo_frame.columnconfigure(0, weight=1)
        
        repo_title = ttkb.Label(
            repo_frame,
            text="Repositorio del Proyecto",
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
            text="Visite el repositorio para actualizaciones, documentación técnica y nuevas versiones.",
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
            text="Historial de Versiones",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        version_title.grid(row=0, column=0, sticky="w", pady=5)
        
        version_history = (
            "• Versión 1.0.4 (Enero 2025):\n"
            "  - Actualización completa de la pestaña 'Acerca de'\n"
            "  - Información técnica detallada del sistema\n"
            "  - Especificaciones de requisitos del sistema\n"
            "  - Mejoras en la documentación de características\n"
            "  - Optimización del rendimiento de la interfaz\n"
            "  - Corrección de errores menores en cálculos de tiempo\n\n"
            "• Versión 1.0.3 (Diciembre 2024):\n"
            "  - Mejoras en la gestión de datos y funcionalidad de botones\n"
            "  - Nuevo sistema de limpieza individual para registros de tiempo\n"
            "  - Optimización del manejo de Observadores Internos (OI)\n"
            "  - Implementación de guardado automático cada 10 segundos\n"
            "  - Mejoras en cálculos de tiempos de vuelo y registro de eventos\n"
            "  - Actualización de la interfaz para mejor organización visual\n"
            "  - Nuevo selector para Director Médico con opciones predefinidas\n"
            "  - Sistema mejorado de carga silenciosa de datos\n\n"
            "• Versión 1.0.2 (Noviembre 2024):\n"
            "  - Mejoras en la interfaz y nuevas funcionalidades\n"
            "  - Implementación inicial del sistema de exportación\n"
            "  - Optimización del manejo de datos de alumnos\n"
            "  - Corrección de errores en el cronómetro\n"
            "  - Mejoras en la validación de datos\n\n"
            "• Versión 1.0.1 (Octubre 2024):\n"
            "  - Corrección de errores críticos y optimizaciones\n"
            "  - Mejoras en la estabilidad general del sistema\n"
            "  - Implementación de sistema de respaldo automático\n"
            "  - Corrección de problemas de memoria\n\n"
            "• Versión 1.0.0 (Agosto 2024):\n"
            "  - Lanzamiento inicial de la aplicación\n"
            "  - Funcionalidades básicas de registro y gestión\n"
            "  - Interfaz de usuario básica\n"
            "  - Sistema de cronómetro integrado\n"
            "  - Registro básico de datos de vuelo"
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
        
        # Support and contact
        support_frame = ttkb.Frame(main_container)
        support_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
        support_frame.columnconfigure(0, weight=1)
        
        support_title = ttkb.Label(
            support_frame,
            text="Soporte y Contacto",
            font=('Segoe UI', 12, 'bold'),
            bootstyle="info"
        )
        support_title.grid(row=0, column=0, sticky="w", pady=5)
        
        support_text = (
            "Para soporte técnico, reportes de errores o sugerencias de mejoras:\n\n"
            "• Subdirección Científica Aeroespacial - Fuerza Aérea Colombiana\n"
            "• Personal de la Cámara de Altura\n"
            "• Repositorio GitHub para issues técnicos\n\n"
            "Este software está diseñado específicamente para el uso en las instalaciones "
            "de la Cámara de Altura de la FAC y debe ser operado únicamente por personal "
            "autorizado y debidamente capacitado."
        )
        
        support_label = ttkb.Label(
            support_frame,
            text=support_text,
            font=('Segoe UI', 11),
            wraplength=600,
            justify=tk.LEFT
        )
        support_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        current_row += 1
        
        # Copyright and legal
        copyright_frame = ttkb.Frame(main_container)
        copyright_frame.grid(row=current_row, column=0, sticky="ew", pady=15)
        copyright_frame.columnconfigure(0, weight=1)
        
        copyright_info = ttkb.Label(
            copyright_frame,
            text="© 2024-2025 Fuerza Aérea Colombiana - Subdirección Científica Aeroespacial.\nTodos los derechos reservados.\n\nEste software es propiedad de la Fuerza Aérea Colombiana y está destinado\nexclusivamente para uso oficial en operaciones de entrenamiento aeromédico.",
            font=('Segoe UI', 10),
            wraplength=600,
            justify=tk.CENTER,
            bootstyle="secondary"
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
                icon_img = icon_img.resize((120, 120), Image.LANCZOS)
                
                # Convert to Tkinter PhotoImage
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                
                # Create and place the image label
                icon_label = ttkb.Label(
                    parent,
                    image=self.icon_photo,
                    bootstyle="light"
                )
                icon_label.grid(row=row, column=0, pady=15)
            else:
                # Fallback if icon not found
                icon_placeholder = ttkb.Label(
                    parent,
                    text="📊",
                    font=('Segoe UI', 48),
                    bootstyle="light"
                )
                icon_placeholder.grid(row=row, column=0, pady=15)
        except Exception as e:
            print(f"Error loading icon: {e}")
            # Fallback emoji icon
            icon_placeholder = ttkb.Label(
                parent,
                text="📊",
                font=('Segoe UI', 48),
                bootstyle="light"
            )
            icon_placeholder.grid(row=row, column=0, pady=15)
    
    def load_data(self):
        """Empty implementation to conform to tab interface pattern."""
        pass  # No data to load for About tab 