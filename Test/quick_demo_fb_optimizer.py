"""
Quick Demo - Facebook Thumbnail Optimizer
"""

print("=" * 60)
print("FACEBOOK THUMBNAIL OPTIMIZER - QUICK DEMO")
print("=" * 60)
print()

try:
    from model.facebook_thumbnail_optimizer import FacebookThumbnailOptimizer
    print("✅ Module imported successfully!")
    print()
    
    # Initialize
    optimizer = FacebookThumbnailOptimizer()
    print(f"✅ Optimizer initialized!")
    print(f"   Output directory: {optimizer.output_dir}")
    print()
    
    # Show features
    print("📋 Features:")
    print(f"   - Facebook optimal size: {optimizer.FACEBOOK_OG_WIDTH}x{optimizer.FACEBOOK_OG_HEIGHT}px")
    print(f"   - JPEG quality: {optimizer.JPEG_QUALITY}%")
    print(f"   - Aspect ratio: {optimizer.FACEBOOK_ASPECT_RATIO}:1")
    print()
    
    print("🎯 Enhancements:")
    print("   - Sharpness: +30%")
    print("   - Contrast: +10%")
    print("   - Color saturation: +10%")
    print("   - Progressive JPEG")
    print("   - Alpha channel removal")
    print()
    
    print("✅ Module is ready to use!")
    print()
    print("Usage:")
    print("  optimized_path = optimizer.optimize_for_facebook('image.jpg', enhance=True)")
    print()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("Missing dependencies? Try:")
    print("  pip install Pillow requests")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
