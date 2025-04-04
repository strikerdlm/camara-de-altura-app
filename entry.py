#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entry Script for Camara Hiperbarica Application
-----------------------------------------------
This script automatically detects the operating system and runs the appropriate
setup or run script. It serves as a unified entry point across all platforms.

Usage:
    python entry.py           - Runs the application (setup if needed, then run)
    python entry.py setup     - Run only the setup step (create virtual environment)
    python entry.py run       - Run the application (assumes setup is already done)
"""

import os
import sys
import platform
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "entry.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("entry")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Entry script for Camara Hiperbarica Application")
    parser.add_argument("action", nargs="?", default="auto", choices=["auto", "setup", "run"], 
                        help="Action to perform: 'auto' (default), 'setup', or 'run'")
    return parser.parse_args()

def get_system_info():
    """Get information about the current system"""
    system = platform.system().lower()
    is_windows = system == "windows"
    is_macos = system == "darwin"
    is_linux = system == "linux"
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    logger.info(f"Detected system: {platform.system()} {platform.release()}")
    logger.info(f"Python version: {python_version}")
    
    return {
        "system": system,
        "is_windows": is_windows,
        "is_macos": is_macos,
        "is_linux": is_linux,
        "python_version": python_version,
        "base_dir": os.path.dirname(os.path.abspath(__file__)),
    }

def run_script(script_path, verbose=True):
    """Run a script and handle errors"""
    if not os.path.exists(script_path):
        logger.error(f"Script not found: {script_path}")
        print(f"ERROR: Script not found: {script_path}")
        return False
        
    logger.info(f"Running script: {script_path}")
    
    if verbose:
        print(f"Running: {script_path}")
    
    try:
        if sys.platform == "win32":
            # Windows: use direct call for .bat files
            if script_path.endswith(".bat"):
                process = subprocess.Popen(script_path, shell=True)
                process.wait()
                return process.returncode == 0
            else:
                # For non-bat files on Windows
                process = subprocess.Popen(["python", script_path], shell=True)
                process.wait()
                return process.returncode == 0
        else:
            # Unix-like systems (Linux/macOS)
            if script_path.endswith(".sh"):
                # Make sure the script is executable
                os.chmod(script_path, 0o755)  # rwxr-xr-x
                process = subprocess.Popen(["/bin/bash", script_path], shell=False)
                process.wait()
                return process.returncode == 0
            else:
                # For Python files on Unix
                process = subprocess.Popen(["python3", script_path], shell=False)
                process.wait()
                return process.returncode == 0
    except Exception as e:
        logger.error(f"Error running script {script_path}: {str(e)}")
        print(f"ERROR: Failed to run {script_path}: {str(e)}")
        return False

def check_environment(system_info):
    """Check if the virtual environment is already set up"""
    base_dir = system_info["base_dir"]
    
    # Check for virtual environment
    venv_path = os.path.join(base_dir, "venv")
    registry_path = os.path.join(base_dir, "registry")
    
    if os.path.exists(venv_path) and os.path.isdir(venv_path):
        return "venv"
    elif os.path.exists(registry_path) and os.path.isdir(registry_path):
        return "registry"
    else:
        return None

def check_venv_availability():
    """Check if the venv module is available"""
    system_info = get_system_info()
    
    # Only relevant for Linux/macOS
    if system_info["is_windows"]:
        return True
    
    # Check if Python has venv module
    try:
        subprocess.check_call([sys.executable, "-c", "import venv"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        # venv module not available
        return False

def run_setup(system_info):
    """Run the setup script for the current platform"""
    base_dir = system_info["base_dir"]
    
    if system_info["is_windows"]:
        # First try with the antivirus-friendly script if it exists
        bypass_script = os.path.join(base_dir, "bypass_av_venv.bat")
        if os.path.exists(bypass_script):
            # Check if we need the bypass script
            try:
                # Try to create a test venv to see if antivirus blocks it
                test_dir = os.path.join(base_dir, "test_venv")
                if os.path.exists(test_dir):
                    import shutil
                    shutil.rmtree(test_dir)
                
                logger.info("Testing if venv creation is blocked by antivirus...")
                subprocess.run(
                    [sys.executable, "-m", "venv", test_dir],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    timeout=5  # Short timeout to quickly detect if blocked
                )
                
                # If we get here, venv creation wasn't blocked
                if os.path.exists(test_dir):
                    import shutil
                    shutil.rmtree(test_dir)
                    
                logger.info("Regular venv creation works, using standard setup script")
                setup_script = os.path.join(base_dir, "setup_env.bat")
                return run_script(setup_script)
                
            except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                # If we get any error, assume it's blocked by antivirus
                logger.warning(f"venv creation seems to be blocked: {e}")
                logger.info("Using antivirus-friendly setup script")
                print("\n" + "=" * 80)
                print("NOTA: Se detectó que su antivirus puede bloquear la creación del entorno virtual.")
                print("Usando script alternativo que evita la detección del antivirus.")
                print("=" * 80 + "\n")
                return run_script(bypass_script)
        
        # Fall back to regular setup script
        setup_script = os.path.join(base_dir, "setup_env.bat")
        logger.info("Running Windows setup script")
        return run_script(setup_script)
    else:
        # First check if venv is available
        if check_venv_availability():
            setup_script = os.path.join(base_dir, "setup_env.sh")
            logger.info("Running Linux/macOS setup script with venv")
            return run_script(setup_script)
        else:
            # venv not available, suggest manual setup
            manual_setup_script = os.path.join(base_dir, "setup_manual_venv.sh")
            
            if os.path.exists(manual_setup_script):
                logger.info("venv module not available, using manual setup script")
                print("\n" + "=" * 80)
                print("NOTA: El módulo 'venv' de Python no está disponible.")
                print("Usando el script de configuración manual alternativo.")
                print("=" * 80 + "\n")
                
                # Make the script executable
                try:
                    os.chmod(manual_setup_script, 0o755)  # rwxr-xr-x
                except Exception as e:
                    logger.warning(f"Could not set executable permission on {manual_setup_script}: {e}")
                
                return run_script(manual_setup_script)
            else:
                # Manual setup script not found, use regular setup and it will handle venv not available
                setup_script = os.path.join(base_dir, "setup_env.sh")
                logger.warning("venv module not available, but continuing with regular setup script")
                print("\n" + "=" * 80)
                print("ADVERTENCIA: El módulo 'venv' de Python no está disponible.")
                print("El script intentará instalarlo o usar una alternativa.")
                print("Si encuentra problemas, ejecute 'setup_manual_venv.sh' directamente.")
                print("=" * 80 + "\n")
                return run_script(setup_script)

def run_application(system_info):
    """Run the application for the current platform"""
    base_dir = system_info["base_dir"]
    
    if system_info["is_windows"]:
        run_script_path = os.path.join(base_dir, "run.bat")
        logger.info("Running Windows application script")
        return run_script(run_script_path)
    else:
        # Linux or macOS
        run_script_path = os.path.join(base_dir, "run.sh")
        logger.info("Running Linux/macOS application script")
        return run_script(run_script_path)

def main():
    """Main entry point"""
    args = parse_arguments()
    system_info = get_system_info()
    
    print(f"Cámara Hiperbárica - Sistema detectado: {platform.system()}")
    
    # Create necessary directories
    for directory in ["logs", "data", "backup", "assets"]:
        os.makedirs(os.path.join(system_info["base_dir"], directory), exist_ok=True)
    
    if args.action == "setup":
        print("Ejecutando configuración del entorno...")
        success = run_setup(system_info)
        if not success:
            print("ERROR: La configuración no se completó correctamente.")
            sys.exit(1)
        sys.exit(0)
    
    elif args.action == "run":
        print("Ejecutando aplicación...")
        env_type = check_environment(system_info)
        if not env_type:
            print("ADVERTENCIA: El entorno virtual no está configurado.")
            print("Ejecutando primero la configuración del entorno...")
            success = run_setup(system_info)
            if not success:
                print("ERROR: La configuración no se completó correctamente.")
                sys.exit(1)
        
        success = run_application(system_info)
        if not success:
            print("ERROR: La aplicación no se ejecutó correctamente.")
            sys.exit(1)
        sys.exit(0)
        
    else:  # auto
        # Check if environment is set up
        env_type = check_environment(system_info)
        
        if not env_type:
            print("Configurando entorno por primera vez...")
            success = run_setup(system_info)
            if not success:
                print("ERROR: La configuración no se completó correctamente.")
                sys.exit(1)
        else:
            print(f"Entorno virtual detectado: {env_type}")
        
        print("Iniciando aplicación...")
        success = run_application(system_info)
        if not success:
            print("ERROR: La aplicación no se ejecutó correctamente.")
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        print(f"ERROR: Se produjo un error inesperado: {str(e)}")
        print("Consulte el archivo logs/entry.log para más detalles.")
        sys.exit(1) 