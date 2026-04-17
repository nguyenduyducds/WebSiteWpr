"""
Facebook REST API Helper - Lấy video info NHANH bằng REST API
Không cần browser, không bị timeout!
"""

import requests
import json
import re
from urllib.parse import urlparse, parse_qs

class FacebookRestAPI:
    """
    Lấy Facebook video info bằng REST API thay vì browser
    Nhanh hơn 10-100 lần!
    """
    
    def __init__(self, cookies_file=None):
        """
        Args:
            cookies_file: Đường dẫn đến file cookies (optional, nhưng khuyến nghị)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Load cookies nếu có
        if cookies_file:
            self._load_cookies(cookies_file)
    
    def _load_cookies(self, cookies_file):
        """Load cookies từ file Netscape format"""
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        parts = line.strip().split('\t')
                        if len(parts) >= 7:
                            domain, _, path, secure, expiry, name, value = parts[:7]
                            self.session.cookies.set(
                                name=name,
                                value=value,
                                domain=domain,
                                path=path
                            )
            print(f"[FB-API] ✅ Loaded cookies from {cookies_file}")
        except Exception as e:
            print(f"[FB-API] ⚠️ Could not load cookies: {e}")
    
    def get_video_info(self, fb_url, timeout=10):
        """
        Lấy thông tin video Facebook bằng REST API
        
        Args:
            fb_url: URL Facebook video
            timeout: Timeout (giây)
            
        Returns:
            dict: {'title': str, 'thumbnail': str, 'video_id': str}
        """
        result = {
            'title': None,
            'thumbnail': None,
            'video_id': None,
            'success': False
        }
        
        # Extract video ID
        video_id = self._extract_video_id(fb_url)
        if video_id:
            result['video_id'] = video_id
        
        # Method 1: Try oEmbed API (Fastest - Public API)
        try:
            oembed_url = f"https://www.facebook.com/plugins/video/oembed.json/?url={fb_url}"
            response = self.session.get(oembed_url, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                result['title'] = data.get('title') or data.get('author_name')
                result['thumbnail'] = data.get('thumbnail_url')
                
                if result['title']:
                    print(f"[FB-API] ✅ oEmbed: {result['title'][:50]}...")
                    result['success'] = True
                    return result
        except Exception as e:
            print(f"[FB-API] oEmbed failed: {e}")
        
        # Method 2: Scrape Open Graph tags (Fallback)
        try:
            response = self.session.get(fb_url, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 200:
                html = response.text
                
                # Extract og:title
                title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
                if title_match:
                    result['title'] = title_match.group(1)
                
                # Extract og:image
                image_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
                if image_match:
                    result['thumbnail'] = image_match.group(1)
                
                # Extract from JSON-LD
                if not result['title']:
                    json_ld_match = re.search(r'<script type="application/ld\+json">(.+?)</script>', html, re.DOTALL)
                    if json_ld_match:
                        try:
                            json_data = json.loads(json_ld_match.group(1))
                            result['title'] = json_data.get('name') or json_data.get('headline')
                        except:
                            pass
                
                if result['title']:
                    # Clean title
                    result['title'] = result['title'].replace(' | Facebook', '').strip()
                    print(f"[FB-API] ✅ Scraped: {result['title'][:50]}...")
                    result['success'] = True
                    return result
                    
        except Exception as e:
            print(f"[FB-API] Scraping failed: {e}")
        
        # Method 3: Mobile site (Lighter, faster)
        try:
            mobile_url = fb_url.replace('www.facebook.com', 'm.facebook.com')
            response = self.session.get(mobile_url, timeout=timeout)
            
            if response.status_code == 200:
                html = response.text
                
                # Mobile site has simpler HTML
                title_match = re.search(r'<title>([^<]+)</title>', html)
                if title_match:
                    title = title_match.group(1)
                    # Clean mobile title
                    title = title.replace(' | Facebook', '').replace('Facebook', '').strip()
                    
                    if title and len(title) > 3:
                        result['title'] = title
                        print(f"[FB-API] ✅ Mobile: {result['title'][:50]}...")
                        result['success'] = True
                        return result
                        
        except Exception as e:
            print(f"[FB-API] Mobile site failed: {e}")
        
        # If all failed
        if not result['title']:
            result['title'] = "Facebook Video"
            print(f"[FB-API] ⚠️ All methods failed, using default title")
        
        return result
    
    def _extract_video_id(self, fb_url):
        """Extract video ID từ Facebook URL"""
        # Pattern 1: /videos/123456789
        match = re.search(r'/videos/(\d+)', fb_url)
        if match:
            return match.group(1)
        
        # Pattern 2: /watch/?v=123456789
        match = re.search(r'[?&]v=(\d+)', fb_url)
        if match:
            return match.group(1)
        
        # Pattern 3: fb.watch/xxxxx
        if 'fb.watch' in fb_url:
            parsed = urlparse(fb_url)
            return parsed.path.strip('/')
        
        return None
    
    def batch_get_videos(self, urls, timeout=10, max_workers=5):
        """
        Lấy thông tin nhiều video cùng lúc (parallel)
        
        Args:
            urls: List of Facebook URLs
            timeout: Timeout cho mỗi request
            max_workers: Số thread chạy song song
            
        Returns:
            list: List of video info dicts
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.get_video_info, url, timeout): url 
                for url in urls
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    result['url'] = url
                    results.append(result)
                except Exception as e:
                    print(f"[FB-API] Error processing {url}: {e}")
                    results.append({
                        'url': url,
                        'title': 'Error',
                        'success': False
                    })
        
        return results


# ============= DEMO USAGE =============
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 FACEBOOK REST API - DEMO")
    print("=" * 60)
    print()
    
    # Test URLs
    test_urls = [
        "https://www.facebook.com/watch/?v=123456789",
        "https://fb.watch/xxxxx",
    ]
    
    # Initialize API (with cookies for better results)
    api = FacebookRestAPI(cookies_file="facebook_cookies.txt")
    
    # Test single video
    print("1️⃣ Testing single video:")
    url = test_urls[0]
    info = api.get_video_info(url)
    print(f"   Title: {info['title']}")
    print(f"   Thumbnail: {info['thumbnail']}")
    print(f"   Success: {info['success']}")
    print()
    
    # Test batch
    print("2️⃣ Testing batch (parallel):")
    results = api.batch_get_videos(test_urls, max_workers=3)
    for i, result in enumerate(results, 1):
        print(f"   [{i}] {result['title'][:50]}... - {'✅' if result['success'] else '❌'}")
    
    print()
    print("=" * 60)
    print("✅ DEMO COMPLETE")
    print("=" * 60)
