#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import traceback
import platform
from typing import Optional, Callable, Any, Dict, List, Tuple
from functools import wraps
import tkinter as tk
from tkinter import messagebox

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, "app_errors.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("camara_app")

# Error categories
class AppErrorCategory:
    CRITICAL = "CRITICAL"  # Application cannot continue
    RECOVERABLE = "RECOVERABLE"  # Can continue with reduced functionality
    UI = "UI"  # UI-related errors
    DATA = "DATA"  # Data-related errors
    ENVIRONMENT = "ENVIRONMENT"  # Environment-related issues
    DEPENDENCY = "DEPENDENCY"  # Missing or failed dependencies

# Custom exceptions
class AppError(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, category: str = AppErrorCategory.CRITICAL, 
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.category = category
        self.details = details or {}
        super().__init__(message)

class DependencyError(AppError):
    """Error when a required dependency is missing or fails"""
    def __init__(self, message: str, dependency_name: str, 
                 is_critical: bool = True, alternatives: List[str] = None):
        category = AppErrorCategory.CRITICAL if is_critical else AppErrorCategory.RECOVERABLE
        details = {
            "dependency_name": dependency_name,
            "alternatives": alternatives or []
        }
        super().__init__(message, category=category, details=details)

class DataError(AppError):
    """Error when handling application data"""
    def __init__(self, message: str, is_critical: bool = False, 
                 file_path: Optional[str] = None, operation: Optional[str] = None):
        category = AppErrorCategory.CRITICAL if is_critical else AppErrorCategory.DATA
        details = {
            "file_path": file_path,
            "operation": operation
        }
        super().__init__(message, category=category, details=details)

class EnvironmentError(AppError):
    """Error related to the operating environment"""
    def __init__(self, message: str, is_critical: bool = True,
                 platform_info: Optional[Dict[str, Any]] = None):
        category = AppErrorCategory.CRITICAL if is_critical else AppErrorCategory.ENVIRONMENT
        platform_info = platform_info or {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version()
        }
        super().__init__(message, category=category, details=platform_info)

# Fallback mechanisms
class DependencyFallback:
    """Manages fallbacks for dependencies"""
    
    @staticmethod
    def get_visualization_module():
        """Get the best available visualization module"""
        try:
            import matplotlib
            return "matplotlib"
        except ImportError:
            try:
                import plotly
                return "plotly"
            except ImportError:
                logger.warning("No advanced visualization libraries available, falling back to tkinter")
                return "tkinter"
    
    @staticmethod
    def get_excel_module():
        """Get the best available Excel handling module"""
        try:
            import openpyxl
            return "openpyxl"
        except ImportError:
            try:
                import xlsxwriter
                return "xlsxwriter"
            except ImportError:
                try:
                    import xlwt
                    return "xlwt"
                except ImportError:
                    logger.warning("No Excel libraries available, falling back to CSV")
                    return "csv"
    
    @staticmethod
    def get_ui_toolkit():
        """Get the best available UI toolkit"""
        try:
            import ttkbootstrap
            return "ttkbootstrap"
        except ImportError:
            logger.warning("ttkbootstrap not available, falling back to standard ttk")
            try:
                from tkinter import ttk
                return "ttk"
            except ImportError:
                logger.warning("ttk not available, falling back to basic tkinter")
                return "tkinter"

# Error handling utilities
def try_except_decorator(fallback_value: Any = None, 
                         log_error: bool = True,
                         show_user: bool = False,
                         retry_count: int = 0):
    """Decorator to handle exceptions with fallbacks
    
    Args:
        fallback_value: Value to return if function fails
        log_error: Whether to log the error
        show_user: Whether to show error message to user
        retry_count: Number of times to retry before giving up
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= retry_count:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retries < retry_count:
                        retries += 1
                        logger.warning(f"Retrying {func.__name__} ({retries}/{retry_count})...")
                        continue
                    
                    if log_error:
                        logger.error(f"Error in {func.__name__}: {str(e)}")
                        logger.debug(traceback.format_exc())
                    
                    if show_user and hasattr(tk, '_default_root') and tk._default_root:
                        messagebox.showerror(
                            "Error",
                            f"Error in {func.__name__}: {str(e)}"
                        )
                    
                    return fallback_value
        return wrapper
    return decorator

def handle_critical_exception(e: Exception, exit_code: int = 1) -> None:
    """Handle a critical exception that requires exiting the application
    
    Args:
        e: The exception to handle
        exit_code: Exit code to use when terminating
    """
    error_type = type(e).__name__
    error_msg = str(e)
    
    logger.critical(f"CRITICAL ERROR ({error_type}): {error_msg}")
    logger.critical(traceback.format_exc())
    
    # Create error report
    try:
        report_path = os.path.join(LOG_DIR, f"error_report_{os.getpid()}.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"CRITICAL ERROR REPORT\n")
            f.write(f"='=' * 50 + '\n")
            f.write(f"Error Type: {error_type}\n")
            f.write(f"Error Message: {error_msg}\n")
            f.write(f"Platform: {platform.platform()}\n")
            f.write(f"Python Version: {platform.python_version()}\n")
            f.write(f"='=' * 50 + '\n\n")
            f.write(traceback.format_exc())
        
        logger.info(f"Error report saved to {report_path}")
    except Exception as report_error:
        logger.error(f"Failed to save error report: {report_error}")
    
    # Show error dialog if GUI is available
    if hasattr(tk, '_default_root') and tk._default_root:
        try:
            messagebox.showerror(
                "Critical Error",
                f"A critical error has occurred:\n\n{error_msg}\n\n"
                f"Error report saved to logs directory.\n"
                f"The application will now exit."
            )
        except:
            pass
    
    # Exit application
    sys.exit(exit_code)

# Global exception handler
def setup_global_exception_handler():
    """Set up global exception handler to catch unhandled exceptions"""
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't capture keyboard interrupt (Ctrl+C)
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Show error dialog if GUI is available
        if hasattr(tk, '_default_root') and tk._default_root:
            try:
                messagebox.showerror(
                    "Unhandled Error",
                    f"An unexpected error occurred:\n\n{exc_value}\n\n"
                    f"Please check the log file for details."
                )
            except:
                pass
    
    sys.excepthook = global_exception_handler

# Platform-specific fallbacks
def get_platform_specific_module(windows_module: str, linux_module: str, mac_module: str = None,
                                fallback_module: str = None) -> str:
    """Get platform-specific module name with fallbacks
    
    Args:
        windows_module: Preferred module for Windows
        linux_module: Preferred module for Linux
        mac_module: Preferred module for macOS (defaults to linux_module)
        fallback_module: Ultimate fallback if preferred not available
        
    Returns:
        Name of the module to use
    """
    if mac_module is None:
        mac_module = linux_module
        
    system = platform.system().lower()
    
    if system == 'windows':
        preferred_module = windows_module
    elif system == 'darwin':
        preferred_module = mac_module
    else:  # Linux or other
        preferred_module = linux_module
    
    try:
        __import__(preferred_module)
        return preferred_module
    except ImportError:
        if fallback_module:
            try:
                __import__(fallback_module)
                logger.warning(f"Using fallback module {fallback_module} instead of {preferred_module}")
                return fallback_module
            except ImportError:
                logger.error(f"Neither {preferred_module} nor {fallback_module} are available")
                raise DependencyError(
                    f"Required modules {preferred_module} and {fallback_module} not available",
                    dependency_name=f"{preferred_module}/{fallback_module}",
                    is_critical=True
                )
        else:
            logger.error(f"Module {preferred_module} not available and no fallback provided")
            raise DependencyError(
                f"Required module {preferred_module} not available",
                dependency_name=preferred_module,
                is_critical=True
            )

# Application startup checks
def check_environment():
    """Check if the operating environment supports the application"""
    # Check Python version
    if sys.version_info < (3, 8):
        raise EnvironmentError(
            "Python 3.8 or higher is required",
            is_critical=True
        )
    
    # Check for tkinter
    try:
        import tkinter as tk
    except ImportError:
        raise DependencyError(
            "Tkinter is required but not available",
            dependency_name="tkinter",
            is_critical=True
        )
    
    # Log platform info
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python version: {platform.python_version()}")
    
    return True

# Initialize error handling
def initialize_error_handling():
    """Initialize all error handling mechanisms"""
    setup_global_exception_handler()
    logger.info("Error handling system initialized")
    
    # Check environment
    try:
        check_environment()
    except AppError as e:
        handle_critical_exception(e)
        
    return True 