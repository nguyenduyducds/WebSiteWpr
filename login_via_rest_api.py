"""
GIẢI PHÁP MỚI: Login bằng REST API thay vì Selenium

Vấn đề: Selenium không thể điền form trong headless mode
Giải pháp: Dùng REST API để lấy cookies, sau đó inject vào Selenium
"""

import requests
from urllib.parse import urlparse
import pickle

def login_via_rest_api(site_url, username, password):
    """
    Login vào WordPress bằng REST API và lấy cookies
    """
    # Parse URL
    if not site_url.startswith('http'):
        site_url = 'https://' + site_url
    
    parsed = urlparse(site_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    print(f"[REST API] Attempting login to: {base_url}")
    
    # Create session
    session = requests.Session()
    
    # Step 1: Get login page to get nonce and cookies
    login_url = f"{base_url}/wp-login.php"
    print(f"[REST API] Getting login page...")
    
    try:
        response = session.get(login_url, timeout=10)
        print(f"[REST API] Login page status: {response.status_code}")
        
        # Step 2: Submit login form
        login_data = {
            'log': username,
            'pwd': password,
            'wp-submit': 'Log In',
            'redirect_to': f'{base_url}/wp-admin/',
            'testcookie': '1',
            'rememberme': 'forever'
        }
        
        print(f"[REST API] Submitting login...")
        response = session.post(login_url, data=login_data, allow_redirects=True, timeout=10)
        
        print(f"[REST API] Response status: {response.status_code}")
        print(f"[REST API] Final URL: {response.url}")
        
        # Check if login successful
        if 'wp-admin' in response.url and 'wp-login.php' not in response.url:
            print("[REST API] ✅ Login successful!")
            
            # Convert requests cookies to Selenium format
            selenium_cookies = []
            for cookie in session.cookies:
                selenium_cookie = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain if cookie.domain else parsed.netloc,
                    'path': cookie.path if cookie.path else '/',
                }
                if cookie.expires:
                    selenium_cookie['expiry'] = int(cookie.expires)
                
                selenium_cookies.append(selenium_cookie)
            
            print(f"[REST API] Got {len(selenium_cookies)} cookies")
            
            # Save cookies
            cookie_filename = f"cookies_{username}.pkl"
            with open(cookie_filename, 'wb') as f:
                pickle.dump(selenium_cookies, f)
            
            print(f"[REST API] ✅ Saved cookies to {cookie_filename}")
            
            return True, selenium_cookies
        
        elif 'reauth=1' in response.url:
            print("[REST API] ❌ Login failed: Invalid credentials")
            return False, None
        
        else:
            # Check response content for errors
            if 'login_error' in response.text or 'ERROR' in response.text:
                print("[REST API] ❌ Login failed: Check credentials")
                # Try to extract error message
                import re
                error_match = re.search(r'<div id="login_error">(.+?)</div>', response.text, re.DOTALL)
                if error_match:
                    error_text = error_match.group(1).strip()
                    print(f"[REST API] Error: {error_text}")
            else:
                print("[REST API] ⚠️  Unknown response")
            
            return False, None
            
    except Exception as e:
        print(f"[REST API] ❌ Error: {e}")
        return False, None


if __name__ == "__main__":
    # Test
    site_url = "spotlight.tfvp.org"
    username = "admin79"
    password = input("Enter password: ").strip()
    
    success, cookies = login_via_rest_api(site_url, username, password)
    
    if success:
        print("\n" + "="*60)
        print("✅ LOGIN THÀNH CÔNG VIA REST API!")
        print("="*60)
        print(f"Cookies đã được lưu vào: cookies_{username}.pkl")
        print("Bây giờ Selenium sẽ dùng cookies này để login!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ LOGIN THẤT BẠI")
        print("="*60)
        print("Kiểm tra lại username/password")
