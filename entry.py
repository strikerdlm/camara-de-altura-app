#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entry point for the Cámara Hipobárica application.
This file is for compatibility with existing scripts.
It simply imports and runs the main.py module.
"""

try:
    import main
    # Main module has the __name__ == "__main__" check, so it will run automatically
except ImportError as e:
    import sys
    import os
    
    # Basic error display if main.py is missing
    print("=" * 60)
    print("ERROR: Could not import main.py module")
    print(f"Error details: {e}")
    print("=" * 60)
    print("Please make sure main.py exists in the same directory as entry.py")
    print("=" * 60)
    
    if os.name == 'nt':  # Windows
        input("Press Enter to exit...")
    
    sys.exit(1)