"""
Debug script to diagnose login issues
"""

import time
from model.selenium_wp import SeleniumWPClient
from model.config_manager import ConfigManager

def debug_login():
    """Debug login with detailed output"""
    print("=" * 60)
    print("LOGIN DEBUG TOOL")
    print("=" * 60)
    
    # Load config
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    site_url = config.get("site_url", "")
    username = config.get("username", "")
    password = config.get("password", "")
    
    if not site_url or not username or not password:
        print("❌ No saved credentials found!")
        print("Please login via GUI first.")
        return
    
    print(f"\n📋 Config:")
    print(f"   Site: {site_url}")
    print(f"   User: {username}")
    print(f"   Pass: {'*' * len(password)}")
    
    # Initialize Selenium
    print(f"\n[1] Initializing Selenium (VISIBLE mode for debugging)...")
    client = SeleniumWPClient(site_url, username, password)
    
    try:
        client.init_driver(headless=False)  # Visible mode
        print("✅ Driver initialized")
        
        # Try login
        print(f"\n[2] Attempting login...")
        success = client.login()
        
        if success:
            print("\n✅ LOGIN SUCCESSFUL!")
            print(f"Current URL: {client.driver.current_url}")
            
            # Keep browser open for inspection
            print("\n💡 Browser will stay open for 30 seconds for inspection...")
            time.sleep(30)
        else:
            print("\n❌ LOGIN FAILED!")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
        # Check for common issues
        print("\n🔍 Checking for common issues...")
        
        try:
            current_url = client.driver.current_url
            page_source = client.driver.page_source.lower()
            
            print(f"\n📍 Current URL: {current_url}")
            
            # Check 1: CAPTCHA
            if "captcha" in page_source or "recaptcha" in page_source:
                print("⚠️ CAPTCHA detected!")
                print("   Solution: Disable CAPTCHA for admin login")
                
            # Check 2: Cloudflare
            if "cloudflare" in page_source or "checking your browser" in page_source:
                print("⚠️ Cloudflare protection detected!")
                print("   Solution: Whitelist your IP or disable Cloudflare for wp-login.php")
                
            # Check 3: Rate limiting
            if "rate limit" in page_source or "too many" in page_source:
                print("⚠️ Rate limiting detected!")
                print("   Solution: Wait a few minutes and try again")
                
            # Check 4: Wrong credentials
            if "incorrect" in page_source or "invalid" in page_source:
                print("⚠️ Invalid credentials!")
                print("   Solution: Check username and password")
                
            # Check 5: 2FA
            if "two-factor" in page_source or "2fa" in page_source or "authentication code" in page_source:
                print("⚠️ Two-Factor Authentication detected!")
                print("   Solution: Disable 2FA or use application password")
                
            # Check 6: Popup/Modal
            if "modal" in page_source or "popup" in page_source:
                print("⚠️ Popup/Modal detected!")
                print("   Solution: Check for blocking popups")
            
            print("\n📸 Debug files saved:")
            print("   - login_timeout.png (screenshot)")
            print("   - login_timeout.html (page source)")
            
            # Keep browser open for manual inspection
            print("\n💡 Browser will stay open for 60 seconds for manual inspection...")
            print("   You can manually solve CAPTCHA or check what's blocking login")
            time.sleep(60)
            
        except Exception as debug_err:
            print(f"Could not analyze: {debug_err}")
    
    finally:
        try:
            client.close()
        except:
            pass
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    debug_login()
