from PIL import Image
import os
import sys

# Define input and output file paths - automatically detect path from script location
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "icon.png")
output_file = os.path.join(script_dir, "icon.ico")

print(f"Converting: {input_file}")
print(f"Output to: {output_file}")

# Check if the input file exists
if not os.path.exists(input_file):
    print(f"Error: Input file '{input_file}' not found.")
    sys.exit(1)

try:
    # Open the image file
    img = Image.open(input_file)
    
    # Get the original size to check quality
    original_width, original_height = img.size
    print(f"Original image size: {original_width}x{original_height}")
    
    # Warn if the source image is too small
    if original_width < 512 or original_height < 512:
        print("Warning: For best results, use a source image of at least 512x512 pixels")
        
    # Ensure source image has proper mode for icon
    if img.mode != 'RGBA':
        print(f"Converting image from {img.mode} to RGBA for transparency support")
        img = img.convert('RGBA')

    # Define desired icon sizes - Windows prioritizes certain sizes
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), 
                (128, 128), (256, 256), (512, 512)]
    
    # Create a list to store all the images
    images = []
    
    # Create high quality resized versions for each size
    for size in icon_sizes:
        # Skip sizes larger than the original
        if size[0] > original_width or size[1] > original_height:
            print(f"Skipping size {size} as it's larger than the original image")
            continue
            
        # Use LANCZOS for best quality downsampling
        resized_img = img.resize(size, Image.LANCZOS)
        images.append(resized_img)
    
    # Save using the special multi-size ICO saving method
    # Note: We don't pass the sizes parameter here as we're providing the actual images
    if images:
        # For Windows, the order matters - include largest sizes first
        images.reverse()
        images[0].save(
            output_file, 
            format='ICO', 
            sizes=[(i.width, i.height) for i in images],
            append_images=images[1:] if len(images) > 1 else []
        )
        print(f"Successfully converted to high definition ICO with {len(images)} sizes")
        
        # List all the included sizes
        print("Included sizes:", ", ".join([f"{i.width}x{i.height}" for i in images]))
    else:
        print("No valid sizes to include in the ICO file.")

except Exception as e:
    print(f"An error occurred during conversion: {e}")
    import traceback
    traceback.print_exc() 