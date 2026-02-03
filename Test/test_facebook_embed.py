"""
Test Facebook video embed conversion
"""

import re
from urllib.parse import quote

def convert_facebook_to_iframe(input_text):
    """Convert Facebook video URL to responsive iframe (500x800)"""
    
    if not input_text:
        return ""
    
    # Check if it's Facebook URL
    if 'facebook.com' not in input_text and 'fb.watch' not in input_text and 'fb.com' not in input_text:
        return input_text
    
    print(f"[TEST] Input: {input_text[:100]}...")
    
    # Extract the actual Facebook URL if it's in iframe already
    if '<iframe' in input_text:
        match = re.search(r'href=([^&\s]+)', input_text)
        if match:
            fb_url = match.group(1)
            # URL decode if needed
            fb_url = fb_url.replace('%3A', ':').replace('%2F', '/')
        else:
            # Try to extract from src
            match = re.search(r'src=["\']([^"\']+)["\']', input_text)
            if match:
                fb_url = match.group(1)
            else:
                fb_url = input_text
    else:
        fb_url = input_text.strip()
    
    # Ensure it's a full URL
    if not fb_url.startswith('http'):
        fb_url = 'https://' + fb_url
    
    print(f"[TEST] Extracted URL: {fb_url}")
    
    # URL encode for Facebook embed
    encoded_url = quote(fb_url, safe='')
    
    print(f"[TEST] Encoded URL: {encoded_url[:100]}...")
    
    # Create responsive Facebook iframe (500x800 for better visibility)
    fb_iframe = (
        f'<div style="max-width:500px;margin:0 auto;">'
        f'<iframe src="https://www.facebook.com/plugins/video.php?height=800&href={encoded_url}&show_text=true&width=500&t=0" '
        f'width="500" height="800" style="border:none;overflow:hidden" scrolling="no" frameborder="0" '
        f'allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share" '
        f'allowFullScreen="true"></iframe>'
        f'</div>'
    )
    
    return fb_iframe


# Test cases
print("=" * 80)
print("Facebook Video Embed Conversion Test")
print("=" * 80)
print()

test_cases = [
    # Test 1: Direct Facebook reel URL
    {
        "name": "Direct Facebook Reel URL",
        "input": "https://www.facebook.com/reel/2412419815845658/",
        "expected_width": "500",
        "expected_height": "800"
    },
    
    # Test 2: Facebook video URL
    {
        "name": "Facebook Video URL",
        "input": "https://www.facebook.com/watch/?v=123456789",
        "expected_width": "500",
        "expected_height": "800"
    },
    
    # Test 3: Existing iframe (should extract and recreate)
    {
        "name": "Existing Facebook Iframe",
        "input": '<iframe src="https://www.facebook.com/plugins/video.php?height=476&href=https%3A%2F%2Fwww.facebook.com%2Freel%2F2412419815845658%2F&show_text=true&width=267&t=0" width="267" height="591"></iframe>',
        "expected_width": "500",
        "expected_height": "800"
    },
    
    # Test 4: fb.watch short URL
    {
        "name": "fb.watch Short URL",
        "input": "https://fb.watch/abc123/",
        "expected_width": "500",
        "expected_height": "800"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}: {test['name']}")
    print("-" * 80)
    
    result = convert_facebook_to_iframe(test['input'])
    
    # Check if result is iframe
    if '<iframe' in result:
        print("✅ Result is iframe")
        
        # Check width
        if f'width="{test["expected_width"]}"' in result:
            print(f"✅ Width is {test['expected_width']}")
        else:
            print(f"❌ Width is NOT {test['expected_width']}")
        
        # Check height
        if f'height="{test["expected_height"]}"' in result:
            print(f"✅ Height is {test['expected_height']}")
        else:
            print(f"❌ Height is NOT {test['expected_height']}")
        
        # Check Facebook plugin URL
        if 'facebook.com/plugins/video.php' in result:
            print("✅ Uses Facebook plugin URL")
        else:
            print("❌ Does NOT use Facebook plugin URL")
        
        print()
        print("Result:")
        print(result[:200] + "...")
        
    else:
        print("❌ Result is NOT iframe")
        print(f"Result: {result}")
    
    print()
    print()

print("=" * 80)
print("Test Complete")
print("=" * 80)
