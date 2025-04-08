#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows compatibility functions and utilities for the Cámara Hipobárica application.
These functions handle Windows-specific behaviors and issues.
"""

import os
import sys
import logging

# Setup logger
logger = logging.getLogger(__name__)

def configure_windows_environment():
    """Configure the Windows environment for better compatibility."""
    try:
        # Check if we're on Windows
        if os.name != 'nt':
            return False
            
        # Configure PIL/Pillow for Windows
        try:
            import PIL
            # Add PIL directory to PATH to ensure image codecs are found
            os.environ['PATH'] = os.path.dirname(PIL.__file__) + os.pathsep + os.environ['PATH']
            logger.info("Added PIL directory to PATH for Windows")
        except ImportError:
            logger.warning("PIL not available, skipping PATH configuration")
        
        # Configure locale for Windows
        try:
            import locale
            for locale_name in ['es_ES.utf8', 'es_ES', 'es-ES', 'Spanish_Spain']:
                try:
                    locale.setlocale(locale.LC_ALL, locale_name)
                    logger.info(f"Set locale to {locale_name}")
                    break
                except locale.Error:
                    continue
        except Exception as e:
            logger.warning(f"Error configuring locale: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error in Windows configuration: {e}")
        return False

def set_windows_icon(root, icon_path=None):
    """Set the window icon using Windows-friendly methods."""
    try:
        if os.name != 'nt':
            return False
            
        if icon_path is None:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
            
        if os.path.exists(icon_path):
            try:
                root.wm_iconbitmap(icon_path)
                logger.info(f"Set window icon using wm_iconbitmap: {icon_path}")
                return True
            except Exception as e:
                logger.warning(f"Could not set icon using wm_iconbitmap: {e}")
                
        return False
    except Exception as e:
        logger.error(f"Error setting Windows icon: {e}")
        return False