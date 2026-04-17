"""
WordPress Account Manager
Quản lý nhiều tài khoản WordPress để login nhanh
"""

import json
import os
from cryptography.fernet import Fernet
import base64
import hashlib

class WPAccountManager:
    def __init__(self, config_file="wp_accounts.json"):
        self.config_file = config_file
        self.accounts = []
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
        self.load_accounts()
    
    def _get_or_create_key(self):
        """Tạo hoặc load encryption key"""
        key_file = ".wp_key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Tạo key mới từ machine ID
            machine_id = os.environ.get('COMPUTERNAME', 'default')
            key = base64.urlsafe_b64encode(hashlib.sha256(machine_id.encode()).digest())
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _encrypt(self, text):
        """Mã hóa password"""
        return self.cipher.encrypt(text.encode()).decode()
    
    def _decrypt(self, encrypted_text):
        """Giải mã password"""
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except:
            return ""
    
    def load_accounts(self):
        """Load danh sách tài khoản từ file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = data.get('accounts', [])
            except Exception as e:
                print(f"Error loading accounts: {e}")
                self.accounts = []
        else:
            self.accounts = []
    
    def save_accounts(self):
        """Lưu danh sách tài khoản vào file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'accounts': self.accounts}, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving accounts: {e}")
            return False
    
    def add_account(self, name, site_url, username, password, is_headless=True):
        """Thêm tài khoản mới"""
        # Kiểm tra trùng
        for acc in self.accounts:
            if acc['site_url'] == site_url and acc['username'] == username:
                return False, "Tài khoản đã tồn tại!"
        
        account = {
            'name': name,
            'site_url': site_url,
            'username': username,
            'password': self._encrypt(password),
            'is_headless': is_headless,
            'last_used': None
        }
        
        self.accounts.append(account)
        return self.save_accounts(), "Đã thêm tài khoản!"
    
    def update_account(self, index, name, site_url, username, password, is_headless):
        """Cập nhật tài khoản"""
        if 0 <= index < len(self.accounts):
            self.accounts[index] = {
                'name': name,
                'site_url': site_url,
                'username': username,
                'password': self._encrypt(password) if password else self.accounts[index]['password'],
                'is_headless': is_headless,
                'last_used': self.accounts[index].get('last_used')
            }
            return self.save_accounts(), "Đã cập nhật!"
        return False, "Không tìm thấy tài khoản!"
    
    def delete_account(self, index):
        """Xóa tài khoản"""
        if 0 <= index < len(self.accounts):
            self.accounts.pop(index)
            return self.save_accounts(), "Đã xóa tài khoản!"
        return False, "Không tìm thấy tài khoản!"
    
    def get_account(self, index):
        """Lấy thông tin tài khoản (đã giải mã password)"""
        if 0 <= index < len(self.accounts):
            acc = self.accounts[index].copy()
            acc['password'] = self._decrypt(acc['password'])
            return acc
        return None
    
    def get_all_accounts(self):
        """Lấy tất cả tài khoản (không giải mã password)"""
        return self.accounts
    
    def update_last_used(self, index):
        """Cập nhật thời gian sử dụng cuối"""
        if 0 <= index < len(self.accounts):
            from datetime import datetime
            self.accounts[index]['last_used'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save_accounts()
