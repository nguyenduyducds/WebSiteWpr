import undetected_chromedriver as uc
import time

# Cấu hình trình duyệt
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# Khởi tạo driver
driver = uc.Chrome(options=options, version_main=132)  # Thay 132 bằng phiên bản Chrome của bạn (xem bằng chrome://version)

try:
    print("Đang truy cập Vimeo...")
    driver.get("https://vimeo.com/join")
    
    # Đợi trang load
    time.sleep(5)
    
    # Kiểm tra xem có bị kẹt ở Cloudflare không
    if "Checking if the site connection is secure" in driver.title or "Verify to continue" in driver.page_source:
        print("⚠️ Vẫn bị Cloudflare. Vui lòng đợi hoặc giải CAPTCHA thủ công nếu hiện.")
        # Giữ trình duyệt mở để bạn can thiệp thủ công
        input("Nhấn Enter sau khi bạn đã vượt qua CAPTCHA...")
    else:
        print("✅ Đã vào được trang Vimeo!")

    # Tiếp tục làm việc...
    # Ví dụ: điền form, đăng ký, v.v.

finally:
    # Không đóng ngay — để bạn kiểm tra
    pass