"""
Build WprTool with Custom Icon
Quick build script for the WordPress automation tool
"""

import os
import sys
import shutil
import subprocess

print("="*70)
print("  🚀 BUILDING WPRTOOL WITH CUSTOM ICON")
print("="*70)

# Step 1: Check if icon exists
print("\n[1/4] Checking icon...")
if not os.path.exists("app_icon.ico"):
    print("  ⚠️ Icon not found. Creating icon...")
    try:
        subprocess.run([sys.executable, "create_icon.py"], check=True)
        print("  ✅ Icon created successfully!")
    except Exception as e:
        print(f"  ❌ Error creating icon: {e}")
        print("  💡 Please run: python create_icon.py")
        sys.exit(1)
else:
    print("  ✅ Icon found: app_icon.ico")

# Step 2: Clean old build
print("\n[2/4] Cleaning old build...")
folders_to_clean = ['build', 'dist']
for folder in folders_to_clean:
    if os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            print(f"  🗑️ Removed: {folder}/")
        except Exception as e:
            print(f"  ⚠️ Could not remove {folder}: {e}")

# Step 3: Build with PyInstaller
print("\n[3/4] Building with PyInstaller...")
print("  ⏳ This may take a few minutes...\n")

try:
    result = subprocess.run(
        ["pyinstaller", "--clean", "WprTool.spec"],
        check=True,
        capture_output=True,
        text=True
    )
    print("  ✅ Build completed successfully!")
except subprocess.CalledProcessError as e:
    print(f"  ❌ Build failed!")
    print(f"  Error: {e.stderr}")
    sys.exit(1)

# Step 4: Verify output
print("\n[4/4] Verifying output...")
exe_path = os.path.join("dist", "WprTool", "WprTool.exe")
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"  ✅ Executable created: {exe_path}")
    print(f"  📊 Size: {size_mb:.1f} MB")
    print(f"  🎨 Icon: Embedded (app_icon.ico)")
else:
    print(f"  ❌ Executable not found at: {exe_path}")
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("  ✅ BUILD SUCCESSFUL!")
print("="*70)
print(f"\n📁 Output location: {os.path.abspath('dist/WprTool/')}")
print(f"🚀 Run the app: dist\\WprTool\\WprTool.exe")
print("\n💡 To distribute:")
print("   1. Zip the 'dist/WprTool' folder")
print("   2. Share the ZIP file")
print("   3. Users extract and run WprTool.exe")
print("\n🎨 The app now has a unique icon and won't conflict with other tools!")
