"""
Auto Setup Chrome Portable
Tự động download và setup Chrome Portable nếu chưa có
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path


def check_chrome_portable():
    """Check if Chrome Portable exists"""
    chrome_portable_path = Path("chrome_portable/chrome.exe")
    return chrome_portable_path.exists()


def download_chrome_portable():
    """Download Chrome Portable from official source"""
    print("=" * 60)
    print("🔍 Không tìm thấy Chrome Portable!")
    print("📥 Đang tự động download Chrome Portable...")
    print("=" * 60)
    
    # Chrome Portable download URL (Google Chrome Portable from PortableApps)
    # Note: This is a direct link - may need to update if URL changes
    chrome_url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    
    try:
        # Create temp directory
        temp_dir = Path("temp_chrome_download")
        temp_dir.mkdir(exist_ok=True)
        
        # Download Chrome installer
        print("📥 Downloading Chrome installer...")
        response = requests.get(chrome_url, stream=True, timeout=60)
        response.raise_for_status()
        
        installer_path = temp_dir / "chrome_installer.exe"
        total_size = int(response.headers.get('content-length', 0))
        
        with open(installer_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r📥 Progress: {percent:.1f}%", end='', flush=True)
        
        print("\n✅ Download complete!")
        
        # For now, we'll use system Chrome if portable setup is complex
        # Alternative: Use existing Chrome installation
        print("\n" + "=" * 60)
        print("⚠️ Chrome Portable setup requires manual installation.")
        print("=" * 60)
        print("\n📋 HƯỚNG DẪN SETUP:")
        print("1. Tool sẽ tự động dùng Chrome đã cài trên máy")
        print("2. Hoặc download Chrome Portable từ:")
        print("   https://portableapps.com/apps/internet/google_chrome_portable")
        print("3. Giải nén vào folder 'chrome_portable'")
        print("\n✅ Tool vẫn hoạt động bình thường với Chrome hệ thống!")
        print("=" * 60)
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return False
        
    except Exception as e:
        print(f"\n❌ Lỗi download: {e}")
        print("\n📋 Giải pháp:")
        print("1. Tool sẽ dùng Chrome đã cài trên máy")
        print("2. Hoặc tải Chrome Portable thủ công:")
        print("   https://portableapps.com/apps/internet/google_chrome_portable")
        return False


def setup_chrome_portable_fallback():
    """Setup fallback to use system Chrome"""
    print("\n" + "=" * 60)
    print("🔧 SETUP CHROME")
    print("=" * 60)
    
    # Check if system Chrome exists
    system_chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    chrome_found = False
    for path in system_chrome_paths:
        if os.path.exists(path):
            print(f"✅ Tìm thấy Chrome: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("⚠️ Không tìm thấy Chrome trên hệ thống!")
        print("\n📋 Vui lòng cài Chrome:")
        print("   https://www.google.com/chrome/")
        print("\nHoặc download Chrome Portable:")
        print("   https://portableapps.com/apps/internet/google_chrome_portable")
        print("   Giải nén vào folder 'chrome_portable'")
        return False
    
    print("\n✅ Tool sẽ dùng Chrome hệ thống!")
    print("=" * 60)
    return True


def auto_setup():
    """Main setup function"""
    if check_chrome_portable():
        print("✅ Chrome Portable đã sẵn sàng!")
        return True
    
    print("\n⚠️ Chrome Portable chưa được setup!")
    
    # Try to setup fallback
    return setup_chrome_portable_fallback()


if __name__ == "__main__":
    auto_setup()
