"""
Convert PNG icon to ICO format for Windows app
"""
from PIL import Image
import os

# Input and output paths
png_path = r"C:/Users/Admin/.gemini/antigravity/brain/b67e59a4-489a-41c3-86d9-ae2fecce209b/app_icon_wprtool_1770252755098.png"
ico_path = r"app_icon.ico"

print("Converting PNG to ICO...")

try:
    # Open the PNG image
    img = Image.open(png_path)
    
    # Convert to RGB if necessary (ICO doesn't support RGBA well)
    if img.mode == 'RGBA':
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        img = background
    
    # Resize to multiple sizes for better quality at different resolutions
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    
    # Save as ICO with multiple sizes
    img.save(ico_path, format='ICO', sizes=sizes)
    
    print(f"✅ Icon created successfully: {os.path.abspath(ico_path)}")
    print(f"📊 Sizes included: {sizes}")
    
    # Also save a copy to resources folder
    if not os.path.exists('resources'):
        os.makedirs('resources')
    
    img.save('resources/app_icon.ico', format='ICO', sizes=sizes)
    print(f"✅ Backup saved to: resources/app_icon.ico")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
