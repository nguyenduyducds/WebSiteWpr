import base64
import json
import urllib.request
import urllib.error

class GitHubUploader:
    def __init__(self, token, repo_owner, repo_name):
        """
        token: GitHub Personal Access Token (with repo permissions)
        repo_owner: GitHub username (e.g., 'nguyenduyducds')
        repo_name: Repository name (e.g., 'WebSiteWpr')
        """
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    
    def upload_file(self, file_path, commit_message="Update license keys"):
        """Upload a file to GitHub repository with retry on 409 Conflict"""
        import time
        for attempt in range(3):
            try:
                # Read file content
                with open(file_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                
                # Get current file SHA (if exists)
                file_name = file_path.split('\\')[-1].split('/')[-1]
                url = f"{self.api_base}/contents/{file_name}"
                
                sha = None
                try:
                    req = urllib.request.Request(url)
                    req.add_header('Authorization', f'token {self.token}')
                    req.add_header('Accept', 'application/vnd.github.v3+json')
                    
                    with urllib.request.urlopen(req, timeout=60) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        sha = data.get('sha')
                        print(f"[GITHUB] File tồn tại, SHA: {sha[:7]}...")
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        print("[GITHUB] File chưa tồn tại, sẽ tạo mới")
                    else:
                        print(f"[GITHUB] Lỗi khi lấy thông tin file: {e.code} {e.reason}")
                        # Continue anyway, try to upload
                except Exception as e:
                    print(f"[GITHUB] Cảnh báo khi lấy cấu hình file: {e}")
                
                # Prepare upload data
                upload_data = {
                    "message": commit_message,
                    "content": content,
                    "branch": "master"
                }
                
                if sha:
                    upload_data["sha"] = sha
                
                # Upload
                req = urllib.request.Request(
                    url,
                    data=json.dumps(upload_data).encode('utf-8'),
                    method='PUT'
                )
                req.add_header('Authorization', f'token {self.token}')
                req.add_header('Content-Type', 'application/json')
                req.add_header('Accept', 'application/vnd.github.v3+json')
                
                with urllib.request.urlopen(req, timeout=60) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    print(f"[GITHUB] Đã upload thành công: {result.get('commit', {}).get('message', 'OK')}")
                    return True, "Đã đồng bộ lên GitHub"
                    
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8') if e.fp else "Không có chi tiết lỗi"
                print(f"[GITHUB] Lỗi HTTP {e.code}: {e.reason}")
                print(f"[GITHUB] Chi tiết lỗi: {error_body}")
                if e.code == 409 and attempt < 2:
                    print(f"[GITHUB] Đang thử lại do lỗi 409 (lần {attempt + 1})...")
                    time.sleep(1)
                    continue
                return False, f"Lỗi HTTP {e.code}: {e.reason}"
            except Exception as e:
                print(f"[GITHUB] Ngoại lệ: {e}")
                return False, str(e)
        return False, "Exceeded retry instances"

    def download_file(self, file_path):
        """Download a file from GitHub repository and save it locally"""
        try:
            file_name = file_path.split('\\')[-1].split('/')[-1]
            url = f"{self.api_base}/contents/{file_name}?ref=master"
            
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'token {self.token}')
            req.add_header('Accept', 'application/vnd.github.v3+json')
            
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode('utf-8'))
                content = data.get('content', '')
                if content:
                    # Content is base64 encoded
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(decoded_content)
                    return True, "Đã tải file từ GitHub thành công"
                return False, "Không tìm thấy nội dung file"
                
        except Exception as e:
            return False, f"Lỗi khi tải file: {e}"
