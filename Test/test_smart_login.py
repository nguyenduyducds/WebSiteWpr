"""
🎯 TEST CÁC CẢI TIẾN MỚI - LOGIN THÔNG MINH

Các tính năng mới:
✅ Tự động dùng cookies nếu có (không cần login lại)
✅ Hiển thị tuổi của cookies
✅ Tự động phát hiện CAPTCHA/Cloudflare/Security
✅ Tự động chuyển sang VISIBLE mode nếu headless fail
✅ Cho phép user can thiệp thủ công khi cần
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model.selenium_wp import SeleniumWPClient

print("=" * 70)
print("🎯 TEST LOGIN THÔNG MINH - PHIÊN BẢN CẢI TIẾN")
print("=" * 70)
print()

# Credentials
site_url = "Spotlight.tfvp.org/wp-admin"
username = "admin79"
password = input("Nhập password (hoặc Enter để dùng mặc định): ").strip()
if not password:
    password = "Abc@123456"  # Default password

print()
print("=" * 70)
print("📋 THÔNG TIN:")
print(f"   Site: {site_url}")
print(f"   Username: {username}")
print(f"   Password: {'*' * len(password)}")
print("=" * 70)
print()

# Ask for mode
print("Chọn chế độ:")
print("1. Headless (Nền) - Nhanh, không hiện browser")
print("2. Visible (Hiện) - Chậm hơn, nhưng bạn thấy được")
print()
mode = input("Chọn (1/2, mặc định 1): ").strip()
headless = mode != "2"

print()
print("=" * 70)
print(f"🚀 BẮT ĐẦU TEST - Chế độ: {'HEADLESS' if headless else 'VISIBLE'}")
print("=" * 70)
print()

try:
    # Initialize client
    client = SeleniumWPClient(site_url, username, password)
    
    # Initialize driver
    print(f"[TEST] Đang khởi tạo Chrome driver...")
    client.init_driver(headless=headless)
    print("[TEST] ✅ Driver initialized")
    print()
    
    # Attempt login with smart retry
    print("[TEST] Đang thử login...")
    print("-" * 70)
    success = client.login(retry_visible_on_fail=True)
    print("-" * 70)
    
    if success:
        print()
        print("=" * 70)
        print("✅ ✅ ✅ LOGIN THÀNH CÔNG! ✅ ✅ ✅")
        print("=" * 70)
        print()
        print("📌 Lần sau bạn chạy, tool sẽ:")
        print("   → Tự động dùng cookies đã lưu")
        print("   → Không cần nhập password")
        print("   → Login trong < 5 giây")
        print()
        
        # Keep browser open for a moment
        import time
        print("[TEST] Giữ browser mở 10 giây để bạn xem...")
        for i in range(10, 0, -1):
            print(f"   {i}...", end='\r')
            time.sleep(1)
        print()
    else:
        print()
        print("=" * 70)
        print("❌ LOGIN THẤT BẠI")
        print("=" * 70)
    
    # Close
    print("\n[TEST] Đang đóng browser...")
    client.close()
    print("[TEST] ✅ Đã đóng")
    
except KeyboardInterrupt:
    print("\n\n[TEST] ⚠️  Người dùng hủy (Ctrl+C)")
    try:
        client.close()
    except:
        pass
    
except Exception as e:
    print()
    print("=" * 70)
    print("❌ LỖI XẢY RA")
    print("=" * 70)
    print(f"Lỗi: {e}")
    print()
    print("📸 Kiểm tra các file debug:")
    print("   - debug_login_fail.png")
    print("   - debug_login_fail.html")
    print("   - login_timeout.png (nếu timeout)")
    print("=" * 70)
    
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("🏁 TEST HOÀN TẤT")
print("=" * 70)
