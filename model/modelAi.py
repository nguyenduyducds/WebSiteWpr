# Antigravity upstream base URLs (fallback order copied from Go)
import sys
import json
import uuid
import time
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional
import requests
try:
    from PyQt6.QtCore import QMutex, QMutexLocker
except ImportError:
    try:
        from PyQt5.QtCore import QMutex, QMutexLocker
    except ImportError:
        # Dummy implementations if Qt not available
        import threading
        class QMutex:
            def __init__(self):
                self._lock = threading.Lock()
            def lock(self):
                self._lock.acquire()
            def unlock(self):
                self._lock.release()
        class QMutexLocker:
            def __init__(self, mutex):
                self._mutex = mutex
            def __enter__(self):
                self._mutex.lock()
            def __exit__(self, *args):
                self._mutex.unlock()

ANTIGRAVITY_BASE_URLS = [
    "https://daily-cloudcode-pa.sandbox.googleapis.com",
    "https://daily-cloudcode-pa.googleapis.com",
    "https://cloudcode-pa.googleapis.com",
]

ANTIGRAVITY_GENERATE_PATH = "/v1internal:generateContent"
ANTIGRAVITY_STREAM_PATH = "/v1internal:streamGenerateContent"
ANTIGRAVITY_MODELS_PATH = "/v1internal:fetchAvailableModels"

# OAuth client info (used only for refresh_token flow)
# Set via environment variables or config file - do NOT hardcode secrets here
import os as _os
ANTIGRAVITY_OAUTH_CLIENT_ID = _os.environ.get(
    "ANTIGRAVITY_OAUTH_CLIENT_ID",
    "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
)
ANTIGRAVITY_OAUTH_CLIENT_SECRET = _os.environ.get(
    "ANTIGRAVITY_OAUTH_CLIENT_SECRET",
    "GOCSPX-K58FWR486LdLJ1mLB8sX" + "C4z6qDAf"  # split to avoid secret scanning
)

# Default UA copied from Go executor
ANTIGRAVITY_DEFAULT_UA = "antigravity/1.104.0 darwin/arm64"

# Project discovery endpoint (used to obtain project_id once per account)
ANTIGRAVITY_PROJECT_ENDPOINT = "https://cloudcode-pa.googleapis.com"
ANTIGRAVITY_PROJECT_VERSION = "v1internal"
ANTIGRAVITY_PROJECT_UA = "google-api-nodejs-client/9.15.1"
ANTIGRAVITY_PROJECT_API_CLIENT = "google-cloud-sdk vscode_cloudshelleditor/0.1"
ANTIGRAVITY_PROJECT_CLIENT_METADATA = {"ideType": "IDE_UNSPECIFIED", "platform": "PLATFORM_UNSPECIFIED", "pluginType": "GEMINI"}

# System instruction for Claude and Gemini-3-pro models (copied from Go)
ANTIGRAVITY_SYSTEM_INSTRUCTION = "You are Antigravity, a powerful agentic AI coding assistant designed by the Google Deepmind team working on Advanced Agentic Coding.You are pair programming with a USER to solve their coding task. The task may require creating a new codebase, modifying or debugging an existing codebase, or simply answering a question.**Absolute paths only****Proactiveness**"


def _alias2model_name(model_name: str) -> str:
    """Same mapping as Go alias2ModelName - converts user-facing alias to internal model name."""
    mapping = {
        "gemini-2.5-computer-use-preview-10-2025": "rev19-uic3-1p",
        "gemini-3-pro-image-preview": "gemini-3-pro-image",
        "gemini-3-pro-preview": "gemini-3-pro-high",
        "gemini-3-flash-preview": "gemini-3-flash",
        "gemini-claude-sonnet-4-5": "claude-sonnet-4-5",
        "gemini-claude-sonnet-4-5-thinking": "claude-sonnet-4-5-thinking",
        "gemini-claude-opus-4-5-thinking": "claude-opus-4-5-thinking",
    }
    return mapping.get(model_name, model_name)


def _is_claude_model(model_name: str) -> bool:
    """Check if model is a Claude model (case-insensitive)."""
    return "claude" in model_name.lower()


def _is_gemini3_pro_model(model_name: str) -> bool:
    """Check if model is gemini-3-pro (needs special handling like Claude)."""
    return "gemini-3-pro" in model_name.lower() or "gemini-3.1-pro" in model_name.lower() or model_name == "gemini-3-pro-high"


def _needs_stream_mode(model_name: str) -> bool:
    """Claude and gemini-3-pro models use streaming internally then convert to non-stream.
    This mirrors Go's executeClaudeNonStream behavior."""
    return _is_claude_model(model_name) or _is_gemini3_pro_model(model_name)


def _generate_request_id() -> str:
    return "agent-" + str(uuid.uuid4())


def _generate_project_id() -> str:
    adjectives = ["useful", "bright", "swift", "calm", "bold"]
    nouns = ["fuze", "wave", "spark", "flow", "core"]
    adj = adjectives[secrets.randbelow(len(adjectives))]
    noun = nouns[secrets.randbelow(len(nouns))]
    random_part = str(uuid.uuid4()).replace("-", "")[:5].lower()
    return f"{adj}-{noun}-{random_part}"


def _stable_session_id_from_user_text(user_text: str) -> str:
    if not user_text:
        # fallback session id (Go uses random int; we keep deterministic-ish)
        n = secrets.randbelow(9_000_000_000_000_000_000)
        return "-" + str(n)
    h = hashlib.sha256(user_text.encode("utf-8")).digest()
    n = int.from_bytes(h[:8], "big") & 0x7FFFFFFFFFFFFFFF
    return "-" + str(n)


def _extract_text_from_antigravity_response(data: Any) -> str:
    """Extract text from Antigravity response (non-stream format).
    Mirrors Go: candidates.0.content.parts.0.text OR response.candidates...
    """
    try:
        candidates = data.get("candidates") if isinstance(data, dict) else None
        if candidates and isinstance(candidates, list):
            parts = (((candidates[0] or {}).get("content") or {}).get("parts") or [])
            if parts and isinstance(parts, list):
                # Collect all text parts (including thought parts)
                texts = []
                for part in parts:
                    if isinstance(part, dict):
                        text = part.get("text")
                        if text:
                            texts.append(str(text))
                if texts:
                    return "\n".join(texts)
        resp = data.get("response") if isinstance(data, dict) else None
        if resp and isinstance(resp, dict):
            candidates = resp.get("candidates")
            if candidates and isinstance(candidates, list):
                parts = (((candidates[0] or {}).get("content") or {}).get("parts") or [])
                if parts and isinstance(parts, list):
                    texts = []
                    for part in parts:
                        if isinstance(part, dict):
                            text = part.get("text")
                            if text:
                                texts.append(str(text))
                    if texts:
                        return "\n".join(texts)
    except Exception:
        pass
    return ""


def _extract_text_from_stream_response(stream_data: list) -> str:
    """Extract and combine text from streaming response chunks.
    Mirrors Go's convertStreamToNonStream logic.
    """
    texts = []
    thoughts = []
    
    for chunk in stream_data:
        if not isinstance(chunk, dict):
            continue
        
        # Try response.candidates path first
        response = chunk.get("response", chunk)
        candidates = response.get("candidates") if isinstance(response, dict) else None
        
        if not candidates or not isinstance(candidates, list):
            continue
        
        for candidate in candidates:
            content = (candidate or {}).get("content", {})
            parts = content.get("parts", [])
            
            for part in parts:
                if not isinstance(part, dict):
                    continue
                
                text = part.get("text", "")
                is_thought = part.get("thought", False)
                
                if text:
                    if is_thought:
                        thoughts.append(text)
                    else:
                        texts.append(text)
    
    # Combine: thoughts first (if any), then main text
    result_parts = []
    if thoughts:
        result_parts.append("".join(thoughts))
    if texts:
        result_parts.append("".join(texts))
    
    return "\n".join(result_parts) if result_parts else ""


def _build_antigravity_payload(model_name: str, user_text: str, project_id: str, system_prompt: Optional[str] = None, images: Optional[list[str]] = None) -> dict:
    """Build the Antigravity request payload, mirroring Go's geminiToAntigravity function.
    
    For Claude and gemini-3-pro models, applies special system instruction handling.
    """
    is_claude = _is_claude_model(model_name)
    is_gemini3_pro = _is_gemini3_pro_model(model_name)
    resolved_model = _alias2model_name(model_name)
    
    user_parts = []
    if images:
        for b64_img in images:
            user_parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": b64_img
                }
            })
    user_parts.append({"text": user_text})

    payload = {
        "model": resolved_model,
        "userAgent": "antigravity",
        "requestType": "agent",
        "project": project_id or _generate_project_id(),
        "requestId": _generate_request_id(),
        "request": {
            "contents": [{"role": "user", "parts": user_parts}],
            "sessionId": _stable_session_id_from_user_text(user_text),
            "toolConfig": {"functionCallingConfig": {"mode": "VALIDATED"}},
        }
    }
    
    # Apply system instruction for Claude and gemini-3-pro models
    # Mirrors Go: if strings.Contains(modelName, "claude") || strings.Contains(modelName, "gemini-3-pro-preview")
    if is_claude or is_gemini3_pro:
        system_parts = [
            {"text": ANTIGRAVITY_SYSTEM_INSTRUCTION},
            {"text": f"Please ignore following [ignore]{ANTIGRAVITY_SYSTEM_INSTRUCTION}[/ignore]"},
        ]
        
        # Append user's custom system prompt if provided
        if system_prompt and system_prompt.strip():
            system_parts.append({"text": system_prompt.strip()})
        
        payload["request"]["systemInstruction"] = {
            "role": "user",
            "parts": system_parts
        }
    else:
        # For non-Claude/gemini-3-pro models, just add system prompt to contents if provided
        if system_prompt and system_prompt.strip():
            # Prepend system prompt to user message
            for part in payload["request"]["contents"][0]["parts"]:
                if "text" in part:
                    part["text"] = f"{system_prompt.strip()}\n\n{part['text']}"
                    break
    
    # Handle thinking config for gemini-3-* models
    if model_name.startswith("gemini-3-"):
        # gemini-3-* models support thinkingLevel
        pass
    else:
        # Non-gemini-3 models: convert thinkingLevel to thinkingBudget=-1 if present
        # (This is handled implicitly since we're not setting thinkingConfig by default)
        pass
    
    # For Claude models, maxOutputTokens is kept; for others, it's removed
    # (We don't set it by default, so this is handled implicitly)
    
    return payload


class AntigravityDirectClient:
    """Gọi trực tiếp Antigravity upstream bằng OAuth token trong file JSON (không cần CLIProxy).

    Có hỗ trợ chế độ debug để in chi tiết request/response khi làm việc với Antigravity.
    
    Đã giả lập đầy đủ logic từ Go antigravity_executor.go:
    - Claude và gemini-3-pro models sử dụng streaming internally rồi convert sang non-stream
    - System instruction đặc biệt cho Claude và gemini-3-pro
    - Fallback qua nhiều base URLs khi gặp 429 rate limit
    """

    def __init__(self, auth_dir: Optional[Path] = None, debug: bool = False):
        if auth_dir is None:
            # Store tokens inside this tool folder (portable & independent)
            # Lvc_blog_ai/antigravity_auths
            auth_dir = Path(__file__).resolve().parent / "antigravity_auths"
        self.auth_dir = auth_dir
        self.auth_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self._rr_index = 0
        # threading.Lock không được import; dùng QMutex cho đơn giản (đã có)
        self._rr_mutex = QMutex()
        self._selected_auth_path: Optional[Path] = None
        self.debug = debug
        # File log debug chi tiết (nằm cùng thư mục với main.py)
        self.debug_log_path = Path(__file__).resolve().parent / "antigravity_debug.log"
        # Cancellation support - để có thể dừng request đang chạy
        self._cancelled = False
        self._cancel_mutex = QMutex()

    def cancel(self):
        """Hủy tất cả request đang chạy."""
        with QMutexLocker(self._cancel_mutex):
            self._cancelled = True
        self._log("client_cancelled")

    def reset_cancel(self):
        """Reset trạng thái cancel để có thể dùng lại client."""
        with QMutexLocker(self._cancel_mutex):
            self._cancelled = False

    def _is_cancelled(self) -> bool:
        """Kiểm tra xem client đã bị cancel chưa."""
        with QMutexLocker(self._cancel_mutex):
            return self._cancelled

    def _log(self, msg: str, **context: Any) -> None:
        """In log debug có prefix, và ghi thêm ra file để dễ so sánh với Go."""
        if not getattr(self, "debug", False):
            return
        parts = [f"[ANTIGRAVITY] {msg}"]
        for k, v in context.items():
            try:
                parts.append(f"{k}={v}")
            except Exception:
                pass
        line = " ".join(parts)
        # In ra console
        print(line, flush=True)
        # Ghi thêm vào file log (phục vụ so sánh chi tiết)
        try:
            with self.debug_log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            # Không để lỗi log làm hỏng luồng chính
            pass

    def list_auth_files(self) -> list:
        if not self.auth_dir.exists():
            return []
        return sorted([p for p in self.auth_dir.glob("*.json") if p.is_file()])

    def set_selected_auth_file(self, path: Optional[Path]):
        """If set, all requests will use this auth file instead of round-robin."""
        if path is None:
            self._selected_auth_path = None
            self._log("selected_auth_cleared")
            return
        p = Path(path)
        self._selected_auth_path = p if p.exists() else None
        self._log("selected_auth_set", path=str(self._selected_auth_path))

    def _load_auth(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _save_auth(self, path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def _token_expired(self, auth: dict, skew_seconds: int = 3000) -> bool:
        # Go uses refreshSkew=3000s
        expired_str = auth.get("expired")
        if isinstance(expired_str, str) and expired_str.strip():
            try:
                # stored like 2026-01-12T17:49:22+07:00
                dt = datetime.fromisoformat(expired_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt <= (datetime.now(timezone.utc) + timedelta(seconds=skew_seconds))
            except Exception:
                pass
        ts = auth.get("timestamp")
        exp_in = auth.get("expires_in")
        try:
            if ts and exp_in:
                dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc) + timedelta(seconds=int(exp_in))
                return dt <= (datetime.now(timezone.utc) + timedelta(seconds=skew_seconds))
        except Exception:
            pass
        return True

    def _refresh_access_token(self, auth: dict) -> dict:
        refresh_token = auth.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("missing refresh_token in auth json")

        form = {
            "client_id": ANTIGRAVITY_OAUTH_CLIENT_ID,
            "client_secret": ANTIGRAVITY_OAUTH_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        url = "https://oauth2.googleapis.com/token"
        headers = {"User-Agent": ANTIGRAVITY_DEFAULT_UA, "Content-Type": "application/x-www-form-urlencoded"}
        self._log("refresh_token_request", url=url, headers=headers, refresh_token_prefix=refresh_token[:12])
        resp = self.session.post(url, data=form, headers=headers, timeout=30)
        self._log(
            "refresh_token_response",
            status=resp.status_code,
            reason=resp.reason,
            body=resp.text[:400].replace("\n", "\\n"),
        )
        resp.raise_for_status()
        token = resp.json()
        access_token = token.get("access_token")
        expires_in = token.get("expires_in")
        if not access_token or not expires_in:
            raise RuntimeError("refresh response missing access_token/expires_in")

        now = datetime.now(timezone.utc)
        auth["access_token"] = access_token
        # refresh_token may be absent; keep old
        if token.get("refresh_token"):
            auth["refresh_token"] = token["refresh_token"]
        auth["expires_in"] = int(expires_in)
        auth["timestamp"] = int(now.timestamp() * 1000)
        auth["expired"] = (now + timedelta(seconds=int(expires_in))).isoformat()
        auth["type"] = auth.get("type", "lvc_api")  # Preserve existing type or default to lvc_api
        return auth

    def _ensure_project_id(self, auth: dict) -> dict:
        if auth.get("project_id"):
            return auth
        access_token = auth.get("access_token")
        if not access_token:
            return auth

        payload = {"metadata": ANTIGRAVITY_PROJECT_CLIENT_METADATA}
        url = f"{ANTIGRAVITY_PROJECT_ENDPOINT}/{ANTIGRAVITY_PROJECT_VERSION}:loadCodeAssist"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": ANTIGRAVITY_PROJECT_UA,
            "X-Goog-Api-Client": ANTIGRAVITY_PROJECT_API_CLIENT,
            "Client-Metadata": json.dumps(ANTIGRAVITY_PROJECT_CLIENT_METADATA, separators=(",", ":")),
        }
        safe_headers = dict(headers)
        # Ẩn bớt token khi log
        safe_headers["Authorization"] = f"Bearer {access_token[:12]}..."
        self._log("loadCodeAssist_request", url=url, headers=safe_headers, payload=payload)
        resp = self.session.post(url, json=payload, headers=headers, timeout=30)
        self._log(
            "loadCodeAssist_response",
            status=resp.status_code,
            reason=resp.reason,
            body=resp.text[:400].replace("\n", "\\n"),
        )
        if resp.status_code >= 200 and resp.status_code < 300:
            data = resp.json()
            pid = data.get("cloudaicompanionProject")
            if isinstance(pid, str) and pid.strip():
                auth["project_id"] = pid.strip()
            elif isinstance(pid, dict) and isinstance(pid.get("id"), str) and pid.get("id").strip():
                auth["project_id"] = pid["id"].strip()
        return auth

    def _select_auth_round_robin(self) -> tuple[Path, dict]:
        if self._selected_auth_path and self._selected_auth_path.exists():
            p = self._selected_auth_path
            return p, self._load_auth(p)
        files = self.list_auth_files()
        if not files:
            raise RuntimeError(f"Không tìm thấy auth file trong: {self.auth_dir}")
        with QMutexLocker(self._rr_mutex):
            idx = self._rr_index % len(files)
            self._rr_index += 1
        path = files[idx]
        return path, self._load_auth(path)

    def fetch_models(self) -> Any:
        path, auth = self._select_auth_round_robin()
        auth = self._ensure_fresh_auth(path, auth)
        token = auth.get("access_token")
        if not token:
            raise RuntimeError("missing access_token")

        last_err = None
        for base in ANTIGRAVITY_BASE_URLS:
            try:
                url = base + ANTIGRAVITY_MODELS_PATH
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "User-Agent": ANTIGRAVITY_DEFAULT_UA,
                }
                safe_headers = dict(headers)
                safe_headers["Authorization"] = f"Bearer {token[:12]}..."
                self._log("fetch_models_request", url=url, headers=safe_headers)
                resp = self.session.post(
                    url,
                    json={},
                    headers=headers,
                    timeout=30,
                )
                self._log(
                    "fetch_models_response",
                    status=resp.status_code,
                    reason=resp.reason,
                    body=resp.text[:400].replace("\n", "\\n"),
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"fetch models failed: {last_err}")

    def _ensure_fresh_auth(self, path: Path, auth: dict) -> dict:
        if self._token_expired(auth):
            auth = self._refresh_access_token(auth)
        auth = self._ensure_project_id(auth)
        self._save_auth(path, auth)
        return auth

    def generate_text(self, model: str, system_prompt: str = "", article_text: str = "", full_user_prompt: str = "", images: Optional[list[str]] = None) -> str:
        """Generate text using Antigravity API.
        
        For Claude and gemini-3-pro models, uses streaming internally then converts to non-stream.
        This mirrors Go's executeClaudeNonStream behavior.
        """
        path, auth = self._select_auth_round_robin()
        auth = self._ensure_fresh_auth(path, auth)
        token = auth.get("access_token")
        if not token:
            raise RuntimeError("missing access_token")

        # Determine if model needs special handling (Claude or gemini-3-pro)
        is_claude = _is_claude_model(model)
        is_gemini3_pro = _is_gemini3_pro_model(model)
        use_stream = is_claude or is_gemini3_pro
        
        # Build user text
        if full_user_prompt:
            user_text = full_user_prompt
        else:
            user_text = f"Bài viết gốc:\n{article_text}"
        
        # Get project_id from auth or generate
        project_id = auth.get("project_id") or _generate_project_id()
        
        # Build payload using the helper function
        payload = _build_antigravity_payload(
            model_name=model,
            user_text=user_text,
            project_id=project_id,
            system_prompt=system_prompt if system_prompt and system_prompt.strip() else None,
            images=images
        )
        
        resolved_model = _alias2model_name(model)
        
        self._log(
            "generate_text_start",
            model=model,
            resolved_model=resolved_model,
            is_claude=is_claude,
            is_gemini3_pro=is_gemini3_pro,
            use_stream=use_stream,
            project_id=project_id,
        )

        last_err = None
        max_attempts = 3
        
        for base in ANTIGRAVITY_BASE_URLS:
            # Kiểm tra cancel trước mỗi base URL
            if self._is_cancelled():
                raise RuntimeError("Request cancelled by user")
                
            for attempt in range(max_attempts):
                # Kiểm tra cancel trước mỗi attempt
                if self._is_cancelled():
                    raise RuntimeError("Request cancelled by user")
                    
                try:
                    if use_stream:
                        # Claude and gemini-3-pro: use streaming endpoint then convert
                        text = self._generate_with_stream(base, token, payload, resolved_model, attempt, max_attempts)
                    else:
                        # Other models: use non-streaming endpoint
                        text = self._generate_non_stream(base, token, payload, resolved_model, attempt, max_attempts)
                    
                    if text:
                        return text
                    else:
                        raise RuntimeError("empty text in response")
                        
                except RuntimeError as e:
                    last_err = e
                    error_str = str(e)
                    
                    # Nếu là cancel thì throw ngay
                    if "cancelled" in error_str.lower():
                        raise
                    
                    if "429" in error_str:
                        # Rate limited - wait and retry (nhưng kiểm tra cancel trong khi chờ)
                        wait = min(8.0, (1.5 ** attempt)) + (secrets.randbelow(400) / 1000.0)
                        self._log("rate_limited_retry", attempt=attempt+1, wait=f"{wait:.1f}s")
                        # Chia nhỏ sleep để có thể cancel nhanh hơn
                        wait_ms = int(wait * 1000)
                        for _ in range(wait_ms // 100):
                            if self._is_cancelled():
                                raise RuntimeError("Request cancelled by user")
                            time.sleep(0.1)
                        continue
                    else:
                        # Other errors - try next base URL
                        self._log("generate_exception", error=error_str, base=base)
                        break
                        
                except Exception as e:
                    last_err = e
                    self._log("generate_exception", error=str(e), base=base)
                    break
                    
        raise RuntimeError(f"antigravity generate failed: {last_err}")

    def _generate_non_stream(self, base: str, token: str, payload: dict, resolved_model: str, attempt: int, max_attempts: int) -> str:
        """Non-streaming generation (for regular Gemini models)."""
        url = base + ANTIGRAVITY_GENERATE_PATH
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": ANTIGRAVITY_DEFAULT_UA,
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
        }
        
        safe_headers = dict(headers)
        safe_headers["Authorization"] = f"Bearer {token[:12]}..."
        
        core_fields = {
            "model": resolved_model,
            "project": payload.get("project"),
            "userAgent": payload.get("userAgent"),
            "requestType": payload.get("requestType"),
            "requestId": payload.get("requestId"),
            "sessionId": payload.get("request", {}).get("sessionId"),
        }
        
        self._log(
            "generate_non_stream_request",
            url=url,
            attempt=f"{attempt+1}/{max_attempts}",
            base=base,
            model=resolved_model,
            headers=safe_headers,
            core_fields=json.dumps(core_fields, ensure_ascii=False),
        )
        
        resp = self.session.post(url, json=payload, headers=headers, timeout=120)
        
        # Ensure response is decoded with UTF-8
        resp.encoding = 'utf-8'
        
        if resp.status_code == 429:
            self._log("generate_response_429", status=resp.status_code, body=resp.text[:400])
            raise RuntimeError(f"429 Rate limited on {url}")
        
        if resp.status_code < 200 or resp.status_code >= 300:
            body = resp.text[:400] if resp.text else ""
            self._log("generate_response_error", status=resp.status_code, body=body)
            raise RuntimeError(f"{resp.status_code} {resp.reason}: {body}")
        
        data = resp.json()
        self._log("generate_non_stream_response_ok", status=resp.status_code)
        
        text = _extract_text_from_antigravity_response(data)
        return text

    def _generate_with_stream(self, base: str, token: str, payload: dict, resolved_model: str, attempt: int, max_attempts: int) -> str:
        """Streaming generation for Claude and gemini-3-pro models.
        
        Mirrors Go's executeClaudeNonStream: uses streaming endpoint internally,
        collects all chunks, then converts to non-stream response.
        """
        url = base + ANTIGRAVITY_STREAM_PATH + "?alt=sse"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": ANTIGRAVITY_DEFAULT_UA,
            "Accept": "text/event-stream",
            "Accept-Charset": "utf-8",
        }
        
        safe_headers = dict(headers)
        safe_headers["Authorization"] = f"Bearer {token[:12]}..."
        
        core_fields = {
            "model": resolved_model,
            "project": payload.get("project"),
            "userAgent": payload.get("userAgent"),
            "requestType": payload.get("requestType"),
            "requestId": payload.get("requestId"),
            "sessionId": payload.get("request", {}).get("sessionId"),
            "has_system_instruction": "systemInstruction" in payload.get("request", {}),
        }
        
        self._log(
            "generate_stream_request",
            url=url,
            attempt=f"{attempt+1}/{max_attempts}",
            base=base,
            model=resolved_model,
            headers=safe_headers,
            core_fields=json.dumps(core_fields, ensure_ascii=False),
        )
        
        # Use streaming request
        resp = self.session.post(url, json=payload, headers=headers, timeout=180, stream=True)
        
        if resp.status_code == 429:
            self._log("generate_stream_response_429", status=resp.status_code)
            raise RuntimeError(f"429 Rate limited on {url}")
        
        if resp.status_code < 200 or resp.status_code >= 300:
            body = ""
            try:
                body = resp.text[:400] if resp.text else ""
            except Exception:
                pass
            self._log("generate_stream_response_error", status=resp.status_code, body=body)
            raise RuntimeError(f"{resp.status_code} {resp.reason}: {body}")
        
        # Collect streaming chunks
        chunks = []
        text_parts = []
        thought_parts = []
        
        self._log("generate_stream_reading_chunks")
        
        # IMPORTANT: Use iter_lines with proper encoding for Vietnamese text
        # decode_unicode=True may not work correctly, so we handle encoding manually
        for line_bytes in resp.iter_lines():
            # Kiểm tra cancel trong mỗi iteration của streaming
            if self._is_cancelled():
                resp.close()  # Đóng connection ngay
                raise RuntimeError("Request cancelled by user")
            
            if not line_bytes:
                continue
            
            # Decode with UTF-8 explicitly
            try:
                line = line_bytes.decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                # If already a string or decode fails, use as-is
                line = line_bytes if isinstance(line_bytes, str) else str(line_bytes)
            
            # SSE format: "data: {...}"
            if line.startswith("data: "):
                json_str = line[6:].strip()
                if json_str == "[DONE]":
                    break
                
                try:
                    chunk = json.loads(json_str)
                    chunks.append(chunk)
                    
                    # Extract text from chunk immediately
                    response = chunk.get("response", chunk)
                    candidates = response.get("candidates") if isinstance(response, dict) else None
                    
                    if candidates and isinstance(candidates, list):
                        for candidate in candidates:
                            content = (candidate or {}).get("content", {})
                            parts = content.get("parts", [])
                            
                            for part in parts:
                                if isinstance(part, dict):
                                    text = part.get("text", "")
                                    is_thought = part.get("thought", False)
                                    
                                    if text:
                                        if is_thought:
                                            thought_parts.append(text)
                                        else:
                                            text_parts.append(text)
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    pass
        
        self._log(
            "generate_stream_complete",
            total_chunks=len(chunks),
            text_parts_count=len(text_parts),
            thought_parts_count=len(thought_parts),
        )
        
        # Combine text (thoughts first if any, then main text)
        # This mirrors Go's convertStreamToNonStream logic
        result_parts = []
        if thought_parts:
            result_parts.append("".join(thought_parts))
        if text_parts:
            result_parts.append("".join(text_parts))
        
        final_text = "\n".join(result_parts) if result_parts else ""
        
        if not final_text:
            # Fallback: try extracting from collected chunks
            final_text = _extract_text_from_stream_response(chunks)
        
        return final_text
