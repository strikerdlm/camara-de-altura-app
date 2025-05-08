"""Windows compatibility module for cross-version support."""

import os
import sys
import subprocess
import ctypes
from ctypes import wintypes
import winreg

def is_windows():
    """Check if running on Windows."""
    return sys.platform == 'win32'

def get_windows_version():
    """Get Windows version information."""
    if not is_windows():
        return None
        
    try:
        version = sys.getwindowsversion()
        return {
            'major': version.major,
            'minor': version.minor,
            'build': version.build,
            'platform': version.platform,
            'service_pack': version.service_pack,
            'is_xp_or_older': version.major <= 5,
            'is_vista_or_newer': version.major >= 6,
            'is_win7_or_newer': (version.major, version.minor) >= (6, 1),
            'is_win8_or_newer': (version.major, version.minor) >= (6, 2),
            'is_win10_or_newer': version.major >= 10
        }
    except Exception:
        return None

def get_user_folder():
    """Get the user's home folder in a Windows-compatible way."""
    if is_windows():
        try:
            # Try USERPROFILE first (most reliable on Windows)
            return os.path.expandvars('%USERPROFILE%')
        except Exception:
            # Fallback to HOMEDRIVE + HOMEPATH
            try:
                drive = os.path.expandvars('%HOMEDRIVE%')
                path = os.path.expandvars('%HOMEPATH%')
                return os.path.join(drive, path)
            except Exception:
                # Last resort
                return os.path.expanduser('~')
    return os.path.expanduser('~')

def get_app_data_folder(app_name, roaming=False):
    """Get the appropriate AppData folder for storing application data."""
    if is_windows():
        try:
            # Determine AppData path
            if roaming:
                base = os.path.expandvars('%APPDATA%')  # Roaming
            else:
                base = os.path.expandvars('%LOCALAPPDATA%')  # Local
                
            if not base or base.startswith('%'):
                # Fallback for older Windows versions
                base = os.path.join(get_user_folder(), 'AppData', 'Roaming' if roaming else 'Local')
            
            # Create app-specific folder
            app_folder = os.path.join(base, app_name)
            os.makedirs(app_folder, exist_ok=True)
            return app_folder
            
        except Exception:
            # Fallback to user's home directory
            return os.path.join(get_user_folder(), f'.{app_name.lower()}')
    
    # Non-Windows systems
    return os.path.join(get_user_folder(), f'.{app_name.lower()}')

def run_elevated(cmd, wait=True):
    """Run a command with elevated privileges (UAC prompt)."""
    if not is_windows():
        return False
        
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()
            
        params = ' '.join(f'"{x}"' for x in cmd[1:])
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            'runas',
            cmd[0],
            params,
            None,
            1  # SW_SHOWNORMAL
        )
        
        # Return values > 32 indicate success
        return ret > 32
    except Exception:
        return False

def set_dpi_awareness():
    """Enable DPI awareness for better display scaling."""
    if not is_windows():
        return
        
    try:
        # Try Windows 8.1+ API
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except AttributeError:
            # Try Windows Vista through 8 API
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except AttributeError:
                pass
    except Exception:
        pass

def open_file(filepath):
    """Open a file with the default application in a Windows-compatible way."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    try:
        if is_windows():
            # Use shell execute for better compatibility
            subprocess.run(['cmd', '/c', 'start', '', filepath], shell=True)
        else:
            # Non-Windows platforms
            if sys.platform == 'darwin':  # macOS
                subprocess.call(('open', filepath))
            else:  # Linux
                subprocess.call(('xdg-open', filepath))
    except Exception as e:
        raise OSError(f"Error opening file: {e}")

def open_folder(folderpath):
    """Open a folder in the default file explorer in a Windows-compatible way."""
    if not os.path.exists(folderpath):
        raise FileNotFoundError(f"Folder not found: {folderpath}")
        
    try:
        if is_windows():
            # Use shell execute for better compatibility
            subprocess.run(['cmd', '/c', 'start', '', folderpath], shell=True)
        else:
            # Non-Windows platforms
            if sys.platform == 'darwin':  # macOS
                subprocess.call(('open', folderpath))
            else:  # Linux
                subprocess.call(('xdg-open', folderpath))
    except Exception as e:
        raise OSError(f"Error opening folder: {e}")

def get_registry_value(key_path, value_name):
    """Get a Windows registry value safely."""
    if not is_windows():
        return None
        
    try:
        # Split into root and subkey
        root_key_str, subkey = key_path.split('\\', 1)
        
        # Map root key string to HKEY constant
        root_map = {
            'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
            'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
            'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
            'HKEY_USERS': winreg.HKEY_USERS
        }
        root_key = root_map.get(root_key_str.upper())
        if not root_key:
            return None
            
        # Open and read the registry key
        with winreg.OpenKey(root_key, subkey) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
    except Exception:
        return None

def create_shortcut(target_path, shortcut_path, description=None, icon_path=None):
    """Create a Windows shortcut (.lnk) file."""
    if not is_windows():
        return False
        
    try:
        import pythoncom
        from win32com.shell import shell, shellcon
        
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink
        )
        
        shortcut.SetPath(target_path)
        if description:
            shortcut.SetDescription(description)
        if icon_path:
            shortcut.SetIconLocation(icon_path, 0)
            
        persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(shortcut_path, 0)
        return True
    except Exception:
        return False 