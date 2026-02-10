import sys
import os
import atexit
import subprocess

# Ensure the current directory is in python path to handle imports correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controller.main_controller import AppController

def cleanup_chrome_on_exit():
    """
    TỰ ĐỘNG ĐÓNG Chrome for Testing khi tool thoát.
    Dùng logic từ kill_chrome.bat - target theo ExecutablePath
    """
    print("\n[CLEANUP] 🧹 Đang đóng Chrome for Testing...")
    try:
        from model.utils import resource_path
        # Use resource_path to get the actual running directory (works for both script and frozen EXE)
        current_dir = resource_path("").replace("\\", "\\\\")
        
        # Bước 1: Kill Chrome Portable trong thư mục này (dùng ExecutablePath)
        ps_chrome = f'''powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object {{ $_.Name -eq 'chrome.exe' -and $_.ExecutablePath -like '*{current_dir}*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"'''
        subprocess.run(ps_chrome, shell=True, capture_output=True, timeout=10)
        
        # Bước 2: Kill ChromeDriver trong thư mục này
        ps_driver = f'''powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object {{ $_.Name -eq 'chromedriver.exe' -and $_.ExecutablePath -like '*{current_dir}*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"'''
        subprocess.run(ps_driver, shell=True, capture_output=True, timeout=10)
        
        # Bước 3: Fallback - Kill tất cả chromedriver (thường an toàn)
        subprocess.run("taskkill /F /IM chromedriver.exe /T", shell=True, capture_output=True, timeout=5)
        
        print("[CLEANUP] ✅ Đã đóng Chrome for Testing!")
    except Exception as e:
        print(f"[CLEANUP] ⚠️  Lỗi: {e}")

# Register cleanup function to run on exit
atexit.register(cleanup_chrome_on_exit)

if __name__ == "__main__":
    app = AppController()
    app.run()
