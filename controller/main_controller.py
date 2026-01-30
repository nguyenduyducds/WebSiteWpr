from model.wp_model import BlogPost, WordPressClient
from model.config_manager import ConfigManager
from view.gui_view import GUIView
import threading

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

    def _process_post(self, data, is_batch=False):
        try:
            from model.wp_model import BlogPost
            
            # 1. Create Post Object (Content Generation)
            # Fix: Nếu có video URL nhưng content trống → Auto-generate
            content = data.content.strip() if data.content else ""
            if data.video_url and not content:
                raw_content = ""  # Để trống để auto-generate với video
            else:
                raw_content = content  # Dùng content user nhập
            
            # Get content images (up to 3) and upload them first
            content_image_urls = []
            
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
                        os.makedirs("thumbnails", exist_ok=True)
                        
                        for idx, img_url in enumerate(car_image_urls, 1):
                            try:
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                import random
                                random_suffix = random.randint(1000, 9999)
                                local_path = f"thumbnails/car_api_{timestamp}_{random_suffix}_{idx}.jpg"
                                
                                # Download with retry
                                self.view.after(0, lambda i=idx: self.view.log(f"📥 Đang tải ảnh {i}..."))
                                
                                if image_api.download_image(img_url, local_path):
                                    # Verify file exists and has content
                                    if os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
                                        # Upload to WordPress
                                        self.view.after(0, lambda i=idx: self.view.log(f"📤 Đang upload ảnh {i} lên WordPress..."))
                                        uploaded_url = self.selenium_client.upload_image_to_media(local_path)
                                        
                                        if uploaded_url:
                                            content_image_urls.append(uploaded_url)
                                            self.view.after(0, lambda i=idx: self.view.log(f"✅ Đã upload ảnh {i}"))
                                        else:
                                            self.view.after(0, lambda i=idx: self.view.log(f"⚠️ Upload ảnh {i} thất bại"))
                                        
                                        # Clean up local file
                                        try:
                                            os.remove(local_path)
                                        except:
                                            pass
                                    else:
                                        self.view.after(0, lambda i=idx: self.view.log(f"⚠️ Ảnh {i} không hợp lệ, bỏ qua"))
                                        try:
                                            os.remove(local_path)
                                        except:
                                            pass
                                else:
                                    self.view.after(0, lambda i=idx: self.view.log(f"⚠️ Tải ảnh {i} thất bại"))
                                    
                            except Exception as e:
                                self.view.after(0, lambda err=str(e), i=idx: self.view.log(f"⚠️ Lỗi xử lý ảnh {i}: {err}"))
                    else:
                        self.view.after(0, lambda: self.view.log(f"⚠️ Không tìm thấy ảnh xe phù hợp"))
                        
                except Exception as e:
                    self.view.after(0, lambda err=str(e): self.view.log(f"❌ Lỗi API: {err}"))
                    import traceback
                    traceback.print_exc()
            
            # Process manually provided images
            for i, attr_name in enumerate(['content_image', 'content_image2', 'content_image3'], 1):
                content_image = getattr(data, attr_name, '')
                
                if content_image and content_image.strip():
                    # Check if it's a local file path (not a URL)
                    if not content_image.startswith('http'):
                        # Upload to WordPress Media Library
                        self.view.after(0, lambda idx=i: self.view.log(f"📤 Đang upload ảnh content {idx}..."))
                        uploaded_url = self.selenium_client.upload_image_to_media(content_image)
                        if uploaded_url:
                            content_image_urls.append(uploaded_url)
                            self.view.after(0, lambda url=uploaded_url, idx=i: self.view.log(f"✅ Đã upload ảnh content {idx}: {url}"))
                        else:
                            self.view.after(0, lambda idx=i: self.view.log(f"⚠️ Không thể upload ảnh content {idx}, bỏ qua..."))
                    else:
                        # Already a URL, use directly
                        content_image_urls.append(content_image)
            
            post = BlogPost(data.title, data.video_url, data.image_url, raw_content, content_images=content_image_urls)
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
