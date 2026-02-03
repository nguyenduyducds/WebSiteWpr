
import requests
import webbrowser
from packaging import version
import threading
import os
import sys
import subprocess
import time

class UpdateChecker:
    def __init__(self, current_version, update_url=None):
        self.current_version = current_version
        self.update_url = update_url if update_url else "https://example.com/version.json" 
        self.latest_version = None
        self.download_url = None

    def check_for_updates(self, callback=None):
        """
        Checks for updates asynchronously.
        callback: function(has_update, latest_version_str, download_url)
        """
        def _check():
            try:
                # Add cache buster
                import time
                check_url = self.update_url
                if "?" in check_url:
                    check_url += f"&t={int(time.time())}"
                else:
                    check_url += f"?t={int(time.time())}"
                
                print(f"[Update] Checking URL: {check_url}")
                response = requests.get(check_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    remote_ver_str = data.get("version", "0.0.0")
                    self.download_url = data.get("download_url", "")
                    
                    print(f"[Update] Local: {self.current_version}, Remote: {remote_ver_str}")
                    
                    if version.parse(remote_ver_str) > version.parse(self.current_version):
                        self.latest_version = remote_ver_str
                        if callback:
                            callback(True, remote_ver_str, self.download_url)
                    else:
                        if callback:
                            callback(False, remote_ver_str, None)
                else:
                    print(f"[Update] Check failed: Status {response.status_code}")
                    if callback: callback(False, None, None)
            except Exception as e:
                print(f"[Update] Error checking: {e}")
                if callback: callback(False, None, None)

        threading.Thread(target=_check, daemon=True).start()

    def download_and_install(self, download_url, progress_callback=None, completion_callback=None):
        """
        Downloads the new EXE and seamlessly replaces the current one.
        progress_callback: function(current_bytes, total_bytes)
        completion_callback: function(success, error_msg)
        """
        def _download():
            try:
                # 1. Download to temp file
                print(f"[Update] Downloading from: {download_url}")
                response = requests.get(download_url, stream=True, timeout=10)
                total_size = int(response.headers.get('content-length', 0))
                
                # Determine new filename (e.g., WprTool_new.exe)
                # Ensure we are saving it in the SAME directory to make moving easier
                current_exe = sys.executable
                exe_dir = os.path.dirname(current_exe)
                new_exe_path = os.path.join(exe_dir, "WprTool_new.exe")
                
                block_size = 1024 # 1KB
                downloaded = 0
                
                with open(new_exe_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        f.write(data)
                        downloaded += len(data)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
                            
                print("[Update] Download complete. Preparing to install...")
                
                # 2. Create Updater Batch Script
                # This script: Waits -> Deletes Old EXE -> Renames New EXE -> Restarts -> Deletes Self
                bat_path = os.path.join(exe_dir, "updater.bat")
                exe_name = os.path.basename(current_exe)
                
                # Use 'timeout' to allow main app to close
                # Use 'start "" "app.exe"' to restart non-blocking
                bat_content = f"""
@echo off
timeout /t 2 /nobreak > NUL
del "{exe_name}"
rename "WprTool_new.exe" "{exe_name}"
start "" "{exe_name}"
del "%~f0"
"""
                with open(bat_path, "w") as bat:
                    bat.write(bat_content)
                
                if completion_callback:
                    completion_callback(True, bat_path)
                    
            except Exception as e:
                print(f"[Update] Failed: {e}")
                if completion_callback:
                    completion_callback(False, str(e))

        threading.Thread(target=_download, daemon=True).start()

