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
import threading
import requests


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

    def init_driver(self, headless=False, proxy=None, is_mobile=False, user_data_dir=None, browser_type='chrome'):
        """Initialize Chrome Driver with Enhanced Anti-Detect, Mobile Option & Profile Support"""
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

        # ... (User Agent Logic omitted for brevity, assuming existing) ...
        # Lấy lại đoạn user agent cũ hoặc chỉ update đoạn options
        # Để an toàn, tôi sẽ copy lại logic init_driver nhưng thêm user_data_dir xử lý
        
        # --- 1. ENHANCED USER AGENTS ---
        if is_mobile:
            user_agents = [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36"
            ]
        else:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Safari/537.36"
            ]
            
        chosen_ua = random.choice(user_agents)
        print(f"[VIMEO] Using User-Agent: {chosen_ua}")
        
        # Options setup
        if HAS_UC:
            options = uc.ChromeOptions()
        else:
            options = webdriver.ChromeOptions()
            
        # --- PROFILE SUPPORT (NEW) ---
        if user_data_dir:
            user_data_dir = os.path.abspath(user_data_dir)
            options.add_argument(f"--user-data-dir={user_data_dir}")
            print(f"[VIMEO] 📂 Loading Profile: {user_data_dir}")
            
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-notifications")
        options.add_argument(f"user-agent={chosen_ua}")
        
        # --- BRAVE BROWSER SUPPORT ---
        if browser_type == 'brave':
            brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            if not os.path.exists(brave_path):
                 brave_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), r"BraveSoftware\Brave-Browser\Application\brave.exe")
            
            if os.path.exists(brave_path):
                options.binary_location = brave_path
                print(f"[VIMEO] ✅ Dùng Brave Browser: {brave_path}")
            else:
                print(f"[VIMEO] ⚠️ Không tìm thấy Brave tại các đường dẫn mặc định. Dùng trình duyệt mặc định.")
            
            # Tắt Brave Shields và các tính năng gây block/timeout
            options.add_argument("--disable-brave-extension")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-features=BraveShields,BraveAdBlockService,BraveRewards,BraveNews,BraveVPN,BraveGlobalPrivacyControl")
            options.add_argument("--shield-mode=off")
            # Tắt Global Privacy Control (GPC) - Vimeo dùng để detect bot
            options.add_argument("--disable-features=GlobalPrivacyControl")
            options.page_load_strategy = 'eager'

            # Tắt Shields qua prefs (cách mạnh nhất)
            if 'prefs' not in dir():
                prefs = {}
            extra_prefs = {
                "brave.shields.default_shields_up": False,
                "brave.shields.advanced_view_enabled": False,
                "profile.default_content_setting_values.brave_shields": 2,
                # Tắt Global Privacy Control
                "brave.global_privacy_control_enabled": False,
                "privacy.donottrackheader.enabled": False,
            }
            self._brave_extra_prefs = extra_prefs

        
        if is_mobile:
             options.add_argument("--enable-touch-events")
             
        # --- BLOCK WEBRTC ---
        options.add_argument("--disable-webrtc")
        prefs = {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False
        }
        
        # Add password saving prefs to avoid popup
        prefs["credentials_enable_service"] = False
        prefs["profile.password_manager_enabled"] = False

        # Merge Brave Shields prefs nếu có
        if hasattr(self, '_brave_extra_prefs'):
            prefs.update(self._brave_extra_prefs)
            del self._brave_extra_prefs
        
        try:
            options.add_experimental_option("prefs", prefs)
        except:
            pass

        # Standard Selenium Flags
        if not HAS_UC:
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        
        # Headless optimizations
        if headless:
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
        
        # Proxy
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
                    
                    with zipfile.ZipFile(pluginfile, 'w') as zp:
                        zp.writestr("manifest.json", manifest_json)
                        zp.writestr("background.js", background_js)
                    
                    options.add_extension(pluginfile)
                else:
                    print(f"[VIMEO] Invalid Proxy Format (host:port:user:pass): {proxy}")
            except Exception as e:
                print(f"[VIMEO] Proxy Error: {e}")

        # Driver Initialization
        try:
            print(f"[VIMEO] Initializing Driver ({'UC' if HAS_UC else 'Standard'} Mode)...")
            
            if HAS_UC:
                # ── Xác định driver local và chrome binary ──
                driver_executable_path = None
                if os.path.exists("driver/chromedriver.exe"):
                    driver_executable_path = os.path.abspath("driver/chromedriver.exe")

                # Đọc version từ chromedriver.exe (nguồn đáng tin nhất)
                chrome_version = None
                if driver_executable_path:
                    try:
                        import subprocess as _sp
                        ps_result = _sp.check_output(
                            ["powershell", "-NoProfile", "-Command",
                             f"(Get-Item '{driver_executable_path}').VersionInfo.FileVersion"],
                            stderr=_sp.DEVNULL, creationflags=0x08000000, timeout=5
                        ).decode().strip()
                        chrome_version = int(ps_result.split('.')[0])
                        print(f"[VIMEO] ✅ ChromeDriver version: {chrome_version}")
                    except Exception as ve:
                        print(f"[VIMEO] ⚠️ Không đọc được version driver: {ve}")

                # Set binary_location = chrome_portable nếu tồn tại (khớp với driver local)
                # SKIP nếu đang dùng Brave (Brave tự quản lý binary của nó)
                chrome_portable = os.path.abspath("chrome_portable/chrome.exe")
                if browser_type != 'brave' and os.path.exists(chrome_portable):
                    options.binary_location = chrome_portable
                    print(f"[VIMEO] ✅ Dùng Chrome Portable v{chrome_version}: {chrome_portable}")
                    # Nếu chưa có version, đọc từ portable
                    if not chrome_version:
                        try:
                            import subprocess as _sp
                            ps_result2 = _sp.check_output(
                                ["powershell", "-NoProfile", "-Command",
                                 f"(Get-Item '{chrome_portable}').VersionInfo.FileVersion"],
                                stderr=_sp.DEVNULL, creationflags=0x08000000, timeout=5
                            ).decode().strip()
                            chrome_version = int(ps_result2.split('.')[0])
                            print(f"[VIMEO] ✅ Chrome Portable version: {chrome_version}")
                        except Exception as ve2:
                            print(f"[VIMEO] ⚠️ Không đọc version portable: {ve2}")
                elif browser_type == 'brave':
                    # Brave: không dùng chrome_portable, không dùng driver local (version mismatch)
                    # UC sẽ tự detect Brave version và download driver phù hợp
                    driver_executable_path = None
                    chrome_version = None
                    print(f"[VIMEO] ℹ️ Brave mode: bỏ qua chrome_portable và driver local, UC tự detect")
                else:
                    # Không có portable → Chrome hệ thống → không set version_main để UC tự detect
                    chrome_version = None
                    print(f"[VIMEO] ℹ️ Không có chrome_portable, dùng Chrome hệ thống (UC tự detect)")

                # Build kwargs và khởi động
                uc_kwargs = {"options": options, "headless": headless, "use_subprocess": True}
                if chrome_version:
                    uc_kwargs["version_main"] = chrome_version
                if driver_executable_path:
                    uc_kwargs["driver_executable_path"] = driver_executable_path

                print(f"[VIMEO] 🚀 Launching UC Chrome (version_main={chrome_version})...")
                self.driver = uc.Chrome(**uc_kwargs)
            else:
                self.driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()), options=options
                )
            
            # Additional mobile emulation via CDP if needed
            if is_mobile:
                self.driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {"enabled": True})

            # --- BROWSER FINGERPRINT SPOOFING ---
            self._inject_fingerprint_spoof()

            # --- TẮT BRAVE SHIELDS cho vimeo.com qua CDP ---
            if browser_type == 'brave':
                try:
                    self.driver.execute_cdp_cmd("Brave.setAdBlockingEnabled", {"enabled": False})
                except: pass
                try:
                    # Điều hướng đến brave://settings/shields để tắt qua JS
                    # Cách đáng tin: dùng CDP Storage để set preference
                    self.driver.execute_cdp_cmd("Storage.setStorageItem", {
                        "storageId": {"storageType": "local", "securityOrigin": "chrome://settings"},
                        "key": "brave_shields_default",
                        "value": "0"
                    })
                except: pass
                print("[BRAVE] 🛡️ Shields disabled via prefs")

            self.driver.set_page_load_timeout(120)
            print("[VIMEO] ✅ Browser initialized successfully.")
            return True
        except Exception as e:
            print(f"[VIMEO] ❌ Init Driver Error: {e}")
            self.driver = None
            return False


    # ... (Rest of file) ...

    def login_interactive(self, email, password, browser_type='brave'):
        """
        Login with PERSISTENT PROFILE.
        1. Creates a profile folder for this email.
        2. Opens browser. If previously logged in, it will auto-login via cookies.
        3. If not, it attempts to fill form (or user fills it).
        """
        import re
        try:
            # 1. Prepare Profile Path
            safe_email = re.sub(r'[^a-zA-Z0-9]', '_', email)
            profile_path = os.path.join(os.getcwd(), "browser_profiles", safe_email)
            os.makedirs(profile_path, exist_ok=True)
            
            print(f"[VIMEO] 🚀 Starting session for: {email}")
            print(f"[VIMEO] 📂 Profile stored at: {profile_path}")
            
            # 2. Start browser with Profile
            self.init_driver(headless=False, user_data_dir=profile_path, browser_type=browser_type)
            
            # 3. Go to Vimeo
            self.driver.get("https://vimeo.com/log_in")
            time.sleep(3)
            
            # 4. Check if already logged in (by URL redirect or element)
            current_url = self.driver.current_url
            if "log_in" not in current_url and "join" not in current_url:
                 print(f"[VIMEO] ✅ Detected PREVIOUS SESSION. Already logged in!")
                 print(f"[VIMEO] 🎉 Bạn đã đăng nhập từ trước!")
            else:
                # Try auto-fill if on login page
                try:
                    print("[VIMEO] 🔐 Attempting to auto-fill credentials...")
                    email_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.NAME, "email"))
                    )
                    email_input.clear()
                    email_input.send_keys(email)
                    email_input.send_keys(Keys.RETURN)
                    time.sleep(2)
                    
                    pwd_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.NAME, "password"))
                    )
                    pwd_input.clear()
                    pwd_input.send_keys(password)
                    pwd_input.send_keys(Keys.RETURN)
                    print("[VIMEO] ✅ Auto-filled credentials. Please solve CAPTCHA if asked.")
                except Exception as e:
                    print(f"[VIMEO] ⚠️ Could not auto-fill (maybe already logged in or changed layout): {e}")
            
            # 5. KEEP ALIVE LOOP
            print(f"[VIMEO] 🛑 Browser is open. Close the window to end session.")
            while True:
                try:
                    if not self.driver.window_handles:
                        break
                    time.sleep(1)
                except:
                    break
                    
            print(f"[VIMEO] Session ended for {email}")
            
        except Exception as e:
            print(f"[VIMEO] Error in interactive session: {e}")
        finally:
            self.close()
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
                            
                            # ── STEP 1: Xác định driver/chromedriver local ──
                            driver_executable_path = None
                            if os.path.exists("driver/chromedriver.exe"):
                                driver_executable_path = os.path.abspath("driver/chromedriver.exe")

                            # ── STEP 2: Đọc version từ chromedriver.exe (Source of truth) ──
                            # chromedriver và chrome binary PHẢI cùng version
                            detected_version = None
                            if driver_executable_path and os.path.exists(driver_executable_path):
                                try:
                                    import subprocess as _sp
                                    ps_cmd = f"(Get-Item '{driver_executable_path}').VersionInfo.FileVersion"
                                    ps_out = _sp.check_output(
                                        ["powershell", "-NoProfile", "-Command", ps_cmd],
                                        stderr=_sp.DEVNULL, creationflags=0x08000000, timeout=5
                                    ).decode().strip()
                                    detected_version = int(ps_out.split('.')[0])
                                    print(f"[VIMEO] ✅ ChromeDriver version: {detected_version} (từ driver/chromedriver.exe)")
                                except Exception as ver_e:
                                    print(f"[VIMEO] ⚠️ Không đọc được version driver: {ver_e}")

                            # ── STEP 3: Chọn Chrome binary KHỚP với driver version ──
                            # SKIP nếu đang dùng Brave (binary_location đã được set ở trên)
                            chrome_portable_path = os.path.abspath("chrome_portable/chrome.exe")
                            if browser_type == 'brave':
                                # Brave mode: bỏ qua chrome_portable và driver local
                                # UC tự detect Brave version và download chromedriver phù hợp
                                driver_executable_path = None
                                detected_version = None
                                print(f"[VIMEO] ℹ️ Brave mode: UC tự detect version, bỏ qua driver local")
                            elif os.path.exists(chrome_portable_path):
                                # Dùng chrome_portable (khớp với driver local)
                                options.binary_location = chrome_portable_path
                                print(f"[VIMEO] ✅ Dùng Chrome Portable: {chrome_portable_path}")
                                # Nếu chưa detect được version từ driver, đọc từ portable
                                if not detected_version:
                                    try:
                                        import subprocess as _sp
                                        ps_cmd2 = f"(Get-Item '{chrome_portable_path}').VersionInfo.FileVersion"
                                        ps_out2 = _sp.check_output(
                                            ["powershell", "-NoProfile", "-Command", ps_cmd2],
                                            stderr=_sp.DEVNULL, creationflags=0x08000000, timeout=5
                                        ).decode().strip()
                                        detected_version = int(ps_out2.split('.')[0])
                                        print(f"[VIMEO] ✅ Chrome Portable version: {detected_version}")
                                    except Exception as ver_e2:
                                        print(f"[VIMEO] ⚠️ Không đọc được version portable: {ver_e2}")
                            else:
                                # Không có portable → dùng Chrome hệ thống → không set binary_location
                                # Và cũng không set version_main để UC tự detect
                                print(f"[VIMEO] ℹ️ Không có chrome_portable, dùng Chrome hệ thống")
                                detected_version = None  # Let UC auto-detect system Chrome

                            # ── STEP 4: Khởi động UC Chrome ──
                            uc_kwargs = dict(options=options, headless=headless, use_subprocess=True)
                            if detected_version:
                                uc_kwargs['version_main'] = detected_version
                            if driver_executable_path:
                                uc_kwargs['driver_executable_path'] = driver_executable_path

                            print(f"[VIMEO] 🚀 Launching UC Chrome (version_main={detected_version}, driver={driver_executable_path})")
                            self.driver = uc.Chrome(**uc_kwargs)
                            print(f"[VIMEO] ✅ UC Chrome launched OK")

                            
                            break  # Success
                        except Exception as e:
                             err_str = str(e)
                             print(f"[VIMEO] ❌ Init Driver Error (Attempt {attempt+1}): {err_str[:300]}")
                             if attempt < max_retries - 1:
                                 time.sleep(random.uniform(2, 4))
                                 continue
                             # Final attempt failed
                             if "session not created" in err_str or "version" in err_str.lower():
                                 print("[VIMEO] ❌ Chrome version mismatch! driver/chromedriver.exe không khớp với Chrome.")
                                 print("[VIMEO] 💡 Cần cập nhật driver/chromedriver.exe cho đúng version Chrome.")
                             raise e  # Re-raise so fill_registration_form catches it cleanly

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
            
            # CRITICAL: Validate driver was initialized
            if not self.driver:
                error_msg = "[VIMEO] ❌ CRITICAL: Driver initialization failed! Driver is None."
                print(error_msg)
                raise Exception(error_msg)
            
            print("[VIMEO] Browser initialized successfully.")
            if is_mobile:
                self.driver.set_window_size(390, 844)
            else:
                self.driver.set_window_size(1920, 1080)
            
            # Increase timeout for slow pages like Vimeo upload
            self.driver.set_page_load_timeout(180)  # 3 minutes instead of 60s

        except Exception as e:
            print(f"[VIMEO] Failed to init driver: {e}")
            self.driver = None  # Ensure driver is None on failure
            raise e

    # Class-level: lưu session cookies từ Selenium để reuse cho Pure API
    _shared_vimeo_cookies = None
    _shared_vimeo_xvt = None
    _proxy_list = []  # Danh sách proxy xoay
    _proxy_index = 0

    @classmethod
    def fetch_free_proxies(cls):
        """Lấy danh sách proxy miễn phí từ các nguồn public"""
        proxies = []
        sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        ]
        for url in sources:
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    lines = r.text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if ':' in line and len(line) < 30:
                            proxies.append(line)
                if len(proxies) >= 50:
                    break
            except: pass
        cls._proxy_list = list(set(proxies))
        print(f"[PROXY] 📋 Loaded {len(cls._proxy_list)} free proxies")
        return cls._proxy_list

    @classmethod
    def get_next_proxy(cls):
        """Lấy proxy tiếp theo trong danh sách (round-robin)"""
        if not cls._proxy_list:
            cls.fetch_free_proxies()
        if not cls._proxy_list:
            return None
        proxy = cls._proxy_list[cls._proxy_index % len(cls._proxy_list)]
        cls._proxy_index += 1
        return proxy

    @classmethod
    def test_proxy(cls, proxy, timeout=5):
        """Test proxy có hoạt động không"""
        try:
            r = requests.get(
                "https://api64.ipify.org?format=json",
                proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                timeout=timeout
            )
            if r.status_code == 200:
                ip = r.json().get("ip", "")
                return True, ip
        except: pass
        return False, None

    def register_pure_api(self, name, email, password, log_callback=None):
        """
        Đăng ký Vimeo KHÔNG cần browser - thuần requests.
        Reuse cookies/xvt từ Selenium session trước nếu có.
        Target: ~3s/account.
        """
        import re
        try:
            session = requests.Session()
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Safari/537.36"
            session.headers.update({
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            })

            xvt = None

            # ── Nếu chưa có shared cookies → skip, để Selenium chạy lần đầu ──
            if not VimeoHelper._shared_vimeo_cookies:
                return False, "NO_XVT_NEED_SELENIUM"

            # ── Reuse cookies từ Selenium session trước (đã pass Cloudflare) ──
            for c in VimeoHelper._shared_vimeo_cookies:
                session.cookies.set(c.get('name',''), c.get('value',''), domain=c.get('domain','.vimeo.com'))
            xvt = VimeoHelper._shared_vimeo_xvt
            print(f"[PURE-API] ♻️ Reuse {len(VimeoHelper._shared_vimeo_cookies)} cookies | xvt: {'✅ ' + xvt[:15] if xvt else '❌'}")

            if not xvt:
                return False, "NO_XVT_NEED_SELENIUM"

            # Parse tất cả hidden fields từ form
            hidden_fields = {}
            for m_hf in re.finditer(r'<input[^>]+type=["\']hidden["\'][^>]*>', r.text, re.IGNORECASE):
                tag = m_hf.group(0)
                name_m = re.search(r'name=["\']([^"\']+)["\']', tag)
                val_m = re.search(r'value=["\']([^"\']*)["\']', tag)
                if name_m and val_m:
                    hidden_fields[name_m.group(1)] = val_m.group(1)
            if hidden_fields:
                print(f"[PURE-API] Hidden fields: {list(hidden_fields.keys())}")

            # ── Step 2: POST form đăng ký ──
            form_data = {
                **hidden_fields,
                "action": "join",
                "display_name": name,
                "email": email,
                "password": password,
                "marketing_opt_in": "0",
            }
            if xvt:
                form_data["xvt"] = xvt

            post_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://vimeo.com/join",
                "Origin": "https://vimeo.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            if xvt:
                post_headers["X-Xvt"] = xvt

            if log_callback: log_callback("[PURE-API] 📤 Submit form...")
            r2 = session.post(
                "https://vimeo.com/join",
                data=form_data,
                headers=post_headers,
                timeout=15,
                allow_redirects=True,
            )
            print(f"[PURE-API] POST /join → {r2.status_code} | URL: {r2.url[:80]}")

            # Kiểm tra kết quả
            final_url = r2.url.lower()
            if "survey" in final_url or "onboarding" in final_url or "welcome" in final_url:
                if log_callback: log_callback(f"[PURE-API] ✅ Thành công! URL: {r2.url[:60]}")
                cookies_list = [{"name": c.name, "value": c.value, "domain": c.domain, "path": c.path} for c in session.cookies]
                return True, {"cookies": cookies_list, "url": r2.url}

            # Thử JSON API nếu form POST không work
            if r2.status_code in (200,) and "join" in final_url:
                # Thử endpoint JSON
                json_headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": "https://vimeo.com/join",
                    "Origin": "https://vimeo.com",
                }
                if xvt: json_headers["X-Xvt"] = xvt
                r3 = session.post(
                    "https://vimeo.com/api/v1/users",
                    json={"email": email, "password": password, "display_name": name, "marketing_opt_in": False},
                    headers=json_headers,
                    timeout=15,
                )
                print(f"[PURE-API] POST /api/v1/users → {r3.status_code}: {r3.text[:200]}")
                if r3.status_code in (200, 201):
                    try: data = r3.json()
                    except: data = {}
                    cookies_list = [{"name": c.name, "value": c.value, "domain": c.domain, "path": c.path} for c in session.cookies]
                    return True, {"cookies": cookies_list, "data": data}
                elif r3.status_code == 429:
                    return False, "RATE_LIMITED"
                elif r3.status_code == 403:
                    return False, "IP_BLOCKED"

            # Parse lỗi từ response
            if "already" in r2.text.lower() or "exist" in r2.text.lower():
                return False, "EMAIL_EXISTS"
            if "blocked" in r2.text.lower() or "spam" in r2.text.lower():
                return False, "IP_BLOCKED"

            return False, f"FAILED_{r2.status_code}_{r2.url[:50]}"

        except requests.exceptions.Timeout:
            return False, "TIMEOUT"
        except Exception as e:
            print(f"[PURE-API] ❌ {e}")
            return False, f"ERROR: {e}"

    def _inject_fingerprint_spoof(self):
        """
        Inject JS fingerprint spoofing qua CDP Page.addScriptToEvaluateOnNewDocument.
        Fake: canvas, WebGL, fonts, screen, timezone, hardware, plugins, battery, etc.
        """
        import random
        # Random các thông số phần cứng
        hw_concurrency = random.choice([2, 4, 6, 8, 12, 16])
        device_memory  = random.choice([2, 4, 8])
        screen_w       = random.choice([1366, 1440, 1536, 1920, 2560])
        screen_h       = random.choice([768, 900, 864, 1080, 1440])
        color_depth    = random.choice([24, 30])
        timezone_offset = random.choice([-480, -420, -360, -300, -240, 0, 60, 120, 330, 540])
        canvas_noise   = random.randint(1, 9)
        webgl_vendor   = random.choice([
            "Intel Inc.", "NVIDIA Corporation", "AMD", "Google Inc. (Intel)", "Google Inc. (NVIDIA)"
        ])
        webgl_renderer = random.choice([
            "Intel Iris OpenGL Engine",
            "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
            "Mesa DRI Intel(R) HD Graphics 520",
        ])

        script = f"""
(function() {{
    // ── 1. Navigator properties ──
    const overrides = {{
        hardwareConcurrency: {hw_concurrency},
        deviceMemory: {device_memory},
        platform: 'Win32',
        vendor: 'Google Inc.',
        appVersion: navigator.appVersion,
        language: 'en-US',
        languages: ['en-US', 'en'],
        maxTouchPoints: 0,
        cookieEnabled: true,
        doNotTrack: null,
    }};
    for (const [k, v] of Object.entries(overrides)) {{
        try {{
            Object.defineProperty(navigator, k, {{ get: () => v, configurable: true }});
        }} catch(e) {{}}
    }}

    // ── 2. Screen ──
    try {{
        Object.defineProperty(window, 'screen', {{ value: {{
            width: {screen_w}, height: {screen_h},
            availWidth: {screen_w}, availHeight: {screen_h} - 40,
            colorDepth: {color_depth}, pixelDepth: {color_depth},
        }}, configurable: true }});
    }} catch(e) {{}}

    // ── 3. Timezone ──
    try {{
        const origDateTimeFormat = Intl.DateTimeFormat;
        const tzOffset = {timezone_offset};
        const tzName = tzOffset === 0 ? 'UTC' : 'America/New_York';
        window.Intl.DateTimeFormat = function(locale, opts) {{
            opts = opts || {{}};
            if (!opts.timeZone) opts.timeZone = tzName;
            return new origDateTimeFormat(locale, opts);
        }};
        Object.defineProperty(Date.prototype, 'getTimezoneOffset', {{
            value: () => tzOffset, configurable: true
        }});
    }} catch(e) {{}}

    // ── 4. Canvas fingerprint noise ──
    try {{
        const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {{
            const ctx = this.getContext('2d');
            if (ctx) {{
                const imageData = ctx.getImageData(0, 0, this.width || 1, this.height || 1);
                for (let i = 0; i < imageData.data.length; i += 100) {{
                    imageData.data[i] = (imageData.data[i] + {canvas_noise}) & 0xFF;
                }}
                ctx.putImageData(imageData, 0, 0);
            }}
            return origToDataURL.apply(this, arguments);
        }};
        const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {{
            const data = origGetImageData.apply(this, arguments);
            for (let i = 0; i < data.data.length; i += 100) {{
                data.data[i] = (data.data[i] + {canvas_noise}) & 0xFF;
            }}
            return data;
        }};
    }} catch(e) {{}}

    // ── 5. WebGL vendor/renderer ──
    try {{
        const origGetParam = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{webgl_vendor}';   // UNMASKED_VENDOR_WEBGL
            if (param === 37446) return '{webgl_renderer}'; // UNMASKED_RENDERER_WEBGL
            return origGetParam.apply(this, arguments);
        }};
        const origGetParam2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{webgl_vendor}';
            if (param === 37446) return '{webgl_renderer}';
            return origGetParam2.apply(this, arguments);
        }};
    }} catch(e) {{}}

    // ── 6. AudioContext fingerprint noise ──
    try {{
        const origCreateOscillator = AudioContext.prototype.createOscillator;
        AudioContext.prototype.createOscillator = function() {{
            const osc = origCreateOscillator.apply(this, arguments);
            const origConnect = osc.connect.bind(osc);
            osc.connect = function(dest) {{
                return origConnect(dest);
            }};
            return osc;
        }};
        const origGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function(channel) {{
            const data = origGetChannelData.apply(this, arguments);
            for (let i = 0; i < data.length; i += 100) {{
                data[i] += Math.random() * 0.0001 - 0.00005;
            }}
            return data;
        }};
    }} catch(e) {{}}

    // ── 7. Plugins (fake non-empty) ──
    try {{
        Object.defineProperty(navigator, 'plugins', {{
            get: () => {{
                const arr = [
                    {{ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1 }},
                    {{ name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '', length: 1 }},
                    {{ name: 'Native Client', filename: 'internal-nacl-plugin', description: '', length: 2 }},
                ];
                arr.item = (i) => arr[i];
                arr.namedItem = (n) => arr.find(p => p.name === n);
                arr.refresh = () => {{}};
                return arr;
            }},
            configurable: true
        }});
    }} catch(e) {{}}

    // ── 8. Battery API (fake) ──
    try {{
        navigator.getBattery = () => Promise.resolve({{
            charging: true, chargingTime: 0,
            dischargingTime: Infinity, level: 0.98,
            addEventListener: () => {{}}, removeEventListener: () => {{}}
        }});
    }} catch(e) {{}}

    // ── 9. WebRTC IP leak prevention ──
    try {{
        const origRTCPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection;
        if (origRTCPeerConnection) {{
            window.RTCPeerConnection = function(config) {{
                if (config && config.iceServers) config.iceServers = [];
                return new origRTCPeerConnection(config);
            }};
        }}
    }} catch(e) {{}}

    // ── 10. Remove webdriver flag ──
    try {{
        Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined, configurable: true }});
        delete navigator.__proto__.webdriver;
    }} catch(e) {{}}

    // ── 11. Tắt Global Privacy Control (GPC) - Brave bật mặc định, Vimeo detect ──
    try {{
        Object.defineProperty(navigator, 'globalPrivacyControl', {{ get: () => undefined, configurable: true }});
    }} catch(e) {{}}
    // Tắt doNotTrack
    try {{
        Object.defineProperty(navigator, 'doNotTrack', {{ get: () => null, configurable: true }});
    }} catch(e) {{}}

    console.log('[FP] Fingerprint spoofing active: hw={hw_concurrency} mem={device_memory}GB screen={screen_w}x{screen_h} webgl={webgl_vendor}');
}})();
"""
        try:
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
            print(f"[FP] ✅ Fingerprint spoof injected: hw={hw_concurrency}core/{device_memory}GB screen={screen_w}x{screen_h} WebGL={webgl_vendor[:20]}")
        except Exception as e:
            print(f"[FP] ⚠️ Không inject được fingerprint: {e}")

    def _save_account_from_api(self, email, password, name, api_data, log_callback=None):
        """Lưu account đăng ký thành công qua API"""
        try:
            with open("vimeo_accounts.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}|{password}|{name}\n")
            print(f"[API-REG] ✅ Đã lưu account: {email}")
            if log_callback: log_callback(f"[SAVE] ✅ Đã lưu: {email}|{password}")

            # Lưu cookies nếu có
            if isinstance(api_data, dict) and api_data.get("cookies"):
                cookie_data = {"email": email, "cookies": api_data["cookies"]}
                with open("vimeo_cookies.txt", "a", encoding="utf-8") as f:
                    f.write(json.dumps(cookie_data) + "\n")
                print(f"[API-REG] ✅ Đã lưu cookies cho: {email}")
        except Exception as e:
            print(f"[API-REG] ⚠️ Lỗi lưu account: {e}")

    def register_via_api(self, name, email, password, log_callback=None, xvt=None, browser_cookies=None):
        """
        Đăng ký Vimeo qua API với CSRF token + cookies từ browser đã pass Cloudflare.
        Flow: check email → register
        """
        try:
            session = requests.Session()
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Safari/537.36"
            session.headers.update({
                "User-Agent": ua,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Origin": "https://vimeo.com",
                "Referer": "https://vimeo.com/join",
                "X-Requested-With": "XMLHttpRequest",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
            })

            if not browser_cookies:
                return False, "NO_BROWSER_COOKIES"
            if not xvt:
                return False, "NO_XVT_TOKEN"

            # Inject cookies từ browser
            for name_c, val in browser_cookies.items():
                session.cookies.set(name_c, val, domain=".vimeo.com")
            print(f"[API-REG] 🍪 {len(browser_cookies)} cookies | 🔑 xvt: {xvt[:20]}...")

            base_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-Xvt": xvt,
            }

            # ── Bước 1: Check email (Vimeo 2-step form) ──
            if log_callback: log_callback("[API-REG] � Step 1: Check email...")
            try:
                r1 = session.post(
                    "https://vimeo.com/api/v1/users/check_email",
                    json={"email": email},
                    headers=base_headers, timeout=15
                )
                print(f"[API-REG] check_email → {r1.status_code}: {r1.text[:150]}")
                if r1.status_code == 200:
                    data1 = r1.json()
                    # Nếu email đã tồn tại
                    if data1.get("exists") or data1.get("registered"):
                        return False, "EMAIL_EXISTS"
                    # Lấy token bổ sung nếu có
                    extra_token = data1.get("token") or data1.get("xvt") or data1.get("csrf_token")
                    if extra_token:
                        xvt = extra_token
                        base_headers["X-Xvt"] = xvt
                        print(f"[API-REG] 🔑 Got new token from check_email: {xvt[:20]}...")
            except Exception as e1:
                print(f"[API-REG] check_email error: {e1}")

            # ── Bước 2: Register ──
            if log_callback: log_callback("[API-REG] 📤 Step 2: Register...")
            payload = {
                "email": email,
                "password": password,
                "display_name": name,
                "marketing_opt_in": False,
                "token_type": "email",
            }
            resp = session.post(
                "https://vimeo.com/api/v1/users",
                json=payload,
                headers=base_headers,
                timeout=30,
            )
            print(f"[API-REG] register → {resp.status_code}: {resp.text[:300]}")

            if resp.status_code in (200, 201):
                try: data = resp.json()
                except: data = {}
                user_id = data.get("id") or data.get("user_id") or data.get("uri", "").split("/")[-1]
                if log_callback: log_callback(f"[API-REG] ✅ Thành công! ID: {user_id}")
                cookies_list = [{"name": c.name, "value": c.value, "domain": c.domain, "path": c.path} for c in session.cookies]
                return True, {"user_id": user_id, "cookies": cookies_list, "data": data}
            elif resp.status_code == 429:
                return False, "RATE_LIMITED"
            elif resp.status_code == 403:
                return False, "IP_BLOCKED"
            elif resp.status_code in (401, 400):
                try:
                    msg = resp.json().get("display_message") or resp.json().get("error") or resp.text[:100]
                    print(f"[API-REG] ⚠️ {resp.status_code}: {msg}")
                except: pass
                return False, f"TOKEN_INVALID_{resp.status_code}"
            else:
                return False, f"HTTP_{resp.status_code}"

        except requests.exceptions.Timeout:
            return False, "API_TIMEOUT"
        except Exception as e:
            print(f"[API-REG] ❌ {e}")
            return False, f"API_ERROR: {e}"

    def _intercept_and_replay_registration(self, name, email, password, log_callback=None):
        """
        Dùng CDP để intercept request đăng ký từ browser,
        sau đó replay cho các account tiếp theo.
        Lưu captured request vào self._captured_reg_request
        """
        if not self.driver:
            return False, "NO_DRIVER"
        try:
            # Enable CDP Network
            self.driver.execute_cdp_cmd("Network.enable", {})
            captured = {"found": False, "request_id": None, "headers": {}, "body": ""}

            # Inject JS để intercept fetch/XHR
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                (function() {
                    const origFetch = window.fetch;
                    window.fetch = function(url, opts) {
                        if (url && url.toString().includes('/api/v1/users') && opts && opts.method === 'POST') {
                            window.__vimeo_reg_intercepted__ = {
                                url: url.toString(),
                                headers: opts.headers || {},
                                body: opts.body || ''
                            };
                        }
                        return origFetch.apply(this, arguments);
                    };
                    const origXHROpen = XMLHttpRequest.prototype.open;
                    const origXHRSend = XMLHttpRequest.prototype.send;
                    XMLHttpRequest.prototype.open = function(method, url) {
                        this._url = url; this._method = method;
                        return origXHROpen.apply(this, arguments);
                    };
                    XMLHttpRequest.prototype.send = function(body) {
                        if (this._url && this._url.includes('/api/v1/users') && this._method === 'POST') {
                            window.__vimeo_reg_intercepted__ = {
                                url: this._url, headers: {}, body: body || ''
                            };
                        }
                        return origXHRSend.apply(this, arguments);
                    };
                })();
                """
            })
            if log_callback: log_callback("[CDP] 🎣 Đã cài interceptor, đang chờ form submit...")
            return True, "INTERCEPTOR_READY"
        except Exception as e:
            print(f"[CDP] ❌ Lỗi cài interceptor: {e}")
            return False, str(e)

    def _get_intercepted_request(self):
        """Lấy request đã bị intercept từ browser JS"""
        try:
            data = self.driver.execute_script("return window.__vimeo_reg_intercepted__ || null")
            return data
        except:
            return None

    def fill_registration_form(self, name, email, password, log_callback=None, browser_type='brave'):
        """
        Open Vimeo Join page and fill the form.
        """
        if not self.driver:
            ok = self.init_driver(headless=True, browser_type=browser_type)
            if not ok or not self.driver:
                err_msg = "Không thể khởi động Chrome! Kiểm tra chromedriver.exe và chrome_portable."
                if log_callback: log_callback(f"[ERROR] {err_msg}")
                return False, f"DRIVER_INIT_FAILED: {err_msg}"

        # --- API sẽ được gọi SAU KHI browser pass Cloudflare (lấy CSRF từ browser) ---
        api_result = {"success": False, "data": None}

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

            # --- WARM-UP NAVIGATION STRATEGY ---
            # Cài CDP Network listener + JS interceptor TRƯỚC khi navigate
            try:
                # Enable CDP Network để bắt tất cả request/response
                self.driver.execute_cdp_cmd("Network.enable", {})
                self._cdp_requests = {}  # lưu requestId → {url, method, headers, body}
                self._cdp_responses = {}  # lưu requestId → {status, headers, body}

                # JS interceptor: bắt fetch/XHR + form submit, log tất cả Vimeo API calls
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                    (function() {
                        window.__vimeo_api_log__ = [];
                        window.__vimeo_reg_intercepted__ = null;
                        window.__vimeo_xvt__ = null;
                        window.__vimeo_form_data__ = null;

                        function logReq(url, method, headers, body) {
                            const entry = { url, method, headers: headers || {}, body: body || '', ts: Date.now() };
                            window.__vimeo_api_log__.push(entry);
                            const h = headers || {};
                            const xvt = h['X-Xvt'] || h['x-xvt'] || h['X-CSRF-Token'] || h['x-csrf-token'];
                            if (xvt) { window.__vimeo_xvt__ = xvt; }
                            if (url && url.includes('vimeo.com') && method === 'POST') {
                                window.__vimeo_reg_intercepted__ = entry;
                            }
                        }

                        // Intercept fetch
                        const origFetch = window.fetch;
                        window.fetch = function(url, opts) {
                            const u = (url || '').toString();
                            const m = (opts && opts.method || 'GET').toUpperCase();
                            const h = (opts && opts.headers) || {};
                            const b = (opts && opts.body) || '';
                            if (u.includes('vimeo.com')) {
                                logReq(u, m, h, b);
                                console.log('[FETCH]', m, u.replace('https://vimeo.com',''), typeof b === 'string' ? b.substring(0,150) : '');
                            }
                            const p = origFetch.apply(this, arguments);
                            if (u.includes('vimeo.com')) {
                                p.then(r => r.clone().text().then(text => {
                                    const last = window.__vimeo_api_log__.find(e => e.url === u && e.method === m);
                                    if (last) { last.response_status = r.status; last.response_body = text.substring(0,500); }
                                    console.log('[FETCH-RESP]', r.status, u.replace('https://vimeo.com',''), text.substring(0,200));
                                    if (m === 'POST') window.__vimeo_reg_response__ = { status: r.status, body: text, url: u };
                                })).catch(()=>{});
                            }
                            return p;
                        };

                        // Intercept XHR
                        const origOpen = XMLHttpRequest.prototype.open;
                        const origSend = XMLHttpRequest.prototype.send;
                        const origSetHdr = XMLHttpRequest.prototype.setRequestHeader;
                        XMLHttpRequest.prototype.open = function(m, u) {
                            this._u = u; this._m = m; this._h = {};
                            return origOpen.apply(this, arguments);
                        };
                        XMLHttpRequest.prototype.setRequestHeader = function(k, v) {
                            if (this._h) this._h[k] = v;
                            return origSetHdr.apply(this, arguments);
                        };
                        XMLHttpRequest.prototype.send = function(body) {
                            if (this._u && this._u.includes('vimeo.com')) {
                                logReq(this._u, this._m || 'GET', this._h, body);
                                console.log('[XHR]', this._m, this._u.replace('https://vimeo.com',''), typeof body === 'string' ? body.substring(0,150) : '');
                                this.addEventListener('load', function() {
                                    console.log('[XHR-RESP]', this.status, this._u, this.responseText.substring(0,200));
                                    if (this._m === 'POST') window.__vimeo_reg_response__ = { status: this.status, body: this.responseText, url: this._u };
                                }.bind(this));
                            }
                            return origSend.apply(this, arguments);
                        };

                        // Intercept form submit (Vimeo dùng traditional form POST)
                        const origSubmit = HTMLFormElement.prototype.submit;
                        HTMLFormElement.prototype.submit = function() {
                            const fd = {};
                            for (const el of this.elements) {
                                if (el.name) fd[el.name] = el.value;
                            }
                            window.__vimeo_form_data__ = {
                                action: this.action,
                                method: this.method,
                                data: fd
                            };
                            console.log('[FORM-SUBMIT]', this.method, this.action, JSON.stringify(fd).substring(0,200));
                            return origSubmit.apply(this, arguments);
                        };
                        // Bắt cả submit event
                        document.addEventListener('submit', function(e) {
                            const form = e.target;
                            const fd = {};
                            for (const el of form.elements) {
                                if (el.name) fd[el.name] = el.value;
                            }
                            window.__vimeo_form_data__ = {
                                action: form.action,
                                method: form.method,
                                data: fd
                            };
                            console.log('[FORM-EVENT]', form.method, form.action, JSON.stringify(fd).substring(0,200));
                        }, true);
                    })();
                    """
                })
                print("[CDP] 🎣 Full API interceptor ready - logging all Vimeo API calls")
            except Exception as cdp_e:
                print(f"[CDP] ⚠️ Không cài được interceptor: {cdp_e}")

            print("[VIMEO] Navigating to Join page directly...")
            # Tắt Brave Shields cho vimeo.com trước khi navigate
            if browser_type == 'brave':
                try:
                    # Dùng CDP để tắt shields qua brave://settings/shields
                    self.driver.get("chrome://settings/")
                    time.sleep(0.5)
                    # Inject JS tắt shields default
                    self.driver.execute_script("""
                        if (window.chrome && window.chrome.settingsPrivate) {
                            chrome.settingsPrivate.setPref('brave.shields.default_shields_up', false);
                        }
                    """)
                    time.sleep(0.3)
                except: pass
            self.driver.get("https://vimeo.com/join")
            # Chờ React render form input (eager đã có DOM, chờ thêm JS render)
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[type='text']"))
                )
                print("[VIMEO] ✅ Form input detected after page load.")
            except Exception:
                # Nếu không thấy input, chờ thêm 3s cho React
                time.sleep(3)

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
                    form_inputs = [i for i in inputs if i.is_displayed()]
                    if len(form_inputs) >= 1:
                        print("[VIMEO] ✅ Cloudflare passed! Form detected.")
                        # Cài interceptor lần 2 (backup, lần đầu đã cài trước navigate)
                        self._intercept_and_replay_registration(name, email, password, log_callback)
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
                    if unknown_state_count % 5 == 0:
                        print(f"[VIMEO] ❓ State Unknown (No Form, No Captcha) - Count {unknown_state_count}")
                        print(f"   [URL] {self.driver.current_url}")
                        print(f"   [Title] {self.driver.title}")
                        try:
                            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                            print(f"   [DEBUG] Total inputs (incl hidden): {len(all_inputs)}")
                            self.driver.execute_script("window.scrollTo(0, 300)")
                        except: pass
                    # Nếu 0 inputs sau 15s → refresh để trigger React render
                    if unknown_state_count == 15:
                        try:
                            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                            if len(all_inputs) == 0:
                                print("[VIMEO] 🔄 0 inputs sau 15s, refresh để trigger React...")
                                self.driver.refresh()
                                time.sleep(3)
                                unknown_state_count = 0
                        except: pass

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
                            print("[VIMEO] No password field yet. Submitting email step...")
                            # Dùng Enter trên email field - an toàn nhất, không click nhầm OAuth
                            try:
                                visible_emails[0].send_keys(Keys.RETURN)
                                print("[VIMEO] Sent ENTER on email field.")
                            except:
                                # Fallback: tìm Continue button, lọc kỹ OAuth
                                continue_btns = self.driver.find_elements(By.XPATH,
                                    "//button[not(contains(., 'Google')) and not(contains(., 'Facebook')) and not(contains(., 'Apple')) and not(contains(@class,'google')) and not(contains(@class,'facebook')) and not(contains(@class,'social'))]"
                                    "[contains(., 'Continue') or contains(., 'Next') or contains(., 'Tiếp') or contains(., 'email')]"
                                )
                                visible_cns = [b for b in continue_btns if b.is_displayed()]
                                if visible_cns:
                                    visible_cns[0].click()
                                    print(f"[VIMEO] Clicked Continue: '{visible_cns[0].text}'")
                    except:
                        pass
                    try:
                        print("[VIMEO] Waiting for password field to appear...")
                        WebDriverWait(self.driver, 10).until(  # tăng từ 5s lên 10s
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                        )
                        time.sleep(0.5)
                        # --- Thử API ngay sau khi password field xuất hiện ---
                        # Lúc này Vimeo đã gọi API check email → xvt đã được interceptor bắt
                        try:
                            import re as _re
                            xvt = self.driver.execute_script("return window.__vimeo_xvt__ || null")
                            if not xvt:
                                # Thử tìm trong cookies
                                for c in self.driver.get_cookies():
                                    if 'xvt' in c.get('name','').lower():
                                        xvt = c['value']; break
                            browser_cookies = {c['name']: c['value'] for c in self.driver.get_cookies()}
                            print(f"[API-REG] 🔑 xvt sau email step: {'✅ ' + xvt[:20] if xvt else '❌ chưa có'} | 🍪 {len(browser_cookies)}")
                            if xvt:
                                if log_callback: log_callback("[API-REG] ⚡ Có xvt! Thử submit qua API...")
                                api_ok, api_data = self.register_via_api(
                                    name, email, password, log_callback,
                                    xvt=xvt, browser_cookies=browser_cookies
                                )
                                if api_ok:
                                    if log_callback: log_callback("[API-REG] ✅ API thành công!")
                                    self._save_account_from_api(email, password, name, api_data, log_callback)
                                    return True, "SUCCESS_VIA_API"
                                else:
                                    print(f"[API-REG] ⚠️ API thất bại ({api_data}), tiếp tục Selenium...")
                        except Exception as api_e:
                            print(f"[API-REG] ⚠️ {api_e}")
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
                            print(f"[VIMEO] Field #{idx+1}: name='{v.get_attribute('name')}', placeholder='{v.get_attribute('placeholder')}', type='{v.get_attribute('type')}'")
                        except:
                            pass
                    # Debug: dump tất cả visible inputs
                    try:
                        all_vis = self.driver.find_elements(By.CSS_SELECTOR, "input:not([type='hidden'])")
                        print(f"[VIMEO] All visible inputs ({len(all_vis)}):")
                        for inp in all_vis:
                            try:
                                if inp.is_displayed():
                                    print(f"  - type={inp.get_attribute('type')} name={inp.get_attribute('name')} placeholder={inp.get_attribute('placeholder')}")
                            except: pass
                    except: pass

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
                        print("[VIMEO] 1 password field - fill + JS confirm")
                        p_input = unique_pass[0]
                        try:
                            p_input.click()
                            p_input.clear()
                            p_input.send_keys(password)
                            if log_callback: log_callback("[FORM] ✅ Đã điền Mật khẩu.")
                            time.sleep(0.5)
                            # Fill tất cả password fields bằng JS với React-compatible events
                            confirm_filled = self.driver.execute_script("""
                                var pwd = arguments[0];
                                var inputs = document.querySelectorAll('input[type="password"]');
                                var filled = 0;
                                inputs.forEach(function(inp) {
                                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                        window.HTMLInputElement.prototype, 'value').set;
                                    nativeInputValueSetter.call(inp, pwd);
                                    inp.dispatchEvent(new Event('input', {bubbles:true}));
                                    inp.dispatchEvent(new Event('change', {bubbles:true}));
                                    inp.dispatchEvent(new Event('blur', {bubbles:true}));
                                    filled++;
                                });
                                return filled;
                            """, password)
                            print(f"[VIMEO] JS React fill: {confirm_filled} password fields")
                        except Exception as e:
                            print(f"[VIMEO] Password fill failed: {e}")
                    else:
                        print("[VIMEO] Warning: No password field found!")
            except Exception as e:
                print(f"[VIMEO] Password fill error: {e}")

            # --- 4. CLICK JOIN / SUBMIT ---
            print("[VIMEO] Clicking Final 'Join' button...")
            time.sleep(0.3)
            try:
                join_btns = self.driver.find_elements(By.XPATH, "//button[(contains(., 'Join') or contains(., 'Sign up') or contains(., 'Đăng ký') or contains(., 'Hoàn tất')) and not(contains(., 'Google')) and not(contains(., 'Facebook')) and not(contains(., 'Apple'))]")
                visible_btns = [b for b in join_btns if b.is_displayed()]
                if visible_btns:
                    visible_btns[0].click()
                    print("[VIMEO] Clicked Join button (Text Match)!")
                else:
                    # Lọc kỹ submit button - không được là Google/Facebook/Apple OAuth
                    submits = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                    safe_submits = []
                    for s in submits:
                        if not s.is_displayed(): continue
                        txt = s.text.lower()
                        cls = (s.get_attribute('class') or '').lower()
                        href = (s.get_attribute('data-href') or s.get_attribute('onclick') or '').lower()
                        # Bỏ qua nếu liên quan Google/Facebook/Apple/OAuth
                        if any(k in txt for k in ['google', 'facebook', 'apple', 'twitter']): continue
                        if any(k in cls for k in ['google', 'facebook', 'apple', 'oauth', 'social']): continue
                        if 'google' in href or 'facebook' in href: continue
                        safe_submits.append(s)
                        print(f"[VIMEO] Safe submit candidate: '{s.text}' class='{cls[:40]}'")
                    if safe_submits:
                        safe_submits[-1].click()
                        print(f"[VIMEO] Clicked safe Submit: '{safe_submits[-1].text}'")
                    else:
                        # Last resort: Enter trên password field
                        pass_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                        visible_pass_f = [e for e in pass_inputs if e.is_displayed()]
                        if visible_pass_f:
                            visible_pass_f[-1].send_keys(Keys.ENTER)
                        pass_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                        visible_pass_f = [e for e in pass_inputs if e.is_displayed()]
                        if visible_pass_f:
                            visible_pass_f[-1].send_keys(Keys.ENTER)
                            print("[VIMEO] Sent ENTER key to submit.")
                    
                # Wait for page to process + bắt intercepted request
                time.sleep(1)
                try:
                    intercepted = self._get_intercepted_request()
                    if intercepted:
                        self._last_reg_request = intercepted
                        print(f"[CDP] 🎣 Captured registration request! URL: {intercepted.get('url','')[:60]}")
                        if log_callback: log_callback("[CDP] 🎣 Đã bắt được request đăng ký!")
                    # Log form data (traditional form submit)
                    form_data = self.driver.execute_script("return window.__vimeo_form_data__ || null")
                    if form_data:
                        print(f"[CDP] 📋 FORM SUBMIT: {form_data.get('method','?').upper()} {form_data.get('action','?')}")
                        print(f"[CDP] 📋 FORM DATA: {str(form_data.get('data',{}))[:300]}")
                        self._last_form_data = form_data
                    # In API log
                    api_log = self.driver.execute_script("return window.__vimeo_api_log__ || []")
                    if api_log:
                        print(f"[CDP] 📋 Tổng {len(api_log)} API calls:")
                        for entry in api_log[-10:]:
                            status = entry.get('response_status', '?')
                            body_preview = (entry.get('response_body') or '')[:80]
                            print(f"  [{status}] {entry.get('method','?')} {entry.get('url','')[:80]}")
                            if body_preview: print(f"       ↳ {body_preview}")
                    xvt_now = self.driver.execute_script("return window.__vimeo_xvt__ || null")
                    if xvt_now:
                        print(f"[CDP] � xvt: {xvt_now[:40]}...")
                        self._last_xvt = xvt_now
                    reg_resp = self.driver.execute_script("return window.__vimeo_reg_response__ || null")
                    if reg_resp:
                        print(f"[CDP] 📨 Reg [{reg_resp.get('status')}] {reg_resp.get('url','')[:60]}: {str(reg_resp.get('body',''))[:200]}")
                except Exception as cdp_e:
                    print(f"[CDP] ⚠️ {cdp_e}")
                time.sleep(1)
                
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
                        # survey/join, survey/*, onboarding/* đều là SUCCESS
                        if "survey" in curr or "onboarding" in curr or "welcome" in curr:
                            print(f"[VIMEO] ✅ Registration completed! (Survey/Onboarding) URL: {curr}")
                            break
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
                        if "log_in" not in curr and "login" not in curr:
                            # Chỉ fail nếu vẫn đúng trang /join (không phải survey/join)
                            if curr.rstrip('/') == "https://vimeo.com/join":
                                pass  # vẫn trên trang join, chờ tiếp
                            elif any(pattern in curr for pattern in success_patterns) or "vimeo.com" in curr:
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
                
                # accounts.google.com là FAIL
                if "accounts.google.com" in curr_url:
                    print("[VIMEO] ❌ Bị redirect sang Google OAuth!")
                    return False, "WRONG_BUTTON_GOOGLE"

                # survey/join, onboarding → SUCCESS
                if "survey" in curr_url or "onboarding" in curr_url or "welcome" in curr_url:
                    print(f"[VIMEO] ✅ Success via survey/onboarding: {curr_url}")
                    # fall through to cookie check

                # Vẫn ở trang join → fail, nhưng log body để debug
                is_still_join = "vimeo.com/join" in curr_url and "survey" not in curr_url
                if is_still_join or "log_in" in curr_url:
                    try:
                        body_text = self.driver.find_element(By.TAG_NAME, "body").text
                        # Log 200 ký tự đầu để debug
                        print(f"[VIMEO] Body snippet: {body_text[:300]}")
                        body_lower = body_text.lower()
                        if any(k in body_lower for k in ["blocked", "restricted", "banned", "too many", "rate limit", "429"]):
                            return False, "IP_BLOCKED"
                        if any(k in body_lower for k in ["captcha", "verify", "robot", "human"]):
                            return False, "CAPTCHA_REQUIRED"
                        if any(k in body_lower for k in ["already", "exist", "registered", "taken"]):
                            return False, "EMAIL_EXISTS"
                        if any(k in body_lower for k in ["invalid", "incorrect"]):
                            print(f"[VIMEO] Form error detected")
                            return False, "FORM_ERROR"
                        if "password" in body_lower and ("confirm" in body_lower or "symbol" in body_lower or "number" in body_lower):
                            print(f"[VIMEO] Password validation error - form not submitted")
                            return False, "FORM_ERROR"
                    except: pass
                    return False, "TIMEOUT_JOIN_PAGE"
                
                # Check if we have valid session cookies (means registration succeeded)
                try:
                    cookies = self.driver.get_cookies()
                    vimeo_session = any(cookie.get('name') == 'vimeo' for cookie in cookies)
                    if vimeo_session:
                        print("[VIMEO] ✅ Valid session cookie found - Registration successful!")
                        
                        # Save account to vimeo_accounts.txt
                        with open("vimeo_accounts.txt", "a", encoding="utf-8") as f:
                            f.write(f"{email}|{password}|{name}\n")
                        
                        # Lưu cookies vào class variable để Pure API reuse
                        try:
                            xvt_saved = getattr(self, '_last_xvt', None)
                            VimeoHelper._shared_vimeo_cookies = cookies
                            VimeoHelper._shared_vimeo_xvt = xvt_saved
                            print(f"[VIMEO] ♻️ Shared {len(cookies)} cookies cho Pure API lần sau")
                        except: pass

                        # Save cookies to vimeo_cookies.txt
                        try:
                            cookie_data = {"email": email, "cookies": cookies}
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
            error_detail = str(e)[:200]  # Lấy 200 ký tự đầu của lỗi
            print(f"[VIMEO] ❌ Exception chi tiết: {error_detail}")
            if log_callback: log_callback(f"[ERROR] Chi tiết lỗi: {error_detail}")
            
            # Check for network/IP related errors
            if any(keyword in error_msg for keyword in ["network", "connection", "timeout", "refused"]):
                return False, "NETWORK_ERROR"
            elif any(keyword in error_msg for keyword in ["blocked", "restricted", "banned"]):
                return False, "IP_BLOCKED"
            elif any(keyword in error_msg for keyword in ["session", "driver", "chrome", "version"]):
                return False, f"DRIVER_ERROR: {str(e)[:100]}"
            else:
                return False, f"GENERAL_ERROR: {str(e)[:100]}"

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
                        print("[VIMEO] Smart thumbnail failed/skipped. Using screenshot fallback...")
                        filename = f"thumb_{video_id}_screen.png"
                        save_path = os.path.join(thumb_dir, filename)
                        
                        try:
                            # 0. Try to extract thumbnail URL from page source (Most Reliable)
                            print("[VIMEO] Searching for thumbnail URL in page source...")
                            try:
                                import re, urllib.request
                                page_source = self.driver.page_source
                                # Look for Vimeo thumbnail CDN links without catching small ones immediately
                                matches = re.findall(r'https://i\.vimeocdn\.com/video/[a-zA-Z0-9_\-]+(?=\?|\"|\'|\.)', page_source)
                                if matches:
                                    # Filter and get the clean base URL
                                    base_url = re.sub(r'_[a-zA-Z0-9x\-]+$', '', matches[0])
                                    urllib.request.urlretrieve(base_url, save_path)
                                    thumbnail_path = save_path
                                    print(f"[VIMEO] ✅ Downloaded official thumbnail URL: {base_url}")
                            except Exception as e:
                                print(f"[VIMEO] Getting thumbnail from source failed: {e}")

                            if not thumbnail_path:
                                # 1. Play video first to get a good frame (not black/logo)
                                print("[VIMEO] ▶️ Playing video to capture good frame...")
                                try:
                                    # Find and click play button
                                    play_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Play'], button[title*='Play'], .vp-play, [data-testid='play-button']")
                                    if play_buttons:
                                        play_buttons[0].click()
                                        print("[VIMEO] ▶️ Play button clicked")
                                    else:
                                        # Try keyboard shortcut
                                        self.driver.execute_script("document.querySelector('video')?.play() || document.querySelector('[data-testid=\"video-player\"]')?.click()")
                                        print("[VIMEO] ▶️ Play via script")
                                    
                                    # Wait 3-5 seconds for video to render a good frame
                                    print("[VIMEO] ⏳ Waiting 4 seconds for video to render...")
                                    time.sleep(4)
                                    
                                except Exception as play_err:
                                    print(f"[VIMEO] ⚠️ Could not play video: {play_err}, will capture current frame")
                                
                                # 2. Try to capture the video container element directly
                                print("[VIMEO] Attempting to capture player element...")
                                
                                # Try to hide UI elements first to get clean frame
                                try:
                                    self.driver.execute_script("""
                                        var uis = document.querySelectorAll('button, .vp-controls, .vp-title, .vp-telecine, .vp-sidedock, .vp-controls-wrapper, [class*="overlay"]');
                                        uis.forEach(function(el) { if(el) el.style.opacity = '0'; });
                                    """)
                                    time.sleep(0.5)
                                except: pass
                                
                                player_elems = self.driver.find_elements(By.CSS_SELECTOR, ".player-wrapper, [data-testid='video-player'], .vp-video-wrapper, .video-player, video")
                                if player_elems:
                                    # Find largest visible player
                                    best_elem = None
                                    max_area = 0
                                    for el in player_elems:
                                        if el.is_displayed():
                                            area = el.size['width'] * el.size['height']
                                            if area > max_area:
                                                max_area = area
                                                best_elem = el
                                    
                                    if best_elem and max_area > 10000:
                                        best_elem.screenshot(save_path)
                                        thumbnail_path = save_path
                                        print(f"[VIMEO] ✅ Captured clean video player element (after playing).")
                                    else:
                                        raise Exception("No valid player element found")
                                else:
                                    raise Exception("No player element found")

                        except Exception as screen_err:
                            print(f"[VIMEO] Player capture failed: {screen_err}. Using full page crop...")
                            # 2. Fallback to old full page screenshot + crop
                            try:
                                self.driver.save_screenshot(save_path)
                                self.crop_vimeo_ui(save_path)
                                thumbnail_path = save_path
                                print(f"[VIMEO] ✅ Full page screenshot (cropped): {os.path.basename(thumbnail_path)}")
                            except Exception as e2:
                                print(f"[VIMEO] Full screenshot failed: {e2}")
                        
                except Exception as e:
                    print(f"[VIMEO] ⚠️ Thumbnail generation failed: {e}")
                    thumbnail_path = None
                
                # FACEBOOK OPTIMIZATION: Optimize thumbnail for Facebook after generation
                if thumbnail_path and os.path.exists(thumbnail_path):
                    try:
                        print(f"[VIMEO] 🎨 Tối ưu hóa thumbnail cho Facebook...")
                        from model.facebook_thumbnail_optimizer import FacebookThumbnailOptimizer
                        
                        fb_optimizer = FacebookThumbnailOptimizer()
                        optimized_thumb = fb_optimizer.optimize_for_facebook(
                            thumbnail_path,
                            enhance=True  # Tăng độ nét, tương phản, màu sắc
                        )
                        
                        if optimized_thumb and os.path.exists(optimized_thumb):
                            # Replace original thumbnail with optimized version
                            import shutil
                            shutil.copy2(optimized_thumb, thumbnail_path)
                            print(f"[VIMEO] ✅ Thumbnail đã tối ưu cho Facebook (1200x630px, chất lượng cao)")
                            
                            # Clean up optimized file (we copied it to original path)
                            try:
                                os.remove(optimized_thumb)
                            except:
                                pass
                        else:
                            print(f"[VIMEO] ⚠️ Facebook optimization failed, using original thumbnail")
                    except Exception as opt_err:
                        print(f"[VIMEO] ⚠️ Could not optimize for Facebook: {opt_err}")
                        # Continue with original thumbnail

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
        """Extract best quality frame from video (Robust Unicode Support)"""
        temp_video_path = None
        try:
            import cv2
            import numpy as np
            import shutil
            import tempfile
            
            # 1. Handle Unicode Paths on Windows:
            # OpenCV often fails with non-ASCII paths. We copy to a temp ASCII file.
            if not os.path.exists(video_path):
                print(f"[VIMEO] ❌ Video file not found: {video_path}")
                return None

            # Create temp file with simple name
            fd, temp_video_path = tempfile.mkstemp(suffix=".mp4")
            os.close(fd)
            
            print(f"[VIMEO] 📥 Creating temp copy for processing: {os.path.basename(temp_video_path)}...")
            shutil.copy2(video_path, temp_video_path)
            
            # 2. Process with OpenCV
            cap = cv2.VideoCapture(temp_video_path)
            if not cap.isOpened():
                print("[VIMEO] ⚠️ OpenCV failed to open video.")
                if os.path.exists(temp_video_path): os.remove(temp_video_path)
                return None
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                # Stream or error, try reading a few frames
                total_frames = 100
                
            # Analyze middle section to avoid black intro/outro
            start_frame = int(total_frames * 0.2)
            end_frame = int(total_frames * 0.8)
            # IMPROVED: Check more frames for better quality (10 instead of 5)
            num_candidates = 10
            step = max(1, (end_frame - start_frame) // num_candidates)
            
            best_score = -1.0
            best_frame = None
            best_frame_idx = -1
            
            print(f"[VIMEO] 🎬 Analyzing {num_candidates} frames for best quality...")
            
            for i in range(num_candidates):
                frame_idx = start_frame + (i * step)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret: continue
                
                # Quality Score: Sharpness + Contrast
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur = cv2.Laplacian(gray, cv2.CV_64F).var()
                contrast = np.std(gray)
                
                # Penalize full black/white
                mean_val = np.mean(gray)
                penalty = 0.1 if (mean_val < 20 or mean_val > 235) else 1.0
                
                score = (blur * 0.6 + contrast * 0.4) * penalty
                
                if score > best_score:
                    best_score = score
                    best_frame = frame
                    best_frame_idx = frame_idx
            
            cap.release()
            
            if best_frame_idx >= 0:
                print(f"[VIMEO] ✅ Best frame: #{best_frame_idx} (score: {best_score:.2f})")
            
            # 3. Save result with MAXIMUM QUALITY
            if best_frame is not None:
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # CRITICAL: Save with MAXIMUM JPEG quality (100%)
                # cv2.imencode parameters: [quality_flag, quality_value]
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 100]  # 100 = maximum quality
                is_success, buffer = cv2.imencode(".jpg", best_frame, encode_params)
                
                if is_success:
                    with open(output_path, "wb") as f:
                        f.write(buffer)
                    
                    # Get file size for verification
                    file_size = len(buffer) / 1024  # KB
                    print(f"[VIMEO] ✅ Extracted HIGHEST QUALITY thumbnail from video")
                    print(f"[VIMEO]    Quality: 100% JPEG | Size: {file_size:.1f} KB")
                    
                    # Cleanup temp
                    if temp_video_path and os.path.exists(temp_video_path):
                        os.remove(temp_video_path)
                    return output_path
            
            if temp_video_path and os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            return None
            
        except ImportError:
            print("[VIMEO] ⚠️ OpenCV not installed (pip install opencv-python).")
            if temp_video_path and os.path.exists(temp_video_path):
                try: os.remove(temp_video_path)
                except: pass
            return None
        except Exception as e:
            print(f"[VIMEO] Smart thumbnail error: {e}")
            if temp_video_path and os.path.exists(temp_video_path):
                try: os.remove(temp_video_path)
                except: pass
            return None

    def login_interactive(self, email, password, browser_type='brave'):
        """
        Login and KEEP BROWSER OPEN for user interaction.
        This runs in a loop monitoring the window until user closes it.
        """
        try:
            print(f"[VIMEO] 🚀 Starting interactive login for: {email}")
            
            # 1. Start browser (VISIBLE MODE)
            self.init_driver(headless=False, browser_type=browser_type)
            
            # 2. Perform login
            self.driver.get("https://vimeo.com/log_in")
            time.sleep(2)
            
            # Check for email input
            try:
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
                email_input.clear()
                email_input.send_keys(email)
                email_input.send_keys(Keys.RETURN)
                print("[VIMEO] Entered email")
                time.sleep(2)
                
                # Check for password input
                pwd_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
                pwd_input.clear()
                pwd_input.send_keys(password)
                pwd_input.send_keys(Keys.RETURN)
                print("[VIMEO] Entered password")
                
                # Check for success (simple check)
                time.sleep(5)
                if "log_in" not in self.driver.current_url:
                    print(f"[VIMEO] ✅ Login successful for {email}")
                else:
                    print(f"[VIMEO] ⚠️ Login might have failed or needs CAPTCHA")
                    
            except Exception as e:
                print(f"[VIMEO] ❌ Login automation error: {e}")
                print(f"[VIMEO] Please login manually in the opened window.")
            
            # 3. KEEP ALIVE LOOP
            print(f"[VIMEO] 🛑 Browser is open. Close the window to end session.")
            while True:
                try:
                    # Check if window is still open
                    if not self.driver.window_handles:
                        break
                    time.sleep(1)
                except:
                    break
                    
            print(f"[VIMEO] Session ended for {email}")
            
        except Exception as e:
            print(f"[VIMEO] Error in interactive session: {e}")
        finally:
            self.close()

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None