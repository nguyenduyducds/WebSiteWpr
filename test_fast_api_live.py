import json
import time
import sys
import os

# Add model to path
sys.path.append(os.getcwd())

from model.wp_rest_api_fast import WordPressRESTClientFast
from model.wp_model import BlogPost

def test_live_speed():
    print("🚀 STARTING LIVE SPEED TEST...")
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            
        site_url = config.get('site_url')
        username = config.get('username')
        password = config.get('password')
        
        print(f"Target: {site_url}")
        print(f"User: {username}")
        
        if not site_url or not username or not password:
            print("❌ Config missing credentials")
            return
            
    except Exception as e:
        print(f"❌ Could not load config: {e}")
        return

    # Initialize Fast Client
    print("\n1. Initializing Client...")
    start_init = time.time()
    client = WordPressRESTClientFast(site_url, username, password)
    print(f"   ⏱️ Init time: {time.time() - start_init:.4f}s")
    
    # Create Test Post
    blog_post = BlogPost(
        title=f"Speed Test {int(time.time())}",
        raw_content="<p>This is a speed test of the optimized REST API client.</p>",
        video_url="",
        image_url=""
    )
    blog_post.generate_seo_content()
    
    # Measure Post Time
    print("\n2. Posting Article...")
    start_post = time.time()
    success, result = client.post_article_fast(blog_post)
    end_post = time.time()
    
    duration = end_post - start_post
    
    if success:
        print(f"\n✅ SUCCESS!")
        print(f"   🔗 URL: {result}")
        print(f"   ⏱️ POST DURATION: {duration:.4f} seconds")
        
        if duration < 2.0:
            print("   🚀 RESULT: EXTREMELY FAST (< 2s)")
        elif duration < 5.0:
            print("   ⚡ RESULT: FAST (< 5s)")
        else:
            print("   🐢 RESULT: SLOW (> 5s)")
    else:
        print(f"\n❌ FAILED: {result}")

    client.close()

if __name__ == "__main__":
    test_live_speed()
