#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from typing import Any, Dict

class AppConfig:
    """Application configuration manager."""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config: Dict[str, Any] = {
            'app_name': 'Cámara Hipobárica',
            'version': '1.0.0',
            'theme': 'darkly',
            'data_dir': 'data',
            'backup_dir': 'backup',
            'log_dir': 'logs',
            'autosave_interval': 300,  # 5 minutes
            'debug': False
        }
        
        # Create necessary directories
        os.makedirs(self.config['data_dir'], exist_ok=True)
        os.makedirs(self.config['backup_dir'], exist_ok=True)
        os.makedirs(self.config['log_dir'], exist_ok=True)
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Use default config if loading fails
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_setting(self, key: str) -> Any:
        """Get a configuration setting."""
        return self.config.get(key)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a configuration setting."""
        self.config[key] = value
        self.save()
    
    def save(self) -> None:
        """Save current configuration."""
        self._save_config()
