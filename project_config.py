#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Project Configuration Module
Ensures the application runs from the correct directory
"""

import os
from pathlib import Path


def ensure_correct_working_directory():
    """
    Ensures the application is running from the correct working directory.
    This should be called at the start of main.py or any entry point.
    """
    # Get the directory where this config file is located
    current_file = Path(__file__).resolve()
    project_root = current_file.parent
    
    # Expected project directory name
    expected_dir = "a_camara"
    
    # Check if we're in the correct directory
    if project_root.name != expected_dir:
        print(f"Warning: Expected to be in '{expected_dir}' directory")
        print(f"Current directory: {project_root}")
        
        # Try to find the correct directory
        if (project_root / expected_dir).exists():
            correct_dir = project_root / expected_dir
            os.chdir(correct_dir)
            print(f"Changed to correct directory: {correct_dir}")
        else:
            print("Could not find the correct project directory!")
            return False
    
    # Ensure we're actually in the right place by checking for key files
    required_files = ['main.py', 'tab6_sintomas.py', 'data_manager.py']
    missing_files = []
    
    for file in required_files:
        if not (project_root / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"Warning: Missing required files: {missing_files}")
        print(f"Current directory: {os.getcwd()}")
        return False
        
    print(f"✓ Running from correct directory: {os.getcwd()}")
    return True


def get_project_root():
    """
    Returns the project root directory as a Path object.
    """
    return Path(__file__).resolve().parent


def get_data_directory():
    """
    Returns the data directory path.
    """
    return get_project_root() / "data"


def get_logs_directory():
    """
    Returns the logs directory path.
    """
    return get_project_root() / "logs"


def get_exports_directory():
    """
    Returns the exports directory path.
    """
    return get_project_root() / "exports"


def get_virtual_env_path():
    """
    Returns the virtual environment path if it exists.
    """
    venv_path = get_project_root() / "registry"
    return venv_path if venv_path.exists() else None


# Project information
PROJECT_INFO = {
    "name": "Cámara de Altitud - Observador de Registro",
    "version": "1.0.0",
    "description": "Altitude Chamber Training Data Collection Application",
    "correct_directory": (
        r"C:\Users\User\OneDrive\FAC\Research\Altitude Chamber"
        r"\Obervador de Registro\a_camara"
    ),
    "python_files": [
        "main.py", "data_manager.py", "tab1_vuelo.py", 
        "tab2_alumnos.py", "tab3_tiempos.py", "tab4_rd.py", 
        "tab5_reactores.py", "tab6_sintomas.py",
        "tab7_exportar.py", "tab8_about.py"
    ]
}


if __name__ == "__main__":
    """Test the configuration when run directly."""
    print("=" * 60)
    print("PROJECT CONFIGURATION TEST")
    print("=" * 60)
    
    print(f"Project: {PROJECT_INFO['name']}")
    print(f"Version: {PROJECT_INFO['version']}")
    print()
    
    if ensure_correct_working_directory():
        print("✓ Directory configuration is correct")
        print(f"✓ Project root: {get_project_root()}")
        print(f"✓ Data directory: {get_data_directory()}")
        print(f"✓ Logs directory: {get_logs_directory()}")
        print(f"✓ Exports directory: {get_exports_directory()}")
        
        venv = get_virtual_env_path()
        if venv:
            print(f"✓ Virtual environment: {venv}")
        else:
            print("! Virtual environment not found")
            
    else:
        print("✗ Directory configuration has issues")
        print("Please run the application from the correct directory:")
        print(PROJECT_INFO['correct_directory']) 