#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
# from ttkbootstrap.style import utility
from ttkbootstrap.scrolled import ScrolledFrame
import os
import sys
import datetime
from PIL import Image, ImageTk
import locale

# Set the locale to Spanish
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES')
    except locale.Error:
        pass  # Fallback to system default

# Import custom modules
from config import AppConfig
from tab1_vuelo import VueloTab
from tab2_alumnos import AlumnosTab
from tab3_tiempos import TiemposTab
from tab4_rd import RDTab
from tab5_reactores import ReactoresTab
from data_manager import DataManager

class WelcomeScreen:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        # Configure the window
        self.root.title("Bienvenido")
        self.root.geometry("1200x800")
        self.root.configure(bg="white")
        
        # Create fallback welcome screen (placeholder)
        self.create_fallback_welcome()
    
    def create_fallback_welcome(self):
        """Create a fallback welcome screen"""
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
        
        # Add start button
        button_frame = ttkb.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=50)
        
        start_button = ttkb.Button(
            button_frame,
            text="INICIAR SISTEMA",
            bootstyle="primary",
            width=20,
            command=self.callback
        )
        start_button.pack(pady=20)

def launch_main_app():
    print("Launching main app...")
    welcome_root.destroy()
    # In a real app, this would launch the main application

if __name__ == "__main__":
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