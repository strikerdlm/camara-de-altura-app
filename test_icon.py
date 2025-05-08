import tkinter as tk
import os
import sys
from PIL import Image, ImageTk
import subprocess

def ensure_assets_dir():
    """Ensure assets directory exists and return its path."""
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    return assets_dir

def generate_icon():
    """Generate high-resolution icon if needed."""
    print("Checking icon generation...")
    assets_dir = ensure_assets_dir()
    icon_script = os.path.join(assets_dir, "windows_icon_fix.py")
    icon_path = os.path.join(assets_dir, "icon.ico")

    # Only generate if script exists and icon doesn't
    if os.path.exists(icon_script) and not os.path.exists(icon_path):
        try:
            subprocess.run(
                [sys.executable, icon_script],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            print("Successfully generated high-resolution icon")
        except Exception as e:
            print(f"Error generating icon: {e}")

def set_window_icon(window):
    """Set window icon in a Windows-compatible way."""
    assets_dir = ensure_assets_dir()
    ico_path = os.path.join(assets_dir, "icon.ico")
    png_path = os.path.join(assets_dir, "icon.png")

    try:
        # Try .ico file first (Windows)
        if os.path.exists(ico_path):
            window.iconbitmap(ico_path)
        # Fallback to .png
        elif os.path.exists(png_path):
            icon_image = Image.open(png_path)
            icon_photo = ImageTk.PhotoImage(icon_image)
            window.iconphoto(True, icon_photo)
            # Keep a reference to prevent garbage collection
            window._icon_photo = icon_photo
    except Exception as e:
        print(f"Warning: Could not set window icon: {e}")

def main():
    """Main test function."""
    # Generate icon if needed
    generate_icon()

    # Create test window
    root = tk.Tk()
    root.title("Icon Test - High Resolution")
    root.geometry("500x300")

    # Set the icon
    set_window_icon(root)

    # Add a label
    label = tk.Label(root, text="Testing Window Icon\nCheck the window decoration and taskbar", pady=20)
    label.pack()

    root.mainloop()

if __name__ == "__main__":
    main() 