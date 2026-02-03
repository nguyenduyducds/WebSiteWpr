import requests
import webbrowser
from packaging import version
import threading
import os
import sys
import subprocess
import time
import tempfile

class UpdateChecker:
    def __init__(self, current_version, update_url=None):
        self.current_version = current_version
        self.update_url = update_url if update_url else "https://example.com/version.json" 
        self.latest_version = None
        self.download_url = None

    def check_for_updates(self, callback=None):
        def _check():
            try:
                # Add cache buster to URL
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
        Downloads a Setup EXE to a temporary folder and runs it.
        This allows upgrading "Folder-based" apps by running an external installer.
        """
        def _download():
            try:
                print(f"[Update] Downloading Installer from: {download_url}")
                response = requests.get(download_url, stream=True, timeout=15)
                total_size = int(response.headers.get('content-length', 0))
                
                # Download to %TEMP% directory
                temp_dir = tempfile.gettempdir()
                installer_name = "WprTool_Update_Installer.exe"
                installer_path = os.path.join(temp_dir, installer_name)
                
                # Use bigger block size for speed
                block_size = 8192
                downloaded = 0
                
                with open(installer_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        f.write(data)
                        downloaded += len(data)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
                            
                print("[Update] Download complete. Executing installer...")
                
                if completion_callback:
                    completion_callback(True, installer_path)
                    
            except Exception as e:
                print(f"[Update] Failed: {e}")
                if completion_callback:
                    completion_callback(False, str(e))

        threading.Thread(target=_download, daemon=True).start()
