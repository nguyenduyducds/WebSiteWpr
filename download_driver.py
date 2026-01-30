import os
import shutil
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

print("Downloading ChromeDriver...")
# Install returns the path to the executable
driver_path = ChromeDriverManager().install()
print(f"Downloaded to: {driver_path}")

# Verify config
target_dir = os.path.join(os.getcwd(), "driver")
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

target_path = os.path.join(target_dir, "chromedriver.exe")

# Remove old
if os.path.exists(target_path):
    os.remove(target_path)

# Copy
print(f"Copying to {target_path}...")
shutil.copy2(driver_path, target_path)

# Check size
size = os.path.getsize(target_path)
print(f"File size: {size / 1024 / 1024:.2f} MB")

if size < 5 * 1024 * 1024:
    print("WARNING: File size is suspiciously small!")
else:
    print("SUCCESS: Driver downloaded and copied correctly.")
