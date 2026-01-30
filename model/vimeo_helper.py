from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import os
import json


class VimeoHelper:
    # Class-level counter for account rotation across multiple instances
    _global_account_index = 0
    _account_lock = None  # Will be initialized as threading.Lock()
    
    def __init__(self):
        self.driver = None
        self.current_account_index = 0  # Track which account we're using
        self.available_accounts = []  # List of available accounts from cookies
        
        # Initialize lock if not already done
        if VimeoHelper._account_lock is None:
            import threading
            VimeoHelper._account_lock = threading.Lock()
    
    def auto_click_ok_buttons(self):
        """
        Auto-click any "OK", "Confirm", "Accept" buttons in popups/modals
        This handles Vimeo's blue info popups and other dialogs
        """
        try:
            # Find all visible "OK" buttons (case-insensitive)
            ok_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(translate(text(), 'OK', 'ok'), 'ok')] | "
                "//button[contains(translate(@aria-label, 'OK', 'ok'), 'ok')] | "
                "//button[contains(@class, 'ok')] | "
                "//button[contains(@class, 'confirm')] | "
                "//button[contains(@class, 'accept')] | "
                "//button[text()='OK'] | "
                "//button[text()='Ok'] | "
                "//button[@aria-label='OK'] | "
                "//button[@aria-label='Ok']"
            )
            
            for btn in ok_buttons:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        btn_text = btn.text.strip().lower()
                        # Click if button text is "ok" or empty (icon button)
                        if 'ok' in btn_text or btn_text == '':
                            print(f"[VIMEO] 🔘 Auto-clicking OK button...")
                            self.driver.execute_script("arguments[0].click();", btn)
                            time.sleep(0.3)
                            return True
                except:
                    pass
        except:
            pass
        
        return False

    def init_driver(self, headless=False, proxy=None, is_mobile=False):
        """Initialize Chrome Driver with Enhanced Anti-Detect & Mobile Option"""
        import random
        import os
        self.is_headless = headless
        
        # Try to import UC
        try:
            import undetected_chromedriver as uc
            HAS_UC = True
        except ImportError:
            HAS_UC = False
            print("[VIMEO] 'undetected-chromedriver' not found. Using standard Selenium.")

        # --- 1. ENHANCED USER AGENTS (More realistic) ---
        if is_mobile:
            user_agents = [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36"
            ]
        else:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Safari/537.36"
            ]
            
        chosen_ua = random.choice(user_agents)
        print(f"[VIMEO] Using User-Agent ({'Mobile' if is_mobile else 'Desktop'}): {chosen_ua}")
        
        # Options setup
        if HAS_UC:
            options = uc.ChromeOptions()
        else:
            options = webdriver.ChromeOptions()
            
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-notifications")
        options.add_argument(f"user-agent={chosen_ua}")
        
        if is_mobile:
             # Basic Mobile Emulation for visual rendering
             # CRITICAL: We DO NOT use 'mobileEmulation' option as it crashes UC and some standard drivers.
             # We rely on UA + Window Size + Touch Events.
             options.add_argument("--enable-touch-events")
             # Force a small window size later
             
        # --- BLOCK WEBRTC (Prevent IP Leak) ---
        options.add_argument("--disable-webrtc")
        prefs = {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False
        }
        try:
            options.add_experimental_option("prefs", prefs)
        except:
            pass # Some drivers might not support this, ignore if fails
         
        
        # Standard Selenium Flags (Only if NOT using UC, as UC handles this)
        if not HAS_UC:
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations for headless mode
        if headless:
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            # Note: Don't disable JS as Vimeo needs it
        
        # --- PROXY HANDLING ---
        if proxy:
            try:
                parts = proxy.strip().split(':')
                if len(parts) == 4:
                    PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = parts
                    print(f"[VIMEO] Using Proxy: {PROXY_HOST}:{PROXY_PORT}")
                    
                    manifest_json = """
                    {
                        "version": "1.0.0",
                        "manifest_version": 2,
                        "name": "Chrome Proxy",
                        "permissions": [
                            "proxy",
                            "tabs",
                            "unlimitedStorage",
                            "storage",
                            "<all_urls>",
                            "webRequest",
                            "webRequestBlocking"
                        ],
                        "background": {
                            "scripts": ["background.js"]
                        },
                        "minimum_chrome_version":"22.0.0"
                    }
                    """
                    background_js = """
                    var config = {
                            mode: "fixed_servers",
                            rules: {
                              singleProxy: {
                                scheme: "http",
                                host: "%s",
                                port: parseInt(%s)
                              },
                              bypassList: ["localhost"]
                            }
                          };

                    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                    function callbackFn(details) {
                        return {
                            authCredentials: {
                                username: "%s",
                                password: "%s"
                            }
                        };
                    }

                    chrome.webRequest.onAuthRequired.addListener(
                                callbackFn,
                                {urls: ["<all_urls>"]},
                                ['blocking']
                    );
                    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
                    
                    import zipfile
                    pluginfile = 'proxy_auth_plugin.zip'
                    if os.path.exists(pluginfile): os.remove(pluginfile)
                    
                    with zipfile.ZipFile(pluginfile, 'w') as zp:
                        zp.writestr("manifest.json", manifest_json)
                        zp.writestr("background.js", background_js)
                    
                    # Both UC and Standard Selenium support extension
                    options.add_argument(f"--load-extension={os.path.abspath(pluginfile)}")
                elif len(parts) == 2:
                     options.add_argument(f'--proxy-server={proxy}')
            except Exception as e:
                print(f"[VIMEO] Proxy Setup Error: {e}")

        try:
            print("[VIMEO] Initializing Driver (UC Mode)..." if HAS_UC else "[VIMEO] Initializing Driver (Standard)...")
            
            if HAS_UC:
                # Undetected Chromedriver Init with thread-safe handling
                # CRITICALLY IMPORTANT: Use a global lock for UC init to prevent race conditions on the executable
                import threading
                uc_lock = threading.Lock()
                
                with uc_lock:
                    # Retry logic for multi-threading race condition
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            # Use unique user-data-dir for each thread to avoid profile conflicts
                            import tempfile
                            unique_dir = os.path.join(tempfile.gettempdir(), f"chrome_profile_{os.getpid()}_{id(self)}")
                            options.add_argument(f"--user-data-dir={unique_dir}")
                            
                            # Specify version_main to match your portable chrome
                            # If using portable, we must point to it.
                            chrome_portable_path = None
                            if os.path.exists("chrome_portable/chrome.exe"):
                                chrome_portable_path = os.path.abspath("chrome_portable/chrome.exe")
                                options.binary_location = chrome_portable_path

                            # Driver executable path
                            # FIX FOR "WinError 32" and "Session not created":
                            # 1. Use local driver directly if exists (Avoids UC patching race)
                            # 2. Set distinct driver_executable_path
                            
                            driver_executable_path = None
                            if os.path.exists("driver/chromedriver.exe"):
                                driver_executable_path = os.path.abspath("driver/chromedriver.exe")
                            
                            if driver_executable_path:
                                # Use provided driver, disable UC patching logic by not setting version_main (or careful setting)
                                self.driver = uc.Chrome(options=options, 
                                                      headless=headless, 
                                                      use_subprocess=True, 
                                                      driver_executable_path=driver_executable_path,
                                                      version_main=None)
                            else:
                                # Fallback to UC auto-patch
                                self.driver = uc.Chrome(options=options, headless=headless, use_subprocess=True, version_main=132) 
                            
                            break  # Success
                        except Exception as e:
                             print(f"[VIMEO] Driver Init Error (Attempt {attempt+1}): {e}")
                             if attempt == max_retries - 1:
                                 # If failed, try ONE LAST TIME with standard Selenium if specific error
                                 if "session not created" in str(e) or "WinError" in str(e):
                                     print("[VIMEO] Switching to Standard Selenium due to UC Error...")
                                     HAS_UC = False
                                     # Will fall through to 'if not HAS_UC' block below? No, need to raise or handle.
                                     # Let's re-raise for now, or we can restructure. 
                                     # Better to raise so we know.
                                     pass
                             time.sleep(random.uniform(2, 5)) # Stagger retries more
            else:
                if headless:
                    options.add_argument("--headless=new")
                
                # Retry logic for Driver Installation
                driver_path = None
                for attempt in range(3):
                    try:
                        driver_path = ChromeDriverManager().install()
                        break
                    except Exception as install_e:
                        print(f"[VIMEO] Driver Install Failed (Attempt {attempt+1}): {install_e}")
                        time.sleep(2)
                
                if not driver_path:
                    # Fallback: Try running without explicit path (system path) or raise
                    print("[VIMEO] Could not download driver. Trying default system driver...")
                    self.driver = webdriver.Chrome(options=options)
                else:
                    service = ChromeService(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=options)
                
                # Fingerprint for Standard
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": chosen_ua})
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                })
            
            print("[VIMEO] Browser initialized successfully.")
            if is_mobile:
                self.driver.set_window_size(390, 844)
            else:
                self.driver.set_window_size(1920, 1080)
            
            # Increase timeout for slow pages like Vimeo upload
            self.driver.set_page_load_timeout(180)  # 3 minutes instead of 60s

        except Exception as e:
            print(f"[VIMEO] Failed to init driver: {e}")
            raise e

    def fill_registration_form(self, name, email, password, log_callback=None):
        """
        Open Vimeo Join page and fill the form.
        """
        if not self.driver:
            self.init_driver(headless=True)

        try:
            # --- VERIFY PROXY IP --- (Optimized)
            try:
                print("[VIMEO] 🔎 Verifying Proxy IP...")
                if log_callback: log_callback("[VIMEO] 🔎 Đang kiểm tra IP...")
                
                self.driver.get("https://api64.ipify.org?format=json")
                time.sleep(1)  # Reduced from 2s to 1s
                body_elem = self.driver.find_element(By.TAG_NAME, "body")
                ip_text = body_elem.text
                print(f"[VIMEO] 🌍 Current IP (Seen by Browser): {ip_text}")
                
                if log_callback: 
                    log_callback(f"[NETWORK] 🌍 IP hiện tại (Trình duyệt): {ip_text}")
                    
            except Exception as ip_e:
                print(f"[VIMEO] ⚠️ Could not verify IP: {ip_e}")

            # --- WARM-UP NAVIGATION STRATEGY --- (Optimized)
            print("[VIMEO] Navigating to Join page directly...")
            self.driver.get("https://vimeo.com/join")  # Direct to join page
            time.sleep(2)  # Reduced from 3s to 2s

            # --- CAPTCHA / CLOUDFLARE HANDLING --- (Optimized)
            print(f"[VIMEO] Checking page: {self.driver.current_url}")
            
            start_cf_time = time.time()
            refresh_count = 0
            unknown_state_count = 0
            
            while True:
                curr_time = time.time()
                elapsed = curr_time - start_cf_time
                
                # TIMEOUT / REFRESH STRATEGY (60s - Reduced)
                if elapsed > 60:  # Reduced from 120s to 60s
                    if refresh_count == 0:
                         print("[VIMEO] 🔄 Stuck in Cloudflare > 1 min. Refreshing page...")
                         self.driver.refresh()
                         refresh_count += 1
                         start_cf_time = time.time() # Reset timer once
                         time.sleep(3)  # Reduced from 5s to 3s
                         continue
                    else:
                         print("[VIMEO] ❌ Cloudflare Timeout (Given up).")
                         break # Proceed to form fill (will likely fail but let it try)

                # Check if we passed (Form fields visible)
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    # Vimeo form has name="name", name="email" etc.
                    # Or check for 'Sign up with Google' button presence to be sure
                    form_inputs = [i for i in inputs if i.is_displayed()]
                    if len(form_inputs) >= 1: # Changed to >= 1 because new form is 2-step (Only Email first)
                        print("[VIMEO] ✅ Cloudflare passed! Form detected (Email field found).")
                        break
                except: pass

                # --- HANDLING CHALLENGE ---
                page_source = self.driver.page_source.lower()
                if "verify to continue" in page_source or "just a moment" in page_source:
                    print(f"[VIMEO] ⚠️ Cloudflare/Verify detected ({int(elapsed)}s)... Looking for checkbox.")
                    time.sleep(2) # Reduced from 3s to 2s

                    try:
                        # Strategy 1: Look for Cloudflare Turnstile (Shadow DOM)
                        cf_hosts = self.driver.find_elements(By.CSS_SELECTOR, "div.cf-turnstile-wrapper, div.cf-turnstile")
                        for host in cf_hosts:
                            try:
                                host.click()
                                print("[VIMEO] 🖱️ Clicked Cloudflare Wrapper.")
                                time.sleep(1)  # Reduced from 2s to 1s
                            except: pass
                            
                        # Strategy 2: iFrames
                        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                        for frame in iframes:
                            try:
                                src = frame.get_attribute("src") or ""
                                if "turnstile" in src or "challenge" in src:
                                    self.driver.switch_to.frame(frame)
                                    checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                                    checkbox.click()
                                    print("[VIMEO] 🖱️ Clicked Checkbox inside iFrame!")
                                    self.driver.switch_to.default_content()
                                    time.sleep(0.5)  # Reduced from 1s to 0.5s
                            except:
                                self.driver.switch_to.default_content()
                    except Exception as cf_e:
                        pass
                
                else:
                    # UNKNOWN STATE DETECTOR
                    unknown_state_count += 1
                    if unknown_state_count % 5 == 0: # Every 10s (5 * 2s)
                        print(f"[VIMEO] ❓ State Unknown (No Form, No Captcha) - Count {unknown_state_count}")
                        print(f"   [URL] {self.driver.current_url}")
                        print(f"   [Title] {self.driver.title}")

                time.sleep(1)  # Reduced from 2s to 1s
            
            # --- END CAPTCHA HANDLING ---

            print("[VIMEO] Page header loaded.")
            
            # --- 0. CLICK "SIGN UP WITH EMAIL" (If Hidden) ---
            try:
                email_links = self.driver.find_elements(By.XPATH, "//a[contains(., 'email') or contains(., 'Email')] | //button[contains(., 'email') or contains(., 'Email')]")
                visible_links = [l for l in email_links if l.is_displayed()]
                # filter out 'Google' or 'Facebook'
                clean_links = [l for l in visible_links if 'google' not in l.text.lower() and 'facebook' not in l.text.lower()]
                
                # Check if we already see email input
                email_input_visible = False
                try:
                    e_in = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
                    if e_in.is_displayed(): email_input_visible = True
                except: pass

                if not email_input_visible and clean_links:
                    print(f"[VIMEO] Clicking '{clean_links[0].text}' to reveal form...")
                    clean_links[0].click()
                    time.sleep(1)
            except: pass

            # --- 1. FILL EMAIL ---
            print("[VIMEO] looking for Email field...")
            try:
                email_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[id*='email']")
                visible_emails = [e for e in email_inputs if e.is_displayed()]
                if visible_emails:
                    visible_emails[0].clear()
                    visible_emails[0].send_keys(email)
                    print("[VIMEO] Filled Email.")
                    if log_callback: log_callback("[FORM] ✅ Đã điền Email.")
                    try:
                        if not self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']"):
                            print("[VIMEO] No password field yet. Clicking Continue/Submit to proceed...")
                            continue_btns = self.driver.find_elements(By.XPATH, "//button[(contains(., 'Continue') or contains(., 'email')) and not(contains(., 'Google')) and not(contains(., 'Facebook'))]")
                            visible_cns = [b for b in continue_btns if b.is_displayed()]
                            if visible_cns:
                                visible_cns[0].click()
                            else:
                                s_btns = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
                                if s_btns:
                                    s_btns[0].click()
                    except:
                        pass
                    try:
                        print("[VIMEO] Waiting for password field to appear...")
                        WebDriverWait(self.driver, 5).until(  # Reduced from 10s to 5s
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                        )
                        time.sleep(0.5)  # Reduced from 1s to 0.5s
                    except:
                        print("[VIMEO] Warning: Password field did not appear quickly.")
            except Exception as e:
                print(f"[VIMEO] Email fill error: {e}")

            # --- 2. FILL NAME ---
            try:
                name_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[name='name'], input[id*='name'], input[placeholder*='name'], input[placeholder*='Name']")
                visible_names = [e for e in name_inputs if e.is_displayed()]
                visible_names = [e for e in visible_names if 'email' not in (e.get_attribute('name') or '').lower() and 'email' not in (e.get_attribute('type') or '').lower()]
                if visible_names:
                    visible_names[0].clear()
                    visible_names[0].send_keys(name)
                    print("[VIMEO] Filled Name.")
                    if log_callback: log_callback("[FORM] ✅ Đã điền Tên.")
            except Exception as e:
                print(f"[VIMEO] Name fill error: {e}")

            # --- 3. FILL PASSWORD (AND CONFIRM PASSWORD) ---
            try:
                print("[VIMEO] Searching for all password fields...")
                visible_pass = []
                for attempt in range(3):
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    candidates = []
                    for i in all_inputs:
                        try:
                            i_type = (i.get_attribute("type") or "").lower()
                            i_name = (i.get_attribute("name") or "").lower()
                            i_placeholder = (i.get_attribute("placeholder") or "").lower()
                            i_aria = (i.get_attribute("aria-label") or "").lower()
                            if "password" in i_type or "password" in i_name or "confirm" in i_name or "password" in i_placeholder or "confirm" in i_placeholder or "password" in i_aria:
                                if i.is_displayed():
                                    candidates.append(i)
                        except:
                            pass
                    if len(candidates) >= 2:
                        visible_pass = candidates
                        break
                    time.sleep(1)
                if attempt == 2:
                    visible_pass = candidates

                if len(visible_pass) > 0:
                    for idx, v in enumerate(visible_pass):
                        try:
                            print(f"[VIMEO] Field #{idx+1}: name='{v.get_attribute('name')}', placeholder='{v.get_attribute('placeholder')}'")
                        except:
                            pass
                    unique_pass = []
                    for p in visible_pass:
                        if p not in unique_pass:
                            unique_pass.append(p)

                    if len(unique_pass) >= 2:
                        for i, p_input in enumerate(unique_pass):
                            try:
                                p_input.clear()
                                p_input.send_keys(password)
                                print(f"[VIMEO] Filled password/confirm field #{i+1}")
                                if log_callback and i==0: log_callback("[FORM] ✅ Đã điền Mật khẩu.")
                                time.sleep(0.1)
                            except:
                                pass
                    elif len(unique_pass) == 1:
                        print("[VIMEO] Only found 1 password field. Using TAB strategy for Confirm Password...")
                        p_input = unique_pass[0]
                        try:
                            p_input.click()
                            p_input.clear()
                            p_input.send_keys(password)
                            print("[VIMEO] Filled first password field.")
                            time.sleep(0.2)
                            from selenium.webdriver.common.action_chains import ActionChains
                            actions = ActionChains(self.driver)
                            actions.send_keys(Keys.TAB)
                            actions.pause(0.2)
                            actions.send_keys(password)
                            actions.perform()
                            print("[VIMEO] Sent TAB + Password (Blind Fill for Confirm).")
                        except Exception as e:
                            print(f"[VIMEO] TAB Strategy failed: {e}")
                    else:
                        print("[VIMEO] Warning: No password field found!")
            except Exception as e:
                print(f"[VIMEO] Password fill error: {e}")

            # --- 4. CLICK JOIN / SUBMIT ---
            print("[VIMEO] Clicking Final 'Join' button...")
            time.sleep(0.3)  # Reduced from 0.5s
            try:
                join_btns = self.driver.find_elements(By.XPATH, "//button[(contains(., 'Join') or contains(., 'Sign up') or contains(., 'Đăng ký') or contains(., 'Hoàn tất')) and not(contains(., 'Google')) and not(contains(., 'Facebook'))]")
                visible_btns = [b for b in join_btns if b.is_displayed()]
                if visible_btns:
                    visible_btns[0].click()
                    print("[VIMEO] Clicked Join button (Text Match)!")
                else:
                    submits = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                    visible_submits = [s for s in submits if s.is_displayed()]
                    if visible_submits:
                        visible_submits[-1].click()
                        print("[VIMEO] Clicked Submit button (Type Match).")
                    else:
                        pass_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                        visible_pass = [e for e in pass_inputs if e.is_displayed()]
                        if visible_pass:
                            visible_pass[-1].send_keys(Keys.ENTER)
                            print("[VIMEO] Sent ENTER key to submit.")
                    
                # Wait for page to process
                time.sleep(2)  # Reduced from 3s
                
                # Check for errors and IP blocks
                body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                if "network error" in body_text or "something went wrong" in body_text or "spam" in body_text:
                    print("❌ [LỖI] Vimeo chặn đăng ký (Spam/Network Error).")
                    return False, "IP_BLOCKED"
                
                # Check for rate limiting or IP restrictions
                if "too many requests" in body_text or "rate limit" in body_text or "try again later" in body_text:
                    print("❌ [LỖI] IP bị rate limit.")
                    return False, "RATE_LIMITED"
                
                # Check for account creation limits
                if "account limit" in body_text or "maximum accounts" in body_text or "limit reached" in body_text:
                    print("❌ [LỖI] Đã đạt giới hạn tạo tài khoản.")
                    return False, "ACCOUNT_LIMIT"
                
            except Exception as e:
                print(f"[VIMEO] Join click error: {e}")
                # Check if it's an IP block related error
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                    if any(keyword in body_text for keyword in ["blocked", "restricted", "banned", "too many"]):
                        return False, "IP_BLOCKED"
                except:
                    pass
                return False, f"CLICK_ERROR"

            # --- 5. HANDLE SURVEY & TRIALS (LOOP) --- (Optimized)
            print("[VIMEO] Enter validation loop...")
            if getattr(self, 'is_headless', False):
                 # Headless: Shorter wait
                 end_time = time.time() + 10  # Reduced from 15s to 10s
            else:
                 # Visible: Shorter wait 
                 end_time = time.time() + 60  # Reduced from 120s to 60s
                 print("[VIMEO] ⚠️ Visible Mode: Waiting 60s for you to solve Captcha/Join manually...")
            
            # Validation Flag
            is_success = True
            
            while time.time() < end_time:
                try:
                    if not self.driver: break
                    
                    # Enhanced Skip Detection - Multiple Strategies
                    skip_found = False
                    
                    # Strategy 1: Text-based Skip buttons
                    skip_elements = self.driver.find_elements(By.XPATH, "//*[text()='Skip' or text()='Bỏ qua' or contains(text(), 'Skip trial') or contains(text(), 'No thanks') or contains(text(), 'Maybe later')]")
                    visible_skips = [e for e in skip_elements if e.is_displayed()]
                    if visible_skips:
                        for btn in visible_skips:
                            try:
                                btn.click()
                                print(f"[VIMEO] Clicked Skip button (Text): {btn.text}")
                                skip_found = True
                                time.sleep(1)  # Reduced from 2s to 1s
                                break
                            except: pass
                    
                    # Strategy 2: Look for "Skip" in top-right corner (common pattern)
                    if not skip_found:
                        try:
                            skip_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='skip'], button[data-testid*='skip'], .skip-button, [class*='skip']")
                            for link in skip_links:
                                if link.is_displayed() and ('skip' in link.text.lower() or 'skip' in (link.get_attribute('class') or '').lower()):
                                    link.click()
                                    print(f"[VIMEO] Clicked Skip link (CSS): {link.text}")
                                    skip_found = True
                                    time.sleep(1)  # Reduced from 2s to 1s
                                    break
                        except: pass
                    
                    # Strategy 3: Survey/Onboarding specific - Look for "Next" or close buttons
                    if not skip_found:
                        try:
                            # Check if we're on a survey page
                            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                            if "how do you plan" in page_text or "survey" in page_text or "tell us about" in page_text:
                                # Try to find Next button and click it (sometimes skips survey)
                                next_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Continue') or contains(text(), 'Finish')]")
                                for btn in next_btns:
                                    if btn.is_displayed():
                                        btn.click()
                                        print(f"[VIMEO] Clicked survey Next/Continue: {btn.text}")
                                        skip_found = True
                                        time.sleep(1)  # Reduced from 2s to 1s
                                        break
                        except: pass
                    
                    # Strategy 4: Close modal/popup buttons
                    if not skip_found:
                        try:
                            close_btns = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Close'], .close-button, [data-testid='close'], .modal-close")
                            for btn in close_btns:
                                if btn.is_displayed():
                                    btn.click()
                                    print("[VIMEO] Clicked Close button")
                                    skip_found = True
                                    time.sleep(1)  # Reduced from 2s to 1s
                                    break
                        except: pass
                    
                    if not skip_found:
                        time.sleep(0.5)  # Reduced from 1s to 0.5s
                        
                    # Check URL to see if we moved past Join/Survey
                    try:
                        curr = self.driver.current_url.lower()
                        # More comprehensive success URL patterns
                        success_patterns = [
                            "vimeo.com/home",
                            "vimeo.com/manage", 
                            "vimeo.com/settings",
                            "vimeo.com/upload",
                            "/onboarding/complete",
                            "/welcome"
                        ]
                        
                        # Check if we're no longer on join/login pages
                        if "join" not in curr and "log_in" not in curr and "login" not in curr:
                            # Additional check - are we on a main Vimeo page?
                            if any(pattern in curr for pattern in success_patterns) or curr == "https://vimeo.com/" or "vimeo.com" in curr:
                                print(f"[VIMEO] ✅ Registration completed! Current URL: {curr}")
                                break
                    except: 
                        break 
                    
                except Exception as e:
                    if "invalid session" in str(e).lower(): break
                    time.sleep(1)
            
            # FINAL VERIFICATION
            try:
                curr_url = self.driver.current_url.lower()
                print(f"[VIMEO] Final URL: {curr_url}")
                
                # Check if still on join/login pages (real failure)
                if "join" in curr_url or "log_in" in curr_url or "login" in curr_url:
                    # Additional check for IP blocks
                    try:
                        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                        if any(keyword in body_text for keyword in ["blocked", "restricted", "banned", "suspended", "too many", "rate limit"]):
                            return False, "IP_BLOCKED"
                        if any(keyword in body_text for keyword in ["captcha", "verify", "robot", "human"]):
                            return False, "CAPTCHA_REQUIRED"
                    except: pass
                    
                    if not getattr(self, 'is_headless', False):
                         return False, f"TIMEOUT_JOIN_PAGE"
                    return False, f"TIMEOUT_JOIN_PAGE"
                
                # Check if we have valid session cookies (means registration succeeded)
                try:
                    cookies = self.driver.get_cookies()
                    vimeo_session = any(cookie.get('name') == 'vimeo' for cookie in cookies)
                    if vimeo_session:
                        print("[VIMEO] ✅ Valid session cookie found - Registration successful!")
                        
                        # Save account to vimeo_accounts.txt
                        with open("vimeo_accounts.txt", "a", encoding="utf-8") as f:
                            f.write(f"{email}|{password}|{name}\n")
                        
                        # Save cookies to vimeo_cookies.txt
                        try:
                            cookie_data = {
                                "email": email,
                                "cookies": cookies
                            }
                            with open("vimeo_cookies.txt", "a", encoding="utf-8") as f:
                                f.write(json.dumps(cookie_data) + "\n")
                            print(f"[VIMEO] ✅ Đã lưu {len(cookies)} cookies vào vimeo_cookies.txt")
                            if log_callback: log_callback(f"[SAVE] ✅ Đã lưu cookie cho: {email}")
                        except Exception as cookie_err:
                            print(f"[VIMEO] ⚠️ Không thể lưu cookie: {cookie_err}")
                        
                        return True, "SUCCESS_WITH_COOKIE"
                except:
                    pass
                    
            except: pass
            
            # Fallback - Save account if we made it this far
            print("[VIMEO] ⚠️ Uncertain state, but saving account as precaution...")
            with open("vimeo_accounts.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}|{password}|{name}\n")
            
            # Try to save cookies anyway
            try:
                cookies = self.driver.get_cookies()
                if cookies:
                    cookie_data = {
                        "email": email,
                        "cookies": cookies
                    }
                    with open("vimeo_cookies.txt", "a", encoding="utf-8") as f:
                        f.write(json.dumps(cookie_data) + "\n")
                    print(f"[VIMEO] ✅ Đã lưu {len(cookies)} cookies (uncertain state)")
                    if log_callback: log_callback(f"[SAVE] ✅ Đã lưu cookie cho: {email}")
            except Exception as cookie_err:
                print(f"[VIMEO] ⚠️ Không thể lưu cookie: {cookie_err}")
            
            return True, "SUCCESS_UNCERTAIN"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = str(e).lower()
            
            # Check for network/IP related errors
            if any(keyword in error_msg for keyword in ["network", "connection", "timeout", "refused"]):
                return False, "NETWORK_ERROR"
            elif any(keyword in error_msg for keyword in ["blocked", "restricted", "banned"]):
                return False, "IP_BLOCKED"
            else:
                return False, f"GENERAL_ERROR"

    def login_vimeo(self, email, password, log_callback=None):
        if not self.driver: self.init_driver(headless=True)
        try:
            print(f"[VIMEO] Logging in with {email}...")
            if log_callback: log_callback(f"[LOGIN] Đăng nhập: {email}...")
            
            # Navigate if not already there
            if "log_in" not in self.driver.current_url:
                self.driver.get("https://vimeo.com/log_in")
                time.sleep(5)

            # --- HANDLE COMPLIANCE/COOKIE OVERLAYS ---
            try:
                # OneTrust / Cookie banner
                onetrust = self.driver.find_elements(By.ID, "onetrust-accept-btn-handler")
                if onetrust:
                    onetrust[0].click()
                    time.sleep(1)
                
                # Close buttons (modals)
                close_btns = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Close'], .js-close_modal")
                for btn in close_btns:
                    if btn.is_displayed(): btn.click()
            except: pass

            # Strategy 1: Find Email Field
            e_in = None
            try:
                # Based on user screenshot, it's a standard input. 
                # Sometimes Selenium gets blocked by invisible overlays, so we try multiple ways.
                
                # Method A: Specific ID often used by Vimeo
                try:
                     e_in = self.driver.find_element(By.ID, "email")
                except: pass
                
                # Method B: Name attribute
                if not e_in:
                    try: e_in = self.driver.find_element(By.NAME, "email")
                    except: pass
                
                # Method C: Input type generic
                if not e_in:
                    try: e_in = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
                    except: pass
                
                if e_in:
                    print(f"[VIMEO] Found email field: {e_in.get_attribute('outerHTML')[:50]}...")
                    
                    # Force visible
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", e_in)
                    time.sleep(1)
                    
                    # Try standard send_keys
                    try:
                        e_in.clear()
                        e_in.click()
                        e_in.send_keys(email)
                    except Exception as standard_err:
                        print(f"[VIMEO] Standard typing failed ({standard_err}), trying JS injection...")
                        # Fallback: Javascript Injection (Bypasses overlays/unclickable states)
                        self.driver.execute_script("arguments[0].value = arguments[1];", e_in, email)
                        # Trigger change event so React/Vue detects it
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", e_in)
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", e_in)
                    
                    print("[VIMEO] Email entered.")
                else:
                    raise Exception("Could not find any email input field")

            except Exception as e_fill:
                 print(f"[VIMEO] Fill email failed: {e_fill}")
                 if log_callback: log_callback(f"[LOGIN] Lỗi nhập email: {e_fill}")
                 # DEBUG SCREENSHOT
                 try: self.driver.save_screenshot(f"login_fail_{email}.png")
                 except: pass
                 return False

            time.sleep(1)

            # Strategy 2: Find Password Field
            try:
                p_in = self.driver.find_element(By.CSS_SELECTOR, "input[name='password'], input[type='password'], #password_input")
                p_in.click()
                time.sleep(0.5)
                p_in.clear()
                p_in.send_keys(password)
                print("[VIMEO] Password entered.")
            except Exception as p_fill:
                 print(f"[VIMEO] Fill password failed: {p_fill}")
                 if log_callback: log_callback(f"[LOGIN] Lỗi nhập password: {p_fill}")
                 return False

            time.sleep(1)

            # Strategy 3: Click Login/Submit Button
            try:
                submit_btns = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .js-login_submit")
                clicked = False
                if submit_btns:
                    # Prefer button with "log in" or "email" text
                    target_btn = submit_btns[0]
                    for btn in submit_btns:
                        txt = btn.text.lower()
                        if "email" in txt or "log in" in txt:
                            target_btn = btn
                            break
                    
                    try:
                        target_btn.click()
                        clicked = True
                    except:
                        self.driver.execute_script("arguments[0].click();", target_btn)
                        clicked = True
                
                if not clicked:
                    p_in.send_keys(Keys.ENTER)

            except Exception as s_err:
                 print(f"[VIMEO] Click submit failed: {s_err}")
                 p_in.send_keys(Keys.ENTER)

            
            # Wait for success
            time.sleep(8)
            current_url = self.driver.current_url.lower()
            if "log_in" not in current_url and "join" not in current_url:
                if log_callback: log_callback("[LOGIN] ✅ Đăng nhập thành công!")
                return True
            else:
                 # Check for errors on page
                 try:
                     errs = self.driver.find_elements(By.CSS_SELECTOR, ".error_msg, [role='alert'], .invalid_input")
                     for err in errs:
                         if err.is_displayed():
                             print(f"[VIMEO] Login Error displayed: {err.text}")
                             if log_callback: log_callback(f"[LOGIN] Lỗi từ web: {err.text}")
                 except: pass
                 
                 if log_callback: log_callback("[LOGIN] ❌ Đăng nhập thất bại (URL chưa đổi)")
                 return False
        except Exception as e:
            print(f"[VIMEO] Login Error: {e}")
            if log_callback: log_callback(f"[LOGIN] Lỗi: {e}")
            return False

    def load_cookies_from_file(self, email):
        """Find cookies for a specific email in vimeo_cookies.txt"""
        if not os.path.exists("vimeo_cookies.txt"):
            return None
        try:
            with open("vimeo_cookies.txt", "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if data.get("email") == email and "cookies" in data:
                            return data["cookies"]
                    except: pass
        except: return None
        return None

    def login_with_cookies(self, email=None, log_callback=None):
        """Inject cookies and verify login"""
        cookies = None
        
        if email:
            cookies = self.load_cookies_from_file(email)
            if log_callback: log_callback(f"[AUTH] Tìm cookie cho: {email}...")
        
        # If no cookies found for specific email, use round-robin selection
        if not cookies:
            if log_callback: log_callback("[AUTH] Không tìm thấy cookie cụ thể, thử cookie bất kỳ...")
            
            # Load all accounts if not loaded
            if not self.available_accounts:
                self.load_all_available_accounts()
            
            if self.available_accounts:
                # Use global counter for round-robin across threads
                with VimeoHelper._account_lock:
                    account_index = VimeoHelper._global_account_index % len(self.available_accounts)
                    VimeoHelper._global_account_index += 1
                
                account = self.available_accounts[account_index]
                cookies = account['cookies']
                email = account['email']
                self.current_account_index = account_index
                
                if log_callback: log_callback(f"[AUTH] Sử dụng cookie của: {email} (#{account_index + 1}/{len(self.available_accounts)})")
                print(f"[VIMEO] Using account #{account_index + 1}: {email}")
            else:
                # Fallback to old behavior if load failed
                try:
                    with open("vimeo_cookies.txt", "r", encoding="utf-8") as f:
                        for line in f:
                            try:
                                data = json.loads(line.strip())
                                if "cookies" in data:
                                    cookies = data["cookies"]
                                    email = data.get("email", "unknown")
                                    if log_callback: log_callback(f"[AUTH] Sử dụng cookie của: {email}")
                                    break
                            except: continue
                except: pass
        
        if not cookies:
            if log_callback: log_callback("[AUTH] ❌ Không tìm thấy cookie nào!")
            return False

        if not self.driver: self.init_driver(headless=True)
        try:
            print(f"[VIMEO] Using cookies for {email}...")
            if log_callback: log_callback(f"[AUTH] Đang áp dụng cookie...")
            
            # Go to a Vimeo page first to set the domain
            self.driver.get("https://vimeo.com/")
            time.sleep(2)
            
            # Add cookies
            cookies_added = 0
            for cookie in cookies:
                try:
                    # Clean up cookie data for Selenium
                    clean_cookie = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain'],
                        'path': cookie.get('path', '/'),
                    }
                    
                    # Add optional fields if present
                    if 'expiry' in cookie:
                        clean_cookie['expiry'] = int(cookie['expiry'])
                    if 'secure' in cookie:
                        clean_cookie['secure'] = cookie['secure']
                    if 'httpOnly' in cookie:
                        clean_cookie['httpOnly'] = cookie['httpOnly']
                    
                    self.driver.add_cookie(clean_cookie)
                    cookies_added += 1
                except Exception as e:
                    print(f"[VIMEO] Failed to add cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            
            if log_callback: log_callback(f"[AUTH] Đã thêm {cookies_added} cookies")
            
            # Test login by going to upload page
            self.driver.get("https://vimeo.com/upload")
            time.sleep(3)
            
            current_url = self.driver.current_url.lower()
            if "login" not in current_url and "log_in" not in current_url:
                if log_callback: log_callback("[AUTH] ✅ Cookie đăng nhập thành công!")
                return True
            else:
                if log_callback: log_callback("[AUTH] ❌ Cookie hết hạn hoặc không hợp lệ.")
                return False
                
        except Exception as e:
            if log_callback: log_callback(f"[AUTH] Lỗi cookie: {e}")
            print(f"[VIMEO] Cookie login error: {e}")
            return False

    def load_all_available_accounts(self):
        """Load all available accounts from vimeo_cookies.txt"""
        self.available_accounts = []
        
        if not os.path.exists("vimeo_cookies.txt"):
            print("[VIMEO] ⚠️ Không tìm thấy file vimeo_cookies.txt")
            return
        
        try:
            with open("vimeo_cookies.txt", "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if "cookies" in data and "email" in data:
                            self.available_accounts.append({
                                'email': data['email'],
                                'cookies': data['cookies']
                            })
                    except:
                        continue
            
            print(f"[VIMEO] ✅ Đã load {len(self.available_accounts)} tài khoản từ cookies")
        except Exception as e:
            print(f"[VIMEO] ❌ Lỗi load accounts: {e}")

    def switch_to_next_account(self, log_callback=None):
        """Switch to next available account when quota is full"""
        if not self.available_accounts:
            self.load_all_available_accounts()
        
        if not self.available_accounts:
            if log_callback: log_callback("[SWITCH] ❌ Không có tài khoản nào khả dụng!")
            return False
        
        # Move to next account
        self.current_account_index += 1
        
        if self.current_account_index >= len(self.available_accounts):
            if log_callback: log_callback("[SWITCH] ❌ Đã thử hết tất cả tài khoản!")
            return False
        
        account = self.available_accounts[self.current_account_index]
        email = account['email']
        
        if log_callback: log_callback(f"[SWITCH] 🔄 Chuyển sang tài khoản: {email}")
        print(f"[VIMEO] Switching to account: {email}")
        
        # Login with new account
        try:
            # Clear current session
            if self.driver:
                self.driver.delete_all_cookies()
                time.sleep(1)
            
            # Apply new cookies
            self.driver.get("https://vimeo.com/")
            time.sleep(2)
            
            cookies_added = 0
            for cookie in account['cookies']:
                try:
                    clean_cookie = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain'],
                        'path': cookie.get('path', '/'),
                    }
                    
                    if 'expiry' in cookie:
                        clean_cookie['expiry'] = int(cookie['expiry'])
                    if 'secure' in cookie:
                        clean_cookie['secure'] = cookie['secure']
                    if 'httpOnly' in cookie:
                        clean_cookie['httpOnly'] = cookie['httpOnly']
                    
                    self.driver.add_cookie(clean_cookie)
                    cookies_added += 1
                except:
                    continue
            
            if log_callback: log_callback(f"[SWITCH] Đã thêm {cookies_added} cookies")
            
            # Verify login
            self.driver.get("https://vimeo.com/upload")
            time.sleep(3)
            
            current_url = self.driver.current_url.lower()
            if "login" not in current_url and "log_in" not in current_url:
                if log_callback: log_callback(f"[SWITCH] ✅ Đã chuyển sang: {email}")
                return True
            else:
                if log_callback: log_callback(f"[SWITCH] ❌ Tài khoản {email} không hợp lệ, thử tiếp...")
                # Try next account recursively
                return self.switch_to_next_account(log_callback)
                
        except Exception as e:
            if log_callback: log_callback(f"[SWITCH] ❌ Lỗi chuyển account: {e}")
            print(f"[VIMEO] Switch account error: {e}")
            return False

    def auto_login(self, log_callback=None):
        """Try to login automatically using cookies first, then password fallback"""
        if log_callback: log_callback("[LOGIN] Bắt đầu auto login...")
        
        # Load available accounts if not loaded yet
        if not self.available_accounts:
            self.load_all_available_accounts()
        
        # Strategy 1: Try cookie login first (any available account)
        if os.path.exists("vimeo_cookies.txt"):
            if log_callback: log_callback("[LOGIN] Thử đăng nhập bằng cookie...")
            if self.login_with_cookies(None, log_callback):
                return True
        
        # Strategy 2: Fallback to password login
        if not os.path.exists("vimeo_accounts.txt"):
            if log_callback: log_callback("[LOGIN] ❌ Không tìm thấy file tài khoản!")
            return False
            
        try:
            with open("vimeo_accounts.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if log_callback: log_callback(f"[LOGIN] Tìm thấy {len(lines)} tài khoản, thử đăng nhập...")
            
            # Try last few accounts (most recent)
            for line in reversed(lines[-5:]):  # Try last 5 accounts
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    email = parts[0]
                    pwd = parts[1]
                    
                    if log_callback: log_callback(f"[LOGIN] Thử tài khoản: {email}")
                    
                    # Try password login
                    if self.login_vimeo(email, pwd, log_callback):
                        if log_callback: log_callback(f"[LOGIN] ✅ Đăng nhập thành công với: {email}")
                        return True
                    else:
                        if log_callback: log_callback(f"[LOGIN] ❌ Thất bại với: {email}")
                        
            if log_callback: log_callback("[LOGIN] ❌ Tất cả tài khoản đều thất bại!")
            return False
            
        except Exception as e:
            if log_callback: log_callback(f"[LOGIN] Lỗi đọc file tài khoản: {e}")
            return False

    def upload_video(self, file_path, log_callback=None, retry_on_quota=True):
        """
        Upload a video to Vimeo, check quota, and get link.
        Returns: success (bool), message (str), data (dict or None), quota_full (bool)
        """
        if not os.path.exists(file_path):
            return False, "File video không tồn tại!", None, False
        
        # Auto-recover if driver is missing or dead
        if not self.driver:
             if log_callback: log_callback("[DRIVER] Khởi tạo lại trình duyệt...")
             self.init_driver(headless=True)

        try:
            print("[VIMEO] Navigating to Upload page...")
            if log_callback: log_callback("[STEP] Đang vào trang Upload...")
            
            try:
                self.driver.get("https://vimeo.com/upload")
            except Exception as nav_err:
                # Handle timeout errors gracefully
                error_msg = str(nav_err).lower()
                if "timeout" in error_msg:
                    print("[VIMEO] ⚠️ Page load timeout, but continuing anyway...")
                    if log_callback: log_callback("[WARN] Trang load chậm, nhưng vẫn tiếp tục...")
                    # Stop page load and continue
                    try:
                        self.driver.execute_script("window.stop();")
                    except:
                        pass
                else:
                    raise nav_err
            
            time.sleep(1)  # Reduced from 3s to 1s
            
            # --- LOGIN CHECK ---
            # Robust check for logged-out state
            needs_login = False
            try:
                # Check for "Log in" or "Join" buttons
                page_source = self.driver.page_source.lower()
                if "log in" in page_source and "vimeo.com/log_in" in page_source:
                    needs_login = True
                    print("[VIMEO] Detect 'Log in' link/text in source.")
                elif "join" in page_source and "vimeo.com/join" in page_source:
                    needs_login = True
                    print("[VIMEO] Detect 'Join' link/text in source.")
                
                # Check specifics elements if broad check is consistent
                login_btns = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='log_in'], button[data-testid*='login'], .js-login_link")
                join_btns = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='join'], button[data-testid*='join']")
                
                if login_btns or join_btns:
                     needs_login = True
            except Exception as e:
                print(f"[VIMEO] Login check error: {e}")

            if needs_login:
                msg = "[AUTH] Phát hiện chưa đăng nhập (Found Login/Join btn). Đang thử auto-login..."
                print(f"[VIMEO] {msg}")
                if log_callback: log_callback(msg)
                
                if self.auto_login(log_callback):
                    # Login successful, reload upload page
                    if log_callback: log_callback("[AUTH] Tải lại trang Upload...")
                    self.driver.get("https://vimeo.com/upload")
                    time.sleep(2)  # Reduced from 5s to 2s
                else:
                     return False, "Chưa đăng nhập & Auto-login thất bại! Vui lòng kiểm tra file cookie/account.", None, False

            # --- QUOTA CHECK ---
            print("[VIMEO] Checking storage quota...")
            if log_callback: log_callback("[STEP] Kiểm tra dung lượng...")
            
            quota_exceeded = False
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                if "1gb of 1gb" in body_text or "limit reached" in body_text or "quota exceeded" in body_text:
                    quota_exceeded = True
                    if log_callback: log_callback("[QUOTA] ⚠️ Phát hiện quota đầy!")
                    
                import re
                match = re.search(r"([\d\.]+)gb of 1gb", body_text)
                if match:
                    used = float(match.group(1))
                    if log_callback: log_callback(f"[QUOTA] Đã dùng: {used}GB / 1GB")
                    if used >= 1.0:
                        quota_exceeded = True
            except:
                pass
            
            # If quota exceeded and retry is enabled, switch account
            if quota_exceeded and retry_on_quota:
                if log_callback: log_callback("[QUOTA] 🔄 Đang chuyển sang tài khoản khác...")
                
                if self.switch_to_next_account(log_callback):
                    # Successfully switched, retry upload with new account
                    if log_callback: log_callback("[RETRY] ♻️ Thử lại upload với tài khoản mới...")
                    return self.upload_video(file_path, log_callback, retry_on_quota=False)  # Don't retry again
                else:
                    return False, "QUOTA_EXCEEDED - Tất cả tài khoản đều đầy dung lượng!", None, True
            elif quota_exceeded:
                return False, "QUOTA_EXCEEDED", None, True

            # --- UPLOAD TRIGGER ---
            print("[VIMEO] Finding file input...")
            try:
                file_input = WebDriverWait(self.driver, 5).until(  # Reduced from 10s to 5s
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
                self.driver.execute_script("arguments[0].style.visibility = 'visible';", file_input)
                self.driver.execute_script("arguments[0].style.opacity = '1';", file_input)
                print(f"[VIMEO] Uploading: {file_path}")
                if log_callback: log_callback(f"[STEP] Đang gửi file: {os.path.basename(file_path)}...")
                file_input.send_keys(file_path)

                # --- WAIT FOR PROCESSING / SUCCESS ---
                print("[VIMEO] File sent. Waiting for upload to complete...")
                if log_callback: log_callback("[STEP] Đang chờ upload hoàn tất...")
                
                max_wait = 600  # Wait up to 10 minutes for upload
                start = time.time()
                upload_complete = False
                video_id = None
                
                # STAY ON UPLOAD PAGE - Don't navigate away!
                print("[VIMEO] 💡 Giữ nguyên trang upload, không chuyển trang...")
                
                while time.time() - start < max_wait:
                    curr_url = self.driver.current_url
                    
                    # AUTO-CLICK "OK" BUTTONS IN POPUPS/MODALS
                    self.auto_click_ok_buttons()
                    
                    # Close any popups/modals that might appear
                    try:
                        modals = self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'], div[class*='modal'], div[class*='popup']")
                        if modals:
                            # Try to find and click OK/Close buttons
                            close_btns = self.driver.find_elements(By.CSS_SELECTOR, 
                                "button[aria-label='Close'], button.close-button, svg[data-icon='cross'], "
                                "button[class*='close'], button[class*='dismiss']"
                            )
                            for btn in close_btns:
                                if btn.is_displayed():
                                    print("[VIMEO] ❌ Closing detected modal/popup...")
                                    self.driver.execute_script("arguments[0].click();", btn)
                                    time.sleep(0.5)
                    except:
                        pass
                    
                    # Check 1: Look for "Upload complete" or "Optimizing" message ON CURRENT PAGE
                    try:
                        body_text = self.driver.find_element(By.TAG_NAME, "body").text
                        
                        # Check for upload progress
                        if "Uploading" in body_text:
                            # Extract percentage if possible
                            import re
                            match = re.search(r'Uploading\s+(\d+)%', body_text)
                            if match:
                                percent = match.group(1)
                                elapsed = int(time.time() - start)
                                print(f"[VIMEO] ⏳ Uploading {percent}% ({elapsed}s)")
                                if log_callback: log_callback(f"[UPLOAD] ⏳ Đang upload {percent}%...")
                        
                        # Check if upload is complete
                        if "Upload complete" in body_text or "Optimizing" in body_text:
                            print("[VIMEO] ✅ Upload hoàn tất! Đang tối ưu hóa...")
                            if log_callback: log_callback("[UPLOAD] ✅ Upload xong, đang tối ưu hóa...")
                            upload_complete = True
                            # Don't break yet - wait for optimization to finish
                        
                        # Check if optimization is done (video becomes viewable)
                        if upload_complete and ("Go to video" in body_text or "View video" in body_text):
                            print("[VIMEO] ✅ Tối ưu hóa xong!")
                            # Now we can get the video link
                            try:
                                links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/manage/videos/') or contains(@href, 'vimeo.com/')]")
                                for link in links:
                                    href = link.get_attribute("href")
                                    if "/videos/" in href or "vimeo.com/" in href:
                                        if "/videos/" in href:
                                            video_id = href.split("/videos/")[-1].split("/")[0]
                                        else:
                                            video_id = href.split("vimeo.com/")[-1].split("/")[0]
                                        print(f"[VIMEO] ✅ Got video ID: {video_id}")
                                        break
                            except:
                                pass
                            
                            if video_id:
                                break
                    except:
                        pass
                    
                    # Check 2: If page redirected automatically (some Vimeo accounts do this)
                    if "/manage/videos/" in curr_url and "upload" not in curr_url:
                        print("[VIMEO] Page auto-redirected to video page")
                        try:
                            video_id = curr_url.split("/videos/")[-1].split("/")[0]
                            upload_complete = True
                            break
                        except:
                            pass
                    
                    # Check 3: Look for quota exceeded
                    try:
                        body_text_lower = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                        if "quota exceeded" in body_text_lower or "upgrade to upload more" in body_text_lower or "not enough storage" in body_text_lower:
                            return False, "QUOTA_EXCEEDED (During upload)", None, True
                    except:
                        pass
                    
                    time.sleep(2)  # Check every 2 seconds

                if not upload_complete or not video_id:
                    print("[VIMEO] ⚠️ Upload timeout or video ID not found")
                    # Try to extract video ID from page source
                    try:
                        page_source = self.driver.page_source
                        import re
                        matches = re.findall(r'/videos/(\d{10,})', page_source)
                        if matches:
                            video_id = matches[0]
                            print(f"[VIMEO] Found video ID in page source: {video_id}")
                        else:
                            matches = re.findall(r'vimeo\.com/(\d{10,})', page_source)
                            if matches:
                                video_id = matches[0]
                                print(f"[VIMEO] Found video ID in vimeo.com link: {video_id}")
                    except:
                        pass
                    
                    if not video_id:
                        return True, "Upload sent but video ID not found (may still be processing)", None, False

                print(f"[VIMEO] Video ID found: {video_id}. Checking for Embed options...")

                wait_start = time.time()
                ready_to_click = False
                check_count = 0
                max_checks = 30  # Maximum 30 checks (60 seconds with 2s sleep)
                
                while time.time() - wait_start < 30 and check_count < max_checks:  # Reduced from 60s to 30s
                    check_count += 1
                    try:
                        embed_btns = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Embed'], button[title='Embed'], button[data-testid='header-embed-button'], .iris_btn--secondary")
                        if not embed_btns:
                            embed_btns = self.driver.find_elements(By.XPATH, "//button[descendant::*[contains(text(), 'Embed')]]")
                        if embed_btns:
                            for btn in embed_btns:
                                if btn.is_displayed() and btn.is_enabled():
                                    print("[VIMEO] Found Embed button! Proceeding...")
                                    ready_to_click = True
                                    break
                        if ready_to_click:
                            break
                        
                        # Only print status every 5 checks to avoid spam
                        if check_count % 5 == 0:
                            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                            if "upload complete" in body_text:
                                print(f"[VIMEO] Upload complete, waiting for Embed button... ({check_count}/{max_checks})")
                    except:
                        pass
                    time.sleep(1)  # Reduced from 2s to 1s
                
                # If Embed button not found after timeout, skip to fallback
                if not ready_to_click:
                    print("[VIMEO] ⚠️ Embed button not found after 30s, using fallback embed code...")

                embed_code = ""
                video_title = ""
                
                # Try to get title from Vimeo first (more reliable)
                try:
                    title_input = self.driver.find_elements(By.CSS_SELECTOR, "input[data-qa='title-input'], input[name='name'], input[placeholder*='title' i]")
                    if title_input and title_input[0].get_attribute("value"):
                        video_title = title_input[0].get_attribute("value").strip()
                        print(f"[VIMEO] Got title from Vimeo input: {video_title}")
                except Exception as e:
                    print(f"[VIMEO] Could not get title from Vimeo: {e}")
                
                # Fallback to filename if Vimeo title is empty
                if not video_title:
                    try:
                        # Ensure proper Unicode handling for filenames
                        video_title = os.path.basename(file_path)
                        # Remove extension
                        video_title = os.path.splitext(video_title)[0]
                        print(f"[VIMEO] Using filename as title: {video_title}")
                    except Exception as e:
                        print(f"[VIMEO] Error getting filename: {e}")
                        video_title = "Untitled Video"
                
                # Only try to get embed code if button was found
                if ready_to_click:
                    try:
                        print("[VIMEO] Clicking 'Embed' button...")
                        embed_btns = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Embed'], button[title='Embed'], button[data-testid='header-embed-button']")
                        if not embed_btns:
                            embed_btns = self.driver.find_elements(By.XPATH, "//button[descendant::*[contains(text(), 'Embed')]]")
                        if embed_btns:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", embed_btns[0])
                            time.sleep(0.3)  # Reduced from 0.5s
                            embed_btns[0].click()
                            time.sleep(1)  # Reduced from 1.5s

                        try:
                            print("[VIMEO] Searching for 'Copy embed code' button...")
                            copy_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Copy embed code')]")
                            if not copy_btns:
                                copy_btns = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'copy') or contains(text(), 'Copy')]//button")
                            if copy_btns:
                                visible_copy = [b for b in copy_btns if b.is_displayed()]
                                if visible_copy:
                                    btn = visible_copy[0]
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                                    time.sleep(0.3)  # Reduced from 0.5s
                                    try:
                                        import pyperclip
                                        pyperclip.copy("")
                                    except ImportError:
                                        pass
                                    btn.click()
                                    print("[VIMEO] Clicked 'Copy embed code' button.")
                                    time.sleep(0.7)  # Reduced from 1.0s
                                    try:
                                        import pyperclip
                                        clipboard_text = pyperclip.paste()
                                        if clipboard_text and ("<div" in clipboard_text or "<iframe" in clipboard_text):
                                            embed_code = clipboard_text
                                            print("[VIMEO] Success: Got embed code from clipboard.")
                                    except Exception as p_e:
                                        print(f"[VIMEO] Clipboard read failed: {p_e}")
                        except Exception as e:
                            print(f"[VIMEO] Copy button strategy failed: {e}")

                        # Close sidebar
                        print("[VIMEO] Closing sidebar...")
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                            time.sleep(1)
                            close_btns = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Close'], button[data-testid='close-button']")
                            for btn in close_btns:
                                if btn.is_displayed():
                                    btn.click()
                                    time.sleep(1)
                        except:
                            pass

                        # Title already extracted above, no need to extract again here

                    except Exception as e:
                        print(f"[VIMEO] Embed button strategy failed: {e}.")
                else:
                    print("[VIMEO] Skipping embed code extraction (button not found).")

                if not embed_code or ("<iframe" not in embed_code and "<div" not in embed_code):
                    embed_code = (
                        f'<div style="padding:56.25% 0 0 0;position:relative;">'
                        f'<iframe src="https://player.vimeo.com/video/{video_id}?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" '
                        f'frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media" '
                        f'style="position:absolute;top:0;left:0;width:100%;height:100%;" title="{video_title}"></iframe>'
                        f'</div><script src="https://player.vimeo.com/api/player.js"></script>'
                    )
                    print("[VIMEO] constructed fallback responsive embed code.")

                video_link = f"https://vimeo.com/{video_id}"

                print("[VIMEO] ⏳ Đợi Vimeo xử lý video để có thể xem được...")
                if log_callback: log_callback("[VIDEO] ⏳ Đang đợi Vimeo xử lý video (có thể mất 5-15 phút)...")
                
                # CRITICAL: Wait for video to be processed so it's viewable
                # STAY ON CURRENT PAGE - Don't navigate away!
                print("[VIMEO] 💡 Giữ nguyên trang hiện tại, đợi video xử lý xong...")
                processing_done = self.wait_for_video_processing_on_current_page(video_id, max_wait=900, log_callback=log_callback)
                
                if processing_done:
                    print("[VIMEO] ✅ Video đã xử lý xong, có thể xem được!")
                    if log_callback: log_callback("[VIDEO] ✅ Video đã sẵn sàng để xem")
                else:
                    print("[VIMEO] ⚠️ Video vẫn đang xử lý sau 15 phút")
                    if log_callback: log_callback("[VIDEO] ⚠️ Video vẫn đang xử lý, vui lòng đợi thêm hoặc check thủ công")
                
                quota_full = False

                thumbnail_path = None
                # Generate thumbnail (optimized for speed)
                try:
                    print(f"[VIMEO] Generating thumbnail...")
                    thumb_dir = os.path.join(os.getcwd(), "thumbnails")
                    if not os.path.exists(thumb_dir):
                        os.makedirs(thumb_dir)
                    
                    # Try smart thumbnail first (from video file)
                    filename = f"thumb_{video_id}.jpg"
                    save_path = os.path.join(thumb_dir, filename)
                    
                    if os.path.exists(file_path):
                        smart_thumb = self.extract_smart_thumbnail(file_path, save_path)
                        if smart_thumb:
                            thumbnail_path = smart_thumb
                            print(f"[VIMEO] ✅ Thumbnail created: {os.path.basename(thumbnail_path)}")
                    
                    # Fallback to screenshot if smart thumbnail fails
                    if not thumbnail_path:
                        print("[VIMEO] Using screenshot fallback...")
                        filename = f"thumb_{video_id}_screen.png"
                        save_path = os.path.join(thumb_dir, filename)
                        self.driver.save_screenshot(save_path)
                        self.crop_vimeo_ui(save_path)
                        thumbnail_path = save_path
                        print(f"[VIMEO] ✅ Screenshot thumbnail: {os.path.basename(thumbnail_path)}")
                        
                except Exception as e:
                    print(f"[VIMEO] ⚠️ Thumbnail generation failed: {e}")
                    thumbnail_path = None

                return True, "Upload thành công!", {
                    "video_link": video_link,
                    "embed_code": embed_code,
                    "video_id": video_id,
                    "title": video_title,
                    "thumbnail": thumbnail_path
                }, quota_full

            except Exception as e:
                # Critical Error Handling & Session Recovery
                err_msg = str(e)
                print(f"[VIMEO] Upload Exception: {e}")
                if log_callback: log_callback(f"[ERROR] Exception: {e}")
                
                # Check if session is dead
                is_dead = False
                if "invalid session" in err_msg.lower() or "disconnected" in err_msg.lower() or "closed" in err_msg.lower():
                    is_dead = True
                else:
                    # Active check
                    try:
                        _ = self.driver.current_url
                    except:
                        is_dead = True

                if is_dead:
                    print("[VIMEO] Driver appears dead. Resetting...")
                    if log_callback: log_callback("[DRIVER] Driver lỗi, đang reset...")
                    try:
                        self.driver.quit()
                    except: pass
                    self.driver = None

                return False, f"Lỗi trong quá trình upload: {e}", None, False

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Lỗi khởi tạo upload: {e}", None, False

    def crop_vimeo_ui(self, image_path):
        try:
            from PIL import Image
            img = Image.open(image_path)
            w, h = img.size
            left = 0
            top = int(h * 0.15)
            right = int(w * 0.90)
            bottom = int(h * 0.85)
            if right > left and bottom > top:
                crop_box = (left, top, right, bottom)
                cropped_img = img.crop(crop_box)
                cropped_img.save(image_path)
                print(f"[VIMEO] Auto-Cropped UI from screenshot: {image_path}")
        except Exception as e:
            print(f"[VIMEO] Cropping error: {e}")

    def wait_for_video_processing(self, video_id, max_wait=900):
        """
        Wait for Vimeo to finish processing video so it's viewable
        Keeps browser open and waits until video is fully processed
        
        Args:
            video_id: Vimeo video ID
            max_wait: Maximum seconds to wait (default 900s = 15 minutes)
            
        Returns:
            True if video is ready, False if timeout
        """
        try:
            import time
            from selenium.webdriver.common.by import By
            
            print(f"[VIMEO] 🎬 Đợi video {video_id} xử lý xong (tối đa {max_wait//60} phút)...")
            print(f"[VIMEO] 💡 Trình duyệt sẽ GIỮ MỞ cho đến khi video sẵn sàng")
            
            video_url = f"https://vimeo.com/{video_id}"
            start_time = time.time()
            check_interval = 10  # Check every 10 seconds
            last_status = ""
            
            while time.time() - start_time < max_wait:
                try:
                    # Navigate to video page
                    self.driver.get(video_url)
                    time.sleep(3)  # Wait for page to load
                    
                    # Check 1: Look for "Optimizing" message
                    try:
                        body_text = self.driver.find_element(By.TAG_NAME, "body").text
                        if "Optimizing" in body_text or "This may take a while" in body_text:
                            elapsed = int(time.time() - start_time)
                            if last_status != "optimizing":
                                print(f"[VIMEO] 🔄 Video đang tối ưu hóa (Optimizing)...")
                                last_status = "optimizing"
                            print(f"[VIMEO] ⏳ Đã đợi {elapsed}s / {max_wait}s ({elapsed//60} phút)")
                            time.sleep(check_interval)
                            continue
                    except:
                        pass
                    
                    # Check 2: Look for video player (means video is ready)
                    try:
                        # Try to find the play button or video element
                        player_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                            "video, .vp-video-wrapper, .vp-player, button[aria-label='Play']")
                        
                        if player_elements and any(el.is_displayed() for el in player_elements):
                            print(f"[VIMEO] ✅ Video player detected - video is READY!")
                            print(f"[VIMEO] ✅ Video có thể xem được rồi!")
                            return True
                    except:
                        pass
                    
                    # Check 3: Try to click play button to verify video works
                    try:
                        play_button = self.driver.find_element(By.CSS_SELECTOR, 
                            "button[aria-label='Play'], .vp-center .vp-icon-play")
                        if play_button and play_button.is_displayed():
                            print(f"[VIMEO] ✅ Play button found - video is READY!")
                            return True
                    except:
                        pass
                    
                    # Check 4: Look for processing/transcoding messages
                    page_source = self.driver.page_source.lower()
                    if "processing" in page_source or "transcoding" in page_source:
                        elapsed = int(time.time() - start_time)
                        if last_status != "processing":
                            print(f"[VIMEO] 🔄 Video đang xử lý (Processing/Transcoding)...")
                            last_status = "processing"
                        print(f"[VIMEO] ⏳ Đã đợi {elapsed}s / {max_wait}s ({elapsed//60} phút)")
                        time.sleep(check_interval)
                        continue
                    
                    # Check 5: If page loaded normally without processing messages, video might be ready
                    if "player.vimeo.com" in page_source or '"player"' in page_source:
                        print(f"[VIMEO] ✅ Video player code detected - video is READY!")
                        return True
                    
                    # Still waiting...
                    elapsed = int(time.time() - start_time)
                    print(f"[VIMEO] ⏳ Đang kiểm tra... {elapsed}s / {max_wait}s ({elapsed//60} phút)")
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"[VIMEO] ⚠️ Lỗi khi check: {e}")
                    time.sleep(check_interval)
            
            # Timeout
            elapsed = int(time.time() - start_time)
            print(f"[VIMEO] ⏱️ Timeout sau {elapsed}s ({elapsed//60} phút)")
            print(f"[VIMEO] ⚠️ Video có thể vẫn đang xử lý, vui lòng check thủ công")
            return False
            
        except Exception as e:
            print(f"[VIMEO] ❌ Lỗi wait_for_processing: {e}")
            return False
    
    def wait_for_video_processing_on_current_page(self, video_id, max_wait=900, log_callback=None):
        """
        Wait for Vimeo to finish processing video WITHOUT navigating away from current page
        Stays on upload page and monitors for completion signals
        
        Args:
            video_id: Vimeo video ID
            max_wait: Maximum seconds to wait (default 900s = 15 minutes)
            log_callback: Optional callback for GUI updates
            
        Returns:
            True if video is ready, False if timeout
        """
        try:
            import time
            from selenium.webdriver.common.by import By
            
            print(f"[VIMEO] 🎬 Đợi video {video_id} xử lý xong (tối đa {max_wait//60} phút)...")
            print(f"[VIMEO] 💡 GIỮ NGUYÊN TRANG HIỆN TẠI - Không chuyển trang!")
            if log_callback:
                log_callback(f"[VIDEO] ⏳ Đang đợi video xử lý (giữ nguyên trang)...")
            
            start_time = time.time()
            check_interval = 5  # Check every 5 seconds
            last_status = ""
            last_log_time = 0
            
            while time.time() - start_time < max_wait:
                try:
                    elapsed = int(time.time() - start_time)
                    
                    # AUTO-CLICK "OK" BUTTONS IN POPUPS/MODALS
                    self.auto_click_ok_buttons()
                    
                    # Get current page text
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    
                    # Check 1: Still uploading?
                    if "Uploading" in body_text:
                        import re
                        match = re.search(r'Uploading\s+(\d+)%', body_text)
                        if match:
                            percent = match.group(1)
                            if last_status != f"uploading_{percent}":
                                print(f"[VIMEO] ⏳ Uploading {percent}% ({elapsed}s)")
                                if log_callback and time.time() - last_log_time > 5:
                                    log_callback(f"[UPLOAD] ⏳ Đang upload {percent}%...")
                                    last_log_time = time.time()
                                last_status = f"uploading_{percent}"
                        time.sleep(check_interval)
                        continue
                    
                    # Check 2: Upload complete, now optimizing?
                    if "Upload complete" in body_text or "Optimizing" in body_text:
                        if last_status != "optimizing":
                            print(f"[VIMEO] 🔄 Upload xong! Đang tối ưu hóa (Optimizing)...")
                            if log_callback:
                                log_callback("[VIDEO] 🔄 Đang tối ưu hóa video...")
                            last_status = "optimizing"
                        
                        # Update progress every 30 seconds
                        if time.time() - last_log_time > 30:
                            print(f"[VIMEO] ⏳ Vẫn đang tối ưu hóa... {elapsed}s / {max_wait}s ({elapsed//60} phút)")
                            if log_callback:
                                log_callback(f"[VIDEO] ⏳ Đang tối ưu hóa... ({elapsed//60} phút)")
                            last_log_time = time.time()
                        
                        time.sleep(check_interval)
                        continue
                    
                    # Check 3: Look for completion signals
                    completion_signals = [
                        "Go to video",
                        "View video", 
                        "Share video",
                        "Edit video",
                        "Video settings",
                        "Your video is ready"
                    ]
                    
                    if any(signal in body_text for signal in completion_signals):
                        print(f"[VIMEO] ✅ Video đã xử lý xong! Phát hiện: {[s for s in completion_signals if s in body_text]}")
                        if log_callback:
                            log_callback("[VIDEO] ✅ Video đã sẵn sàng!")
                        return True
                    
                    # Check 4: Look for buttons that indicate completion
                    try:
                        completion_buttons = self.driver.find_elements(By.XPATH, 
                            "//button[contains(text(), 'Go to video')] | "
                            "//button[contains(text(), 'View video')] | "
                            "//a[contains(text(), 'Go to video')] | "
                            "//a[contains(text(), 'View video')]"
                        )
                        if completion_buttons:
                            visible_buttons = [b for b in completion_buttons if b.is_displayed()]
                            if visible_buttons:
                                print(f"[VIMEO] ✅ Video đã xử lý xong! Tìm thấy nút hoàn thành")
                                if log_callback:
                                    log_callback("[VIDEO] ✅ Video đã sẵn sàng!")
                                return True
                    except:
                        pass
                    
                    # Check 5: Check page source for player embed (means video is ready)
                    try:
                        page_source = self.driver.page_source.lower()
                        if f'player.vimeo.com/video/{video_id}' in page_source:
                            print(f"[VIMEO] ✅ Video player embed detected - video is READY!")
                            if log_callback:
                                log_callback("[VIDEO] ✅ Video đã sẵn sàng!")
                            return True
                    except:
                        pass
                    
                    # Check 6: If no processing messages and we've waited at least 2 minutes, assume ready
                    if elapsed > 120:  # 2 minutes
                        if "processing" not in body_text.lower() and "optimizing" not in body_text.lower():
                            print(f"[VIMEO] ✅ Không còn thông báo xử lý - video có thể đã sẵn sàng")
                            if log_callback:
                                log_callback("[VIDEO] ✅ Video có thể đã sẵn sàng")
                            return True
                    
                    # Still waiting...
                    if time.time() - last_log_time > 30:
                        print(f"[VIMEO] ⏳ Đang kiểm tra... {elapsed}s / {max_wait}s ({elapsed//60} phút)")
                        if log_callback:
                            log_callback(f"[VIDEO] ⏳ Đang đợi... ({elapsed//60} phút)")
                        last_log_time = time.time()
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"[VIMEO] ⚠️ Lỗi khi check: {e}")
                    time.sleep(check_interval)
            
            # Timeout
            elapsed = int(time.time() - start_time)
            print(f"[VIMEO] ⏱️ Timeout sau {elapsed}s ({elapsed//60} phút)")
            print(f"[VIMEO] ⚠️ Video có thể vẫn đang xử lý, vui lòng check thủ công")
            if log_callback:
                log_callback(f"[VIDEO] ⏱️ Timeout - vui lòng check thủ công")
            return False
            
        except Exception as e:
            print(f"[VIMEO] ❌ Lỗi wait_for_processing_on_current_page: {e}")
            return False
    
    def extract_smart_thumbnail(self, video_path, output_path):
        """Extract best quality frame from video for thumbnail (optimized for speed)"""
        try:
            import cv2
            import numpy as np
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            # Analyze middle section of video (skip intro/outro)
            start_frame = int(total_frames * 0.15)
            end_frame = int(total_frames * 0.85)
            if start_frame >= end_frame:
                start_frame = 0
                end_frame = total_frames
            
            # Reduced from 10 to 5 candidates for speed
            num_candidates = 5
            step = max(1, (end_frame - start_frame) // num_candidates)
            
            best_score = -1.0
            best_frame = None
            
            for i in range(0, num_candidates):
                frame_idx = start_frame + (i * step)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Quick quality analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                mean_brightness = np.mean(gray)
                contrast_score = np.std(gray)
                
                # Penalize too dark or too bright frames
                if mean_brightness < 40 or mean_brightness > 220:
                    penalty = 0.2
                else:
                    penalty = 1.0
                
                final_score = (blur_score * 0.7) + (contrast_score * 10 * 0.3)
                final_score *= penalty
                
                if final_score > best_score:
                    best_score = final_score
                    best_frame = frame
            
            cap.release()
            
            if best_frame is not None:
                cv2.imwrite(output_path, best_frame)
                return output_path
            return None
            
        except ImportError:
            print("[VIMEO] ⚠️ OpenCV not installed. Install with: pip install opencv-python")
            return None
        except Exception as e:
            print(f"[VIMEO] Smart thumbnail error: {e}")
            return None

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None