import undetected_chromedriver as uc
import shutil
import os
import time

print("Initializing UC to fetch driver...")
try:
    # Init driver (this triggers download/patch)
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    driver = uc.Chrome(options=options, use_subprocess=True)
    
    # Get executable path
    driver_path = driver.driver_executable_path
    print(f"UC Driver Path: {driver_path}")
    
    if driver_path and os.path.exists(driver_path):
        size = os.path.getsize(driver_path)
        print(f"Driver Size: {size/1024/1024:.2f} MB")
        
        # Copy to our folder
        target_dir = os.path.join(os.getcwd(), "driver")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        target_path = os.path.join(target_dir, "chromedriver.exe")
        
        shutil.copy2(driver_path, target_path)
        print(f"Copied to: {target_path}")
    
    driver.quit()
except Exception as e:
    print(f"Error: {e}")
