"""
Test Vimeo API Upload
Run this to test if your API credentials are working
"""

import sys
import os

# Add model to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'model'))

from vimeo_api import VimeoAPIUploader


def test_api_connection():
    """Test API connection and credentials"""
    print("=" * 60)
    print("Testing Vimeo API Connection")
    print("=" * 60)
    print()
    
    uploader = VimeoAPIUploader()
    
    if not uploader.client:
        print("❌ API client not initialized")
        print()
        print("📝 Please configure vimeo_api_config.json with your credentials")
        print()
        print("Steps:")
        print("1. Go to https://developer.vimeo.com/apps")
        print("2. Create new app")
        print("3. Generate Access Token with scopes: upload, edit, video_files, private")
        print("4. Fill in vimeo_api_config.json")
        print()
        return False
    
    print("✅ API client initialized!")
    print()
    
    # Get user info
    print("Fetching user info...")
    user_info = uploader.get_user_info()
    
    if not user_info:
        print("❌ Failed to get user info")
        print("⚠️ Check your access token and scopes")
        return False
    
    print("✅ User info retrieved!")
    print()
    print("-" * 60)
    print(f"👤 User: {user_info['name']}")
    print(f"🔗 Profile: {user_info['link']}")
    print(f"💾 Total Quota: {user_info['quota_total_mb']:.1f} MB")
    print(f"📊 Used: {user_info['quota_used_mb']:.1f} MB ({user_info['quota_percent']:.1f}%)")
    print(f"✅ Free: {user_info['quota_free_mb']:.1f} MB")
    print("-" * 60)
    print()
    
    if user_info['quota_free_mb'] < 10:
        print("⚠️ WARNING: Low quota! Less than 10 MB free")
        print("   Consider deleting old videos or upgrading account")
        print()
    
    print("🎉 API is ready to use!")
    print()
    print("Next steps:")
    print("1. Use VimeoAPIUploader in your code")
    print("2. Call upload_video() to upload videos")
    print("3. Enjoy 10x faster uploads!")
    print()
    
    return True


def test_upload_sample():
    """Test upload with a sample video (if available)"""
    print("=" * 60)
    print("Testing Sample Upload")
    print("=" * 60)
    print()
    
    # Look for sample video
    sample_paths = [
        "sample_video.mp4",
        "test_video.mp4",
        "video.mp4"
    ]
    
    sample_video = None
    for path in sample_paths:
        if os.path.exists(path):
            sample_video = path
            break
    
    if not sample_video:
        print("⚠️ No sample video found")
        print("   To test upload, place a video file named 'sample_video.mp4' in this folder")
        print()
        return False
    
    print(f"📹 Found sample video: {sample_video}")
    print()
    
    uploader = VimeoAPIUploader()
    
    if not uploader.client:
        print("❌ API client not initialized")
        return False
    
    print("Starting upload test...")
    print()
    
    def log_callback(msg):
        print(f"  {msg}")
    
    success, message, data, quota_exceeded = uploader.upload_video(
        file_path=sample_video,
        title="Test Upload from WprTool",
        description="This is a test upload using Vimeo API",
        privacy="nobody",  # Private video
        log_callback=log_callback
    )
    
    print()
    
    if success:
        print("✅ Upload successful!")
        print()
        print("-" * 60)
        print(f"🎬 Video ID: {data['video_id']}")
        print(f"🔗 Link: {data['video_link']}")
        print(f"📝 Title: {data['title']}")
        if data.get('thumbnail'):
            print(f"🖼️ Thumbnail: {data['thumbnail']}")
        print("-" * 60)
        print()
        print("Embed code:")
        print(data['embed_code'][:100] + "...")
        print()
        return True
    else:
        print(f"❌ Upload failed: {message}")
        if quota_exceeded:
            print("⚠️ Quota exceeded - delete old videos or upgrade account")
        print()
        return False


if __name__ == "__main__":
    # Test 1: Connection
    connection_ok = test_api_connection()
    
    if not connection_ok:
        print("❌ Connection test failed. Fix the issues above and try again.")
        sys.exit(1)
    
    # Test 2: Upload (optional)
    print()
    response = input("Do you want to test upload with a sample video? (y/n): ")
    
    if response.lower() == 'y':
        print()
        upload_ok = test_upload_sample()
        
        if upload_ok:
            print("🎉 All tests passed!")
            sys.exit(0)
        else:
            print("⚠️ Upload test failed, but connection is OK")
            sys.exit(1)
    else:
        print()
        print("✅ Connection test passed!")
        print("   You can now use Vimeo API in your tool")
        sys.exit(0)
