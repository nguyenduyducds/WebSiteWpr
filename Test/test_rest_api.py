"""
Test WordPress REST API Direct Method
This bypasses Selenium/Gutenberg completely
"""

import sys
sys.path.insert(0, '.')

from model.wp_rest_api import WordPressRESTClient
from model.wp_model import BlogPost

def test_rest_api():
    """Test REST API posting"""
    
    # Configuration
    SITE_URL = "https://spotlight.tfvp.org"  # or bodycam.vansonnguyen.com
    USERNAME = "admin79"
    PASSWORD = input("Enter password: ")
    
    print("=" * 60)
    print("TESTING WORDPRESS REST API METHOD")
    print("=" * 60)
    
    # Create client
    client = WordPressRESTClient(SITE_URL, USERNAME, PASSWORD)
    
    # Step 1: Test API availability
    print("\n[STEP 1] Testing API availability...")
    is_available, status_code, message = client.test_api_availability()
    
    if not is_available:
        print(f"❌ REST API not available: {message}")
        print("\nRECOMMENDATIONS:")
        if status_code == 403:
            print("- REST API is blocked by security plugin (Wordfence, iThemes, etc.)")
            print("- Contact admin to whitelist REST API")
            print("- Or use Selenium method as fallback")
        elif status_code == 404:
            print("- REST API might be disabled")
            print("- Check WordPress version (need 4.7+)")
        return False
    
    print("✅ REST API is available!")
    
    # Step 2: Login
    print("\n[STEP 2] Logging in...")
    if not client.login():
        print("❌ Login failed")
        print("\nTROUBLESHOOTING:")
        print("- Check username and password")
        print("- Try creating an Application Password in WordPress")
        print("  (Users → Your Profile → Application Passwords)")
        return False
    
    print("✅ Login successful!")
    
    # Step 3: Create test post
    print("\n[STEP 3] Creating test post...")
    
    test_post = BlogPost(
        title="REST API Test Post - " + __import__('time').strftime("%Y-%m-%d %H:%M:%S"),
        video_url="https://player.vimeo.com/video/123456789",
        image_url="",  # Optional: add path to test image
        raw_content=""
    )
    
    # Generate content
    test_post.generate_seo_content()
    
    print(f"Title: {test_post.title}")
    print(f"Content length: {len(test_post.content)} chars")
    
    # Upload image if provided
    featured_media_id = None
    if test_post.image_url:
        print("\n[STEP 4] Uploading featured image...")
        success, media_id, media_url = client.upload_image(test_post.image_url)
        if success:
            print(f"✅ Image uploaded: {media_url}")
            featured_media_id = media_id
        else:
            print("⚠️ Image upload failed, continuing without it...")
    
    # Create post
    print("\n[STEP 5] Creating post...")
    success, post_id, post_url = client.create_post(
        title=test_post.title,
        content=test_post.content,
        featured_media_id=featured_media_id,
        status='publish'
    )
    
    if success:
        print("=" * 60)
        print("✅✅✅ SUCCESS! ✅✅✅")
        print("=" * 60)
        print(f"Post ID: {post_id}")
        print(f"Post URL: {post_url}")
        print("\nREST API method works perfectly!")
        print("This is MUCH faster and more reliable than Selenium.")
        return True
    else:
        print("❌ Post creation failed")
        return False

if __name__ == "__main__":
    test_rest_api()
