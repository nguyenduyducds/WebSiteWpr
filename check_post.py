import sys, io, requests, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Check if WordPress outputs og:image meta tag
url = 'https://spotlight.tfvp.org/2431/26/'
resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
html = resp.text

# Find og:image
og_matches = re.findall(r'<meta\s+[^>]*property=["\']og:image["\'][^>]*>', html, re.IGNORECASE)
if og_matches:
    for m in og_matches:
        print(f"Found og:image: {m}")
        content = re.search(r'content=["\']([^"\']+)["\']', m)
        if content:
            print(f"  URL: {content.group(1)}")
else:
    print("NO og:image meta tag found!")
    
# Check twitter:image  
tw_matches = re.findall(r'<meta\s+[^>]*name=["\']twitter:image["\'][^>]*>', html, re.IGNORECASE)
if tw_matches:
    for m in tw_matches:
        print(f"Found twitter:image: {m}")
else:
    print("NO twitter:image meta tag found!")

# Check if featured image appears in the head section
head_match = re.search(r'<head>(.*?)</head>', html, re.DOTALL | re.IGNORECASE)
if head_match:
    head = head_match.group(1)
    if 'fb_natural' in head:
        print("\nFeatured image URL found in <head>!")
    elif '2427' in head:
        print("\nMedia ID 2427 found in <head>!")
    else:
        print("\nFeatured image NOT referenced in <head>")
        
# Find any image references for the featured image
if 'fb_natural_20260226_161639' in html:
    print("\nFeatured image URL IS in the page HTML")
else:
    print("\nFeatured image URL NOT found in page HTML at all!")

# Find the first image in content
first_img = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
if first_img:
    print(f"\nFirst <img> found: {first_img.group(1)[:100]}")
