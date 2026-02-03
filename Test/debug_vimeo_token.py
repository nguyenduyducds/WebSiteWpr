"""
Debug Vimeo API Token - Check what's wrong
"""

import json
import requests

# Load config
with open('vimeo_api_config.json', 'r') as f:
    config = json.load(f)

access_token = config['access_token']
client_id = config['client_id']
client_secret = config['client_secret']

print("=" * 60)
print("Vimeo API Token Debug")
print("=" * 60)
print()

print("Config loaded:")
print(f"  Access Token: {access_token[:20]}... (length: {len(access_token)})")
print(f"  Client ID: {client_id[:20]}...")
print(f"  Client Secret: {client_secret[:20]}...")
print()

# Test 1: Direct API call to /me
print("-" * 60)
print("Test 1: GET /me (user info)")
print("-" * 60)

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/vnd.vimeo.*+json;version=3.4'
}

try:
    response = requests.get('https://api.vimeo.com/me', headers=headers)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! User info:")
        print(f"  Name: {data.get('name')}")
        print(f"  Link: {data.get('link')}")
        print(f"  Account: {data.get('account')}")
        print()
        
        # Check quota
        quota = data.get('upload_quota', {})
        if quota:
            space = quota.get('space', {})
            print("Quota info:")
            print(f"  Total: {space.get('max', 0) / (1024*1024):.1f} MB")
            print(f"  Used: {space.get('used', 0) / (1024*1024):.1f} MB")
            print(f"  Free: {space.get('free', 0) / (1024*1024):.1f} MB")
        else:
            print("⚠️ No quota info in response")
        
    elif response.status_code == 401:
        print("❌ UNAUTHORIZED - Token is invalid or expired")
        print()
        print("Response:")
        print(response.text)
        print()
        print("Solutions:")
        print("1. Generate a new token at https://developer.vimeo.com/apps")
        print("2. Make sure to select these scopes:")
        print("   - Public")
        print("   - Private")
        print("   - Upload")
        print("   - Edit")
        print("   - Video Files")
        
    elif response.status_code == 403:
        print("❌ FORBIDDEN - Token doesn't have required scopes")
        print()
        print("Response:")
        print(response.text)
        print()
        print("Solution: Generate new token with more scopes")
        
    else:
        print(f"❌ ERROR: {response.status_code}")
        print()
        print("Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Check token format
print("-" * 60)
print("Test 2: Token Format Check")
print("-" * 60)

issues = []

if len(access_token) < 20:
    issues.append("Token too short (should be 30+ characters)")

if access_token.startswith('http'):
    issues.append("Token looks like a URL (should be alphanumeric string)")

if '/' in access_token or ':' in access_token:
    issues.append("Token contains invalid characters")

if not access_token.replace('-', '').replace('_', '').isalnum():
    issues.append("Token contains special characters (should be alphanumeric)")

if issues:
    print("⚠️ Token format issues:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ Token format looks OK")

print()

# Test 3: Try with PyVimeo library
print("-" * 60)
print("Test 3: PyVimeo Library Test")
print("-" * 60)

try:
    import vimeo
    
    client = vimeo.VimeoClient(
        token=access_token,
        key=client_id,
        secret=client_secret
    )
    
    print("✅ VimeoClient initialized")
    
    # Try to get user info
    response = client.get('/me')
    
    if response.status_code == 200:
        data = response.json()
        print("✅ GET /me successful via PyVimeo")
        print(f"  User: {data.get('name')}")
    else:
        print(f"❌ GET /me failed: {response.status_code}")
        print(f"  Response: {response.text}")
        
except ImportError:
    print("⚠️ PyVimeo not installed")
    print("  Run: pip install PyVimeo")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Debug Complete")
print("=" * 60)
