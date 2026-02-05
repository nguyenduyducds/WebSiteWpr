"""
Quick test for Image APIs
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.image_api import ImageAPI

print("="*60)
print("TESTING IMAGE APIs")
print("="*60)

api = ImageAPI()
query = "Ferrari supercar"

# Test 1: Unsplash
print("\n1. Testing Unsplash...")
try:
    results = api.search_car_images(query, count=3)
    print(f"   Result: {'✅ OK' if results else '❌ FAIL'} - {len(results)} images")
    if results:
        print(f"   Sample: {results[0][:60]}...")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Pexels
print("\n2. Testing Pexels...")
try:
    results = api.search_pexels_images(query, count=3)
    print(f"   Result: {'✅ OK' if results else '❌ FAIL'} - {len(results)} images")
    if results:
        print(f"   Sample: {results[0][:60]}...")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Pixabay
print("\n3. Testing Pixabay...")
try:
    results = api.search_pixabay_images(query, count=3)
    print(f"   Result: {'✅ OK' if results else '❌ FAIL'} - {len(results)} images")
    if results:
        print(f"   Sample: {results[0][:60]}...")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Multi-source rotation
print("\n4. Testing Multi-Source Rotation...")
for i in range(3):
    results = api.search_multi_source(f"{query} test{i}", count=2)
    print(f"   Request {i+1}: {'✅ OK' if results else '❌ FAIL'} - {len(results)} images (index: {api.current_api_index})")

# Test 5: Main function
print("\n5. Testing get_car_images_from_title...")
try:
    results = api.get_car_images_from_title("Ferrari F8 Tributo 2024", count=3)
    print(f"   Result: {'✅ OK' if results else '❌ FAIL'} - {len(results)} images")
    print(f"   Pool: {len(api.image_pool)}, Used: {len(api.used_images)}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("TEST COMPLETE!")
print("="*60)
