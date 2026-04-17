"""
Facebook Fast Fetcher - Bypass yt-dlp for Facebook
Sử dụng REST API + requests thay vì yt-dlp để tránh bị block

Features:
- Dùng Facebook oEmbed API (nhanh nhất)
- Fallback to Mobile scrape (m.facebook.com)
- Fallback to requests + BeautifulSoup (multi-UA)
- Cuối cùng mới dùng yt-dlp
"""

import requests
import re
import time
import json
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
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
        Tries multiple oEmbed endpoints:
        - video/oembed.json
        - post/oembed.json  
        - page/oembed.json
        """
        try:
            # Clean URL
            clean_url = url.replace('m.facebook.com', 'www.facebook.com')
            clean_url = clean_url.replace('web.facebook.com', 'www.facebook.com')
            
            # Try multiple oEmbed endpoints
            oembed_endpoints = [
                f"https://www.facebook.com/plugins/video/oembed.json/?url={quote(clean_url)}",
                f"https://www.facebook.com/plugins/post/oembed.json/?url={quote(clean_url)}",
            ]
            
            for oembed_url in oembed_endpoints:
                try:
                    response = self.session.get(oembed_url, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract title from various fields
                        title = None
                        if 'title' in data:
                            title = data['title']
                        
                        # Try author_name as fallback title
                        if not title and 'author_name' in data:
                            title = data['author_name']
                        
                        if not title and 'html' in data:
                            html = data['html']
                            # Try multiple patterns
                            for pattern in [r'title="([^"]+)"', r'aria-label="([^"]+)"']:
                                title_match = re.search(pattern, html)
                                if title_match:
                                    title = title_match.group(1)
                                    break
                        
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
                except:
                    continue
            
            return {'success': False, 'error': f'oEmbed returned errors for all endpoints'}
            
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
    
    def fetch_via_mobile_scrape(self, url: str) -> Dict:
        """
        Method 2b: Scrape m.facebook.com (mobile site is simpler)
        Mobile Facebook returns more metadata in HTML than desktop
        """
        try:
            from bs4 import BeautifulSoup
            
            # Convert to mobile URL
            mobile_url = url.replace('www.facebook.com', 'm.facebook.com')
            mobile_url = mobile_url.replace('web.facebook.com', 'm.facebook.com')
            if 'm.facebook.com' not in mobile_url and 'fb.watch' not in mobile_url:
                mobile_url = url  # Keep as-is for fb.watch
            
            # Mobile browser user agent  
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
            }
            
            response = requests.get(mobile_url, headers=headers, timeout=8, allow_redirects=True)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'Mobile HTTP {response.status_code}'}
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            title = None
            thumbnail = None
            
            # 1. Try og:title
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content')
            
            # 2. Try og:description as fallback
            if not title:
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    desc = og_desc.get('content', '')
                    if desc and len(desc) > 5:
                        title = desc[:200]  # Use first 200 chars of description
            
            # 3. Try twitter:title
            if not title:
                tw_title = soup.find('meta', attrs={'name': 'twitter:title'})
                if tw_title:
                    title = tw_title.get('content')
            
            # 4. Try <title> tag
            if not title and soup.title:
                title = soup.title.string
            
            # 5. Try JSON-LD structured data
            if not title:
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        ld_data = json.loads(script.string)
                        if isinstance(ld_data, dict):
                            title = ld_data.get('name') or ld_data.get('headline')
                            if not thumbnail:
                                thumbnail = ld_data.get('thumbnailUrl') or ld_data.get('image')
                    except:
                        pass
            
            # 6. Try to extract from inline JSON data (Facebook embeds data in script tags)
            if not title:
                for pattern in [
                    r'"title"\s*:\s*"([^"]{5,200})"',
                    r'"name"\s*:\s*"([^"]{5,200})"',
                    r'"message"\s*:\s*\{"text"\s*:\s*"([^"]{5,200})"',
                ]:
                    match = re.search(pattern, html)
                    if match:
                        candidate = match.group(1)
                        # Decode unicode escapes
                        try:
                            candidate = candidate.encode().decode('unicode_escape')
                        except:
                            pass
                        if len(candidate) > 5:
                            title = candidate
                            break
            
            # Get thumbnail
            og_image = soup.find('meta', property='og:image')
            if og_image:
                thumbnail = og_image.get('content')
            
            # Validate title
            invalid_titles = ['facebook', 'log into facebook', 'login', 'watch',
                            'this page isn', 'content not found', 'unavailable',
                            'log in or sign up', 'đăng nhập']
            
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
                    'method': 'facebook_mobile_scrape'
                }
            
            return {'success': False, 'error': 'No valid metadata found on mobile site'}
            
        except ImportError:
            return {'success': False, 'error': 'BeautifulSoup not installed'}
        except Exception as e:
            return {'success': False, 'error': f'Mobile scrape error: {str(e)}'}
    
    def fetch_via_requests(self, url: str) -> Dict:
        """
        Method 3: Direct requests with multiple User-Agent strategies
        Tries: Googlebot → Facebook crawler → regular browser
        """
        try:
            from bs4 import BeautifulSoup
            
            # Multiple UA strategies - some sites respond differently to different crawlers
            ua_strategies = [
                {
                    'name': 'Googlebot',
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                },
                {
                    'name': 'FacebookBot',
                    'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                },
                {
                    'name': 'Chrome',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
            ]
            
            for strategy in ua_strategies:
                try:
                    strategy_name = strategy.pop('name')
                    headers = {**strategy, 'Accept-Language': 'en-US,en;q=0.5'}
                    
                    response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    title = None
                    thumbnail = None
                    
                    og_title = soup.find('meta', property='og:title')
                    if og_title:
                        title = og_title.get('content')
                    
                    if not title:
                        og_desc = soup.find('meta', property='og:description')
                        if og_desc:
                            desc = og_desc.get('content', '')
                            if desc and len(desc) > 10:
                                title = desc[:200]
                    
                    og_image = soup.find('meta', property='og:image')
                    if og_image:
                        thumbnail = og_image.get('content')
                    
                    # Validate title
                    invalid_titles = ['facebook', 'log into facebook', 'login', 'watch', 
                                    'this page isn', 'content not found', 'unavailable',
                                    'log in or sign up', 'đăng nhập']
                    
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
                            'method': f'facebook_requests_{strategy_name}'
                        }
                except:
                    continue
            
            return {'success': False, 'error': 'No valid metadata found with any UA strategy'}
            
        except ImportError:
            return {'success': False, 'error': 'BeautifulSoup not installed'}
        except Exception as e:
            return {'success': False, 'error': f'Requests error: {str(e)}'}
    
    def fetch_via_ytdlp(self, url: str) -> Dict:
        """
        Method 4: yt-dlp (LAST RESORT)
        Chỉ dùng khi các method khác fail
        Uses impersonate option for better success rate
        """
        try:
            from model.enhanced_ytdlp import EnhancedYTDLP
            
            ytdlp = EnhancedYTDLP(
                cookies_file="facebook_cookies.txt",
                max_workers=1,
                request_delay=2.0,
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
        
        # Method 2: Mobile scrape (reliable for public videos)
        print(f"[FB-FAST] Trying mobile scrape...")
        result = self.fetch_via_mobile_scrape(url)
        if result['success']:
            print(f"[FB-FAST] ✅ Mobile scrape success: {result.get('title', 'N/A')[:50]}")
            return result
        print(f"[FB-FAST] ⚠️ Mobile scrape failed: {result.get('error')}")
        
        # Method 3: Graph API (if token available)
        if self.access_token:
            print(f"[FB-FAST] Trying Graph API...")
            result = self.fetch_via_graph_api(url)
            if result['success']:
                print(f"[FB-FAST] ✅ Graph API success: {result.get('title', 'N/A')[:50]}")
                return result
            print(f"[FB-FAST] ⚠️ Graph API failed: {result.get('error')}")
        
        # Method 4: Requests + multi-UA strategies
        print(f"[FB-FAST] Trying requests (multi-UA)...")
        result = self.fetch_via_requests(url)
        if result['success']:
            print(f"[FB-FAST] ✅ Requests success: {result.get('title', 'N/A')[:50]}")
            return result
        print(f"[FB-FAST] ⚠️ Requests failed: {result.get('error')}")
        
        # Method 5: yt-dlp (last resort)
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
