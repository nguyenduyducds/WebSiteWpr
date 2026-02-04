"""
Facebook Thumbnail Optimizer
Tự động chụp và tối ưu hóa thumbnail chất lượng cao cho Facebook

Facebook ưu tiên:
- Ảnh có kích thước 1200x630px (tỷ lệ 1.91:1)
- Ảnh có độ phân giải cao, rõ nét
- Ảnh không bị nén quá mức
"""

from PIL import Image, ImageEnhance, ImageFilter
import os
import requests
from io import BytesIO


class FacebookThumbnailOptimizer:
    """Tối ưu hóa ảnh thumbnail cho Facebook"""
    
    # Facebook recommended sizes
    FACEBOOK_OG_WIDTH = 1200
    FACEBOOK_OG_HEIGHT = 630
    FACEBOOK_ASPECT_RATIO = 1.91  # 1200/630
    
    # Quality settings
    JPEG_QUALITY = 95  # Chất lượng cao (85-95 là tốt nhất)
    PNG_COMPRESSION = 6  # PNG compression level (0-9, 6 là balanced)
    
    def __init__(self):
        """Initialize optimizer"""
        self.output_dir = "thumbnails_optimized"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"[FB_THUMB] Created output directory: {self.output_dir}")
    
    def optimize_for_facebook(self, image_path, output_filename=None, enhance=True):
        """
        Tối ưu hóa ảnh cho Facebook Open Graph
        
        Args:
            image_path: Đường dẫn ảnh gốc (local hoặc URL)
            output_filename: Tên file output (optional)
            enhance: Có tăng cường chất lượng ảnh không
            
        Returns:
            str: Đường dẫn ảnh đã tối ưu
        """
        try:
            print(f"[FB_THUMB] Optimizing image for Facebook...")
            
            # Load image
            if image_path.startswith('http'):
                print(f"[FB_THUMB] Downloading image from URL...")
                response = requests.get(image_path, timeout=30)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(image_path)
            
            print(f"[FB_THUMB] Original size: {img.size} ({img.mode})")
            
            # Convert to RGB if needed (remove alpha channel)
            if img.mode in ('RGBA', 'LA', 'P'):
                print(f"[FB_THUMB] Converting {img.mode} to RGB...")
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Enhance image quality (optional)
            if enhance:
                img = self._enhance_image(img)
            
            # Resize to Facebook optimal size
            img = self._resize_for_facebook(img)
            
            # Generate output filename
            if not output_filename:
                timestamp = __import__('time').strftime('%Y%m%d_%H%M%S')
                output_filename = f"fb_thumb_{timestamp}.jpg"
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Save with high quality
            img.save(
                output_path,
                'JPEG',
                quality=self.JPEG_QUALITY,
                optimize=True,
                progressive=True,  # Progressive JPEG for better loading
                subsampling=0  # Best quality subsampling
            )
            
            # Get file size
            file_size = os.path.getsize(output_path) / 1024  # KB
            
            print(f"[FB_THUMB] ✅ Optimized image saved!")
            print(f"[FB_THUMB]    Path: {output_path}")
            print(f"[FB_THUMB]    Size: {img.size}")
            print(f"[FB_THUMB]    File size: {file_size:.1f} KB")
            print(f"[FB_THUMB]    Quality: {self.JPEG_QUALITY}%")
            
            return output_path
            
        except Exception as e:
            print(f"[FB_THUMB] ❌ Error optimizing image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _resize_for_facebook(self, img):
        """
        Resize ảnh theo kích thước tối ưu cho Facebook
        Giữ nguyên tỷ lệ và crop nếu cần
        """
        original_width, original_height = img.size
        original_ratio = original_width / original_height
        
        print(f"[FB_THUMB] Resizing to Facebook optimal size ({self.FACEBOOK_OG_WIDTH}x{self.FACEBOOK_OG_HEIGHT})...")
        
        # Calculate target size maintaining aspect ratio
        if original_ratio > self.FACEBOOK_ASPECT_RATIO:
            # Image is wider - fit to height
            new_height = self.FACEBOOK_OG_HEIGHT
            new_width = int(new_height * original_ratio)
        else:
            # Image is taller - fit to width
            new_width = self.FACEBOOK_OG_WIDTH
            new_height = int(new_width / original_ratio)
        
        # Resize with high-quality resampling
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop to exact Facebook size if needed
        if new_width != self.FACEBOOK_OG_WIDTH or new_height != self.FACEBOOK_OG_HEIGHT:
            # Center crop
            left = (new_width - self.FACEBOOK_OG_WIDTH) // 2
            top = (new_height - self.FACEBOOK_OG_HEIGHT) // 2
            right = left + self.FACEBOOK_OG_WIDTH
            bottom = top + self.FACEBOOK_OG_HEIGHT
            
            img = img.crop((left, top, right, bottom))
            print(f"[FB_THUMB] Cropped to exact size: {img.size}")
        
        return img
    
    def _enhance_image(self, img):
        """
        Tăng cường chất lượng ảnh
        - Tăng độ nét (sharpness)
        - Tăng độ tương phản (contrast)
        - Tăng độ bão hòa màu (color saturation)
        """
        print(f"[FB_THUMB] Enhancing image quality...")
        
        # 1. Sharpen (tăng độ nét)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)  # 1.0 = original, >1.0 = sharper
        
        # 2. Contrast (tăng độ tương phản)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)  # Slight contrast boost
        
        # 3. Color saturation (tăng độ bão hòa màu)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)  # Slight color boost
        
        # 4. Brightness (điều chỉnh độ sáng nếu cần)
        # enhancer = ImageEnhance.Brightness(img)
        # img = enhancer.enhance(1.05)
        
        print(f"[FB_THUMB] ✅ Image enhanced (sharper, more contrast)")
        
        return img
    
    def create_thumbnail_from_video_frame(self, video_url, frame_time=5):
        """
        Chụp frame từ video làm thumbnail
        (Requires ffmpeg or selenium for video capture)
        
        Args:
            video_url: URL video (YouTube, Vimeo, etc.)
            frame_time: Thời điểm chụp (giây)
            
        Returns:
            str: Đường dẫn ảnh thumbnail
        """
        # TODO: Implement video frame capture
        # This would require ffmpeg or selenium screenshot
        print(f"[FB_THUMB] Video frame capture not implemented yet")
        return None
    
    def batch_optimize(self, image_paths):
        """
        Tối ưu hóa nhiều ảnh cùng lúc
        
        Args:
            image_paths: List đường dẫn ảnh
            
        Returns:
            list: List đường dẫn ảnh đã tối ưu
        """
        optimized_paths = []
        
        for i, path in enumerate(image_paths, 1):
            print(f"\n[FB_THUMB] Processing {i}/{len(image_paths)}: {os.path.basename(path)}")
            optimized = self.optimize_for_facebook(path)
            if optimized:
                optimized_paths.append(optimized)
        
        print(f"\n[FB_THUMB] ✅ Batch optimization complete: {len(optimized_paths)}/{len(image_paths)} successful")
        return optimized_paths
    
    def validate_facebook_requirements(self, image_path):
        """
        Kiểm tra ảnh có đáp ứng yêu cầu Facebook không
        
        Facebook requirements:
        - Minimum: 200x200px
        - Recommended: 1200x630px
        - Aspect ratio: 1.91:1
        - Max file size: 8MB
        - Format: JPG, PNG
        
        Returns:
            tuple: (is_valid, issues)
        """
        try:
            img = Image.open(image_path)
            width, height = img.size
            file_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
            
            issues = []
            
            # Check minimum size
            if width < 200 or height < 200:
                issues.append(f"❌ Too small: {width}x{height} (minimum 200x200)")
            
            # Check recommended size
            if width < 1200 or height < 630:
                issues.append(f"⚠️ Below recommended: {width}x{height} (recommended 1200x630)")
            
            # Check aspect ratio
            ratio = width / height
            if abs(ratio - self.FACEBOOK_ASPECT_RATIO) > 0.1:
                issues.append(f"⚠️ Aspect ratio: {ratio:.2f} (recommended 1.91:1)")
            
            # Check file size
            if file_size > 8:
                issues.append(f"❌ File too large: {file_size:.1f}MB (max 8MB)")
            
            # Check format
            if img.format not in ['JPEG', 'PNG']:
                issues.append(f"⚠️ Format: {img.format} (recommended JPEG or PNG)")
            
            is_valid = len([i for i in issues if i.startswith('❌')]) == 0
            
            if is_valid and not issues:
                print(f"[FB_THUMB] ✅ Image meets Facebook requirements!")
            else:
                print(f"[FB_THUMB] Validation results:")
                for issue in issues:
                    print(f"[FB_THUMB]   {issue}")
            
            return is_valid, issues
            
        except Exception as e:
            print(f"[FB_THUMB] ❌ Validation error: {e}")
            return False, [f"❌ Error: {e}"]


# Test and Demo
if __name__ == "__main__":
    print("=" * 60)
    print("FACEBOOK THUMBNAIL OPTIMIZER")
    print("=" * 60)
    print()
    
    optimizer = FacebookThumbnailOptimizer()
    
    print("Features:")
    print("✅ Resize to Facebook optimal size (1200x630px)")
    print("✅ Enhance sharpness, contrast, and color")
    print("✅ High-quality JPEG compression (95%)")
    print("✅ Remove alpha channel (convert to RGB)")
    print("✅ Progressive JPEG for better loading")
    print("✅ Validate Facebook requirements")
    print()
    
    print("Usage:")
    print("  optimizer = FacebookThumbnailOptimizer()")
    print("  optimized_path = optimizer.optimize_for_facebook('path/to/image.jpg')")
    print()
    
    print("=" * 60)
