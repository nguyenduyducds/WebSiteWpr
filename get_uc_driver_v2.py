from undetected_chromedriver import Patcher
import shutil
import os

print("Fetching driver via Patcher...")
p = Patcher()
p.auto() # Downloads and patches

print(f"Executable path: {p.executable_path}")

if p.executable_path and os.path.exists(p.executable_path):
    size = os.path.getsize(p.executable_path)
    print(f"Size: {size/1024/1024:.2f} MB")
    
    target_dir = os.path.join(os.getcwd(), "driver")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    target_path = os.path.join(target_dir, "chromedriver.exe")
    
    shutil.copy2(p.executable_path, target_path)
    print(f"Success! Copied to {target_path}")
else:
    print("Failed to get executable path")
