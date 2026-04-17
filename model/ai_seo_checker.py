"""
AI SEO Checker — phân tích & tối ưu bài WordPress đạt 100 điểm SEO
Sử dụng AntigravityDirectClient (modelAi.py) để gọi Gemini/Claude
"""
from __future__ import annotations

import re
import json
import html as html_lib
from urllib.parse import urlparse
from typing import Optional, Dict, Any
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _strip_tags(html_text: str) -> str:
    text = re.sub(r'<script[^>]*?>.*?</script>', ' ', html_text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*?>.*?</style>',  ' ', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html_lib.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def _find_tag_contents(html_text: str, tag: str) -> list:
    pattern = rf'<{tag}[^>]*>(.*?)</{tag}>'
    return re.findall(pattern, html_text, flags=re.DOTALL | re.IGNORECASE)


def _find_meta(html_text: str, name: str) -> str:
    patterns = [
        rf'<meta\s+name=["\']?{re.escape(name)}["\']?\s+content=["\']([^"\']*)["\'][^>]*/?>',
        rf'<meta\s+content=["\']([^"\']*)["\'][^>]*name=["\']?{re.escape(name)}["\']?[^>]*/?>',
        rf'<meta\s+property=["\']?{re.escape(name)}["\']?\s+content=["\']([^"\']*)["\'][^>]*/?>',
        rf'<meta\s+content=["\']([^"\']*)["\'][^>]*property=["\']?{re.escape(name)}["\']?[^>]*/?>',
    ]
    for pat in patterns:
        m = re.search(pat, html_text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ''


# ── Fetch ──────────────────────────────────────────────────────────

def fetch_html(url: str, timeout: int = 20) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
    }
    resp = requests.get(url, headers=headers, timeout=timeout, verify=False)
    resp.encoding = resp.apparent_encoding or 'utf-8'
    return resp.text


# ── Parse ─────────────────────────────────────────────────────────

def parse_seo_data(html: str, url: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {'url': url}

    # Title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    data['title']     = _strip_tags(title_match.group(1)) if title_match else ''
    data['title_len'] = len(data['title'])

    # Meta description
    data['meta_desc']     = _find_meta(html, 'description')
    data['meta_desc_len'] = len(data['meta_desc'])

    # Canonical
    cm = re.search(r'<link[^>]*rel=["\']?canonical["\']?[^>]*href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    data['canonical'] = cm.group(1) if cm else ''

    # OG tags
    data['og_title'] = _find_meta(html, 'og:title')
    data['og_desc']  = _find_meta(html, 'og:description')
    data['og_image'] = _find_meta(html, 'og:image')

    # H1-H3
    data['h1_list'] = [_strip_tags(h) for h in _find_tag_contents(html, 'h1')]
    data['h2_list'] = [_strip_tags(h) for h in _find_tag_contents(html, 'h2')]
    data['h3_list'] = [_strip_tags(h) for h in _find_tag_contents(html, 'h3')]
    data['h1_count'] = len(data['h1_list'])
    data['h2_count'] = len(data['h2_list'])
    data['h3_count'] = len(data['h3_list'])

    # Images
    img_tags = re.findall(r'<img([^>]+)>', html, re.IGNORECASE)
    imgs = []
    for tag_attrs in img_tags:
        src_m = re.search(r'src=["\']([^"\']+)["\']', tag_attrs, re.IGNORECASE)
        alt_m = re.search(r'alt=["\']([^"\']*)["\']', tag_attrs, re.IGNORECASE)
        src = src_m.group(1) if src_m else ''
        alt = alt_m.group(1) if alt_m else ''
        if src and not src.startswith('data:'):
            imgs.append({'src': src, 'alt': alt})
    data['images']     = imgs
    data['img_count']  = len(imgs)
    data['img_no_alt'] = sum(1 for img in imgs if not img['alt'].strip())

    # Links
    parsed_base = urlparse(url)
    links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
    internal, external = [], []
    for href, anchor in links:
        parsed = urlparse(href)
        if not parsed.scheme or parsed.netloc == parsed_base.netloc:
            internal.append({'href': href, 'anchor': _strip_tags(anchor)})
        elif parsed.scheme in ('http', 'https'):
            external.append({'href': href, 'anchor': _strip_tags(anchor)})
    data['internal_links'] = internal
    data['external_links'] = external

    # Body text + word count
    article_m = re.search(r'<(?:article|main)[^>]*>(.*?)</(?:article|main)>', html, re.DOTALL | re.IGNORECASE)
    body_html = article_m.group(1) if article_m else html
    data['body_text']  = _strip_tags(body_html)
    data['word_count'] = len(re.findall(r'\b\w+\b', data['body_text']))

    # Schema + Robots
    data['has_schema']  = bool(re.search(r'application/ld\+json', html, re.IGNORECASE))
    data['robots_meta'] = _find_meta(html, 'robots')

    return data


# ── Score ─────────────────────────────────────────────────────────

def score_seo(data: Dict[str, Any]) -> Dict[str, Any]:
    breakdown, issues, passed = [], [], []
    total = 0

    def add(name, points, max_pts, note, ok):
        nonlocal total
        total += points
        breakdown.append({'name': name, 'points': points, 'max': max_pts, 'note': note, 'ok': ok})
        if ok:
            passed.append(f"✅ {name}: {note}")
        else:
            issues.append(f"❌ {name}: {note}")

    tl = data.get('title_len', 0)
    if 50 <= tl <= 60:   add('Title', 15, 15, f"{tl} ký tự ✓", True)
    elif 30 <= tl < 70:  add('Title',  8, 15, f"{tl} ký tự (cần 50-60)", False)
    elif tl > 0:         add('Title',  3, 15, f"{tl} ký tự — chỉnh lại!", False)
    else:                add('Title',  0, 15, "Không có title!", False)

    ml = data.get('meta_desc_len', 0)
    if 120 <= ml <= 160: add('Meta Description', 15, 15, f"{ml} ký tự ✓", True)
    elif 80 <= ml < 200: add('Meta Description',  8, 15, f"{ml} ký tự (cần 120-160)", False)
    elif ml > 0:         add('Meta Description',  3, 15, f"{ml} ký tự — chỉnh lại!", False)
    else:                add('Meta Description',  0, 15, "Không có meta description!", False)

    h1c = data.get('h1_count', 0)
    if h1c == 1:   add('H1', 10, 10, "Có đúng 1 H1 ✓", True)
    elif h1c > 1:  add('H1',  4, 10, f"Có {h1c} H1 — chỉ nên có 1", False)
    else:          add('H1',  0, 10, "Không có H1!", False)

    h2c = data.get('h2_count', 0)
    h3c = data.get('h3_count', 0)
    if h2c >= 2:   add('H2/H3', 10, 10, f"{h2c} H2, {h3c} H3 ✓", True)
    elif h2c == 1: add('H2/H3',  5, 10, f"Chỉ {h2c} H2, cần ≥2", False)
    else:          add('H2/H3',  0, 10, "Không có H2!", False)

    wc = data.get('word_count', 0)
    if wc >= 1200: add('Nội dung', 10, 10, f"{wc} từ ✓", True)
    elif wc >= 800: add('Nội dung', 7, 10, f"{wc} từ (nên ≥1200)", False)
    elif wc >= 400: add('Nội dung', 4, 10, f"{wc} từ — quá ngắn!", False)
    else:           add('Nội dung', 0, 10, f"{wc} từ — cần viết thêm!", False)

    ic, no_alt = data.get('img_count', 0), data.get('img_no_alt', 0)
    if ic == 0:    add('Ảnh & Alt', 4, 10, "Không có ảnh", False)
    elif no_alt == 0: add('Ảnh & Alt', 10, 10, f"{ic} ảnh, đủ alt ✓", True)
    else:          add('Ảnh & Alt', max(0, 10 - no_alt * 3), 10, f"{no_alt}/{ic} ảnh thiếu alt!", False)

    ilc = len(data.get('internal_links', []))
    if ilc >= 3:   add('Internal Links', 5, 5, f"{ilc} links ✓", True)
    elif ilc >= 1: add('Internal Links', 2, 5, f"{ilc} link (cần ≥3)", False)
    else:          add('Internal Links', 0, 5, "Không có internal link!", False)

    elc = len(data.get('external_links', []))
    if elc >= 2:   add('External Links', 5, 5, f"{elc} links ✓", True)
    elif elc >= 1: add('External Links', 3, 5, f"{elc} link", False)
    else:          add('External Links', 0, 5, "Không có external link", False)

    if data.get('has_schema'):   add('Schema JSON-LD', 5, 5, "Có ✓", True)
    else:                        add('Schema JSON-LD', 0, 5, "Thiếu Schema!", False)

    og_ok = bool(data.get('og_title') and data.get('og_desc') and data.get('og_image'))
    add('Open Graph', 5 if og_ok else 2, 5, "Đủ OG tags ✓" if og_ok else "Thiếu OG tags", og_ok)

    if data.get('canonical'):    add('Canonical', 5, 5, "Có ✓", True)
    else:                        add('Canonical', 0, 5, "Thiếu canonical!", False)

    robots = data.get('robots_meta', '').lower()
    if 'noindex' in robots:      add('Robots', 0, 5, f"⚠️ Đang noindex!", False)
    else:                        add('Robots', 5, 5, "Index/Follow ✓", True)

    return {'score': min(100, total), 'breakdown': breakdown, 'issues': issues, 'passed': passed}


# ── AI Optimizer ──────────────────────────────────────────────────

SEO_SYSTEM_PROMPT = """Bạn là chuyên gia SEO WordPress hàng đầu Việt Nam.
Nhiệm vụ: Phân tích bài viết và đề xuất cải tiến để đạt 100 điểm SEO.
Trả lời bằng JSON hợp lệ theo đúng schema, không thêm text khác bên ngoài JSON."""


def build_ai_prompt(seo_data: Dict, score_result: Dict, keyword: str = '') -> str:
    issues_text = '\n'.join(score_result.get('issues', [])) or 'Không có vấn đề'
    h1 = seo_data.get('h1_list', [])
    h2 = seo_data.get('h2_list', [])
    return f"""Phân tích SEO cho bài WordPress:

URL: {seo_data.get('url', '')}
Điểm SEO hiện tại: {score_result.get('score', 0)}/100
Keyword chính: {keyword or '(tự xác định từ nội dung)'}

Thông tin hiện tại:
- Title ({seo_data.get('title_len',0)} ký tự): "{seo_data.get('title','')}"
- Meta Desc ({seo_data.get('meta_desc_len',0)} ký tự): "{seo_data.get('meta_desc','')}"
- H1: {h1[:2]}
- H2: {h2[:5]}
- Từ: {seo_data.get('word_count',0)} | Ảnh thiếu alt: {seo_data.get('img_no_alt',0)}/{seo_data.get('img_count',0)}
- Internal links: {len(seo_data.get('internal_links',[]))} | External: {len(seo_data.get('external_links',[]))}
- Schema: {seo_data.get('has_schema',False)} | Canonical: {bool(seo_data.get('canonical'))}

Vấn đề cần sửa:
{issues_text}

Nội dung (1000 từ đầu):
{seo_data.get('body_text','')[:2500]}

Trả về JSON (không kèm text khác), đầy đủ các field sau:
{{
  "optimized_title": "Title mới 50-60 ký tự có keyword",
  "optimized_meta_desc": "Meta description mới 120-160 ký tự",
  "suggested_keyword": "keyword chính",
  "h1_suggestion": "H1 tối ưu nếu cần thay",
  "h2_suggestions": ["H2 số 1", "H2 số 2", "H2 số 3", "H2 số 4"],
  "content_to_add": "300+ từ nội dung có giá trị thêm vào cuối bài, có keyword tự nhiên",
  "alt_text_suggestions": ["alt ảnh 1 có keyword", "alt ảnh 2", "alt ảnh 3"],
  "action_items": ["Bước 1", "Bước 2", "Bước 3", "Bước 4", "Bước 5"],
  "score_analysis": "Giải thích ngắn gọn tại sao điểm thấp và cần làm gì",
  "estimated_score_after": 97,
  "css_style": "/* CSS chuẩn FE dev cho bài viết WP, áp dụng vào .seo-post */ ... (viết đầy đủ, ídẹp, responsive, typography chuẩn)",
  "faq_block": "<div class=\"faq-block\">... HTML FAQ 3 câu hỏi liên quan keyword, đủ schema FAQPage ...</div>",
  "schema_override": "<script type=\"application/ld+json\">... JSON-LD Article/FAQPage đầy đủ ...</script>"
}}"""


def ai_analyze(url: str, ai_client, model: str = 'gemini-2.5-flash-preview',
               keyword: str = '', on_progress=None) -> Dict[str, Any]:
    """Full pipeline: fetch → parse → score → AI gợi ý."""
    result = {'seo_data': None, 'score_result': None, 'ai_suggestions': None, 'error': None}

    def prog(msg):
        print(f"[AI_SEO] {msg}")
        if on_progress: on_progress(msg)

    try:
        prog(f"🌐 Fetching: {url}")
        html = fetch_html(url)
        if len(html) < 500:
            result['error'] = "Trang quá ngắn hoặc không lấy được HTML!"; return result

        prog("🔍 Phân tích SEO...")
        seo_data = parse_seo_data(html, url)
        result['seo_data'] = seo_data

        prog("📊 Tính điểm...")
        score_result = score_seo(seo_data)
        result['score_result'] = score_result
        prog(f"📈 Điểm hiện tại: {score_result['score']}/100")

        prog("🤖 AI đang phân tích & đề xuất...")
        prompt = build_ai_prompt(seo_data, score_result, keyword)
        raw = ai_client.generate_text(
            model=model,
            system_prompt=SEO_SYSTEM_PROMPT,
            full_user_prompt=prompt
        )

        prog("✅ AI xong — đang parse kết quả...")
        m = re.search(r'\{[\s\S]*\}', raw)
        if m:
            try:
                result['ai_suggestions'] = json.loads(m.group(0))
                est = result['ai_suggestions'].get('estimated_score_after', '?')
                prog(f"🎯 Ước tính sau tối ưu: {est}/100")
            except json.JSONDecodeError:
                result['ai_suggestions'] = {'raw': raw}
                prog("⚠️ AI trả về text, không phải JSON chuẩn")
        else:
            result['ai_suggestions'] = {'raw': raw}
            prog("⚠️ Không tìm thấy JSON trong phản hồi AI")

    except Exception as e:
        import traceback
        result['error'] = str(e)
        traceback.print_exc()
        prog(f"❌ Lỗi: {e}")

    return result
