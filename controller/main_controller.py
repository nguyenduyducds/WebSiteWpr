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

    def _upload_image_smart(self, image_path):
        """
        Smart image upload: Try REST API first (fast), fallback to Selenium
        Uses cookies AND nonce from Selenium session for REST API authentication
        
        Args:
            image_path: Path to local image file
            
        Returns:
            tuple: (media_id, media_url) or (None, None) if failed
        """
        try:
            # Try REST API first (if available and admin account)
            if hasattr(self, 'rest_client') and self.rest_client:
                # RETRY LOGIC: Try up to 2 times
                for attempt in range(2):
                    try:
                        print(f"[CONTROLLER] Trying REST API upload for: {image_path} (Attempt {attempt+1})")
                        
                        # Copy cookies from Selenium to REST API session (Refresh every time)
                        if hasattr(self, 'selenium_client') and self.selenium_client.driver:
                            try:
                                selenium_cookies = self.selenium_client.driver.get_cookies()
                                for cookie in selenium_cookies:
                                    self.rest_client.session.cookies.set(
                                        cookie['name'], 
                                        cookie['value'],
                                        domain=cookie.get('domain', '')
                                    )
                                # print(f"[CONTROLLER] Copied cookies from Selenium")
                                
                                # Extract nonce if needed (only on first attempt to save time)
                                if attempt == 0 or not self.rest_client.nonce:
                                    try:
                                        nonce = self.selenium_client.driver.execute_script("""
                                            if (window.wpApiSettings && window.wpApiSettings.nonce) return window.wpApiSettings.nonce;
                                            if (window.wp && window.wp.api && window.wp.api.settings && window.wp.api.settings.nonce) return window.wp.api.settings.nonce;
                                            return null;
                                        """)
                                        if nonce:
                                            self.rest_client.nonce = nonce
                                    except:
                                        pass
                            except Exception as cookie_err:
                                print(f"[CONTROLLER] Warning: Could not sync cookies: {cookie_err}")
                        
                        success, media_id, media_url = self.rest_client.upload_image(image_path)
                        
                        if success and media_url:
                            print(f"[CONTROLLER] ✅ REST API upload successful: {media_url}")
                            return media_id, media_url  # Return BOTH media_id and media_url
                        else:
                            print(f"[CONTROLLER] ⚠️ REST API upload failed (Attempt {attempt+1})")
                            import time
                            time.sleep(1) # Wait before retry
                    except Exception as rest_err:
                        print(f"[CONTROLLER] REST API upload error: {rest_err}")
                        import time
                        time.sleep(1)
            
            # Fallback to Selenium (no media_id available)
            print(f"[CONTROLLER] Using Selenium upload for: {image_path}")
            uploaded_url = self.selenium_client.upload_image_to_media(image_path)
            
            if uploaded_url:
                print(f"[CONTROLLER] ✅ Selenium upload successful: {uploaded_url}")
                return None, uploaded_url  # No media_id from Selenium
            else:
                print(f"[CONTROLLER] ❌ Selenium upload failed")
                return None, None
            
        except Exception as e:
            print(f"[CONTROLLER] ❌ Image upload error: {e}")
            return None, None

    def _process_post(self, data, is_batch=False):
        try:
            # Initialize REST API client for fast image uploads (if admin account)
            if not hasattr(self, 'rest_client'):
                from model.wp_rest_api import WordPressRESTClient
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
            # STEP 1: Upload FEATURED IMAGE as FIRST content image
            # ========================================
            content_image_urls = []  # Initialize here
            featured_media_id = None # Initialize featured_media_id
            
            if data.image_url and data.image_url.strip():
                # Check if it's a local file path (not a URL)
                if not data.image_url.startswith('http'):
                    self.view.after(0, lambda: self.view.log(f"🖼️ Đang tối ưu hóa ảnh đại diện cho Facebook..."))
                    
                    # FACEBOOK OPTIMIZATION: Use high-quality optimization for featured image
                    image_to_upload = data.image_url  # Default to original
                    try:
                        import os  # Import here to avoid scope issues
                        from model.facebook_thumbnail_optimizer import FacebookThumbnailOptimizer
                        fb_optimizer = FacebookThumbnailOptimizer()
                        
                        # Optimize for Facebook (1200x630px, 95% quality, enhanced sharpness)
                        optimized_path = fb_optimizer.optimize_for_facebook(
                            data.image_url, 
                            enhance=True  # Tăng độ nét, tương phản, màu sắc
                        )
                        
                        if optimized_path and os.path.exists(optimized_path):
                            image_to_upload = optimized_path  # Use Facebook-optimized version
                            print(f"[CONTROLLER] ✅ Using Facebook-optimized image: {optimized_path}")
                            self.view.after(0, lambda: self.view.log(f"✅ Đã tối ưu ảnh cho Facebook (1200x630px, chất lượng cao)"))
                        else:
                            print(f"[CONTROLLER] Facebook optimization failed, using original: {data.image_url}")
                            self.view.after(0, lambda: self.view.log(f"⚠️ Tối ưu thất bại, dùng ảnh gốc"))
                    except Exception as opt_err:
                        print(f"[CONTROLLER] Warning: Could not optimize for Facebook: {opt_err}")
                        print(f"[CONTROLLER] Using original image: {data.image_url}")
                        self.view.after(0, lambda: self.view.log(f"⚠️ Lỗi tối ưu, dùng ảnh gốc"))
                    
                    # Upload as FIRST content image
                    print(f"[CONTROLLER] 📤 Uploading featured image as content image: {image_to_upload}")
                    media_id, media_url = self._upload_image_smart(image_to_upload)
                    
                    if media_url:
                        content_image_urls.append(media_url)  # Add to content images
                        data.image_url = media_url # CRITICAL: Update data.image_url to remote URL for SEO/Meta tags
                        if media_id:
                            featured_media_id = media_id
                            print(f"[CONTROLLER] ✅ Captured featured_media_id: {featured_media_id}")
                        print(f"[CONTROLLER] ✅ Featured image uploaded - URL: {media_url}")
                        self.view.after(0, lambda url=media_url: self.view.log(f"✅ Đã upload ảnh đại diện: {url}"))
                    else:
                        print(f"[CONTROLLER] ⚠️ Featured image upload failed!")
                        self.view.after(0, lambda: self.view.log(f"⚠️ Không thể upload ảnh đại diện"))
                elif data.image_url.startswith('http'):
                    # Already a URL, add directly
                    content_image_urls.append(data.image_url)
            
            print(f"[CONTROLLER] 📸 Content images so far: {len(content_image_urls)}")
            
            # ========================================
            # STEP 2: Upload CONTENT IMAGES (after featured image)
            # ========================================
            # NOTE: content_image_urls already initialized in STEP 1 with featured image
            # Get content images (up to 3) and upload them
            
            # Check if we need to auto-fetch car images
            auto_fetch = getattr(data, 'auto_fetch_images', False)
            has_any_image = any([
                getattr(data, 'content_image', '').strip(),
                getattr(data, 'content_image2', '').strip(),
                getattr(data, 'content_image3', '').strip()
            ])
            
            # Auto-fetch images if enabled and no images provided
            if auto_fetch and not has_any_image:
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
                        
                        # PARALLEL DOWNLOAD + OPTIMIZE - Download and optimize all images at once
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
                                # Optimize immediately after download
                                # Use LOW quality for content images (so featured image is prioritized)
                                # Featured: 1200x630 @ 95% | Content: 360p @ 55% (intentionally lower)
                                optimized_path = image_api.optimize_image_for_upload(local_path, max_width=360, quality=55)
                                return optimized_path
                            return None
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                            future_to_task = {
                                executor.submit(download_and_optimize, task[1], task[2]): task 
                                for task in download_tasks
                            }
                            
                            for future in concurrent.futures.as_completed(future_to_task):
                                task = future_to_task[future]
                                idx, img_url, local_path = task
                                
                                try:
                                    optimized_path = future.result()
                                    if optimized_path and os.path.exists(optimized_path) and os.path.getsize(optimized_path) > 1024:
                                        downloaded_images.append((idx, optimized_path))
                                        self.view.after(0, lambda i=idx: self.view.log(f"✅ Đã tải & tối ưu ảnh {i}"))
                                    else:
                                        self.view.after(0, lambda i=idx: self.view.log(f"⚠️ Ảnh {i} không hợp lệ"))
                                        try:
                                            if local_path and os.path.exists(local_path):
                                                os.remove(local_path)
                                        except:
                                            pass
                                except Exception as e:
                                    self.view.after(0, lambda err=str(e), i=idx: self.view.log(f"⚠️ Lỗi tải ảnh {i}: {err}"))
                        
                        # PARALLEL UPLOAD - Upload all images at once
                        if downloaded_images:
                            self.view.after(0, lambda: self.view.log(f"📤 Đang upload {len(downloaded_images)} ảnh song song lên WordPress..."))
                            
                            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                                future_to_img = {
                                    executor.submit(self._upload_image_smart, img[1]): img 
                                    for img in downloaded_images
                                }
                                
                                for future in concurrent.futures.as_completed(future_to_img):
                                    img = future_to_img[future]
                                    idx, local_path = img
                                    
                                    try:
                                        media_id, uploaded_url = future.result()  # Unpack tuple
                                        
                                        if uploaded_url:
                                            content_image_urls.append(uploaded_url)
                                            self.view.after(0, lambda i=idx: self.view.log(f"✅ Đã upload ảnh {i}"))
                                            
                                            # Auto-save uploaded image to library
                                            try:
                                                success, saved_path = image_api.save_image_to_library(local_path)
                                                if success:
                                                    self.view.after(0, lambda: self.view.log(f"💾 Đã lưu ảnh vào thư viện"))
                                            except Exception as save_err:
                                                print(f"[CONTROLLER] Warning: Could not save to library: {save_err}")
                                        else:
                                            self.view.after(0, lambda i=idx: self.view.log(f"⚠️ Upload ảnh {i} thất bại"))
                                        
                                        # Clean up local file
                                        try:
                                            os.remove(local_path)
                                        except:
                                            pass
                                            
                                    except Exception as e:
                                        self.view.after(0, lambda err=str(e), i=idx: self.view.log(f"⚠️ Lỗi upload ảnh {i}: {err}"))
                        else:
                            self.view.after(0, lambda: self.view.log(f"⚠️ Không có ảnh hợp lệ để upload"))
                    else:
                        self.view.after(0, lambda: self.view.log(f"⚠️ Không tìm thấy ảnh xe phù hợp"))
                        
                except Exception as e:
                    self.view.after(0, lambda err=str(e): self.view.log(f"❌ Lỗi API: {err}"))
                    import traceback
                    traceback.print_exc()
            
            # Process manually provided content images - OPTIMIZE BEFORE UPLOAD
            for i, attr_name in enumerate(['content_image', 'content_image2', 'content_image3'], 1):
                content_image = getattr(data, attr_name, '')
                
                if content_image and content_image.strip():
                    # Check if it's a local file path (not a URL)
                    if not content_image.startswith('http'):
                        # Optimize image before upload for faster speed
                        try:
                            from model.image_api import ImageAPI
                            img_api = ImageAPI()
                            # Use LOW quality for content images (so featured image is prioritized by Facebook)
                            # Featured: 1200x630 @ 95% | Content: 360p @ 55% (intentionally lower)
                            optimized_path = img_api.optimize_image_for_upload(content_image, max_width=360, quality=55)
                            content_image = optimized_path  # Use optimized version
                        except Exception as opt_err:
                            print(f"[CONTROLLER] Warning: Could not optimize image: {opt_err}")
                        
                        # Upload to WordPress using smart method (REST API → Selenium)
                        self.view.after(0, lambda idx=i: self.view.log(f"📤 Đang upload ảnh content {idx}..."))
                        media_id, uploaded_url = self._upload_image_smart(content_image)  # Unpack tuple
                        if uploaded_url:
                            content_image_urls.append(uploaded_url)
                            self.view.after(0, lambda url=uploaded_url, idx=i: self.view.log(f"✅ Đã upload ảnh content {idx}: {url}"))
                            
                            # Auto-save uploaded image to library
                            try:
                                from model.image_api import ImageAPI
                                img_api = ImageAPI()
                                success, saved_path = img_api.save_image_to_library(content_image)
                                if success:
                                    self.view.after(0, lambda: self.view.log(f"💾 Đã lưu ảnh content vào thư viện"))
                            except Exception as save_err:
                                print(f"[CONTROLLER] Warning: Could not save to library: {save_err}")
                        else:
                            self.view.after(0, lambda idx=i: self.view.log(f"⚠️ Không thể upload ảnh content {idx}, bỏ qua..."))
                    else:
                        # Already a URL, use directly
                        content_image_urls.append(content_image)
            
            # DEBUG: Check content images count
            print(f"[CONTROLLER] 📸 Total content images for BlogPost: {len(content_image_urls)}")
            
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
            if not hasattr(self, 'selenium_client') or self.selenium_client.driver is None:
                # Initialize selenium client for image uploads
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
            success, message = auto_client.post_article(post, reuse_selenium_client=self.selenium_client)
            
            # 4. Update UI - PASS TITLE EXPLICITLY
            self.view.after(0, lambda s=success, m=message, b=is_batch, t=post.title: self.view.on_post_finished(s, m, b, t))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Pass title from data if possible, or "Error Post"
            err_title = data.title if hasattr(data, 'title') else "Error Post"
            self.view.after(0, lambda msg=str(e), b=is_batch, t=err_title: self.view.on_post_finished(False, msg, b, t))
