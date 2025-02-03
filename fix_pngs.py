from PIL import Image
import os

def fix_png(filepath):
    img = Image.open(filepath)
    # Convert to RGB if needed
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        alpha = img.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, mask=alpha)
    else:
        bg = img.convert('RGB')
    # Save without iCCP chunk
    bg.save(filepath, 'PNG', icc_profile=None)

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                filepath = os.path.join(root, file)
                fix_png(filepath)

# Process all PNGs in the resources directory
process_directory('./resources')
