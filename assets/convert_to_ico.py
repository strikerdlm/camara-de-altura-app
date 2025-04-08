from PIL import Image
import os

# Define input and output file paths
input_file = r"C:\Users\User\OneDrive\FAC\Research\Python Scripts\Textapp\a_camara\assets\icon.png"
output_file = r"C:\Users\User\OneDrive\FAC\Research\Python Scripts\Textapp\a_camara\assets\icon.ico"

# Check if the input file exists
if not os.path.exists(input_file):
    print(f"Error: Input file '{input_file}' not found.")
else:
    try:
        # Open the image file
        img = Image.open(input_file)

        # Define desired icon sizes (standard ICO sizes)
        # You can customize this list if needed
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

        # Save the image as an ICO file with multiple sizes
        img.save(output_file, format='ICO', sizes=icon_sizes)

        print(f"Successfully converted '{input_file}' to '{output_file}'")

    except Exception as e:
        print(f"An error occurred during conversion: {e}") 