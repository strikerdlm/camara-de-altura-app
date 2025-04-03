#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

def create_logo():
    """Create a placeholder logo if one doesn't exist"""
    logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.jpg')
    
    if os.path.exists(logo_path):
        print(f"Logo already exists at {logo_path}")
        return
    
    print(f"Creating placeholder logo at {logo_path}")
    
    # Create a blank image with a blue background (500x500 pixels)
    img = Image.new('RGB', (500, 500), color=(0, 51, 102))
    d = ImageDraw.Draw(img)
    
    # Try to use a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw text
    d.text((250, 200), "FAC", font=font, fill=(255, 255, 255), anchor="mm")
    d.text((250, 250), "REGISTRO", font=font, fill=(255, 255, 255), anchor="mm")
    d.text((250, 300), "CÁMARA DE ALTURA", font=font, fill=(255, 255, 255), anchor="mm")
    
    # Draw a circle
    d.ellipse((150, 50, 350, 250), outline=(255, 255, 255), width=3)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(logo_path), exist_ok=True)
    
    # Save the image
    img.save(logo_path)

def create_icon():
    """Create a placeholder icon if one doesn't exist"""
    icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
    
    if os.path.exists(icon_path):
        print(f"Icon already exists at {icon_path}")
        return
    
    print(f"Creating placeholder icon at {icon_path}")
    
    # Create a blank square image with a blue background (256x256 pixels)
    img = Image.new('RGBA', (256, 256), color=(0, 51, 102, 255))
    d = ImageDraw.Draw(img)
    
    # Try to use a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw text
    d.text((128, 128), "FAC", font=font, fill=(255, 255, 255), anchor="mm")
    
    # Draw a circle
    d.ellipse((78, 78, 178, 178), outline=(255, 255, 255), width=3)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    
    # Save the image as PNG first (PIL needs this for ICO conversion)
    png_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
    img.save(png_path)
    
    # Convert to ICO
    icon_img = Image.open(png_path)
    icon_img.save(icon_path)

def create_welcome_screen():
    """Create a modern, minimalist welcome screen image"""
    welcome_path = os.path.join(os.path.dirname(__file__), 'assets', 'welcome.jpg')
    
    if os.path.exists(welcome_path):
        print(f"Welcome screen already exists at {welcome_path}")
        return
    
    print(f"Creating welcome screen at {welcome_path}")
    
    # Create a large blank image with a subtle gradient background (1200x800 pixels)
    img = Image.new('RGB', (1200, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Create a subtle gradient background
    for y in range(800):
        # Calculate color based on position (white to very light blue)
        blue_intensity = int(240 + (y / 800) * 15)  # 240-255
        color = (248, 250, blue_intensity)
        draw.line([(0, y), (1200, y)], fill=color)
    
    # Try to load fonts, with fallbacks
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 48)
    except IOError:
        try:
            title_font = ImageFont.truetype("Arial Bold.ttf", 48)
        except IOError:
            title_font = ImageFont.load_default()
    
    try:
        subtitle_font = ImageFont.truetype("arial.ttf", 28)
    except IOError:
        subtitle_font = ImageFont.load_default()
    
    try:
        small_font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        small_font = ImageFont.load_default()
    
    # Colors
    primary_color = (0, 51, 102)  # Dark blue
    secondary_color = (0, 102, 204)  # Medium blue
    accent_color = (240, 120, 20)  # Orange
    
    # Draw a decorative header bar
    draw.rectangle([(0, 0), (1200, 80)], fill=primary_color)
    
    # Draw main title
    draw.text((600, 200), "REGISTRO DE ENTRENAMIENTO", 
              font=title_font, fill=primary_color, anchor="mm")
    draw.text((600, 260), "CÁMARA DE ALTURA", 
              font=title_font, fill=primary_color, anchor="mm")
    
    # Draw a horizontal separator line
    draw.line([(400, 320), (800, 320)], fill=secondary_color, width=2)
    
    # Draw subtitle
    draw.text((600, 380), "Fuerza Aérea Colombiana", 
              font=subtitle_font, fill=secondary_color, anchor="mm")
    
    # Draw decorative elements - stylized aircraft silhouette
    # Simplified aircraft silhouette
    points = [
        (450, 500), (500, 480), (750, 480), (800, 500),  # Main body
        (800, 500), (750, 520), (500, 520), (450, 500),  # Close the shape
        
        (550, 480), (500, 430), (550, 430), (600, 480),  # Left wing
        (700, 480), (750, 430), (700, 430), (650, 480),  # Right wing
        
        (750, 520), (780, 570), (750, 570), (720, 520),  # Left stabilizer
        (550, 520), (520, 570), (550, 570), (580, 520),  # Right stabilizer
    ]
    
    # Draw the aircraft with a slight transparency
    for i in range(0, len(points), 4):
        if i + 3 < len(points):
            draw.polygon([points[i], points[i+1], points[i+2], points[i+3]], 
                         fill=(secondary_color[0], secondary_color[1], secondary_color[2], 128))
    
    # Draw a thin footer bar
    draw.rectangle([(0, 750), (1200, 800)], fill=primary_color)
    
    # Add version and copyright info in the footer
    draw.text((600, 775), "Sistema de Registro v1.0", 
              font=small_font, fill=(255, 255, 255), anchor="mm")
    draw.text((1150, 775), "© 2024 FAC", 
              font=small_font, fill=(255, 255, 255), anchor="rm")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(welcome_path), exist_ok=True)
    
    # Apply a slight blur for a more polished look
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Enhance contrast slightly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.05)
    
    # Save the image
    img.save(welcome_path, quality=95)

if __name__ == "__main__":
    # Create assets
    create_logo()
    create_icon()
    create_welcome_screen()
    print("Placeholder assets created successfully.") 