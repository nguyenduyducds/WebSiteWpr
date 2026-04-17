"""
Kiểm tra website WordPress có hoạt động bình thường không
"""
import requests
import sys

site_url = "https://spotlight.tfvp.org"

print("=" * 60)
print("🔍 KIỂM TRA WEBSITE WORDPRESS")
print("=" * 60)

# Test 1: Kiểm tra homepage
print(f"\n[1] Kiểm tra homepage: {site_url}")
try:
    response = requests.get(site_url, timeout=10)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   ✅ Response time: {response.elapsed.total_seconds():.2f}s")
    
    if "cloudflare" in response.text.lower():
        print("   ⚠️  PHÁT HIỆN CLOUDFLARE!")
    if "captcha" in response.text.lower():
        print("   ⚠️  PHÁT HIỆN CAPTCHA!")
        
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Test 2: Kiểm tra login page
login_url = f"{site_url}/wp-login.php"
print(f"\n[2] Kiểm tra login page: {login_url}")
try:
    response = requests.get(login_url, timeout=10)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   ✅ Response time: {response.elapsed.total_seconds():.2f}s")
    
    # Check for security features
    if "cloudflare" in response.text.lower():
        print("   ⚠️  CLOUDFLARE đang bảo vệ trang login!")
    if "recaptcha" in response.text.lower() or "hcaptcha" in response.text.lower():
        print("   ⚠️  CAPTCHA được kích hoạt trên trang login!")
    if "wordfence" in response.text.lower():
        print("   ⚠️  WordFence security plugin đang hoạt động!")
    if "limit" in response.text.lower() or "blocked" in response.text.lower():
        print("   ⚠️  Có thể bị rate limiting hoặc IP block!")
    
    # Check for login form
    if 'id="user_login"' in response.text:
        print("   ✅ Login form tồn tại")
    else:
        print("   ❌ Không tìm thấy login form!")
        
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Test 3: Kiểm tra wp-admin
admin_url = f"{site_url}/wp-admin/"
print(f"\n[3] Kiểm tra wp-admin: {admin_url}")
try:
    response = requests.get(admin_url, timeout=10, allow_redirects=False)
    print(f"   ✅ Status: {response.status_code}")
    if response.status_code == 302:
        redirect = response.headers.get('Location', '')
        print(f"   ↪️  Redirect to: {redirect}")
        if "wp-login.php" in redirect:
            print("   ✅ Redirect đúng (yêu cầu login)")
        
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Test 4: Kiểm tra REST API
api_url = f"{site_url}/wp-json/wp/v2/posts"
print(f"\n[4] Kiểm tra REST API: {api_url}")
try:
    response = requests.get(api_url, timeout=10)
    print(f"   ✅ Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ REST API hoạt động bình thường")
    elif response.status_code == 401:
        print("   ℹ️  REST API yêu cầu authentication (bình thường)")
    else:
        print(f"   ⚠️  REST API trả về status: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

print("\n" + "=" * 60)
print("KẾT LUẬN:")
print("=" * 60)
print("Nếu thấy cảnh báo về Cloudflare/CAPTCHA/WordFence,")
print("đó có thể là nguyên nhân khiến login tự động bị chặn.")
print("=" * 60)
