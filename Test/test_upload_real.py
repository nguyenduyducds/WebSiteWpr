"""
Test real video upload to Vimeo using API
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'model'))

from vimeo_api import VimeoAPIUploader

def test_upload():
    print("=" * 60)
    print("Test Vimeo API Upload")
    print("=" * 60)
    print()
    
    # Initialize uploader
    uploader = VimeoAPIUploader()
    
    if not uploader.client:
        print("❌ API not configured!")
        return False
    
    print("✅ API client ready!")
    print()
    
    # Get user info
    user_info = uploader.get_user_info()
    if user_info:
        print(f"👤 User: {user_info['name']}")
        print(f"🔗 Profile: {user_info['link']}")
        
        if user_info['quota_total_mb'] > 0:
            print(f"💾 Quota: {user_info['quota_free_mb']:.1f} MB free / {user_info['quota_total_mb']:.1f} MB total")
        else:
            print(f"💾 Quota: Free account (500 MB/week)")
        print()
    
    # Ask for video file
    print("Enter video file path to upload:")
    print("(Or press Enter to skip)")
    video_path = input("> ").strip()
    
    if not video_path:
        print()
        print("No video provided. Test skipped.")
        return True
    
    # Remove quotes if user copy-pasted path
    video_path = video_path.strip('"').strip("'")
    
    if not os.path.exists(video_path):
        print()
        print(f"❌ File not found: {video_path}")
        return False
    
    # Get video info
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    filename = os.path.basename(video_path)
    
    print()
    print(f"📹 File: {filename}")
    print(f"📦 Size: {file_size_mb:.1f} MB")
    print()
    
    # Confirm upload
    print("⚠️ This will upload the video to your Vimeo account!")
    confirm = input("Continue? (y/n): ")
    
    if confirm.lower() != 'y':
        print()
        print("Upload cancelled.")
        return True
    
    print()
    print("-" * 60)
    print("Starting upload...")
    print("-" * 60)
    print()
    
    # Progress callback
    def log_callback(msg):
        print(f"  {msg}")
    
    # Upload
    success, message, data, quota_exceeded = uploader.upload_video(
        file_path=video_path,
        title=f"Test Upload - {filename}",
        description="Test upload from WprTool using Vimeo API",
        privacy="nobody",  # Private video
        log_callback=log_callback
    )
    
    print()
    print("-" * 60)
    
    if success:
        print("✅ UPLOAD SUCCESSFUL!")
        print("-" * 60)
        print()
        print(f"🎬 Video ID: {data['video_id']}")
        print(f"🔗 Link: {data['video_link']}")
        print(f"📝 Title: {data['title']}")
        
        if data.get('thumbnail'):
            print(f"🖼️ Thumbnail: {data['thumbnail']}")
        
        print()
        print("Embed code:")
        print(data['embed_code'][:150] + "...")
        print()
        print("-" * 60)
        print()
        print("🎉 Test passed! Vimeo API is working perfectly!")
        print()
        print("Next steps:")
        print("1. Check video on Vimeo: " + data['video_link'])
        print("2. Integrate API into your tool")
        print("3. Enjoy 10x faster uploads!")
        
        return True
    else:
        print("❌ UPLOAD FAILED")
        print("-" * 60)
        print()
        print(f"Error: {message}")
        
        if quota_exceeded:
            print()
            print("⚠️ Quota exceeded!")
            print("Solutions:")
            print("1. Delete old videos from Vimeo")
            print("2. Wait for weekly quota reset")
            print("3. Upgrade to Vimeo Pro")
        
        return False

if __name__ == "__main__":
    try:
        success = test_upload()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print()
        print("❌ Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
