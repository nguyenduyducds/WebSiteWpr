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
import threading

# GLOBAL UPLOAD LIMITER: Configurable based on volume
# Default: 5 for normal use, 15 for high volume (200+ posts)
_upload_semaphore = threading.Semaphore(15)  # Increased for HIGH VOLUME mode


class WordPressRESTClientFast:
    """
    Ultra-fast WordPress REST API client
    Optimized for speed - target 1 second per request
    """
    
    def __init__(self, site_url, username, password, enable_rate_limiting=False, verbose=True):
        """
        Initialize WordPress REST API client with speed optimizations
        
        Args:
            site_url: WordPress site URL (e.g., "https://example.com")
            username: WordPress username
            password: WordPress password or application password
            enable_rate_limiting: Enable rate limiting for high volume (200+) requests (default: False for max speed)
            verbose: Enable detailed logging (default: True). Set to False for 5-10% speed boost
        """
        self.site_url = site_url.rstrip('/')
        if not self.site_url.startswith('http'):
            self.site_url = 'https://' + self.site_url
        
        # Remove /wp-admin if present
        if '/wp-admin' in self.site_url:
            self.site_url = self.site_url.split('/wp-admin')[0]
        
        self.username = username
        self.password = password
        self.verbose = verbose
        
        # SPEED OPTIMIZATION: Create session with connection pooling
        self.session = self._create_optimized_session()
        
        self.nonce = None
        self.cookies_loaded = False
        
        # Rate limiting for high volume requests (OPTIONAL - disabled by default for speed)
        self.enable_rate_limiting = enable_rate_limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum 100ms between requests
        self.request_count = 0
        
        # REST API endpoints
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.posts_endpoint = f"{self.api_base}/posts"
        self.media_endpoint = f"{self.api_base}/media"
        
        if verbose:
            if enable_rate_limiting:
                print(f"[FAST_API] 🚀 Initialized FAST mode (HIGH VOLUME) for: {self.site_url}")
            else:
                print(f"[FAST_API] ⚡ Initialized ULTRA-FAST mode (NO LIMITS) for: {self.site_url}")
    
    def _create_optimized_session(self):
        """
        Create optimized session with connection pooling and retries
        OPTIMIZED FOR HIGH VOLUME (200+ requests)
        """
        session = requests.Session()
        
        # HIGH VOLUME OPTIMIZATION: Larger connection pool for 200+ requests
        adapter = HTTPAdapter(
            pool_connections=50,   # Increased from 10 - more connection pools
            pool_maxsize=100,      # Increased from 20 - handle 200+ concurrent requests
            max_retries=Retry(
                total=5,           # Increased from 2 - more retries for reliability
                backoff_factor=0.3,  # Increased from 0.1 - better backoff for server load
                status_forcelist=[429, 500, 502, 503, 504],  # Added 429 (Too Many Requests)
                raise_on_status=False  # Don't raise exception, let us handle it
            )
        )
        
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # SPEED HACK 1: Enable compression (gzip/deflate)
        session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Encoding': 'gzip, deflate, br',  # Enable compression
            'Accept': 'application/json',  # Prefer JSON responses
        })
        
        # SPEED HACK 2: Disable SSL verification for local/dev (ONLY if needed)
        # session.verify = False  # Uncomment ONLY for local development
        
        return session
    
    def _log(self, message):
        """Helper to log only when verbose is enabled (SPEED HACK 4)"""
        if self.verbose:
            print(message)
    
    def _wait_for_rate_limit(self):
        """
        Rate limiting: Wait if needed to avoid overwhelming server
        Prevents 429 (Too Many Requests) errors
        ONLY ACTIVE when enable_rate_limiting=True
        """
        if not self.enable_rate_limiting:
            return  # Skip rate limiting for max speed
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Every 50 requests, add a longer pause to let server breathe
        if self.request_count % 50 == 0:
            print(f"[FAST_API] ⏸️ Pause after {self.request_count} requests...")
            time.sleep(1.0)  # 1 second pause every 50 requests
    
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
                # CRITICAL: Extract nonce for REST API access with cookies
                self._extract_nonce()
                return True
            
            print("[FAST_API] ❌ Login failed")
            return False
                
        except Exception as e:
            print(f"[FAST_API] ❌ Login error: {e}")
            return False

    def _extract_nonce(self):
        """Extract WordPress nonce from dashboard - Critical for Cookie Auth"""
        try:
            # SPEED HACK 3: Skip if we already have a valid nonce (saves 1 request)
            if self.nonce:
                print(f"[FAST_API] ✅ Using cached nonce: {self.nonce[:10]}...")
                return True
            
            print("[FAST_API] Extracting nonce from dashboard...")
            dashboard_url = f"{self.site_url}/wp-admin/"
            response = self.session.get(dashboard_url, timeout=10)
            
            # Match wpApiSettings.nonce
            match = re.search(r'wpApiSettings["\']?\s*[=:]\s*\{[^}]*["\']nonce["\']\s*:\s*["\']([a-zA-Z0-9]+)["\']', response.text)
            if match:
                self.nonce = match.group(1)
                print(f"[FAST_API] ✅ Found nonce: {self.nonce[:10]}...")
                return True
                
            # Fallback patterns
            match = re.search(r'["\']nonce["\']\s*:\s*["\']([a-zA-Z0-9]+)["\']', response.text)
            if match:
                self.nonce = match.group(1)
                print(f"[FAST_API] ✅ Found nonce (fallback): {self.nonce[:10]}...")
                return True
                
            print("[FAST_API] ⚠️ Could not extract nonce")
            return False
        except:
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
            
            # Rate limiting: Wait if needed
            self._wait_for_rate_limit()
            
            # GLOBAL RATE LIMIT: Acquire semaphore (max 5 uploads system-wide)
            # This prevents overwhelming WordPress when running multiple posts in parallel
            with _upload_semaphore:
                self._log(f"[FAST_API] 🔒 Acquired upload slot (max 5 concurrent)")
                
                # HIGH VOLUME: Retry logic with exponential backoff
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # HIGH VOLUME: Increased timeout to 60s (was 30s) for parallel stability
                        response = self.session.post(
                            self.media_endpoint,
                            headers=headers,
                            data=file_data,
                            timeout=60  # Increased from 30s for parallel posts
                        )
                        
                        if response.status_code in [200, 201]:
                            data = response.json()
                            media_id = data.get('id')
                            media_url = data.get('source_url')
                            
                            print(f"[FAST_API] ✅ Upload done! ID: {media_id}")
                            return True, media_id, media_url
                        elif response.status_code == 429:  # Too Many Requests
                            if attempt < max_retries - 1:
                                wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                                print(f"[FAST_API] ⚠️ Rate limited (429), waiting {wait_time}s... (attempt {attempt+1}/{max_retries})")
                                time.sleep(wait_time)
                                continue
                            else:
                                print(f"[FAST_API] ❌ Upload failed: Rate limited after {max_retries} attempts")
                                return False, None, None
                        else:
                            print(f"[FAST_API] ❌ Upload failed: {response.status_code}")
                            if attempt < max_retries - 1:
                                time.sleep(1)  # Wait 1s before retry
                                continue
                            return False, None, None
                            
                    except requests.exceptions.Timeout:
                        if attempt < max_retries - 1:
                            print(f"[FAST_API] ⚠️ Timeout, retrying... (attempt {attempt+1}/{max_retries})")
                            time.sleep(2)
                            continue
                        else:
                            print(f"[FAST_API] ❌ Upload timeout after {max_retries} attempts")
                            return False, None, None
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"[FAST_API] ⚠️ Error: {e}, retrying...")
                            time.sleep(1)
                            continue
                        else:
                            print(f"[FAST_API] ❌ Upload error: {e}")
                            return False, None, None

            
            return False, None, None
                
        except Exception as e:
            print(f"[FAST_API] ❌ Upload error: {e}")
            return False, None, None
    
    def upload_images_parallel(self, image_paths, max_workers=3):
        """
        PARALLEL IMAGE UPLOAD - Upload multiple images simultaneously
        SPEED BOOST: 2-3x faster than sequential upload (optimized for stability)
        
        Args:
            image_paths: List of image file paths
            max_workers: Number of parallel workers (default: 3, reduced from 10 for stability)
            
        Returns:
            list: List of tuples (success, media_id, media_url) for each image
        """
        if not image_paths:
            return []
        
        self._log(f"[FAST_API] 🚀 Parallel uploading {len(image_paths)} images with {max_workers} workers...")
        
        results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all upload tasks
            future_to_path = {
                executor.submit(self.upload_image_fast, path): path 
                for path in image_paths
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self._log(f"[FAST_API] ❌ Parallel upload error for {path}: {e}")
                    results.append((False, None, None))
        
        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if r[0])
        self._log(f"[FAST_API] ✅ Parallel upload done: {success_count}/{len(image_paths)} in {elapsed:.2f}s")
        
        return results
    
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
            
            # Rate limiting: Wait if needed
            self._wait_for_rate_limit()
            
            # HIGH VOLUME: Retry logic with exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # HIGH VOLUME: Increased timeout to 20s (was 10s) for better reliability
                    response = self.session.post(
                        self.posts_endpoint,
                        json=post_data,
                        headers=headers,
                        timeout=20  # Increased from 10s for high volume
                    )
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        post_id = data.get('id')
                        post_url = data.get('link')
                        
                        print(f"[FAST_API] ✅ Post created! URL: {post_url}")
                        return True, post_id, post_url
                    elif response.status_code == 429:  # Too Many Requests
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                            print(f"[FAST_API] ⚠️ Rate limited (429), waiting {wait_time}s... (attempt {attempt+1}/{max_retries})")
                            time.sleep(wait_time)
                            continue
                        else:
                            print(f"[FAST_API] ❌ Post failed: Rate limited after {max_retries} attempts")
                            return False, None, None
                    else:
                        print(f"[FAST_API] ❌ Post failed: {response.status_code}")
                        if attempt < max_retries - 1:
                            time.sleep(1)  # Wait 1s before retry
                            continue
                        return False, None, None
                        
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        print(f"[FAST_API] ⚠️ Timeout, retrying... (attempt {attempt+1}/{max_retries})")
                        time.sleep(2)
                        continue
                    else:
                        print(f"[FAST_API] ❌ Post timeout after {max_retries} attempts")
                        return False, None, None
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"[FAST_API] ⚠️ Error: {e}, retrying...")
                        time.sleep(1)
                        continue
                    else:
                        print(f"[FAST_API] ❌ Post error: {e}")
                        return False, None, None
            
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
    
    def set_rate_limiting(self, enabled):
        """
        Enable or disable rate limiting dynamically
        
        Args:
            enabled: True to enable rate limiting (for 200+ requests), False for max speed
        """
        self.enable_rate_limiting = enabled
        if enabled:
            print("[FAST_API] 🚀 Rate limiting ENABLED (High Volume mode)")
        else:
            print("[FAST_API] ⚡ Rate limiting DISABLED (Ultra-Fast mode)")
    
    # Aliases for compatibility with standard WordPressRESTClient
    def upload_image(self, image_path):
        return self.upload_image_fast(image_path)

    def create_post(self, title, content, featured_media_id=None, status='publish', categories=None, tags=None):
        # Note: categories and tags ignored in fast mode for now, can be added if needed
        return self.create_post_fast(title, content, featured_media_id, status)

    def post_article(self, blog_post):
        return self.post_article_fast(blog_post)
    
    def test_api_availability(self, aggressive=True):
        # Override to match signature but keep aggressive default
        return super().test_api_availability(aggressive) if hasattr(super(), 'test_api_availability') else (True, 200, "Aggressive mode")


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
