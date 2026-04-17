#!/usr/bin/env python3
"""
Script tự động check các link đã đăng xem có lên được không
"""

import requests
import time
from datetime import datetime

def check_link_status(url, timeout=10):
    """
    Check xem link có accessible không
    Returns: (status_code, is_ok, message)
    """
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        status_code = response.status_code
        
        if status_code == 200:
            return status_code, True, "✅ OK"
        elif status_code == 404:
            return status_code, False, "❌ Not Found (404)"
        elif status_code == 403:
            return status_code, False, "❌ Forbidden (403)"
        elif status_code == 500:
            return status_code, False, "❌ Server Error (500)"
        else:
            return status_code, False, f"⚠️ Status {status_code}"
            
    except requests.exceptions.Timeout:
        return None, False, "⏱️ Timeout"
    except requests.exceptions.ConnectionError:
        return None, False, "🔌 Connection Error"
    except Exception as e:
        return None, False, f"❌ Error: {str(e)}"

def check_links_from_file(filename="published_links.txt"):
    """
    Đọc file chứa links và check từng link
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]
        
        if not links:
            print("❌ Không tìm thấy link nào trong file!")
            return
        
        print(f"🔍 Bắt đầu check {len(links)} links...")
        print("=" * 80)
        
        results = {
            'success': [],
            'failed': [],
            'total': len(links)
        }
        
        for idx, link in enumerate(links, 1):
            print(f"\n[{idx}/{len(links)}] Checking: {link}")
            
            status_code, is_ok, message = check_link_status(link)
            
            print(f"    → {message}")
            if status_code:
                print(f"    → Status Code: {status_code}")
            
            if is_ok:
                results['success'].append(link)
            else:
                results['failed'].append((link, message))
            
            # Delay giữa các request để tránh spam
            if idx < len(links):
                time.sleep(1)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 KẾT QUẢ TỔNG HỢP")
        print("=" * 80)
        print(f"✅ Thành công: {len(results['success'])}/{results['total']}")
        print(f"❌ Thất bại: {len(results['failed'])}/{results['total']}")
        
        if results['failed']:
            print("\n❌ DANH SÁCH LINK LỖI:")
            for link, msg in results['failed']:
                print(f"   • {link}")
                print(f"     {msg}")
        
        # Save report
        report_filename = f"link_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(f"Link Check Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total Links: {results['total']}\n")
            f.write(f"Success: {len(results['success'])}\n")
            f.write(f"Failed: {len(results['failed'])}\n\n")
            
            if results['success']:
                f.write("✅ SUCCESSFUL LINKS:\n")
                for link in results['success']:
                    f.write(f"   {link}\n")
                f.write("\n")
            
            if results['failed']:
                f.write("❌ FAILED LINKS:\n")
                for link, msg in results['failed']:
                    f.write(f"   {link}\n")
                    f.write(f"   → {msg}\n\n")
        
        print(f"\n💾 Report saved to: {report_filename}")
        
    except FileNotFoundError:
        print(f"❌ File '{filename}' không tồn tại!")
        print("💡 Tạo file published_links.txt và thêm các link cần check (mỗi link một dòng)")

def check_single_link(url):
    """Check một link đơn lẻ"""
    print(f"🔍 Checking: {url}")
    status_code, is_ok, message = check_link_status(url)
    print(f"   → {message}")
    if status_code:
        print(f"   → Status Code: {status_code}")
    return is_ok

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Check single link from command line
        url = sys.argv[1]
        check_single_link(url)
    else:
        # Check all links from file
        check_links_from_file()
