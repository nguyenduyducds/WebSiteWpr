import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import re

class VimeoHttpHelper:
    def __init__(self):
        # Create a CloudScraper session (bypasses simple Cloudflare)
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.cookies_file = "vimeo_cookies.txt"

    def login(self, email, password):
        """
        Attempt to login via HTTP with CloudScraper.
        """
        try:
            # 1. Get Login Page for CSRF Token
            print("[HTTP-CF] Fetching Login Page...")
            resp = self.session.get("https://vimeo.com/log_in")
            
            if resp.status_code != 200:
                return False, f"Failed to load page: {resp.status_code}"

            # Search for CSRF / Scripts
            xsrft = None
            match = re.search(r'"xsrft":"([^"]+)"', resp.text)
            if match:
                xsrft = match.group(1)
            
            if not xsrft:
                soup = BeautifulSoup(resp.text, 'lxml')
                inp = soup.find('input', {'name': 'token'})
                if inp: xsrft = inp.get('value')
            
            if not xsrft:
                 return False, "Could not extract CSRF token (Structure changed?)"

            print(f"[HTTP-CF] CSRF: {xsrft[:10]}...")

            # 2. Login POST
            payload = {
                "email": email,
                "password": password,
                "action": "login",
                "service": "vimeo",
                "token": xsrft
            }
            
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://vimeo.com/log_in"
            }
            
            print("[HTTP-CF] Sending Credentials...")
            login_resp = self.session.post(
                "https://vimeo.com/log_in?action=login", 
                data=payload,
                headers=headers
            )
            
            if "user_id" in login_resp.text:
                 # Check if we got cookies
                 cookies = self.session.cookies.get_dict()
                 if "vimeo" in cookies:
                     return True, "Login Success (Cookies obtained)"
                 else:
                     return True, "Login Success (But explicit cookie missing?)"
            
            # Error check
            try:
                rj = login_resp.json()
                if not rj.get("success"):
                     return False, f"Vimeo Error: {rj.get('message', 'Unknown')}"
            except: pass
            
            return False, f"Login Failed or Captcha triggered. {login_resp.status_code}"

        except Exception as e:
            return False, f"Exception: {e}"
