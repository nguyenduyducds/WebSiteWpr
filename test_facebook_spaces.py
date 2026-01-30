"""
Test Facebook iframe NO SPACES - Facebook blocks if there are spaces!
"""

def test_facebook_iframe_no_spaces():
    """Test that Facebook iframe has NO spaces between attributes (Facebook requirement)"""
    
    from urllib.parse import quote
    
    fb_url = "https://www.facebook.com/reel/2412419815845658/"
    encoded_url = quote(fb_url, safe='')
    
    # CORRECT format - NO SPACES between attributes (Facebook blocks otherwise)
    embed_code = (
        f'<div style="max-width:500px;margin:0 auto;">'
        f'<iframe src="https://www.facebook.com/plugins/video.php?height=800&href={encoded_url}&show_text=true&width=500&t=0"'
        f'width="500"'
        f'height="800"'
        f'style="border:none;overflow:hidden"'
        f'scrolling="no"'
        f'frameborder="0"'
        f'allowfullscreen="true"'
        f'allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"'
        f'allowFullScreen="true">'
        f'</iframe>'
        f'</div>'
    )
    
    print("=" * 80)
    print("FACEBOOK IFRAME NO-SPACE TEST")
    print("=" * 80)
    print("\nGenerated embed code:")
    print(embed_code)
    print("\n" + "=" * 80)
    
    # Check that attributes are concatenated (NO spaces)
    checks = [
        ('&t=0"width=', 'src and width concatenated'),
        ('"500"height=', 'width and height concatenated'),
        ('"800"style=', 'height and style concatenated'),
        ('hidden"scrolling=', 'style and scrolling concatenated'),
        ('"no"frameborder=', 'scrolling and frameborder concatenated'),
        ('"0"allowfullscreen=', 'frameborder and allowfullscreen concatenated'),
        ('"true"allow=', 'allowfullscreen and allow concatenated'),
        ('web-share"allowFullScreen=', 'allow and allowFullScreen concatenated'),
    ]
    
    print("\nCONCATENATION CHECKS (should all PASS):")
    print("-" * 80)
    all_passed = True
    
    for pattern, description in checks:
        if pattern in embed_code:
            print(f"✅ PASS: {description} - found '{pattern}'")
        else:
            print(f"❌ FAIL: {description} - pattern '{pattern}' not found")
            all_passed = False
    
    # Check that there are NO spaces between attributes
    print("\nSPACE CHECKS (should all PASS - meaning NO spaces found):")
    print("-" * 80)
    
    bad_patterns = [
        ('&t=0" width=', 'Space between src and width'),
        ('"500" height=', 'Space between width and height'),
        ('"800" style=', 'Space between height and style'),
        ('hidden" scrolling=', 'Space between style and scrolling'),
        ('"no" frameborder=', 'Space between scrolling and frameborder'),
        ('"0" allowfullscreen=', 'Space between frameborder and allowfullscreen'),
        ('"true" allow=', 'Space between allowfullscreen and allow'),
        ('web-share" allowFullScreen=', 'Space between allow and allowFullScreen'),
    ]
    
    for pattern, description in bad_patterns:
        if pattern in embed_code:
            print(f"❌ FAIL: {description} - found space!")
            all_passed = False
        else:
            print(f"✅ PASS: {description} - no space found")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Format matches Facebook requirements!")
        print("   (NO spaces between attributes - Facebook won't block)")
    else:
        print("❌ SOME CHECKS FAILED - Review the format!")
    print("=" * 80)
    
    return embed_code

if __name__ == "__main__":
    result = test_facebook_iframe_no_spaces()
    
    print("\n\nFINAL OUTPUT (this should work on WordPress without FB blocking):")
    print("-" * 80)
    print(result)
    print("-" * 80)
    
    print("\n\nEXPECTED FORMAT (from user):")
    print("-" * 80)
    print('<iframesrc="https://www.facebook.com/plugins/video.php?height=476&href=https%3A%2F%2Fwww.facebook.com%2Freel%2F2412419815845658%2F&show_text=true&width=267&t=0"width="267"height="591"style="border:none;overflow:hidden"scrolling="no"frameborder="0"allowfullscreen="true"allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"allowFullScreen="true"></iframe>')
    print("-" * 80)

