"""
WordPress High Volume Uploader - Wrapper for BatchUploadManager
Tối ưu cho 200+ bài viết
"""

from model.batch_upload_manager import BatchUploadManager
from model.wp_rest_api_fast import WordPressRESTClientFast
from typing import List, Dict, Callable, Optional
import time


class WordPressHighVolumeUploader:
    """
    Upload hàng loạt bài viết lên WordPress với batch processing
    Tối ưu cho 200+ bài
    """
    
    def __init__(
        self,
        site_url: str,
        username: str,
        password: str,
        mode: str = "balanced"  # conservative, balanced, aggressive
    ):
        """
        Args:
            site_url: WordPress site URL
            username: WordPress username
            password: WordPress password
            mode: Upload mode (conservative/balanced/aggressive)
        """
        self.site_url = site_url
        self.username = username
        self.password = password
        
        # Configure based on mode
        if mode == "conservative":
            batch_size = 10
            max_parallel_batches = 2
            max_workers_per_batch = 3
        elif mode == "balanced":
            batch_size = 20
            max_parallel_batches = 3
            max_workers_per_batch = 5
        elif mode == "aggressive":
            batch_size = 50
            max_parallel_batches = 5
            max_workers_per_batch = 10
        else:
            raise ValueError(f"Invalid mode: {mode}. Use: conservative/balanced/aggressive")
        
        # Create batch manager
        self.batch_manager = BatchUploadManager(
            batch_size=batch_size,
            max_parallel_batches=max_parallel_batches,
            max_workers_per_batch=max_workers_per_batch
        )
        
        # Create WordPress client (reusable)
        self.wp_client = WordPressRESTClientFast(
            site_url=site_url,
            username=username,
            password=password,
            enable_rate_limiting=True,  # Enable for high volume
            verbose=False  # Disable verbose for speed
        )
        
        # Login once
        print(f"[HIGH_VOLUME] 🔐 Logging in to WordPress...")
        if not self.wp_client.login_fast():
            raise Exception("WordPress login failed!")
        
        print(f"[HIGH_VOLUME] ✅ Logged in successfully")
        print(f"[HIGH_VOLUME] 🚀 Mode: {mode.upper()}")
        print(f"[HIGH_VOLUME] 📦 Batch size: {batch_size}")
        print(f"[HIGH_VOLUME] ⚡ Parallel batches: {max_parallel_batches}")
    
    def upload_posts(
        self,
        blog_posts: List,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Upload hàng loạt blog posts
        
        Args:
            blog_posts: List of BlogPost objects
            progress_callback: Optional callback(completed, total, eta)
            
        Returns:
            dict: {
                'success_count': int,
                'failed_count': int,
                'failed_posts': list,
                'total_time': float,
                'posts_per_minute': float
            }
        """
        print(f"\n[HIGH_VOLUME] 📊 Starting upload of {len(blog_posts)} posts...")
        
        start_time = time.time()
        
        # Convert BlogPost objects to dicts
        posts_data = []
        for post in blog_posts:
            posts_data.append({
                'blog_post': post,
                'title': post.title if hasattr(post, 'title') else 'Untitled'
            })
        
        # Upload function wrapper
        def upload_single_post(post_data):
            """Upload a single post"""
            blog_post = post_data['blog_post']
            
            try:
                # Upload using WordPress client
                success, result = self.wp_client.post_article_fast(blog_post)
                
                if success:
                    return True, result  # result = post_url
                else:
                    return False, result  # result = error message
                    
            except Exception as e:
                return False, str(e)
        
        # Process with batch manager
        success_count, failed_count, failed_posts = self.batch_manager.process_posts_batch(
            posts=posts_data,
            upload_func=upload_single_post,
            progress_callback=progress_callback
        )
        
        # Calculate stats
        total_time = time.time() - start_time
        posts_per_minute = len(blog_posts) / (total_time / 60) if total_time > 0 else 0
        
        result = {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_posts': failed_posts,
            'total_time': total_time,
            'posts_per_minute': posts_per_minute
        }
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"[HIGH_VOLUME] ✅ UPLOAD COMPLETE!")
        print(f"{'='*60}")
        print(f"Success: {success_count}/{len(blog_posts)} ({success_count/len(blog_posts)*100:.1f}%)")
        print(f"Failed: {failed_count}")
        print(f"Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"Speed: {posts_per_minute:.1f} posts/minute")
        print(f"{'='*60}\n")
        
        return result
    
    def close(self):
        """Close WordPress client"""
        self.wp_client.close()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 WORDPRESS HIGH VOLUME UPLOADER - DEMO")
    print("=" * 60)
    print()
    
    # Mock BlogPost class
    class BlogPost:
        def __init__(self, title, content):
            self.title = title
            self.content = content
            self.image_url = None
    
    # Example: 200 posts
    test_posts = [
        BlogPost(f"Post {i}", f"<p>Content for post {i}</p>")
        for i in range(1, 201)
    ]
    
    # Create uploader
    uploader = WordPressHighVolumeUploader(
        site_url="https://your-site.com",
        username="admin",
        password="your-password",
        mode="balanced"  # conservative, balanced, aggressive
    )
    
    # Progress callback
    def progress_callback(completed, total, eta):
        print(f"[PROGRESS] {completed}/{total} ({completed/total*100:.1f}%) - ETA: {eta/60:.1f} min")
    
    # Upload
    result = uploader.upload_posts(
        test_posts,
        progress_callback=progress_callback
    )
    
    # Close
    uploader.close()
    
    print("\n✅ DEMO COMPLETE")
    print(f"Result: {result}")
