from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://your-wordpress-site.com/wp-admin/post.php?post=123&action=edit")

# Trích xuất _wpnonce từ HTML
nonce = driver.find_element(By.NAME, "_wpnonce").get_attribute("value")

# Gửi request với token
driver.execute_script("""
    const formData = new FormData();
    formData.append('_wpnonce', arguments[0]);
    formData.append('action', 'publish');
    
    fetch('/wp-admin/post.php', {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    });
""", nonce)