"""
🔧 GIẢI PHÁP TOÀN DIỆN CHO VẤN ĐỀ LOGIN

Nếu login tự động không hoạt động, có 3 nguyên nhân chính:
1. Website có CAPTCHA/Cloudflare/Security plugin
2. Credentials không đúng
3. IP bị block do quá nhiều lần thử

GIẢI PHÁP:
"""

print("=" * 70)
print("🔧 CHỌN PHƯƠNG PHÁP LOGIN")
print("=" * 70)
print()
print("1️⃣  LOGIN TỰ ĐỘNG (Headless) - Nhanh nhưng dễ bị chặn")
print("2️⃣  LOGIN BÁN TỰ ĐỘNG (Visible Browser) - Bạn có thể can thiệp")
print("3️⃣  SỬ DỤNG COOKIES TỪ BROWSER THẬT - Đáng tin cậy nhất")
print()
print("=" * 70)

choice = input("\nChọn phương pháp (1/2/3): ").strip()

if choice == "1":
    print("\n✅ Bạn chọn: LOGIN TỰ ĐỘNG")
    print("Đang chạy test_login_fix.py...")
    import subprocess
    subprocess.run(["py", "test_login_fix.py"])
    
elif choice == "2":
    print("\n✅ Bạn chọn: LOGIN BÁN TỰ ĐỘNG")
    print("Đang mở browser visible...")
    import subprocess
    subprocess.run(["py", "test_manual_login.py"])
    
elif choice == "3":
    print("\n✅ Bạn chọn: SỬ DỤNG COOKIES")
    print()
    print("📋 HƯỚNG DẪN:")
    print("-" * 70)
    print("1. Mở Chrome/Edge bình thường")
    print("2. Vào: https://spotlight.tfvp.org/wp-admin/")
    print("3. Login bằng tay (nhập username/password)")
    print("4. Sau khi vào dashboard, nhấn F12")
    print("5. Chọn tab 'Application' > 'Cookies'")
    print("6. Tìm cookies có tên bắt đầu bằng 'wordpress_logged_in'")
    print("7. Copy toàn bộ cookies")
    print()
    print("HOẶC dùng cách nhanh:")
    print("-" * 70)
    print("1. Login vào WordPress bằng browser thật")
    print("2. Nhấn F12 > Console")
    print("3. Paste lệnh này:")
    print()
    print('   copy(JSON.stringify(document.cookie))')
    print()
    print("4. Cookies đã được copy vào clipboard")
    print("5. Tạo file 'manual_cookies.txt' và paste vào")
    print("-" * 70)
    print()
    
    # Tạo script để import cookies
    import_script = """
import pickle
import json

# Đọc cookies từ file
with open('manual_cookies.txt', 'r') as f:
    cookie_string = f.read().strip()

# Parse cookies
cookies = []
for item in cookie_string.split('; '):
    if '=' in item:
        name, value = item.split('=', 1)
        cookies.append({
            'name': name,
            'value': value,
            'domain': '.tfvp.org',
            'path': '/'
        })

# Lưu vào file pickle
with open('cookies_admin79.pkl', 'wb') as f:
    pickle.dump(cookies, f)

print(f"✅ Đã import {len(cookies)} cookies vào cookies_admin79.pkl")
print("Bây giờ bạn có thể chạy tool bình thường!")
"""
    
    with open("import_manual_cookies.py", "w", encoding="utf-8") as f:
        f.write(import_script)
    
    print("✅ Đã tạo script: import_manual_cookies.py")
    print()
    print("Sau khi có cookies, chạy:")
    print("   py import_manual_cookies.py")
    print()
    
else:
    print("\n❌ Lựa chọn không hợp lệ!")

print()
print("=" * 70)
