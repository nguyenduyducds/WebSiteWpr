"""
Test Classic Editor posting - bypasses all Gutenberg issues
"""
from model.selenium_wp import SeleniumWPClient
from dataclasses import dataclass

@dataclass
class BlogPost:
    title: str
    content: str
    image_url: str = ""

# Test configuration
SITE_URL = "spotlight.tfvp.org"  # or "bodycam.vansonnguyen.com"
USERNAME = "admin79"
PASSWORD = "your_password_here"

# Create test post
test_post = BlogPost(
    title="Test Classic Editor - " + str(int(__import__('time').time())),
    content="""
<h2>Test Post via Classic Editor</h2>
<p>This post was created using Classic Editor, bypassing all Gutenberg REST API issues.</p>

<div style="padding:56.25% 0 0 0;position:relative;">
<iframe src="https://player.vimeo.com/video/1152744141?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" 
frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media" 
style="position:absolute;top:0;left:0;width:100%;height:100%;" title="Test Video"></iframe>
</div>

<p>Video should appear above.</p>
""",
    image_url="thumbnails/thumb_1159503140.jpg"  # Update with actual path
)

print("=" * 60)
print("TESTING CLASSIC EDITOR POSTING")
print("=" * 60)

# Create client
client = SeleniumWPClient(SITE_URL, USERNAME, PASSWORD)

try:
    # Post using Classic Editor (default now)
    print("\n🎯 Posting via Classic Editor...")
    success, url = client.post_article(test_post, use_classic_editor=True)
    
    if success:
        print(f"\n✅ SUCCESS!")
        print(f"📝 Post URL: {url}")
        print(f"\n🔍 Please verify:")
        print(f"   1. Post is published (not draft)")
        print(f"   2. Title is correct")
        print(f"   3. Content displays properly")
        print(f"   4. Video embed works")
        print(f"   5. Featured image is set")
    else:
        print(f"\n❌ FAILED: {url}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Keep browser open for inspection
    input("\nPress Enter to close browser...")
    client.close()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
