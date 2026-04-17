"""
Version information for WprTool
"""

__version__ = "2.0.4"
__app_name__ = "WprTool - WordPress Auto Posting"
__author__ = "NguyenDuyDuc"
__copyright__ = "Copyright (C) 2026 NguyenDuyDuc"
__build_date__ = "2026-02-06"

# Version history
VERSION_HISTORY = {
    "2.0.4": {
        "date": "2026-02-06",
        "features": [
            "🤖 Tab AI Thumbnail với preview Before/After",
            "📱 Tự động phát hiện aspect ratio (9:16 dọc / 16:9 ngang)",
            "🖼️ Upload ảnh test và xem kết quả real-time",
            "⚙️ Cài đặt AI: Resolution, Upscale, Sharpen, Color",
            "📉 Giảm resolution ảnh content xuống 180px",
            "💾 Lưu config AI vào JSON để tái sử dụng",
        ]
    },
    "2.0.3": {
        "date": "2026-02-05",
        "features": [
            "✅ Icon riêng cho app (không trùng tool khác)",
            "✅ Hiển thị version trong giao diện",
            "✅ Nút 'Thông Tin' để xem version",
            "✅ Chức năng Copy Tất Cả Link với tiêu đề",
            "✅ Cải thiện UX và giao diện",
        ]
    },
    "2.0.2": {
        "date": "2026-02-05",
        "features": [
            "✅ Thêm 3 API ảnh (Unsplash + Pexels + Pixabay)",
            "✅ Hệ thống luân phiên API tự động",
            "✅ Tự động phát hiện tỷ lệ video Vimeo (9:16 hoặc 16:9)",
            "✅ Nút 'Thêm tất cả vào hàng chờ'",
            "✅ Cải thiện hiển thị video dọc Vimeo",
        ]
    },
    "2.0.1": {
        "date": "2026-01-30",
        "features": [
            "✅ Facebook Thumbnail Optimizer (1200x630px @ 95%)",
            "✅ Vimeo Thumbnail Quality Boost (100% JPEG)",
            "✅ Content Image Optimization (360p @ 55%)",
            "✅ Chrome Process Cleanup utility",
        ]
    },
    "2.0.0": {
        "date": "2026-01-25",
        "features": [
            "✅ Giao diện mới với CustomTkinter",
            "✅ Hỗ trợ đa nền tảng (Facebook, YouTube, Vimeo)",
            "✅ Tích hợp AI content generation",
            "✅ Batch posting từ CSV",
        ]
    }
}

def get_version():
    """Get current version string"""
    return __version__

def get_full_version():
    """Get full version info"""
    return f"{__app_name__} v{__version__}"

def get_version_info():
    """Get detailed version information"""
    current = VERSION_HISTORY.get(__version__, {})
    return {
        "version": __version__,
        "app_name": __app_name__,
        "author": __author__,
        "build_date": __build_date__,
        "features": current.get("features", [])
    }
