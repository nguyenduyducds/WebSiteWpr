"""
🔍 SCRIPT KIỂM TRA VẤN ĐỀ SCAN LINK CHẬM
Chạy script này để tìm nguyên nhân chính xác
"""

import sys
import os

print("=" * 60)
print("🔍 KIỂM TRA HỆ THỐNG - SCAN LINK CHẬM")
print("=" * 60)
print()

# 1. Kiểm tra Python version
print("1️⃣ Kiểm tra Python Version:")
print(f"   ✅ Python {sys.version}")
print()

# 2. Kiểm tra các thư viện quan trọng
print("2️⃣ Kiểm tra Thư Viện:")
libraries = {
    'yt_dlp': 'yt-dlp (Lấy video info)',
    'undetected_chromedriver': 'undetected-chromedriver (Bypass bot detection)',
    'selenium': 'Selenium (Browser automation)',
    'requests': 'Requests (HTTP requests)',
    'bs4': 'BeautifulSoup4 (Parse HTML)',
    'cv2': 'OpenCV (Face detection - Optional)',
}

missing_libs = []
for lib, desc in libraries.items():
    try:
        __import__(lib)
        print(f"   ✅ {lib:30s} - {desc}")
    except ImportError:
        print(f"   ❌ {lib:30s} - THIẾU! ({desc})")
        missing_libs.append(lib)

print()

# 3. Kiểm tra yt-dlp có hỗ trợ impersonate không
print("3️⃣ Kiểm tra yt-dlp Impersonate:")
try:
    import yt_dlp
    import subprocess
    
    # Check if yt-dlp supports impersonate
    result = subprocess.run(
        ['yt-dlp', '--list-impersonate-targets'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0 and result.stdout:
        print(f"   ✅ yt-dlp hỗ trợ impersonate")
        if 'chrome' in result.stdout.lower():
            print(f"   ✅ Có hỗ trợ Chrome impersonate")
        else:
            print(f"   ⚠️ KHÔNG hỗ trợ Chrome impersonate (cần cài curl-cffi)")
    else:
        print(f"   ⚠️ yt-dlp KHÔNG hỗ trợ impersonate (cần cài curl-cffi)")
        print(f"   💡 Nhưng vẫn có thể hoạt động bình thường!")
        
except Exception as e:
    print(f"   ⚠️ Không kiểm tra được: {e}")

print()

# 4. Kiểm tra Chrome/ChromeDriver
print("4️⃣ Kiểm tra Chrome Driver:")
chrome_portable = os.path.join(os.getcwd(), "chrome_portable", "chrome.exe")
if os.path.exists(chrome_portable):
    print(f"   ✅ Tìm thấy Chrome Portable")
else:
    print(f"   ⚠️ Không tìm thấy Chrome Portable (sẽ dùng Chrome hệ thống)")

print()

# 5. Kiểm tra Facebook Cookies
print("5️⃣ Kiểm tra Facebook Cookies:")
cookie_path = "facebook_cookies.txt"
if os.path.exists(cookie_path):
    with open(cookie_path, 'r', encoding='utf-8') as f:
        lines = [l for l in f.readlines() if l.strip() and not l.startswith('#')]
    print(f"   ✅ Tìm thấy facebook_cookies.txt ({len(lines)} cookies)")
    print(f"   💡 Có cookie → Ít bị Facebook chặn hơn")
else:
    print(f"   ❌ KHÔNG có facebook_cookies.txt")
    print(f"   ⚠️ Chạy chế độ Guest → DỄ BỊ FACEBOOK CHẶN!")
    print(f"   💡 Đây có thể là nguyên nhân chính gây CHẬM!")

print()

# 6. Test kết nối Facebook
print("6️⃣ Test Kết Nối Facebook:")
try:
    import requests
    import time
    
    start = time.time()
    response = requests.get(
        'https://www.facebook.com',
        headers={'User-Agent': 'Mozilla/5.0'},
        timeout=10
    )
    elapsed = time.time() - start
    
    print(f"   ✅ Kết nối thành công ({elapsed:.2f}s)")
    
    if 'login' in response.url.lower() or 'checkpoint' in response.url.lower():
        print(f"   ⚠️ Facebook yêu cầu đăng nhập → CẦN COOKIE!")
    elif elapsed > 5:
        print(f"   ⚠️ Kết nối chậm ({elapsed:.2f}s) → Có thể do mạng hoặc bị chặn")
    else:
        print(f"   ✅ Kết nối tốt")
        
except Exception as e:
    print(f"   ❌ Lỗi kết nối: {e}")
    print(f"   ⚠️ Có thể bị Firewall/Antivirus chặn")

print()

# 7. Kết luận
print("=" * 60)
print("📊 KẾT LUẬN:")
print("=" * 60)

if missing_libs:
    print(f"❌ THIẾU {len(missing_libs)} THƯ VIỆN:")
    for lib in missing_libs:
        print(f"   - {lib}")
    print()
    print("💡 Cài đặt bằng lệnh:")
    print(f"   pip install {' '.join(missing_libs)}")
    print()

if not os.path.exists(cookie_path):
    print("⚠️ NGUYÊN NHÂN CHÍNH: THIẾU FACEBOOK COOKIES")
    print()
    print("📝 CÁCH KHẮC PHỤC:")
    print("   1. Cài extension 'Get cookies.txt' trên Chrome")
    print("   2. Đăng nhập Facebook")
    print("   3. Export cookies → Lưu thành 'facebook_cookies.txt'")
    print("   4. Đặt file vào thư mục tool")
    print()
    print("   → Sau khi có cookie, scan sẽ NHANH HƠN NHIỀU!")
    print()

print("💡 KHUYẾN NGHỊ:")
if missing_libs or not os.path.exists(cookie_path):
    print("   1. Cài đủ thư viện (nếu thiếu)")
    print("   2. Thêm Facebook cookies (QUAN TRỌNG NHẤT!)")
    print("   3. Tắt Headless mode nếu vẫn chậm")
else:
    print("   ✅ Hệ thống OK!")
    print("   💡 Nếu vẫn chậm:")
    print("      - Tắt Headless mode")
    print("      - Kiểm tra Firewall/Antivirus")
    print("      - Thử đổi mạng/VPN")

print()
print("=" * 60)
print("✅ HOÀN TẤT KIỂM TRA")
print("=" * 60)
