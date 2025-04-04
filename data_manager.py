#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
import shutil
import pandas as pd
from typing import Dict, Any, Optional

class DataManager:
    """Data management class for the application."""
    
    def __init__(self, data_dir: str = 'data', backup_dir: str = 'backup'):
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        self.current_file: Optional[str] = None
        self.current_data: Dict[str, Any] = {}
        
        # Create necessary directories
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
    
    def _load_data(self, file_path: str) -> Dict[str, Any]:
        """Load data from a JSON file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
    
    def save_data(self) -> None:
        """Save current data to file."""
        if not self.current_file:
            return
        
        try:
            # Create backup before saving
            self.create_backup()
            
            # Save current data
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def _backup_file(self, source: str) -> str:
        """Create a backup of a file."""
        if not os.path.exists(source):
            return ""
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(source)
        backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copy2(source, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return ""
    
    def create_backup(self) -> str:
        """Create a backup of the current data file."""
        if not self.current_file or not os.path.exists(self.current_file):
            return ""
        
        return self._backup_file(self.current_file)
    
    def save_as_new_session(self, session_name: str) -> bool:
        """Save current data as a new session."""
        if not session_name:
            return False
        
        # Generate new filename
        filename = f"{session_name}.json"
        new_file = os.path.join(self.data_dir, filename)
        
        try:
            # Save current data to new file
            with open(new_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=4)
            
            # Update current file
            self.current_file = new_file
            return True
        except Exception as e:
            print(f"Error saving new session: {e}")
            return False
    
    def clear_data(self) -> None:
        """Clear current data."""
        self.current_data = {}
        self.current_file = None
    
    def save_to_csv(self, file_path: str) -> bool:
        """Export current data to CSV format."""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame([self.current_data])
            
            # Save to CSV
            df.to_csv(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def save_to_excel(self, file_path: str) -> bool:
        """Export current data to Excel format."""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame([self.current_data])
            
            # Save to Excel
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
