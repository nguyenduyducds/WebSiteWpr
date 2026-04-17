import undetected_chromedriver as uc
import os

print("Testing headless UC...")
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# Path to portable if needed
chrome_path = os.path.join(os.getcwd(), "chrome_portable", "chrome.exe")
if os.path.exists(chrome_path): 
    options.binary_location = chrome_path

driver = uc.Chrome(options=options, version_main=144, headless=True)
driver.get("https://google.com")
print("Title:", driver.title)
driver.quit()
print("Success!")
