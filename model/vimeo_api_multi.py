"""
Vimeo Account Creator
- Cách 3: Fresh browser context (xóa hoàn toàn fingerprint)
- Cách 4: Email tạm từ Guerrillamail API (không cần đăng ký)
- Proxy tùy chọn để đổi IP
"""

import os
import re
import json
import time
import random
import string
from typing import Optional, Dict, List


# ─────────────────────────────────────────────
#  Email tạm – Guerrillamail public API
# ─────────────────────────────────────────────
class TempEmailService:
    """Lấy email tạm miễn phí từ Guerrillamail (không cần API key)."""

    BASE = "https://www.guerrillamail.com/ajax.php"

    def __init__(self):
        import requests
        self.sess = requests.Session()
        self.sess.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        self.sid_token = None
        self.email_address = None

    def get_email(self) -> str:
        """Lấy địa chỉ email tạm mới."""
        r = self.sess.get(self.BASE, params={"f": "get_email_address"}, timeout=10)
        data = r.json()
        self.sid_token = data.get("sid_token")
        self.email_address = data.get("email_addr")
        print(f"[TEMP-EMAIL] Địa chỉ: {self.email_address}")
        return self.email_address

    def wait_for_confirm_link(self, timeout: int = 120) -> Optional[str]:
        """Chờ email xác nhận từ Vimeo, trả về link confirm."""
        print(f"[TEMP-EMAIL] Đang chờ email từ Vimeo (tối đa {timeout}s)...")
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                r = self.sess.get(
                    self.BASE,
                    params={"f": "get_email_list", "offset": 0, "sid_token": self.sid_token},
                    timeout=10,
                )
                emails = r.json().get("list", [])
                if emails:
                    mail_id = emails[0].get("mail_id")
                    r2 = self.sess.get(
                        self.BASE,
                        params={"f": "fetch_email", "email_id": mail_id, "sid_token": self.sid_token},
                        timeout=10,
                    )
                    body = r2.json().get("mail_body", "")
                    # Tìm link vimeo trong body
                    links = re.findall(r'https?://[^\s"<>]+vimeo[^\s"<>]+', body)
                    if links:
                        print(f"[TEMP-EMAIL] Link xác nhận tìm thấy!")
                        return links[0]
            except Exception as e:
                print(f"[TEMP-EMAIL] Lỗi check inbox: {e}")
            time.sleep(6)
        print("[TEMP-EMAIL] Hết thời gian chờ email.")
        return None


# ─────────────────────────────────────────────
#  Tạo tài khoản Vimeo
# ─────────────────────────────────────────────
class VimeoAccountCreator:
    """
    Tự động tạo tài khoản Vimeo.
    - email_service: TempEmailService (Guerrillamail)
    - Browser fingerprint mới hoàn toàn mỗi lần
    - Proxy tùy chọn
    """

    ACCOUNTS_FILE = "vimeo_accounts.json"

    FIRST_NAMES = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard",
        "Emily", "Sarah", "Jessica", "Jennifer", "Ashley", "Amanda", "Melissa",
        "Daniel", "Matthew", "Anthony", "Mark", "Laura", "Carol", "Maria",
    ]
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor",
        "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Lee",
    ]
    TIMEZONES = [
        "America/New_York", "America/Los_Angeles", "America/Chicago",
        "America/Denver", "Europe/London", "Europe/Paris", "Europe/Berlin",
        "Asia/Tokyo", "Asia/Singapore", "Australia/Sydney",
    ]
    LOCALES = ["en-US", "en-GB", "fr-FR", "de-DE", "es-ES", "nl-NL"]

    def __init__(self, proxy: Optional[str] = None, headless: bool = True):
        self.proxy = proxy
        self.headless = headless

    # ── helpers ──────────────────────────────
    def _random_password(self) -> str:
        chars = string.ascii_letters + string.digits + "!@#$"
        pwd = (
            random.choice(string.ascii_uppercase)
            + random.choice(string.ascii_lowercase)
            + random.choice(string.digits)
            + random.choice("!@#$")
            + "".join(random.choices(chars, k=8))
        )
        return "".join(random.sample(pwd, len(pwd)))

    def _random_name(self) -> tuple:
        return random.choice(self.FIRST_NAMES), random.choice(self.LAST_NAMES)

    def _random_ua(self) -> str:
        ver = random.choice(["120.0.0.0", "121.0.0.0", "122.0.0.0", "124.0.0.0"])
        return (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{ver} Safari/537.36"
        )

    def _human_type(self, page, selector: str, text: str):
        """Gõ từng ký tự giống người để tránh bot-detect."""
        page.click(selector, timeout=10000)
        time.sleep(random.uniform(0.2, 0.5))
        for ch in text:
            page.type(selector, ch, delay=random.randint(60, 160))
        time.sleep(random.uniform(0.3, 0.7))

    # ── main ─────────────────────────────────
    def create_account(self, log_callback=None) -> Dict:
        from playwright.sync_api import sync_playwright

        def log(msg):
            print(f"[CREATOR] {msg}")
            if log_callback:
                log_callback(msg)

        result = {"success": False, "email": None, "password": None, "name": None, "error": None}

        # 1. Email tạm
        log("📧 Lấy email tạm từ Guerrillamail...")
        try:
            email_svc = TempEmailService()
            email = email_svc.get_email()
            log(f"✅ Email: {email}")
        except Exception as e:
            result["error"] = f"Không lấy được email tạm: {e}"
            return result

        # 2. Thông tin ngẫu nhiên
        first, last = self._random_name()
        full_name = f"{first} {last}"
        password = self._random_password()
        ua = self._random_ua()
        timezone = random.choice(self.TIMEZONES)
        locale = random.choice(self.LOCALES)
        vw = random.randint(1280, 1920)
        vh = random.randint(720, 1080)

        log(f"👤 Tên: {full_name} | 🔑 Pass: {password}")

        # 3. Playwright fresh context
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                ],
            )

            ctx_opts = {
                "user_agent": ua,
                "viewport": {"width": vw, "height": vh},
                "locale": locale,
                "timezone_id": timezone,
            }
            if self.proxy:
                ctx_opts["proxy"] = {"server": self.proxy}
                log(f"🌐 Proxy: {self.proxy}")

            context = browser.new_context(**ctx_opts)

            # Stealth: ẩn webdriver
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                window.chrome = {runtime: {}};
            """)

            page = context.new_page()

            try:
                # 4. Mở trang đăng ký
                log("🌐 Mở trang đăng ký Vimeo...")
                page.goto("https://vimeo.com/join", wait_until="domcontentloaded", timeout=30000)
                time.sleep(random.uniform(1.5, 3.0))

                # 5. Điền form
                log("✍️ Điền thông tin đăng ký...")

                # Selectors Vimeo join form
                sel_name  = "input[name='user[display_name]'], input[placeholder*='name' i], #signup_display_name"
                sel_email = "input[name='user[email]'], input[type='email'], #signup_email"
                sel_pass  = "input[name='user[password]'], input[type='password'], #signup_password"
                sel_btn   = "button[type='submit'], button:has-text('Join'), input[type='submit']"

                page.wait_for_selector(sel_email, timeout=15000)

                try:
                    self._human_type(page, sel_name, full_name)
                except Exception:
                    log("⚠️ Không tìm thấy trường tên, bỏ qua...")

                self._human_type(page, sel_email, email)
                self._human_type(page, sel_pass, password)

                # 6. Submit
                log("🚀 Submit form...")
                time.sleep(random.uniform(0.8, 1.8))
                page.click(sel_btn, timeout=10000)
                time.sleep(5)

                # 7. Kiểm tra kết quả
                current = page.url
                log(f"📍 URL sau đăng ký: {current}")

                if "join" in current or "error" in current.lower():
                    try:
                        err = page.inner_text(".iris_alert, .error, [class*='error']")
                        result["error"] = f"Vimeo từ chối: {err[:100]}"
                    except Exception:
                        result["error"] = "Đăng ký thất bại (không rõ lý do)"
                    return result

                # 8. Chờ email xác nhận
                log("📬 Đang chờ email xác nhận từ Vimeo...")
                confirm = email_svc.wait_for_confirm_link(timeout=90)

                if confirm:
                    log(f"🔗 Mở link xác nhận...")
                    page.goto(confirm, timeout=30000)
                    time.sleep(3)
                    log("✅ Email đã xác nhận!")
                else:
                    log("⚠️ Không nhận được email xác nhận (có thể không cần hoặc đã tự xử lý)")

                # 9. Lưu tài khoản
                result.update({"success": True, "email": email, "password": password, "name": full_name})
                self._save(result)
                log(f"💾 Tài khoản đã lưu vào {self.ACCOUNTS_FILE}")

            except Exception as e:
                import traceback
                traceback.print_exc()
                result["error"] = str(e)
                log(f"❌ Lỗi: {e}")
            finally:
                context.close()
                browser.close()

        return result

    def _save(self, data: Dict):
        accounts: List[Dict] = []
        if os.path.exists(self.ACCOUNTS_FILE):
            try:
                with open(self.ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    accounts = json.load(f)
            except Exception:
                accounts = []

        accounts.append({
            "email":      data["email"],
            "password":   data["password"],
            "name":       data["name"],
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status":     "active",
        })

        with open(self.ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=2, ensure_ascii=False)

    # ── tạo nhiều tài khoản ──────────────────
    def create_multiple(
        self,
        count: int,
        proxies: Optional[List[str]] = None,
        log_callback=None,
    ) -> List[Dict]:
        """Tạo `count` tài khoản, luân phiên proxy nếu có."""
        results = []
        for i in range(count):
            proxy = proxies[i % len(proxies)] if proxies else self.proxy
            if log_callback:
                log_callback(f"\n[{i+1}/{count}] 🔄 Đang tạo tài khoản #{i+1}...")
            creator = VimeoAccountCreator(proxy=proxy, headless=self.headless)
            r = creator.create_account(log_callback=log_callback)
            results.append(r)
            if r["success"]:
                if log_callback:
                    log_callback(f"✅ [{i+1}/{count}] Thành công: {r['email']}")
            else:
                if log_callback:
                    log_callback(f"❌ [{i+1}/{count}] Thất bại: {r.get('error')}")

            # Nghỉ ngẫu nhiên giữa các lần tạo
            if i < count - 1:
                wait = random.randint(15, 40)
                if log_callback:
                    log_callback(f"⏳ Chờ {wait}s trước tài khoản tiếp theo...")
                time.sleep(wait)

        return results

    @staticmethod
    def load_accounts() -> List[Dict]:
        """Đọc danh sách tài khoản đã lưu."""
        path = VimeoAccountCreator.ACCOUNTS_FILE
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


# ─────────────────────────────────────────────
#  Test nhanh
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Vimeo Account Creator – Test")
    print("=" * 60)

    creator = VimeoAccountCreator(
        proxy=None,       # Thêm proxy: "http://ip:port"
        headless=False,   # False = thấy browser
    )

    result = creator.create_account()
    print("\n── Kết quả ──")
    print(json.dumps(result, indent=2, ensure_ascii=False))
