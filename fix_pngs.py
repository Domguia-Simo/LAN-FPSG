from PIL import Image 
import os

def fix_png_files(directory):     
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                filepath = os.path.join(root, file)
                try:
                    # Open and resave without color profile
                    with Image.open(filepath) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGBA')
                        else:
                            img = img.convert('RGB')
                        # Save without color profile
                        img.save(filepath, 'PNG', optimize=True)
                    print(f"Fixed: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    ## Fix PNGs in resources folders
    fix_png_files("resources/sprites")
    fix_png_files("resources/textures")
