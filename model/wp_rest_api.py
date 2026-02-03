"""
WordPress REST API Direct Client
Bypasses Selenium/Gutenberg completely - uses Python requests to post directly
This is the MOST RELIABLE method when REST API is available
"""

import requests
from requests.auth import HTTPBasicAuth
import os
import re
from urllib.parse import urlparse, urljoin
import time


class WordPressRESTClient:
    """
    Direct WordPress REST API client using Python requests
    No Selenium, no Gutenberg, no JavaScript - just pure HTTP requests
    """
    
    def __init__(self, site_url, username, password):
        """
        Initialize WordPress REST API client
        
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
        self.session = requests.Session()
        self.nonce = None
        self.cookies_loaded = False
        
        # REST API endpoints
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.posts_endpoint = f"{self.api_base}/posts"
        self.media_endpoint = f"{self.api_base}/media"
        
        # EFFICIENCY & ROBUSTNESS: Add Connection Pooling and Retries
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        print(f"[REST_API] Initialized for: {self.site_url}")
        print(f"[REST_API] API Base: {self.api_base}")
    
    def test_api_availability(self, aggressive=False):
        """
        Test if WordPress REST API is available and not blocked
        
        Args:
            aggressive: If True, skip availability check and try anyway (bypass bot detection)
        
        Returns:
            tuple: (is_available: bool, status_code: int, message: str)
        """
        if aggressive:
            print("[REST_API] 🚀 AGGRESSIVE MODE: Skipping availability check, will try anyway")
            return True, 200, "Aggressive mode - bypassing check"
        
        try:
            print("[REST_API] Testing API availability...")
            response = self.session.get(self.api_base, timeout=10)
            
            if response.status_code == 200:
                print("[REST_API] ✅ REST API is available!")
                return True, 200, "REST API available"
            elif response.status_code == 403:
                print("[REST_API] ⚠️ REST API blocked (403) - will try aggressive mode")
                # Don't give up - try aggressive mode
                return True, 403, "REST API blocked but will try anyway"
            elif response.status_code == 404:
                print("[REST_API] ⚠️ REST API not found (404) - will try alternative endpoints")
                return True, 404, "REST API not found but will try anyway"
            else:
                print(f"[REST_API] ⚠️ Unexpected status: {response.status_code} - will try anyway")
                return True, response.status_code, f"Unexpected status but will try anyway"
                
        except requests.exceptions.RequestException as e:
            print(f"[REST_API] ⚠️ Connection error: {e} - will try anyway")
            # Don't give up on connection errors - might be temporary
            return True, 0, f"Connection error but will try anyway"
    
    def login(self):
        """
        Login to WordPress and get authentication cookies + nonce
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            print(f"[REST_API] Logging in as: {self.username}")
            
            # Method 1: Try cookie-based authentication (most reliable)
            login_url = f"{self.site_url}/wp-login.php"
            
            # Add headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': self.site_url,
                'Origin': self.site_url,
            }
            
            login_data = {
                'log': self.username,
                'pwd': self.password,
                'wp-submit': 'Log In',
                'redirect_to': f"{self.site_url}/wp-admin/",
                'testcookie': '1'
            }
            
            response = self.session.post(login_url, data=login_data, headers=headers, allow_redirects=True, timeout=30)
            
            # Check if login successful - multiple methods
            cookies = self.session.cookies.get_dict()
            
            # Check 1: wordpress_logged_in cookie
            if any('wordpress_logged_in' in key for key in cookies.keys()):
                print("[REST_API] ✅ Login successful (cookie-based)")
                self.cookies_loaded = True
                
                # Get nonce from dashboard
                self._extract_nonce()
                return True
            
            # Check 2: Check if we're redirected to wp-admin
            if 'wp-admin' in response.url:
                print("[REST_API] ✅ Login successful (redirected to wp-admin)")
                self.cookies_loaded = True
                self._extract_nonce()
                return True
            
            # Check 3: Look for login error
            if 'login_error' in response.text or 'incorrect' in response.text.lower():
                print("[REST_API] ❌ Login failed: Invalid username or password")
                return False
            
            print("[REST_API] ⚠️ Cookie login uncertain, trying application password...")
            
            # Method 2: Try application password (HTTP Basic Auth)
            return self._try_application_password()
                
        except Exception as e:
            print(f"[REST_API] ❌ Login failed: {e}")
            return False
    
    def _try_application_password(self):
        """
        Try authentication using application password (HTTP Basic Auth)
        
        Returns:
            bool: True if successful
        """
        try:
            print("[REST_API] Trying application password authentication...")
            
            # Test with a simple GET request
            response = self.session.get(
                f"{self.api_base}/users/me",
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=10
            )
            
            if response.status_code == 200:
                print("[REST_API] ✅ Application password authentication successful")
                # Store auth for future requests
                self.session.auth = HTTPBasicAuth(self.username, self.password)
                return True
            else:
                print(f"[REST_API] ❌ Application password failed: {response.status_code}")
                print(f"[REST_API] Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"[REST_API] Application password error: {e}")
            return False
    
    def _extract_nonce(self):
        """
        Extract WordPress nonce from dashboard page
        """
        try:
            print("[REST_API] Extracting nonce from dashboard...")
            dashboard_url = f"{self.site_url}/wp-admin/"
            response = self.session.get(dashboard_url)
            
            # Try to find nonce in page source
            # Pattern 1: wpApiSettings.nonce
            match = re.search(r'"nonce":"([a-f0-9]+)"', response.text)
            if match:
                self.nonce = match.group(1)
                print(f"[REST_API] ✅ Found nonce: {self.nonce[:20]}...")
                return True
            
            # Pattern 2: _wpnonce hidden field
            match = re.search(r'name="_wpnonce"\s+value="([^"]+)"', response.text)
            if match:
                self.nonce = match.group(1)
                print(f"[REST_API] ✅ Found nonce from field: {self.nonce[:20]}...")
                return True
            
            print("[REST_API] ⚠️ Could not extract nonce (will try without it)")
            return False
            
        except Exception as e:
            print(f"[REST_API] Nonce extraction error: {e}")
            return False
    
    def upload_image(self, image_path):
        """
        Upload image to WordPress Media Library
        
        Args:
            image_path: Path to image file
            
        Returns:
            tuple: (success: bool, media_id: int or None, media_url: str or None)
        """
        try:
            if not os.path.exists(image_path):
                print(f"[REST_API] ❌ Image not found: {image_path}")
                return False, None, None
            
            print(f"[REST_API] Uploading image: {os.path.basename(image_path)}")
            
            # Prepare file
            filename = os.path.basename(image_path)
            
            # Detect MIME type
            mime_type = 'image/jpeg'
            if filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                mime_type = 'image/gif'
            elif filename.lower().endswith('.webp'):
                mime_type = 'image/webp'
            
            # Prepare headers - CRITICAL: Add all authentication headers
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': mime_type,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
            
            # Add nonce if available (from Selenium)
            if self.nonce:
                headers['X-WP-Nonce'] = self.nonce
                print(f"[REST_API] Using nonce: {self.nonce[:20]}...")
            
            # Method 1: Try with cookies + nonce (most reliable for admin)
            with open(image_path, 'rb') as f:
                file_data = f.read()
            
            response = self.session.post(
                self.media_endpoint,
                headers=headers,
                data=file_data,
                timeout=60
            )
            
            # If 401 error, try with HTTP Basic Auth as fallback
            if response.status_code == 401 and hasattr(self.session, 'auth') and self.session.auth:
                print(f"[REST_API] Cookie auth failed, trying HTTP Basic Auth...")
                response = self.session.post(
                    self.media_endpoint,
                    headers=headers,
                    data=file_data,
                    auth=self.session.auth,
                    timeout=60
                )
            
            if response.status_code in [200, 201]:
                data = response.json()
                media_id = data.get('id')
                media_url = data.get('source_url')
                
                print(f"[REST_API] ✅ Image uploaded successfully!")
                print(f"[REST_API] Media ID: {media_id}")
                print(f"[REST_API] Media URL: {media_url}")
                
                return True, media_id, media_url
            else:
                print(f"[REST_API] ❌ Upload failed: {response.status_code}")
                print(f"[REST_API] Response: {response.text[:500]}")
                return False, None, None
                
        except Exception as e:
            print(f"[REST_API] ❌ Upload error: {e}")
            import traceback
            traceback.print_exc()
            return False, None, None
    
    def create_post(self, title, content, featured_media_id=None, status='publish', categories=None, tags=None):
        """
        Create a new WordPress post
        
        Args:
            title: Post title
            content: Post content (HTML)
            featured_media_id: Featured image media ID (optional)
            status: Post status ('publish', 'draft', 'pending', etc.)
            categories: List of category IDs (optional)
            tags: List of tag IDs (optional)
            
        Returns:
            tuple: (success: bool, post_id: int or None, post_url: str or None)
        """
        try:
            print(f"[REST_API] Creating post: {title[:50]}...")
            
            # Prepare post data
            post_data = {
                'title': title,
                'content': content,
                'status': status,
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
                print(f"[REST_API] Setting featured image: {featured_media_id}")
            
            if categories:
                post_data['categories'] = categories
            
            if tags:
                post_data['tags'] = tags
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
            }
            
            if self.nonce:
                headers['X-WP-Nonce'] = self.nonce
            
            # Create post
            response = self.session.post(
                self.posts_endpoint,
                json=post_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                post_id = data.get('id')
                post_url = data.get('link')
                
                print(f"[REST_API] ✅ Post created successfully!")
                print(f"[REST_API] Post ID: {post_id}")
                print(f"[REST_API] Post URL: {post_url}")
                
                # VERIFY: Check if featured_media was actually set
                actual_featured_media = data.get('featured_media')
                if actual_featured_media:
                    print(f"[REST_API] ✅ VERIFIED: Featured media in response: {actual_featured_media}")
                    if featured_media_id and actual_featured_media != featured_media_id:
                        print(f"[REST_API] ⚠️ WARNING: Featured media mismatch!")
                        print(f"[REST_API]   Expected: {featured_media_id}")
                        print(f"[REST_API]   Got: {actual_featured_media}")
                        
                        # FORCE UPDATE: Update featured_media again
                        print(f"[REST_API] 🔄 Force updating featured_media to {featured_media_id}...")
                        try:
                            update_response = self.session.post(
                                f"{self.posts_endpoint}/{post_id}",
                                json={"featured_media": featured_media_id},
                                headers=headers,
                                timeout=30
                            )
                            if update_response.status_code in [200, 201]:
                                print(f"[REST_API] ✅ Featured media force updated successfully!")
                            else:
                                print(f"[REST_API] ⚠️ Failed to force update featured media: {update_response.status_code}")
                        except Exception as update_err:
                            print(f"[REST_API] ⚠️ Error force updating featured media: {update_err}")
                else:
                    print(f"[REST_API] ⚠️ WARNING: No featured_media in response!")
                    if featured_media_id:
                        print(f"[REST_API]   Expected featured_media: {featured_media_id}")
                        
                        # FORCE SET: Set featured_media via update
                        print(f"[REST_API] 🔄 Force setting featured_media to {featured_media_id}...")
                        try:
                            update_response = self.session.post(
                                f"{self.posts_endpoint}/{post_id}",
                                json={"featured_media": featured_media_id},
                                headers=headers,
                                timeout=30
                            )
                            if update_response.status_code in [200, 201]:
                                print(f"[REST_API] ✅ Featured media force set successfully!")
                            else:
                                print(f"[REST_API] ⚠️ Failed to force set featured media: {update_response.status_code}")
                        except Exception as update_err:
                            print(f"[REST_API] ⚠️ Error force setting featured media: {update_err}")
                
                return True, post_id, post_url
            else:
                print(f"[REST_API] ❌ Post creation failed: {response.status_code}")
                print(f"[REST_API] Response: {response.text[:500]}")
                return False, None, None
                
        except Exception as e:
            print(f"[REST_API] ❌ Post creation error: {e}")
            import traceback
            traceback.print_exc()
            return False, None, None
    
    def post_article(self, blog_post):
        """
        Complete workflow: Upload image + Create post
        
        Args:
            blog_post: BlogPost object with title, content, image_url
            
        Returns:
            tuple: (success: bool, post_url: str or error_message)
        """
        try:
            # Step 1: Test API availability (Aggressive mode to avoid false 403 blocks)
            is_available, status_code, message = self.test_api_availability(aggressive=True)
            if not is_available:
                return False, f"REST API not available: {message}"
            
            # Step 2: Login
            if not self.cookies_loaded:
                if not self.login():
                    return False, "Login failed"
            
            # Step 3: Get featured media ID
            featured_media_id = None
            
            # CRITICAL FIX: Use featured_media_id from BlogPost if already uploaded
            if hasattr(blog_post, 'featured_media_id') and blog_post.featured_media_id:
                featured_media_id = blog_post.featured_media_id
                print(f"[REST_API] ✅ Using existing featured_media_id: {featured_media_id}")
            elif blog_post.image_url:
                # Only upload if we don't have media_id yet
                print(f"[REST_API] No featured_media_id found, uploading image...")
                success, media_id, media_url = self.upload_image(blog_post.image_url)
                if success:
                    featured_media_id = media_id
                else:
                    print("[REST_API] ⚠️ Featured image upload failed, continuing without it...")
            
            # Step 4: Create post
            success, post_id, post_url = self.create_post(
                title=blog_post.title,
                content=blog_post.content,
                featured_media_id=featured_media_id,
                status='publish'
            )
            
            if success:
                return True, post_url
            else:
                return False, "Post creation failed"
                
        except Exception as e:
            print(f"[REST_API] ❌ post_article error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
    
    def close(self):
        """Close session"""
        self.session.close()
        print("[REST_API] Session closed")
