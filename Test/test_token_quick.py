"""
Quick Token Test - Paste your new token here to test immediately
"""

import requests
import json

# PASTE YOUR NEW TOKEN HERE:
NEW_TOKEN = "PASTE_YOUR_NEW_TOKEN_HERE"

# Or load from config file
try:
    with open('vimeo_api_config.json', 'r') as f:
        config = json.load(f)
        if NEW_TOKEN == "PASTE_YOUR_NEW_TOKEN_HERE":
            NEW_TOKEN = config['access_token']
except:
    pass

print("=" * 60)
print("Quick Token Test")
print("=" * 60)
print()

if NEW_TOKEN == "PASTE_YOUR_NEW_TOKEN_HERE":
    print("❌ No token provided!")
    print()
    print("Option 1: Edit this file and paste token at line 9")
    print("Option 2: Update vimeo_api_config.json")
    exit(1)

print(f"Testing token: {NEW_TOKEN[:20]}... (length: {len(NEW_TOKEN)})")
print()

# Test API call
headers = {
    'Authorization': f'Bearer {NEW_TOKEN}',
    'Accept': 'application/vnd.vimeo.*+json;version=3.4'
}

try:
    response = requests.get('https://api.vimeo.com/me', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! Token is valid!")
        print()
        print("-" * 60)
        print(f"👤 User: {data.get('name', 'N/A')}")
        print(f"🔗 Profile: {data.get('link', 'N/A')}")
        print(f"📧 Email: {data.get('email', 'N/A')}")
        print()
        
        quota = data.get('upload_quota', {})
        if quota:
            space = quota.get('space', {})
            total_mb = space.get('max', 0) / (1024*1024)
            used_mb = space.get('used', 0) / (1024*1024)
            free_mb = space.get('free', 0) / (1024*1024)
            
            print(f"💾 Total Quota: {total_mb:.1f} MB")
            print(f"📊 Used: {used_mb:.1f} MB ({used_mb/total_mb*100:.1f}%)")
            print(f"✅ Free: {free_mb:.1f} MB")
        print("-" * 60)
        print()
        print("🎉 You can now use Vimeo API!")
        print()
        print("Next steps:")
        print("1. Make sure this token is in vimeo_api_config.json")
        print("2. Run: python test_vimeo_api.py")
        print("3. Start uploading videos!")
        
    elif response.status_code == 401:
        print("❌ UNAUTHORIZED - Token is invalid!")
        print()
        print("Error:", response.json().get('error', 'Unknown error'))
        print()
        print("Solutions:")
        print("1. Go to https://developer.vimeo.com/apps")
        print("2. Select your app")
        print("3. Go to 'Authentication' tab")
        print("4. Generate NEW token with scopes:")
        print("   ✅ Public")
        print("   ✅ Private")
        print("   ✅ Upload")
        print("   ✅ Edit")
        print("   ✅ Video Files")
        print("5. Copy the NEW token (should be 50-100 characters)")
        print("6. Paste it in vimeo_api_config.json")
        
    else:
        print(f"❌ ERROR: {response.status_code}")
        print()
        print("Response:", response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()
