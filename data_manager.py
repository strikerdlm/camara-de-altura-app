#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
import shutil
from typing import Dict, Any, Optional
import pandas as pd

class DataManager:
    """Data manager for the application"""
    
    def __init__(self):
        """Initialize the data manager"""
        # Setup file paths
        self.base_path = os.path.dirname(__file__)
        self.data_path = os.path.join(self.base_path, 'data')
        self.backup_path = os.path.join(self.base_path, 'backup')
        self.export_path = os.path.join(self.base_path, 'exports') # New path for exports
        self.current_file = os.path.join(self.data_path, 'current_session.json')
        
        # Create directories if they don't exist
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        os.makedirs(self.export_path, exist_ok=True) # Create exports directory
        
        # Initialize or load current data
        self.current_data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from current session file"""
        if os.path.exists(self.current_file):
            try:
                with open(self.current_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                # If error loading, create backup of corrupted file
                self._backup_file(self.current_file, reason="corrupted")
        
        # Return empty data structure if no file exists or error loading
        return {}
    
    def save_data(self) -> None:
        """Save current data to file"""
        try:
            # Add timestamp for when data was last saved
            self.current_data['last_saved'] = datetime.datetime.now().isoformat()
            
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.current_file), exist_ok=True)
            
            # Save data
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def _backup_file(self, file_path: str, reason: str = "backup") -> None:
        """Create a backup of a file"""
        if not os.path.exists(file_path):
            return
        
        # Get base filename
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        # Create backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_{reason}_{timestamp}{ext}"
        backup_path = os.path.join(self.backup_path, backup_name)
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_path, exist_ok=True)
        
        # Copy file to backup
        try:
            shutil.copy2(file_path, backup_path)
            print(f"Created backup: {backup_path}")
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def create_backup(self) -> None:
        """Create a manual backup of current data"""
        self._backup_file(self.current_file)
    
    def save_as_new_session(self) -> None:
        """Save current data as a new session file"""
        # Create backup of current session
        self.create_backup()
        
        # Create a filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"session_{timestamp}.json"
        new_file_path = os.path.join(self.data_path, new_filename)
        
        # Save data to new file
        try:
            with open(new_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=4, ensure_ascii=False)
            print(f"Saved new session: {new_file_path}")
        except Exception as e:
            print(f"Error saving new session: {e}")
    
    def clear_data(self) -> None:
        """Clear all current data (with backup)"""
        # Create backup before clearing
        self.create_backup()
        
        # Clear data
        self.current_data = {}
        self.save_data()

    def _generate_export_filename(self, extension: str) -> str:
        """Generates a timestamped filename for exports."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_export_{timestamp}.{extension}"
        return os.path.join(self.export_path, filename)

    def save_to_csv(self, filename: Optional[str] = None) -> Optional[str]:
        """Exports the current data to a CSV file."""
        if not self.current_data:
            print("No data to export to CSV.")
            return None

        if filename is None:
            filename = self._generate_export_filename("csv")
        elif not os.path.isabs(filename):
             filename = os.path.join(self.export_path, filename)

        try:
            df = pd.json_normalize(self.current_data, sep='_')
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Data successfully exported to CSV: {filename}")
            return filename
        except ImportError:
             print("Error: pandas library is required to export to CSV.")
             return None
        except Exception as e:
            print(f"Error exporting data to CSV: {e}")
            return None

    def save_to_excel(self, filename: Optional[str] = None) -> Optional[str]:
        """Exports the current data to an Excel file (.xlsx)."""
        if not self.current_data:
            print("No data to export to Excel.")
            return None
        
        if filename is None:
            filename = self._generate_export_filename("xlsx")
        elif not os.path.isabs(filename):
             filename = os.path.join(self.export_path, filename)

        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for key, value in self.current_data.items():
                    try:
                        if isinstance(value, dict):
                             df = pd.json_normalize(value, sep='_')
                        elif isinstance(value, list):
                             df = pd.DataFrame(value)
                        else:
                             df = pd.DataFrame({key: [value]})
                        
                        sheet_name = str(key).replace('[', '').replace(']', '').replace('*', '').replace(':', '').replace('?', '').replace('/', '').replace('\\','')[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False, engine='openpyxl')
                    except Exception as sheet_error:
                        print(f"Could not convert section '{key}' to Excel sheet: {sheet_error}")
            
            print(f"Data successfully exported to Excel: {filename}")
            return filename
        except ImportError:
            print("Error: pandas and openpyxl libraries are required to export to Excel.")
            return None
        except Exception as e:
            print(f"Error exporting data to Excel: {e}")
            return None