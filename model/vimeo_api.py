"""
Vimeo API Upload Module - Fast video upload using Vimeo REST API
No Selenium needed - Direct API calls for 10x faster uploads!

Requirements:
    pip install PyVimeo

Setup:
    1. Go to https://developer.vimeo.com/apps
    2. Create new app
    3. Generate Access Token with scopes: upload, edit, video_files
    4. Add credentials to vimeo_api_config.json
"""

import os
import time
import json
import vimeo
from typing import Optional, Tuple, Dict, Callable


class VimeoAPIUploader:
    """Fast Vimeo upload using official API"""
    
    def __init__(self, config_file: str = "vimeo_api_config.json"):
        """
        Initialize Vimeo API client
        
        Args:
            config_file: Path to config file with API credentials
        """
        self.config_file = config_file
        self.client = None
        self.load_config()
    
    def load_config(self):
        """Load API credentials from config file"""
        try:
            if not os.path.exists(self.config_file):
                print(f"[VIMEO_API] ⚠️ Config file not found: {self.config_file}")
                print(f"[VIMEO_API] Creating template config file...")
                self.create_template_config()
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            token = config.get('access_token')
            client_id = config.get('client_id')
            client_secret = config.get('client_secret')
            
            if not token or not client_id or not client_secret:
                print(f"[VIMEO_API] ❌ Missing credentials in config file")
                return False
            
            # Initialize Vimeo client
            self.client = vimeo.VimeoClient(
                token=token,
                key=client_id,
                secret=client_secret
            )
            
            print(f"[VIMEO_API] ✅ API client initialized")
            return True
            
        except Exception as e:
            print(f"[VIMEO_API] ❌ Error loading config: {e}")
            return False
    
    def create_template_config(self):
        """Create template config file"""
        template = {
            "access_token": "bbae08872f2a3151647e386e9872f3db",
            "client_id": "c98b7960179d9b0a7057603f1c8a88def562250e",
            "client_secret": "pftWGNTTxptr8taF5t4MHzYPn8ure2h4WMdmZXCE3jl5FlnEinSvmC50krQNaBfkZ0/UAgbslYDvfXRvcUvnPCGRER6KNhGI2BBfIENuxx3LQHUufpawR/BoUwY/jwRL",
            "instructions": {
                "step_1": "Go to https://developer.vimeo.com/apps",
                "step_2": "Create new app or select existing app",
                "step_3": "Go to 'Authentication' tab",
                "step_4": "Generate Access Token with scopes: upload, edit, video_files, private",
                "step_5": "Copy Client ID, Client Secret, and Access Token",
                "step_6": "Paste them above and save this file"
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4, ensure_ascii=False)
        
        print(f"[VIMEO_API] ✅ Created template config: {self.config_file}")
        print(f"[VIMEO_API] 📝 Please fill in your API credentials")
    
    def upload_video(
        self, 
        file_path: str, 
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy: str = "anybody",
        log_callback: Optional[Callable] = None
    ) -> Tuple[bool, str, Optional[Dict], bool]:
        """
        Upload video to Vimeo using API (FAST!)
        
        Args:
            file_path: Path to video file
            title: Video title (optional, uses filename if not provided)
            description: Video description (optional)
            privacy: Privacy setting - "anybody", "nobody", "password", "unlisted"
            log_callback: Callback function for progress updates
            
        Returns:
            Tuple of (success, message, video_data, quota_exceeded)
            video_data contains: video_link, embed_code, video_id, title
        """
        if not self.client:
            return False, "API client not initialized. Please check config file.", None, False
        
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}", None, False
        
        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            filename = os.path.basename(file_path)
            
            # Use filename as title if not provided
            if not title:
                title = os.path.splitext(filename)[0]
            
            print(f"[VIMEO_API] 📤 Uploading: {filename} ({file_size_mb:.1f} MB)")
            if log_callback:
                log_callback(f"[API] 📤 Uploading {filename} ({file_size_mb:.1f} MB)...")
            
            # Check quota first (if available)
            try:
                user_info = self.client.get('/me').json()
                quota = user_info.get('upload_quota', {})
                space_free = quota.get('space', {}).get('free', 0)
                
                # Free accounts may not return quota info (returns 0)
                if space_free > 0:
                    if space_free < file_size:
                        space_free_mb = space_free / (1024 * 1024)
                        print(f"[VIMEO_API] ❌ Not enough quota: {space_free_mb:.1f} MB free, need {file_size_mb:.1f} MB")
                        return False, "QUOTA_EXCEEDED", None, True
                    
                    print(f"[VIMEO_API] ✅ Quota OK: {space_free / (1024 * 1024):.1f} MB free")
                else:
                    # Free account - quota not available via API
                    print(f"[VIMEO_API] ℹ️ Quota info not available (Free account)")
                    print(f"[VIMEO_API] ℹ️ Free accounts have 500 MB/week limit")
            except Exception as e:
                print(f"[VIMEO_API] ⚠️ Could not check quota: {e}")
            
            # Upload video
            start_time = time.time()
            print(f"[VIMEO_API] ⏳ Starting upload...")
            if log_callback:
                log_callback("[API] ⏳ Đang upload video...")
            
            try:
                # Upload with metadata
                video_uri = self.client.upload(
                    file_path,
                    data={
                        'name': title,
                        'description': description or '',
                        'privacy': {
                            'view': privacy,
                            'embed': 'public'  # Allow embedding
                        }
                    }
                )
                
                upload_time = time.time() - start_time
                print(f"[VIMEO_API] ✅ Upload complete in {upload_time:.1f}s!")
                if log_callback:
                    log_callback(f"[API] ✅ Upload xong ({upload_time:.1f}s)")
                
            except vimeo.exceptions.VideoUploadFailure as e:
                error_msg = str(e)
                if 'quota' in error_msg.lower() or 'storage' in error_msg.lower():
                    return False, "QUOTA_EXCEEDED", None, True
                return False, f"Upload failed: {error_msg}", None, False
            
            # Extract video ID
            video_id = video_uri.split('/')[-1]
            print(f"[VIMEO_API] 🎬 Video ID: {video_id}")
            
            # Wait for video to be processed
            print(f"[VIMEO_API] ⏳ Đợi Vimeo xử lý video...")
            if log_callback:
                log_callback("[API] ⏳ Đang đợi Vimeo xử lý video...")
            
            processing_done = self.wait_for_processing(video_uri, log_callback=log_callback)
            
            if processing_done:
                print(f"[VIMEO_API] ✅ Video đã xử lý xong!")
                if log_callback:
                    log_callback("[API] ✅ Video đã sẵn sàng!")
            else:
                print(f"[VIMEO_API] ⚠️ Video vẫn đang xử lý")
                if log_callback:
                    log_callback("[API] ⚠️ Video vẫn đang xử lý")
            
            # Get video details
            video_data = self.client.get(video_uri).json()
            
            # Get embed code
            embed_html = video_data.get('embed', {}).get('html', '')
            
            # If no embed HTML, construct it
            if not embed_html:
                embed_html = (
                    f'<div style="padding:56.25% 0 0 0;position:relative;">'
                    f'<iframe src="https://player.vimeo.com/video/{video_id}?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" '
                    f'frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media" '
                    f'style="position:absolute;top:0;left:0;width:100%;height:100%;" title="{title}"></iframe>'
                    f'</div><script src="https://player.vimeo.com/api/player.js"></script>'
                )
            
            video_link = video_data.get('link', f"https://vimeo.com/{video_id}")
            
            # Generate thumbnail - try Vimeo API first (highest quality)
            thumbnail_path = None
            try:
                print(f"[VIMEO_API] 📸 Lấy thumbnail từ Vimeo API...")
                thumbnail_path = self.fetch_vimeo_thumbnail(video_uri, video_id)
                if thumbnail_path:
                    print(f"[VIMEO_API] ✅ Thumbnail từ Vimeo: {os.path.basename(thumbnail_path)}")
                else:
                    print(f"[VIMEO_API] ⚠️ Không lấy được từ Vimeo, thử chụp từ file video...")
                    thumbnail_path = self.generate_thumbnail(file_path, video_id)
                    if thumbnail_path:
                        print(f"[VIMEO_API] ✅ Thumbnail từ video: {os.path.basename(thumbnail_path)}")
            except Exception as e:
                print(f"[VIMEO_API] ⚠️ Thumbnail generation failed: {e}")
            
            result_data = {
                "video_link": video_link,
                "embed_code": embed_html,
                "video_id": video_id,
                "title": title,
                "thumbnail": thumbnail_path
            }
            
            total_time = time.time() - start_time
            print(f"[VIMEO_API] 🎉 Total time: {total_time:.1f}s")
            
            return True, "Upload thành công!", result_data, False
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Lỗi upload: {e}", None, False
    
    def wait_for_processing(
        self, 
        video_uri: str, 
        max_wait: int = 900,
        log_callback: Optional[Callable] = None
    ) -> bool:
        """
        Wait for video to finish processing
        
        Args:
            video_uri: Video URI from upload (e.g., /videos/123456)
            max_wait: Maximum seconds to wait (default 900 = 15 minutes)
            log_callback: Callback for progress updates
            
        Returns:
            True if video is ready, False if timeout
        """
        start_time = time.time()
        check_interval = 10  # Check every 10 seconds
        last_log_time = 0
        
        while time.time() - start_time < max_wait:
            try:
                video_data = self.client.get(video_uri).json()
                status = video_data.get('status', 'unknown')
                transcode_status = video_data.get('transcode', {}).get('status', 'unknown')
                
                elapsed = int(time.time() - start_time)
                
                # Check if video is available
                if status == 'available' and transcode_status == 'complete':
                    print(f"[VIMEO_API] ✅ Video sẵn sàng sau {elapsed}s!")
                    return True
                
                # Log progress every 30 seconds
                if time.time() - last_log_time > 30:
                    print(f"[VIMEO_API] ⏳ Status: {status}, Transcode: {transcode_status} ({elapsed}s)")
                    if log_callback:
                        log_callback(f"[API] ⏳ Đang xử lý... ({elapsed//60} phút)")
                    last_log_time = time.time()
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"[VIMEO_API] ⚠️ Error checking status: {e}")
                time.sleep(check_interval)
        
        # Timeout
        elapsed = int(time.time() - start_time)
        print(f"[VIMEO_API] ⏱️ Timeout sau {elapsed}s")
        return False
    
    def fetch_vimeo_thumbnail(self, video_uri: str, video_id: str) -> Optional[str]:
        """
        Lấy thumbnail chất lượng cao nhất từ Vimeo API.
        Vimeo cung cấp nhiều size, ta chọn size lớn nhất.
        """
        try:
            import urllib.request

            thumb_dir = os.path.join(os.getcwd(), "thumbnails")
            os.makedirs(thumb_dir, exist_ok=True)
            save_path = os.path.join(thumb_dir, f"thumb_{video_id}.jpg")

            # Gọi Vimeo API lấy danh sách pictures
            pictures_uri = f"{video_uri}/pictures"
            resp = self.client.get(pictures_uri)
            data = resp.json()

            sizes = []
            # Có thể trả về list hoặc single object
            if isinstance(data, dict):
                items = data.get('data', [data])
            else:
                items = data

            for item in items:
                for sz in item.get('sizes', []):
                    w = sz.get('width', 0)
                    link = sz.get('link_with_play_button') or sz.get('link', '')
                    if link and w:
                        sizes.append((w, link))

            if not sizes:
                # Thử lấy từ video data trực tiếp
                video_data = self.client.get(video_uri, params={'fields': 'pictures'}).json()
                for sz in video_data.get('pictures', {}).get('sizes', []):
                    w = sz.get('width', 0)
                    link = sz.get('link_with_play_button') or sz.get('link', '')
                    if link and w:
                        sizes.append((w, link))

            if not sizes:
                print(f"[VIMEO_API] ⚠️ Không tìm thấy thumbnail từ API")
                return None

            # Chọn ảnh có width lớn nhất (chất lượng cao nhất)
            sizes.sort(key=lambda x: x[0], reverse=True)
            best_url = sizes[0][1]
            best_width = sizes[0][0]
            print(f"[VIMEO_API] 🖼️ Thumbnail tốt nhất: {best_width}px - {best_url}")

            # Tải về
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(best_url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(save_path, 'wb') as f:
                    f.write(response.read())

            if os.path.getsize(save_path) > 0:
                return save_path
            return None

        except Exception as e:
            print(f"[VIMEO_API] fetch_vimeo_thumbnail error: {e}")
            return None

    def generate_thumbnail(self, video_path: str, video_id: str) -> Optional[str]:
        """Fallback: chụp frame từ file video với chất lượng cao"""
        try:
            thumb_dir = os.path.join(os.getcwd(), "thumbnails")
            os.makedirs(thumb_dir, exist_ok=True)
            save_path = os.path.join(thumb_dir, f"thumb_{video_id}.jpg")

            # Thử dùng ffmpeg trước (chất lượng tốt nhất)
            import subprocess, shutil
            if shutil.which('ffmpeg'):
                try:
                    # Lấy duration rồi chụp frame ở giữa
                    probe = subprocess.run(
                        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                         '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
                        capture_output=True, text=True, timeout=30
                    )
                    duration = float(probe.stdout.strip() or '0')
                    seek_time = max(duration / 2, 1)

                    result = subprocess.run([
                        'ffmpeg', '-y',
                        '-ss', str(seek_time),
                        '-i', video_path,
                        '-frames:v', '1',
                        '-q:v', '1',      # Chất lượng JPEG cao nhất (1-31, 1=tốt nhất)
                        '-vf', 'scale=1280:-1',  # Scale lên 1280px nếu cần
                        save_path
                    ], capture_output=True, timeout=60)

                    if result.returncode == 0 and os.path.exists(save_path):
                        print(f"[VIMEO_API] 📸 Thumbnail ffmpeg OK ({os.path.getsize(save_path)//1024} KB)")
                        return save_path
                except Exception as fe:
                    print(f"[VIMEO_API] ffmpeg error: {fe}")

            # Fallback: dùng OpenCV với chất lượng JPEG cao
            import cv2
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(total_frames // 2, 1))
            ret, frame = cap.read()
            cap.release()

            if ret:
                # Lưu với chất lượng JPEG cao nhất (95)
                cv2.imwrite(save_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                print(f"[VIMEO_API] 📸 Thumbnail cv2 OK ({os.path.getsize(save_path)//1024} KB)")
                return save_path

            return None

        except Exception as e:
            print(f"[VIMEO_API] generate_thumbnail error: {e}")
            return None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get user account info and quota"""
        if not self.client:
            return None
        
        try:
            user_info = self.client.get('/me').json()
            quota = user_info.get('upload_quota', {})
            
            space_total = quota.get('space', {}).get('max', 0)
            space_used = quota.get('space', {}).get('used', 0)
            space_free = quota.get('space', {}).get('free', 0)
            
            return {
                'name': user_info.get('name'),
                'link': user_info.get('link'),
                'quota_total_mb': space_total / (1024 * 1024),
                'quota_used_mb': space_used / (1024 * 1024),
                'quota_free_mb': space_free / (1024 * 1024),
                'quota_percent': (space_used / space_total * 100) if space_total > 0 else 0
            }
        except Exception as e:
            print(f"[VIMEO_API] Error getting user info: {e}")
            return None


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("Vimeo API Upload Test")
    print("=" * 60)
    
    uploader = VimeoAPIUploader()
    
    if not uploader.client:
        print("\n❌ API client not initialized")
        print("📝 Please configure vimeo_api_config.json with your credentials")
        print("\nSteps:")
        print("1. Go to https://developer.vimeo.com/apps")
        print("2. Create new app")
        print("3. Generate Access Token with scopes: upload, edit, video_files")
        print("4. Fill in vimeo_api_config.json")
    else:
        print("\n✅ API client ready!")
        
        # Get user info
        user_info = uploader.get_user_info()
        if user_info:
            print(f"\n👤 User: {user_info['name']}")
            print(f"💾 Quota: {user_info['quota_free_mb']:.1f} MB free / {user_info['quota_total_mb']:.1f} MB total")
            print(f"📊 Used: {user_info['quota_percent']:.1f}%")
