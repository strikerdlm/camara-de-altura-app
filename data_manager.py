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
        
        # Try to load data from default file
        self.default_file = os.path.join(data_dir, 'current_data.json')
        if os.path.exists(self.default_file):
            self.load_data(self.default_file)
    
    def get_current_session_id(self) -> str:
        """Get the current session ID in X-YY format."""
        try:
            # First try to get the session number directly
            session_id = self.current_data.get('vuelo', {}).get('numero_entrenamiento', '')
            
            # If no specific session ID, use vuelo_del_ano with year format
            if not session_id:
                vuelo_del_ano = self.current_data.get('vuelo', {}).get('vuelo_del_ano', '')
                if vuelo_del_ano:
                    # Get current year's last two digits
                    year_suffix = datetime.now().strftime("%y")
                    # Ensure vuelo_del_ano is an integer between 0-365
                    try:
                        num_vuelo = int(vuelo_del_ano)
                        if 0 <= num_vuelo <= 365:
                            session_id = f"{num_vuelo}-{year_suffix}"
                    except ValueError:
                        print(f"Warning: Invalid vuelo_del_ano value: {vuelo_del_ano}")
            
            return session_id
        except Exception as e:
            print(f"Error getting session ID: {e}")
            return ''

    def get_current_session_data(self) -> Dict[str, Any]:
        """Get data for the current session."""
        try:
            session_id = self.get_current_session_id()
            if not session_id:
                return {}
            
            # Get session data from sessions_data dictionary
            sessions_data = self.current_data.get('sessions_data', {})
            return sessions_data.get(session_id, {})
        except Exception as e:
            print(f"Error getting session data: {e}")
            return {}

    def save_session_data(self, session_data: Dict[str, Any]) -> bool:
        """Save data for the current session while preserving other sessions."""
        try:
            session_id = self.get_current_session_id()
            if not session_id:
                return False
            
            # Make sure sessions_data exists
            if 'sessions_data' not in self.current_data:
                self.current_data['sessions_data'] = {}
            
            # Update session data
            self.current_data['sessions_data'][session_id] = session_data
            
            # Save to file
            self.save_data()
            return True
        except Exception as e:
            print(f"Error saving session data: {e}")
            return False
    
    def load_data(self, file_path: Optional[str] = None) -> bool:
        """Load data from a JSON file."""
        if file_path is None:
            file_path = self.default_file
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.current_data = json.load(f)
                self.current_file = file_path
                
                # Ensure session data structure exists
                if 'sessions_data' not in self.current_data:
                    self.current_data['sessions_data'] = {}
                
                # If current session has no ID but has vuelo_del_ano, create a proper ID
                if 'vuelo' in self.current_data:
                    vuelo_data = self.current_data['vuelo']
                    if not vuelo_data.get('numero_entrenamiento') and vuelo_data.get('vuelo_del_ano'):
                        try:
                            vuelo_number = int(vuelo_data['vuelo_del_ano'])
                            if 0 <= vuelo_number <= 365:
                                # Get current year's last two digits
                                year_suffix = datetime.now().strftime("%y")
                                vuelo_data['numero_entrenamiento'] = f"{vuelo_number}-{year_suffix}"
                                print(f"Generated session ID: {vuelo_data['numero_entrenamiento']}")
                        except ValueError:
                            print(f"Warning: vuelo_del_ano is not a valid integer: {vuelo_data['vuelo_del_ano']}")
                
                print(f"Data loaded from: {file_path}")
                return True
            else:
                print(f"File does not exist: {file_path}")
                self.current_data = {'sessions_data': {}}
                self.current_file = file_path
                return False
        except Exception as e:
            print(f"Error loading data: {e}")
            self.current_data = {'sessions_data': {}}
            return False
    
    def save_data(self) -> bool:
        """Save current data to file."""
        if not self.current_file:
            self.current_file = self.default_file
        
        try:
            # Create backup before saving
            if os.path.exists(self.current_file):
                self.create_backup()
            
            # Ensure sessions_data structure exists
            if 'sessions_data' not in self.current_data:
                self.current_data['sessions_data'] = {}
            
            # Get current session ID
            session_id = self.get_current_session_id()
            
            # If we have a session ID, make sure this session exists in sessions_data
            if session_id and session_id not in self.current_data['sessions_data']:
                self.current_data['sessions_data'][session_id] = {}
                
                # Copy relevant tab data to the session data
                if 'vuelo' in self.current_data:
                    self.current_data['sessions_data'][session_id]['vuelo'] = self.current_data['vuelo'].copy()
                if 'participantes' in self.current_data:
                    self.current_data['sessions_data'][session_id]['participantes'] = self.current_data['participantes'].copy()
                if 'event_times' in self.current_data:
                    self.current_data['sessions_data'][session_id]['event_times'] = self.current_data['event_times'].copy()
                if 'student_hypoxia_end_times' in self.current_data:
                    self.current_data['sessions_data'][session_id]['student_hypoxia_end_times'] = self.current_data['student_hypoxia_end_times'].copy()
                if 'rd' in self.current_data:
                    self.current_data['sessions_data'][session_id]['rd'] = self.current_data['rd'].copy()
                if 'reactions_data' in self.current_data:
                    self.current_data['sessions_data'][session_id]['reactions_data'] = self.current_data['reactions_data'].copy()
                if 'student_symptoms' in self.current_data:
                    self.current_data['sessions_data'][session_id]['student_symptoms'] = self.current_data['student_symptoms'].copy()
            
            # Save current data
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=4)
            
            print(f"Data saved to: {self.current_file}")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
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
            
    def load_archived_data(self, training_id: str) -> Dict[str, Any]:
        """Load all archived data for a specific training ID.
        
        This allows loading data from all tabs when viewing a saved training.
        """
        try:
            # Path to the archives directory
            archives_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'archives')
            
            # Check if archives directory exists
            if not os.path.exists(archives_dir):
                print(f"Archives directory not found: {archives_dir}")
                return {}
            
            # Path to the full training data archives file
            full_data_file = os.path.join(archives_dir, 'training_full_data.json')
            
            # If full data file exists, load all tab data for this training
            if os.path.exists(full_data_file):
                with open(full_data_file, 'r', encoding='utf-8') as f:
                    all_training_data = json.load(f)
                    
                    # Check if this training ID exists in the full data
                    if training_id in all_training_data:
                        print(f"Found full archived data for training ID: {training_id}")
                        return all_training_data[training_id]
            
            # If not found or file doesn't exist, return empty dict
            return {}
            
        except Exception as e:
            print(f"Error loading archived data: {e}")
            return {}

    def load_training(self, session_id):
        """Load data for a specific training session."""
        try:
            # Check if sessions_data exists and has this session
            if 'sessions_data' not in self.current_data:
                print(f"No sessions_data found in current_data")
                return False
                
            if session_id not in self.current_data['sessions_data']:
                print(f"Session ID {session_id} not found in sessions_data")
                return False
            
            # Get the session data
            session_data = self.current_data['sessions_data'][session_id]
            
            # Copy session data to the current data structure for each tab
            if 'vuelo' in session_data:
                self.current_data['vuelo'] = session_data['vuelo'].copy()
                print(f"Loaded vuelo data for session {session_id}")
                
            if 'participantes' in session_data:
                self.current_data['participantes'] = session_data['participantes'].copy()
                print(f"Loaded participantes data for session {session_id}")
                
            if 'event_times' in session_data:
                self.current_data['event_times'] = session_data['event_times'].copy()
                print(f"Loaded event_times data for session {session_id}")
                
            if 'student_hypoxia_end_times' in session_data:
                self.current_data['student_hypoxia_end_times'] = session_data['student_hypoxia_end_times'].copy()
                print(f"Loaded student_hypoxia_end_times data for session {session_id}")
                
            if 'rd' in session_data:
                self.current_data['rd'] = session_data['rd'].copy()
                print(f"Loaded rd data for session {session_id}")
                
            if 'reactions_data' in session_data:
                self.current_data['reactions_data'] = session_data['reactions_data'].copy()
                print(f"Loaded reactions_data for session {session_id}")
                
            if 'student_symptoms' in session_data:
                self.current_data['student_symptoms'] = session_data['student_symptoms'].copy()
                print(f"Loaded student_symptoms data for session {session_id}")
                
            print(f"Successfully loaded all data for session {session_id}")
            return True
            
        except Exception as e:
            print(f"Error loading training session {session_id}: {e}")
            return False
