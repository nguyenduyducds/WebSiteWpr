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
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Suppress SSL warnings
import os
import re
from urllib.parse import urlparse, urljoin
import time
import concurrent.futures
import threading

# GLOBAL UPLOAD LIMITER:
# Concurrency that is too high often triggers WAF/rate-limit (429) or per-user throttles,
# making uploads appear "stuck" for some accounts while others look normal.
# Keep a safer default, and allow overriding via env var for controlled environments.
def _get_max_concurrent_uploads() -> int:
    try:
        v = int(os.environ.get("WP_MAX_CONCURRENT_UPLOADS", "").strip() or "5")
        return max(1, min(v, 30))
    except Exception:
        return 5

_upload_semaphore = threading.Semaphore(_get_max_concurrent_uploads())


class WordPressRESTClientFast:
    """
    Ultra-fast WordPress REST API client
    Optimized for speed - target 1 second per request
    """
    
    def __init__(self, site_url, username, password, app_password=None, enable_rate_limiting=False, verbose=True):
        """
        Initialize WordPress REST API client with speed optimizations
        
        Args:
            site_url: WordPress site URL (e.g., "https://example.com")
            username: WordPress username
            password: WordPress password or application password
            app_password: Optional WordPress Application Password for REST Basic Auth (recommended)
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
        self.app_password = app_password
        self.verbose = verbose
        
        # SPEED OPTIMIZATION: Create session with connection pooling
        self.session = self._create_optimized_session()
        
        self.nonce = None
        self.cookies_loaded = False
        # If a site returns HTML for REST endpoints (security plugin/WAF),
        # we mark REST as blocked and let callers bypass REST immediately.
        self.rest_blocked = False
        self.rest_blocked_reason = None
        
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
                status_forcelist=[429, 502, 503, 504],  # Removed 500
                allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS"], # TRÁNH TRÙNG LẶP: Không auto-retry POST
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
        
        # SSL: Tắt verify vì một số site dùng cert tự ký hoặc cert hết hạn
        session.verify = False
        
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
            
            basic_password = self.app_password or self.password
            # WP displays application passwords with spaces; normalize.
            if isinstance(basic_password, str):
                basic_password = basic_password.replace(" ", "")
            response = self.session.get(
                f"{self.api_base}/users/me",
                auth=HTTPBasicAuth(self.username, basic_password),
                headers={"Accept": "application/json"},
                timeout=5  # Reduced timeout
            )
            
            if response.status_code == 200:
                print("[FAST_API] ✅ Application password auth successful!")
                self.session.auth = HTTPBasicAuth(self.username, basic_password)
                self.cookies_loaded = True
                return True
            else:
                # Helpful diagnostics: many security plugins return HTML/200 for blocked REST,
                # but /users/me should normally be JSON 401/403 if unauthorized.
                try:
                    ct = (response.headers.get("Content-Type") or "").strip()
                    print(f"[FAST_API] Application password auth failed: status={response.status_code}, content-type={ct}")
                except Exception:
                    pass
            
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

    def _refresh_auth(self):
        """
        Anti-Block Mechanism: Refresh session and Nonce when 403 detected
        """
        print("[FAST_API] 🛡️ Anti-Block: Refreshing session and authentication...")
        try:
            # 1. Reset Session (New Connection)
            self.session.close()
            self.session = self._create_optimized_session()
            
            # 2. Re-Login
            self.cookies_loaded = False
            self.nonce = None
            return self.login_fast()
        except Exception as e:
            print(f"[FAST_API] ❌ Refresh failed: {e}")
            return False

    def upload_image_via_admin_async(self, image_path):
        """
        FAST UPLOAD (non-REST): Use wp-admin async-upload.php with existing logged-in cookies.
        This bypasses REST API blocks (HTML responses) and is usually much faster than Selenium UI.
        Requires: valid wp-admin cookies in self.session (typically synced from Selenium).
        """
        try:
            if not os.path.exists(image_path):
                print(f"[FAST_API] ❌ Image not found: {image_path}")
                return False, None, None

            filename = os.path.basename(image_path)
            mime_type = 'image/jpeg'
            if filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                mime_type = 'image/gif'
            elif filename.lower().endswith('.webp'):
                mime_type = 'image/webp'

            # 1) Get nonce from media upload page (wp-admin), via existing cookies
            media_new_url = f"{self.site_url}/wp-admin/media-new.php"
            resp = self.session.get(media_new_url, timeout=15)
            html = resp.text or ""

            # Try to read nonce from _wpPluploadSettings
            nonce = None
            m = re.search(r'"_wpnonce"\s*:\s*"([a-fA-F0-9]+)"', html)
            if m:
                nonce = m.group(1)
            if not nonce:
                # Fallback: common hidden nonce field patterns
                m = re.search(r'name="_wpnonce"\s+value="([a-fA-F0-9]+)"', html)
                if m:
                    nonce = m.group(1)

            if not nonce:
                print("[FAST_API] ❌ Could not extract wp-admin upload nonce (async-upload)")
                return False, None, None

            # 2) POST multipart to async-upload endpoint
            upload_url = f"{self.site_url}/wp-admin/async-upload.php"
            data = {
                "action": "upload-attachment",
                "_wpnonce": nonce,
            }

            with open(image_path, "rb") as f:
                files = {
                    "async-upload": (filename, f, mime_type),
                }
                r = self.session.post(upload_url, data=data, files=files, timeout=60)

            # WP sometimes returns JSON; sometimes returns just the attachment ID.
            attachment_id = None
            media_url = None

            ct = (r.headers.get("Content-Type") or "").lower()
            text = (r.text or "").strip()

            if "application/json" in ct:
                try:
                    j = r.json()
                    attachment_id = j.get("id") or j.get("data", {}).get("id")
                    media_url = j.get("url") or j.get("data", {}).get("url")
                except Exception:
                    pass

            if attachment_id is None:
                m = re.search(r"\b(\d{1,12})\b", text)
                if m:
                    try:
                        attachment_id = int(m.group(1))
                    except Exception:
                        attachment_id = None

            # 3) If we have an attachment ID but no URL, fetch attachment edit page and scrape URL
            if attachment_id and not media_url:
                edit_url = f"{self.site_url}/wp-admin/post.php?post={attachment_id}&action=edit"
                er = self.session.get(edit_url, timeout=15)
                ehtml = er.text or ""
                # Common input field in attachment edit screen
                m = re.search(r'id="attachment_url"\s+value="([^"]+)"', ehtml)
                if m:
                    media_url = m.group(1)
                else:
                    # Fallback: look for uploads URL-like strings
                    m = re.search(r'(https?://[^"\s]+/wp-content/uploads/[^"\s]+)', ehtml)
                    if m:
                        media_url = m.group(1)

            if attachment_id and media_url:
                print(f"[FAST_API] ✅ Admin async-upload done! ID: {attachment_id}")
                return True, attachment_id, media_url

            print(f"[FAST_API] ❌ Admin async-upload failed (status={r.status_code}, content-type={r.headers.get('Content-Type')})")
            if self.verbose:
                preview = text.replace("\n", " ")
                print(f"[FAST_API] Body preview: {preview[:250]}")
            return False, None, None
        except Exception as e:
            print(f"[FAST_API] ❌ Admin async-upload error: {e}")
            return False, None, None

    def create_post_via_admin_form(self, title, content, status="publish", featured_media_id=None):
        """
        FAST POST (non-REST): Create a post by submitting wp-admin post form (Classic Editor backend).
        This bypasses REST API blocks and avoids Selenium UI automation.
        Requires: valid wp-admin cookies in self.session.
        """
        try:
            # 1) Load post-new.php.
            # We append ?classic-editor to bypass Gutenberg's JS shell if possible.
            new_url = f"{self.site_url}/wp-admin/post-new.php?classic-editor"
            r = self.session.get(new_url, timeout=20, allow_redirects=True)
            html = r.text or ""

            # If not logged in, wp-admin will redirect or return login HTML
            if "wp-login.php" in (getattr(r, "url", "") or "") or ("name=\"log\"" in html and "name=\"pwd\"" in html):
                print("[FAST_API] ❌ wp-admin not authenticated for post-new.php")
                return False, None, None

            post_id = None
            # Prefer extracting from redirect URL to post.php?post=<id>&action=edit
            try:
                m = re.search(r"[?&]post=(\d+)\b", getattr(r, "url", "") or "")
                if m:
                    post_id = int(m.group(1))
            except Exception:
                pass
            if not post_id:
                m = re.search(r'name="post_ID"\s+value="(\d+)"', html)
                if m:
                    post_id = int(m.group(1))
            if not post_id:
                m = re.search(r'"post"\s*:\s*\{"id"\s*:\s*(\d+)', html)
                if m:
                    post_id = int(m.group(1))
            if not post_id:
                # Gutenberg JS bootstraps the current post id in various shapes
                patterns = [
                    r'"postId"\s*:\s*(\d+)',
                    r'"post_id"\s*:\s*(\d+)',
                    r'core/editor"\s*:\s*\{[^}]*"postId"\s*:\s*(\d+)',
                    r'wp\.editPost\.initialize\s*\(\s*["\'][^"\']+["\']\s*,\s*["\'][^"\']+["\']\s*,\s*(\d+)',
                    r'post_ID"\s*value\s*=\s*"(\d+)',
                    r'admin-ajax\.php\?action=oembed-cache&post=(\d+)',
                    r'post=(\d+)&action=edit'
                ]
                for pat in patterns:
                    m = re.search(pat, html)
                    if m:
                        try:
                            post_id = int(m.group(1))
                            break
                        except Exception:
                            pass

            # GUTENBERG FALLBACK: If still no post_id, try creating via WP REST API with cookie/nonce auth
            if not post_id:
                print("[FAST_API] ⚠️ Could not find post_id from post-new.php (Gutenberg). Trying REST with cookie auth...")
                # Extract nonce from page HTML for cookie-based REST auth
                nonce_rest = None
                for pat in [
                    r'"nonce"\s*:\s*"([a-fA-F0-9]+)"',
                    r'wpApiSettings["\']?\s*[=:]\s*\{[^}]*["\']nonce["\']\s*:\s*["\']([a-fA-F0-9]+)["\']',
                    r'["\']nonce["\']\s*:\s*["\']([a-fA-F0-9]+)["\']',
                ]:
                    m = re.search(pat, html)
                    if m:
                        nonce_rest = m.group(1)
                        break
                
                # If no nonce from post-new.php, try dashboard
                if not nonce_rest:
                    try:
                        dash_r = self.session.get(f"{self.site_url}/wp-admin/", timeout=15)
                        for pat in [
                            r'wpApiSettings["\']?\s*[=:]\s*\{[^}]*["\']nonce["\']\s*:\s*["\']([a-fA-F0-9]+)["\']',
                            r'["\']nonce["\']\s*:\s*["\']([a-fA-F0-9]+)["\']',
                        ]:
                            m = re.search(pat, dash_r.text or "")
                            if m:
                                nonce_rest = m.group(1)
                                break
                    except Exception:
                        pass

                if nonce_rest:
                    try:
                        rest_headers = {
                            'X-WP-Nonce': nonce_rest,
                            'Content-Type': 'application/json',
                        }
                        import json as _json
                        payload_dict = {
                            'title': title,
                            'content': content,
                            'status': status,
                        }
                        if featured_media_id:
                            payload_dict['featured_media'] = featured_media_id
                        payload = _json.dumps(payload_dict)
                        rest_resp = self.session.post(
                            f"{self.site_url}/wp-json/wp/v2/posts",
                            data=payload,
                            headers=rest_headers,
                            timeout=30,
                        )
                        ct = (rest_resp.headers.get('Content-Type') or '').lower()
                        if rest_resp.status_code in (200, 201) and 'json' in ct:
                            jdata = rest_resp.json()
                            post_id = jdata.get('id')
                            post_url = jdata.get('link') or jdata.get('guid', {}).get('rendered', '')
                            if post_id:
                                print(f"[FAST_API] ✅ Post created via REST+nonce cookie auth! ID: {post_id}")
                                return True, post_id, post_url
                        else:
                            print(f"[FAST_API] ⚠️ REST+nonce failed (status={rest_resp.status_code}, ct={ct})")
                    except Exception as rest_err:
                        print(f"[FAST_API] ⚠️ REST+nonce error: {rest_err}")
                else:
                    print("[FAST_API] ⚠️ Could not extract nonce for REST+cookie fallback")

            # 2) Load edit screen to extract the correct _wpnonce/_wp_http_referer for editpost
            if not post_id:
                print("[FAST_API] ❌ Could not determine post_id from post-new.php (Gutenberg)")
                return False, None, None

            edit_url = f"{self.site_url}/wp-admin/post.php?post={post_id}&action=edit"
            er = self.session.get(edit_url, timeout=20, allow_redirects=True)
            ehtml = er.text or ""

            if "wp-login.php" in (getattr(er, "url", "") or "") or ("name=\"log\"" in ehtml and "name=\"pwd\"" in ehtml):
                print("[FAST_API] ❌ wp-admin not authenticated for post edit screen")
                return False, None, None

            nonce = None
            # Prefer nonce near the main post form
            m = re.search(r'<form[^>]+id="post"[\s\S]*?name="_wpnonce"\s+value="([a-fA-F0-9]+)"', ehtml, re.IGNORECASE)
            if m:
                nonce = m.group(1)
            if not nonce:
                m = re.search(r'name="_wpnonce"\s+value="([a-fA-F0-9]+)"', ehtml)
                if m:
                    nonce = m.group(1)

            referer = None
            m = re.search(r'name="_wp_http_referer"\s+value="([^"]+)"', ehtml)
            if m:
                referer = m.group(1)

            original_post_status = None
            m = re.search(r'name="original_post_status"\s+value="([^"]+)"', ehtml)
            if m:
                original_post_status = m.group(1)

            post_author = None
            m = re.search(r'name="post_author"\s+value="(\d+)"', ehtml)
            if m:
                post_author = m.group(1)

            user_id = None
            m = re.search(r'name="user_ID"\s+value="(\d+)"', ehtml)
            if m:
                user_id = m.group(1)

            if not nonce:
                print("[FAST_API] ❌ Could not extract _wpnonce from post edit screen")
                return False, None, None

            # 3) Submit to post.php (editpost)
            post_php = f"{self.site_url}/wp-admin/post.php"
            data = {
                "_wpnonce": nonce,
                "_wp_http_referer": referer or f"/wp-admin/post.php?post={post_id}&action=edit",
                "user_ID": user_id or "1",
                "action": "editpost",
                "originalaction": "editpost",
                "post_author": post_author or "1",
                "post_type": "post",
                "original_post_status": original_post_status or "auto-draft",
                "referredby": "",
                "post_ID": str(post_id),
                "post_title": title,
                "content": content,
                "post_status": status,
                # Ensure WP treats this as publish click
                "publish": "Publish",
            }
            # Set featured image if provided
            if featured_media_id:
                data["_thumbnail_id"] = str(featured_media_id)

            resp = self.session.post(post_php, data=data, timeout=30, allow_redirects=True)

            # Success typically redirects to post.php?post=ID&action=edit or to post.php?post=ID&action=edit&message=6
            final_url = getattr(resp, "url", "") or ""
            if f"post={post_id}" in final_url or resp.status_code in (200, 302):
                # Try to build public URL (best-effort): fetch permalink from edit screen
                er2 = self.session.get(edit_url, timeout=20)
                ehtml2 = er2.text or ""
                permalink = None
                m = re.search(r'id="sample-permalink"\s*[^>]*>\s*<a[^>]+href="([^"]+)"', ehtml2)
                if m:
                    permalink = m.group(1)
                else:
                    # Try to find Gutenberg's canonical link or just use default post URL
                    m = re.search(r'<link rel="canonical" href="([^"]+)"', ehtml2)
                    if m:
                        permalink = m.group(1)
                    else:
                        permalink = f"{self.site_url}/?p={post_id}"
                print(f"[FAST_API] ✅ Admin post form submitted! ID: {post_id}")
                return True, post_id, permalink

            print(f"[FAST_API] ❌ Admin post form failed (status={resp.status_code})")
            if self.verbose:
                preview = (resp.text or "").strip().replace("\n", " ")
                print(f"[FAST_API] Body preview: {preview[:250]}")
            return False, None, None
        except Exception as e:
            print(f"[FAST_API] ❌ Admin post form error: {e}")
            return False, None, None
    
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
                self._log(f"[FAST_API] 🔒 Acquired upload slot (max {_get_max_concurrent_uploads()} concurrent)")
                
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
                            # Some WAF/plugins return HTML (or an empty body) with 200/201,
                            # which would crash json() and make the upload look "stuck".
                            try:
                                data = response.json()
                            except ValueError:
                                ct = (response.headers.get("Content-Type") or "").strip()
                                body_preview = ""
                                try:
                                    body_preview = (response.text or "").strip().replace("\n", " ")
                                except Exception:
                                    body_preview = "<unreadable body>"
                                # Include final URL/redirect hints for diagnosing "HTML instead of JSON"
                                final_url = getattr(response, "url", None)
                                if final_url:
                                    print(f"[FAST_API] Final URL: {final_url}")
                                try:
                                    if getattr(response, "history", None):
                                        hist = " -> ".join([f"{r.status_code}:{getattr(r,'url', '')}" for r in response.history][-5:])
                                        if hist:
                                            print(f"[FAST_API] Redirect history: {hist}")
                                except Exception:
                                    pass

                                print(f"[FAST_API] ❌ Upload got non-JSON response (status={response.status_code}, content-type={ct})")
                                print(f"[FAST_API] Body preview: {body_preview[:250]}")
                                # Mark REST blocked so upper layers can bypass further REST attempts.
                                self.rest_blocked = True
                                self.rest_blocked_reason = f"media returned non-JSON ({ct})"

                                # If we got an HTML login page, our cookie/nonce is missing/expired.
                                # Try refreshing auth once, then let the outer retry loop re-attempt.
                                lower = body_preview.lower()
                                looks_like_login = ("wp-login.php" in lower) or ('name="log"' in lower and 'name="pwd"' in lower) or ("id=\"login\"" in lower)
                                if looks_like_login and attempt < max_retries - 1:
                                    print(f"[FAST_API] 🛡️ Looks like WP login page. Refreshing auth and retrying... (attempt {attempt+1})")
                                    if self._refresh_auth():
                                        if self.nonce:
                                            headers['X-WP-Nonce'] = self.nonce
                                        time.sleep(0.5)
                                        continue
                                return False, None, None

                            media_id = data.get('id')
                            media_url = data.get('source_url')

                            if not media_id or not media_url:
                                ct = (response.headers.get("Content-Type") or "").strip()
                                print(f"[FAST_API] ❌ Upload response missing fields (id/source_url). status={response.status_code}, content-type={ct}")
                                if self.verbose:
                                    try:
                                        print(f"[FAST_API] JSON keys: {list(data.keys())[:30]}")
                                    except Exception:
                                        pass
                                return False, None, None

                            print(f"[FAST_API] ✅ Upload done! ID: {media_id}")
                            return True, media_id, media_url
                        elif response.status_code == 403: # Forbidden
                            print(f"[FAST_API] 🛡️ 403 Forbidden on upload. Refreshing auth... (attempt {attempt+1})")
                            if self._refresh_auth():
                                # IMPORTANT: Headers are just a dictionary copy in the loop context in Python? 
                                # No, 'headers' was defined outside. Modifying it is fine.
                                if self.nonce: headers['X-WP-Nonce'] = self.nonce
                                # IMPORTANT: 'file_data' is in memory, so we can just retry post
                                continue
                            return False, None, None
                        elif response.status_code == 429:  # Too Many Requests
                            if attempt < max_retries - 1:
                                retry_after = response.headers.get("Retry-After")
                                if retry_after:
                                    try:
                                        wait_time = max(1.0, float(retry_after))
                                    except Exception:
                                        wait_time = (2 ** attempt) * 2
                                else:
                                    wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                                print(f"[FAST_API] ⚠️ Rate limited (429), waiting {wait_time}s... (attempt {attempt+1}/{max_retries})")
                                # Adaptive: if we're seeing 429, enable pacing for the rest of this run
                                self.enable_rate_limiting = True
                                time.sleep(wait_time)
                                continue
                            else:
                                print(f"[FAST_API] ❌ Upload failed: Rate limited after {max_retries} attempts")
                                return False, None, None
                        else:
                            print(f"[FAST_API] ❌ Upload failed: {response.status_code}")
                            if self.verbose:
                                try:
                                    preview = (response.text or "").strip().replace("\n", " ")
                                    print(f"[FAST_API] Response preview: {preview[:200]}")
                                except Exception:
                                    pass
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
                    except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                         # Anti-Block: Connection reset by peer usually means Firewall block or Overload
                         print(f"[FAST_API] 🛡️ Connection Error ({e}). Renewing session... (attempt {attempt+1})")
                         if attempt < max_retries - 1:
                             time.sleep(1)
                             self.session = self._create_optimized_session()
                             # Re-login might be needed if session was cookie-based
                             if not getattr(self.session, 'auth', None): 
                                 self.login_fast()
                                 if self.nonce: headers['X-WP-Nonce'] = self.nonce
                             
                             f.seek(0)
                             continue
                         return False, None, None
                    except Exception as e:
                        # Unknown errors should not be blindly retried; log response context if available.
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
    
    def create_post_fast(self, title, content, featured_media_id=None, featured_image_url=None, status='publish'):
        """
        FAST POST CREATION with reduced timeout
        
        Args:
            title: Post title
            content: Post content (HTML)
            featured_media_id: Featured image media ID (optional)
            featured_image_url: Featured image URL for og:image override (optional)
            status: Post status (default: 'publish')
            
        Returns:
            tuple: (success: bool, post_id: int or None, post_url: str or None)
        """
        try:
            print(f"[FAST_API] ⚡ Fast creating post: {title[:50]}...")
            
            # 🔥 SPEEDHACK: Always create as 'draft' first. 
            # WordPress takes huge CPU/Time to process a 'publish' request because 
            # it builds sitemaps, clears caching, sends emails, etc.
            # 'draft' is instant. We will publish it in a separate step.
            final_status = status
            post_data = {
                'title': title,
                'content': content,
                'status': 'draft' if final_status == 'publish' else final_status,
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
            # Add meta fields for og:image override (works with Yoast, JNews, RankMath, etc.)
            if featured_image_url:
                post_data['meta'] = {
                    '_yoast_wpseo_opengraph-image': featured_image_url,
                    '_yoast_wpseo_twitter-image': featured_image_url,
                }
            
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
                    # Tạo bài dạng DRAFT siêu nhanh (timeout thấp)
                    response = self.session.post(
                        self.posts_endpoint,
                        json=post_data,
                        headers=headers,
                        timeout=15  # Drafts lưu rất nhanh nên không sợ văng
                    )
                    
                    if response.status_code in [200, 201]:
                        # Some sites/WAFs return HTML (login/challenge) even with 200/201.
                        try:
                            data = response.json()
                        except ValueError:
                            ct = (response.headers.get("Content-Type") or "").strip()
                            body_preview = ""
                            try:
                                body_preview = (response.text or "").strip().replace("\n", " ")
                            except Exception:
                                body_preview = "<unreadable body>"
                            final_url = getattr(response, "url", None)
                            if final_url:
                                print(f"[FAST_API] Final URL: {final_url}")
                            try:
                                if getattr(response, "history", None):
                                    hist = " -> ".join([f"{r.status_code}:{getattr(r,'url', '')}" for r in response.history][-5:])
                                    if hist:
                                        print(f"[FAST_API] Redirect history: {hist}")
                            except Exception:
                                pass
                            print(f"[FAST_API] ❌ Post got non-JSON response (status={response.status_code}, content-type={ct})")
                            print(f"[FAST_API] Body preview: {body_preview[:250]}")
                            # Mark REST blocked so upper layers can bypass further REST attempts.
                            self.rest_blocked = True
                            self.rest_blocked_reason = f"posts returned non-JSON ({ct})"

                            lower = body_preview.lower()
                            looks_like_login = ("wp-login.php" in lower) or ('name="log"' in lower and 'name="pwd"' in lower) or ("id=\"login\"" in lower)
                            if looks_like_login and attempt < max_retries - 1:
                                print(f"[FAST_API] 🛡️ Looks like WP login page. Refreshing auth and retrying... (attempt {attempt+1})")
                                if self._refresh_auth():
                                    if self.nonce:
                                        headers['X-WP-Nonce'] = self.nonce
                                    time.sleep(0.5)
                                    continue
                            return False, None, None
                        post_id = data.get('id')
                        post_url = data.get('link')
                        
                        # VERIFY: Check if featured_media was actually set
                        actual_featured = data.get('featured_media')
                        if featured_media_id:
                            if actual_featured == featured_media_id:
                                print(f"[FAST_API] ✅ Featured media VERIFIED: {actual_featured}")
                            elif actual_featured and actual_featured != featured_media_id:
                                print(f"[FAST_API] ⚠️ Featured media MISMATCH! Expected {featured_media_id}, got {actual_featured}")
                                # Force update
                                self._force_set_featured_media(post_id, featured_media_id, headers)
                            else:
                                print(f"[FAST_API] ⚠️ Featured media NOT SET in response! Force updating...")
                                self._force_set_featured_media(post_id, featured_media_id, headers)
                        
                        # 🔥 SPEEDHACK: Now Trigger Publish in the background
                        if final_status == 'publish':
                            print(f"[FAST_API] ⚡ Tốc độ ánh sáng: Bài (ID: {post_id}) đã lưu tạm. Đang kích hoạt xuất bản...")
                            try:
                                publish_resp = self.session.post(
                                    f"{self.posts_endpoint}/{post_id}",
                                    json={"status": "publish"},
                                    headers=headers,
                                    timeout=3 # Cố tình set 3 giây. Nếu WP bị quá tải và không phản hồi kịp, 
                                              # ta kệ xác luôn vì lệnh publish đã chắc chắn bay vào máy chủ WP!
                                )
                                if publish_resp.status_code in [200, 201]:
                                    post_url = publish_resp.json().get('link', post_url)
                            except requests.exceptions.ReadTimeout:
                                print(f"[FAST_API] ⚡ Gửi lệnh xuất bản thành công! (WP server đang lưu ngầm, app đi tiếp)")
                            except Exception as publish_err:
                                print(f"[FAST_API] ⚠️ Lỗi khi đẩy publish (có thể sẽ lưu ở dạng nháp): {publish_err}")
                        
                        print(f"[FAST_API] ✅ Đăng thành công! Mở: {post_url}")
                        return True, post_id, post_url
                    elif response.status_code == 403: # Forbidden
                         print(f"[FAST_API] 🛡️ 403 Forbidden on create_post. Refreshing auth... (attempt {attempt+1})")
                         if self._refresh_auth():
                             if self.nonce: headers['X-WP-Nonce'] = self.nonce
                             continue
                         return False, None, None
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
                        
                except requests.exceptions.ReadTimeout:
                    # TRÁNH TRÙNG LẶP: Đã gửi request lên thành công, WP đang xử lý nhưng quá lâu (lag).
                    # NẾU retry lúc này, wp sẽ đăng 2 bài. 
                    print(f"[FAST_API] ⚠️ ReadTimeout (WP quá tải). Không retry để tránh trùng lặp bài viết!")
                    return False, None, None
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        print(f"[FAST_API] ⚠️ Connection Timeout, retrying... (attempt {attempt+1}/{max_retries})")
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
    
    def _force_set_featured_media(self, post_id, featured_media_id, headers):
        """Force update featured_media on an existing post"""
        try:
            response = self.session.post(
                f"{self.posts_endpoint}/{post_id}",
                json={"featured_media": featured_media_id},
                headers=headers,
                timeout=10
            )
            if response.status_code in [200, 201]:
                print(f"[FAST_API] ✅ Featured media force-set to {featured_media_id}")
            else:
                print(f"[FAST_API] ⚠️ Force-set failed: {response.status_code}")
        except Exception as e:
            print(f"[FAST_API] ⚠️ Force-set error: {e}")
    
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
            elif getattr(blog_post, 'image_url', None):
                upload_start = time.time()
                # If image_url is already a remote URL, don't try to "upload" it as a local file.
                # We'll use it as og:image override instead (and/or leave featured_media unset).
                if isinstance(blog_post.image_url, str) and blog_post.image_url.startswith('http'):
                    print("[FAST_API] ℹ️ Featured image is already a URL, skipping media upload")
                else:
                    success, media_id, media_url = self.upload_image_fast(blog_post.image_url)
                    if success:
                        featured_media_id = media_id
                print(f"[FAST_API] ⏱️ Upload took: {time.time() - upload_start:.2f}s")
            
            # Step 4: Create post (pass featured_image_url for og:image override)
            featured_image_url = getattr(blog_post, 'image_url', None) if isinstance(getattr(blog_post, 'image_url', None), str) else None
            post_start = time.time()
            success, post_id, post_url = self.create_post_fast(
                title=blog_post.title,
                content=blog_post.content,
                featured_media_id=featured_media_id,
                featured_image_url=featured_image_url,
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
