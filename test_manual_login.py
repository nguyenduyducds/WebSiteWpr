"""
Test script - Mở browser VISIBLE để login bằng tay
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model.selenium_wp import SeleniumWPClient
import time

# Test credentials
site_url = "Spotlight.tfvp.org/wp-admin"
username = "admin79"
password = "Abc@123456"  # Thay bằng password thật

print("=" * 60)
print("🔍 MỞ BROWSER ĐỂ BẠN LOGIN BẰNG TAY")
print("=" * 60)
print(f"Site: {site_url}")
print(f"Username: {username}")
print("=" * 60)

try:
    # Initialize client
    client = SeleniumWPClient(site_url, username, password)
    
    # MỞ BROWSER VISIBLE (headless=False)
    print("\n[TEST] Đang mở Chrome browser...")
    client.init_driver(headless=False)  # ← VISIBLE MODE
    
    print("\n[TEST] Browser đã mở!")
    print("=" * 60)
    print("📌 HƯỚNG DẪN:")
    print("1. Browser sẽ tự động điền username/password")
    print("2. Nếu không tự động, hãy điền bằng tay")
    print("3. Nhấn Login và xem điều gì xảy ra")
    print("4. Chờ 60 giây để bạn quan sát...")
    print("=" * 60)
    
    # Navigate to login page
    from urllib.parse import urlparse
    parsed = urlparse(site_url if site_url.startswith('http') else 'https://' + site_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    login_url = base_url + '/wp-login.php'
    
    print(f"\n[TEST] Đang mở trang login: {login_url}")
    client.driver.get(login_url)
    
    # Wait for page to load
    time.sleep(3)
    
    # Try to fill fields (but don't submit)
    try:
        print("\n[TEST] Đang thử điền username/password...")
        user_field = client.driver.find_element("id", "user_login")
        pass_field = client.driver.find_element("id", "user_pass")
        
        # Fill using JavaScript
        client.driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, user_field, username)
        
        client.driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, pass_field, password)
        
        print("✅ Đã điền username/password")
        print("\n⏳ Bây giờ bạn có thể:")
        print("   - Nhấn nút 'Log In' bằng tay")
        print("   - Hoặc chờ script tự động submit sau 10 giây")
        
    except Exception as e:
        print(f"⚠️ Không thể tự động điền: {e}")
        print("👉 Hãy điền username/password BẰNG TAY")
    
    # Wait 10 seconds before auto-submit
    print("\n[TEST] Đếm ngược 10 giây trước khi tự động submit...")
    for i in range(10, 0, -1):
        print(f"   {i}...", end='\r')
        time.sleep(1)
    
    # Try to submit
    try:
        print("\n\n[TEST] Đang submit form...")
        submit_btn = client.driver.find_element("id", "wp-submit")
        submit_btn.click()
        print("✅ Đã click nút Login")
    except Exception as e:
        print(f"⚠️ Không thể click submit: {e}")
    
    # Wait to see what happens
    print("\n[TEST] Chờ 60 giây để xem kết quả...")
    print("=" * 60)
    print("👀 QUAN SÁT BROWSER VÀ CHO TÔI BIẾT:")
    print("   1. Có xuất hiện CAPTCHA không?")
    print("   2. Có thông báo lỗi gì không?")
    print("   3. Trang có redirect không?")
    print("   4. URL hiện tại là gì?")
    print("=" * 60)
    
    for i in range(60, 0, -1):
        current_url = client.driver.current_url
        print(f"\r⏱️  {i}s - URL: {current_url[:80]}...", end='')
        time.sleep(1)
    
    print("\n\n[TEST] Hoàn tất! Đang đóng browser...")
    
    # Take screenshot before closing
    client.driver.save_screenshot("manual_login_test.png")
    print("📸 Đã lưu screenshot: manual_login_test.png")
    
    # Save HTML
    with open("manual_login_test.html", "w", encoding="utf-8") as f:
        f.write(client.driver.page_source)
    print("📄 Đã lưu HTML: manual_login_test.html")
    
    # Close
    time.sleep(2)
    client.close()
    
except Exception as e:
    print(f"\n❌ LỖI: {e}")
    import traceback
    traceback.print_exc()

print("\n[TEST] Test hoàn tất!")
