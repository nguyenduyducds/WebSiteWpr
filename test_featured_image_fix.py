"""
Test featured image in default theme (theme="none")
"""

from model.wp_model import BlogPost

# Test 1: With raw content
print("=" * 60)
print("TEST 1: Raw content with featured image")
print("=" * 60)

post1 = BlogPost(
    title="Test Featured Image",
    video_url="https://player.vimeo.com/video/123456789",
    image_url="https://example.com/featured.jpg",
    raw_content="""
<!-- wp:paragraph -->
<p>This is paragraph 1.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This is paragraph 2.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>This is paragraph 3.</p>
<!-- /wp:paragraph -->
""",
    content_images=[]
)

post1.theme = "none"  # Use default theme
post1.generate_seo_content()

print("\nGenerated content preview (first 1000 chars):")
print(post1.content[:1000])
print("\n...")

# Check if featured image is in content
if post1.image_url in post1.content:
    print("\n✅ PASS: Featured image URL found in content")
else:
    print("\n❌ FAIL: Featured image URL NOT found in content")

# Test 2: Auto-generated content
print("\n" + "=" * 60)
print("TEST 2: Auto-generated content with featured image")
print("=" * 60)

post2 = BlogPost(
    title="Auto Generated Test",
    video_url="https://player.vimeo.com/video/987654321",
    image_url="https://example.com/auto-featured.jpg",
    raw_content="",  # Empty = auto-generate
    content_images=[]
)

post2.theme = "none"  # Use default theme
post2.generate_seo_content()

print("\nGenerated content preview (first 1000 chars):")
print(post2.content[:1000])
print("\n...")

# Check if featured image is in content
if post2.image_url in post2.content:
    print("\n✅ PASS: Featured image URL found in auto-generated content")
else:
    print("\n❌ FAIL: Featured image URL NOT found in auto-generated content")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("Featured images should now appear at the TOP of content")
print("when using theme='none' (default raw HTML mode)")
