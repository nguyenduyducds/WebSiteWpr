"""
Smart Video Fetcher - Hybrid Approach
Kết hợp nhiều phương pháp để có tốc độ + độ tin cậy cao nhất

Priority: YouTube API > yt-dlp > requests > Selenium
"""

import os
import re
from typing import Dict, Optional
from model.enhanced_ytdlp import EnhancedYTDLP


class SmartVideoFetcher:
    """
    Intelligent video metadata fetcher với fallback chain
    
    Features:
    - YouTube API (fastest, requires API key)
    - yt-dlp (reliable, multi-platform)
    - requests + BeautifulSoup (fast, simple)
    - Selenium (slow, last resort)
    """
    
    def __init__(self, youtube_api_key: Optional[str] = None, cookies_file: str = "facebook_cookies.txt"):
        """
        Args:
            youtube_api_key: Optional YouTube Data API v3 key
            cookies_file: Path to cookies file for yt-dlp
        """
        self.youtube_api_key = youtube_api_key
        self.cookies_file = cookies_file
        
        # Initialize yt-dlp with optimized settings
        self.ytdlp = EnhancedYTDLP(
            cookies_file=cookies_file,
            max_workers=5,
            request_delay=0.5,
            timeout=30
        )
        
        # YouTube API client (lazy init)
        self._youtube_client = None
    
    def detect_platform(self, url: str) -> str:
        """Detect video platform from URL"""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return 'facebook'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'vimeo.com' in url_lower:
            return 'vimeo'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        else:
            return 'unknown'
    
    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def fetch_via_youtube_api(self, url: str) -> Dict:
        """
        Fetch via YouTube Data API v3 (FASTEST for YouTube)
        
        Requires API key: https://console.cloud.google.com/
        Free quota: 10,000 units/day (~3,000 videos)
        """
        try:
            from googleapiclient.discovery import build
            
            # Lazy init YouTube client
            if not self._youtube_client:
                self._youtube_client = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            video_id = self.extract_youtube_id(url)
            if not video_id:
                return {'success': False, 'error': 'Invalid YouTube URL'}
            
            # Fetch video details
            request = self._youtube_client.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return {'success': False, 'error': 'Video not found'}
            
            snippet = response['items'][0]['snippet']
            
            return {
                'success': True,
                'title': snippet['title'],
                'thumbnail': snippet['thumbnails']['maxres']['url'] if 'maxres' in snippet['thumbnails'] else snippet['thumbnails']['high']['url'],
                'url': url,
                'method': 'youtube_api'
            }
            
        except ImportError:
            print("[API] google-api-python-client not installed. Run: pip install google-api-python-client")
            return {'success': False, 'error': 'Missing google-api-python-client'}
        except Exception as e:
            print(f"[API] YouTube API error: {e}")
            return {'success': False, 'error': str(e)}
    
    def fetch_via_ytdlp(self, url: str) -> Dict:
        """Fetch via yt-dlp (RELIABLE, multi-platform)"""
        try:
            result = self.ytdlp.get_video_info(url, use_cache=True, max_retries=3)
            
            if result['success']:
                result['method'] = 'ytdlp'
            
            return result
            
        except Exception as e:
            print(f"[YTDLP] Error: {e}")
            return {'success': False, 'error': str(e), 'url': url}
    
    def fetch_via_requests(self, url: str) -> Dict:
        """
        Fetch via requests + BeautifulSoup (FAST but fragile)
        Only works for pages with og:tags
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract og:title and og:image
            title_tag = soup.find('meta', property='og:title')
            image_tag = soup.find('meta', property='og:image')
            
            title = title_tag.get('content') if title_tag else None
            thumbnail = image_tag.get('content') if image_tag else None
            
            if not title:
                return {'success': False, 'error': 'No og:title found'}
            
            return {
                'success': True,
                'title': title,
                'thumbnail': thumbnail,
                'url': url,
                'method': 'requests'
            }
            
        except Exception as e:
            print(f"[REQUESTS] Error: {e}")
            return {'success': False, 'error': str(e), 'url': url}
    
    def get_video_info(self, url: str, force_method: Optional[str] = None) -> Dict:
        """
        Get video info with intelligent fallback chain
        
        Args:
            url: Video URL
            force_method: Force specific method ('youtube_api', 'ytdlp', 'requests')
        
        Returns:
            dict: {'success': bool, 'title': str, 'thumbnail': str, 'method': str}
        """
        platform = self.detect_platform(url)
        
        # Force specific method if requested
        if force_method:
            if force_method == 'youtube_api':
                return self.fetch_via_youtube_api(url)
            elif force_method == 'ytdlp':
                return self.fetch_via_ytdlp(url)
            elif force_method == 'requests':
                return self.fetch_via_requests(url)
        
        # Smart fallback chain
        
        # 1. Try YouTube API first (if available and is YouTube)
        if platform == 'youtube' and self.youtube_api_key:
            print(f"[SMART] Trying YouTube API for {url[:50]}...")
            result = self.fetch_via_youtube_api(url)
            if result['success']:
                return result
            print(f"[SMART] YouTube API failed, falling back...")
        
        # 2. Try yt-dlp (most reliable)
        print(f"[SMART] Trying yt-dlp for {url[:50]}...")
        result = self.fetch_via_ytdlp(url)
        if result['success']:
            return result
        print(f"[SMART] yt-dlp failed, falling back...")
        
        # 3. Try requests (fast but fragile)
        print(f"[SMART] Trying requests for {url[:50]}...")
        result = self.fetch_via_requests(url)
        if result['success']:
            return result
        print(f"[SMART] requests failed")
        
        # All methods failed
        return {
            'success': False,
            'error': 'All methods failed',
            'url': url,
            'method': 'none'
        }
    
    def batch_get_videos(self, urls: list, progress_callback=None) -> list:
        """
        Batch fetch with smart routing
        
        Args:
            urls: List of video URLs
            progress_callback: Optional callback(current, total, result)
        
        Returns:
            list: List of result dicts
        """
        results = []
        total = len(urls)
        
        # Group URLs by platform for optimization
        youtube_urls = []
        other_urls = []
        
        for url in urls:
            if self.detect_platform(url) == 'youtube' and self.youtube_api_key:
                youtube_urls.append(url)
            else:
                other_urls.append(url)
        
        print(f"[SMART] Processing {len(youtube_urls)} YouTube URLs via API")
        print(f"[SMART] Processing {len(other_urls)} other URLs via yt-dlp")
        
        # Process YouTube URLs via API (fast)
        for i, url in enumerate(youtube_urls, 1):
            result = self.fetch_via_youtube_api(url)
            results.append(result)
            
            if progress_callback:
                progress_callback(i, total, result)
        
        # Process other URLs via yt-dlp (batch)
        if other_urls:
            ytdlp_results = self.ytdlp.batch_get_videos(other_urls, use_cache=True)
            results.extend(ytdlp_results)
        
        return results


# ============= DEMO USAGE =============
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SMART VIDEO FETCHER - DEMO")
    print("=" * 60)
    print()
    
    # Initialize (with or without YouTube API key)
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')  # Set in environment or replace with your key
    
    fetcher = SmartVideoFetcher(
        youtube_api_key=YOUTUBE_API_KEY,
        cookies_file="facebook_cookies.txt"
    )
    
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # YouTube
        "https://www.facebook.com/watch/?v=123456789",  # Facebook
        "https://vimeo.com/123456789",                  # Vimeo
    ]
    
    # Test 1: Single video
    print("1️⃣ Testing single video:")
    result = fetcher.get_video_info(test_urls[0])
    print(f"   Title: {result.get('title', 'N/A')}")
    print(f"   Method: {result.get('method', 'N/A')}")
    print(f"   Success: {result['success']}")
    print()
    
    # Test 2: Batch processing
    print("2️⃣ Testing batch processing:")
    results = fetcher.batch_get_videos(test_urls)
    for i, r in enumerate(results, 1):
        status = "✅" if r['success'] else "❌"
        method = r.get('method', 'N/A')
        title = r.get('title', 'Failed')[:50] if r.get('title') else 'Failed'
        print(f"   [{i}] {status} [{method}] {title}...")
    
    print()
    print("=" * 60)
    print("✅ DEMO COMPLETE")
    print("=" * 60)
