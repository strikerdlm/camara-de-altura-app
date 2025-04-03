#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from typing import Dict, Any, Optional

class AppConfig:
    """Configuration manager for the application"""
    
    def __init__(self):
        """Initialize the configuration manager"""
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.config_data = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "app_name": "Registro Entrenamiento en Cámara de Altura",
            "version": "1.0.0",
            "theme": "litera",
            "data_directory": os.path.join(os.path.dirname(__file__), "data"),
            "backup_directory": os.path.join(os.path.dirname(__file__), "backup"),
            "log_directory": os.path.join(os.path.dirname(__file__), "logs"),
            "autosave_interval": 60,  # seconds
            "debug_mode": False
        }
        
        # Create directories if they don't exist
        for dir_key in ["data_directory", "backup_directory", "log_directory"]:
            os.makedirs(default_config[dir_key], exist_ok=True)
        
        # Try to load existing config
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    return {**default_config, **loaded_config}
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # If no config exists or error loading, create a new one
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config_data: Dict[str, Any]) -> None:
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        return self.config_data.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a configuration setting"""
        self.config_data[key] = value
        self._save_config(self.config_data)
    
    def save(self) -> None:
        """Save current configuration"""
        self._save_config(self.config_data) 