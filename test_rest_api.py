"""Quick test for Facebook REST API"""
from model.facebook_rest_api import FacebookRestAPI

# Test URL
test_url = "https://www.facebook.com/watch/?v=1234567890"

print("Testing Facebook REST API...")
print(f"URL: {test_url}")
print()

# Initialize API
api = FacebookRestAPI(cookies_file="facebook_cookies.txt")

# Get info
result = api.get_video_info(test_url, timeout=10)

print()
print("=" * 60)
print("RESULT:")
print(f"  Success: {result['success']}")
print(f"  Title: {result['title']}")
print(f"  Thumbnail: {result['thumbnail']}")
print(f"  Video ID: {result['video_id']}")
print("=" * 60)
