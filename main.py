#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import sys
import os
import locale
import datetime
from PIL import Image, ImageTk

# Import error handling system before anything else
try:
    from error_handler import (
        initialize_error_handling, handle_critical_exception, 
        logger, try_except_decorator, AppError, DependencyError,
        DependencyFallback, get_platform_specific_module
    )
    
    # Initialize error handling early
    initialize_error_handling()
except ImportError:
    # Basic error handling if error_handler.py is missing
    import logging
    import traceback
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("logs/fallback_error.log"), logging.StreamHandler()]
    )
    logger = logging.getLogger("fallback")
    logger.error("Could not import error_handler.py, using fallback error handling")
    
    # Define minimal functions to allow program to continue
    def handle_critical_exception(e, exit_code=1):
        logger.critical(f"CRITICAL ERROR: {str(e)}")
        traceback.print_exc()
        sys.exit(exit_code)
    
    def try_except_decorator(fallback_value=None, log_error=True, show_user=False, retry_count=0):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if log_error:
                        logger.error(f"Error in {func.__name__}: {str(e)}")
                    return fallback_value
            return wrapper
        return decorator
    
    class AppError(Exception):
        pass
    
    class DependencyError(AppError):
        pass
    
    class DependencyFallback:
        @staticmethod
        def get_ui_toolkit():
            try:
                import ttkbootstrap
                return "ttkbootstrap"
            except ImportError:
                try:
                    from tkinter import ttk
                    return "ttk"
                except ImportError:
                    return "tkinter"
    
    def get_platform_specific_module(windows_module, linux_module, mac_module=None, fallback_module=None):
        import platform
        system = platform.system().lower()
        if system == 'windows':
            return windows_module
        elif system == 'darwin':
            return mac_module or linux_module
        else:
            return linux_module

# Set the locale to Spanish - with fallback
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES')
    except locale.Error:
        logger.warning("Could not set Spanish locale, using system default")

# Import UI toolkit with fallbacks
ui_toolkit = DependencyFallback.get_ui_toolkit()
logger.info(f"Using UI toolkit: {ui_toolkit}")

if ui_toolkit == "ttkbootstrap":
    try:
        import ttkbootstrap as ttkb
        from ttkbootstrap.constants import *
        from ttkbootstrap.scrolled import ScrolledFrame
        THEME = "litera"  # Modern light theme for ttkbootstrap
        logger.info("Successfully imported ttkbootstrap")
    except ImportError as e:
        logger.error(f"Failed to import ttkbootstrap: {e}")
        ui_toolkit = "ttk"  # Fallback to standard ttk

if ui_toolkit == "ttk":
    try:
        import tkinter.ttk as ttk
        ttkb = ttk  # Alias for compatibility
        THEME = None  # No theming in standard ttk
        
        # Create minimal replacement for ScrolledFrame
        class ScrolledFrame(ttk.Frame):
            def __init__(self, master=None, **kwargs):
                super().__init__(master, **kwargs)
                self.canvas = tk.Canvas(self)
                self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
                self.container = ttk.Frame(self.canvas)
                
                self.canvas.configure(yscrollcommand=self.scrollbar.set)
                self.canvas.create_window((0, 0), window=self.container, anchor="nw")
                
                self.canvas.pack(side="left", fill="both", expand=True)
                self.scrollbar.pack(side="right", fill="y")
                
                self.container.bind("<Configure>", lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox("all")))
                
        logger.info("Successfully imported ttk fallback")
    except ImportError as e:
        logger.error(f"Failed to import ttk: {e}")
        ui_toolkit = "tkinter"  # Fallback to basic tkinter

if ui_toolkit == "tkinter":
    # Create minimal replacements for ttkbootstrap/ttk
    logger.warning("Using basic tkinter fallback - UI will be minimal")
    
    class MinimalFrame(tk.Frame):
        def __init__(self, master=None, bootstyle=None, padding=0, **kwargs):
            padding_x = padding if isinstance(padding, int) else padding[0] if isinstance(padding, tuple) else 0
            padding_y = padding if isinstance(padding, int) else padding[1] if isinstance(padding, tuple) else 0
            super().__init__(master, padx=padding_x, pady=padding_y, **kwargs)
    
    class MinimalButton(tk.Button):
        def __init__(self, master=None, bootstyle=None, **kwargs):
            super().__init__(master, **kwargs)
    
    class MinimalLabel(tk.Label):
        def __init__(self, master=None, bootstyle=None, **kwargs):
            super().__init__(master, **kwargs)
    
    class MinimalEntry(tk.Entry):
        def __init__(self, master=None, bootstyle=None, **kwargs):
            super().__init__(master, **kwargs)
    
    class ScrolledFrame(tk.Frame):
        def __init__(self, master=None, autohide=True, **kwargs):
            super().__init__(master, **kwargs)
            self.canvas = tk.Canvas(self)
            self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.container = tk.Frame(self.canvas)
            
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.canvas.create_window((0, 0), window=self.container, anchor="nw")
            
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
            
            self.container.bind("<Configure>", lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
    
    # Create a minimal Window class like ttkbootstrap's
    class Window(tk.Tk):
        def __init__(self, themename=None, **kwargs):
            super().__init__(**kwargs)
    
    # Assign our minimal classes to ttkb
    ttkb = type('ttkb', (), {
        'Frame': MinimalFrame,
        'Button': MinimalButton,
        'Label': MinimalLabel,
        'Entry': MinimalEntry,
        'Window': Window
    })
    
    THEME = None

# Try to import application modules with error handling
try:
    from config import AppConfig
    from data_manager import DataManager
    logger.info("Successfully imported core modules")
except ImportError as e:
    handle_critical_exception(DependencyError(
        f"Failed to import core modules: {e}",
        dependency_name="config/data_manager",
        is_critical=True
    ))

# Try to import tab modules - with fallback options
@try_except_decorator(fallback_value=None, log_error=True)
def import_tab_modules():
    modules = {}
    
    try:
        from tab1_vuelo import VueloTab
        modules['VueloTab'] = VueloTab
        logger.info("Imported VueloTab successfully")
    except ImportError as e:
        logger.error(f"Failed to import VueloTab: {e}")
        # Will attempt fallback in the MainApp class
    
    try:
        from tab2_alumnos import AlumnosTab
        modules['AlumnosTab'] = AlumnosTab
        logger.info("Imported AlumnosTab successfully")
    except ImportError as e:
        logger.error(f"Failed to import AlumnosTab: {e}")
    
    try:
        from tab3_tiempos import TiemposTab
        modules['TiemposTab'] = TiemposTab
        logger.info("Imported TiemposTab successfully")
    except ImportError as e:
        logger.error(f"Failed to import TiemposTab: {e}")
    
    try:
        from tab4_rd import RDTab
        modules['RDTab'] = RDTab
        logger.info("Imported RDTab successfully")
    except ImportError as e:
        logger.error(f"Failed to import RDTab: {e}")
    
    try:
        from tab5_reactores import ReactoresTab
        modules['ReactoresTab'] = ReactoresTab
        logger.info("Imported ReactoresTab successfully")
    except ImportError as e:
        logger.error(f"Failed to import ReactoresTab: {e}")
    
    try:
        from tab6_sintomas import SintomasTab
        modules['SintomasTab'] = SintomasTab
        logger.info("Imported SintomasTab successfully")
    except ImportError as e:
        logger.error(f"Failed to import SintomasTab: {e}")
    
    return modules

# Import tab modules
tab_modules = import_tab_modules()

class WelcomeScreen:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        # Configure the window
        self.root.title("Bienvenido")
        self.root.geometry("1200x800")
        
        if ui_toolkit != "tkinter":
            self.root.configure(bg="white")
        
        # Try to load logo image if available, otherwise create fallback welcome screen
        try:
            self.create_welcome_with_logo()
        except Exception as e:
            logger.warning(f"Could not create welcome screen with logo: {e}")
            self.create_fallback_welcome()
    
    @try_except_decorator(log_error=True)
    def create_welcome_with_logo(self):
        """Create welcome screen with logo if available"""
        # Check if logo exists
        logo_path = os.path.join("assets", "logo.png")
        if not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found at {logo_path}")
        
        # Create content frame
        content_frame = ttkb.Frame(self.root, bootstyle="light")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a header
        header_frame = ttkb.Frame(content_frame, bootstyle="primary")
        header_frame.pack(fill=tk.X, ipady=30)
        
        header_label = ttkb.Label(
            header_frame,
            text="SISTEMA DE REGISTRO",
            font=("Segoe UI", 24, "bold"),
            bootstyle="inverse-primary"
        )
        header_label.pack(pady=20)
        
        # Load and display logo
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((200, 200), Image.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        
        # Store reference to prevent garbage collection
        self.logo_photo = logo_photo
        
        logo_label = ttkb.Label(content_frame, image=logo_photo, bootstyle="light")
        logo_label.pack(pady=20)
        
        # Add subtitle
        subtitle_frame = ttkb.Frame(content_frame)
        subtitle_frame.pack(fill=tk.X, pady=20)
        
        subtitle_label = ttkb.Label(
            subtitle_frame,
            text="ENTRENAMIENTO EN CÁMARA DE ALTURA",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        subtitle_label.pack()
        
        # Add organization name
        org_frame = ttkb.Frame(content_frame)
        org_frame.pack(fill=tk.X, pady=20)
        
        org_label = ttkb.Label(
            org_frame,
            text="Fuerza Aérea Colombiana",
            font=("Segoe UI", 14),
            bootstyle="secondary"
        )
        org_label.pack()
        
        # Add start button - Make it more prominent
        button_frame = ttkb.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=50)
        
        # Clear instruction text
        instruction_label = ttkb.Label(
            button_frame,
            text="Haga clic en el botón para iniciar el sistema",
            font=("Segoe UI", 12),
            bootstyle="info"
        )
        instruction_label.pack(pady=10)
        
        start_button = ttkb.Button(
            button_frame,
            text="INICIAR SISTEMA",
            command=self.callback,
            style="success.TButton"
        )
        if ui_toolkit == "ttkbootstrap":
            start_button.configure(bootstyle="success", width=30, padding=15)
        else:
            start_button.configure(width=30)
        
        start_button.pack(pady=20)
    
    def create_fallback_welcome(self):
        """Create a fallback welcome screen without images"""
        # Create content frame
        content_frame = ttkb.Frame(self.root, bootstyle="light")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a header
        header_frame = ttkb.Frame(content_frame, bootstyle="primary")
        header_frame.pack(fill=tk.X, ipady=30)
        
        header_label = ttkb.Label(
            header_frame,
            text="SISTEMA DE REGISTRO",
            font=("Segoe UI", 24, "bold"),
            bootstyle="inverse-primary"
        )
        header_label.pack(pady=20)
        
        # Add subtitle
        subtitle_frame = ttkb.Frame(content_frame)
        subtitle_frame.pack(fill=tk.X, pady=40)
        
        subtitle_label = ttkb.Label(
            subtitle_frame,
            text="ENTRENAMIENTO EN CÁMARA DE ALTURA",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        subtitle_label.pack()
        
        # Add organization name
        org_frame = ttkb.Frame(content_frame)
        org_frame.pack(fill=tk.X, pady=20)
        
        org_label = ttkb.Label(
            org_frame,
            text="Fuerza Aérea Colombiana",
            font=("Segoe UI", 14),
            bootstyle="secondary"
        )
        org_label.pack()
        
        # Add start button - Make it more prominent
        button_frame = ttkb.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=50)
        
        # Clear instruction text
        instruction_label = ttkb.Label(
            button_frame,
            text="Haga clic en el botón para iniciar el sistema",
            font=("Segoe UI", 12),
            bootstyle="info"
        )
        instruction_label.pack(pady=10)
        
        start_button = ttkb.Button(
            button_frame,
            text="INICIAR SISTEMA",
            command=self.callback,
            style="success.TButton"
        )
        if ui_toolkit == "ttkbootstrap":
            start_button.configure(bootstyle="success", width=30, padding=15)
        else:
            start_button.configure(width=30)
            
        start_button.pack(pady=20)

class MainApp:
    def __init__(self, root):
        self.root = root
        self.config = AppConfig()
        self.data_manager = DataManager()
        
        # Configure the main window
        self.root.title("Registro Entrenamiento en Cámara de Altura")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Set application icon if available
        self.set_icon()
        
        # Create main frame
        self.main_container = ttkb.Frame(self.root, bootstyle="light")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.main_container) if ui_toolkit == "ttk" else ttkb.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs with fallbacks
        self.create_tabs()
        
        # Set up autosave timer
        self.setup_autosave()
        
        logger.info("MainApp initialized successfully")
    
    @try_except_decorator(log_error=True)
    def set_icon(self):
        """Set the application icon if available"""
        icon_path = os.path.join("assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
                logger.info("Application icon set successfully")
            except Exception as e:
                logger.warning(f"Could not set application icon: {e}")
    
    def create_tabs(self):
        """Create all application tabs with fallbacks for missing modules"""
        # Create basic fallback frames for any missing tab classes
        fallback_frame_classes = {}
        
        # Tab 1: Vuelo (Flight Data)
        if 'VueloTab' in tab_modules:
            self.tab1 = tab_modules['VueloTab'](self.notebook, self.data_manager)
            self.notebook.add(self.tab1, text="Datos del entrenamiento de hipoxia hipobárica")
            logger.info("Added VueloTab")
        else:
            self.tab1 = self.create_fallback_tab("Vuelo", "Este módulo no está disponible")
            self.notebook.add(self.tab1, text="Datos del entrenamiento de hipoxia hipobárica")
            logger.warning("Using fallback for VueloTab")
        
        # Tab 2: Alumnos (Students)
        if 'AlumnosTab' in tab_modules:
            self.tab2 = tab_modules['AlumnosTab'](self.notebook, self.data_manager)
            self.notebook.add(self.tab2, text="Alumnos")
            logger.info("Added AlumnosTab")
        else:
            self.tab2 = self.create_fallback_tab("Alumnos", "Este módulo no está disponible")
            self.notebook.add(self.tab2, text="Alumnos")
            logger.warning("Using fallback for AlumnosTab")
        
        # Tab 3: Tiempos (Times)
        if 'TiemposTab' in tab_modules:
            self.tab3 = tab_modules['TiemposTab'](self.notebook, self.data_manager)
            self.notebook.add(self.tab3, text="Tiempos")
            logger.info("Added TiemposTab")
        else:
            self.tab3 = self.create_fallback_tab("Tiempos", "Este módulo no está disponible")
            self.notebook.add(self.tab3, text="Tiempos")
            logger.warning("Using fallback for TiemposTab")
        
        # Tab 4: RD
        if 'RDTab' in tab_modules:
            self.tab4 = tab_modules['RDTab'](self.notebook, self.data_manager)
            self.notebook.add(self.tab4, text="Descompresión Rápida")
            logger.info("Added RDTab")
        else:
            self.tab4 = self.create_fallback_tab("RD", "Este módulo no está disponible")
            self.notebook.add(self.tab4, text="Descompresión Rápida")
            logger.warning("Using fallback for RDTab")
        
        # Tab 5: Reactores (Reactors)
        if 'ReactoresTab' in tab_modules:
            self.tab5 = tab_modules['ReactoresTab'](self.notebook, self.data_manager)
            self.notebook.add(self.tab5, text="Reactores")
            logger.info("Added ReactoresTab")
        else:
            self.tab5 = self.create_fallback_tab("Reactores", "Este módulo no está disponible")
            self.notebook.add(self.tab5, text="Reactores")
            logger.warning("Using fallback for ReactoresTab")
        
        # Tab 6: Síntomas (Symptoms)
        if 'SintomasTab' in tab_modules:
            self.tab6 = tab_modules['SintomasTab'](self.notebook, self.data_manager)
            self.notebook.add(self.tab6, text="Síntomas")
            logger.info("Added SintomasTab")
        else:
            self.tab6 = self.create_fallback_tab("Síntomas", "Este módulo no está disponible")
            self.notebook.add(self.tab6, text="Síntomas")
            logger.warning("Using fallback for SintomasTab")
    
    def create_fallback_tab(self, name, message):
        """Create a fallback tab when a module is missing"""
        frame = ttkb.Frame(self.notebook, padding=20)
        
        error_label = ttkb.Label(
            frame,
            text=f"Error: {message}",
            font=("Segoe UI", 14, "bold"),
            bootstyle="danger"
        )
        error_label.pack(pady=20)
        
        info_label = ttkb.Label(
            frame,
            text="Por favor, consulte los registros de errores para más detalles.",
            font=("Segoe UI", 12),
            wraplength=500
        )
        info_label.pack(pady=10)
        
        return frame
    
    def setup_autosave(self):
        """Setup autosave functionality with error handling"""
        # Rule: Autosave every 10 seconds
        autosave_interval_seconds = 10 
        autosave_interval_ms = autosave_interval_seconds * 1000
        
        @try_except_decorator(log_error=True)
        def autosave():
            try:
                self.data_manager.save_data()
                logger.debug(f"Autosave successful: {datetime.datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                logger.error(f"Error during autosave: {e}")
            finally:
                # Always reschedule the next autosave
                self._autosave_job = self.root.after(autosave_interval_ms, autosave)
        
        # Start the autosave timer
        self._autosave_job = self.root.after(autosave_interval_ms, autosave)
        logger.info(f"Autosave scheduled every {autosave_interval_seconds} seconds")

def launch_main_app():
    """Launch the main application with error handling"""
    logger.info("Launching main application...")
    
    try:
        global welcome_root
        
        # Instead of destroying and recreating the window, reuse it
        if welcome_root:
            # Clear all widgets
            for widget in welcome_root.winfo_children():
                widget.destroy()
            
            # Reconfigure window for main app
            welcome_root.title("Registro Entrenamiento en Cámara de Altura")
            welcome_root.geometry("1200x800")
            welcome_root.minsize(1000, 700)
            
            # Create the main application instance with the same root
            app = MainApp(welcome_root)
            logger.info("Main application UI created on existing window")
        else:
            logger.error("Welcome window not available, creating new window")
            # Create main application window if welcome_root somehow not available
            main_root = ttkb.Window(themename=THEME) if THEME else ttkb.Window()
            main_root.title("Registro Entrenamiento en Cámara de Altura")
            main_root.geometry("1200x800")
            main_root.minsize(1000, 700)
            
            # Create the main application instance
            app = MainApp(main_root)
            logger.info("Main application UI created on new window")
            
            # Start the Tkinter main loop
            main_root.mainloop()
            
    except Exception as e:
        handle_critical_exception(e)

# Ensure the welcome_root is accessible as a global variable
welcome_root = None

if __name__ == "__main__":
<<<<<<< HEAD
    try:
        # Create directories if they don't exist
        for dir_name in ["assets", "data", "logs", "backup"]:
            os.makedirs(os.path.join(os.path.dirname(__file__), dir_name), exist_ok=True)
        
        # Ensure assets directory has required files
        icon_path = os.path.join("assets", "icon.ico")
        if not os.path.exists(icon_path):
            logger.warning(f"Icon file not found at {icon_path}")
            # Could add code here to generate a default icon
        
        # Skip welcome screen and go straight to main application
        # Create the main app window directly
        logger.info("Starting application directly (skipping welcome screen)")
        main_root = ttkb.Window(themename=THEME) if THEME else ttkb.Window()
        main_root.title("Registro Entrenamiento en Cámara de Altura")
        
        # Center window
        main_root.update_idletasks()
        width = 1200
        height = 800
        try:
            x = (main_root.winfo_screenwidth() // 2) - (width // 2)
            y = (main_root.winfo_screenheight() // 2) - (height // 2)
            main_root.geometry(f'{width}x{height}+{x}+{y}')
        except Exception as e:
            logger.warning(f"Could not center window: {e}")
            main_root.geometry('1200x800')  # Fallback
            
        main_root.minsize(1000, 700)
        
        # Try to set the application icon if available
        try:
            if os.path.exists(icon_path):
                main_root.iconbitmap(icon_path)
                logger.info("Application icon set successfully")
        except Exception as e:
            logger.warning(f"Could not set application icon: {e}")
        
        # Create the main application instance
        app = MainApp(main_root)
        logger.info("Main application UI created")
        
        # Start main loop
        main_root.mainloop()
    except Exception as e:
        handle_critical_exception(e) 
=======
    # Create the welcome screen first
    welcome_root = ttkb.Window(themename="litera")  # Modern light theme
    welcome_app = WelcomeScreen(welcome_root, launch_main_app)
    
    # Center the window on screen
    welcome_root.update_idletasks()
    width = welcome_root.winfo_width()
    height = welcome_root.winfo_height()
    x = (welcome_root.winfo_screenwidth() // 2) - (width // 2)
    y = (welcome_root.winfo_screenheight() // 2) - (height // 2)
    welcome_root.geometry(f'+{x}+{y}')
    
    welcome_root.mainloop()
>>>>>>> 05623bafcb4dd46d5d368abaece58d4cebd092c3
