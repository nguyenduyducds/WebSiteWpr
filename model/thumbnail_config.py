"""
Thumbnail AI Configuration Manager
Lưu và load cấu hình AI cho thumbnail optimization
"""
import json
import os

class ThumbnailConfig:
    DEFAULT_CONFIG = {
        "output_resolution": "720p",  # 720p, 1080p
        "use_ai_upscale": False,
        "ai_upscale_threshold": 360,  # Chỉ dùng AI khi ảnh < 360p
        "use_face_restoration": False,
        "sharpen_strength": 0.5,  # 0.0 - 1.0
        "color_correction": True,
        "output_quality": 92,  # 1-100
        "content_image_height": 180  # Height for content images
    }
    
    def __init__(self, config_file="thumbnail_ai_config.json"):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self):
        """Load config from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new options added)
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except Exception as e:
                print(f"[THUMB_CONFIG] Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """Save config to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"[THUMB_CONFIG] ✅ Saved config to {self.config_file}")
            return True
        except Exception as e:
            print(f"[THUMB_CONFIG] ❌ Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set config value"""
        self.config[key] = value
    
    def reset_to_defaults(self):
        """Reset all settings to default"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
