
import requests
import webbrowser
from packaging import version
import threading

class UpdateChecker:
    def __init__(self, current_version, update_url=None):
        self.current_version = current_version
        # Placeholder URL - User should replace this with their actual version file URL
        # Format of remote file: JSON {"version": "1.0.1", "download_url": "..."} or just raw text "1.0.1"
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
                # 1. Fetch remote version
                # Note: Setting a short timeout to prevent hanging the app on startup
                response = requests.get(self.update_url, timeout=3)
                
                if response.status_code == 200:
                    data = response.json()
                    remote_ver_str = data.get("version", "0.0.0")
                    self.download_url = data.get("download_url", "")
                    
                    # 2. Compare versions
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
                print(f"[Update] Error checking for updates: {e}")
                if callback: callback(False, None, None)

        # Run in thread
        t = threading.Thread(target=_check, daemon=True)
        t.start()
