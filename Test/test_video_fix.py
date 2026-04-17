from model.theme_manager import ThemeManager
import os

# Create dummy templates dir if strictly needed, but ThemeManager handles missing files gracefully (loaded as generic).
# So just run.

def test():
    print("Initializing ThemeManager...")
    try:
        tm = ThemeManager()
    except Exception as e:
        print(f"Init failed: {e}")
        return

    print("\n--- TEST CASE 1: Raw Iframe Input (Simulating GitHub/YT Embed) ---")
    iframe_input = '<iframe width="560" height="315" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    
    # Run the function
    result = tm.generate_video_embed(iframe_input)
    
    print(f"INPUT LENGTH: {len(iframe_input)}")
    print(f"OUTPUT: {result}")
    
    # Validation
    if 'src="<iframe' in result:
        print("❌ FAIL: DOUBLE WRAP DETECTED! (Broken HTML)")
    elif '<div class="video-wrapper"><iframe' in result:
        print("✅ PASS: Correctly detected HTML and wrapped it in div.")
    else:
        print("❓ WARNING: Unexpected output format.")

    print("\n--- TEST CASE 2: Standard URL Input ---")
    url_input = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result2 = tm.generate_video_embed(url_input)
    if 'src="https://www.youtube.com/embed/' in result2 and not '<iframe' in result2.split('src=')[1]:
         print("✅ PASS: Correctly converted URL to Embed.")
    else:
         print(f"❌ FAIL: URL Conversion failed. Output: {result2}")

if __name__ == "__main__":
    test()
