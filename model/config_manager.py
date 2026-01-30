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

    def save_config(self, site_url, username, password):
        data = {
            "site_url": site_url,
            "username": username,
            "password": password
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving config: {e}")
