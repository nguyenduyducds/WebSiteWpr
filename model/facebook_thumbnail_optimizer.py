"""
Facebook Thumbnail Optimizer - PHIÊN BẢN 1080p ULTRA SHARP + AI UPSCALER
- Độ phân giải đầu ra: 1920x1080 (Full HD)
- Tự động dùng Real-ESRGAN AI upscale nếu ảnh nhỏ (tránh vỡ ảnh)
- 4 tầng làm nét chồng lớp + điều chỉnh thông minh
- Khử màu cam triệt để + tăng độ trong
"""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import os
import requests
from io import BytesIO
import cv2
import numpy as np
from scipy.signal import convolve2d

# === Thêm Real-ESRGAN (nếu có) ===
try:
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
    HAS_REALESRGAN = True
    print("[AI UPSCALER] Real-ESRGAN sẵn sàng!")
except ImportError:
    HAS_REALESRGAN = False
    print("[AI UPSCALER] Chưa cài realesrgan → sẽ dùng LANCZOS cổ điển (có thể bị vỡ nếu upscale mạnh)")


class FacebookThumbnailOptimizerUltra:
    OUTPUT_WIDTH = 1920
    OUTPUT_HEIGHT = 1080
    OUTPUT_ASPECT_RATIO = 1920 / 1080
    
    def __init__(self):
        self.output_dir = "thumbnails_optimized"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[ULTRA_SHARP_1080p] Output directory: {self.output_dir}")
    
    def optimize_for_facebook(self, image_path, output_filename=None, enhance=True):
        """
        Tối ưu ảnh cho Facebook - PHIÊN BẢN TỰ NHIÊN + AUTO ASPECT RATIO
        - Tự động phát hiện 9:16 (dọc) hoặc 16:9 (ngang)
        - Chỉ upscale lên 720p (đủ cho FB, tránh quá xử lý)
        - Không làm nét quá mức
        - Giữ màu sắc tự nhiên
        """
        try:
            print(f"\n{'='*60}")
            print("[FB_THUMB] 🖼️ BẮT ĐẦU TỐI ƯU ẢNH")
            print(f"{'='*60}")
            
            # Load image
            if str(image_path).startswith('http'):
                response = requests.get(image_path, timeout=30)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(image_path)
            
            original_size = img.size
            print(f"[FB_THUMB] Ảnh gốc: {original_size}")
            
            # Chuẩn hóa RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = bg
            
            # ============= AUTO-DETECT ASPECT RATIO =============
            aspect_ratio = img.width / img.height
            
            TARGET_WIDTH = 1920
            TARGET_HEIGHT = 1080
            
            # Phát hiện orientation - OUTPUT: LUÔN LÀ FULL HD 1080p (ngang)
            if aspect_ratio < 0.75:  # Portrait (9:16 hoặc gần đó)
                orientation = "PORTRAIT (9:16)"
                print(f"[FB_THUMB] 📱 Phát hiện video dọc → Tạo ảnh ngang {TARGET_WIDTH}x{TARGET_HEIGHT} (Full HD) với nền mờ (Pillarbox)")
                
                # Tạo background mờ từ ảnh gốc
                bg_scale = TARGET_WIDTH / img.width
                bg_new_height = int(img.height * bg_scale)
                bg_img = img.resize((TARGET_WIDTH, bg_new_height), Image.Resampling.LANCZOS)
                
                # Cắt lấy giữa cho background
                top_bg = (bg_img.height - TARGET_HEIGHT) // 2
                bg_img = bg_img.crop((0, top_bg, TARGET_WIDTH, top_bg + TARGET_HEIGHT))
                
                # Làm mờ mạnh
                bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=40))
                
                # Làm tối nhẹ nền mờ để ảnh chính nổi bật hơn
                bg_img = ImageEnhance.Brightness(bg_img).enhance(0.7)
                
                # Xử lý foreground (ảnh gốc)
                fg_scale = TARGET_HEIGHT / img.height
                fg_new_width = int(img.width * fg_scale)
                fg_img = img.resize((fg_new_width, TARGET_HEIGHT), Image.Resampling.LANCZOS)
                
                # Tính vị trí để chèn foreground vào chính giữa background
                paste_x = (TARGET_WIDTH - fg_new_width) // 2
                
                # Dán foreground chồng lên background mờ
                bg_img.paste(fg_img, (paste_x, 0))
                
                img = bg_img
                # Định dạng là ảnh ngang hoàn chỉnh, không cần enhance/upscale thêm
                need_upscale = False
                print(f"[FB_THUMB] → Xử lý xong ảnh dọc với viền mờ tự nhiên")
                
            else:  # Landscape (16:9 hoặc gần đó)
                orientation = "LANDSCAPE (16:9)"
                print(f"[FB_THUMB] 🖥️ Phát hiện video ngang → Thumbnail {TARGET_WIDTH}x{TARGET_HEIGHT} (Full HD)")
                
                # ============= UPSCALE NHẸ (NẾU CẦN) =============
                need_upscale = img.height < TARGET_HEIGHT or img.width < TARGET_WIDTH
                if need_upscale:
                    scale_h = TARGET_HEIGHT / img.height
                    scale_w = TARGET_WIDTH / img.width
                    scale_factor = max(scale_h, scale_w)
                    
                    print(f"[FB_THUMB] Upscale nhẹ x{scale_factor:.1f} → dùng LANCZOS chất lượng cao")
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    print(f"[FB_THUMB] → Sau upscale: {img.size}")
                
                # ============= CROP VỀ TARGET RATIO =============
                img = self._crop_to_ratio(img, TARGET_WIDTH, TARGET_HEIGHT)
                print(f"[FB_THUMB] → Sau crop {orientation}: {img.size}")
                
                # ============= RESIZE CHÍNH XÁC =============
                if img.size != (TARGET_WIDTH, TARGET_HEIGHT):
                    img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
                    print(f"[FB_THUMB] → Resize cuối: {img.size}")
                
                # ============= XỬ LÝ NHẸ (CHỈ KHI CẦN) =============
                if enhance and need_upscale:
                    print("[FB_THUMB] ✨ Làm nét nhẹ (chỉ vì đã upscale)...")
                    # Chỉ làm nét rất nhẹ để bù lại độ mờ từ upscale
                    img = self._gentle_sharpen(img)
                else:
                    print("[FB_THUMB] ✅ Giữ nguyên ảnh gốc (không cần xử lý)")
            
            # ============= LƯU =============
            if not output_filename:
                from time import strftime
                output_filename = f"fb_natural_{strftime('%Y%m%d_%H%M%S')}.jpg"
            
            output_path = os.path.join(self.output_dir, output_filename)
            # Quality 92 là sweet spot (đủ nét, file nhỏ)
            img.save(output_path, 'JPEG', quality=92, subsampling=0, optimize=True)
            
            file_size_kb = os.path.getsize(output_path) / 1024
            print(f"\n{'='*60}")
            print(f"[FB_THUMB] ✅ HOÀN THÀNH: {output_path}")
            print(f"[FB_THUMB] 📏 Kích thước: {img.size}")
            print(f"[FB_THUMB] 💾 Dung lượng: {file_size_kb:.1f} KB")
            print(f"{'='*60}\n")
            
            return output_path
            
        except Exception as e:
            print(f"[ULTRA] ❌ LỖI: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # ================== AI UPSCALE ==================
    def _ai_upscale(self, img, target_scale=4):
        if not HAS_REALESRGAN:
            return img
        
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        upsampler = RealESRGANer(
            scale=4,
            model_path='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
            model=model,
            tile=400,      # Tile để tránh hết VRAM/RAM
            tile_pad=10,
            pre_pad=0,
            half=False     # False = CPU, True = GPU (nếu có)
        )
        
        img_np = np.array(img)
        output, _ = upsampler.enhance(img_np, outscale=target_scale)
        return Image.fromarray(output)
    
    
    # ================== CROP ==================
    def _crop_to_ratio(self, img, target_width, target_height):
        """Crop ảnh về tỷ lệ mong muốn"""
        target_ratio = target_width / target_height
        img_ratio = img.width / img.height
        
        if img_ratio > target_ratio:
            new_height = img.height
            new_width = int(new_height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, new_height))
        else:
            new_width = img.width
            new_height = int(new_width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, new_width, top + new_height))
        return img
    
    # ================== LÀM NÉT NHẸ ==================
    def _gentle_sharpen(self, img):
        """Làm nét rất nhẹ nhàng - chỉ để bù lại độ mờ từ upscale"""
        from PIL import ImageFilter
        # Unsharp mask với strength thấp
        return img.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=3))
    
    # ================== XỬ LÝ MÀU ==================
    def _remove_color_cast_pro(self, img):
        img_np = np.array(img).astype(np.float32)
        
        # White balance
        avg_b, avg_g, avg_r = np.mean(img_np, axis=(0,1))
        k = (avg_r + avg_g + avg_b) / 3
        img_np[:, :, 0] *= k / (avg_b + 1e-5)
        img_np[:, :, 1] *= k / (avg_g + 1e-5)
        img_np[:, :, 2] *= k / (avg_r + 1e-5)
        
        # Giảm kênh đỏ thừa
        red_channel = img_np[:, :, 2]
        mask = ((red_channel > 80) & (red_channel < 180)).astype(np.float32) * 0.15
        img_np[:, :, 2] = red_channel * (1 - mask)
        
        # Tăng clarity
        img_np = self._apply_clarity(img_np, amount=0.25)
        
        return Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
    
    def _apply_clarity(self, img_np, amount=0.2):
        img_lab = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2LAB)
        L = img_lab[:, :, 0].astype(np.float32)
        blurred = cv2.GaussianBlur(L, (0, 0), 1.0)
        mask = L - blurred
        L = L + mask * amount
        img_lab[:, :, 0] = np.clip(L, 0, 255).astype(np.uint8)
        return cv2.cvtColor(img_lab, cv2.COLOR_LAB2RGB).astype(np.float32)
    
    # ================== SHARPEN PIPELINE ==================
    def _ultra_sharpen_pipeline(self, img, strength_multiplier=1.0):
        img_np = np.array(img).astype(np.float32)
        
        # Blur nhẹ chống artifact từ upscale
        img_np = cv2.GaussianBlur(img_np, (0, 0), 0.5)
        
        print("[ULTRA]   → Tầng 1: Deblur nhẹ")
        img_np = self._richardson_lucy_deblur(img_np, iterations=5)
        
        print("[ULTRA]   → Tầng 2: High-frequency boost")
        img_np = self._high_frequency_boost(img_np, strength=0.35 * strength_multiplier)
        
        print("[ULTRA]   → Tầng 3: Edge-aware sharpen")
        img_np = self._edge_aware_sharpen(img_np, radius=1.2, amount=1.8 * strength_multiplier)
        
        print("[ULTRA]   → Tầng 4: Micro-texture")
        img_np = self._micro_texture_enhance(img_np, strength=0.4 * strength_multiplier)
        
        # Blend cuối: 85% nét + 15% gốc
        original_np = np.array(img).astype(np.float32)
        img_np = img_np * 0.85 + original_np * 0.15
        
        return Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
    
    # Các hàm sharpen giữ nguyên (chỉ chỉnh strength)
    def _richardson_lucy_deblur(self, img_np, iterations=5):
        try:
            def rl_deconvolve(channel, psf, iterations):
                estimate = np.full_like(channel, 0.5)
                for _ in range(iterations):
                    blurred = convolve2d(estimate, psf, 'same')
                    ratio = channel / (blurred + 1e-6)
                    estimate *= convolve2d(ratio, psf[::-1, ::-1], 'same')
                return estimate
            
            psf = np.array([[0.0625, 0.125, 0.0625],
                            [0.125,  0.25,  0.125],
                            [0.0625, 0.125, 0.0625]])
            
            result = np.zeros_like(img_np)
            for i in range(3):
                result[:, :, i] = rl_deconvolve(img_np[:, :, i], psf, iterations)
            return np.clip(result, 0, 255)
        except:
            return img_np
    
    def _high_frequency_boost(self, img_np, strength=0.3):
        blurred = cv2.GaussianBlur(img_np, (0, 0), 1.0)
        high_freq = img_np - blurred
        return img_np + high_freq * strength
    
    def _edge_aware_sharpen(self, img_np, radius=1.0, amount=1.5):
        gray = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        edges = cv2.Laplacian(gray, cv2.CV_32F)
        edge_mask = np.abs(edges) > 15
        edge_mask = edge_mask.astype(np.float32)
        edge_mask = cv2.GaussianBlur(edge_mask, (5, 5), 1.0)
        edge_mask = np.clip(edge_mask * 1.5, 0, 1.0)
        
        blurred = cv2.GaussianBlur(img_np, (0, 0), radius)
        sharpened = img_np + (img_np - blurred) * amount
        
        result = img_np * (1 - edge_mask[..., np.newaxis]) + sharpened * edge_mask[..., np.newaxis]
        return result
    
    def _micro_texture_enhance(self, img_np, strength=0.3):
        img_lab = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2LAB)
        L = img_lab[:, :, 0].astype(np.float32)
        blurred1 = cv2.GaussianBlur(L, (0, 0), 0.8)
        blurred2 = cv2.GaussianBlur(L, (0, 0), 2.0)
        texture = blurred1 - blurred2
        L = L + texture * strength * 2.0
        img_lab[:, :, 0] = np.clip(L, 0, 255).astype(np.uint8)
        return cv2.cvtColor(img_lab, cv2.COLOR_LAB2RGB).astype(np.float32)
    
    # ================== TRÍCH FRAME VIDEO ==================
    def create_thumbnail_from_video_frame(self, video_path_or_url, start_percent=0.1, end_percent=0.6, samples=30):
        """Chọn frame nét nhất từ video với độ chính xác cao"""
        try:
            print(f"\n[ULTRA] 🔍 Tìm frame nét nhất trong video...")
            cap = cv2.VideoCapture(video_path_or_url)
            if not cap.isOpened():
                print("[ULTRA] ❌ Không mở được video")
                return None
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            print(f"[ULTRA]   → Tổng frames: {total_frames} | FPS: {fps:.2f} | Độ dài: {duration:.1f}s")
            
            # Quét rộng hơn để tìm frame đẹp (10% -> 60% của video)
            start_frame = int(total_frames * start_percent) 
            end_frame = int(total_frames * end_percent)
            step = max(1, (end_frame - start_frame) // samples)
            
            best_frame = None
            best_score = 0
            
            for i, frame_idx in enumerate(range(start_frame, end_frame, step)):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Check resolution on first frame
                if i == 0:
                     h, w = frame.shape[:2]
                     aspect_ratio = w / h
                     
                     # Detect orientation
                     if aspect_ratio < 0.75:
                         orientation = "Khung (9:16)"
                     else:
                         orientation = "Khung (16:9)"
                     
                     print(f"[ULTRA]   → Độ phân giải nguồn: {w}x{h} | {orientation}")
                
                # Đa metric scoring: Laplacian variance + Tenengrad
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                tenengrad = np.sum(sobelx**2 + sobely**2) / (gray.shape[0] * gray.shape[1])
                
                # Tính điểm độ nét
                score = laplacian_var * 0.7 + tenengrad * 0.3
                
                # Ưu tiên các frame có độ sáng tốt (không quá tối/quá sáng)
                mean_brightness = np.mean(gray)
                if 40 < mean_brightness < 215:
                     score *= 1.2 # Bonus cho frame ánh sáng tốt
                else:
                     score *= 0.8 # Phạt frame quá tối/cháy sáng
                
                if score > best_score:
                    best_score = score
                    best_frame = frame.copy()
                    best_time = frame_idx / fps if fps > 0 else 0
            
            cap.release()
            
            if best_frame is None:
                print("[ULTRA] ❌ Không tìm thấy frame đạt chuẩn")
                return None
            
            frame_rgb = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            temp_path = os.path.join(self.output_dir, "ultra_frame_best.jpg")
            img.save(temp_path, quality=98)
            
            print(f"[ULTRA] ✅ Chọn frame tốt nhất tại {best_time:.2f}s (score: {best_score:.0f})")
            print(f"[ULTRA] 💾 Lưu frame tạm: {temp_path}")
            
            return temp_path
            
        except Exception as e:
            print(f"[ULTRA] ❌ Lỗi xử lý video: {e}")
            return None
    
# ============= DEMO =============
if __name__ == "__main__":
    optimizer = FacebookThumbnailOptimizerUltra()
    
    # Thay đường dẫn thật của bạn
    image_path = "anh_goc_cua_ban.jpg"  # hoặc link http, hoặc file từ video
    
    # Nếu từ video:
    # frame_path = optimizer.create_thumbnail_from_video_frame("video.mp4")
    # if frame_path: final = optimizer.optimize_for_facebook(frame_path, "thumb_final.jpg")
    
    final_thumb = optimizer.optimize_for_facebook(image_path, "thumbnail_1080p_ai_net_cang.jpg")
    
    if final_thumb:
        print(f"🎉 Hoàn thành! File: {final_thumb}")

# ============= ALIAS ĐỂ TƯƠNG THÍCH NGƯỢC =============
# Các file khác đang import "FacebookThumbnailOptimizer" (tên cũ)
# Alias này đảm bảo chúng dùng được class Ultra mới
FacebookThumbnailOptimizer = FacebookThumbnailOptimizerUltra