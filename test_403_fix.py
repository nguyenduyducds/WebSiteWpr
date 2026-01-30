"""
Test script để kiểm tra fix lỗi 403
"""
import sys
sys.path.insert(0, '.')

from model.selenium_wp import SeleniumWPClient
from model.wp_model import BlogPost

# Test data
test_post = BlogPost(
    title="Test 403 Fix - " + str(__import__('time').time()),
    content="<p>This is a test post to verify 403 fix is working.</p><p>REST API calls are blocked, using form submit instead.</p>",
    image_url=None
)

# Init client
client = SeleniumWPClient(
    site_url="bodycam.vansonnguyen.com",
    username="admin79",  # Thay bằng username thật
    password="your_password"  # Thay bằng password thật
)

try:
    print("=" * 60)
    print("TESTING 403 FIX")
    print("=" * 60)
    
    # Init driver
    client.init_driver(headless=False)  # Để thấy quá trình
    
    # Login
    print("\n[1] Logging in...")
    client.login()
    
    # Post article
    print("\n[2] Posting article with 403 fix...")
    success, result = client.post_article(test_post)
    
    if success:
        print(f"\n✅ SUCCESS! Post published at: {result}")
    else:
        print(f"\n❌ FAILED: {result}")
    
    input("\nPress Enter to close browser...")
    
finally:
    if client.driver:
        client.close()
