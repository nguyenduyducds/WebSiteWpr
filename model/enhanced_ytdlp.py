"""
Enhanced yt-dlp Helper - Nâng cấp với retry, cache, và parallel processing
Version: 2.0.7+ (Anti-Rate-Limit Edition)
"""

import yt_dlp
import os
import json
import time
import hashlib
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from threading import Lock, Semaphore

class EnhancedYTDLP:
    """
    yt-dlp wrapper với các tính năng nâng cao:
    - Retry mechanism với exponential backoff
    - Cache (lưu kết quả)
    - Parallel processing với rate limiting
    - User-agent rotation
    - Adaptive delays để tránh bị block
    - Better error handling
    """
    
    # User-agent pool để rotate
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    def __init__(self, cookies_file="facebook_cookies.txt", cache_dir=".cache/ytdlp", 
                 max_workers=5, request_delay=0.5, timeout=30):
        """
        Args:
            cookies_file: Path to cookies file
            cache_dir: Directory to store cache
            max_workers: Maximum parallel workers (default: 5)
            request_delay: Delay between requests in seconds (default: 0.5)
            timeout: Socket timeout in seconds (default: 30)
        """
        self.cookies_file = cookies_file
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting settings
        self.max_workers = max_workers
        self.request_delay = request_delay
        self.timeout = timeout
        self.last_request_time = 0
        self.request_lock = Lock()
        
        # Semaphore để giới hạn concurrent requests
        self.semaphore = Semaphore(max_workers)
        
        # Base options for yt-dlp
        self.base_opts = {
            'quiet': True,
            'no_warnings': True,
            'simulate': True,
            'extract_flat': False,
            'noplaylist': True,
            'ignoreerrors': True,
            'socket_timeout': timeout,
            # BỔ SUNG BYPASS MẠNH (Không cần VPN/Proxy đối với đa phần trường hợp)
            'extractor_args': {
                'youtube': {
                    # Dùng client android/ios để lách thuật toán chặn IP / captcha của YouTube
                    'player_client': ['android', 'ios'],
                }
            },
            'sleep_interval_requests': 1.0, # Nghỉ một chút giữa các request để youtube khỏi block
            'nocheckcertificate': True,     # Vượt qua lỗi SSL nếu có
            # Tắt random User-Agent tự chế (yt-dlp sẽ tự làm tốt hơn và ít bị lock hơn khi đi kèm player_client)
        }
        
        # Tự động load danh sách Proxy nếu có (để không phải fake VPN toàn máy)
        self.proxies = []
        if os.path.exists("proxies.txt"):
            try:
                with open("proxies.txt", "r", encoding="utf-8") as f:
                    self.proxies = [p.strip() for p in f.readlines() if p.strip() and not p.startswith("#")]
                if self.proxies:
                    print(f"[YTDLP+] 🛡️ Đã tải {len(self.proxies)} proxies dự phòng từ proxies.txt")
            except Exception as e:
                print(f"[YTDLP+] ⚠️ Error reading proxies.txt: {e}")
        
        # Add cookies if available
        if os.path.exists(cookies_file):
            self.base_opts['cookiefile'] = cookies_file
            print(f"[YTDLP+] ✅ Loaded cookies from {cookies_file}")
        else:
            print(f"[YTDLP+] ⚠️ No cookies file found, running in guest mode")
        
        print(f"[YTDLP+] ⚙️ Config: workers={max_workers}, delay={request_delay}s, timeout={timeout}s")
    
    def _get_cache_key(self, url):
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, url):
        """Get cache file path for URL"""
        cache_key = self._get_cache_key(url)
        return self.cache_dir / f"{cache_key}.json"
    
    def _load_from_cache(self, url, max_age_hours=24):
        """
        Load result from cache if available and not expired
        
        Args:
            url: Video URL
            max_age_hours: Maximum cache age in hours
            
        Returns:
            dict or None: Cached result or None if not found/expired
        """
        cache_path = self._get_cache_path(url)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check cache age
            cache_age = time.time() - cache_path.stat().st_mtime
            if cache_age > max_age_hours * 3600:
                print(f"[YTDLP+] ⏰ Cache expired ({cache_age/3600:.1f}h old)")
                return None
            
            # Load cache
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"[YTDLP+] ✅ Cache hit: {data.get('title', '')[:50]}...")
            return data
            
        except Exception as e:
            print(f"[YTDLP+] ⚠️ Cache load error: {e}")
            return None
    
    def _save_to_cache(self, url, data):
        """Save result to cache"""
        try:
            cache_path = self._get_cache_path(url)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[YTDLP+] 💾 Cached result for future use")
        except Exception as e:
            print(f"[YTDLP+] ⚠️ Cache save error: {e}")
    
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting between requests"""
        with self.request_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.request_delay:
                sleep_time = self.request_delay - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
    
    def _get_random_user_agent(self):
        """Get a random user agent"""
        return random.choice(self.USER_AGENTS)
    
    def get_video_info(self, url, use_cache=True, max_retries=3):
        """
        Get video info with retry, exponential backoff, and rate limiting
        
        Args:
            url: Video URL
            use_cache: Whether to use cache
            max_retries: Number of retries on failure (default: 3)
            
        Returns:
            dict: {'title': str, 'thumbnail': str, 'success': bool, 'error': str}
        """
        result = {
            'title': None,
            'thumbnail': None,
            'success': False,
            'error': None,
            'url': url
        }
        
        # Try cache first
        if use_cache:
            cached = self._load_from_cache(url)
            if cached:
                return cached
        
        # Acquire semaphore to limit concurrent requests
        with self.semaphore:
            # Try extraction with exponential backoff
            for attempt in range(max_retries + 1):
                try:
                    # Wait for rate limiting
                    self._wait_for_rate_limit()
                    
                    if attempt > 0:
                        # Exponential backoff: 2^attempt seconds (2s, 4s, 8s...)
                        backoff_time = min(2 ** attempt, 30)  # Max 30s
                        print(f"[YTDLP+] 🔄 Retry {attempt}/{max_retries} (waiting {backoff_time}s)...")
                        time.sleep(backoff_time)
                    
                    # Lấy base options
                    opts = self.base_opts.copy()
                    
                    # Nâng cấp logic bypass ở mỗi lần retry để ép qua tường lửa
                    if attempt == 1:
                        opts['extractor_args'] = {'youtube': {'player_client': ['ios', 'android']}}
                        opts['sleep_interval_requests'] = 2.0
                    elif attempt == 2:
                        opts['extractor_args'] = {'youtube': {'player_client': ['tv', 'mweb']}}
                        opts['sleep_interval_requests'] = 3.0
                    elif attempt == 3:
                        opts['extractor_args'] = {'youtube': {'player_client': ['web_creator', 'web']}}
                        opts['sleep_interval_requests'] = 5.0
                        
                    # Kích hoạt xoay vòng Proxy ở các lần retry nếu có proxies.txt
                    if self.proxies and attempt > 0:
                        proxy = random.choice(self.proxies)
                        opts['proxy'] = proxy
                        print(f"[YTDLP+] 🔁 Đang đổi IP (Proxy): {proxy}")
                    
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        if info:
                            result['title'] = info.get('title', '').strip()
                            result['thumbnail'] = info.get('thumbnail')
                            result['success'] = True
                            
                            # Save to cache
                            if use_cache and result['title']:
                                self._save_to_cache(url, result)
                            
                            print(f"[YTDLP+] ✅ Extracted: {result['title'][:50]}...")
                            return result
                            
                except Exception as e:
                    error_msg = str(e).lower()
                    result['error'] = str(e)
                    
                    # Check if it's a rate limit error
                    is_rate_limit = any(keyword in error_msg for keyword in 
                                       ['429', 'too many requests', 'rate limit', 'throttle'])
                    
                    if is_rate_limit:
                        print(f"[YTDLP+] ⚠️ Rate limit detected! Slowing down...")
                        # Increase delay temporarily
                        self.request_delay = min(self.request_delay * 1.5, 5.0)
                    
                    if attempt == max_retries:
                        print(f"[YTDLP+] ❌ Failed after {max_retries} retries: {e}")
                    else:
                        print(f"[YTDLP+] ⚠️ Attempt {attempt + 1} failed: {e}")
        
        return result
    
    
    def batch_get_videos(self, urls, max_workers=None, use_cache=True, progress_callback=None):
        """
        Get info for multiple videos in parallel with rate limiting
        
        Args:
            urls: List of video URLs
            max_workers: Number of parallel workers (None = use instance setting)
            use_cache: Whether to use cache
            progress_callback: Callback function(current, total, result)
            
        Returns:
            list: List of result dicts
        """
        results = []
        total = len(urls)
        workers = max_workers or self.max_workers
        
        print(f"[YTDLP+] 🚀 Processing {total} URLs with {workers} workers...")
        print(f"[YTDLP+] 📊 Rate limit: {self.request_delay}s delay, {self.timeout}s timeout")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.get_video_info, url, use_cache): url
                for url in urls
            }
            
            # Collect results as they complete
            for i, future in enumerate(as_completed(future_to_url), 1):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Calculate ETA
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    eta = avg_time * (total - i)
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(i, total, result)
                    else:
                        status = "✅" if result['success'] else "❌"
                        print(f"[YTDLP+] [{i}/{total}] {status} {url[:50]}... (ETA: {eta:.1f}s)")
                        
                except Exception as e:
                    print(f"[YTDLP+] ❌ Error processing {url}: {e}")
                    results.append({
                        'url': url,
                        'title': None,
                        'success': False,
                        'error': str(e)
                    })
        
        success_count = sum(1 for r in results if r['success'])
        total_time = time.time() - start_time
        avg_time = total_time / total if total > 0 else 0
        
        print(f"[YTDLP+] 🏁 Complete: {success_count}/{total} successful")
        print(f"[YTDLP+] ⏱️ Total time: {total_time:.1f}s (avg: {avg_time:.2f}s/video)")
        
        return results
    
    def clear_cache(self, older_than_hours=None):
        """
        Clear cache files
        
        Args:
            older_than_hours: Only clear files older than this (None = all)
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if older_than_hours is None:
                    cache_file.unlink()
                    count += 1
                else:
                    age = time.time() - cache_file.stat().st_mtime
                    if age > older_than_hours * 3600:
                        cache_file.unlink()
                        count += 1
            except Exception as e:
                print(f"[YTDLP+] ⚠️ Error deleting {cache_file}: {e}")
        
        print(f"[YTDLP+] 🗑️ Cleared {count} cache files")


# ============= DEMO USAGE =============
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ENHANCED YT-DLP - DEMO")
    print("=" * 60)
    print()
    
    # Initialize
    ytdlp = EnhancedYTDLP(cookies_file="facebook_cookies.txt")
    
    # Test URLs
    test_urls = [
        "https://www.facebook.com/watch/?v=123456789",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    
    # Test 1: Single video with cache
    print("1️⃣ Testing single video (with cache):")
    result = ytdlp.get_video_info(test_urls[0])
    print(f"   Title: {result['title']}")
    print(f"   Success: {result['success']}")
    print()
    
    # Test 2: Same video again (should hit cache)
    print("2️⃣ Testing cache hit:")
    result = ytdlp.get_video_info(test_urls[0])
    print(f"   Title: {result['title']}")
    print()
    
    # Test 3: Batch processing
    print("3️⃣ Testing batch processing:")
    results = ytdlp.batch_get_videos(test_urls, max_workers=2)
    for i, r in enumerate(results, 1):
        status = "✅" if r['success'] else "❌"
        print(f"   [{i}] {status} {r['title'][:50] if r['title'] else 'Failed'}...")
    
    print()
    print("=" * 60)
    print("✅ DEMO COMPLETE")
    print("=" * 60)
