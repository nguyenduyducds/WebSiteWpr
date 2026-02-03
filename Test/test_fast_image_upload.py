"""
Test Fast Image Upload with REST API
"""

from model.wp_rest_api import WordPressRESTClient
import os

# Config
SITE_URL = "https://bodycam.vansonnguyen.com"
USERNAME = "admin79"  # Admin account
PASSWORD = "your_password_here"  # Replace with actual password

def test_rest_api_image_upload():
    """Test uploading image via REST API (fast method)"""
    
    print("=" * 60)
    print("TEST: Fast Image Upload with REST API")
    print("=" * 60)
    
    # 1. Initialize REST API client
    print("\n[1] Initializing REST API client...")
    client = WordPressRESTClient(SITE_URL, USERNAME, PASSWORD)
    
    # 2. Login
    print("\n[2] Logging in...")
    if not client.login():
        print("❌ Login failed!")
        return False
    
    print("✅ Login successful!")
    
    # 3. Find a test image
    print("\n[3] Finding test image...")
    test_images = []
    
    # Check thumbnails folder
    if os.path.exists("thumbnails"):
        for filename in os.listdir("thumbnails"):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join("thumbnails", filename))
    
    # Check saved_car_images folder
    if os.path.exists("saved_car_images"):
        for filename in os.listdir("saved_car_images"):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join("saved_car_images", filename))
    
    if not test_images:
        print("❌ No test images found in thumbnails/ or saved_car_images/")
        return False
    
    test_image = test_images[0]
    print(f"✅ Using test image: {test_image}")
    print(f"   Size: {os.path.getsize(test_image) // 1024} KB")
    
    # 4. Upload image via REST API
    print("\n[4] Uploading image via REST API...")
    import time
    start_time = time.time()
    
    success, media_id, media_url = client.upload_image(test_image)
    
    elapsed = time.time() - start_time
    
    if success:
        print(f"✅ Upload successful in {elapsed:.2f} seconds!")
        print(f"   Media ID: {media_id}")
        print(f"   Media URL: {media_url}")
        return True
    else:
        print(f"❌ Upload failed after {elapsed:.2f} seconds")
        return False

if __name__ == "__main__":
    test_rest_api_image_upload()
