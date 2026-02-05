"""
Test Vimeo Embed with Aspect Ratio Detection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from view.gui_view import GUIView

print("="*70)
print("TESTING VIMEO EMBED - ASPECT RATIO DETECTION")
print("="*70)

# Create a mock GUI instance
class MockController:
    pass

gui = GUIView(MockController())

# Test cases
test_videos = [
    ("1084537", "Horizontal Video (16:9)"),  # Example horizontal video
    ("76979871", "Vertical Video (9:16)"),   # Example vertical video
]

print("\n🎬 Testing Vimeo embed code generation:\n")

for video_id, description in test_videos:
    print(f"\n{'='*70}")
    print(f"Video ID: {video_id}")
    print(f"Description: {description}")
    print(f"{'='*70}\n")
    
    embed_code = gui.create_vimeo_embed(video_id, f"Test {description}")
    
    # Check if it's vertical (has max-width:400px)
    is_vertical = "max-width:400px" in embed_code
    
    print(f"✅ Embed code generated!")
    print(f"📊 Detected as: {'VERTICAL (9:16)' if is_vertical else 'HORIZONTAL (16:9)'}")
    print(f"\n📝 Embed Code Preview:")
    print("-" * 70)
    print(embed_code[:300] + "..." if len(embed_code) > 300 else embed_code)
    print("-" * 70)

print("\n" + "="*70)
print("✅ TEST COMPLETE!")
print("="*70)
print("\n💡 Tips:")
print("  - Vertical videos (9:16) will have max-width:400px and be centered")
print("  - Horizontal videos (16:9) will be full-width responsive")
print("  - The tool automatically detects aspect ratio from Vimeo API")
