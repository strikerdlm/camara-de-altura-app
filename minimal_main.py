#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox
import os
import sys
from PIL import Image, ImageTk, ImageFilter, ImageEnhance

# Add path to allow imports from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MainApp:
    """Main application class"""
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI"""
        # Configure the window
        self.root.title("Registro Entrenamiento en Cámara de Altura")
        self.root.geometry("1200x800")
        
        # Create main container
        main_container = ttkb.Frame(self.root, bootstyle="light")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a notebook for tabs
        notebook = ttkb.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        tab1 = ttkb.Frame(notebook)
        tab2 = ttkb.Frame(notebook)
        tab3 = ttkb.Frame(notebook)
        tab4 = ttkb.Frame(notebook)
        tab5 = ttkb.Frame(notebook)
        
        notebook.add(tab1, text="Datos de Vuelo")
        notebook.add(tab2, text="Alumnos")
        notebook.add(tab3, text="Tiempos")
        notebook.add(tab4, text="Descompresión Rápida")
        notebook.add(tab5, text="Reactores")
        
        # Add a placeholder label to each tab
        for i, tab in enumerate([tab1, tab2, tab3, tab4, tab5]):
            label = ttkb.Label(
                tab,
                text=f"Tab {i+1} Content",
                font=("Segoe UI", 18),
                bootstyle="primary"
            )
            label.pack(pady=50)

class WelcomeScreen:
    def __init__(self, root):
        self.root = root
        
        # Configure the window
        self.root.title("Bienvenido")
        self.root.geometry("1200x800")
        
        # Create main frame
        self.main_frame = ttkb.Frame(self.root, bootstyle="light")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create welcome screen
        self.create_welcome_screen()
    
    def create_welcome_screen(self):
        """Create an attractive welcome screen"""
        # Top decorative bar
        top_bar = ttkb.Frame(self.main_frame, height=10, bootstyle="primary")
        top_bar.pack(fill=tk.X, side=tk.TOP)
        
        # Content container with padding
        content = ttkb.Frame(self.main_frame, padding=30)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Logo/header section
        header_frame = ttkb.Frame(content)
        header_frame.pack(fill=tk.X, pady=(50, 30))
        
        # Try to load logo if exists, otherwise use text
        logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.jpg')
        if os.path.exists(logo_path):
            try:
                # Load and resize logo
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((200, 200), Image.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = ttkb.Label(header_frame, image=self.logo_photo)
                logo_label.pack(pady=10)
            except Exception as e:
                print(f"Error loading logo: {e}")
                self.use_text_header(header_frame)
        else:
            self.use_text_header(header_frame)
        
        # Main title
        title_frame = ttkb.Frame(content)
        title_frame.pack(fill=tk.X, pady=20)
        
        title = ttkb.Label(
            title_frame,
            text="SISTEMA DE REGISTRO",
            font=("Segoe UI", 32, "bold"),
            bootstyle="primary"
        )
        title.pack()
        
        # Subtitle
        subtitle = ttkb.Label(
            title_frame,
            text="ENTRENAMIENTO EN CÁMARA DE ALTURA",
            font=("Segoe UI", 20, "bold"),
            bootstyle="info"
        )
        subtitle.pack(pady=10)
        
        # Organization
        org_frame = ttkb.Frame(content)
        org_frame.pack(fill=tk.X, pady=30)
        
        org = ttkb.Label(
            org_frame,
            text="Fuerza Aérea Colombiana",
            font=("Segoe UI", 16),
            bootstyle="secondary"
        )
        org.pack()
        
        # Decorative separator
        separator = ttkb.Separator(content)
        separator.pack(fill=tk.X, pady=30)
        
        # Start button section
        button_frame = ttkb.Frame(content)
        button_frame.pack(fill=tk.X, pady=40)
        
        start_button = ttkb.Button(
            button_frame,
            text="INICIAR SISTEMA",
            bootstyle="success",
            width=25,
            padding=15,
            command=self.launch_main_app
        )
        start_button.pack()
        
        # Bottom decorative bar
        bottom_bar = ttkb.Frame(self.main_frame, height=10, bootstyle="primary")
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def use_text_header(self, parent):
        """Create a text-based header if logo is unavailable"""
        header = ttkb.Label(
            parent,
            text="FAC",
            font=("Segoe UI", 40, "bold"),
            bootstyle="primary"
        )
        header.pack(pady=10)
    
    def launch_main_app(self):
        """Launch the main application"""
        # Destroy welcome screen
        self.root.destroy()
        
        # Create main application window
        main_root = ttkb.Window(themename="litera")
        main_root.title("Registro Entrenamiento en Cámara de Altura")
        main_root.geometry("1200x800")
        
        # Center the window
        main_root.update_idletasks()
        width = main_root.winfo_width()
        height = main_root.winfo_height()
        x = (main_root.winfo_screenwidth() // 2) - (width // 2)
        y = (main_root.winfo_screenheight() // 2) - (height // 2)
        main_root.geometry(f'+{x}+{y}')
        
        # Initialize main application
        app = MainApp(main_root)
        
        # Start main application
        main_root.mainloop()

if __name__ == "__main__":
    # Create welcome screen with a modern theme
    root = ttkb.Window(themename="solar")
    app = WelcomeScreen(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')
    
    # Start application
    root.mainloop() 