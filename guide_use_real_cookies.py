"""
GIẢI PHÁP THAY THẾ: Sử dụng cookies từ browser thật của bạn

HƯỚNG DẪN:
1. Mở Chrome/Edge thông thường
2. Login vào https://spotlight.tfvp.org/wp-admin/ BẰNG TAY
3. Sau khi login thành công, chạy script này
4. Script sẽ copy cookies từ browser thật sang automation browser
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🍪 HƯỚNG DẪN SỬ DỤNG COOKIES TỪ BROWSER THẬT")
print("=" * 60)
print()
print("BƯỚC 1: Mở Chrome/Edge thông thường")
print("BƯỚC 2: Truy cập: https://spotlight.tfvp.org/wp-admin/")
print("BƯỚC 3: Login BẰNG TAY (nhập username/password)")
print("BƯỚC 4: Sau khi vào được dashboard, nhấn F12")
print("BƯỚC 5: Vào tab 'Console'")
print("BƯỚC 6: Paste đoạn code này vào Console:")
print()
print("-" * 60)
print("""
// Copy đoạn này vào Console của browser
copy(JSON.stringify(document.cookie.split('; ').map(c => {
    const [name, value] = c.split('=');
    return {name, value, domain: '.tfvp.org', path: '/'};
})));
""")
print("-" * 60)
print()
print("BƯỚC 7: Cookies đã được copy vào clipboard")
print("BƯỚC 8: Paste vào file: cookies_from_browser.json")
print("BƯỚC 9: Chạy lại tool, nó sẽ tự động dùng cookies này")
print()
print("=" * 60)
print()

# Tạo file mẫu
sample_cookies = """
[
    {"name": "wordpress_logged_in_xxx", "value": "your_cookie_value", "domain": ".tfvp.org", "path": "/"},
    {"name": "wp-settings-time-1", "value": "1234567890", "domain": ".tfvp.org", "path": "/"}
]
"""

with open("cookies_from_browser_SAMPLE.json", "w", encoding="utf-8") as f:
    f.write(sample_cookies.strip())

print("✅ Đã tạo file mẫu: cookies_from_browser_SAMPLE.json")
print()
print("📌 LƯU Ý:")
print("   - Cách này BỎ QUA hoàn toàn việc login tự động")
print("   - Cookies sẽ hết hạn sau vài ngày/tuần")
print("   - Khi hết hạn, lặp lại quy trình trên")
print()
print("=" * 60)
