#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from datetime import datetime
import locale
from typing import Optional, Dict, Any, List
import pandas as pd

class RDTab(ttkb.Frame):
    """Tab for rapid decompression (RD) profile data"""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, padding=20)
        self.data_manager = data_manager
        
        # RD options defined by the rule
        self.oi_options = ["OI1", "OI2"]
        self.original_seat_options = [str(i) for i in range(1, 9)] # Seats 1-8
        self.new_seat_options = ["7", "8"] # Target seats 7 or 8
        
        # RD data structure based on rule (rd1, rd2)
        self.rd_data = {}
        self.initialize_data()
        
        # Create the layout
        self.create_widgets()
        
    def initialize_data(self):
        """Initialize or load RD data for RD1 and RD2 profiles."""
        # Default structure for one profile
        default_profile_data = {
            'oi': self.oi_options[0], # Default to OI1
            'original_seat': self.original_seat_options[0], # Default to 1
            'new_seat': self.new_seat_options[0], # Default to 7
            'novedad': ''
        }

        # Try to load RD data from data manager
        loaded_data = {}
        if hasattr(self.data_manager, 'current_data') and 'rd_data' in self.data_manager.current_data:
            loaded_data = self.data_manager.current_data.get('rd_data', {})
            # Ensure loaded data has the expected keys, otherwise use defaults
            if not isinstance(loaded_data.get('rd1'), dict):
                 loaded_data['rd1'] = default_profile_data.copy()
            if not isinstance(loaded_data.get('rd2'), dict):
                 loaded_data['rd2'] = default_profile_data.copy()
        else:
            # Create empty data structure with defaults if nothing loaded
            loaded_data = {
                'rd1': default_profile_data.copy(),
                'rd2': default_profile_data.copy()
            }
        
        self.rd_data = loaded_data

    def create_widgets(self):
        """Create the tab UI widgets for RD1 and RD2."""
        
        # Title
        title_label = ttkb.Label(
            self, 
            text="PERFIL DE DESCOMPRESIÓN RÁPIDA", 
            font=('Segoe UI', 14, 'bold'),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))

        # --- RD1 Section --- 
        rd1_frame = ttkb.LabelFrame(self, text="RD 1", padding=15, bootstyle="info")
        rd1_frame.pack(fill=tk.X, pady=10)
        self.rd1_vars = self._create_profile_widgets(rd1_frame, self.rd_data['rd1'])

        # --- RD2 Section --- 
        rd2_frame = ttkb.LabelFrame(self, text="RD 2", padding=15, bootstyle="info")
        rd2_frame.pack(fill=tk.X, pady=10)
        self.rd2_vars = self._create_profile_widgets(rd2_frame, self.rd_data['rd2'])
        
        # --- Removed old operators/observations sections --- 

        # Action buttons (consider placing them outside frames if needed)
        button_frame = ttkb.Frame(self)
        button_frame.pack(fill=tk.X, pady=20, side=tk.BOTTOM) # Place at bottom
        
        save_btn = ttkb.Button(
            button_frame, 
            text="Guardar Datos RD", 
            command=self.save_data,
            bootstyle="success", # Updated style
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttkb.Button(
            button_frame, 
            text="Limpiar Datos RD", 
            command=self.clear_form,
            bootstyle="warning", # Updated style
            width=15
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)

    def _create_profile_widgets(self, parent_frame, profile_data):
        """Helper function to create widgets for a single RD profile."""
        widgets = {}
        row = 0

        # OI (Operador Interno)
        oi_label = ttkb.Label(parent_frame, text="Operador Interno (OI):")
        oi_label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
        widgets['oi'] = tk.StringVar(value=profile_data.get('oi', self.oi_options[0]))
        oi_combo = ttkb.Combobox(
            parent_frame, 
            textvariable=widgets['oi'],
            values=self.oi_options,
            width=8,
            state="readonly"
        )
        oi_combo.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        row += 1

        # Silla (Original Seat)
        silla_label = ttkb.Label(parent_frame, text="Silla Original:")
        silla_label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
        widgets['original_seat'] = tk.StringVar(value=profile_data.get('original_seat', self.original_seat_options[0]))
        silla_combo = ttkb.Combobox(
            parent_frame, 
            textvariable=widgets['original_seat'],
            values=self.original_seat_options,
            width=8,
            state="readonly"
        )
        silla_combo.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        row += 1

        # Nueva Posición (New Seat)
        new_seat_label = ttkb.Label(parent_frame, text="Nueva Posición:")
        new_seat_label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
        widgets['new_seat'] = tk.StringVar(value=profile_data.get('new_seat', self.new_seat_options[0]))
        new_seat_combo = ttkb.Combobox(
            parent_frame, 
            textvariable=widgets['new_seat'],
            values=self.new_seat_options,
            width=8,
            state="readonly"
        )
        new_seat_combo.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        row += 1

        # Novedad (Incident Description)
        novedad_label = ttkb.Label(parent_frame, text="Novedad:")
        novedad_label.grid(row=row, column=0, padx=5, pady=5, sticky='nw') # Align north-west
        widgets['novedad'] = tk.StringVar(value=profile_data.get('novedad', ''))
        novedad_entry = ttkb.Entry(
            parent_frame, 
            textvariable=widgets['novedad'],
            width=40 # Adjust width as needed
        )
        novedad_entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew') # Expand horizontally
        
        # Configure column weights for resizing
        parent_frame.columnconfigure(1, weight=1)

        return widgets
    
    def collect_data(self) -> Dict[str, Any]:
        """Collect RD data from both profile forms."""
        data = {
            'rd1': {
                'oi': self.rd1_vars['oi'].get(),
                'original_seat': self.rd1_vars['original_seat'].get(),
                'new_seat': self.rd1_vars['new_seat'].get(),
                'novedad': self.rd1_vars['novedad'].get()
            },
            'rd2': {
                'oi': self.rd2_vars['oi'].get(),
                'original_seat': self.rd2_vars['original_seat'].get(),
                'new_seat': self.rd2_vars['new_seat'].get(),
                'novedad': self.rd2_vars['novedad'].get()
            }
        }
        return data
    
    def save_data(self):
        """Save RD data for both profiles."""
        self.rd_data = self.collect_data()
        
        if hasattr(self.data_manager, 'current_data'):
            self.data_manager.current_data['rd_data'] = self.rd_data
            # Ensure the main save_data method exists and handles saving the whole structure
            if hasattr(self.data_manager, 'save_data') and callable(self.data_manager.save_data):
                self.data_manager.save_data()
                print("RD data saved.")
            else:
                 print("Error: DataManager does not have a callable save_data method.")
        else:
            print("Error: DataManager or current_data not found.")
    
    def clear_form(self):
        """Clear all RD data fields for both profiles."""
        # Default values
        default_oi = self.oi_options[0]
        default_orig_seat = self.original_seat_options[0]
        default_new_seat = self.new_seat_options[0]

        # Clear RD1
        self.rd1_vars['oi'].set(default_oi)
        self.rd1_vars['original_seat'].set(default_orig_seat)
        self.rd1_vars['new_seat'].set(default_new_seat)
        self.rd1_vars['novedad'].set('')

        # Clear RD2
        self.rd2_vars['oi'].set(default_oi)
        self.rd2_vars['original_seat'].set(default_orig_seat)
        self.rd2_vars['new_seat'].set(default_new_seat)
        self.rd2_vars['novedad'].set('')

        # Optionally, immediately save the cleared state
        # self.save_data()
        print("RD form cleared.") 