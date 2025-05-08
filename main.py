#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import sys
import os
import locale
import datetime
from PIL import Image, ImageTk
import time
import subprocess

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
        try:
            # Windows-specific locale names
            locale.setlocale(locale.LC_ALL, 'es-ES')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Spanish_Spain')
            except locale.Error:
                logger.warning("Could not set Spanish locale, using system default")

# Import UI toolkit with fallbacks
ui_toolkit = DependencyFallback.get_ui_toolkit()
logger.info(f"Using UI toolkit: {ui_toolkit}")

# Configure Pillow for Windows - prevent potential image loading issues
try:
    import PIL
    # Check if we're on Windows
    if os.name == 'nt':
        # Ensure Pillow can find image codecs on Windows
        os.environ['PATH'] = os.path.dirname(PIL.__file__) + os.pathsep + os.environ['PATH']
        logger.info("Added PIL directory to PATH for Windows")
        
        # Handle virtual environment paths for icon loading
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("Running in a virtual environment - adjusting icon paths")
            # Virtual environment detected - ensure PIL can fully access DLLs
            try:
                # Find the root of the virtual environment
                venv_root = sys.prefix
                # Add the virtual environment's DLLs to PATH
                os.environ['PATH'] = os.path.join(venv_root, 'Lib', 'site-packages', 'PIL') + os.pathsep + os.environ['PATH']
                os.environ['PATH'] = os.path.join(venv_root, 'DLLs') + os.pathsep + os.environ['PATH']
                logger.info("Added virtual environment paths to PATH for icon support")
            except Exception as e:
                logger.warning(f"Failed to add virtual environment paths: {e}")
except Exception as e:
    logger.warning(f"Could not configure PIL for Windows: {e}")

if ui_toolkit == "ttkbootstrap":
    try:
        import ttkbootstrap as ttkb
        from ttkbootstrap.constants import *
        from ttkbootstrap.scrolled import ScrolledFrame
        # Make ScrolledFrame available as a direct attribute of ttkb
        ttkb.ScrolledFrame = ScrolledFrame
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
    
    try:
        from tab8_about import AboutTab
        modules['AboutTab'] = AboutTab
        logger.info("Imported AboutTab successfully")
    except ImportError as e:
        logger.error(f"Failed to import AboutTab: {e}")
    
    return modules

# Import tab modules
tab_modules = import_tab_modules()

# Ensure icon works in virtual environments by directly embedding the icon creation logic
def create_high_dpi_ico(input_png, output_ico):
    """
    Creates a high-resolution ICO file optimized for Windows applications
    with special attention to DPI awareness.
    """
    if not os.path.exists(input_png):
        return False
    
    try:
        # Open original image
        img = Image.open(input_png)
        
        # Check if image is in RGBA mode (with transparency)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Standard sizes needed (in order of importance for Windows)
        # Place largest sizes first as Windows often uses the first size it finds
        icon_sizes = [256, 128, 96, 64, 48, 40, 32, 24, 16]
        
        # Filter out sizes larger than our source image
        original_width, original_height = img.size
        valid_sizes = [size for size in icon_sizes if size <= min(original_width, original_height)]
        
        if not valid_sizes:
            return False
            
        # Create a list of images to include in the ICO
        images = []
        for size in valid_sizes:
            # For best quality, use LANCZOS resampling
            resized = img.resize((size, size), Image.LANCZOS)
            images.append(resized)
        
        # Save as ICO - first image is most important for Windows display
        images[0].save(
            output_ico,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:] if len(images) > 1 else []
        )
        return True
    
    except Exception as e:
        return False

@try_except_decorator(log_error=True)
def set_window_icon(window, force_refresh=False):
    """
    Enhanced function to set high-resolution application icon with Windows DPI awareness 
    
    Args:
        window: The tkinter window to set the icon for
        force_refresh: If True, recreate the ICO file from source PNG before setting
    """
    # Icon file paths
    icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    ico_path = os.path.join(icon_dir, "icon.ico")
    png_path = os.path.join(icon_dir, "icon.png")
    
    logger.info(f"Setting window icon with ICO path: {ico_path}")
    
    # If requested, regenerate the ICO file for high-DPI
    if force_refresh and os.path.exists(png_path):
        try:
            logger.info("Regenerating high-DPI icon.ico from icon.png")
            # Directly generate the ICO file using our embedded function
            if create_high_dpi_ico(png_path, ico_path):
                logger.info("Successfully regenerated icon.ico")
            else:
                logger.warning("Could not generate icon.ico, will try other methods")
        except Exception as e:
            logger.error(f"Error regenerating icon.ico: {e}")
    
    success = False
    
    # TRY MULTIPLE METHODS TO SET ICON
    # Method 1: On Windows, use wm_iconbitmap - direct way to set icon
    if os.name == 'nt' and os.path.exists(ico_path):
        try:
            # For Windows, apply icon with a small delay and directly
            window.after(100, lambda: window.wm_iconbitmap(ico_path))
            # Also try immediate application
            try:
                window.wm_iconbitmap(ico_path)
            except Exception:
                pass
            logger.info("Set icon using wm_iconbitmap on Windows (.ico file)")
            success = True
        except Exception as e:
            logger.error(f"Error setting icon with wm_iconbitmap: {e}")
    
    # Method 2: Use PhotoImage approach - for non-Windows or as backup
    if not success and os.path.exists(png_path):
        try:
            # Load the image directly for iconphoto method
            img = Image.open(png_path)
            
            # Make sure it's in RGBA mode for transparency
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create multiple sizes for better icon display
            icon_images = []
            
            # Windows scaling sizes - in reverse order (largest first)
            sizes = [256, 128, 96, 64, 48, 32, 16]
            
            width, height = img.size
            for size in sizes:
                if size <= min(width, height):
                    try:
                        # Use high-quality LANCZOS resizing
                        resized = img.resize((size, size), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(resized)
                        icon_images.append(photo)
                    except Exception as e:
                        logger.error(f"Error creating icon size {size}: {e}")
            
            if icon_images:
                # Use iconphoto with all sizes (Tkinter standard method)
                if hasattr(window, 'iconphoto'):
                    # Apply the icon both immediately and after a short delay
                    try:
                        window.iconphoto(True, *icon_images)
                    except Exception:
                        pass
                    # Also apply after a delay
                    window.after(200, lambda: window.iconphoto(True, *icon_images))
                    # Store reference to prevent garbage collection
                    window._icon_images = icon_images
                    logger.info(f"Set icon using iconphoto with {len(icon_images)} sizes")
                    success = True
        except Exception as e:
            logger.error(f"Error setting icon with multi-size approach: {e}")

    # Method 3: If icon.ico exists but methods 1 and 2 failed, try setting with Tk call
    if not success and os.name == 'nt' and os.path.exists(ico_path):
        try:
            # Try low-level Tk call as a last resort (works in some environments where others fail)
            window.tk.call('wm', 'iconbitmap', window._w, ico_path)
            logger.info("Set icon using tk.call method")
            success = True
        except Exception as e:
            logger.error(f"Error setting icon with tk.call: {e}")
    
    # Return success status
    return success

class SplashScreen:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        # Configure the window - completely borderless
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-alpha', 1.0)  # Full opacity
        
        # Set full background to black first (will be replaced by image)
        self.root.configure(bg="black")
        
        # Try to set the application icon - force refresh on startup
        set_window_icon(self.root, force_refresh=True)
        
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
        """Set the application icon"""
        return set_window_icon(self.root)
    
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
        
        # Set the application icon with our improved function
        set_window_icon(self.root)
        
        # Try to load logo image if available, otherwise create fallback welcome screen
        try:
            self.create_welcome_with_logo()
        except Exception as e:
            logger.warning(f"Could not create welcome screen with logo: {e}")
            self.create_fallback_welcome()
    
    @try_except_decorator(log_error=True)
    def set_icon(self):
        """Set the application icon"""
        return set_window_icon(self.root)
    
    @try_except_decorator(log_error=True)
    def create_welcome_with_logo(self):
        """Create welcome screen with logo if available"""
        # Check if logo exists
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
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
        self.root.title("Sistema de Registro de Entrenamiento Fisiológico en Hipoxia Hipobárica - SUCAE / DIMAE")
        
        # Set window size and fullscreen - adjusted for Windows
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height-80}+0+0")
        
        # Create data manager
        self.data_manager = DataManager()

        # --- Persistent Top Bar Widgets ---
        self.topbar_frame = ttkb.Frame(self.root, bootstyle="light")
        self.topbar_frame.pack(fill=tk.X, side=tk.TOP, padx=0, pady=(0, 2))

        # --- All timers and segment in a single line, left-aligned ---
        # Hora local
        self.clock_var = tk.StringVar()
        self.clock_label = ttkb.Label(
            self.topbar_frame, text="Hora local:",
            font=("Segoe UI", 11, "bold"), bootstyle="danger",
            padding=(5, 0)
        )
        self.clock_label.pack(side=tk.LEFT, padx=(10, 2))
        self.clock_value = ttkb.Label(
            self.topbar_frame, textvariable=self.clock_var,
            font=("Consolas", 15, "bold"), bootstyle="danger",
            padding=(2, 0)
        )
        self.clock_value.pack(side=tk.LEFT, padx=(0, 10))

        # Separator
        self.sep1 = ttkb.Label(self.topbar_frame, text="-", font=("Segoe UI", 13, "bold"), padding=(5, 0))
        self.sep1.pack(side=tk.LEFT)

        # Tiempo Total
        self.total_timer_var = tk.StringVar(value="00:00:00")
        self.total_timer_label = ttkb.Label(
            self.topbar_frame, text="Tiempo Total:",
            font=("Segoe UI", 11, "bold"), bootstyle="success",
            padding=(5, 0)
        )
        self.total_timer_label.pack(side=tk.LEFT, padx=(10, 2))
        self.total_timer_value = ttkb.Label(
            self.topbar_frame, textvariable=self.total_timer_var,
            font=("Consolas", 15, "bold"), bootstyle="success",
            padding=(2, 0)
        )
        self.total_timer_value.pack(side=tk.LEFT, padx=(0, 10))

        # Separator
        self.sep2 = ttkb.Label(self.topbar_frame, text="-", font=("Segoe UI", 13, "bold"), padding=(5, 0))
        self.sep2.pack(side=tk.LEFT)

        # Tiempo del segmento
        self.chrono_var = tk.StringVar(value="00:00:00")
        self.chrono_label = ttkb.Label(
            self.topbar_frame, text="Tiempo del segmento:",
            font=("Segoe UI", 11, "bold"), bootstyle="info",
            padding=(5, 0)
        )
        self.chrono_label.pack(side=tk.LEFT, padx=(10, 2))
        self.chrono_value = ttkb.Label(
            self.topbar_frame, textvariable=self.chrono_var,
            font=("Consolas", 15, "bold"), bootstyle="info",
            padding=(2, 0)
        )
        self.chrono_value.pack(side=tk.LEFT, padx=(0, 10))

        # Separator
        self.sep3 = ttkb.Label(self.topbar_frame, text="-", font=("Segoe UI", 13, "bold"), padding=(5, 0))
        self.sep3.pack(side=tk.LEFT)

        # Segmento
        self.current_segment_var = tk.StringVar(value="-")
        self.segment_label = ttkb.Label(
            self.topbar_frame, text="Segmento:",
            font=("Segoe UI", 11, "bold"), bootstyle="secondary",
            padding=(5, 0)
        )
        self.segment_label.pack(side=tk.LEFT, padx=(10, 2))
        self.segment_value = ttkb.Label(
            self.topbar_frame, textvariable=self.current_segment_var,
            font=("Segoe UI", 13, "bold"), bootstyle="secondary",
            padding=(2, 0)
        )
        self.segment_value.pack(side=tk.LEFT, padx=(0, 10))

        # --- DNIT Segment Timer ---
        self.dnit_timer_var = tk.StringVar(value="00:00")
        self.dnit_timer_label = ttkb.Label(
            self.topbar_frame, text="DNIT:",
            font=("Segoe UI", 11, "bold"), bootstyle="danger",
            padding=(5, 0)
        )
        self.dnit_timer_value = ttkb.Label(
            self.topbar_frame, textvariable=self.dnit_timer_var,
            font=("Consolas", 15, "bold"), bootstyle="danger",
            padding=(2, 0)
        )
        # Not packed yet; will be packed only during DNIT segment
        self._dnit_timer_job = None
        self._dnit_start_time = None
        self._dnit_running = False

        # --- Hipoxia Segment Timer ---
        self.hipoxia_timer_var = tk.StringVar(value="00:00")
        self.hipoxia_timer_label = ttkb.Label(
            self.topbar_frame, text="HIPOXIA:",
            font=("Segoe UI", 11, "bold"), bootstyle="danger",
            padding=(5, 0)
        )
        self.hipoxia_timer_value = ttkb.Label(
            self.topbar_frame, textvariable=self.hipoxia_timer_var,
            font=("Consolas", 15, "bold"), bootstyle="danger",
            padding=(2, 0)
        )
        self._hipoxia_timer_job = None
        self._hipoxia_start_time = None
        self._hipoxia_running = False

        # --- Vision Nocturna Segment Timer ---
        self.vision_timer_var = tk.StringVar(value="00:00")
        self.vision_timer_label = ttkb.Label(
            self.topbar_frame, text="VISIÓN NOCTURNA:",
            font=("Segoe UI", 11, "bold"), bootstyle="danger",
            padding=(5, 0)
        )
        self.vision_timer_value = ttkb.Label(
            self.topbar_frame, textvariable=self.vision_timer_var,
            font=("Consolas", 15, "bold"), bootstyle="danger",
            padding=(2, 0)
        )
        self._vision_timer_job = None
        self._vision_start_time = None
        self._vision_running = False

        # Map event keys to display text (for segment name)
        self._event_labels = {
            'ingreso_alumnos': 'Ingreso alumnos a la cámara',
            'inicio_dnit': 'Inicio tiempo DNIT',
            'inicio_chequeo_oidos': 'Inicio perfil chequeo de oidos y SPN',
            'fin_chequeo_oidos': 'Finalización de perfil chequeo de oidos y SPN',
            'terminacion_dnit': 'Terminación tiempo DNIT',
            'inicio_ascenso': 'Inicio ascenso',
            'inicio_hipoxia': 'Inicio Ejercicio de hipoxia',
            'fin_hipoxia': 'Finalización ejercicio de hipoxia',
            'inicio_vision_nocturna': 'Inicio ejercicio de visión nocturna',
            'fin_vision_nocturna': 'Terminación ejercicio de visión nocturna',
            'finalizacion_perfil': 'Finalización de perfil',
            'inicio_ascenso_rd1': 'Inicio ascenso RD1',
            'rd1_inicio_descenso': 'RD1 e inicio descenso',
            'inicio_ascenso_rd2': 'Inicio ascenso RD2',
            'rd2_inicio_descenso': 'RD2 e inicio descenso',
            'finalizacion_entrenamiento': 'Finalización de entrenamiento de hipoxia hipobárica',
        }
        self._setup_clock()

        # Setup GUI
        self.setup_ui()
        set_window_icon(self.root)
        self.data_manager.load_data()

    def _setup_clock(self):
        def update_clock():
            now = datetime.datetime.now().strftime('%H:%M:%S')
            self.clock_var.set(now)
            self.root.after(1000, update_clock)
        update_clock()

    # --- Chronometer logic ---
    def start_chronometer(self):
        self._chrono_start_time = datetime.datetime.now()
        self._chrono_running = True
        self._update_chronometer()
    def reset_chronometer(self):
        self._chrono_start_time = datetime.datetime.now()
        self.chrono_var.set("00:00:00")
    def stop_chronometer(self):
        self._chrono_running = False
        if self._chrono_job:
            self.root.after_cancel(self._chrono_job)
            self._chrono_job = None
    def _update_chronometer(self):
        if not self._chrono_running or not self._chrono_start_time:
            return
        elapsed = datetime.datetime.now() - self._chrono_start_time
        h, rem = divmod(int(elapsed.total_seconds()), 3600)
        m, s = divmod(rem, 60)
        self.chrono_var.set(f"{h:02}:{m:02}:{s:02}")
        self._chrono_job = self.root.after(1000, self._update_chronometer)

    # --- Total timer logic ---
    def start_total_timer(self):
        self._total_timer_start = datetime.datetime.now()
        self._total_timer_end = None
        self._total_timer_running = True
        self._update_total_timer()
    def stop_total_timer(self):
        self._total_timer_end = datetime.datetime.now()
        self._total_timer_running = False
        if self._total_timer_job:
            self.root.after_cancel(self._total_timer_job)
            self._total_timer_job = None
    def _update_total_timer(self):
        if not self._total_timer_running or not self._total_timer_start:
            return
        end_time = datetime.datetime.now() if not self._total_timer_end else self._total_timer_end
        elapsed = end_time - self._total_timer_start
        h, rem = divmod(int(elapsed.total_seconds()), 3600)
        m, s = divmod(rem, 60)
        self.total_timer_var.set(f"{h:02}:{m:02}:{s:02}")
        if self._total_timer_running:
            self._total_timer_job = self.root.after(1000, self._update_total_timer)

    # --- DNIT Segment Timer logic ---
    def start_dnit_timer(self):
        self._dnit_start_time = datetime.datetime.now()
        self._dnit_running = True
        self._update_dnit_timer()
        # Show DNIT timer widgets
        self.dnit_timer_label.pack(side=tk.LEFT, padx=(10, 2))
        self.dnit_timer_value.pack(side=tk.LEFT, padx=(0, 10))

    def stop_dnit_timer(self):
        self._dnit_running = False
        if self._dnit_timer_job:
            self.root.after_cancel(self._dnit_timer_job)
            self._dnit_timer_job = None
        self.dnit_timer_var.set("00:00")
        # Hide DNIT timer widgets
        self.dnit_timer_label.pack_forget()
        self.dnit_timer_value.pack_forget()

    def _update_dnit_timer(self):
        if not self._dnit_running or not self._dnit_start_time:
            return
        elapsed = datetime.datetime.now() - self._dnit_start_time
        m, s = divmod(int(elapsed.total_seconds()), 60)
        self.dnit_timer_var.set(f"{m:02}:{s:02}")
        self._dnit_timer_job = self.root.after(1000, self._update_dnit_timer)

    # --- Hipoxia Segment Timer logic ---
    def start_hipoxia_timer(self):
        self._hipoxia_start_time = datetime.datetime.now()
        self._hipoxia_running = True
        self._update_hipoxia_timer()
        self.hipoxia_timer_label.pack(side=tk.LEFT, padx=(10, 2))
        self.hipoxia_timer_value.pack(side=tk.LEFT, padx=(0, 10))

    def stop_hipoxia_timer(self):
        self._hipoxia_running = False
        if self._hipoxia_timer_job:
            self.root.after_cancel(self._hipoxia_timer_job)
            self._hipoxia_timer_job = None
        self.hipoxia_timer_var.set("00:00")
        self.hipoxia_timer_label.pack_forget()
        self.hipoxia_timer_value.pack_forget()

    def _update_hipoxia_timer(self):
        if not self._hipoxia_running or not self._hipoxia_start_time:
            return
        elapsed = datetime.datetime.now() - self._hipoxia_start_time
        m, s = divmod(int(elapsed.total_seconds()), 60)
        self.hipoxia_timer_var.set(f"{m:02}:{s:02}")
        self._hipoxia_timer_job = self.root.after(1000, self._update_hipoxia_timer)

    # --- Vision Nocturna Segment Timer logic ---
    def start_vision_timer(self):
        self._vision_start_time = datetime.datetime.now()
        self._vision_running = True
        self._update_vision_timer()
        self.vision_timer_label.pack(side=tk.LEFT, padx=(10, 2))
        self.vision_timer_value.pack(side=tk.LEFT, padx=(0, 10))

    def stop_vision_timer(self):
        self._vision_running = False
        if self._vision_timer_job:
            self.root.after_cancel(self._vision_timer_job)
            self._vision_timer_job = None
        self.vision_timer_var.set("00:00")
        self.vision_timer_label.pack_forget()
        self.vision_timer_value.pack_forget()

    def _update_vision_timer(self):
        if not self._vision_running or not self._vision_start_time:
            return
        elapsed = datetime.datetime.now() - self._vision_start_time
        m, s = divmod(int(elapsed.total_seconds()), 60)
        self.vision_timer_var.set(f"{m:02}:{s:02}")
        self._vision_timer_job = self.root.after(1000, self._update_vision_timer)

    # --- Event notification from TiemposTab ---
    def notify_event(self, event_key):
        label = self._event_labels.get(event_key, event_key)
        self.current_segment_var.set(label)
        if event_key == 'ingreso_alumnos':
            self.start_chronometer()
            self.start_total_timer()
        elif event_key == 'finalizacion_entrenamiento':
            self.stop_chronometer()
            self.stop_total_timer()
        elif event_key == 'inicio_dnit':
            self.reset_chronometer()
            self.start_chronometer()
            self.start_dnit_timer()
        elif event_key == 'terminacion_dnit':
            self.reset_chronometer()
            self.start_chronometer()
            self.stop_dnit_timer()
        elif event_key == 'inicio_hipoxia':
            self.reset_chronometer()
            self.start_chronometer()
            self.start_hipoxia_timer()
        elif event_key == 'fin_hipoxia':
            self.reset_chronometer()
            self.start_chronometer()
            self.stop_hipoxia_timer()
        elif event_key == 'inicio_vision_nocturna':
            self.reset_chronometer()
            self.start_chronometer()
            self.start_vision_timer()
        elif event_key == 'fin_vision_nocturna':
            self.reset_chronometer()
            self.start_chronometer()
            self.stop_vision_timer()
        else:
            self.reset_chronometer()
            self.start_chronometer()
        # Always update segment name
        self.current_segment_var.set(label)

    def setup_ui(self):
        """Create the main UI elements"""
        # NOTE: The topbar_frame is already packed in __init__
        self.notebook = ttkb.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
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
        
        # Tab 8: About (Acerca de)
        if 'AboutTab' in tab_modules:
            self.tab8 = tab_modules['AboutTab'](self.notebook, self.data_manager, self)
            self.notebook.add(self.tab8, text="Acerca de")
            logger.info("Added AboutTab")
        else:
            self.tab8 = self.create_fallback_tab("Acerca de", "Este módulo no está disponible")
            self.notebook.add(self.tab8, text="Acerca de")
            logger.warning("Using fallback for AboutTab")
            
        # Set up tab change event to refresh data when switching tabs
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """Refresh the newly selected tab with latest data, respecting prevent_load_overwrite."""
        try:
            selected_tab_widget = self.notebook.nametowidget(self.notebook.select())
            current_tab_idx = self.notebook.index(selected_tab_widget)

            # Check if the selected tab has the prevent_load_overwrite flag and if it's True
            prevent_load = False
            if hasattr(selected_tab_widget, 'prevent_load_overwrite') and selected_tab_widget.prevent_load_overwrite:
                prevent_load = True
                logger.info(f"Tab {current_tab_idx} selected, but load_data skipped due to prevent_load_overwrite flag.")

            # Reload data for the current tab only if not prevented
            if not prevent_load and hasattr(selected_tab_widget, 'load_data'):
                selected_tab_widget.load_data()
                logger.info(f"Refreshed tab {current_tab_idx} on selection")
                # Explicitly update the tab's UI after its data is loaded
                if isinstance(selected_tab_widget, tk.Frame): # Check if it's a widget
                    selected_tab_widget.update_idletasks()
                    logger.info(f"Called update_idletasks for Tab: {current_tab_idx}")
            elif prevent_load:
                # Log that loading was skipped but the tab was selected
                 logger.info(f"Selected tab {current_tab_idx}, load_data skipped.")
            else:
                # Tab might not have load_data (like AboutTab)
                 logger.info(f"Selected tab {current_tab_idx} has no load_data method or flag prevents load.")

        except Exception as e:
            logger.error(f"Error in on_tab_changed: {e}")
            # Attempt to get tab index via selected widget name if direct method fails
            try:
                 selected_name = str(self.notebook.select())
                 current_tab_idx = self.notebook.index(selected_name)
                 logger.error(f"Error refreshing tab index {current_tab_idx} on change: {e}")
            except Exception:
                 logger.error(f"Could not determine selected tab index during error handling.")

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
        print("Attempting to refresh all tabs...")

        # Check if we are in a 'new record' state (indicated by tab1's flag)
        is_new_record = False
        if hasattr(self, 'tab1') and hasattr(self.tab1, 'prevent_load_overwrite') and self.tab1.prevent_load_overwrite:
            is_new_record = True
            print("Detected 'new record' state (tab1.prevent_load_overwrite is True), will skip load_data during this refresh for tabs respecting the flag.")

        # Get the current session ID
        session_id = self.data_manager.get_current_session_id()
        print(f"Current session ID for refresh: {session_id}")

        tabs_to_refresh = [
            ('tab1', 'Vuelo'), ('tab2', 'Alumnos'), ('tab3', 'Tiempos'),
            ('tab4', 'RD'), ('tab5', 'Reactores'), ('tab6', 'Sintomas'),
            ('tab7', 'Exportar'), ('tab8', 'About')
        ]

        for tab_attr, tab_name in tabs_to_refresh:
            if hasattr(self, tab_attr):
                tab_instance = getattr(self, tab_attr)
                if hasattr(tab_instance, 'load_data'):
                    # If not in a 'new record' state (e.g., after loading an archive),
                    # ensure prevent_load_overwrite is False so tabs display the new session data.
                    if not is_new_record and hasattr(tab_instance, 'prevent_load_overwrite'):
                        if tab_instance.prevent_load_overwrite: # Log if it was unexpectedly True
                            print(f"INFO: Forcing prevent_load_overwrite=False for {tab_name} during refresh_all_tabs as not in new_record state.")
                        tab_instance.prevent_load_overwrite = False
                    
                    # Now, check the flag again before calling load_data
                    # In a 'new_record' state, load_data is skipped if the flag is True (which it should be)
                    # In other states (like after loading an archive), the flag should now be False.
                    if hasattr(tab_instance, 'prevent_load_overwrite') and tab_instance.prevent_load_overwrite:
                        print(f"Skipping load_data for Tab {tab_name} because prevent_load_overwrite is True.")
                    else:
                        try:
                            print(f"Calling load_data for Tab: {tab_name} (prevent_load_overwrite is {getattr(tab_instance, 'prevent_load_overwrite', 'N/A')})")
                            tab_instance.load_data()
                            print(f"Refreshed Tab: {tab_name}")
                            # Explicitly update the tab's UI after its data is loaded
                            if isinstance(tab_instance, tk.Frame): # Check if it's a widget
                                tab_instance.update_idletasks()
                                print(f"Called update_idletasks for Tab: {tab_name}")
                        except Exception as e:
                            logger.error(f"Error refreshing tab {tab_name}: {e}")
                else:
                    print(f"Tab {tab_name} has no load_data method.")
            else:
                print(f"Tab attribute {tab_attr} not found in MainApp.")

        print("Finished refresh_all_tabs.")
    
    def get_current_session_id(self):
        """Get the ID of the current session from data_manager."""
        return self.data_manager.get_current_session_id()

def launch_main_app():
    """Launch the main application with error handling"""
    logger.info("Launching main application...")
    
    # Generate high-resolution icon for the main application
    icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    ico_path = os.path.join(icon_dir, "icon.ico")
    png_path = os.path.join(icon_dir, "icon.png")
    
    # Regenerate the icon each time the main app launches
    if os.path.exists(png_path):
        try:
            logger.info("Regenerating high-resolution icon for main application...")
            create_high_dpi_ico(png_path, ico_path)
            logger.info("Successfully regenerated high-res icon.ico")
        except Exception as e:
            logger.warning(f"Failed to regenerate high-res icon: {e}")
    
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
            
            # Set high-resolution icon for the main window - IMPORTANT!
            set_window_icon(splash_root, force_refresh=True)
            
            # Create the main application instance with the same root
            app = MainApp(splash_root)
            logger.info("Main application UI created on existing window")
            
            # Make the window visible again
            splash_root.deiconify()
            
            # Extra attempt to set icon after window is fully visible
            splash_root.after(500, lambda: set_window_icon(splash_root))
        else:
            logger.error("Splash window not available, creating new window")
            # Create main application window if splash_root somehow not available
            main_root = ttkb.Window(themename=THEME) if THEME and ui_toolkit == "ttkbootstrap" else ttkb.Window()
            main_root.title("Registro Entrenamiento en Cámara de Altura")
            main_root.geometry("1200x800")
            main_root.minsize(1000, 700)
            
            # Set high-resolution icon for new window - IMPORTANT!
            set_window_icon(main_root, force_refresh=True)
            
            # Create the main application instance
            app = MainApp(main_root)
            logger.info("Main application UI created on new window")
            
            # Extra attempt to set icon after window is shown
            main_root.after(500, lambda: set_window_icon(main_root))
            
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
        
        # Generate high-resolution icon at startup
        icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        ico_path = os.path.join(icon_dir, "icon.ico")
        png_path = os.path.join(icon_dir, "icon.png")
        
        # Ensure high-resolution icon is generated BEFORE creating any windows
        if os.path.exists(png_path):
            logger.info("Pre-generating high-resolution icon with embedded function...")
            try:
                create_high_dpi_ico(png_path, ico_path)
                logger.info("Successfully pre-generated high-res icon.ico")
            except Exception as e:
                logger.warning(f"Failed to pre-generate high-res icon: {e}")
        
        # Create splash screen window
        logger.info("Starting application with splash screen")
        splash_root = ttkb.Window(themename=THEME) if THEME and ui_toolkit == "ttkbootstrap" else ttkb.Window()
        
        # Create splash screen
        splash = SplashScreen(splash_root, launch_main_app)
        
        # Start the Tkinter main loop
        splash_root.mainloop()
    except Exception as e:
        handle_critical_exception(e)
