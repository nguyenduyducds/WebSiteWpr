import requests
from bs4 import BeautifulSoup

def fetch_sslproxies(url="https://www.sslproxies.org/"):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = []
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) >= 7:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    https_support = cols[6].text.strip().lower()
                    if "yes" in https_support:
                        proxies.append(f"{ip}:{port}")
        return proxies
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def fetch_geonode():
    """Fetch from Geonode API"""
    try:
        # API returns JSON
        url = "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc&protocols=https"
        response = requests.get(url, timeout=10)
        data = response.json()
        proxies = []
        for item in data.get('data', []):
            ip = item.get('ip')
            port = item.get('port')
            if ip and port:
                proxies.append(f"{ip}:{port}")
        return proxies
    except Exception as e:
        print(f"Error fetching Geonode: {e}")
        return []

def fetch_proxyscrape():
    """Fetch from ProxyScrape API"""
    try:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=yes&anonymity=all"
        response = requests.get(url, timeout=10)
        proxies = []
        for line in response.text.split('\n'):
            line = line.strip()
            if line and ':' in line:
                proxies.append(line)
        return proxies
    except Exception as e:
        print(f"Error fetching ProxyScrape: {e}")
        return []

def get_free_proxies():
    """Aggregates proxies from multiple sources"""
    print("[PROXY_MOD] Starting multi-source fetch...")
    all_proxies = set()
    
    # 1. SSL Proxies
    p1 = fetch_sslproxies("https://www.sslproxies.org/")
    print(f"[PROXY_MOD] SSLProxies: {len(p1)}")
    all_proxies.update(p1)
    
    # 2. US Proxy
    p2 = fetch_sslproxies("https://www.us-proxy.org/")
    print(f"[PROXY_MOD] US-Proxy: {len(p2)}")
    all_proxies.update(p2)
    
    # 3. Geonode
    p3 = fetch_geonode()
    print(f"[PROXY_MOD] Geonode: {len(p3)}")
    all_proxies.update(p3)
    
    # 4. ProxyScrape (Replaces spys/others harder to scrape)
    p4 = fetch_proxyscrape()
    print(f"[PROXY_MOD] ProxyScrape: {len(p4)}")
    all_proxies.update(p4)
    
    final_list = list(all_proxies)
    print(f"[PROXY_MOD] Total Unique Proxies: {len(final_list)}")
    return final_list

def check_proxy_alive(proxy_str):
    """
    Check if a proxy is alive by connecting to a test URL.
    Returns True if alive, False otherwise.
    Timeout is set to 5 seconds to be quick.
    """
    try:
        parts = proxy_str.strip().split(':')
        
        # Construct proxy dict for requests
        if len(parts) == 4:
            ip, port, user, pwd = parts
            proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
        elif len(parts) == 2:
            ip, port = parts
            proxy_url = f"http://{ip}:{port}"
        else:
            return False
            
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        # Test connection - Google is reliable, or httpbin for IP check
        # verification=False to avoid SSL cert errors on some proxies, though risky for MITM it proves 'aliveness'
        response = requests.get("https://www.google.com", proxies=proxies, timeout=5)
        
        if response.status_code == 200:
            return True
            
    except:
        pass
        
    return False

if __name__ == "__main__":
    print("Đang lấy danh sách proxy miễn phí...")
    proxy_list = get_free_proxies()
    print(f"Tìm thấy {len(proxy_list)} proxy.")
    for p in proxy_list[:5]:
        print(p)