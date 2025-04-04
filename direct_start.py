#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import sys
import os
import locale
import datetime
import logging

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/direct_start.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("direct_start")

# Ensure directories exist
for dir_name in ["assets", "data", "logs", "backup"]:
    os.makedirs(dir_name, exist_ok=True)

# Find the UI toolkit to use
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    toolkit = "ttkbootstrap"
    logger.info("Using ttkbootstrap")
except ImportError:
    try:
        import tkinter.ttk as ttk
        ttkb = ttk
        toolkit = "ttk"
        logger.info("Using ttk (ttkbootstrap not found)")
    except ImportError:
        ttkb = tk
        toolkit = "tk"
        logger.info("Using tk (ttk not found)")

class SimpleApp:
    def __init__(self, root):
        self.root = root
        
        # Configure the window
        self.root.title("Registro Entrenamiento en Cámara de Altura")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Create a frame with a button to launch the real app
        self.frame = ttkb.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header = ttkb.Label(
            self.frame, 
            text="Sistema de Registro de Cámara de Altura",
            font=("Segoe UI", 24, "bold")
        )
        self.header.pack(pady=40)
        
        # Subtitle
        self.subtitle = ttkb.Label(
            self.frame,
            text="Fuerza Aérea Colombiana",
            font=("Segoe UI", 18)
        )
        self.subtitle.pack(pady=20)
        
        # Launch button
        self.button = ttkb.Button(
            self.frame,
            text="INICIAR APLICACIÓN",
            command=self.launch_main_app
        )
        self.button.pack(pady=50)
        
    def launch_main_app(self):
        # Import the main application
        try:
            logger.info("Importing main application...")
            import main
            from main import MainApp
            
            # Hide the current window (don't destroy it)
            self.root.withdraw()
            
            # Create a new window for the main app
            logger.info("Creating main application window...")
            main_window = ttkb.Window()
            main_window.title("Registro Entrenamiento en Cámara de Altura")
            main_window.geometry("1200x800")
            main_window.minsize(1000, 700)
            
            # Center it
            width, height = 1200, 800
            x = (main_window.winfo_screenwidth() // 2) - (width // 2)
            y = (main_window.winfo_screenheight() // 2) - (height // 2)
            main_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Create the main app
            logger.info("Creating main application...")
            app = MainApp(main_window)
            logger.info("Main application created successfully")
            
            # Set up a callback to close both windows when the main app closes
            def on_main_close():
                logger.info("Main application closing...")
                main_window.destroy()
                self.root.destroy()
                
            main_window.protocol("WM_DELETE_WINDOW", on_main_close)
            
            # Start the main app's event loop
            main_window.mainloop()
            
        except Exception as e:
            logger.error(f"Error launching main app: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error to user
            tk.messagebox.showerror(
                "Error", 
                f"No se pudo iniciar la aplicación principal: {str(e)}\n\n"
                "Por favor consulte los registros para más detalles."
            )

if __name__ == "__main__":
    try:
        # Create main window
        logger.info("Starting application...")
        root = ttkb.Window()
        root.title("Iniciador - Cámara de Altura")
        
        # Center the window
        width, height = 800, 600
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create simple launcher
        app = SimpleApp(root)
        
        # Start the app
        logger.info("Starting main loop...")
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        import traceback
        traceback.print_exc() 