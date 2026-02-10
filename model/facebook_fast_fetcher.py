"""
Facebook Fast Fetcher - Bypass yt-dlp for Facebook
Sử dụng REST API + requests thay vì yt-dlp để tránh bị block

Features:
- Dùng Facebook oEmbed API (nhanh nhất)
- Fallback to Graph API
- Fallback to requests + BeautifulSoup
- Cuối cùng mới dùng yt-dlp
"""

import requests
import re
import time
from typing import Dict, Optional
from urllib.parse import quote, urlparse, parse_qs


class FacebookFastFetcher:
    """
    Fast Facebook video metadata fetcher
    Bypass yt-dlp để tránh rate limiting
    """
    
    def __init__(self, facebook_access_token: Optional[str] = None):
        """
        Args:
            facebook_access_token: Optional Facebook Graph API access token
        """
        self.access_token = facebook_access_token
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract Facebook video ID from URL"""
        patterns = [
            r'facebook\.com/watch/?\?v=(\d+)',
            r'facebook\.com/.*?/videos/(\d+)',
            r'fb\.watch/([a-zA-Z0-9_-]+)',
            r'facebook\.com/reel/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def fetch_via_oembed(self, url: str) -> Dict:
        """
        Method 1: Facebook oEmbed API (FASTEST, NO AUTH)
        https://developers.facebook.com/docs/plugins/oembed
        
        Ưu điểm:
        - Không cần access token
        - Rất nhanh
        - Ít bị rate limit
        """
        try:
            # Clean URL
            clean_url = url.replace('m.facebook.com', 'www.facebook.com')
            clean_url = clean_url.replace('web.facebook.com', 'www.facebook.com')
            
            # oEmbed endpoint
            oembed_url = f"https://www.facebook.com/plugins/video/oembed.json/?url={quote(clean_url)}"
            
            response = self.session.get(oembed_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract title from HTML
                title = None
                if 'title' in data:
                    title = data['title']
                elif 'html' in data:
                    # Parse HTML to get title
                    html = data['html']
                    title_match = re.search(r'title="([^"]+)"', html)
                    if title_match:
                        title = title_match.group(1)
                
                # Get thumbnail
                thumbnail = data.get('thumbnail_url')
                
                if title or thumbnail:
                    return {
                        'success': True,
                        'title': title,
                        'thumbnail': thumbnail,
                        'url': url,
                        'method': 'facebook_oembed'
                    }
            
            return {'success': False, 'error': f'oEmbed returned {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': f'oEmbed error: {str(e)}'}
    
    def fetch_via_graph_api(self, url: str) -> Dict:
        """
        Method 2: Facebook Graph API (FAST, REQUIRES TOKEN)
        https://developers.facebook.com/docs/graph-api/reference/video
        
        Ưu điểm:
        - Chính xác cao
        - Ít bị rate limit
        
        Nhược điểm:
        - Cần access token
        """
        if not self.access_token:
            return {'success': False, 'error': 'No access token'}
        
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return {'success': False, 'error': 'Cannot extract video ID'}
            
            # Graph API endpoint
            graph_url = f"https://graph.facebook.com/v18.0/{video_id}"
            params = {
                'fields': 'title,description,picture,source',
                'access_token': self.access_token
            }
            
            response = self.session.get(graph_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'title': data.get('title') or data.get('description', '').split('\n')[0],
                    'thumbnail': data.get('picture'),
                    'url': url,
                    'method': 'facebook_graph_api'
                }
            
            return {'success': False, 'error': f'Graph API returned {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': f'Graph API error: {str(e)}'}
    
    def fetch_via_requests(self, url: str) -> Dict:
        """
        Method 3: Direct requests + BeautifulSoup (FAST but FRAGILE)
        
        Ưu điểm:
        - Nhanh
        - Không cần auth
        
        Nhược điểm:
        - Dễ bị block
        - Có thể không lấy được title
        """
        try:
            from bs4 import BeautifulSoup
            
            # Use Facebook bot user agent
            headers = {
                'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = self.session.get(url, headers=headers, timeout=8, allow_redirects=True)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract og:title and og:image
            title = None
            thumbnail = None
            
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content')
            
            og_image = soup.find('meta', property='og:image')
            if og_image:
                thumbnail = og_image.get('content')
            
            # Validate title (avoid generic titles)
            invalid_titles = ['facebook', 'log into facebook', 'login', 'watch', 
                            'this page isn', 'content not found', 'unavailable']
            
            if title:
                is_invalid = any(inv in title.lower() for inv in invalid_titles)
                if is_invalid:
                    title = None
            
            if title or thumbnail:
                return {
                    'success': True,
                    'title': title,
                    'thumbnail': thumbnail,
                    'url': url,
                    'method': 'facebook_requests'
                }
            
            return {'success': False, 'error': 'No valid metadata found'}
            
        except ImportError:
            return {'success': False, 'error': 'BeautifulSoup not installed'}
        except Exception as e:
            return {'success': False, 'error': f'Requests error: {str(e)}'}
    
    def fetch_via_ytdlp(self, url: str) -> Dict:
        """
        Method 4: yt-dlp (LAST RESORT)
        Chỉ dùng khi các method khác fail
        """
        try:
            from model.enhanced_ytdlp import EnhancedYTDLP
            
            ytdlp = EnhancedYTDLP(
                cookies_file="facebook_cookies.txt",
                max_workers=1,
                request_delay=2.0,  # Delay dài để tránh rate limit
                timeout=30
            )
            
            result = ytdlp.get_video_info(url, use_cache=True, max_retries=2)
            
            if result['success']:
                result['method'] = 'facebook_ytdlp'
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'yt-dlp error: {str(e)}'}
    
    def get_video_info(self, url: str, skip_ytdlp: bool = True) -> Dict:
        """
        Get Facebook video info with intelligent fallback
        
        Args:
            url: Facebook video URL
            skip_ytdlp: If True, skip yt-dlp (default: True for speed)
        
        Returns:
            dict: {'success': bool, 'title': str, 'thumbnail': str, 'method': str}
        """
        # Validate URL
        if 'facebook.com' not in url and 'fb.watch' not in url:
            return {'success': False, 'error': 'Not a Facebook URL', 'url': url}
        
        print(f"[FB-FAST] Processing: {url[:60]}...")
        
        # Method 1: oEmbed (fastest, no auth)
        print(f"[FB-FAST] Trying oEmbed API...")
        result = self.fetch_via_oembed(url)
        if result['success']:
            print(f"[FB-FAST] ✅ oEmbed success: {result.get('title', 'N/A')[:50]}")
            return result
        print(f"[FB-FAST] ⚠️ oEmbed failed: {result.get('error')}")
        
        # Method 2: Graph API (if token available)
        if self.access_token:
            print(f"[FB-FAST] Trying Graph API...")
            result = self.fetch_via_graph_api(url)
            if result['success']:
                print(f"[FB-FAST] ✅ Graph API success: {result.get('title', 'N/A')[:50]}")
                return result
            print(f"[FB-FAST] ⚠️ Graph API failed: {result.get('error')}")
        
        # Method 3: Requests + BeautifulSoup
        print(f"[FB-FAST] Trying requests...")
        result = self.fetch_via_requests(url)
        if result['success']:
            print(f"[FB-FAST] ✅ Requests success: {result.get('title', 'N/A')[:50]}")
            return result
        print(f"[FB-FAST] ⚠️ Requests failed: {result.get('error')}")
        
        # Method 4: yt-dlp (last resort)
        if not skip_ytdlp:
            print(f"[FB-FAST] Trying yt-dlp (last resort)...")
            result = self.fetch_via_ytdlp(url)
            if result['success']:
                print(f"[FB-FAST] ✅ yt-dlp success: {result.get('title', 'N/A')[:50]}")
                return result
            print(f"[FB-FAST] ⚠️ yt-dlp failed: {result.get('error')}")
        
        # All methods failed
        return {
            'success': False,
            'error': 'All methods failed',
            'url': url,
            'method': 'none'
        }
    
    def batch_get_videos(self, urls: list, skip_ytdlp: bool = True, 
                        delay: float = 0.2, progress_callback=None) -> list:
        """
        Batch fetch Facebook videos
        
        Args:
            urls: List of Facebook URLs
            skip_ytdlp: Skip yt-dlp for speed (default: True)
            delay: Delay between requests (default: 0.2s)
            progress_callback: Optional callback(current, total, result)
        
        Returns:
            list: List of result dicts
        """
        results = []
        total = len(urls)
        
        print(f"[FB-FAST] 🚀 Processing {total} Facebook URLs...")
        print(f"[FB-FAST] ⚙️ Settings: skip_ytdlp={skip_ytdlp}, delay={delay}s")
        
        start_time = time.time()
        
        for i, url in enumerate(urls, 1):
            # Get video info
            result = self.get_video_info(url, skip_ytdlp=skip_ytdlp)
            results.append(result)
            
            # Progress callback
            if progress_callback:
                progress_callback(i, total, result)
            else:
                status = "✅" if result['success'] else "❌"
                method = result.get('method', 'none')
                print(f"[FB-FAST] [{i}/{total}] {status} [{method}]")
            
            # Delay between requests
            if i < total:
                time.sleep(delay)
        
        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if r['success'])
        
        print(f"\n[FB-FAST] 🏁 Complete: {success_count}/{total} successful")
        print(f"[FB-FAST] ⏱️ Time: {elapsed:.1f}s (avg: {elapsed/total:.2f}s/video)")
        
        return results


# ============= DEMO USAGE =============
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 FACEBOOK FAST FETCHER - DEMO")
    print("=" * 60)
    print()
    
    # Initialize
    fetcher = FacebookFastFetcher()
    
    # Test URLs (thay bằng URLs thật của bạn)
    test_urls = [
        "https://www.facebook.com/watch/?v=123456789",
        "https://fb.watch/abc123",
    ]
    
    # Test 1: Single video
    print("1️⃣ Testing single video:")
    if test_urls:
        result = fetcher.get_video_info(test_urls[0], skip_ytdlp=True)
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Method: {result.get('method', 'N/A')}")
        print(f"   Success: {result['success']}")
    print()
    
    # Test 2: Batch processing
    print("2️⃣ Testing batch processing:")
    results = fetcher.batch_get_videos(test_urls, skip_ytdlp=True, delay=0.2)
    
    print()
    print("=" * 60)
    print("✅ DEMO COMPLETE")
    print("=" * 60)
