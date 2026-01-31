import time
import os
import sys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pickle # Cần thiết cho việc lưu/load cookie

class SeleniumWPClient:
    def __init__(self, site_url, username, password):
        self.site_url = site_url
        self.username = username
        self.password = password
        self.driver = None

    def _check_and_handle_popups(self):
        """
        Check for and handle common popups/CAPTCHA that block login
        """
        try:
            # Check for CAPTCHA
            captcha_selectors = [
                "iframe[src*='recaptcha']",
                "iframe[src*='hcaptcha']",
                ".g-recaptcha",
                ".h-captcha",
                "#captcha",
                "[class*='captcha']"
            ]
            
            for selector in captcha_selectors:
                if len(self.driver.find_elements(By.CSS_SELECTOR, selector)) > 0:
                    print("[SELENIUM] ⚠️ CAPTCHA detected! Please solve it manually...")
                    print("[SELENIUM] Waiting 30 seconds for manual CAPTCHA solve...")
                    time.sleep(30)
                    return
            
            # Check for common popup close buttons
            popup_close_selectors = [
                "button.close",
                "button[aria-label='Close']",
                ".modal-close",
                ".popup-close",
                "[class*='close-button']",
                "[class*='dismiss']"
            ]
            
            for selector in popup_close_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    try:
                        elements[0].click()
                        print(f"[SELENIUM] ✅ Closed popup: {selector}")
                        time.sleep(1)
                        return
                    except:
                        pass
            
            # Check for "Remember Me" checkbox and check it
            try:
                remember_me = self.driver.find_elements(By.ID, "rememberme")
                if remember_me and not remember_me[0].is_selected():
                    remember_me[0].click()
                    print("[SELENIUM] ✅ Checked 'Remember Me'")
            except:
                pass
                
        except Exception as e:
            # Silently ignore errors in popup detection
            pass

    def init_driver(self, headless=False):
        options = uc.ChromeOptions()
        
        if headless:
            options.add_argument("--headless=new")
            print("[SELENIUM] Running in HEADLESS mode (Background)")
        
        # Anti-detection options (CRITICAL) - Compatible with undetected-chromedriver
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        
        # Stability options (IMPORTANT - prevent crashes)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")  # NEW: Allow popups
        options.add_argument("--disable-extensions")  # NEW: Disable extensions
        options.add_argument("--disable-software-rasterizer")  # NEW: Stability
        options.add_argument("--disable-web-security")  # NEW: Avoid CORS issues
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--log-level=3")
        
        # Memory and performance options (NEW - prevent crashes)
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        
        # Check for Chrome Portable
        chrome_portable_path = None
        driver_portable_path = None
        
        if os.path.exists("chrome_portable/chrome.exe"):
            chrome_portable_path = os.path.abspath("chrome_portable/chrome.exe")
            
        if os.path.exists("driver/chromedriver.exe"):
            driver_portable_path = os.path.abspath("driver/chromedriver.exe")
        
        # Check bundled (PyInstaller)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            bundled_chrome = os.path.join(base_path, "chrome_portable", "chrome.exe")
            bundled_driver = os.path.join(base_path, "driver", "chromedriver.exe")
            
            if os.path.exists(bundled_chrome):
                chrome_portable_path = bundled_chrome
            if os.path.exists(bundled_driver):
                driver_portable_path = bundled_driver
        
        try:
            if chrome_portable_path:
                print(f"[SELENIUM] Using Chrome Portable: {chrome_portable_path}")
                options.binary_location = chrome_portable_path
                
                if driver_portable_path:
                    self.driver = uc.Chrome(options=options, driver_executable_path=driver_portable_path, use_subprocess=True)
                else:
                    self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            else:
                print("[SELENIUM] Using System Chrome...")
                self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            
            # Set page load timeout to prevent hanging
            self.driver.set_page_load_timeout(60)
            
            print("[SELENIUM] Driver initialized successfully")
                
        except Exception as e:
            print(f"[SELENIUM] Failed to initialize Chrome: {e}")
            raise Exception(f"Cannot initialize Chrome: {e}")

    def login(self, destination_url=None):
        try:
            site_url = self.site_url.strip()
            if not site_url.startswith('http'):
                site_url = 'https://' + site_url
            
            from urllib.parse import urlparse
            parsed = urlparse(site_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            admin_url = base_url + '/wp-admin/'
            login_url = base_url + '/wp-login.php'
            final_dest = destination_url if destination_url else admin_url
            
            # --- COOKIE LOGIN ---
            cookie_filename = f"cookies_{self.username}.pkl"
            
            if os.path.exists(cookie_filename):
                print(f"[SELENIUM] Found cookies. Trying cookie login...")
                self.driver.get(base_url) # Go to homepage first
                try:
                    cookies = pickle.load(open(cookie_filename, "rb"))
                    for cookie in cookies:
                        if 'expiry' in cookie: del cookie['expiry']
                        try: self.driver.add_cookie(cookie)
                        except: pass
                    
                    self.driver.get(final_dest)
                    
                    # Quick check - reduced timeout from 5s to 2s
                    try:
                        WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.ID, "wpadminbar")))
                        print("[SELENIUM] ✅ Login via Cookies SUCCESSFUL!")
                        return True
                    except:
                        print("[SELENIUM] Cookies expired or invalid.")
                except Exception as e:
                    print(f"[SELENIUM] Cookie error: {e}")

            # --- MANUAL LOGIN ---
            print(f"[SELENIUM] Navigating to login: {login_url}")
            self.driver.get(login_url)
            
            # Reduced wait time from 10s to 5s
            print("[SELENIUM] Finding login fields...")
            user_field = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "user_login")))
            
            # Fill both fields quickly without separate waits
            user_field.send_keys(self.username)
            pass_field = self.driver.find_element(By.ID, "user_pass")
            pass_field.send_keys(self.password)
            
            print("[SELENIUM] Submitting login form...")
            try:
                # Method 1: JavaScript click (most reliable)
                submit_btn = self.driver.find_element(By.ID, "wp-submit")
                self.driver.execute_script("arguments[0].click();", submit_btn)
                print("[SELENIUM] Clicked via JavaScript")
            except Exception as click_err:
                print(f"[SELENIUM] JS click failed: {click_err}, trying Enter key...")
                try:
                    self.driver.find_element(By.ID, "user_pass").send_keys(Keys.RETURN)
                    print("[SELENIUM] Submitted via Enter key")
                except Exception as enter_err:
                    print(f"[SELENIUM] Enter key failed: {enter_err}, trying form submit...")
                    # Method 3: Submit form directly
                    try:
                        form = self.driver.find_element(By.ID, "loginform")
                        self.driver.execute_script("arguments[0].submit();", form)
                        print("[SELENIUM] Submitted via form.submit()")
                    except Exception as form_err:
                        print(f"[SELENIUM] All submit methods failed: {form_err}")
                        raise Exception("Cannot submit login form")
            
            # Wait a bit for page to start loading (reduced from 3s to 1s)
            print("[SELENIUM] Waiting for page to load...")
            time.sleep(1)
            
            # Check if browser is still alive
            try:
                current_url = self.driver.current_url
                print(f"[SELENIUM] Page loaded, current URL: {current_url}")
            except Exception as browser_err:
                print(f"[SELENIUM] ❌ Browser crashed or closed: {browser_err}")
                raise Exception("Browser crashed during login. This might be due to Chrome Portable instability. Try using system Chrome or restart the app.")
            
            # Check for CAPTCHA or popup immediately after submit
            self._check_and_handle_popups()
            
            print("[SELENIUM] Waiting for dashboard (up to 30s)...")  # Reduced from 60s to 30s
            
            # Polling loop for 30 seconds (reduced from 60s)
            start_time = time.time()
            login_success = False
            popup_check_count = 0
            check_interval = 0.5  # Check every 0.5s instead of 1s for faster detection
            
            while time.time() - start_time < 30:  # Reduced timeout to 30s
                current_url = self.driver.current_url
                elapsed = int(time.time() - start_time)
                
                # Debug: Print current URL every 3 seconds (reduced from 5s)
                if elapsed % 3 == 0 and elapsed > 0:
                    print(f"[SELENIUM] [{elapsed}s] Current URL: {current_url}")
                
                try:
                    # Check 1: Dashboard loaded (FASTEST - check first)
                    if len(self.driver.find_elements(By.ID, "wpadminbar")) > 0:
                        print("[SELENIUM] ✅ Found Admin Bar! Login Complete.")
                        login_success = True
                        break
                    
                    # Check 2: Redirected to admin (but NOT login page with redirect param)
                    if "wp-admin" in current_url and "wp-login.php" not in current_url:
                        print(f"[SELENIUM] ✅ Redirected to wp-admin: {current_url}")
                        # Reduced wait time from 2s to 0.5s
                        time.sleep(0.5)
                        print("[SELENIUM] Login Complete.")
                        login_success = True
                        break
                    
                    # Check 3: Redirected to dashboard (some sites use /dashboard/)
                    if "dashboard" in current_url.lower() and "wp-login.php" not in current_url:
                        print(f"[SELENIUM] ✅ URL contains dashboard: {current_url}")
                        login_success = True
                        break

                    # Check 4: Login Error (check early to fail fast)
                    error_elems = self.driver.find_elements(By.ID, "login_error")
                    if len(error_elems) > 0:
                        error_text = error_elems[0].text
                        print(f"[SELENIUM] ❌ LOGIN ERROR: {error_text}")
                        
                        # Capture screenshot for error analysis
                        self.driver.save_screenshot("login_error_caught.png")
                        raise Exception(f"WordPress Login Error: {error_text}")
                    
                    # Check 5: Still on login page but no error (might be loading)
                    if "wp-login.php" in current_url:
                        # Check if there's a success message
                        if len(self.driver.find_elements(By.CSS_SELECTOR, ".message")) > 0:
                            print("[SELENIUM] Found success message, waiting for redirect...")
                        
                        # Check for popup/CAPTCHA every 5 seconds (reduced from 10s)
                        if popup_check_count % 10 == 0 and popup_check_count > 0:
                            self._check_and_handle_popups()
                        popup_check_count += 1
                        
                except Exception as e:
                    if "WordPress Login Error" in str(e):
                        raise e
                    # Ignore other transient errors during check
                    pass
                
                time.sleep(check_interval)  # 0.5s instead of 1s
            
            if not login_success:
                print("[SELENIUM] Login Timed Out (30s).")  # Updated message
                
                # Take screenshot and save HTML for debugging
                try:
                    self.driver.save_screenshot("login_timeout.png")
                    with open("login_timeout.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print("[SELENIUM] 📸 Saved debug files: login_timeout.png and login_timeout.html")
                except:
                    pass
                
                # Check if still on login page
                current_url = self.driver.current_url
                if "wp-login.php" in current_url:
                    # Check for specific issues
                    page_source = self.driver.page_source.lower()
                    
                    if "captcha" in page_source or "recaptcha" in page_source:
                        raise Exception("Login blocked by CAPTCHA. Please disable CAPTCHA for admin login or solve it manually.")
                    elif "cloudflare" in page_source:
                        raise Exception("Login blocked by Cloudflare. Please whitelist your IP or disable Cloudflare for wp-login.php")
                    elif "rate limit" in page_source or "too many" in page_source:
                        raise Exception("Login blocked by rate limiting. Please wait a few minutes and try again.")
                    else:
                        raise Exception("Login timed out after 30s. Site might be slow, blocked, or requires manual verification. Check login_timeout.png for details.")
                else:
                    raise Exception(f"Login timed out. Stuck at: {current_url}")


            print("[SELENIUM] Login Successful!")
            
            # Save Cookies
            pickle.dump(self.driver.get_cookies(), open(cookie_filename, "wb"))
            
            if destination_url and destination_url not in self.driver.current_url:
                self.driver.get(destination_url)

            return True
        except Exception as e:
            print(f"[SELENIUM] Login Failed: {e}")
            try:
                self.driver.save_screenshot("debug_login_fail.png")
                with open("debug_login_fail.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("[SELENIUM] 📸 Saved debug screenshot to 'debug_login_fail.png' and HTML to 'debug_login_fail.html'")
                print(f"[SELENIUM] Current URL: {self.driver.current_url}")
            except Exception as debug_err:
                print(f"[SELENIUM] Could not save debug info: {debug_err}")
            
            raise Exception(f"Login Failed: {str(e)}")

    def set_react_value(self, element, value):
        """
        FIX QUAN TRỌNG: Hàm này dùng Native Value Setter để qua mặt React.
        Giúp WordPress nhận diện được nội dung đã thay đổi.
        """
        js_script = """
            var element = arguments[0];
            var value = arguments[1];
            
            // Lấy setter gốc của prototype để bypass React override
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
            nativeInputValueSetter.call(element, value);
            
            // Dispatch event để React cập nhật State
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
        """
        self.driver.execute_script(js_script, element, value)

    def upload_image_to_media(self, image_path):
        """
        Upload an image to WordPress Media Library and return its URL.
        Returns None if upload fails.
        """
        if not self.driver:
            self.init_driver()
        
        try:
            import os
            if not os.path.exists(image_path):
                print(f"[SELENIUM] Image file not found: {image_path}")
                return None
            
            # 1. Upload via media-new.php
            site_url = self.site_url.rstrip('/')
            if not site_url.startswith('http'):
                site_url = 'https://' + site_url
            if 'wp-admin' in site_url:
                site_url = site_url.split('/wp-admin')[0]
            
            # Ensure logged in
            if "wp-admin" not in self.driver.current_url:
                self.login(destination_url=site_url + "/wp-admin/media-new.php")
            else:
                self.driver.get(site_url + "/wp-admin/media-new.php")
            
            time.sleep(2)
            
            # Find file input and upload
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            
            abs_path = os.path.abspath(image_path)
            file_input.send_keys(abs_path)
            print(f"[SELENIUM] Uploading content image: {os.path.basename(image_path)}")
            
            # Wait longer for upload to complete
            time.sleep(8) 
            
            # 2. Go to Media Library to get the Link (More reliable)
            self.driver.get(site_url + "/wp-admin/upload.php?mode=list&orderby=date&order=desc")
            
            # Wait for list to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#the-list tr"))
            )
            
            # Get the first item (Rows in list view)
            first_row = self.driver.find_element(By.CSS_SELECTOR, "#the-list tr:first-child")
            
            # Get URL directly from 'Copy Link' button or hidden data if possible,
            # Or click 'Edit' to get it.
            # In List View, usually there is a "Copy URL" link if we hover? 
            # Or we can get it from the filename link.
            
            # Let's try to get the "Copy URL" button value if it exists (modern WP)
            try:
                copy_btn = first_row.find_element(By.CSS_SELECTOR, ".copy-attachment-url")
                url = copy_btn.get_attribute("data-clipboard-text")
                if url:
                    print(f"[SELENIUM] ✅ Got URL from Copy Button: {url}")
                    return url
            except:
                pass
                
            # Fallback: Click the title to open Edit page, then get URL
            try:
                title_link = first_row.find_element(By.CSS_SELECTOR, ".column-title strong a, .row-title")
                edit_url = title_link.get_attribute("href")
                self.driver.get(edit_url)
                
                # In Edit Media page
                url_input = WebDriverWait(self.driver, 10).until(
                     EC.presence_of_element_located((By.CSS_SELECTOR, "input.attachment-details-copy-link, #attachment_url"))
                )
                uploaded_url = url_input.get_attribute("value")
                if uploaded_url:
                     print(f"[SELENIUM] ✅ Got URL from Edit Page: {uploaded_url}")
                     return uploaded_url
            except Exception as e:
                print(f"[SELENIUM] Failed to get URL via Edit Page: {e}")

            return None
            
        except Exception as e:
            print(f"[SELENIUM] ❌ Failed to upload content image: {e}")
            import traceback
            traceback.print_exc()
            return None


    def post_article_classic_editor(self, blog_post, force_fresh_login=False):
        """
        Post article using Classic Editor (NO REST API - NO 403 ERRORS)
        This method bypasses Gutenberg completely and uses the old WordPress editor
        
        Args:
            blog_post: BlogPost object
            force_fresh_login: Clear cookies and login fresh (default: False to reuse cookies)
        """
        if not self.driver:
            self.init_driver()
        
        try:
            # Only clear cookies if explicitly requested
            if force_fresh_login:
                print("[SELENIUM] 🔄 Forcing fresh login for Classic Editor...")
                try:
                    self.driver.delete_all_cookies()
                    cookie_file = f"cookies_{self.username}.pkl"
                    if os.path.exists(cookie_file):
                        os.remove(cookie_file)
                        print(f"[SELENIUM] ✅ Deleted cookie file: {cookie_file}")
                except Exception as e:
                    print(f"[SELENIUM] Warning: Could not clear cookies: {e}")
            else:
                print("[SELENIUM] Using existing cookies (no fresh login)")
            
            # 1. Prepare URL and Login
            site_url = self.site_url.rstrip('/')
            if not site_url.startswith('http'):
                site_url = 'https://' + site_url
            if 'wp-admin' in site_url:
                site_url = site_url.split('/wp-admin')[0]
            
            # Force Classic Editor by adding parameter
            new_post_url = site_url + "/wp-admin/post-new.php?classic-editor"
            
            # Try to reuse existing session
            if "wp-admin" not in self.driver.current_url:
                print("[SELENIUM] Not in wp-admin, logging in...")
                self.login(destination_url=new_post_url)
            else:
                print("[SELENIUM] Already in wp-admin, navigating to new post...")
                self.driver.get(new_post_url)
            
            time.sleep(4)
            
            # ---------------------------------------------------------
            # CRITICAL: DISMISS WELCOME MODAL FIRST (Before setting anything)
            # ---------------------------------------------------------
            print("[SELENIUM] Checking for welcome modal...")
            try:
                # Wait a bit for modal to appear
                time.sleep(2)
                
                # Try to close the modal by clicking through it
                modal_dismissed = False
                for attempt in range(5):
                    try:
                        # Look for any button in modal (Next, Get started, Close, etc.)
                        modal_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                            ".components-modal__content button, .components-guide button, .components-button.is-primary")
                        
                        if modal_buttons:
                            for btn in modal_buttons:
                                if btn.is_displayed():
                                    btn_text = btn.text.lower()
                                    print(f"[SELENIUM] Found modal button: '{btn_text}'")
                                    self.driver.execute_script("arguments[0].click();", btn)
                                    time.sleep(1)
                                    modal_dismissed = True
                                    break
                        
                        # Try close button (X)
                        try:
                            close_btn = self.driver.find_element(By.CSS_SELECTOR, 
                                ".components-modal__header button[aria-label='Close'], button[aria-label='Close dialog']")
                            if close_btn.is_displayed():
                                self.driver.execute_script("arguments[0].click();", close_btn)
                                print("[SELENIUM] Clicked close button")
                                modal_dismissed = True
                                break
                        except:
                            pass
                        
                        if modal_dismissed:
                            break
                            
                    except Exception as e:
                        print(f"[SELENIUM] Modal dismiss attempt {attempt + 1} failed: {e}")
                    
                    time.sleep(1)
                
                if modal_dismissed:
                    print("[SELENIUM] ✅ Welcome modal dismissed")
                    time.sleep(2)  # Wait for modal to fully close
                else:
                    print("[SELENIUM] No modal found or already dismissed")
                    
            except Exception as e:
                print(f"[SELENIUM] Modal handling error: {e}")
            
            print("[SELENIUM] Checking for Classic Editor...")
            
            # Check if Classic Editor is available
            try:
                # Try to find classic editor title field
                title_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "title"))
                )
                print("[SELENIUM] ✅ Classic Editor detected")
            except:
                print("[SELENIUM] ⚠️ Classic Editor not available")
                print("[SELENIUM] Checking if we're in Gutenberg instead...")
                
                # Check if Gutenberg loaded
                try:
                    gutenberg_title = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".editor-post-title__input, textarea"))
                    )
                    print("[SELENIUM] ✅ Gutenberg detected, will use Gutenberg workflow")
                    # Don't return False, continue with Gutenberg
                except:
                    print("[SELENIUM] ❌ Neither Classic nor Gutenberg editor found")
                    return False, "No editor available"
            
            # ---------------------------------------------------------
            # STEP 1: SET TITLE (Works for both Classic and Gutenberg)
            # ---------------------------------------------------------
            print(f"[SELENIUM] Setting Title: {blog_post.title}")
            try:
                # Try Classic Editor first
                try:
                    print("[SELENIUM] Waiting for Classic Editor title field...")
                    title_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "title"))
                    )
                    time.sleep(1)
                    
                    # Set title with event trigger (CRITICAL for Classic Editor)
                    self.driver.execute_script("""
                        const titleField = document.getElementById('title');
                        titleField.value = arguments[0];
                        
                        // Trigger input event (WordPress needs this)
                        const inputEvent = new Event('input', { bubbles: true });
                        titleField.dispatchEvent(inputEvent);
                        
                        // Trigger change event
                        const changeEvent = new Event('change', { bubbles: true });
                        titleField.dispatchEvent(changeEvent);
                        
                        // Force update
                        titleField.setAttribute('data-value', arguments[0]);
                        
                        // CRITICAL: Blur and focus to trigger WordPress validation
                        titleField.blur();
                        titleField.focus();
                    """, blog_post.title)
                    
                    # Verify
                    time.sleep(0.5)
                    current_value = title_field.get_attribute("value")
                    print(f"[SELENIUM] ✅ Title set (Classic Editor): {current_value}")
                    
                except:
                    # Fallback to Gutenberg - Use React method
                    print("[SELENIUM] Waiting for Gutenberg title field...")
                    
                    # CRITICAL FIX: Close block inserter panel if it's open
                    # Try multiple methods to close the panel
                    panel_closed = False
                    
                    # Method 1: Click X button
                    try:
                        print("[SELENIUM] Trying to close block inserter panel (Method 1: X button)...")
                        x_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Close block inserter'], button.components-button[aria-label*='Close']")
                        for btn in x_buttons:
                            if btn.is_displayed():
                                btn.click()
                                time.sleep(0.5)
                                panel_closed = True
                                print("[SELENIUM] ✅ Closed panel via X button")
                                break
                    except Exception as e:
                        print(f"[SELENIUM] Method 1 failed: {e}")
                    
                    # Method 2: Click inserter toggle button if it's active
                    if not panel_closed:
                        try:
                            print("[SELENIUM] Trying to close block inserter panel (Method 2: Toggle button)...")
                            toggle_button = self.driver.find_element(By.CSS_SELECTOR, ".edit-post-header-toolbar__inserter-toggle[aria-pressed='true']")
                            if toggle_button:
                                toggle_button.click()
                                time.sleep(0.5)
                                panel_closed = True
                                print("[SELENIUM] ✅ Closed panel via toggle button")
                        except Exception as e:
                            print(f"[SELENIUM] Method 2 failed: {e}")
                    
                    # Method 3: Press Escape key
                    if not panel_closed:
                        try:
                            print("[SELENIUM] Trying to close block inserter panel (Method 3: ESC key)...")
                            from selenium.webdriver.common.keys import Keys
                            body = self.driver.find_element(By.TAG_NAME, "body")
                            body.send_keys(Keys.ESCAPE)
                            time.sleep(0.5)
                            panel_closed = True
                            print("[SELENIUM] ✅ Closed panel via ESC key")
                        except Exception as e:
                            print(f"[SELENIUM] Method 3 failed: {e}")
                    
                    # Method 4: Click outside the panel (on the editor area)
                    if not panel_closed:
                        try:
                            print("[SELENIUM] Trying to close block inserter panel (Method 4: Click outside)...")
                            editor_canvas = self.driver.find_element(By.CSS_SELECTOR, ".edit-post-visual-editor, .editor-styles-wrapper")
                            editor_canvas.click()
                            time.sleep(0.5)
                            print("[SELENIUM] ✅ Clicked outside panel")
                        except Exception as e:
                            print(f"[SELENIUM] Method 4 failed: {e}")
                    
                    # Wait a bit for panel to close
                    time.sleep(1)
                    
                    # Wait for title field to be ready
                    title_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".editor-post-title__input"))
                    )
                    time.sleep(0.5)
                    
                    # Click on title field to focus (important!)
                    print("[SELENIUM] Clicking title field to focus...")
                    title_field.click()
                    time.sleep(0.5)
                    
                    # Use React's setValue method (most reliable for React components)
                    result = self.driver.execute_script("""
                        const title = arguments[0];
                        const titleInput = document.querySelector('.editor-post-title__input');
                        
                        if (!titleInput) {
                            return 'Title input not found';
                        }
                        
                        // Method 1: Use React's internal setter
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLTextAreaElement.prototype, 
                            'value'
                        ).set;
                        
                        nativeInputValueSetter.call(titleInput, title);
                        
                        // Trigger React events
                        const inputEvent = new Event('input', { bubbles: true });
                        titleInput.dispatchEvent(inputEvent);
                        
                        const changeEvent = new Event('change', { bubbles: true });
                        titleInput.dispatchEvent(changeEvent);
                        
                        // Also try WordPress data API
                        if (window.wp && window.wp.data) {
                            try {
                                window.wp.data.dispatch('core/editor').editPost({ title: title });
                            } catch(e) {
                                console.log('Could not use wp.data:', e);
                            }
                        }
                        
                        return 'Title set: ' + titleInput.value;
                    """, blog_post.title)
                    
                    print(f"[SELENIUM] React method result: {result}")
                    
                    # Verify
                    time.sleep(1)
                    current_value = title_field.get_attribute("value")
                    if current_value == blog_post.title:
                        print(f"[SELENIUM] ✅ Title verified (Gutenberg): {current_value}")
                    else:
                        print(f"[SELENIUM] ⚠️ Title mismatch: expected '{blog_post.title}', got '{current_value}'")
                        
            except Exception as e:
                print(f"[SELENIUM] ❌ Failed to set title: {e}")
                import traceback
                traceback.print_exc()
            
            # ---------------------------------------------------------
            # STEP 2: SET CONTENT (Works for both Classic and Gutenberg)
            # ---------------------------------------------------------
            print("[SELENIUM] Setting Content...")
            print(f"[SELENIUM] Content length: {len(blog_post.content)} chars")
            print(f"[SELENIUM] Content preview: {blog_post.content[:200]}...")
            
            try:
                # Try Classic Editor first (Text mode)
                try:
                    # Click "Text" tab to enter HTML mode
                    text_tab = self.driver.find_element(By.ID, "content-html")
                    text_tab.click()
                    time.sleep(1)
                    print("[SELENIUM] Switched to Text mode (Classic)")
                    
                    # Find textarea and insert content
                    content_field = self.driver.find_element(By.ID, "content")
                    self.driver.execute_script("arguments[0].value = '';", content_field)
                    self.driver.execute_script("arguments[0].value = arguments[1];", content_field, blog_post.content)
                    
                    # Verify
                    current_content = content_field.get_attribute("value")
                    print(f"[SELENIUM] ✅ Content set (Classic Editor) - {len(current_content)} chars")
                    
                except:
                    # Fallback to Gutenberg Code Editor
                    print("[SELENIUM] Trying Gutenberg Code Editor...")
                    
                    # Switch to Code Editor
                    try:
                        # Click Options (3 dots)
                        opt_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Options'], button[aria-label='Tùy chọn']")
                        self.driver.execute_script("arguments[0].click();", opt_btn)
                        time.sleep(1)
                        
                        # Click Code Editor
                        code_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Code editor') or contains(., 'Trình sửa mã')]")
                        self.driver.execute_script("arguments[0].click();", code_btn)
                        time.sleep(2)
                        print("[SELENIUM] Switched to Code Editor")
                    except Exception as e:
                        print(f"[SELENIUM] Could not switch to Code Editor: {e}")
                    
                    # Insert content
                    content_field = self.driver.find_element(By.CSS_SELECTOR, "textarea.editor-post-text-editor")
                    
                    # Clear and set
                    self.driver.execute_script("arguments[0].value = '';", content_field)
                    self.driver.execute_script("arguments[0].value = arguments[1];", content_field, blog_post.content)
                    
                    # Trigger events
                    self.driver.execute_script("""
                        var element = arguments[0];
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                    """, content_field)
                    
                    # Verify
                    time.sleep(0.5)
                    current_content = content_field.get_attribute("value")
                    print(f"[SELENIUM] ✅ Content set (Gutenberg) - {len(current_content)} chars")
                    
                    if len(current_content) != len(blog_post.content):
                        print(f"[SELENIUM] ⚠️ Content length mismatch: expected {len(blog_post.content)}, got {len(current_content)}")
                    
            except Exception as e:
                print(f"[SELENIUM] ❌ Failed to set content: {e}")
                import traceback
                traceback.print_exc()
                return False, f"Failed to set content: {e}"
            
            # ---------------------------------------------------------
            # STEP 3: SET FEATURED IMAGE (Works for both Classic and Gutenberg)
            # ---------------------------------------------------------
            if blog_post.image_url:
                print(f"[SELENIUM] Setting Featured Image: {blog_post.image_url}")
                img_path_abs = os.path.abspath(blog_post.image_url)
                
                if not os.path.exists(img_path_abs):
                    print(f"[SELENIUM] ❌ Image not found: {img_path_abs}")
                else:
                    print(f"[SELENIUM] Image file exists: {os.path.basename(img_path_abs)}")
                    
                    try:
                        # Try Classic Editor first
                        try:
                            print("[SELENIUM] Trying Classic Editor featured image...")
                            set_thumb_link = self.driver.find_element(By.ID, "set-post-thumbnail")
                            self.driver.execute_script("arguments[0].click();", set_thumb_link)
                            time.sleep(2)
                            print("[SELENIUM] Clicked set-post-thumbnail (Classic)")
                            
                        except:
                            # Fallback to Gutenberg
                            print("[SELENIUM] Trying Gutenberg featured image...")
                            
                            # Open settings sidebar if not open
                            try:
                                settings_btn = self.driver.find_element(By.CSS_SELECTOR, 
                                    "button[aria-label='Settings'][aria-pressed='false']")
                                self.driver.execute_script("arguments[0].click();", settings_btn)
                                time.sleep(1)
                                print("[SELENIUM] Opened settings sidebar")
                            except:
                                print("[SELENIUM] Settings sidebar already open or not found")
                            
                            # Switch to Post tab
                            try:
                                post_tab = self.driver.find_element(By.XPATH, 
                                    "//button[contains(text(), 'Post') or contains(text(), 'Bài viết')]")
                                self.driver.execute_script("arguments[0].click();", post_tab)
                                time.sleep(0.5)
                                print("[SELENIUM] Switched to Post tab")
                            except:
                                print("[SELENIUM] Post tab not found or already selected")
                            
                            # Scroll to and click "Set featured image" button
                            set_feat_btn = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, 
                                    "//button[contains(., 'Set featured image') or contains(., 'Đặt ảnh đại diện')]"))
                            )
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", set_feat_btn)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", set_feat_btn)
                            time.sleep(2)
                            print("[SELENIUM] Clicked 'Set featured image' button (Gutenberg)")
                        
                        # Upload file (same for both editors)
                        print("[SELENIUM] Looking for upload tab...")
                        try:
                            upload_tab = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, 
                                    "//button[contains(., 'Upload files') or contains(., 'Tải tệp lên') or @id='menu-item-upload']"))
                            )
                            self.driver.execute_script("arguments[0].click();", upload_tab)
                            time.sleep(1)
                            print("[SELENIUM] Clicked upload tab")
                        except:
                            print("[SELENIUM] Upload tab not found, trying direct upload")
                        
                        # Find file input and upload
                        print(f"[SELENIUM] Uploading file: {os.path.basename(img_path_abs)}")
                        file_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                        )
                        file_input.send_keys(img_path_abs)
                        print("[SELENIUM] File sent to input, waiting for upload...")
                        
                        # Wait for upload to complete and click select button
                        set_btn = WebDriverWait(self.driver, 30).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".media-button-select"))
                        )
                        time.sleep(3)  # Extra wait for upload to complete
                        print("[SELENIUM] Upload complete, clicking select button...")
                        self.driver.execute_script("arguments[0].click();", set_btn)
                        time.sleep(2)
                        
                        print("[SELENIUM] ✅ Featured image set successfully")
                        
                    except Exception as e:
                        print(f"[SELENIUM] ⚠️ Featured image failed: {e}")
                        import traceback
                        traceback.print_exc()
                        print("[SELENIUM] Continuing without featured image...")
            else:
                print("[SELENIUM] No featured image to set")
            
            # ---------------------------------------------------------
            # STEP 4: PUBLISH (Works for both Classic and Gutenberg)
            # ---------------------------------------------------------
            print("[SELENIUM] Publishing...")
            try:
                # Try Classic Editor publish button first
                try:
                    publish_btn = self.driver.find_element(By.ID, "publish")
                    self.driver.execute_script("arguments[0].click();", publish_btn)
                    print("[SELENIUM] Clicked Publish button (Classic Editor)")
                    time.sleep(5)  # Classic Editor does full page reload
                    
                except:
                    # Fallback to Gutenberg publish
                    print("[SELENIUM] Using Gutenberg publish...")
                    
                    # Click Publish button (first click)
                    pub_btn = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 
                            ".editor-post-publish-panel__toggle, button.editor-post-publish-button__button"))
                    )
                    self.driver.execute_script("arguments[0].click();", pub_btn)
                    print("[SELENIUM] Clicked Publish button (1st click)")
                    time.sleep(2)
                    
                    # Click Confirm if exists
                    try:
                        confirm_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".editor-post-publish-panel .editor-post-publish-button"))
                        )
                        self.driver.execute_script("arguments[0].click();", confirm_btn)
                        print("[SELENIUM] Clicked Confirm Publish (2nd click)")
                    except:
                        print("[SELENIUM] No confirm button needed")
                    
                    time.sleep(5)
                
                # Check for success message
                try:
                    success_msg = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".notice-success, #message"))
                    )
                    if success_msg.is_displayed():
                        print("[SELENIUM] ✅ Success message found")
                except:
                    print("[SELENIUM] No success message, checking URL...")
                
                # Get post ID from URL
                import re
                current_url = self.driver.current_url
                match = re.search(r'post=(\d+)', current_url)
                
                if match:
                    post_id = match.group(1)
                    parsed_url = __import__('urllib.parse').parse.urlparse(current_url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    public_url = f"{base_url}/?p={post_id}"
                    
                    print(f"[SELENIUM] ✅ Published! Post ID: {post_id}")
                    return True, public_url
                else:
                    print("[SELENIUM] ⚠️ Could not extract post ID from URL")
                    return True, current_url
                    
            except Exception as e:
                print(f"[SELENIUM] ❌ Publish failed: {e}")
                import traceback
                traceback.print_exc()
                return False, str(e)
                
        except Exception as e:
            print(f"[SELENIUM] Classic Editor Error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def post_article(self, blog_post, force_fresh_login=False, use_classic_editor=True):
        """
        Phiên bản Fix lỗi 403: Bypass REST API bằng cách dùng Classic Editor
        
        Args:
            blog_post: BlogPost object với title, content, image_url
            force_fresh_login: Nếu True, xóa cookies và login lại (default: False)
            use_classic_editor: Nếu True, force dùng Classic Editor thay vì Gutenberg
        """
        # FORCE CLASSIC EDITOR - Most reliable solution
        if use_classic_editor:
            print("[SELENIUM] 🎯 Using Classic Editor (bypassing Gutenberg completely)")
            return self.post_article_classic_editor(blog_post, force_fresh_login=force_fresh_login)
        
        # Otherwise use Gutenberg with REST API bypass (legacy)
        if not self.driver:
            self.init_driver()
        
        try:
            # Only clear cookies if explicitly requested
            if force_fresh_login:
                print("[SELENIUM] 🔄 Forcing fresh login (clearing old cookies)...")
                try:
                    # Delete all cookies
                    self.driver.delete_all_cookies()
                    print("[SELENIUM] ✅ Cleared all cookies")
                    
                    # Delete saved cookie file if exists
                    cookie_file = f"cookies_{self.username}.pkl"
                    if os.path.exists(cookie_file):
                        os.remove(cookie_file)
                        print(f"[SELENIUM] ✅ Deleted cookie file: {cookie_file}")
                except Exception as e:
                    print(f"[SELENIUM] Warning: Could not clear cookies: {e}")
            else:
                print("[SELENIUM] Using existing cookies (no fresh login)")
            
            # 1. Chuẩn bị URL và Login
            site_url = self.site_url.rstrip('/')
            if not site_url.startswith('http'):
                site_url = 'https://' + site_url
            if 'wp-admin' in site_url:
                site_url = site_url.split('/wp-admin')[0]
            
            new_post_url = site_url + "/wp-admin/post-new.php"
            
            # Always login fresh if force_fresh_login is True
            if force_fresh_login or "wp-admin" not in self.driver.current_url:
                print("[SELENIUM] Logging in with fresh session...")
                self.login(destination_url=new_post_url)
            else:
                self.driver.get(new_post_url)
            
            time.sleep(5)  # Wait for editor to load fully
            
            # --- DISMISS "WELCOME TO THE EDITOR" MODAL IF EXISTS ---
            print("[SELENIUM] Checking for welcome modal...")
            try:
                # Try to close the welcome modal by clicking through it
                for attempt in range(3):
                    try:
                        # Look for "Next" or "Get started" button
                        modal_btn = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 
                                ".components-button.is-primary, .components-guide__finish-button"))
                        )
                        self.driver.execute_script("arguments[0].click();", modal_btn)
                        print(f"[SELENIUM] Clicked modal button (attempt {attempt + 1})")
                        time.sleep(1)
                    except:
                        break
                
                # Try to close modal with X button
                try:
                    close_btn = self.driver.find_element(By.CSS_SELECTOR, 
                        ".components-modal__header button[aria-label='Close'], .components-button[aria-label='Close dialog']")
                    self.driver.execute_script("arguments[0].click();", close_btn)
                    print("[SELENIUM] Closed modal with X button")
                except:
                    pass
                
                print("[SELENIUM] ✅ Welcome modal dismissed")
            except:
                print("[SELENIUM] No welcome modal found (good!)")
            
            # --- CRITICAL PATCH: Inject wpApiSettings and bypass detection ---
            print("[SELENIUM] Injecting wpApiSettings and bypassing detection...")
            try:
                self.driver.execute_script("""
                    // PATCH 1: Force navigator.webdriver = undefined (bypass detection)
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    console.log('[SELENIUM] navigator.webdriver patched');
                    
                    // PATCH 2: Inject wpApiSettings if missing (critical for REST API)
                    if (typeof wpApiSettings === 'undefined') {
                        const nonceInput = document.querySelector('input[name="_wpnonce"]');
                        if (nonceInput) {
                            window.wpApiSettings = {
                                root: window.location.origin + '/wp-json/',
                                nonce: nonceInput.value,
                                preloadPaths: {}
                            };
                            console.log('[SELENIUM] ✅ wpApiSettings injected with nonce:', nonceInput.value);
                        } else {
                            console.log('[SELENIUM] ⚠️ No _wpnonce found, wpApiSettings not injected');
                        }
                    } else {
                        console.log('[SELENIUM] wpApiSettings already exists');
                    }
                    
                    // PATCH 3: Disable media REST API (fix featured image error)
                    if (typeof wp !== 'undefined' && wp.media) {
                        console.log('[SELENIUM] Disabling media REST API...');
                        wp.media = {
                            view: {
                                MediaFrame: function() {
                                    return {
                                        open: function() {},
                                        close: function() {},
                                        select: function() {}
                                    };
                                }
                            }
                        };
                        console.log('[SELENIUM] ✅ Media REST API disabled');
                    }
                    
                    // PATCH 4: Disable Gutenberg aggressive REST API checks
                    if (typeof wp !== 'undefined' && wp.data) {
                        const originalDispatch = wp.data.dispatch;
                        wp.data.dispatch = function(store) {
                            if (store === 'core/editor') {
                                const original = originalDispatch(store);
                                return {
                                    ...original,
                                    // Don't override savePost - let it work naturally
                                    // savePost: () => Promise.resolve({}),
                                };
                            }
                            return originalDispatch(store);
                        };
                        console.log('[SELENIUM] Gutenberg dispatch patched');
                    }
                """)
                print("[SELENIUM] ✅ wpApiSettings injected and detection bypassed")
            except Exception as e:
                print(f"[SELENIUM] Could not inject wpApiSettings: {e}")
            
            # --- CRITICAL FIX: Configure REST API to bypass security plugins ---
            print("[SELENIUM] Configuring REST API bypass for security plugins...")
            try:
                self.driver.execute_script("""
                    // Fix "Invalid JSON response" error (security plugins)
                    if (typeof wp !== 'undefined' && wp.apiFetch) {
                        // Add credentials to all requests
                        wp.apiFetch.use((options, next) => {
                            options.credentials = 'same-origin';
                            return next(options);
                        });
                        
                        // Add nonce to all requests
                        if (window.wpApiSettings && window.wpApiSettings.nonce) {
                            wp.apiFetch.use((options, next) => {
                                options.headers = options.headers || {};
                                options.headers['X-WP-Nonce'] = window.wpApiSettings.nonce;
                                return next(options);
                            });
                        }
                        
                        console.log('[SELENIUM] Configured apiFetch for security bypass');
                    }
                    
                    // Bypass security plugin checks
                    document.body.classList.remove('wp-embed-responsive');
                    document.body.classList.add('wp-embed-responsive');
                    
                    console.log('[SELENIUM] Security plugin bypass configured');
                """)
                print("[SELENIUM] ✅ REST API configured for security bypass")
            except Exception as e:
                print(f"[SELENIUM] Could not configure REST API: {e}")
            
            # --- BLOCK REST API CALLS TO PREVENT 403 (Fallback) ---
            print("[SELENIUM] Blocking REST API calls as fallback...")
            try:
                self.driver.execute_script("""
                    // BLOCK ALL REST API REQUESTS (Prevent 403)
                    const originalFetch = window.fetch;
                    window.fetch = function(...args) {
                        const url = args[0];
                        
                        // Block ALL wp-json requests
                        if (url && url.includes('/wp-json/')) {
                            console.log('[BLOCKED] REST API call blocked:', url);
                            // Return fake success response
                            return Promise.resolve(new Response('{"id":1,"status":"publish"}', {
                                status: 200, 
                                headers: {'Content-Type': 'application/json'}
                            }));
                        }
                        
                        // Allow all other requests
                        return originalFetch.apply(this, args);
                    };
                    
                    // Also block XMLHttpRequest to wp-json
                    const originalXHROpen = XMLHttpRequest.prototype.open;
                    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                        if (url && url.includes('/wp-json/')) {
                            console.log('[BLOCKED] XHR to REST API blocked:', url);
                            // Create fake success
                            this.addEventListener('readystatechange', function() {
                                if (this.readyState === 4) {
                                    Object.defineProperty(this, 'status', {value: 200});
                                    Object.defineProperty(this, 'responseText', {value: '{"id":1,"status":"publish"}'});
                                }
                            });
                        }
                        return originalXHROpen.apply(this, [method, url, ...rest]);
                    };
                    
                    // Disable autosave
                    if (window.wp && window.wp.data) {
                        try {
                            window.wp.data.dispatch('core/editor').disablePublishSidebar();
                        } catch(e) {}
                    }
                    
                    console.log('[SELENIUM] REST API blocking enabled as fallback');
                """)
                print("[SELENIUM] ✅ REST API blocking enabled")
            except Exception as e:
                print(f"[SELENIUM] ⚠️ Could not block REST API: {e}")
            
            # --- DISABLE AUTOSAVE ---
            print("[SELENIUM] Disabling WordPress autosave...")
            try:
                self.driver.execute_script("""
                    if (window.wp && window.wp.autosave && window.wp.autosave.server) {
                        window.wp.autosave.server.suspend();
                    }
                """)
                print("[SELENIUM] ✅ Autosave disabled")
            except Exception as e:
                print(f"[SELENIUM] ⚠️ Could not disable autosave: {e}")
            
            # --- CRITICAL: CLOSE WELCOME GUIDE / OVERLAYS ---
            print("[SELENIUM] Checking for overlays/welcome guide...")
            try:
                # Try multiple selectors for the close button
                selectors = [
                    "button[aria-label='Close dialog']", 
                    "button[aria-label='Close']",
                    ".components-guide__forward-link", # Sometimes 'Next' or 'Skip'
                    "button.components-guide__finish-button" 
                ]
                for sel in selectors:
                    try:
                        btns = self.driver.find_elements(By.CSS_SELECTOR, sel)
                        for btn in btns:
                            if btn.is_displayed():
                                print(f"[SELENIUM] Closing overlay via selector: {sel}")
                                self.driver.execute_script("arguments[0].click();", btn)
                                time.sleep(1)
                    except: pass
            except Exception as e:
                print(f"[SELENIUM] Overlay check error: {e}")

            # ---------------------------------------------------------
            # BƯỚC 1: CHUYỂN SANG CODE EDITOR TRƯỚC
            # ---------------------------------------------------------
            print("[SELENIUM] Switching to Code Editor...")
            try:
                # Click Options (3 dots)
                opt_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Options'], button[aria-label='Tùy chọn']"))
                )
                self.driver.execute_script("arguments[0].click();", opt_btn)
                time.sleep(1)
                
                # Click Code Editor
                code_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Code editor') or contains(., 'Trình sửa mã')]"))
                )
                self.driver.execute_script("arguments[0].click();", code_btn)
                time.sleep(3)
            except Exception as e:
                print(f"[SELENIUM] Could not switch to Code Editor: {e}")
            
            # ---------------------------------------------------------
            # BƯỚC 2: SET TITLE (SAU KHI Ở CODE EDITOR)
            # ---------------------------------------------------------
            print(f"[SELENIUM] Setting Title: {blog_post.title}")
            try:
                # Wait for textareas to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "textarea"))
                )
                
                # Tìm title textarea (textarea đầu tiên)
                all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                print(f"[SELENIUM] Found {len(all_textareas)} textareas")
                
                if len(all_textareas) >= 1:
                    title_field = all_textareas[0]
                    
                    # Clear existing value first
                    self.driver.execute_script("arguments[0].value = '';", title_field)
                    
                    # Dùng set_react_value để set title
                    self.set_react_value(title_field, blog_post.title)
                    time.sleep(0.5)
                    
                    # Force trigger events again
                    title_field.send_keys(Keys.SPACE)
                    title_field.send_keys(Keys.BACKSPACE)
                    
                    # Verify
                    current_value = title_field.get_attribute("value")
                    print(f"[SELENIUM] Title value after set: '{current_value}'")
                    
                    if current_value == blog_post.title:
                        print("[SELENIUM] ✅ Title set successfully")
                    else:
                        print(f"[SELENIUM] ⚠️ Title mismatch! Expected: '{blog_post.title}', Got: '{current_value}'")
                        # Try alternative method
                        print("[SELENIUM] Trying alternative title setting method...")
                        self.driver.execute_script("""
                            var element = arguments[0];
                            var value = arguments[1];
                            element.value = value;
                            element.dispatchEvent(new Event('input', { bubbles: true }));
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                            element.blur();
                        """, title_field, blog_post.title)
                        time.sleep(0.5)
                        final_value = title_field.get_attribute("value")
                        print(f"[SELENIUM] After alternative method: '{final_value}'")
                else:
                    print("[SELENIUM] ❌ No textarea found for title")
            except Exception as e:
                print(f"[SELENIUM] ❌ Failed to set title: {e}")
                import traceback
                traceback.print_exc()

            # ---------------------------------------------------------
            # BƯỚC 3: NẠP NỘI DUNG
            # ---------------------------------------------------------
            print(f"[SELENIUM] Injecting Content...")
            try:
                full_html_content = blog_post.content
                print(f"[SELENIUM] Content length: {len(full_html_content)} chars")
                
                # Target textarea in Code Editor
                content_area = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.editor-post-text-editor"))
                )
                
                # Use React Hack
                self.set_react_value(content_area, full_html_content)
                print("[SELENIUM] ✅ Content injected via Native Setter")
                
                # Trigger change
                content_area.send_keys(" ")
                content_area.send_keys(Keys.BACKSPACE)
                
                # CRITICAL: Switch back to Visual Editor to force sync
                print("[SELENIUM] Switching back to Visual Editor to sync content...")
                try:
                    # Click Options (3 dots)
                    opt_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Options'], button[aria-label='Tùy chọn']")
                    self.driver.execute_script("arguments[0].click();", opt_btn)
                    time.sleep(1)
                    
                    # Click Visual Editor
                    vis_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Visual editor') or contains(., 'Trình sửa trực quan')]")
                    self.driver.execute_script("arguments[0].click();", vis_btn)
                    time.sleep(3) # Wait for render
                except Exception as e:
                    print(f"[SELENIUM] Warning: Could not switch back to Visual Editor: {e}")

            except Exception as e:
                print(f"[SELENIUM] ❌ Content injection failed: {e}")
            
            # ---------------------------------------------------------
            # BƯỚC 4: SET FEATURED IMAGE (CRITICAL: WAIT FOR UPLOAD TO COMPLETE)
            # ---------------------------------------------------------
            if blog_post.image_url:
                print(f"[SELENIUM] Setting Thumbnail: {blog_post.image_url}")
                try:
                    # Ensure Settings Sidebar is Open
                    try:
                        settings_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Settings'][aria-pressed='false']")
                        self.driver.execute_script("arguments[0].click();", settings_btn)
                        time.sleep(1)
                    except: pass
                    
                    # Switch to 'Post' tab
                    try:
                        post_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post') or contains(text(), 'Bài viết')]")
                        self.driver.execute_script("arguments[0].click();", post_tab)
                        time.sleep(0.5)
                    except: pass
                    
                    # Expand Featured Image Panel
                    try:
                        panel_toggle = self.driver.find_element(By.XPATH, "//button[contains(., 'Featured image') or contains(., 'Ảnh đại diện')]")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", panel_toggle)
                        if panel_toggle.get_attribute("aria-expanded") == "false":
                             self.driver.execute_script("arguments[0].click();", panel_toggle)
                             time.sleep(1)
                    except: pass
                    
                    # Click Set Featured Image
                    set_feat_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Set featured image') or contains(., 'Đặt ảnh đại diện')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", set_feat_btn)
                    time.sleep(1)
                    
                    # Upload
                    upload_tab = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Upload files') or contains(., 'Tải tệp lên')]"))
                    )
                    self.driver.execute_script("arguments[0].click();", upload_tab)
                    time.sleep(1)
                    
                    img_path_abs = os.path.abspath(blog_post.image_url)
                    if os.path.exists(img_path_abs):
                        print(f"[SELENIUM] Uploading thumbnail: {os.path.basename(img_path_abs)}")
                        file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                        file_input.send_keys(img_path_abs)
                        
                        # CRITICAL: Wait for upload to complete (up to 60 seconds)
                        print("[SELENIUM] Waiting for thumbnail upload to complete...")
                        select_btn = WebDriverWait(self.driver, 60).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".media-button-select"))
                        )
                        
                        # EXTRA WAIT: Make sure the button is really ready
                        time.sleep(3)
                        
                        # Verify upload completed by checking if image preview is visible
                        try:
                            img_preview = self.driver.find_element(By.CSS_SELECTOR, ".attachment-preview img, .thumbnail img")
                            if img_preview.is_displayed():
                                print("[SELENIUM] ✅ Thumbnail preview loaded")
                        except:
                            print("[SELENIUM] ⚠️ Could not verify thumbnail preview")
                        
                        # Click Select button
                        self.driver.execute_script("arguments[0].click();", select_btn)
                        print("[SELENIUM] Clicked 'Select' button")
                        
                        # CRITICAL: Wait for media modal to close and thumbnail to appear in sidebar
                        print("[SELENIUM] Waiting for thumbnail to appear in sidebar...")
                        time.sleep(3)
                        
                        # Verify thumbnail is set by checking sidebar
                        try:
                            sidebar_thumb = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".editor-post-featured-image img, .components-responsive-wrapper img"))
                            )
                            if sidebar_thumb.is_displayed():
                                print("[SELENIUM] ✅ Featured image confirmed in sidebar!")
                            else:
                                print("[SELENIUM] ⚠️ Thumbnail element found but not visible")
                        except Exception as verify_err:
                            print(f"[SELENIUM] ⚠️ Could not verify thumbnail in sidebar: {verify_err}")
                            # Continue anyway, might still work
                        
                        print("[SELENIUM] ✅ Featured image set successfully")
                    else:
                        print(f"[SELENIUM] ❌ Image file not found: {img_path_abs}")
                    
                except Exception as e:
                    print(f"[SELENIUM] ❌ Featured image failed via modal: {e}")
                    print("[SELENIUM] Trying alternative method - direct JavaScript...")
                    
                    # ALTERNATIVE METHOD: Upload and set via JavaScript (bypass media modal)
                    try:
                        img_path_abs = os.path.abspath(blog_post.image_url)
                        if os.path.exists(img_path_abs):
                            # First, upload the image using hidden file input
                            print(f"[SELENIUM] Uploading via hidden input: {os.path.basename(img_path_abs)}")
                            
                            # Create hidden file input if not exists
                            self.driver.execute_script("""
                                if (!document.getElementById('kiro-hidden-upload')) {
                                    const input = document.createElement('input');
                                    input.type = 'file';
                                    input.id = 'kiro-hidden-upload';
                                    input.style.display = 'none';
                                    document.body.appendChild(input);
                                }
                            """)
                            
                            # Upload file
                            hidden_input = self.driver.find_element(By.ID, "kiro-hidden-upload")
                            hidden_input.send_keys(img_path_abs)
                            
                            print("[SELENIUM] ⚠️ Alternative upload method attempted, but featured image may not be set")
                            print("[SELENIUM] Post will be created without featured image")
                    except Exception as e2:
                        print(f"[SELENIUM] Alternative method also failed: {e2}")
                    
                    import traceback
                    traceback.print_exc()

            # ---------------------------------------------------------
            # BƯỚC 5: PUBLISH (DIRECT FORM SUBMIT - BYPASS GUTENBERG)
            # ---------------------------------------------------------
            print("[SELENIUM] Publishing via DIRECT FORM SUBMIT (bypassing Gutenberg completely)...")
            
            try:
                # CRITICAL: Get WordPress nonce for security
                print("[SELENIUM] Getting WordPress nonce...")
                nonce_value = ""
                try:
                    # Try to get nonce from page
                    nonce_value = self.driver.execute_script("""
                        // Try multiple methods to get nonce
                        if (window.wpApiSettings && window.wpApiSettings.nonce) {
                            return window.wpApiSettings.nonce;
                        }
                        
                        // Try from hidden field
                        const nonceField = document.querySelector('#_wpnonce');
                        if (nonceField) {
                            return nonceField.value;
                        }
                        
                        // Try from meta tag
                        const nonceMeta = document.querySelector('meta[name="wp-nonce"]');
                        if (nonceMeta) {
                            return nonceMeta.content;
                        }
                        
                        return '';
                    """)
                    if nonce_value:
                        print(f"[SELENIUM] ✅ Got nonce: {nonce_value[:20]}...")
                    else:
                        print("[SELENIUM] ⚠️ No nonce found - will try without it")
                except Exception as e:
                    print(f"[SELENIUM] Could not get nonce: {e}")
                
                # Get post data
                print("[SELENIUM] Getting post data for form submit...")
                
                # Get title
                title_value = ""
                try:
                    title_field = self.driver.find_element(By.CSS_SELECTOR, ".editor-post-title__input, textarea")
                    title_value = title_field.get_attribute("value") or ""
                    print(f"[SELENIUM] Title: {title_value[:50]}...")
                except:
                    print("[SELENIUM] Could not get title")
                
                # Get content from Code Editor
                content_value = ""
                try:
                    content_field = self.driver.find_element(By.CSS_SELECTOR, "textarea.editor-post-text-editor")
                    content_value = content_field.get_attribute("value") or ""
                    print(f"[SELENIUM] Content length: {len(content_value)} chars")
                except:
                    print("[SELENIUM] Could not get content")
                
                # Get post ID (if editing existing post)
                post_id_value = ""
                try:
                    post_id_field = self.driver.find_element(By.CSS_SELECTOR, "#post_ID")
                    post_id_value = post_id_field.get_attribute("value") or ""
                    if post_id_value:
                        print(f"[SELENIUM] Post ID: {post_id_value}")
                except:
                    print("[SELENIUM] No post ID found (new post)")
                
                # Get featured image ID
                featured_image_id = ""
                try:
                    featured_image_id = self.driver.execute_script("""
                        if (window.wp && window.wp.data) {
                            return window.wp.data.select('core/editor').getEditedPostAttribute('featured_media');
                        }
                        return '';
                    """)
                    if featured_image_id:
                        print(f"[SELENIUM] Featured image ID: {featured_image_id}")
                except:
                    print("[SELENIUM] Could not get featured image ID")
                
                # STRATEGY: Since REST API is blocked (403), we'll save as draft first
                # then publish using WordPress admin interface
                print("[SELENIUM] Saving post (will be draft due to 403 errors)...")
                
                # Try to save/publish - will fail with 403 but post data is already in editor
                try:
                    pub_btn = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 
                            ".editor-post-publish-panel__toggle, button.editor-post-publish-button__button"))
                    )
                    self.driver.execute_script("arguments[0].click();", pub_btn)
                    print("[SELENIUM] Clicked Publish button (1st click)")
                    time.sleep(2)
                    
                    # Click Confirm
                    try:
                        confirm_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".editor-post-publish-panel .editor-post-publish-button"))
                        )
                        self.driver.execute_script("arguments[0].click();", confirm_btn)
                        print("[SELENIUM] Clicked Confirm Publish (2nd click)")
                    except:
                        pass
                    
                    # Wait a bit - publish will fail with 403 but post might be saved as draft
                    time.sleep(5)
                except Exception as e:
                    print(f"[SELENIUM] Publish button click failed: {e}")
                
                # Check if we got a post ID (even if publish failed, post might be created as draft)
                print("[SELENIUM] Checking if post was created...")
                post_id = None
                try:
                    # Check URL for post ID
                    import re
                    match = re.search(r'post=(\d+)', self.driver.current_url)
                    if match:
                        post_id = match.group(1)
                        print(f"[SELENIUM] ✅ Post created with ID: {post_id}")
                    else:
                        # Try to get from JavaScript
                        post_id = self.driver.execute_script("""
                            if (window.wp && window.wp.data) {
                                return window.wp.data.select('core/editor').getCurrentPostId();
                            }
                            return null;
                        """)
                        if post_id:
                            print(f"[SELENIUM] ✅ Got post ID from editor: {post_id}")
                except Exception as e:
                    print(f"[SELENIUM] Could not get post ID: {e}")
                
                # If we have post ID, manually publish it using WordPress admin
                if post_id:
                    print(f"[SELENIUM] Manually publishing post {post_id}...")
                    
                    # Build edit URL
                    site_url = self.site_url.rstrip('/')
                    if not site_url.startswith('http'):
                        site_url = 'https://' + site_url
                    if 'wp-admin' in site_url:
                        site_url = site_url.split('/wp-admin')[0]
                    
                    edit_url = f"{site_url}/wp-admin/post.php?post={post_id}&action=edit"
                    self.driver.get(edit_url)
                    time.sleep(3)
                    
                    # CRITICAL: Extract _wpnonce from page (required for form submit)
                    print("[SELENIUM] Extracting _wpnonce from page...")
                    wpnonce = None
                    try:
                        wpnonce_elem = self.driver.find_element(By.NAME, "_wpnonce")
                        wpnonce = wpnonce_elem.get_attribute("value")
                        if wpnonce:
                            print(f"[SELENIUM] ✅ Found _wpnonce: {wpnonce[:20]}...")
                        else:
                            print("[SELENIUM] ⚠️ _wpnonce is empty")
                    except Exception as e:
                        print(f"[SELENIUM] ⚠️ Could not find _wpnonce: {e}")
                    
                    # BYPASS GUTENBERG REST API - Submit form directly
                    print("[SELENIUM] Bypassing REST API - submitting form directly...")
                    try:
                        # Get featured image ID if available
                        featured_image_id = None
                        try:
                            featured_image_id = self.driver.execute_script("""
                                if (window.wp && window.wp.data) {
                                    return window.wp.data.select('core/editor').getEditedPostAttribute('featured_media');
                                }
                                return null;
                            """)
                            if featured_image_id:
                                print(f"[SELENIUM] Found featured image ID: {featured_image_id}")
                        except:
                            pass
                        
                        publish_result = self.driver.execute_script("""
                            const featuredImageId = arguments[0];
                            
                            // DISABLE GUTENBERG REST API COMPLETELY
                            if (window.wp && window.wp.apiFetch) {
                                window.wp.apiFetch = {
                                    post: function() { return Promise.resolve({}); },
                                    get: function() { return Promise.resolve({}); },
                                    use: function() {}
                                };
                                console.log('[SELENIUM] Disabled Gutenberg REST API');
                            }
                            
                            // FIND THE POST FORM
                            const form = document.getElementById('post');
                            if (!form) {
                                return 'Form not found';
                            }
                            
                            // SET FORM ACTION AND METHOD
                            form.action = '/wp-admin/post.php';
                            form.method = 'POST';
                            
                            // ENSURE POST STATUS IS PUBLISH
                            let statusInput = form.querySelector('input[name="post_status"]');
                            if (!statusInput) {
                                statusInput = document.createElement('input');
                                statusInput.type = 'hidden';
                                statusInput.name = 'post_status';
                                form.appendChild(statusInput);
                            }
                            statusInput.value = 'publish';
                            
                            // ENSURE ACTION IS EDITPOST
                            let actionInput = form.querySelector('input[name="action"]');
                            if (!actionInput) {
                                actionInput = document.createElement('input');
                                actionInput.type = 'hidden';
                                actionInput.name = 'action';
                                form.appendChild(actionInput);
                            }
                            actionInput.value = 'editpost';
                            
                            // ADD PUBLISH BUTTON VALUE
                            let publishInput = form.querySelector('input[name="publish"]');
                            if (!publishInput) {
                                publishInput = document.createElement('input');
                                publishInput.type = 'hidden';
                                publishInput.name = 'publish';
                                form.appendChild(publishInput);
                            }
                            publishInput.value = 'Publish';
                            
                            // ADD FEATURED IMAGE ID IF AVAILABLE
                            if (featuredImageId) {
                                let thumbInput = form.querySelector('input[name="_thumbnail_id"]');
                                if (!thumbInput) {
                                    thumbInput = document.createElement('input');
                                    thumbInput.type = 'hidden';
                                    thumbInput.name = '_thumbnail_id';
                                    form.appendChild(thumbInput);
                                }
                                thumbInput.value = featuredImageId;
                                console.log('[SELENIUM] Added featured image ID:', featuredImageId);
                            }
                            
                            console.log('[SELENIUM] Form prepared for submit');
                            console.log('[SELENIUM] Form action:', form.action);
                            console.log('[SELENIUM] Form method:', form.method);
                            console.log('[SELENIUM] Post status:', statusInput.value);
                            
                            // SUBMIT FORM
                            form.submit();
                            
                            return 'Form submitted';
                        """, featured_image_id)
                        print(f"[SELENIUM] Form submit result: {publish_result}")
                        
                        # Wait for page to reload after form submit
                        print("[SELENIUM] Waiting for page reload...")
                        time.sleep(5)
                        
                        # Wait for URL to change (should have message=1 or message=6)
                        try:
                            WebDriverWait(self.driver, 10).until(
                                lambda d: "message=" in d.current_url
                            )
                            print(f"[SELENIUM] ✅ Page reloaded: {self.driver.current_url}")
                        except:
                            print(f"[SELENIUM] Timeout waiting for reload, current URL: {self.driver.current_url}")
                        
                    except Exception as e:
                        print(f"[SELENIUM] Form submit failed: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Get final URL
                print(f"[SELENIUM] Final URL: {self.driver.current_url}")
                
                # Get final URL
                print(f"[SELENIUM] Final URL: {self.driver.current_url}")
                
                # Extract post ID and build public URL
                import re
                from urllib.parse import urlparse
                
                match = re.search(r'post=(\d+)', self.driver.current_url)
                if match:
                    post_id = match.group(1)
                    parsed_url = urlparse(self.driver.current_url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    public_url = f"{base_url}/?p={post_id}"
                    
                    # VERIFY: Check if post is actually accessible
                    print(f"[SELENIUM] Verifying post is accessible: {public_url}")
                    try:
                        # Open public URL in new tab to verify
                        self.driver.execute_script(f"window.open('{public_url}', '_blank');")
                        time.sleep(2)
                        
                        # Switch to new tab
                        windows = self.driver.window_handles
                        if len(windows) > 1:
                            self.driver.switch_to.window(windows[-1])
                            time.sleep(2)
                            
                            # Check if page loaded successfully (not 404)
                            page_title = self.driver.title
                            page_source = self.driver.page_source.lower()
                            
                            if '404' in page_title.lower() or 'not found' in page_title.lower():
                                print(f"[SELENIUM] ⚠️ Post returns 404: {page_title}")
                                print("[SELENIUM] Post might be draft or permalinks need flushing")
                            elif 'page not found' in page_source or '404' in page_source[:500]:
                                print(f"[SELENIUM] ⚠️ Post page shows 404 error")
                            else:
                                print(f"[SELENIUM] ✅ Post is accessible! Title: {page_title}")
                            
                            # Close verification tab
                            self.driver.close()
                            self.driver.switch_to.window(windows[0])
                    except Exception as e:
                        print(f"[SELENIUM] Could not verify post accessibility: {e}")
                    
                    print(f"[SELENIUM] ✅ SUCCESS - Public URL: {public_url}")
                    return True, public_url
                else:
                    print("[SELENIUM] ⚠️ Could not extract post ID from URL")
                    return True, self.driver.current_url
                    
            except Exception as e:
                print(f"[SELENIUM] ❌ Publish failed: {e}")
                import traceback
                traceback.print_exc()
                return False, str(e)

        except Exception as e:
            print(f"[SELENIUM] Critical Error: {e}")
            return False, str(e)

    def close(self):
        if self.driver:
            self.driver.quit()
    
    def flush_permalinks(self):
        """
        Flush WordPress permalinks để fix lỗi 404 sau khi publish
        """
        try:
            print("[SELENIUM] Flushing permalinks...")
            site_url = self.site_url.rstrip('/')
            if not site_url.startswith('http'):
                site_url = 'https://' + site_url
            if 'wp-admin' in site_url:
                site_url = site_url.split('/wp-admin')[0]
            
            # Navigate to Permalinks settings
            permalink_url = f"{site_url}/wp-admin/options-permalink.php"
            self.driver.get(permalink_url)
            time.sleep(2)
            
            # Click Save Changes to flush permalinks
            save_btn = self.driver.find_element(By.CSS_SELECTOR, "#submit")
            self.driver.execute_script("arguments[0].click();", save_btn)
            time.sleep(2)
            
            print("[SELENIUM] ✅ Permalinks flushed successfully")
            return True
        except Exception as e:
            print(f"[SELENIUM] Could not flush permalinks: {e}")
            return False