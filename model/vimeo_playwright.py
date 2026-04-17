from playwright.sync_api import sync_playwright
import os
import time
import json
import re

class VimeoPlaywrightHelper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def init_driver(self, headless=True):
        """Initialize Playwright Browser (Chrome Slim)"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
        
        if not self.browser:
            print(f"[VIMEO-PW] Launching Chromium (Headless: {headless})...")
            # Using chromium for "Chrome slim" experience
            # Optimized args for low memory usage
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage", # Fix shared memory issues
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                    "--mute-audio"
                ]
            )

    def close(self):
        """Close browser to free RAM immediately"""
        try:
            if self.context: self.context.close()
            # We keep the browser process running to reuse it for next upload? 
            # Or close it entirely to be safe? 
            # User wants "Anti-Lag", so closing context is usually enough (like closing a tab/window).
            # But creating a new browser instance is also cheap in Playwright.
            # Let's keep browser open, close context.
            self.context = None
            self.page = None
        except:
            pass
            
    def full_close(self):
        """Shut down everything (App exit)"""
        try:
            self.close()
            if self.browser: self.browser.close()
            if self.playwright: self.playwright.stop()
        except: pass
        self.browser = None
        self.playwright = None

    def add_cookies(self, cookies):
        """
        Add cookies to the current context.
        Selenium cookies: [{'name': 'x', 'value': 'y', 'domain': '.vimeo.com', ...}]
        Playwright needs similar.
        """
        if not self.browser:
            self.init_driver(headless=True)
            
        if not self.context:
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 720}, # Smaller viewport = less RAM
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
        # Convert/Filter cookies if necessary
        pw_cookies = []
        for c in cookies:
            if not c: continue # Skip None/Empty cookies
            
            # Fix domain if needed
            new_c = {
                'name': c.get('name'),
                'value': c.get('value'),
                'domain': c.get('domain'),
                'path': c.get('path', '/')
            }
            pw_cookies.append(new_c)
            
        try:
            self.context.add_cookies(pw_cookies)
            print("[VIMEO-PW] Cookies applied.")
        except Exception as e:
            print(f"[VIMEO-PW] Cookie Warning: {e}")

    def upload_video(self, file_path):
        """
        Upload video using Playwright.
        Returns: success, message, data, quota_full
        """
        import os
        if not os.path.exists(file_path):
            return False, "File not found", None, False

        # Ensure we have a context (add_cookies should have created it, otherwise create new)
        if not self.browser: self.init_driver(headless=True)
        if not self.context: 
            self.context = self.browser.new_context()

        try:
            self.page = self.context.new_page()

            # --- NAVIGATION ---
            print("[VIMEO-PW] Navigating to Upload...")
            try:
                self.page.goto("https://vimeo.com/upload", wait_until="domcontentloaded", timeout=60000)
            except Exception as nav_e:
                print(f"[VIMEO-PW] Nav Timeout: {nav_e}")
                return False, "Navigation Timeout/Error", None, False
            
            # Check Login
            time.sleep(2) # Brief wait for redirects
            if "log_in" in self.page.url or "join" in self.page.url:
                 return False, "Not logged in (Cookies missing/invalid)", None, False

            # --- QUOTA CHECK ---
            print("[VIMEO-PW] Checking Quota...")
            try:
                # Fast text check
                body_text = self.page.inner_text("body").lower()
                if "1gb of 1gb" in body_text or "limit reached" in body_text or "quota exceeded" in body_text:
                     return False, "QUOTA_EXCEEDED (Text)", None, True
            except: pass

            # --- UPLOAD ---
            print(f"[VIMEO-PW] Uploading: {os.path.basename(file_path)}")
            
            # Set Input Files (Handles hidden inputs automatically)
            try:
                self.page.set_input_files("input[type='file']", file_path)
            except Exception as e:
                 # Try finding it specifically if generic selector fails
                 print(f"[VIMEO-PW] Input error: {e}. Retrying with loose selector...")
                 self.page.set_input_files("input", file_path)
            
            # --- WAIT FOR UPLOAD TO START ---
            print("[VIMEO-PW] File sent. Waiting for upload to start...")
            
            # Wait for URL change to /manage/videos/...
            video_id = None
            redirected = False
            start_time = time.time()
            
            # Polling loop (Playwright doesn't have a simple "wait_for_url_contains" that returns the url easily without throw)
            while time.time() - start_time < 60:
                curr_url = self.page.url
                if "/manage/videos/" in curr_url and "upload" not in curr_url:
                    video_id = curr_url.split("/videos/")[-1].split("/")[0]
                    redirected = True
                    break
                
                # Check for "Upload complete" text
                try:
                    if self.page.is_visible("text=Upload complete") or self.page.is_visible("text=Go to video"):
                        # Try to grab link
                        # <a href="/manage/videos/...">
                        href = self.page.get_attribute("a[href*='/manage/videos/']", "href")
                        if href:
                            video_id = href.split("/videos/")[-1].split("/")[0]
                            redirected = True
                            break
                except: pass
                
                # Check Quota Popup
                try:
                    if self.page.is_visible("text=Quota exceeded") or self.page.is_visible("text=Not enough storage"):
                        return False, "QUOTA_EXCEEDED (Popup)", None, True
                except: pass
                
                time.sleep(1)

            if not redirected:
                 return True, "Upload started (Background processing)", None, False
            
            print(f"[VIMEO-PW] Video ID: {video_id}")

            # --- WAIT FOR PROCESSING / EMBED ---
            # We stay on the page to let it process
            print("[VIMEO-PW] Monitoring status...")
            
            # Smart Wait Loop
            # We look for "Optimization complete" OR "Embed" button
            wait_start = time.time()
            is_ready = False
            
            while time.time() - wait_start < 600: # 10 mins max
                try:
                    # check for success text
                    if self.page.is_visible("text=Upload complete") or self.page.is_visible("text=Complete"):
                        print("[VIMEO-PW] Upload Complete detected.")
                        time.sleep(5) # Let it settle
                        is_ready = True
                        break
                        
                    # check for player
                    if self.page.is_visible(".vp-controls") or self.page.is_visible("button[aria-label='Play']"):
                        print("[VIMEO-PW] Player Ready.")
                        is_ready = True
                        break
                        
                    time.sleep(5)
                except: time.sleep(5)
            
            # --- GENERATE OUTPUT ---
            video_title = os.path.basename(file_path) # Fallback title
            try:
                # Try getting real title input
                val = self.page.input_value("input[data-qa='title-input']")
                if val: video_title = val
            except: pass

            # Fallback Embed Code (100% Reliability, 0% Clipboard Issues)
            embed_code = (f'<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/{video_id}?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" '
                          f'frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media" '
                          f'style="position:absolute;top:0;left:0;width:100%;height:100%;" title="{video_title}"></iframe></div>'
                          f'<script src="https://player.vimeo.com/api/player.js"></script>')

            # Smart Thumbnail Generation
            thumbnail_path = None
            try:
                # Smart Thumbnail Generation - RE-ENABLED (Saved to separate folder)
                thumb_dir = os.path.join(os.getcwd(), "video_frames")
                if not os.path.exists(thumb_dir): os.makedirs(thumb_dir)
                filename = f"thumb_{video_id}.jpg"
                save_path = os.path.join(thumb_dir, filename)
                
                # Use the existing Smart Extractor logic
                extracted_thumb = self.extract_smart_thumbnail(file_path, save_path)
                if extracted_thumb:
                     thumbnail_path = extracted_thumb
                     print(f"[VIMEO-PW] Smart Thumbnail: {thumbnail_path}")
            except Exception as e:
                print(f"[VIMEO-PW] Thumb Error: {e}")

            return True, "Upload Success", {
                "video_link": f"https://vimeo.com/{video_id}",
                "embed_code": embed_code,
                "video_id": video_id,
                "title": video_title,
                "thumbnail": thumbnail_path
            }, False

        except Exception as e:
            return False, f"Error: {e}", None, False

    def extract_smart_thumbnail(self, video_path, output_path):
        """Scans video for best frame using OpenCV"""
        try:
            import cv2
            import numpy as np
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened(): return None
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / (fps if fps > 0 else 30)
            
            # Avoid beginning/end
            start_sec = max(2, duration * 0.1)
            end_sec = min(duration - 2, duration * 0.9)
            
            best_frame = None
            best_score = -1
            
            # Check 10 candidate frames
            timestamps = np.linspace(start_sec, end_sec, num=10)
            
            for t in timestamps:
                cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
                ret, frame = cap.read()
                if not ret: continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                score = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                if score > best_score:
                    best_score = score
                    best_frame = frame
            
            cap.release()
            
            if best_frame is not None:
                cv2.imwrite(output_path, best_frame)
                return output_path
            return None
        except:
            return None
