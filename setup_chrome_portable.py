#!/usr/bin/env python3
"""
Script tự động download và setup Chrome Portable
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path

# Chrome for Testing version (stable) - Updated to match user's Chrome 144
CHROME_VERSION = "144.0.7559.109"  # Closest available to user's 144.0.7559.97
CHROME_URL = f"https://storage.googleapis.com/chrome-for-testing-public/{CHROME_VERSION}/win64/chrome-win64.zip"
CHROMEDRIVER_URL = f"https://storage.googleapis.com/chrome-for-testing-public/{CHROME_VERSION}/win64/chromedriver-win64.zip"

def download_file(url, filename):
    """Download file với progress bar"""
    print(f"📥 Downloading {filename}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"   Progress: {percent:.1f}%", end='\r')
    
    print(f"\n✅ Downloaded {filename}")

def extract_zip(zip_path, extract_to):
    """Extract zip file"""
    print(f"📦 Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✅ Extracted to {extract_to}")

def setup_chrome_portable():
    """Setup Chrome Portable"""
    print("🚀 Chrome Portable Setup")
    print("=" * 50)
    
    # Create directories
    chrome_dir = Path("chrome_portable")
    driver_dir = Path("driver")
    temp_dir = Path("temp_download")
    
    chrome_dir.mkdir(exist_ok=True)
    driver_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Download Chrome
        chrome_zip = temp_dir / "chrome.zip"
        if not chrome_zip.exists():
            download_file(CHROME_URL, chrome_zip)
        
        # Download ChromeDriver
        driver_zip = temp_dir / "chromedriver.zip"
        if not driver_zip.exists():
            download_file(CHROMEDRIVER_URL, driver_zip)
        
        # Extract Chrome
        print("\n📦 Extracting Chrome...")
        extract_zip(chrome_zip, temp_dir)
        
        # Move Chrome files
        chrome_extracted = temp_dir / "chrome-win64"
        if chrome_extracted.exists():
            print("📁 Moving Chrome files...")
            for item in chrome_extracted.iterdir():
                dest = chrome_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(chrome_dir))
            print("✅ Chrome files moved")
        
        # Extract ChromeDriver
        print("\n📦 Extracting ChromeDriver...")
        extract_zip(driver_zip, temp_dir)
        
        # Move ChromeDriver
        driver_extracted = temp_dir / "chromedriver-win64" / "chromedriver.exe"
        if driver_extracted.exists():
            print("📁 Moving ChromeDriver...")
            dest_driver = driver_dir / "chromedriver.exe"
            if dest_driver.exists():
                dest_driver.unlink()
            shutil.move(str(driver_extracted), str(dest_driver))
            print("✅ ChromeDriver moved")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        shutil.rmtree(temp_dir)
        print("✅ Cleanup complete")
        
        # Verify
        print("\n✅ SETUP COMPLETE!")
        print("=" * 50)
        print(f"📁 Chrome Portable: {chrome_dir.absolute()}")
        print(f"📁 ChromeDriver: {driver_dir.absolute()}")
        
        chrome_exe = chrome_dir / "chrome.exe"
        driver_exe = driver_dir / "chromedriver.exe"
        
        if chrome_exe.exists():
            print(f"✅ Chrome: {chrome_exe}")
        else:
            print(f"❌ Chrome not found: {chrome_exe}")
        
        if driver_exe.exists():
            print(f"✅ ChromeDriver: {driver_exe}")
        else:
            print(f"❌ ChromeDriver not found: {driver_exe}")
        
        print("\n🎯 Next steps:")
        print("1. Update WprTool.spec to include chrome_portable")
        print("2. Rebuild: pyinstaller --clean WprTool.spec")
        print("3. Test the tool")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🌐 Chrome Portable Setup Tool")
    print("=" * 50)
    print(f"Chrome Version: {CHROME_VERSION}")
    print(f"Platform: Windows 64-bit")
    print("=" * 50)
    
    response = input("\n⚠️  This will download ~200MB. Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return
    
    success = setup_chrome_portable()
    
    if success:
        print("\n🎉 Setup successful!")
    else:
        print("\n❌ Setup failed!")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()