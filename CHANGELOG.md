# 📋 WprTool Changelog

## 🚀 Version 2.1.2 - Publish Button Fix (28/01/2026)

### ✅ **Critical Fix:**
- **Fixed post not published issue** - Posts now properly published instead of staying as Draft
- **404 error resolved** - Posts are now accessible after publishing
- **Improved publish button detection** - 5 different strategies to ensure button is clicked
- **Better error handling** - Clear error messages instead of silent failures

### 🔧 **Technical Improvements:**
- **Publish Toggle:** Added ESC to close overlays, scroll to center, multiple click strategies
- **Publish Confirmation:** Retry up to 5 times with different selectors
- **Post Verification:** Check if post is actually published before returning success
- **Screenshot on Error:** Automatically saves screenshot when publish fails
- **Exception Raising:** Fails fast with clear error instead of continuing with Draft post

### 📝 **Affected Components:**
- `model/selenium_wp.py` - Completely rewritten publish logic
- Added `test_publish_fix.py` - Interactive test for publish functionality
- Added `check_post_status.py` - Tool to check post status in WordPress
- Added `FIX_PUBLISH_BUTTON_ISSUE.md` - Complete documentation

### 🎯 **User Impact:**
- No more "success" messages with 404 posts
- Posts are guaranteed to be Published or error is shown
- Easier debugging with screenshots
- More reliable batch posting

### 🐛 **Bug Fixed:**
**Issue:** Tool reported success but post returned 404 (Page Not Found)
**Cause:** Publish confirmation button not clicked, post stayed as Draft
**Solution:** Multiple strategies with retry logic and proper error handling

---

## 🚀 Version 2.1.1 - Title Paste Freeze Fix (28/01/2026)

### ✅ **Critical Fix:**
- **Fixed GUI freeze when pasting titles** - Tool no longer freezes when pasting Unicode text
- **Unicode character support** - Properly handles Spanish (ñ), Chinese (中文), Vietnamese, and all special characters
- **Async paste handling** - Non-blocking clipboard operations keep GUI responsive

### 🔧 **Technical Implementation:**
- **Custom paste handler** - `_handle_title_paste()` intercepts Ctrl+V events
- **Async insertion** - Uses `self.after()` to prevent main thread blocking
- **Safe insert helper** - `_safe_insert()` with error handling
- **Fallback support** - Default behavior still works if custom handler fails

### 📝 **Affected Components:**
- `view/gui_view.py` - Added paste handler and safe insert method
- Title entry field now has custom Ctrl+V binding

### 🧪 **Testing:**
- Added `test_title_paste_fix.py` - Interactive test for paste functionality
- Added `validate_fix.py` - Automated validation of fix implementation
- Added `FIX_TITLE_PASTE_FREEZE.md` - Complete technical documentation

### 🎯 **User Impact:**
Users can now paste any title without freezing, including:
- Spanish: "Militar eng4ño su esposo" ✅
- Chinese: "中文标题" ✅
- Vietnamese: "Tiêu đề tiếng Việt" ✅
- All Unicode characters ✅

---

## 🚀 Version 2.1.0 - Video Embed Fix (27/01/2026)

### ✅ **Major Fixes:**
- **Fixed video embed issue** - Videos now display properly on WordPress
- **Improved video processing** - Better handling of iframe codes and URLs
- **Fixed GUI content handling** - Raw content field now works correctly
- **Enhanced responsive video containers** - Better mobile compatibility

### 🎬 **Video Embed Improvements:**
- **Iframe code support** - Direct paste of `<iframe>` embed codes
- **URL support** - Vimeo, YouTube, Facebook URLs auto-convert
- **Responsive containers** - Videos adapt to all screen sizes
- **Better error handling** - Clear debug messages for troubleshooting

### 🔧 **Technical Updates:**
- **Controller logic fix** - Proper handling of empty content fields
- **Video block generation** - Cleaner, more reliable HTML output
- **Chrome options fix** - Resolved compatibility issues
- **Debug tools added** - Multiple test scripts for troubleshooting

### 📚 **Documentation Added:**
- `VIDEO_EMBED_GUIDE.md` - Complete video embed troubleshooting guide
- `fix_thumbnail_issue.md` - Solutions for thumbnail-only display issues
- Debug scripts for testing video functionality

### 🎯 **Usage Changes:**
- **Content field**: Leave empty for auto-generation with video
- **Video URL field**: Supports both URLs and iframe codes
- **Better WordPress compatibility** - Works with more themes/plugins

---

## 📦 **Previous Versions:**

### Version 2.0.0 - Major Refactor
- Modern GUI with CustomTkinter
- Selenium-based posting
- Batch processing support
- Vimeo integration

### Version 1.x - Legacy
- Basic WordPress posting
- XML-RPC based
- Simple GUI

---

## 🔮 **Upcoming Features:**
- Plugin compatibility checker
- Theme-specific video embed modes
- Automatic WordPress settings optimization
- Video preview in GUI

---

*For support and troubleshooting, see the included guide files.*