import os
import sys
from PIL import Image

def create_high_dpi_ico(input_png, output_ico):
    """
    Creates a high-resolution ICO file optimized for Windows applications
    with special attention to DPI awareness.
    """
    print(f"Creating high-DPI ICO file from: {input_png}")
    print(f"Saving to: {output_ico}")
    
    if not os.path.exists(input_png):
        print(f"Error: Input file '{input_png}' not found")
        return False
    
    try:
        # Open original image
        img = Image.open(input_png)
        
        # Print original dimensions
        original_width, original_height = img.size
        print(f"Original image dimensions: {original_width}x{original_height} pixels")
        
        # Check if image is in RGBA mode (with transparency)
        if img.mode != 'RGBA':
            print(f"Converting from {img.mode} to RGBA for transparency support")
            img = img.convert('RGBA')
        
        # Create largest image first (Windows prefers the first image in the ICO)
        # Windows 10/11 uses these icon sizes: 16, 20, 24, 30, 32, 36, 40, 48, 60, 64, 72, 80, 96, 128, 256
        # Most important are 16, 32, 48, 64, 128, 256 - and for high-DPI, 96 and 256 are critical
        
        # Standard sizes needed (in order of importance for Windows)
        # Place largest sizes first as Windows often uses the first size it finds
        icon_sizes = [256, 128, 96, 64, 48, 40, 32, 24, 16]
        
        # Filter out sizes larger than our source image
        valid_sizes = [size for size in icon_sizes if size <= min(original_width, original_height)]
        
        if not valid_sizes:
            print("Error: Source image is too small for any valid icon sizes")
            return False
            
        print(f"Creating ICO with {len(valid_sizes)} sizes: {', '.join(map(str, valid_sizes))}")
        
        # Create a list of images to include in the ICO
        images = []
        for size in valid_sizes:
            # For best quality, use LANCZOS resampling
            resized = img.resize((size, size), Image.LANCZOS)
            images.append(resized)
        
        # Save as ICO - first image is most important for Windows display
        # Use append_images for rest of the sizes
        images[0].save(
            output_ico,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:] if len(images) > 1 else []
        )
        
        print(f"Successfully created high-DPI ICO file: {output_ico}")
        print(f"Included sizes: {', '.join([f'{img.width}x{img.height}' for img in images])}")
        return True
    
    except Exception as e:
        print(f"Error creating ICO file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Get directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    input_file = os.path.join(script_dir, "icon.png")
    output_file = os.path.join(script_dir, "icon.ico")
    
    # Create high-DPI ICO file
    success = create_high_dpi_ico(input_file, output_file)
    
    if success:
        print("\nNOTE: For Windows applications, you need to:")
        print("1. Ensure your .exe has a proper application manifest for DPI awareness")
        print("2. Restart your application to see the new icon")
        sys.exit(0)
    else:
        print("\nFailed to create high-DPI ICO file")
        sys.exit(1) 