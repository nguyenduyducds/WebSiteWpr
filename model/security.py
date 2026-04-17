
import hashlib
import uuid
import platform
import subprocess

import socket
import urllib.request

# --- CONFIGURATION ---
SECRET_SALT = "LVC_MEDIA_TOOL_2026_SECURE_SALT_!@#"

def get_machine_id():
    """
    Lấy Hardware ID duy nhất của máy.
    Kết hợp UUID node và tên máy để tạo fingerprint.
    """
    try:
        # 1. Get MAC Address (safe uuid)
        mac = uuid.getnode()
        # 2. Get Machine Name
        node = platform.node()
        # 3. Combine
        raw = f"{mac}-{node}"
        # 4. Hash it to make it short and clean
        return hashlib.md5(raw.encode()).hexdigest()[:8].upper()
    except:
        return "UNKNOWN_ID"

def get_public_ip():
    """
    Lay dia chi IP Public cua may (de quan ly).
    Fallback ve Local IP neu khong co internet.
    """
    try:
        # Try external service (fast timeout = 2s)
        with urllib.request.urlopen('https://api.ipify.org', timeout=2) as response:
            return response.read().decode('utf8')
    except:
        try:
            # Fallback 2
            with urllib.request.urlopen('https://ipv4.icanhazip.com', timeout=2) as response:
                return response.read().decode('utf8').strip()
        except:
            # Fallback to local IP
            try:
                return socket.gethostbyname(socket.gethostname())
            except:
                return "Unknown IP"

def generate_key(prefix="LVC", machine_id=None):
    """
    Tạo key.
    - Nếu có machine_id: Key chỉ hoạt động trên máy đó (Locked).
    - Nếu không (None): Key hoạt động mọi nơi (Global).
    """
    # 1. Random part
    random_part = uuid.uuid4().hex[:8].upper()
    
    # 2. Determine lock string
    lock_str = machine_id.strip().upper() if machine_id else "GLOBAL_UNLOCK"
    
    # 3. Create signature
    # Signature = Hash( RANDOM + SALT + LOCK_STR )
    raw_str = f"{random_part}{SECRET_SALT}{lock_str}"
    signature = hashlib.sha256(raw_str.encode()).hexdigest()[:4].upper()
    
    # 4. Format: PREFIX-RANDOM-SIGNATURE
    return f"{prefix}-{random_part}-{signature}"

def validate_key(key_input):
    """
    Kiểm tra key hợp lệ trên máy này không.
    Thử 2 trường hợp:
    1. Key Global (Không khóa cứng)
    2. Key Locked (Khóa cứng theo Machine ID hiện tại)
    """
    try:
        key_input = key_input.strip().upper()
        parts = key_input.split('-')
        
        if len(parts) != 3:
            return False
            
        prefix, random_part, signature = parts
        
        if prefix != "LVC":
            return False
            
        # Case 1: Check if it's a GLOBAL key
        raw_global = f"{random_part}{SECRET_SALT}GLOBAL_UNLOCK"
        sig_global = hashlib.sha256(raw_global.encode()).hexdigest()[:4].upper()
        if signature == sig_global:
            return True
            
        # Case 2: Check if it's LOCKED to THIS machine
        current_machine_id = get_machine_id()
        raw_local = f"{random_part}{SECRET_SALT}{current_machine_id}"
        sig_local = hashlib.sha256(raw_local.encode()).hexdigest()[:4].upper()
        
        if signature == sig_local:
            return True
            
        return False
    except:
        return False
