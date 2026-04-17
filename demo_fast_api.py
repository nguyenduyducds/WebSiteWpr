"""
DEMO: Ultra-Fast WordPress API Posting
Target: 1 second per API call

Usage:
1. Update your credentials below
2. Run: python demo_fast_api.py
3. Watch the speed!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model.wp_model import BlogPost, WPFastClient
from model.wp_rest_api_fast import WordPressBatchProcessor
import time


def demo_single_post_fast():
    """
    Demo: Single post with ultra-fast mode
    Target: < 2 seconds total
    """
    print("=" * 60)
    print("DEMO 1: SINGLE POST - ULTRA-FAST MODE")
    print("=" * 60)
    
    # TODO: Update these with your WordPress credentials
    SITE_URL = "https://your-site.com"
    USERNAME = "your-username"
    PASSWORD = "your-password"
    
    # Create a sample blog post
    blog_post = BlogPost(
        title="Test Post - Ultra Fast Mode",
        video_url="https://player.vimeo.com/video/123456789",
        image_url="",  # Optional: path to local image
        raw_content="<p>This is a test post created with ultra-fast mode!</p><p>Speed is everything.</p>"
    )
    
    # Generate content
    blog_post.generate_seo_content()
    
    # Create fast client
    client = WPFastClient(SITE_URL, USERNAME, PASSWORD)
    
    # Post article and measure time
    start_time = time.time()
    success, result = client.post_article(blog_post)
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"RESULT: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"URL: {result}")
    print("=" * 60)
    
    client.close()


def demo_batch_posts_fast():
    """
    Demo: Multiple posts in parallel
    Target: 3 posts in < 5 seconds
    """
    print("\n" + "=" * 60)
    print("DEMO 2: BATCH POSTS - PARALLEL PROCESSING")
    print("=" * 60)
    
    # TODO: Update these with your WordPress credentials
    SITE_URL = "https://your-site.com"
    USERNAME = "your-username"
    PASSWORD = "your-password"
    
    # Create multiple blog posts
    blog_posts = []
    for i in range(3):
        blog_post = BlogPost(
            title=f"Batch Test Post #{i+1}",
            video_url="https://player.vimeo.com/video/123456789",
            raw_content=f"<p>This is batch post #{i+1} created in parallel!</p>"
        )
        blog_post.generate_seo_content()
        blog_posts.append(blog_post)
    
    # Create batch processor
    processor = WordPressBatchProcessor(
        SITE_URL, 
        USERNAME, 
        PASSWORD,
        max_workers=3  # Process 3 posts in parallel
    )
    
    # Post articles and measure time
    start_time = time.time()
    results = processor.post_articles_parallel(blog_posts)
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"BATCH RESULT:")
    for i, (success, result) in enumerate(results):
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  Post #{i+1}: {status} - {result}")
    print(f"\nTotal Time: {total_time:.2f} seconds")
    print(f"Average Time per Post: {total_time/len(blog_posts):.2f} seconds")
    print("=" * 60)


def demo_reuse_client():
    """
    Demo: Reuse client for multiple posts (fastest method)
    Target: < 1 second per post (after first login)
    """
    print("\n" + "=" * 60)
    print("DEMO 3: REUSE CLIENT - MAXIMUM SPEED")
    print("=" * 60)
    
    # TODO: Update these with your WordPress credentials
    SITE_URL = "https://your-site.com"
    USERNAME = "your-username"
    PASSWORD = "your-password"
    
    # Create fast client wrapper
    wp_client = WPFastClient(SITE_URL, USERNAME, PASSWORD)
    
    # Post multiple articles reusing the same client
    for i in range(3):
        blog_post = BlogPost(
            title=f"Reuse Client Test #{i+1}",
            video_url="https://player.vimeo.com/video/123456789",
            raw_content=f"<p>This is post #{i+1} using reused client!</p>"
        )
        blog_post.generate_seo_content()
        
        # Reuse the underlying client
        start_time = time.time()
        success, result = wp_client.post_article(
            blog_post, 
            reuse_client=wp_client.get_client()
        )
        total_time = time.time() - start_time
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"\nPost #{i+1}: {status}")
        print(f"  Time: {total_time:.2f} seconds")
        print(f"  URL: {result}")
    
    wp_client.close()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║  WORDPRESS ULTRA-FAST API DEMO                          ║
║  Target: 1 second per API call                          ║
╚══════════════════════════════════════════════════════════╝

⚠️  IMPORTANT: Update credentials in this file before running!

Available demos:
1. Single post (ultra-fast mode)
2. Batch posts (parallel processing)
3. Reuse client (maximum speed)

""")
    
    choice = input("Select demo (1-3) or 'all' to run all demos: ").strip()
    
    if choice == "1":
        demo_single_post_fast()
    elif choice == "2":
        demo_batch_posts_fast()
    elif choice == "3":
        demo_reuse_client()
    elif choice.lower() == "all":
        demo_single_post_fast()
        demo_batch_posts_fast()
        demo_reuse_client()
    else:
        print("Invalid choice. Please run again and select 1, 2, 3, or 'all'")
