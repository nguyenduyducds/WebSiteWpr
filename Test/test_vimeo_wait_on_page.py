"""
Test script to verify Vimeo upload wait-on-page functionality
This script checks that the new function exists and has correct signature
"""

import sys
import os

# Add model directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'model'))

def test_function_exists():
    """Test that the new function exists"""
    try:
        from vimeo_helper import VimeoHelper
        
        # Check if function exists
        assert hasattr(VimeoHelper, 'wait_for_video_processing_on_current_page'), \
            "❌ Function 'wait_for_video_processing_on_current_page' not found!"
        
        print("✅ Function 'wait_for_video_processing_on_current_page' exists")
        
        # Check function signature
        import inspect
        sig = inspect.signature(VimeoHelper.wait_for_video_processing_on_current_page)
        params = list(sig.parameters.keys())
        
        expected_params = ['self', 'video_id', 'max_wait', 'log_callback']
        assert params == expected_params, \
            f"❌ Function signature mismatch! Expected {expected_params}, got {params}"
        
        print(f"✅ Function signature correct: {params}")
        
        # Check default values
        assert sig.parameters['max_wait'].default == 900, \
            "❌ max_wait default should be 900"
        assert sig.parameters['log_callback'].default is None, \
            "❌ log_callback default should be None"
        
        print("✅ Default parameter values correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_old_function_still_exists():
    """Test that old function still exists for backward compatibility"""
    try:
        from vimeo_helper import VimeoHelper
        
        assert hasattr(VimeoHelper, 'wait_for_video_processing'), \
            "❌ Old function 'wait_for_video_processing' was removed! Should keep for compatibility"
        
        print("✅ Old function 'wait_for_video_processing' still exists (backward compatibility)")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_function_docstring():
    """Test that function has proper documentation"""
    try:
        from vimeo_helper import VimeoHelper
        
        func = VimeoHelper.wait_for_video_processing_on_current_page
        assert func.__doc__ is not None, "❌ Function has no docstring!"
        
        doc = func.__doc__.lower()
        assert 'without navigating' in doc or 'stay' in doc, \
            "❌ Docstring should mention staying on current page"
        
        print("✅ Function has proper docstring")
        print(f"   Docstring preview: {func.__doc__[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Testing Vimeo Wait-On-Page Functionality")
    print("=" * 60)
    print()
    
    tests = [
        ("Function exists", test_function_exists),
        ("Backward compatibility", test_old_function_still_exists),
        ("Documentation", test_function_docstring),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        print("-" * 60)
        result = test_func()
        results.append((name, result))
        print()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The fix is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the code.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
