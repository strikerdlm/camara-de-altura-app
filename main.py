#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import sys
import os
import locale
import datetime
from PIL import Image, ImageTk
import time

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
    
    try:
        from tab7_exportar import ExportarTab
        modules['ExportarTab'] = ExportarTab
        logger.info("Imported ExportarTab successfully")
    except ImportError as e:
        logger.error(f"Failed to import ExportarTab: {e}")
    
    return modules

# Import tab modules
tab_modules = import_tab_modules()

class SplashScreen:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        # Configure the window - completely borderless
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-alpha', 1.0)  # Full opacity
        
        # Set full background to black first (will be replaced by image)
        self.root.configure(bg="black")
        
        # Try to set the application icon
        self.set_icon()
        
        # Try to load welcome image
        try:
            self.create_splash_screen()
        except Exception as e:
            logger.error(f"Could not create splash screen with welcome image: {str(e)}")
            self.create_fallback_splash()
        
        # Set timer to close splash and open main application
        self.root.after(3000, self.close_splash)  # 3000 ms = 3 seconds

    @try_except_decorator(log_error=True)
    def set_icon(self):
        """Set the application icon using PNG directly"""
        # Direct use of PNG for splash screen
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            try:
                # For PNG icons, use PhotoImage
                icon_img = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, icon_photo)
                # Keep a reference to prevent garbage collection
                self.icon_photo = icon_photo
                logger.info("Splash screen icon set successfully")
            except Exception as e:
                logger.error(f"Could not set splash screen icon: {e}")
        else:
            logger.error(f"Icon file not found: {icon_path}")
    
    def create_splash_screen(self):
        """Create splash screen with just the welcome image and nothing else"""
        # Check if welcome image exists - use absolute path
        welcome_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "welcome.png")
        if not os.path.exists(welcome_path):
            logger.error(f"Welcome image not found at {welcome_path}")
            raise FileNotFoundError(f"Welcome image not found at {welcome_path}")
        
        logger.info(f"Loading welcome image from: {welcome_path}")
        
        # Load welcome image directly
        try:
            # Open the image file at original size
            welcome_img = Image.open(welcome_path)
            img_width, img_height = welcome_img.size
            logger.info(f"Image loaded successfully, size: {img_width}x{img_height}")
            
            # Resize the window to exactly match the image dimensions
            self.root.geometry(f"{img_width}x{img_height}+0+0")
            
            # Center the window on screen
            self.center_window(img_width, img_height)
            
            # Convert to Tkinter-compatible photo image (no resize)
            self.welcome_photo = ImageTk.PhotoImage(welcome_img)
            
            # Create a label with the image and no borders/padding
            image_label = tk.Label(
                self.root, 
                image=self.welcome_photo, 
                borderwidth=0, 
                highlightthickness=0, 
                padx=0, 
                pady=0,
                bg="black"
            )
            image_label.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            
            # Force update to make sure the image is displayed
            self.root.update_idletasks()
            self.root.update()
            
        except Exception as e:
            logger.error(f"Error processing welcome image: {str(e)}")
            raise
    
    def center_window(self, width, height):
        """Center the window on the screen"""
        try:
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calculate position
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            # Position window
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            logger.warning(f"Could not center window: {e}")
    
    def create_fallback_splash(self):
        """Create a fallback splash screen without images"""
        # Create content frame with black background
        content_frame = ttkb.Frame(self.root, bootstyle="dark")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title_label = ttkb.Label(
            content_frame,
            text="FUERZA AEROESPACIAL COLOMBIANA",
            font=("Segoe UI", 36, "bold"),
            bootstyle="inverse-dark"
        )
        title_label.pack(pady=(200, 20))
        
        # Add subtitle
        subtitle_label = ttkb.Label(
            content_frame,
            text="ENTRENAMIENTO HIPOXIA HIPOBÁRICA",
            font=("Segoe UI", 28, "bold"),
            bootstyle="inverse-dark"
        )
        subtitle_label.pack(pady=20)
    
    def close_splash(self):
        """Close splash screen and launch main application"""
        # Hide the splash screen but don't destroy it yet
        self.root.withdraw()
        
        # Launch the main application
        self.callback()

class WelcomeScreen:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        # Configure the window
        self.root.title("Bienvenido")
        self.root.geometry("1200x800")
        
        if ui_toolkit != "tkinter":
            self.root.configure(bg="white")
        
        # Set the application icon
        self.set_icon()
        
        # Try to load logo image if available, otherwise create fallback welcome screen
        try:
            self.create_welcome_with_logo()
        except Exception as e:
            logger.warning(f"Could not create welcome screen with logo: {e}")
            self.create_fallback_welcome()
    
    @try_except_decorator(log_error=True)
    def set_icon(self):
        """Set the application icon using PNG directly"""
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            try:
                # Use PhotoImage for PNG icons
                icon_img = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, icon_photo)
                # Keep a reference to prevent garbage collection
                self.icon_photo = icon_photo
                logger.info("Welcome screen icon set successfully")
            except Exception as e:
                logger.error(f"Could not set welcome screen icon: {e}")
        else:
            logger.error(f"Icon file not found: {icon_path}")
    
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
    """Main Application Class"""
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Registro de Hipoxia")
        
        # Set window size and fullscreen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height-80}+0+0")
        # self.root.attributes('-fullscreen', True)  # Uncomment for fullscreen
        
        # Create data manager
        self.data_manager = DataManager()
        
        # Setup GUI
        self.setup_ui()
        
        # Set the application icon
        self.set_icon()
        
        # Load existing data
        self.data_manager.load_data()

    @try_except_decorator(log_error=True)
    def set_icon(self):
        """Set the application icon using the PNG directly"""
        # Use the PNG icon directly with in-memory conversion
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            try:
                # Load the image
                icon_img = Image.open(icon_path)
                
                # Create PhotoImage for Tkinter
                icon_photo = ImageTk.PhotoImage(icon_img)
                
                # Set as window icon
                self.root.iconphoto(True, icon_photo)
                
                # Keep a reference to prevent garbage collection
                self.icon_photo = icon_photo
                logger.info("Application icon set successfully")
            except Exception as e:
                logger.error(f"Icon setting failed: {e}")
        else:
            logger.error(f"Icon file not found at {icon_path}")

    def setup_ui(self):
        """Create the main UI elements"""
        # Create a notebook for tabs
        self.notebook = ttkb.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_tabs()

    def create_tabs(self):
        """Create all application tabs with fallbacks for missing modules"""
        # Create basic fallback frames for any missing tab classes
        fallback_frame_classes = {}
        
        # Tab 1: Vuelo (Flight Data)
        if 'VueloTab' in tab_modules:
            self.tab1 = tab_modules['VueloTab'](self.notebook, self.data_manager, self)
            self.notebook.add(self.tab1, text="Datos generales")
            logger.info("Added VueloTab")
        else:
            self.tab1 = self.create_fallback_tab("Vuelo", "Este módulo no está disponible")
            self.notebook.add(self.tab1, text="Datos generales")
            logger.warning("Using fallback for VueloTab")
        
        # Tab 2: Alumnos (Students)
        if 'AlumnosTab' in tab_modules:
            self.tab2 = tab_modules['AlumnosTab'](self.notebook, self.data_manager, self)
            self.notebook.add(self.tab2, text="Alumnos")
            logger.info("Added AlumnosTab")
        else:
            self.tab2 = self.create_fallback_tab("Alumnos", "Este módulo no está disponible")
            self.notebook.add(self.tab2, text="Alumnos")
            logger.warning("Using fallback for AlumnosTab")
        
        # Tab 3: Tiempos (Times)
        if 'TiemposTab' in tab_modules:
            self.tab3 = tab_modules['TiemposTab'](self.notebook, self.data_manager, self)
            self.notebook.add(self.tab3, text="Tiempos")
            logger.info("Added TiemposTab")
        else:
            self.tab3 = self.create_fallback_tab("Tiempos", "Este módulo no está disponible")
            self.notebook.add(self.tab3, text="Tiempos")
            logger.warning("Using fallback for TiemposTab")
        
        # Tab 4: RD (Rapid Decompression)
        if 'RDTab' in tab_modules:
            self.tab4 = tab_modules['RDTab'](self.notebook, self.data_manager, self)
            self.notebook.add(self.tab4, text="RD")
            logger.info("Added RDTab")
        else:
            self.tab4 = self.create_fallback_tab("RD", "Este módulo no está disponible")
            self.notebook.add(self.tab4, text="RD")
            logger.warning("Using fallback for RDTab")
        
        # Tab 5: Reactores (Reactions)
        if 'ReactoresTab' in tab_modules:
            self.tab5 = tab_modules['ReactoresTab'](self.notebook, self.data_manager, self)
            self.notebook.add(self.tab5, text="Reactores")
            logger.info("Added ReactoresTab")
        else:
            self.tab5 = self.create_fallback_tab("Reactores", "Este módulo no está disponible")
            self.notebook.add(self.tab5, text="Reactores")
            logger.warning("Using fallback for ReactoresTab")
        
        # Tab 6: Sintomas (Symptoms)
        if 'SintomasTab' in tab_modules:
            self.tab6 = tab_modules['SintomasTab'](self.notebook, self.data_manager, self)
            self.notebook.add(self.tab6, text="Síntomas")
            logger.info("Added SintomasTab")
        else:
            self.tab6 = self.create_fallback_tab("Síntomas", "Este módulo no está disponible")
            self.notebook.add(self.tab6, text="Síntomas")
            logger.warning("Using fallback for SintomasTab")
        
        # Tab 7: Exportar (Export)
        if 'ExportarTab' in tab_modules:
            self.tab7 = tab_modules['ExportarTab'](self.notebook, self.data_manager, self)
            self.notebook.add(self.tab7, text="Exportar")
            logger.info("Added ExportarTab")
        else:
            self.tab7 = self.create_fallback_tab("Exportar", "Este módulo no está disponible")
            self.notebook.add(self.tab7, text="Exportar")
            logger.warning("Using fallback for ExportarTab")
            
        # Set up tab change event to refresh data when switching tabs
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """Refresh the newly selected tab with latest data."""
        try:
            current_tab_idx = self.notebook.index(self.notebook.select())
            current_tab = None
            
            # Map index to tab object
            if current_tab_idx == 0:
                current_tab = self.tab1
            elif current_tab_idx == 1:
                current_tab = self.tab2
            elif current_tab_idx == 2:
                current_tab = self.tab3
            elif current_tab_idx == 3:
                current_tab = self.tab4
            elif current_tab_idx == 4:
                current_tab = self.tab5
            elif current_tab_idx == 5:
                current_tab = self.tab6
            elif current_tab_idx == 6:
                current_tab = self.tab7
            
            # Reload data for the current tab
            if current_tab and hasattr(current_tab, 'load_data'):
                current_tab.load_data()
                logger.info(f"Refreshed tab {current_tab_idx} on selection")
        except Exception as e:
            logger.error(f"Error refreshing tab on change: {e}")
    
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
    
    def refresh_all_tabs(self):
        """Refresh data in all tabs - called after data changes"""
        print("Refreshing all tabs with updated data")
        
        # Get the current session ID
        session_id = self.data_manager.get_current_session_id()
        print(f"Current session ID: {session_id}")
        
        # Refresh tab1 (VueloTab)
        if hasattr(self, 'tab1') and hasattr(self.tab1, 'load_data'):
            try:
                self.tab1.load_data()
                print("Refreshed Tab1: Vuelo")
            except Exception as e:
                logger.error(f"Error refreshing tab1: {e}")
                
        # Refresh tab2 (AlumnosTab)
        if hasattr(self, 'tab2') and hasattr(self.tab2, 'load_data'):
            try:
                self.tab2.load_data()
                print("Refreshed Tab2: Alumnos")
            except Exception as e:
                logger.error(f"Error refreshing tab2: {e}")
                
        # Refresh tab3 (TiemposTab)
        if hasattr(self, 'tab3') and hasattr(self.tab3, 'load_data'):
            try:
                self.tab3.load_data()
                print("Refreshed Tab3: Tiempos")
            except Exception as e:
                logger.error(f"Error refreshing tab3: {e}")
                
        # Refresh tab4 (RDTab)
        if hasattr(self, 'tab4') and hasattr(self.tab4, 'load_data'):
            try:
                self.tab4.load_data()
                print("Refreshed Tab4: RD")
            except Exception as e:
                logger.error(f"Error refreshing tab4: {e}")
                
        # Refresh tab5 (ReactoresTab)
        if hasattr(self, 'tab5') and hasattr(self.tab5, 'load_data'):
            try:
                self.tab5.load_data()
                print("Refreshed Tab5: Reactores")
            except Exception as e:
                logger.error(f"Error refreshing tab5: {e}")
                
        # Refresh tab6 (SintomasTab)
        if hasattr(self, 'tab6') and hasattr(self.tab6, 'load_data'):
            try:
                self.tab6.load_data()
                print("Refreshed Tab6: Sintomas")
            except Exception as e:
                logger.error(f"Error refreshing tab6: {e}")
                
        # Refresh tab7 (ExportarTab) if it exists
        if hasattr(self, 'tab7') and hasattr(self.tab7, 'load_data'):
            try:
                self.tab7.load_data()
                print("Refreshed Tab7: Exportar")
            except Exception as e:
                logger.error(f"Error refreshing tab7: {e}")
        
        print("All tabs refreshed successfully")
    
    def get_current_session_id(self):
        """Get the ID of the current session from data_manager."""
        return self.data_manager.get_current_session_id()

def launch_main_app():
    """Launch the main application with error handling"""
    logger.info("Launching main application...")
    
    try:
        global splash_root
        
        # Instead of destroying and recreating the window, reuse it
        if splash_root:
            # Remove overrideredirect to restore window decorations
            splash_root.overrideredirect(False)
            
            # Clear all widgets
            for widget in splash_root.winfo_children():
                widget.destroy()
            
            # Reconfigure window for main app
            splash_root.title("Registro Entrenamiento en Cámara de Altura")
            splash_root.geometry("1200x800")
            splash_root.minsize(1000, 700)
            
            # Create the main application instance with the same root
            app = MainApp(splash_root)
            logger.info("Main application UI created on existing window")
            
            # Make the window visible again
            splash_root.deiconify()
        else:
            logger.error("Splash window not available, creating new window")
            # Create main application window if splash_root somehow not available
            main_root = ttkb.Window(themename=THEME) if THEME and ui_toolkit == "ttkbootstrap" else ttkb.Window()
            main_root.title("Registro Entrenamiento en Cámara de Altura")
            main_root.geometry("1200x800")
            main_root.minsize(1000, 700)
            
            # Set icon for the main window when creating a new window
            try:
                # Use PNG icon directly
                png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
                if os.path.exists(png_path):
                    icon_img = Image.open(png_path)
                    icon_photo = ImageTk.PhotoImage(icon_img)
                    main_root.iconphoto(True, icon_photo)
                    # Store reference to prevent garbage collection
                    main_root._icon_photo = icon_photo
                    logger.info("Main window icon set successfully")
                else:
                    logger.error(f"Icon file not found at {png_path}")
            except Exception as e:
                logger.error(f"Setting main window icon failed: {e}")
            
            # Create the main application instance
            app = MainApp(main_root)
            logger.info("Main application UI created on new window")
            
            # Start the Tkinter main loop
            main_root.mainloop()
            
    except Exception as e:
        handle_critical_exception(e)

# Ensure the global variable for the splash screen is accessible
splash_root = None

if __name__ == "__main__":
    try:
        # Create directories if they don't exist
        for dir_name in ["assets", "data", "logs", "backup"]:
            os.makedirs(os.path.join(os.path.dirname(__file__), dir_name), exist_ok=True)
        
        # Create splash screen window
        logger.info("Starting application with splash screen")
        splash_root = ttkb.Window(themename=THEME) if THEME and ui_toolkit == "ttkbootstrap" else ttkb.Window()
        
        # Create splash screen
        splash = SplashScreen(splash_root, launch_main_app)
        
        # Start the Tkinter main loop
        splash_root.mainloop()
    except Exception as e:
        handle_critical_exception(e)
