"""
Test Facebook Thumbnail Optimizer
Demo tính năng tối ưu hóa ảnh cho Facebook
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.facebook_thumbnail_optimizer import FacebookThumbnailOptimizer


def test_optimize_image():
    """Test tối ưu hóa ảnh cho Facebook"""
    
    print("=" * 70)
    print("FACEBOOK THUMBNAIL OPTIMIZER - TEST")
    print("=" * 70)
    print()
    
    # Initialize optimizer
    optimizer = FacebookThumbnailOptimizer()
    
    print("📋 Yêu cầu Facebook cho Open Graph Image:")
    print("   - Kích thước khuyến nghị: 1200x630px (tỷ lệ 1.91:1)")
    print("   - Kích thước tối thiểu: 200x200px")
    print("   - Kích thước tối đa file: 8MB")
    print("   - Định dạng: JPG, PNG")
    print()
    
    # Test with sample image
    test_image = input("Nhập đường dẫn ảnh để test (hoặc Enter để bỏ qua): ").strip()
    
    if test_image and os.path.exists(test_image):
        print()
        print("🔄 Đang tối ưu hóa ảnh...")
        print()
        
        # Validate before optimization
        print("📊 Kiểm tra ảnh gốc:")
        is_valid, issues = optimizer.validate_facebook_requirements(test_image)
        print()
        
        # Optimize
        optimized_path = optimizer.optimize_for_facebook(
            test_image,
            enhance=True  # Tăng độ nét, tương phản, màu sắc
        )
        
        if optimized_path:
            print()
            print("📊 Kiểm tra ảnh đã tối ưu:")
            is_valid, issues = optimizer.validate_facebook_requirements(optimized_path)
            print()
            
            print("=" * 70)
            print("✅ HOÀN TẤT!")
            print("=" * 70)
            print(f"Ảnh gốc: {test_image}")
            print(f"Ảnh đã tối ưu: {optimized_path}")
            print()
            print("🎯 Cải thiện:")
            print("   ✅ Resize về 1200x630px (tỷ lệ Facebook tối ưu)")
            print("   ✅ Tăng độ nét (sharpness +30%)")
            print("   ✅ Tăng độ tương phản (contrast +10%)")
            print("   ✅ Tăng độ bão hòa màu (color +10%)")
            print("   ✅ Nén JPEG chất lượng cao (95%)")
            print("   ✅ Progressive JPEG (load nhanh hơn)")
            print()
            print("📱 Kết quả:")
            print("   - Facebook sẽ ưu tiên hiển thị ảnh này")
            print("   - Ảnh sẽ rõ nét và đẹp hơn trên Facebook")
            print("   - Không bị mờ hay bị nén quá mức")
            print()
        else:
            print("❌ Tối ưu hóa thất bại!")
    else:
        print("⚠️ Không tìm thấy file hoặc bỏ qua test")
        print()
        print("💡 Hướng dẫn sử dụng:")
        print()
        print("```python")
        print("from model.facebook_thumbnail_optimizer import FacebookThumbnailOptimizer")
        print()
        print("# Khởi tạo")
        print("optimizer = FacebookThumbnailOptimizer()")
        print()
        print("# Tối ưu hóa ảnh")
        print("optimized_path = optimizer.optimize_for_facebook(")
        print("    'path/to/image.jpg',")
        print("    enhance=True  # Tăng chất lượng")
        print(")")
        print()
        print("# Kiểm tra yêu cầu Facebook")
        print("is_valid, issues = optimizer.validate_facebook_requirements('path/to/image.jpg')")
        print()
        print("# Tối ưu nhiều ảnh")
        print("optimized_paths = optimizer.batch_optimize([")
        print("    'image1.jpg',")
        print("    'image2.jpg',")
        print("    'image3.jpg'")
        print("])")
        print("```")
    
    print()
    print("=" * 70)
    print("📚 Tài liệu tham khảo:")
    print("   https://developers.facebook.com/docs/sharing/webmasters/images/")
    print("=" * 70)


def demo_batch_optimization():
    """Demo tối ưu hóa nhiều ảnh"""
    
    print()
    print("=" * 70)
    print("BATCH OPTIMIZATION DEMO")
    print("=" * 70)
    print()
    
    # Check if thumbnails folder exists
    thumbnails_dir = "thumbnails"
    if os.path.exists(thumbnails_dir):
        # Get all images in thumbnails folder
        image_files = [
            os.path.join(thumbnails_dir, f) 
            for f in os.listdir(thumbnails_dir) 
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ]
        
        if image_files:
            print(f"Tìm thấy {len(image_files)} ảnh trong thư mục thumbnails/")
            print()
            
            choice = input("Tối ưu hóa tất cả ảnh? (y/n): ").strip().lower()
            
            if choice == 'y':
                optimizer = FacebookThumbnailOptimizer()
                optimized_paths = optimizer.batch_optimize(image_files[:5])  # Limit to 5 for demo
                
                print()
                print(f"✅ Đã tối ưu {len(optimized_paths)} ảnh!")
                print(f"📁 Ảnh đã lưu trong: {optimizer.output_dir}/")
            else:
                print("Đã hủy")
        else:
            print("Không tìm thấy ảnh trong thư mục thumbnails/")
    else:
        print("Thư mục thumbnails/ không tồn tại")


if __name__ == "__main__":
    try:
        test_optimize_image()
        
        # Optional: Batch optimization demo
        demo_choice = input("\nChạy demo batch optimization? (y/n): ").strip().lower()
        if demo_choice == 'y':
            demo_batch_optimization()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã hủy bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
