from model.wp_model import BlogPost, WordPressClient
from model.config_manager import ConfigManager
from view.gui_view import GUIView
import threading
import os

class AppController:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        # Session storage
        self.site_url = self.config.get("site_url", "")
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")
        
        # API Clients (Lazy loaded)
        self.rest_client = None
        self.selenium_client = None
        self.client_lock = threading.Lock()

    def run(self):
        self.view = GUIView(self, initial_config=self.config)
        self.view.mainloop()

    def handle_login(self, site, user, pwd, headless=False):
        """
        Verify credentials via Selenium.
        """
        import threading
        from model.selenium_wp import SeleniumWPClient
        
        def _verify():
            try:
                # Selenium Login Check
                self.selenium_client = SeleniumWPClient(site, user, pwd)
                self.selenium_client.init_driver(headless=headless) # Starts browser
                success = self.selenium_client.login()
                # DON'T close browser - keep it alive for posting
                
                if success:
                    # Save session
                    self.site_url = site
                    self.username = user
                    self.password = pwd
                    self.config_manager.save_config(site, user, pwd)
                    self.view.after(0, self.view.login_success)
                else:
                    self.selenium_client.close()
                    self.view.after(0, lambda: self.view.login_failed("Đăng nhập thất bại (Selenium). Kiểm tra lại User/Pass."))

            except Exception as e:
                err_msg = str(e)
                if hasattr(self, 'selenium_client'):
                    self.selenium_client.close()
                self.view.after(0, lambda msg=err_msg: self.view.login_failed(msg))
        
        threading.Thread(target=_verify).start()

    def handle_post_request(self, data, is_batch=False):
        """
        Called by View when user clicks POST.
        """
        # Inject session credentials
        data.site_url = self.site_url
        data.username = self.username
        data.password = self.password

        # Thread for Selenium Posting
        thread = threading.Thread(target=self._process_post, args=(data, is_batch))
        thread.start()

    def _is_driver_alive(self):
        """
        Check if Selenium driver is still alive and responsive.
        Returns True if driver is accessible, False otherwise.
        """
        try:
            if not hasattr(self, 'selenium_client') or not self.selenium_client:
                return False
            if not self.selenium_client.driver:
                return False
            # Try to get current URL to verify driver is responsive
            _ = self.selenium_client.driver.current_url
            return True
        except Exception as e:
            print(f"[CONTROLLER] Driver health check failed: {e}")
            return False

    def _upload_image_smart(self, image_path, sync_cookies=True):
        """
        Smart image upload: Try REST API first (fast), fallback to Selenium
        Thread-safe: Locks Selenium access.
        """
        try:
            # Try REST API first (if available)
            if self.rest_client:
                # Sync cookies if requested (do this OUTSIDE thread pool if possible, or use lock)
                if sync_cookies and self._is_driver_alive():
                    with self.client_lock: # Lock while reading cookies from Selenium
                        try:
                            # Only sync if we haven't recently or if force sync
                             selenium_cookies = self.selenium_client.driver.get_cookies()
                             for cookie in selenium_cookies:
                                 self.rest_client.session.cookies.set(
                                     cookie['name'], 
                                     cookie['value'],
                                     domain=cookie.get('domain', '')
                                 )
                             
                             # Extract nonce if needed
                             if not self.rest_client.nonce:
                                 try:
                                     nonce = self.selenium_client.driver.execute_script("return window.wpApiSettings ? window.wpApiSettings.nonce : (window.wp && window.wp.api && window.wp.api.settings ? window.wp.api.settings.nonce : null);")
                                     if nonce:
                                         self.rest_client.nonce = nonce
                                 except:
                                     pass
                        except Exception as cookie_err:
                            print(f"[CONTROLLER] Warning: Cookie sync error: {cookie_err}")

                # RETRY LOGIC: Try up to 2 times
                for attempt in range(2):
                    try:
                        print(f"[CONTROLLER] Trying REST API upload for: {image_path} (Attempt {attempt+1})")
                        success, media_id, media_url = self.rest_client.upload_image(image_path)
                        
                        if success and media_url:
                            print(f"[CONTROLLER] ✅ REST API upload successful: {media_url}")
                            return media_id, media_url
                        
                        import time
                        time.sleep(1)
                    except Exception as rest_err:
                        print(f"[CONTROLLER] REST API upload error: {rest_err}")
            
            # Fallback to Selenium (Thread-Safe with Lock)
            print(f"[CONTROLLER] Using Selenium upload fallback for: {image_path}")
            with self.client_lock: # CRITICAL: Lock Selenium driver usage
                if self._is_driver_alive():
                   uploaded_url = self.selenium_client.upload_image_to_media(image_path)
                   if uploaded_url:
                       print(f"[CONTROLLER] ✅ Selenium upload successful: {uploaded_url}")
                       return None, uploaded_url
                   else:
                       print(f"[CONTROLLER] ❌ Selenium upload failed")
                       return None, None
                else:
                    print(f"[CONTROLLER] ❌ Selenium driver not available")
                    return None, None
            
        except Exception as e:
            print(f"[CONTROLLER] ❌ Image upload error: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def _process_post(self, data, is_batch=False):
        import concurrent.futures # Import locally to avoid scope issues, or move to top level
        try:
            # Initialize REST API client for fast image uploads (if admin account)
            # Initialize REST API client for fast image uploads (if admin account)
            # Initialize REST API client for fast image uploads (if admin account)
            # THREAD SAFETY: Use lock to prevent race conditions in batch mode
            if self.rest_client is None:
                with self.client_lock:
                    if self.rest_client is None:  # Double-check inside lock
                        # USE FAST API CLIENT
                        from model.wp_rest_api_fast import WordPressRESTClientFast as WordPressRESTClient
                        self.rest_client = WordPressRESTClient(self.site_url, self.username, self.password)
                        
                        # Don't login yet - we'll copy cookies from Selenium later
                        print("[CONTROLLER] ✅ REST API client initialized (will use Selenium cookies)")
                        self.view.after(0, lambda: self.view.log(f"⚡ Sẵn sàng upload ảnh nhanh với REST API"))
            
            from model.wp_model import BlogPost
            
            # 1. Create Post Object (Content Generation)
            # Fix: Nếu có video URL nhưng content trống → Auto-generate
            content = data.content.strip() if data.content else ""
            if data.video_url and not content:
                raw_content = ""  # Để trống để auto-generate với video
            else:
                raw_content = content  # Dùng content user nhập
            
            # ========================================
            # UNIFIED PARALLEL IMAGE UPLOAD (Featured + Manual Content)
            # ========================================
            self.view.after(0, lambda: self.view.log(f"⚡ Đang xử lý song song tất cả ảnh..."))
            
            # Sync cookies ONCE for all threads
            if self._is_driver_alive() and self.rest_client:
                 with self.client_lock:
                     try:
                         # Sync cookies
                         selenium_cookies = self.selenium_client.driver.get_cookies()
                         for cookie in selenium_cookies:
                             self.rest_client.session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))
                         # Sync nonce
                         if not self.rest_client.nonce:
                             nonce = self.selenium_client.driver.execute_script("return window.wpApiSettings ? window.wpApiSettings.nonce : (window.wp && window.wp.api && window.wp.api.settings ? window.wp.api.settings.nonce : null);")
                             if nonce: self.rest_client.nonce = nonce
                     except Exception as e:
                         print(f"Cookie sync warning: {e}")

            
            content_image_urls = []  # To store successful uploads
            featured_media_id = None
            
            # 1. Define Upload Tasks
            # Task format: (type, index, source_path_or_url, is_featured)
            upload_tasks = []
            
            # A. Add Featured Image Task
            if data.image_url and data.image_url.strip():
                if not data.image_url.startswith('http'):
                     upload_tasks.append(('featured', 0, data.image_url, True))
                else:
                     # It's a URL, just add to content (will be processed as such)
                     content_image_urls.append(data.image_url) 
            
            # B. Add Manual Content Images Tasks
            manual_images = []
            for i, attr in enumerate(['content_image', 'content_image2', 'content_image3'], 1):
                img_path = getattr(data, attr, '')
                if img_path and img_path.strip():
                    if not img_path.startswith('http'):
                        upload_tasks.append(('content', i, img_path, False))
                    else:
                        manual_images.append((i, img_path)) # Direct URL, no upload needed

            # 2. Execute Parallel Processing (Optimize + Upload)
            image_results = {} # Map index -> url
            
            if upload_tasks:
                print(f"[CONTROLLER] Processing {len(upload_tasks)} manual images in parallel...")
                self.view.after(0, lambda: self.view.log(f"🚀 Upload {len(upload_tasks)} ảnh song song..."))
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(upload_tasks)+1, 10)) as executor:
                    future_to_task = {}
                    
                    for task_type, idx, path, is_featured in upload_tasks:
                        # Define wrapper function for optimization + upload
                        def process_image(t_type, t_idx, t_path, t_featured):
                            # Optimize
                            upload_path = t_path
                            try:
                                import os
                                from model.image_api import ImageAPI
                                from model.facebook_thumbnail_optimizer import FacebookThumbnailOptimizer
                                
                                if t_featured:
                                     # Facebook Optimization (High Quality)
                                     fb_optimizer = FacebookThumbnailOptimizer()
                                     optimized = fb_optimizer.optimize_for_facebook(t_path, enhance=True)
                                     if optimized and os.path.exists(optimized): upload_path = optimized
                                else:
                                     # Content Optimization (Low Quality for speed)
                                     img_api = ImageAPI()
                                     optimized = img_api.optimize_image_for_upload(t_path, max_height=180, quality=55)
                                     if optimized and os.path.exists(optimized): upload_path = optimized
                            except Exception as e:
                                print(f"Optimization error for {t_path}: {e}")
                            
                            # Upload (using sync_cookies=False since we synced globally)
                            # Note: self._upload_image_smart is thread-safe for Selenium, and fast for REST
                            mid, url = self._upload_image_smart(upload_path, sync_cookies=False)
                            
                            # Clean up optimized file if different
                            if upload_path != t_path and upload_path and os.path.exists(upload_path):
                                try:
                                    os.remove(upload_path)
                                except: pass
                                
                            return (t_type, t_idx, mid, url)

                        future = executor.submit(process_image, task_type, idx, path, is_featured)
                        future_to_task[future] = (task_type, idx)
                    
                    # Collect results
                    for future in concurrent.futures.as_completed(future_to_task):
                        t_type, t_idx = future_to_task[future]
                        try:
                            res_type, res_idx, media_id, url = future.result()
                            if url:
                                if res_type == 'featured':
                                    featured_media_id = media_id
                                    # Update data.image_url to key the SEO correct
                                    data.image_url = url 
                                    content_image_urls.append(url) # Add featured to content list too
                                    self.view.after(0, lambda: self.view.log(f"✅ Ảnh đại diện OK"))
                                else:
                                    image_results[res_idx] = url
                                    self.view.after(0, lambda i=res_idx: self.view.log(f"✅ Ảnh content {i} OK"))
                            else:
                                self.view.after(0, lambda t=t_type: self.view.log(f"⚠️ Lỗi upload {t}"))
                        except Exception as e:
                             print(f"Parallel Task Error: {e}")

            # Reconstruct content_image_urls list in order
            # First is featured (already added if success), then manual images in order
            for idx in sorted(image_results.keys()):
                content_image_urls.append(image_results[idx])
            
            # Add Manual URLs (that didn't need upload)
            for idx, url in manual_images:
                content_image_urls.append(url)
            
            print(f"[CONTROLLER] Parallel processing done. Total content images: {len(content_image_urls)}")

            # ========================================
            # STEP 3: Auto-Fetch Car Images (Existing Parallel Logic)
            # ========================================
            # ... (Existing code for auto-fetch continues below) ...
            
            # Check if we need to auto-fetch car images
            auto_fetch = getattr(data, 'auto_fetch_images', False)
            
            # Check if any MANUAL CONTENT images were provided (ignore featured image)
            manual_content_provided = any([
                getattr(data, 'content_image', '').strip(),
                getattr(data, 'content_image2', '').strip(),
                getattr(data, 'content_image3', '').strip()
            ])
            
            # Auto-fetch images if enabled and no manual content images provided
            if auto_fetch and not manual_content_provided:
                self.view.after(0, lambda: self.view.log(f"🚗 Đang tự động lấy ảnh xe từ API..."))
                try:
                    from model.image_api import ImageAPI
                    image_api = ImageAPI()
                    
                    # Get car images based on title
                    car_image_urls = image_api.get_car_images_from_title(data.title, count=3)
                    
                    if car_image_urls:
                        self.view.after(0, lambda count=len(car_image_urls): self.view.log(f"✅ Đã lấy {count} ảnh xe từ API"))
                        
                        # Download images to local folder
                        import os
                        import time
                        os.makedirs("downloaded_cars", exist_ok=True)
                        
                        # PARALLEL DOWNLOAD + OPTIMIZE
                        import concurrent.futures
                        download_tasks = []
                        
                        for idx, img_url in enumerate(car_image_urls, 1):
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            import random
                            random_suffix = random.randint(1000, 9999)
                            local_path = f"downloaded_cars/car_api_{timestamp}_{random_suffix}_{idx}.jpg"
                            download_tasks.append((idx, img_url, local_path))
                        
                        # Download all images in parallel
                        self.view.after(0, lambda: self.view.log(f"📥 Đang tải {len(download_tasks)} ảnh song song..."))
                        downloaded_images = []
                        
                        def download_and_optimize(img_url, local_path):
                            """Download and immediately optimize image"""
                            success = image_api.download_image(img_url, local_path)
                            if success and os.path.exists(local_path):
                                # Optimize - Low quality for content
                                optimized_path = image_api.optimize_image_for_upload(local_path, max_height=180, quality=55)
                                return optimized_path
                            return None
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                            future_to_task = {executor.submit(download_and_optimize, t[1], t[2]): t for t in download_tasks}
                            for future in concurrent.futures.as_completed(future_to_task):
                                idx, _, local_path = future_to_task[future]
                                try:
                                    optimized_path = future.result()
                                    if optimized_path:
                                        downloaded_images.append((idx, optimized_path))
                                    else:
                                        if os.path.exists(local_path): os.remove(local_path)
                                except Exception: pass

                        # PARALLEL UPLOAD
                        if downloaded_images:
                            self.view.after(0, lambda: self.view.log(f"📤 Upload {len(downloaded_images)} ảnh auto..."))
                            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                                future_to_img = {executor.submit(self._upload_image_smart, img[1], False): img for img in downloaded_images}
                                for future in concurrent.futures.as_completed(future_to_img):
                                    img = future_to_img[future]
                                    try:
                                        _, url = future.result()
                                        if url: content_image_urls.append(url)
                                        if os.path.exists(img[1]): os.remove(img[1])
                                    except Exception: pass
                    else:
                        self.view.after(0, lambda: self.view.log(f"⚠️ Không tìm thấy ảnh xe"))
                except Exception as e:
                    print(f"Auto-fetch error: {e}")
            
            # Note: The existing auto-fetch block starts with:
            # check auto_fetch... 
            # We need to make sure we connect correctly.
            
            # ... REMOVING OLD SEQUENTIAL BLOCKS ...
            # The previous code had Step 1 and Step 2 manual separate. 
            # We replaced them with the block above.
            
            # We need to ensure variables align for the BlogPost creation below.
            
            # Create BlogPost WITHOUT featured_image_url and featured_media_id
            # Featured image is now part of content_images (first image)
            # Create BlogPost with featured_media_id (Critical for setting WordPress Featured Image)
            # data.image_url passed as fallback image_url
            post = BlogPost(data.title, data.video_url, data.image_url, raw_content, content_images=content_image_urls, featured_media_id=featured_media_id)
            
            # Set theme if provided
            if hasattr(data, 'theme') and data.theme:
                post.theme = data.theme
                print(f"[CONTROLLER] Using theme: {data.theme}")
            
            post.generate_seo_content()

            # 2. Use Auto Client (tries REST API first, then Selenium)
            # Check if we have an existing selenium client (for image uploads)
            if not self._is_driver_alive():
                # Initialize selenium client for image uploads
                print("[CONTROLLER] Selenium driver not available, initializing...")
                from model.selenium_wp import SeleniumWPClient
                self.selenium_client = SeleniumWPClient(self.site_url, self.username, self.password)
                self.selenium_client.init_driver(headless=False)
                self.selenium_client.login()

            
            # 3. Execute Post using Auto Client (REST API → Selenium fallback)
            if not is_batch:
                print(f"[INFO] Đang đăng bài (tự động chọn phương thức tốt nhất)...")  # Terminal only
            
            # Use WPAutoClient for intelligent method selection
            from model.wp_model import WPAutoClient
            auto_client = WPAutoClient(self.site_url, self.username, self.password)
            
            # Pass existing selenium client to avoid re-login if REST API fails
            success, message = auto_client.post_article(post, reuse_selenium_client=self.selenium_client, reuse_fast_client=self.rest_client)
            
            # 4. Update UI - PASS TITLE EXPLICITLY
            self.view.after(0, lambda s=success, m=message, b=is_batch, t=post.title: self.view.on_post_finished(s, m, b, t))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Pass title from data if possible, or "Error Post"
            err_title = data.title if hasattr(data, 'title') else "Error Post"
            self.view.after(0, lambda msg=str(e), b=is_batch, t=err_title: self.view.on_post_finished(False, msg, b, t))
