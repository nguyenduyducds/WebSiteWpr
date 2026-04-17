
import json
import os
from datetime import datetime
from model.security import generate_key

KEYS_DB_FILE = "license_keys_db.json"

class KeyStorage:
    def __init__(self):
        self.keys = []
        self.load_keys()

    def load_keys(self):
        if os.path.exists(KEYS_DB_FILE):
            try:
                with open(KEYS_DB_FILE, 'r', encoding='utf-8') as f:
                    self.keys = json.load(f)
            except:
                self.keys = []
        else:
            self.keys = []

    def save_keys(self):
        try:
            with open(KEYS_DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.keys, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving keys: {e}")

    def create_new_key(self, note="", hwid=None):
        key = generate_key(machine_id=hwid)
        record = {
            "key": key,
            "note": note,
            "hwid_lock": hwid if hwid else "GLOBAL",
            "activated_ip": None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.keys.insert(0, record) # Add to top
        self.save_keys()
        return record

    def update_key(self, old_key_str, new_note, new_hwid):
        """Update note and HWID for an existing key entry."""
        for k in self.keys:
            if k['key'] == old_key_str:
                k['note'] = new_note
                k['hwid_lock'] = new_hwid if new_hwid else "GLOBAL"
                self.save_keys()
                return True
        return False

    def regenerate_key(self, old_key_str):
        """Generates a NEW key string for an existing record (Keep note + HWID)"""
        for i, k in enumerate(self.keys):
            if k['key'] == old_key_str:
                # Generate new key string derived from same HWID settings
                hwid = k.get('hwid_lock')
                if hwid == "GLOBAL": hwid = None
                
                new_key_str = generate_key(machine_id=hwid)
                
                # Update record
                k['key'] = new_key_str
                k['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Update time
                
                self.save_keys()
                return new_key_str
        return None

    def delete_key(self, key_str):
        self.keys = [k for k in self.keys if k["key"] != key_str]
        self.save_keys()

    def reset_key(self, key_str):
        for k in self.keys:
            if k['key'] == key_str:
                k['hwid_lock'] = "GLOBAL"
                k['activated_ip'] = None
                self.save_keys()
                return True
        return False

    def get_all_keys(self):
        return self.keys

    def try_activate_key(self, key_str, current_hwid, current_ip=None):
        """
        Attempt to activate a key on this machine.
        - If key GLOBAL: Lock it to current_hwid + Save IP
        - If key LOCKED: Check hwid + Update IP if needed
        """
        # Reload to ensure fresh data
        self.load_keys()
        
        for k in self.keys:
            if k['key'] == key_str:
                lock = k.get('hwid_lock', 'GLOBAL')
                
                if lock == 'GLOBAL':
                    # Auto-Lock
                    k['hwid_lock'] = current_hwid
                    k['activated_ip'] = current_ip
                    self.save_keys()
                    return True, "Activation Successful! (Locked to this machine)"
                    
                elif lock == current_hwid:
                    # Update IP if changed
                    if current_ip and k.get('activated_ip') != current_ip:
                        k['activated_ip'] = current_ip
                        self.save_keys()
                    return True, "Welcome back!"
                    
                else:
                    return False, f"Key is already used on another machine!"
                    
        return False, "Key not found in database."
