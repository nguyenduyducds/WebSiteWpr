"""
Test script to verify the login fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model.selenium_wp import SeleniumWPClient

# Test credentials from the screenshot
site_url = "Spotlight.tfvp.org/wp-admin"
username = "admin79"
password = "your_password_here"  # Replace with actual password

print("=" * 60)
print("Testing WordPress Login Fix")
print("=" * 60)

try:
    # Initialize client
    client = SeleniumWPClient(site_url, username, password)
    
    # Initialize driver in headless mode
    client.init_driver(headless=True)
    
    # Attempt login
    print("\n[TEST] Attempting login...")
    success = client.login()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ LOGIN SUCCESSFUL!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ LOGIN FAILED")
        print("=" * 60)
    
    # Keep browser open for a moment to verify
    import time
    time.sleep(5)
    
    # Close
    client.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n[TEST] Test completed. Check the output above for results.")
