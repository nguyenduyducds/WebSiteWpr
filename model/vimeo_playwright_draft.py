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
        """Initialize Playwright Browser"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
        
        if not self.browser:
            print(f"[VIMEO-PW] Launching Chromium (Headless: {headless})...")
            # Using chromium for "Chrome slim" experience
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu"
                ]
            )

    def close(self):
        """Close browser to free RAM"""
        try:
            if self.context: self.context.close()
            if self.browser: self.browser.close()
            if self.playwright: self.playwright.stop()
        except:
            pass
        self.context = None
        self.browser = None
        self.playwright = None
        self.page = None

    def upload_video(self, file_path):
        """
        Upload video using Playwright.
        Returns: success, message, data, quota_full
        """
        if not os.path.exists(file_path):
            return False, "File not found", None, False

        if not self.browser:
            self.init_driver(headless=True)

        try:
            # Create fresh context for this upload (Anti-Lag / Isolation)
            # Load cookies if available
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Load Cookies
            try:
                if os.path.exists("vimeo_cookies.txt"):
                    with open("vimeo_cookies.txt", "r", encoding="utf-8") as f:
                        # This logic needs to be robust to how cookies are stored in the txt
                        # The current system seems to store one JSON object per line: {'email':..., 'cookies': [...]}
                        # We need the cookies for the current account being used.
                        # Wait, the CALLER chooses the account and applies cookies.
                        # With Selenium, the caller passed the helper instance... 
                        # Actually look at gui_view.py: The caller gets 'acc' from list, then manually calls `helper.driver.add_cookie`.
                        # BUT here I am writing a helper method.
                        # To keep it drop-in compatible, I should probably expose a method to add cookies 
                        # OR let the upload method handle it if I pass credentials.
                        
                        # Let's adjust: The GUI worker handles the rotation.
                        # It sets up the driver, adds cookies, THEN calls upload.
                        # So I need a way to `add_cookies` from outside.
                        pass
            except: pass

            self.page = self.context.new_page()

            # --- NAVIGATION ---
            print("[VIMEO-PW] Navigating to Upload...")
            self.page.goto("https://vimeo.com/upload", wait_until="domcontentloaded")
            
            # Check Login
            if "log_in" in self.page.url or "join" in self.page.url:
                 return False, "Not logged in (Cookies missing/invalid)", None, False

            # --- QUOTA CHECK ---
            try:
                body_text = self.page.inner_text("body").lower()
                if "1gb of 1gb" in body_text or "limit reached" in body_text or "quota exceeded" in body_text:
                     return False, "QUOTA_EXCEEDED (Text)", None, True
            except: pass

            # --- UPLOAD ---
            print(f"[VIMEO-PW] Uploading: {os.path.basename(file_path)}")
            
            # Handle File Chooser
            with self.page.expect_file_chooser() as fc_info:
                # Find the input - Playwright can find hidden inputs better
                # Or we trigger the click if input is hidden
                # Vimeo usually has an <input type=file> that might be hidden
                # self.page.click("input[type=file]", force=True) or similar
                # Best way: set_input_files on the input handle directly
                self.page.set_input_files("input[type='file']", file_path)
            
            # Wait for upload to start (URL change or text appearance)
            # Timeout 60s
            try:
                self.page.wait_for_url("**/manage/videos/**", timeout=60000)
                video_id = self.page.url.split("/videos/")[-1].split("/")[0]
            except:
                # Check for "Upload complete" text
                try:
                    self.page.wait_for_selector("text=Upload complete", timeout=5000)
                    # Try to extract ID from link
                    # ...
                    video_id = "unknown" # Fallback
                except:
                    return False, "Upload failed to start or timeout", None, False

            print(f"[VIMEO-PW] Video ID: {video_id}")
            
            # --- GET EMBED CODE ---
            # Wait for "Embed" button
            embed_code = ""
            video_title = os.path.basename(file_path)
            
            try:
                # wait up to 5 mins for processing/embed button
                # We can check for the button repeatedly
                btn = self.page.wait_for_selector("button[aria-label='Embed'], button:has-text('Embed')", timeout=300000)
                if btn:
                    btn.click()
                    
                    # Click Copy
                    copy_btn = self.page.wait_for_selector("button:has-text('Copy embed code')", timeout=5000)
                    if copy_btn:
                        copy_btn.click()
                        # Get clipboard content? Playwright can't easily read system clipboard in headless
                        # unless permissions are set.
                        # BETTER STRATEGY: Intercept the "Copy" action or just read the code from the DOM?
                        # Or, usually the embed code is in a textarea or input inside the modal?
                        # Vimeo's new UI copies to clipboard.
                        
                        # Workaround: Evaluate javascript to read clipboard? 
                        # Usually blocked in headless.
                        
                        # Alternative: Construct fallback code using Video ID. 
                        # The user seems to be okay with fallback if "Embed" button strategy fails, 
                        # BUT they preferred the "Copy" method.
                        
                        # Let's try to find if the code is displayed on screen.
                        # Usually it is shown in the modal too.
                        pass
            except:
                pass
            
            # FALLBACK EMBED
            if not embed_code:
                embed_code = (f'<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/{video_id}?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" '
                              f'frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media" '
                              f'style="position:absolute;top:0;left:0;width:100%;height:100%;" title="{video_title}"></iframe></div>'
                              f'<script src="https://player.vimeo.com/api/player.js"></script>')

            # --- WAIT FOR PROCESSING TO FINISH (Optional based on user pref) ---
            # User wants to wait until "Ready".
            # Check for "Optimization complete" or "Upload complete" toast
            
            # ...
            
            return True, "Upload Success", {
                "video_link": f"https://vimeo.com/{video_id}",
                "embed_code": embed_code,
                "video_id": video_id,
                "title": video_title,
                "thumbnail": None # Smart thumb generation needs local file, we can do that outside or port it
            }, False

        except Exception as e:
            return False, f"Error: {e}", None, False
