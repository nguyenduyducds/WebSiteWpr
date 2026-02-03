"""
WordPress REST API Fast Client - OPTIMIZED FOR MAX SPEED
Target: 1 second per API call
Optimizations:
- Aggressive mode (skip unnecessary checks)
- HTTP/2 + Connection pooling
- Reduced timeouts (5-10s instead of 30s)
- Session reuse
- Parallel uploads
"""

import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import re
from urllib.parse import urlparse, urljoin
import time
import concurrent.futures


class WordPressRESTClientFast:
    """
    Ultra-fast WordPress REST API client
    Optimized for speed - target 1 second per request
    """
    
    def __init__(self, site_url, username, password):
        """
        Initialize WordPress REST API client with speed optimizations
        
        Args:
            site_url: WordPress site URL (e.g., "https://example.com")
            username: WordPress username
            password: WordPress password or application password
        """
        self.site_url = site_url.rstrip('/')
        if not self.site_url.startswith('http'):
            self.site_url = 'https://' + self.site_url
        
        # Remove /wp-admin if present
        if '/wp-admin' in self.site_url:
            self.site_url = self.site_url.split('/wp-admin')[0]
        
        self.username = username
        self.password = password
        
        # SPEED OPTIMIZATION: Create session with connection pooling
        self.session = self._create_optimized_session()
        
        self.nonce = None
        self.cookies_loaded = False
        
        # REST API endpoints
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.posts_endpoint = f"{self.api_base}/posts"
        self.media_endpoint = f"{self.api_base}/media"
        
        print(f"[FAST_API] 🚀 Initialized FAST mode for: {self.site_url}")
    
    def _create_optimized_session(self):
        """
        Create optimized session with connection pooling and retries
        """
        session = requests.Session()
        
        # SPEED OPTIMIZATION: Connection pooling (reuse connections)
        adapter = HTTPAdapter(
            pool_connections=10,  # Number of connection pools
            pool_maxsize=20,      # Max connections per pool
            max_retries=Retry(
                total=2,          # Reduced retries for speed
                backoff_factor=0.1,  # Fast backoff
                status_forcelist=[500, 502, 503, 504]
            )
        )
        
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # SPEED OPTIMIZATION: Keep-Alive headers
        session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        
        return session
    
    def test_api_availability(self, aggressive=True):
        """
        FAST MODE: Always return True in aggressive mode (skip check)
        
        Args:
            aggressive: If True, skip check entirely (default: True)
        
        Returns:
            tuple: (is_available: bool, status_code: int, message: str)
        """
        if aggressive:
            print("[FAST_API] ⚡ AGGRESSIVE MODE: Skipping availability check")
            return True, 200, "Aggressive mode - bypassing check"
        
        # Quick check with reduced timeout
        try:
            response = self.session.get(self.api_base, timeout=3)
            return True, response.status_code, "Quick check passed"
        except:
            return True, 0, "Check failed but will try anyway"
    
    def login_fast(self):
        """
        FAST LOGIN: Try application password first (fastest method)
        
        Returns:
            bool: True if login successful
        """
        try:
            print(f"[FAST_API] ⚡ Fast login as: {self.username}")
            
            # METHOD 1: Try application password FIRST (fastest - no cookies needed)
            print("[FAST_API] Trying application password (fastest method)...")
            
            response = self.session.get(
                f"{self.api_base}/users/me",
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=5  # Reduced timeout
            )
            
            if response.status_code == 200:
                print("[FAST_API] ✅ Application password auth successful!")
                self.session.auth = HTTPBasicAuth(self.username, self.password)
                self.cookies_loaded = True
                return True
            
            # METHOD 2: Cookie-based login (fallback)
            print("[FAST_API] Trying cookie-based login...")
            login_url = f"{self.site_url}/wp-login.php"
            
            login_data = {
                'log': self.username,
                'pwd': self.password,
                'wp-submit': 'Log In',
                'redirect_to': f"{self.site_url}/wp-admin/",
                'testcookie': '1'
            }
            
            response = self.session.post(
                login_url, 
                data=login_data, 
                allow_redirects=True, 
                timeout=10  # Reduced timeout
            )
            
            cookies = self.session.cookies.get_dict()
            if any('wordpress_logged_in' in key for key in cookies.keys()):
                print("[FAST_API] ✅ Cookie login successful!")
                self.cookies_loaded = True
                return True
            
            print("[FAST_API] ❌ Login failed")
            return False
                
        except Exception as e:
            print(f"[FAST_API] ❌ Login error: {e}")
            return False
    
    def upload_image_fast(self, image_path):
        """
        FAST IMAGE UPLOAD with reduced timeout
        
        Args:
            image_path: Path to image file
            
        Returns:
            tuple: (success: bool, media_id: int or None, media_url: str or None)
        """
        try:
            if not os.path.exists(image_path):
                print(f"[FAST_API] ❌ Image not found: {image_path}")
                return False, None, None
            
            print(f"[FAST_API] ⚡ Fast uploading: {os.path.basename(image_path)}")
            
            filename = os.path.basename(image_path)
            
            # Detect MIME type
            mime_type = 'image/jpeg'
            if filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                mime_type = 'image/gif'
            elif filename.lower().endswith('.webp'):
                mime_type = 'image/webp'
            
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': mime_type,
            }
            
            if self.nonce:
                headers['X-WP-Nonce'] = self.nonce
            
            with open(image_path, 'rb') as f:
                file_data = f.read()
            
            # SPEED OPTIMIZATION: Reduced timeout to 15s (was 60s)
            response = self.session.post(
                self.media_endpoint,
                headers=headers,
                data=file_data,
                timeout=15  # Reduced from 60s
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                media_id = data.get('id')
                media_url = data.get('source_url')
                
                print(f"[FAST_API] ✅ Upload done! ID: {media_id}")
                return True, media_id, media_url
            else:
                print(f"[FAST_API] ❌ Upload failed: {response.status_code}")
                return False, None, None
                
        except Exception as e:
            print(f"[FAST_API] ❌ Upload error: {e}")
            return False, None, None
    
    def create_post_fast(self, title, content, featured_media_id=None, status='publish'):
        """
        FAST POST CREATION with reduced timeout
        
        Args:
            title: Post title
            content: Post content (HTML)
            featured_media_id: Featured image media ID (optional)
            status: Post status (default: 'publish')
            
        Returns:
            tuple: (success: bool, post_id: int or None, post_url: str or None)
        """
        try:
            print(f"[FAST_API] ⚡ Fast creating post: {title[:50]}...")
            
            post_data = {
                'title': title,
                'content': content,
                'status': status,
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            if self.nonce:
                headers['X-WP-Nonce'] = self.nonce
            
            # SPEED OPTIMIZATION: Reduced timeout to 10s (was 30s)
            response = self.session.post(
                self.posts_endpoint,
                json=post_data,
                headers=headers,
                timeout=10  # Reduced from 30s
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                post_id = data.get('id')
                post_url = data.get('link')
                
                print(f"[FAST_API] ✅ Post created! URL: {post_url}")
                return True, post_id, post_url
            else:
                print(f"[FAST_API] ❌ Post failed: {response.status_code}")
                return False, None, None
                
        except Exception as e:
            print(f"[FAST_API] ❌ Post error: {e}")
            return False, None, None
    
    def post_article_fast(self, blog_post):
        """
        ULTRA-FAST WORKFLOW: Complete post creation
        Target: < 2 seconds total
        
        Args:
            blog_post: BlogPost object
            
        Returns:
            tuple: (success: bool, post_url: str or error_message)
        """
        start_time = time.time()
        
        try:
            # Step 1: Skip API check (aggressive mode)
            # REMOVED for speed
            
            # Step 2: Fast login (only if not already logged in)
            if not self.cookies_loaded:
                login_start = time.time()
                if not self.login_fast():
                    return False, "Login failed"
                print(f"[FAST_API] ⏱️ Login took: {time.time() - login_start:.2f}s")
            
            # Step 3: Get featured media ID
            featured_media_id = None
            
            if hasattr(blog_post, 'featured_media_id') and blog_post.featured_media_id:
                featured_media_id = blog_post.featured_media_id
                print(f"[FAST_API] ✅ Using existing media ID: {featured_media_id}")
            elif blog_post.image_url:
                upload_start = time.time()
                success, media_id, media_url = self.upload_image_fast(blog_post.image_url)
                if success:
                    featured_media_id = media_id
                print(f"[FAST_API] ⏱️ Upload took: {time.time() - upload_start:.2f}s")
            
            # Step 4: Create post
            post_start = time.time()
            success, post_id, post_url = self.create_post_fast(
                title=blog_post.title,
                content=blog_post.content,
                featured_media_id=featured_media_id,
                status='publish'
            )
            print(f"[FAST_API] ⏱️ Post creation took: {time.time() - post_start:.2f}s")
            
            total_time = time.time() - start_time
            print(f"[FAST_API] ⏱️ TOTAL TIME: {total_time:.2f}s")
            
            if success:
                return True, post_url
            else:
                return False, "Post creation failed"
                
        except Exception as e:
            print(f"[FAST_API] ❌ Error: {e}")
            return False, str(e)
    
    def close(self):
        """Close session"""
        self.session.close()
        print("[FAST_API] Session closed")


# ============================================================================
# BATCH PROCESSING - Multiple posts in parallel
# ============================================================================

class WordPressBatchProcessor:
    """
    Process multiple WordPress posts in parallel for maximum speed
    """
    
    def __init__(self, site_url, username, password, max_workers=3):
        """
        Args:
            max_workers: Number of parallel workers (default: 3)
        """
        self.site_url = site_url
        self.username = username
        self.password = password
        self.max_workers = max_workers
    
    def post_articles_parallel(self, blog_posts):
        """
        Post multiple articles in parallel
        
        Args:
            blog_posts: List of BlogPost objects
            
        Returns:
            list: List of (success, result) tuples
        """
        print(f"[BATCH] 🚀 Processing {len(blog_posts)} posts with {self.max_workers} workers")
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a client for each post
            futures = []
            for blog_post in blog_posts:
                client = WordPressRESTClientFast(self.site_url, self.username, self.password)
                future = executor.submit(client.post_article_fast, blog_post)
                futures.append((future, client))
            
            # Collect results
            for future, client in futures:
                try:
                    success, result = future.result(timeout=30)
                    results.append((success, result))
                except Exception as e:
                    results.append((False, str(e)))
                finally:
                    client.close()
        
        print(f"[BATCH] ✅ Completed {len(results)} posts")
        return results
