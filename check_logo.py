from PIL import Image
import os

try:
    img = Image.open("metro_logo.png")
    print(f"Format: {img.format}")
    print(f"Mode: {img.mode}")
    print(f"Size: {img.size}")
    
    if img.mode == 'RGBA':
        # Check if there are actually transparent pixels
        extrema = img.getextrema()
        alpha_extrema = extrema[3]
        print(f"Alpha extrema: {alpha_extrema}")
        if alpha_extrema[0] < 255:
            print("Image has transparency.")
        else:
            print("Image has alpha channel but is fully opaque.")
    else:
        print("Image is not RGBA.")

except Exception as e:
    print(f"Error: {e}")
