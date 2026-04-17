import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file

    def load_config(self):
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_config(self, site_url, username, password, app_password=None):
        # Merge to avoid wiping unrelated config keys (e.g. update_url)
        existing = self.load_config() or {}
        data = dict(existing)
        data.update({
            "site_url": site_url,
            "username": username,
            "password": password,
        })
        # Optional: WordPress Application Password for REST API Basic Auth
        # Keep existing value if caller doesn't provide one.
        if app_password is not None:
            data["app_password"] = app_password
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving config: {e}")
