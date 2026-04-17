"""
Tab "Web Chuẩn SEO" - Tách ra file riêng để tránh gui_view.py quá dài.
Gồm 2 sub-tab:
  1. Kiểm Tra SEO URL
  2. Kế Hoạch Viết Bài (Pyramid: 1→3→5→5→5 bài/ngày)
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading, re, time, datetime, json, os

try:
    import requests
    requests.packages.urllib3.disable_warnings()
except ImportError:
    requests = None


# =============================================================================
# PHẦN 1: SEO URL CHECKER
# =============================================================================
def _analyze_seo(url: str) -> dict:
    r = {
        "url": url, "title": "", "title_len": 0,
        "meta_desc": "", "meta_desc_len": 0,
        "h1_count": 0, "h1_texts": [], "h2_count": 0,
        "canonical": "", "robots": "", "og_title": "",
        "og_desc": "", "og_image": "", "schema_types": [],
        "img_missing_alt": 0, "img_total": 0,
        "word_count": 0, "load_time_ms": 0,
        "https": url.startswith("https://"),
        "errors": [], "score": 0,
    }
    if not requests:
        r["errors"].append("Thiếu thư viện 'requests'. pip install requests")
        return r
    try:
        t0 = time.time()
        resp = requests.get(url.strip(), timeout=15, verify=False,
                            headers={"User-Agent": "Mozilla/5.0 (SEO-Bot/1.0)"})
        r["load_time_ms"] = int((time.time() - t0) * 1000)
        html = resp.text
    except Exception as e:
        r["errors"].append(f"Không tải được: {e}"); return r

    def _find(pattern, text, group=1, flags=re.IGNORECASE):
        m = re.search(pattern, text, flags)
        return m.group(group).strip() if m else ""

    r["title"] = re.sub(r"<[^>]+>", "", _find(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE|re.DOTALL))
    r["title_len"] = len(r["title"])
    r["meta_desc"] = _find(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html)
    if not r["meta_desc"]:
        r["meta_desc"] = _find(r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', html)
    r["meta_desc_len"] = len(r["meta_desc"])
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE|re.DOTALL)
    r["h1_count"] = len(h1s)
    r["h1_texts"] = [re.sub(r"<[^>]+>","",t).strip()[:80] for t in h1s][:2]
    r["h2_count"] = len(re.findall(r"<h2[^>]*>", html, re.IGNORECASE))
    r["canonical"] = _find(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](.*?)["\']', html)
    r["robots"] = _find(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'](.*?)["\']', html)
    r["og_title"] = _find(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', html)
    r["og_image"] = _find(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']', html)
    r["schema_types"] = list(set(re.findall(r'"@type"\s*:\s*"([^"]+)"', html)))[:5]
    imgs = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
    r["img_total"] = len(imgs)
    r["img_missing_alt"] = sum(1 for i in imgs if not re.search(r'alt=["\'][^"\']+["\']', i, re.IGNORECASE))
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    r["word_count"] = len(text.split())

    s = 0
    if 50 <= r["title_len"] <= 60: s += 15
    elif r["title_len"] > 0: s += 7
    if 120 <= r["meta_desc_len"] <= 160: s += 15
    elif r["meta_desc_len"] > 0: s += 7
    if r["h1_count"] == 1: s += 15
    elif r["h1_count"] > 1: s += 5
    if r["h2_count"] >= 2: s += 10
    if r["canonical"]: s += 10
    if r["og_title"] and r["og_image"]: s += 10
    if r["https"]: s += 10
    if r["schema_types"]: s += 10
    if r["img_total"] > 0:
        s += int((1 - r["img_missing_alt"]/r["img_total"]) * 5)
    r["score"] = min(s, 100)
    return r


def _score_color(score):
    if score >= 80: return "#10B981"
    if score >= 50: return "#F59E0B"
    return "#EF4444"


# =============================================================================
# PHẦN 2: SEO CONTENT GENERATOR (1000-2000 chữ chuẩn SEO)
# =============================================================================
def _gen_seo_article(keyword: str, extra_context: str = "") -> dict:
    """Tạo bài viết chuẩn SEO 1000-2000 chữ dựa trên keyword."""
    kw = keyword.strip()
    kw_lower = kw.lower()

    title = f"{kw} – Hướng Dẫn Chi Tiết Từ A Đến Z"
    meta_desc = f"Tìm hiểu tất cả về {kw}: định nghĩa, lợi ích, cách áp dụng hiệu quả và những lưu ý quan trọng nhất bạn cần biết."

    sections = [
        ("Tổng Quan", f"""
<p><strong>{kw}</strong> là một trong những chủ đề được tìm kiếm nhiều nhất hiện nay. 
Dù bạn là người mới tìm hiểu hay đã có kinh nghiệm, bài viết này sẽ cung cấp 
cho bạn cái nhìn toàn diện và chi tiết nhất về <strong>{kw}</strong>.</p>
<p>Trong bài viết này, chúng tôi sẽ đi qua các khía cạnh quan trọng: định nghĩa cơ bản, 
lợi ích thực tế, cách áp dụng đúng cách, và những sai lầm phổ biến cần tránh. 
Hãy cùng khám phá nhé!</p>
"""),
        (f"{kw} Là Gì?", f"""
<p><strong>{kw}</strong> có thể được hiểu là <em>một tập hợp các phương pháp, 
kiến thức và kỹ năng</em> liên quan đến lĩnh vực này. Đây là khái niệm ngày càng 
được nhiều người quan tâm do tầm quan trọng của nó trong cuộc sống hiện đại.</p>
<p>Theo các chuyên gia, {kw_lower} đóng vai trò then chốt trong việc:</p>
<ul>
<li>Nâng cao hiệu quả công việc và cuộc sống</li>
<li>Tiết kiệm thời gian và nguồn lực đáng kể</li>
<li>Mang lại kết quả bền vững và lâu dài</li>
<li>Tạo lợi thế cạnh tranh rõ ràng</li>
</ul>
<p>Hiểu rõ về {kw_lower} là bước đầu tiên quan trọng để bạn có thể áp dụng 
thành công trong thực tế.</p>
"""),
        (f"Lợi Ích Khi Áp Dụng {kw}", f"""
<p>Việc am hiểu và áp dụng đúng đắn <strong>{kw}</strong> mang lại vô số lợi ích thiết thực. 
Dưới đây là những lợi ích quan trọng nhất bạn có thể nhận được:</p>
<h3>1. Tăng Hiệu Quả Đáng Kể</h3>
<p>Khi bạn nắm vững {kw_lower}, mọi quy trình sẽ trở nên trơn tru và hiệu quả hơn. 
Nhiều người dùng báo cáo năng suất tăng từ 30-50% sau khi áp dụng đúng phương pháp.</p>
<h3>2. Tiết Kiệm Thời Gian và Chi Phí</h3>
<p>Một trong những lợi ích rõ ràng nhất là khả năng tối ưu hóa nguồn lực. 
Bạn sẽ làm được nhiều hơn trong thời gian ít hơn với chi phí thấp hơn.</p>
<h3>3. Kết Quả Bền Vững</h3>
<p>Khác với các giải pháp tạm thời, {kw_lower} mang lại nền tảng vững chắc cho 
sự phát triển lâu dài. Đây là lý do tại sao ngày càng nhiều chuyên gia khuyến nghị phương pháp này.</p>
"""),
        (f"Hướng Dẫn Áp Dụng {kw} Đúng Cách", f"""
<p>Để đạt được kết quả tốt nhất với <strong>{kw}</strong>, bạn cần tuân thủ các bước 
sau đây một cách có hệ thống:</p>
<ol>
<li><strong>Bước 1 – Nghiên Cứu và Chuẩn Bị:</strong> Tìm hiểu kỹ về {kw_lower} trước 
khi bắt đầu. Đọc tài liệu, tham khảo ý kiến chuyên gia và xác định mục tiêu cụ thể của bạn.</li>
<li><strong>Bước 2 – Lập Kế Hoạch Chi Tiết:</strong> Xây dựng kế hoạch rõ ràng với 
timeline cụ thể, nguồn lực cần thiết và các milestones quan trọng.</li>
<li><strong>Bước 3 – Thực Hiện Từng Bước:</strong> Áp dụng {kw_lower} theo từng giai đoạn, 
không nên vội vàng. Mỗi bước cần được hoàn thành tốt trước khi chuyển sang bước tiếp theo.</li>
<li><strong>Bước 4 – Đánh Giá và Tối Ưu:</strong> Thường xuyên đánh giá kết quả và 
điều chỉnh phương pháp để đạt hiệu quả tối đa.</li>
<li><strong>Bước 5 – Mở Rộng Quy Mô:</strong> Khi đã thành công ở quy mô nhỏ, 
tiến hành mở rộng áp dụng trên diện rộng hơn.</li>
</ol>
"""),
        (f"Những Lỗi Phổ Biến Khi Thực Hiện {kw}", f"""
<p>Nhiều người gặp thất bại khi áp dụng <strong>{kw}</strong> chỉ vì mắc phải 
những sai lầm có thể tránh được. Dưới đây là các lỗi phổ biến nhất:</p>
<h3>Lỗi 1: Thiếu Kiên Nhẫn</h3>
<p>{kw} đòi hỏi thời gian và sự kiên trì. Nhiều người bỏ cuộc quá sớm khi chưa 
thấy kết quả ngay lập tức. Hãy nhớ rằng thành công cần có quá trình.</p>
<h3>Lỗi 2: Không Có Kế Hoạch Rõ Ràng</h3>
<p>Bước vào mà không có kế hoạch cụ thể là một trong những nguyên nhân thất bại 
hàng đầu. Luôn lên kế hoạch chi tiết trước khi bắt đầu.</p>
<h3>Lỗi 3: Bỏ Qua Việc Đánh Giá Kết Quả</h3>
<p>Không theo dõi và đánh giá tiến độ khiến bạn không biết mình đang ở đâu 
và cần cải thiện điều gì. Hãy thiết lập hệ thống đo lường hiệu quả từ đầu.</p>
<h3>Lỗi 4: Làm Theo Cảm Tính Thay Vì Dữ Liệu</h3>
<p>Quyết định dựa trên cảm giác thay vì dữ liệu thực tế thường dẫn đến 
kết quả không như mong đợi. Hãy luôn dựa vào số liệu cụ thể.</p>
"""),
        (f"Kinh Nghiệm Thực Tế Về {kw}", f"""
<p>Dựa trên kinh nghiệm thực tế từ hàng trăm trường hợp thành công, chúng tôi 
đúc kết được những bài học vàng về <strong>{kw}</strong>:</p>
<blockquote>
<p><em>"Chìa khóa thành công với {kw_lower} không nằm ở tốc độ mà nằm ở sự 
nhất quán và kiên định trong từng bước thực hiện."</em></p>
</blockquote>
<p>Các chuyên gia hàng đầu trong lĩnh vực này đồng thuận rằng:</p>
<ul>
<li>Bắt đầu từ những điều cơ bản và xây dựng nền tảng vững chắc</li>
<li>Học hỏi từ những người đi trước và tránh lặp lại sai lầm của họ</li>
<li>Luôn cập nhật kiến thức và phương pháp mới nhất</li>
<li>Kết nối với cộng đồng cùng chí hướng để hỗ trợ nhau</li>
<li>Không ngại thử nghiệm và học hỏi từ thất bại</li>
</ul>
"""),
        ("Kết Luận", f"""
<p>Qua bài viết này, chúng tôi đã cùng bạn tìm hiểu toàn diện về <strong>{kw}</strong> – 
từ định nghĩa cơ bản, lợi ích thực tế, cách áp dụng đúng đắn cho đến những 
kinh nghiệm quý báu từ thực tế.</p>
<p>Điều quan trọng nhất cần ghi nhớ là: <strong>{kw}</strong> không phải là đích đến 
mà là hành trình. Hãy kiên nhẫn, nhất quán và không ngừng học hỏi để đạt được 
kết quả tốt nhất.</p>
<p>Nếu bạn có bất kỳ câu hỏi nào về {kw_lower}, hãy để lại bình luận bên dưới 
hoặc liên hệ với chúng tôi. Chúng tôi luôn sẵn sàng hỗ trợ bạn trên hành trình này!</p>
<p><strong>👉 Đừng quên chia sẻ bài viết nếu bạn thấy hữu ích!</strong></p>
"""),
    ]

    # Build HTML content
    intro = f"""<p>Bạn đang tìm kiếm thông tin về <strong>{kw}</strong>? 
Bài viết này sẽ cung cấp cho bạn những kiến thức đầy đủ và chính xác nhất, 
giúp bạn hiểu rõ và áp dụng hiệu quả trong thực tế. Hãy đọc hết bài để 
không bỏ lỡ bất kỳ thông tin quan trọng nào!</p>"""

    html_parts = [intro]
    for sec_title, sec_content in sections:
        html_parts.append(f"<h2>{sec_title}</h2>")
        html_parts.append(sec_content.strip())

    content_html = "\n".join(html_parts)

    # Count words (approx)
    plain = re.sub(r"<[^>]+>", " ", content_html)
    word_count = len(plain.split())

    return {
        "title": title,
        "meta_desc": meta_desc,
        "content_html": content_html,
        "word_count": word_count,
        "keyword": kw,
    }


# =============================================================================
# LỊCH ĐĂNG PYRAMID
# =============================================================================
PYRAMID_SCHEDULE = [
    {"day": 1, "count": 1,  "label": "Ngày 1",  "desc": "Warm-up (1 bài)"},
    {"day": 2, "count": 3,  "label": "Ngày 2",  "desc": "Tăng tốc (3 bài)"},
    {"day": 3, "count": 5,  "label": "Ngày 3",  "desc": "Full speed (5 bài)"},
    {"day": 4, "count": 5,  "label": "Ngày 4",  "desc": "Duy trì (5 bài)"},
    {"day": 5, "count": 5,  "label": "Ngày 5",  "desc": "Duy trì (5 bài)"},
]
TOTAL_POSTS = sum(d["count"] for d in PYRAMID_SCHEDULE)  # = 19


# =============================================================================
# MAIN: setup_seo_tab — được gọi từ gui_view.py
# =============================================================================
def setup_seo_tab(view, tab_frame):
    C = view.colors

    # Sub-tabs bên trong tab SEO
    sub = ctk.CTkTabview(
        tab_frame,
        corner_radius=12,
        border_width=1, border_color=C['border'],
        fg_color=C['bg_light'],
        segmented_button_fg_color=C['bg_dark'],
        segmented_button_selected_color=C['primary'],
        segmented_button_selected_hover_color=C['primary_hover'],
        segmented_button_unselected_color=C['bg_dark'],
        text_color=C['text_primary'],
    )
    sub.pack(fill="both", expand=True, padx=8, pady=8)

    tab_check   = sub.add("🔍 Kiểm Tra SEO URL")
    tab_plan    = sub.add("📅 Kế Hoạch Viết Bài (Pyramid)")
    tab_ai      = sub.add("🤖 AI SEO 100")

    _build_checker_tab(view, C, tab_check)
    _build_plan_tab(view, C, tab_plan)
    _build_ai_seo_tab(view, C, tab_ai)


# =============================================================================
# SUB-TAB 1: KIỂM TRA SEO URL
# =============================================================================
def _build_checker_tab(view, C, parent):
    root = tk.Frame(parent, bg="#FFFBEB")
    root.pack(fill="both", expand=True, padx=10, pady=8)
    root.columnconfigure(0, weight=1, minsize=300)
    root.columnconfigure(1, weight=3)
    root.rowconfigure(0, weight=1)

    # LEFT
    left = ctk.CTkFrame(root, fg_color=C['bg_card'], corner_radius=12,
                         border_width=2, border_color=C['border'])
    left.grid(row=0, column=0, sticky="nsew", padx=(0,8))

    ctk.CTkLabel(left, text="🔍 Nhập URL cần kiểm tra",
                 font=("Segoe UI",13,"bold"), text_color=C['primary']
                 ).pack(anchor="w", padx=14, pady=(12,4))

    url_box = ctk.CTkTextbox(left, height=110, font=("Segoe UI",12),
                              corner_radius=8, border_width=1, border_color=C['border'],
                              fg_color=C['bg_light'])
    url_box.pack(fill="x", padx=14, pady=(0,8))
    url_box.insert("end", "https://example.com\n")

    lbl_prog = ctk.CTkLabel(left, text="", font=("Segoe UI",10), text_color=C['text_secondary'])
    lbl_prog.pack(padx=14)

    btn_run = ctk.CTkButton(left, text="🚀 PHÂN TÍCH SEO", height=42,
                             font=("Segoe UI",12,"bold"),
                             fg_color=C['primary'], hover_color=C['primary_hover'],
                             corner_radius=21)
    btn_run.pack(fill="x", padx=14, pady=6)

    btn_clr = ctk.CTkButton(left, text="🗑️ Xóa kết quả", height=34,
                             font=("Segoe UI",11),
                             fg_color=C['bg_dark'], hover_color=C['border'],
                             text_color=C['text_secondary'], corner_radius=17)
    btn_clr.pack(fill="x", padx=14, pady=(0,8))

    # RIGHT
    right = ctk.CTkFrame(root, fg_color=C['bg_card'], corner_radius=12,
                          border_width=2, border_color=C['border'])
    right.grid(row=0, column=1, sticky="nsew")

    ctk.CTkLabel(right, text="📊 Kết Quả Phân Tích",
                 font=("Segoe UI",13,"bold"), text_color=C['primary']
                 ).pack(anchor="w", padx=14, pady=(12,4))

    scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=4, pady=(0,8))

    def clear_results():
        for w in scroll.winfo_children(): w.destroy()
        lbl_prog.configure(text="")

    def render(d):
        sc  = _score_color(d["score"])
        card = ctk.CTkFrame(scroll, fg_color=C['bg_light'], corner_radius=10,
                             border_width=2, border_color=sc)
        card.pack(fill="x", padx=4, pady=5)

        # Header
        hdr = ctk.CTkFrame(card, fg_color=C['bg_dark'], corner_radius=8)
        hdr.pack(fill="x", padx=8, pady=(8,0))
        ctk.CTkLabel(hdr, text=f"🌐 {d['url'][:65]}",
                     font=("Segoe UI",10,"bold"), text_color=C['text_primary'],
                     anchor="w").pack(side="left", padx=10, pady=6, fill="x", expand=True)
        ctk.CTkLabel(hdr, text=f" {d['score']}/100 ",
                     font=("Segoe UI",12,"bold"), text_color="white",
                     fg_color=sc, corner_radius=8).pack(side="right", padx=8, pady=4)

        # Grid info
        body = tk.Frame(card, bg="#FFFBEB")
        body.pack(fill="x", padx=8, pady=6)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        def cell(col, row, label, val, ok=None):
            f = tk.Frame(body, bg="#FFFBEB")
            f.grid(row=row, column=col, sticky="ew", padx=5, pady=2)
            icon = "✅" if ok is True else ("❌" if ok is False else ("⚠️" if ok=="warn" else "ℹ️"))
            color = "#10B981" if ok is True else ("#EF4444" if ok is False else ("#F59E0B" if ok=="warn" else C['text_secondary']))
            ctk.CTkLabel(f, text=f"{icon} {label}:", font=("Segoe UI",9,"bold"),
                         text_color=C['text_secondary'], anchor="w").pack(anchor="w")
            ctk.CTkLabel(f, text=str(val)[:80] if val else "(trống)",
                         font=("Segoe UI",10), text_color=color if val else "#9CA3AF",
                         anchor="w", wraplength=250).pack(anchor="w")

        tl = d["title_len"]
        cell(0,0,"Title (50-60):", f"{tl}c: {d['title'][:50]}", True if 50<=tl<=60 else ("warn" if tl>0 else False))
        ml = d["meta_desc_len"]
        cell(1,0,"Meta Desc (120-160):", f"{ml}c", True if 120<=ml<=160 else ("warn" if ml>0 else False))
        cell(0,1,"H1:", f"{d['h1_count']} thẻ" + (f" – {d['h1_texts'][0]}" if d['h1_texts'] else ""), True if d['h1_count']==1 else ("warn" if d['h1_count']>1 else False))
        cell(1,1,"H2:", f"{d['h2_count']} thẻ", True if d['h2_count']>=2 else "warn")
        cell(0,2,"HTTPS:", "✔ An toàn" if d['https'] else "✘ Chưa", d['https'])
        lt=d['load_time_ms']; cell(1,2,"Tốc độ:", f"{lt}ms", True if lt<1500 else ("warn" if lt<3000 else False))
        cell(0,3,"Canonical:", d['canonical'] or "(chưa có)", bool(d['canonical']))
        cell(1,3,"OG Image:", d['og_image'] or "(chưa có)", bool(d['og_image']))
        cell(0,4,"Schema:", ", ".join(d['schema_types']) or "(không có)", bool(d['schema_types']))
        cell(1,4,"Ảnh thiếu ALT:", f"{d['img_missing_alt']}/{d['img_total']}", d['img_missing_alt']==0 if d['img_total']>0 else None)

        # Tips
        tips = []
        if tl < 50:   tips.append(f"Title quá ngắn ({tl}c). Nên 50-60.")
        if tl > 60:   tips.append(f"Title quá dài ({tl}c). Rút ngắn xuống 60.")
        if ml < 120:  tips.append(f"Meta desc ngắn ({ml}c). Nên 120-160.")
        if d['h1_count']==0: tips.append("Chưa có H1! Thêm ngay thẻ H1 chứa từ khóa.")
        if d['h1_count']>1:  tips.append(f"Quá nhiều H1 ({d['h1_count']}). Chỉ dùng 1 H1.")
        if not d['canonical']:tips.append("Thêm thẻ canonical tránh trùng nội dung.")
        if not d['og_image']: tips.append("Thêm og:image để share Facebook/Zalo đẹp.")
        if not d['schema_types']: tips.append("Thêm Schema Markup (Article/FAQ) để có Rich Snippet.")
        if not d['https']:    tips.append("Chuyển sang HTTPS ngay!")
        if d['img_missing_alt']>0: tips.append(f"{d['img_missing_alt']} ảnh thiếu ALT. Thêm mô tả alt.")

        if tips:
            tf = ctk.CTkFrame(card, fg_color="#FEF3C7", corner_radius=8)
            tf.pack(fill="x", padx=8, pady=(0,8))
            ctk.CTkLabel(tf, text="💡 Gợi ý cải thiện:", font=("Segoe UI",9,"bold"),
                         text_color="#92400E").pack(anchor="w", padx=10, pady=(6,2))
            for t in tips:
                ctk.CTkLabel(tf, text=f"  • {t}", font=("Segoe UI",9),
                             text_color="#78350F", anchor="w").pack(anchor="w", padx=10)
            tk.Frame(tf, height=4, bg="#FFFBEB").pack()

    def run():
        raw = url_box.get("1.0","end").strip()
        urls = [u.strip() for u in raw.splitlines() if u.strip().startswith("http")]
        if not urls:
            messagebox.showwarning("Thiếu URL","Nhập ít nhất 1 URL bắt đầu bằng http/https!")
            return
        btn_run.configure(state="disabled", text="⏳ Đang phân tích...")
        clear_results()
        def worker():
            for i, url in enumerate(urls, 1):
                lbl_prog.configure(text=f"🔄 {i}/{len(urls)}: {url[:45]}...")
                d = _analyze_seo(url)
                view.after(0, lambda x=d: render(x))
            lbl_prog.configure(text=f"✅ Xong {len(urls)} URL!")
            btn_run.configure(state="normal", text="🚀 PHÂN TÍCH SEO")
        threading.Thread(target=worker, daemon=True).start()

    btn_run.configure(command=run)
    btn_clr.configure(command=clear_results)



# =============================================================================
# HELPER: Wrap nội dung user nhập vào HTML chuẩn SEO
# =============================================================================
def _wrap_seo_html(title: str, raw_content: str, featured_img: str = "",
                   extra_imgs: list = None, meta_desc: str = "") -> dict:
    """
    Tự động chuẩn hóa content cho SEO:
      - Tôn trọng hoàn toàn content của người dùng (không chèn text rác/intro/cta)
      - Cho phép dùng ## cho H2, ### cho H3, **chữ in đậm**
      - Xen kẽ ảnh tự động đều đặn vào giữa các đoạn văn
      - Chỉ thêm JSON-LD và tiêu đề H1 ở đầu
    """
    title = title.strip()
    extra_imgs = extra_imgs or []

    # ---- Bóc tách Markdown đơn giản ----
    # Vì Textbox của Tkinter chỉ nhập text thuần, 
    # người dùng có thể xài Markdown để làm thẻ Heading:
    # "## Tiêu đề con" -> <h2>Tiêu đề con</h2>
    # "### Tiêu đề siêu con" -> <h3>Tiêu đề siêu con</h3>
    content_html = raw_content.strip()
    
    if "<p" not in content_html.lower() and "<h2" not in content_html.lower():
        lines = content_html.split('\n')
        parsed = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('### '):
                parsed.append(f"<h3>{line[4:].strip()}</h3>")
            elif line.startswith('## '):
                parsed.append(f"<h2>{line[3:].strip()}</h2>")
            elif line.startswith('# '):
                # Đề phòng user gõ 1 dấu #, coi như H2
                parsed.append(f"<h2>{line[2:].strip()}</h2>")
            else:
                if not line.startswith('<'):
                    # Đổi **in đậm** thành <strong>
                    line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                    parsed.append(f"<p>{line}</p>")
                else:
                    parsed.append(line)
        content_html = "\n".join(parsed)

    # ---- Tự sinh meta desc nếu trống ----
    if not meta_desc:
        plain = re.sub(r"<[^>]+>", " ", content_html)
        plain = re.sub(r"\s+", " ", plain).strip()
        meta_desc = plain[:157].rsplit(" ", 1)[0] + "..." if len(plain) > 157 else plain

    # ---- Phân bổ ảnh bổ sung xen kẽ vào bài viết ----
    imgs = [img for img in extra_imgs if img.strip()]
    if imgs:
        # Tách theo </p> hoặc </h2> để chèn ảnh
        parts = re.split(r"(</p>|</h2>)", content_html, flags=re.IGNORECASE)
        if len(parts) > 1:
            block_count = len(parts) // 2
            spacing = max(1, block_count // (len(imgs) + 1))
            insert_indices = [spacing * (i + 1) for i in range(len(imgs))]
            
            new_parts = []
            b_idx = 0
            for part in parts:
                new_parts.append(part)
                if part.lower() in ("</p>", "</h2>"):
                    b_idx += 1
                    if b_idx in insert_indices:
                        img_idx = insert_indices.index(b_idx)
                        img_url = imgs[img_idx]
                        img_tag = (
                            f'\n<figure style="text-align:center;margin:20px 0;">\n'
                            f'<img src="{img_url}" alt="{title}" '
                            f'style="max-width:100%;height:auto;border-radius:8px;" loading="lazy">\n'
                            f'<figcaption style="font-size:13px;color:#666;margin-top:5px;">{title}</figcaption>\n'
                            f'</figure>\n'
                        )
                        new_parts.append(img_tag)
            content_html = "".join(new_parts)
        else:
            # Nếu chả có HTML gì, đè lên đỉnh
            img_tags = ""
            for img_url in imgs:
                img_tags += (
                    f'<figure style="text-align:center;margin:20px 0;">\n'
                    f'<img src="{img_url}" alt="{title}" '
                    f'style="max-width:100%;height:auto;border-radius:8px;" loading="lazy">\n'
                    f'</figure>\n'
                )
            content_html = img_tags + content_html

    # ---- Schema JSON-LD ----
    import datetime as _dt
    today = _dt.date.today().isoformat()
    schema = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{meta_desc[:160]}",
  "datePublished": "{today}",
  "dateModified": "{today}",
  "author": {{"@type": "Organization", "name": "Website"}},
  "image": "{featured_img or ''}"
}}
</script>'''

    # ---- Ảnh Featured trên đỉnh ----
    feat_html = ""
    if featured_img:
        feat_html = (
            f'<figure style="margin:0 0 25px 0;text-align:center;">\n'
            f'<img src="{featured_img}" alt="{title}" '
            f'style="max-width:100%;height:auto;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,.15);" '
            f'loading="lazy">\n'
            f'</figure>\n'
        )

    # ---- Lọc bỏ H1 thừa trong AI content (WP tự thêm H1 từ title field) ----
    import re as _re
    # Xóa toàn bộ <h1>...</h1> trong content_html để tránh trùng với WP title
    content_html = _re.sub(r'<h1[^>]*>.*?</h1>', '', content_html,
                            flags=_re.DOTALL | _re.IGNORECASE).strip()

    # ---- Ảnh Featured: KHÔNG chèn lại vào content (WP đã gán featured_image riêng) ----
    # feat_html bỏ trống để tránh ảnh xuất hiện 2 lần

    # ---- Lắp ráp: chỉ schema + content, KHÔNG có H1 và KHÔNG có ảnh lặp ----
    full_html = f"""{schema}
<article class="seo-post">
{content_html}
</article>"""

    # Đếm từ
    plain_all = _re.sub(r"<[^>]+>", " ", full_html)
    wc = len(_re.sub(r"\s+", " ", plain_all).split())

    return {
        "title": title,
        "meta_desc": meta_desc,
        "content_html": full_html,
        "word_count": wc,
    }


# =============================================================================
# SUB-TAB 2: KẾ HOẠCH VIẾT BÀI PYRAMID (REDESIGN)
# =============================================================================
def _build_plan_tab(view, C, parent):
    """
    Layout 3 khu vực:
      LEFT  : Bảng lịch pyramid — chọn slot → load vào editor
      CENTER: Editor — nhập tiêu đề, import bài, thêm ảnh
      RIGHT : Preview output HTML chuẩn SEO
    """
    root = tk.Frame(parent, bg="#FFFBEB")
    root.pack(fill="both", expand=True, padx=8, pady=6)
    root.columnconfigure(0, weight=1, minsize=200)
    root.columnconfigure(1, weight=2, minsize=320)
    root.columnconfigure(2, weight=2, minsize=300)
    root.rowconfigure(0, weight=1)

    # =========================================================
    # CỘT 1 — LỊCH PYRAMID
    # =========================================================
    col1 = ctk.CTkFrame(root, fg_color=C['bg_card'], corner_radius=12,
                         border_width=2, border_color=C['border'])
    col1.grid(row=0, column=0, sticky="nsew", padx=(0,6))

    ctk.CTkLabel(col1, text="📅 Lịch Đăng Bài",
                 font=("Segoe UI",12,"bold"), text_color=C['primary']
                 ).pack(anchor="w", padx=12, pady=(10,2))
    ctk.CTkLabel(col1,
                 text="N1:1  N2:3  N3:5  N4:5  N5:5",
                 font=("Segoe UI",9), text_color=C['text_secondary']
                 ).pack(anchor="w", padx=12, pady=(0,6))

    sched_scroll = ctk.CTkScrollableFrame(col1, fg_color="transparent")
    sched_scroll.pack(fill="both", expand=True, padx=4, pady=4)

    lbl_stat = ctk.CTkLabel(col1, text="", font=("Segoe UI",9), text_color=C['text_secondary'])
    lbl_stat.pack(padx=12, pady=4)

    day_colors = {1:"#BFDBFE", 2:"#A7F3D0", 3:"#FDE68A", 4:"#FBCFE8", 5:"#DDD6FE"}
    slot_buttons = {}  # key: (day,slot) -> CTkButton

    # =========================================================
    # CỘT 2 — EDITOR
    # =========================================================
    col2 = ctk.CTkFrame(root, fg_color=C['bg_card'], corner_radius=12,
                         border_width=2, border_color=C['border'])
    col2.grid(row=0, column=1, sticky="nsew", padx=(0,6))

    ctk.CTkLabel(col2, text="✏️ Soạn Bài Viết",
                 font=("Segoe UI",12,"bold"), text_color=C['primary']
                 ).pack(anchor="w", padx=12, pady=(10,4))

    # Slot indicator
    lbl_slot = ctk.CTkLabel(col2, text="← Chọn slot từ lịch",
                             font=("Segoe UI",10,"bold"), text_color=C['text_secondary'],
                             fg_color=C['bg_dark'], corner_radius=6)
    lbl_slot.pack(fill="x", padx=12, pady=(0,6))

    # Tiêu đề (user tự nhập)
    ctk.CTkLabel(col2, text="🏷️ Tiêu đề bài viết (user tự nhập):",
                 font=("Segoe UI",10,"bold"), text_color=C['text_primary']
                 ).pack(anchor="w", padx=12)
    entry_title = ctk.CTkEntry(col2, placeholder_text="Nhập tiêu đề bài viết...",
                                height=38, font=("Segoe UI",12), corner_radius=8,
                                border_width=1, border_color=C['border'],
                                fg_color=C['bg_light'])
    entry_title.pack(fill="x", padx=12, pady=(2,8))

    # Meta description  
    ctk.CTkLabel(col2, text="📝 Meta Description (để trống = tự sinh):",
                 font=("Segoe UI",10,"bold"), text_color=C['text_primary']
                 ).pack(anchor="w", padx=12)
    entry_meta = ctk.CTkEntry(col2, placeholder_text="Tự sinh từ nội dung nếu để trống...",
                               height=34, font=("Segoe UI",10), corner_radius=8,
                               border_width=1, border_color=C['border'],
                               fg_color=C['bg_light'])
    entry_meta.pack(fill="x", padx=12, pady=(2,8))

    # Ảnh featured
    ctk.CTkLabel(col2, text="🖼️ Ảnh Featured (URL hoặc đường dẫn):",
                 font=("Segoe UI",10,"bold"), text_color=C['text_primary']
                 ).pack(anchor="w", padx=12)
    img_row1 = tk.Frame(col2, bg="#FFFBEB")
    img_row1.pack(fill="x", padx=12, pady=(2,4))
    entry_featured = ctk.CTkEntry(img_row1, placeholder_text="https://... hoặc C:\\path\\image.jpg",
                                   height=32, font=("Segoe UI",10), corner_radius=8,
                                   border_width=1, border_color=C['border'],
                                   fg_color=C['bg_light'])
    entry_featured.pack(side="left", fill="x", expand=True, padx=(0,4))
    def browse_featured():
        from tkinter import filedialog
        p = filedialog.askopenfilename(filetypes=[("Images","*.jpg *.jpeg *.png *.webp *.gif"),("All","*.*")])
        if p:
            entry_featured.delete(0,"end")
            entry_featured.insert(0, p)
    ctk.CTkButton(img_row1, text="📁", width=34, height=32, font=("Segoe UI",12),
                  fg_color=C['bg_dark'], hover_color=C['border'],
                  text_color=C['text_secondary'], corner_radius=8,
                  command=browse_featured).pack(side="right")

    # Ảnh bổ sung (3 ảnh)
    ctk.CTkLabel(col2, text="🖼️ Ảnh bổ sung trong bài (tối đa 3):",
                 font=("Segoe UI",10,"bold"), text_color=C['text_primary']
                 ).pack(anchor="w", padx=12)
    extra_entries = []
    for i in range(3):
        row = tk.Frame(col2, bg="#FFFBEB")
        row.pack(fill="x", padx=12, pady=1)
        ctk.CTkLabel(row, text=f"  Ảnh {i+1}:", font=("Segoe UI",9),
                     text_color=C['text_secondary'], width=45).pack(side="left")
        e = ctk.CTkEntry(row, placeholder_text=f"URL hoặc đường dẫn ảnh {i+1}...",
                         height=28, font=("Segoe UI",9), corner_radius=6,
                         border_width=1, border_color=C['border'],
                         fg_color=C['bg_light'])
        e.pack(side="left", fill="x", expand=True, padx=(2,4))
        def browse_extra(entry=e):
            from tkinter import filedialog
            p = filedialog.askopenfilename(filetypes=[("Images","*.jpg *.jpeg *.png *.webp"),("All","*.*")])
            if p:
                entry.delete(0,"end")
                entry.insert(0, p)
        ctk.CTkButton(row, text="📁", width=28, height=28, font=("Segoe UI",10),
                      fg_color=C['bg_dark'], hover_color=C['border'],
                      text_color=C['text_secondary'], corner_radius=6,
                      command=browse_extra).pack(side="right")
        extra_entries.append(e)

    # Nội dung bài viết
    ctk.CTkLabel(col2, text="📄 Nội dung bài viết (paste vào đây):",
                 font=("Segoe UI",10,"bold"), text_color=C['text_primary']
                 ).pack(anchor="w", padx=12, pady=(6,2))

    # Import buttons
    import_row = tk.Frame(col2, bg="#FFFBEB")
    import_row.pack(fill="x", padx=12, pady=(0,4))

    def import_from_file():
        from tkinter import filedialog
        p = filedialog.askopenfilename(
            filetypes=[("Text/HTML","*.txt *.html *.htm *.md"),("All","*.*")],
            title="Import nội dung bài viết"
        )
        if not p: return
        with open(p, encoding="utf-8", errors="replace") as f:
            content_box.delete("1.0","end")
            content_box.insert("end", f.read())

    def import_from_clipboard():
        try:
            txt = view.clipboard_get()
            content_box.delete("1.0","end")
            content_box.insert("end", txt)
        except:
            messagebox.showwarning("Lỗi","Không lấy được clipboard!")

    ctk.CTkButton(import_row, text="📂 Import từ File", height=30,
                  font=("Segoe UI",10,"bold"),
                  fg_color="#3B82F6", hover_color="#2563EB",
                  text_color="white", corner_radius=15,
                  command=import_from_file).pack(side="left", padx=(0,4))
    ctk.CTkButton(import_row, text="📋 Paste từ Clipboard", height=30,
                  font=("Segoe UI",10,"bold"),
                  fg_color="#8B5CF6", hover_color="#7C3AED",
                  text_color="white", corner_radius=15,
                  command=import_from_clipboard).pack(side="left", padx=(0,4))
    ctk.CTkButton(import_row, text="🗑️ Xóa", height=30,
                  font=("Segoe UI",10),
                  fg_color=C['bg_dark'], hover_color=C['border'],
                  text_color=C['text_secondary'], corner_radius=15,
                  command=lambda: content_box.delete("1.0","end")
                  ).pack(side="left")

    # Hàm tiện ích thêm text tại con trỏ
    def _insert_format(fmt):
        try:
            content_box.insert("insert", fmt)
        except Exception:
            content_box.insert("end", fmt)

    # Nút công cụ (nằm bên phải của thanh import_row)
    ctk.CTkButton(import_row, text="B", width=30, height=26,
                  font=("Segoe UI", 12, "bold"), fg_color=C['bg_card'], hover_color=C['border'],
                  text_color=C['text_primary'], corner_radius=4,
                  command=lambda: _insert_format("**Chữ in đậm** ")).pack(side="right", padx=(4,0))
    
    ctk.CTkButton(import_row, text="H3", width=30, height=26,
                  font=("Segoe UI", 11, "bold"), fg_color=C['bg_card'], hover_color=C['border'],
                  text_color=C['text_primary'], corner_radius=4,
                  command=lambda: _insert_format("\n\n### Tiêu Đề H3 Mới\n")).pack(side="right", padx=(4,0))
                  
    ctk.CTkButton(import_row, text="H2", width=30, height=26,
                  font=("Segoe UI", 11, "bold"), fg_color=C['bg_card'], hover_color=C['border'],
                  text_color=C['text_primary'], corner_radius=4,
                  command=lambda: _insert_format("\n\n## Tiêu Đề H2 Mới\n")).pack(side="right", padx=(4,0))
                  
    ctk.CTkLabel(import_row, text="Thêm:", font=("Segoe UI", 10), text_color=C['text_secondary']).pack(side="right", padx=(10,2))


    # =========================================================

    # BUTTONS TRƯỚC (PACK Ở BOTTOM ĐỂ CHIẾM CHỖ ĐÁY)

    # =========================================================

    btn_row = tk.Frame(col2, bg="#FFFBEB")

    btn_row.pack(side="bottom", fill="x", padx=12, pady=(0,10))



    btn_format = ctk.CTkButton(btn_row, text="⚡ Format Chuẩn SEO",

                                height=42, font=("Segoe UI", 11, "bold"),

                                fg_color=C["primary"], hover_color=C["primary_hover"],

                                corner_radius=21)

    btn_format.pack(side="left", fill="x", expand=True, padx=(0,6))



    btn_save_slot = ctk.CTkButton(btn_row, text="💾 Lưu Slot",

                                   height=42, font=("Segoe UI", 11, "bold"),

                                   fg_color="#10B981", hover_color="#059669",

                                   corner_radius=21)

    btn_save_slot.pack(side="right", fill="x", expand=True)



    # =========================================================

    # TEXTBOX (PACK SAU ── EXPAND CHIẾM TRỌN KHÔNG GIAN CÒN LẠI)

    # =========================================================

    content_box = ctk.CTkTextbox(col2, font=("Segoe UI", 10), wrap="word",

                                  corner_radius=8, border_width=1,

                                  border_color=C["border"],

                                  fg_color=C["bg_light"])

    content_box.pack(side="top", fill="both", expand=True, padx=12, pady=(0,6))



    # =========================================================
    # CỘT 3 — PREVIEW OUTPUT
    # =========================================================
    col3 = ctk.CTkFrame(root, fg_color=C['bg_card'], corner_radius=12,
                         border_width=2, border_color=C['border'])
    col3.grid(row=0, column=2, sticky="nsew")

    top3 = ctk.CTkFrame(col3, fg_color=C['bg_dark'], corner_radius=8)
    top3.pack(fill="x", padx=10, pady=(10,4))
    ctk.CTkLabel(top3, text="👁 Preview & Xuất HTML",
                 font=("Segoe UI",11,"bold"), text_color=C['primary']
                 ).pack(side="left", padx=10, pady=6)
    lbl_wc = ctk.CTkLabel(top3, text="", font=("Segoe UI",9), text_color=C['text_secondary'])
    lbl_wc.pack(side="right", padx=10)

    # SEO Score bar
    score_frame = ctk.CTkFrame(col3, fg_color=C['bg_dark'], corner_radius=8)
    score_frame.pack(fill="x", padx=10, pady=(0,4))
    lbl_score = ctk.CTkLabel(score_frame, text="SEO Score: —",
                              font=("Segoe UI",10,"bold"), text_color=C['text_secondary'])
    lbl_score.pack(side="left", padx=10, pady=5)
    lbl_tips_summary = ctk.CTkLabel(score_frame, text="",
                                     font=("Segoe UI",9), text_color="#F59E0B", wraplength=200)
    lbl_tips_summary.pack(side="right", padx=10, pady=5)

    # Meta info
    info_frm = ctk.CTkFrame(col3, fg_color="#F0FDF4", corner_radius=8)
    info_frm.pack(fill="x", padx=10, pady=(0,4))
    lbl_prev_title = ctk.CTkLabel(info_frm, text="🏷️ —", font=("Segoe UI",10,"bold"),
                                   text_color="#166534", anchor="w", wraplength=280)
    lbl_prev_title.pack(anchor="w", padx=10, pady=(6,1))
    lbl_prev_meta = ctk.CTkLabel(info_frm, text="📝 —", font=("Segoe UI",9),
                                  text_color="#15803D", anchor="w", wraplength=280)
    lbl_prev_meta.pack(anchor="w", padx=10, pady=(0,6))

    # Preview textbox (plain text của HTML)
    prev_box = ctk.CTkTextbox(col3, font=("Segoe UI",9), wrap="word",
                               corner_radius=8, border_width=1, border_color=C['border'],
                               fg_color=C['bg_light'])
    prev_box.pack(fill="both", expand=True, padx=10, pady=(0,4))

    # Action buttons
    act_row = tk.Frame(col3, bg="#FFFBEB")
    act_row.pack(fill="x", padx=10, pady=(0,8))

    def copy_html_current():
        txt = prev_box.get("1.0","end")
        if not txt.strip() or "—" in txt:
            messagebox.showinfo("Chưa có dữ liệu","Hãy Format bài viết trước!")
            return
        if current_result.get("content_html"):
            view.clipboard_clear()
            view.clipboard_append(current_result["content_html"])
            messagebox.showinfo("Đã copy!","HTML chuẩn SEO đã copy vào clipboard!")

    def export_html_file():
        if not current_result.get("content_html"):
            messagebox.showinfo("Chưa có dữ liệu","Hãy Format bài viết trước!")
            return
        from tkinter import filedialog
        p = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML","*.html"),("Text","*.txt"),("All","*.*")],
            title="Xuất file HTML"
        )
        if not p: return
        with open(p,"w",encoding="utf-8") as f:
            f.write(current_result["content_html"])
        messagebox.showinfo("Đã xuất!", f"File HTML đã lưu:\n{p}")

    def save_all_json():
        if not slot_data:
            messagebox.showinfo("Chưa có dữ liệu","Hãy tạo ít nhất 1 bài viết!")
            return
        from tkinter import filedialog
        p = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON","*.json"),("All","*.*")],
            title="Xuất kế hoạch SEO (JSON)"
        )
        if not p: return
        out = {"schedule": PYRAMID_SCHEDULE, "posts": list(slot_data.values())}
        with open(p,"w",encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Đã lưu!", f"Kế hoạch đã lưu:\n{p}")

    ctk.CTkButton(act_row, text="📋 Copy HTML", height=34,
                  font=("Segoe UI",10,"bold"),
                  fg_color="#3B82F6", hover_color="#2563EB",
                  text_color="white", corner_radius=17,
                  command=copy_html_current).pack(side="left", padx=(0,4))
    ctk.CTkButton(act_row, text="💾 Xuất File", height=34,
                  font=("Segoe UI",10,"bold"),
                  fg_color="#10B981", hover_color="#059669",
                  text_color="white", corner_radius=17,
                  command=export_html_file).pack(side="left", padx=(0,4))

    def preview_in_browser():
        """Mở bài viết đã format trong trình duyệt để xem trực tiếp."""
        if not current_result.get("content_html"):
            messagebox.showinfo("Chưa có dữ liệu", "Hãy Format bài viết trước!")
            return
        import tempfile, webbrowser
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                         encoding="utf-8") as f:
            f.write(current_result["content_html"])
            tmp = f.name
        webbrowser.open(f"file:///{tmp.replace(chr(92), '/')}")

    ctk.CTkButton(act_row, text="🌐 Preview", height=34,
                  font=("Segoe UI",10,"bold"),
                  fg_color="#8B5CF6", hover_color="#7C3AED",
                  text_color="white", corner_radius=17,
                  command=preview_in_browser).pack(side="left", padx=(0,4))
    ctk.CTkButton(act_row, text="📦 Lưu JSON", height=34,
                  font=("Segoe UI",10),
                  fg_color=C['bg_dark'], hover_color=C['border'],
                  text_color=C['text_secondary'], corner_radius=17,
                  command=save_all_json).pack(side="right")

    # ── ĐĂNG WORDPRESS SECTION ─────────────────────────────────────────
    wp_frame = ctk.CTkFrame(col3, fg_color="#EFF6FF", corner_radius=10,
                             border_width=1, border_color="#BFDBFE")
    wp_frame.pack(fill="x", padx=10, pady=(0,8))

    wp_top = tk.Frame(wp_frame, bg="#EFF6FF")
    wp_top.pack(fill="x", padx=8, pady=(6,2))
    ctk.CTkLabel(wp_top, text="🚀 Đăng Lên WordPress",
                 font=("Segoe UI",10,"bold"), text_color="#1D4ED8",
                 fg_color="#EFF6FF").pack(side="left")
    lbl_wp_status = ctk.CTkLabel(wp_top, text="", font=("Segoe UI",9),
                                  text_color="#059669", fg_color="#EFF6FF")
    lbl_wp_status.pack(side="right")

    _posted_links = []   # [(title, url), ...]

    def _update_wp_link(post_url, post_title=""):
        """Thêm link bài vừa đăng vào danh sách và làm mới panel"""
        if post_url:
            _posted_links.append((post_title or post_url, post_url))
            _refresh_link_panel()

    # ── PANEL LỊCH SỬ ĐĂNG BÀI ─────────────────────────────────────────
    link_panel_frame = ctk.CTkFrame(col3, fg_color="#F0FDF4", corner_radius=10,
                                     border_width=1, border_color="#86EFAC")
    link_panel_frame.pack(fill="x", padx=10, pady=(0, 6))

    lp_top = tk.Frame(link_panel_frame, bg="#F0FDF4")
    lp_top.pack(fill="x", padx=8, pady=(6,2))
    ctk.CTkLabel(lp_top, text="🔗 Link Bài Đã Đăng",
                 font=("Segoe UI",10,"bold"), text_color="#16A34A",
                 fg_color="#F0FDF4").pack(side="left")
    def _clear_links():
        _posted_links.clear()
        _refresh_link_panel()
    ctk.CTkButton(lp_top, text="Xóa", width=45, height=22,
                  font=("Segoe UI",9), fg_color="#D1FAE5", hover_color="#A7F3D0",
                  text_color="#065F46", corner_radius=6,
                  command=_clear_links).pack(side="right")

    link_scroll = ctk.CTkScrollableFrame(link_panel_frame, fg_color="#F0FDF4",
                                          height=90, corner_radius=6)
    link_scroll.pack(fill="x", padx=6, pady=(2,6))

    lp_empty = ctk.CTkLabel(link_scroll, text="Chưa có bài nào được đăng.",
                             font=("Segoe UI",9), text_color="#6B7280",
                             fg_color="#F0FDF4")
    lp_empty.pack(padx=4, pady=4)

    def _refresh_link_panel():
        for w in link_scroll.winfo_children():
            w.destroy()
        if not _posted_links:
            ctk.CTkLabel(link_scroll, text="Chưa có bài nào được đăng.",
                         font=("Segoe UI",9), text_color="#6B7280",
                         fg_color="#F0FDF4").pack(padx=4, pady=4)
            return
        for i, (ttl, url) in enumerate(reversed(_posted_links)):
            row_bg = "#DCFCE7" if i % 2 == 0 else "#F0FDF4"
            row = tk.Frame(link_scroll, bg=row_bg)
            row.pack(fill="x", padx=2, pady=1)
            num = ctk.CTkLabel(row, text=f"#{len(_posted_links)-i}", width=28,
                               font=("Segoe UI",9,"bold"), text_color="#16A34A",
                               fg_color=row_bg)
            num.pack(side="left", padx=(4,2))
            short_title = ttl[:40] + "..." if len(ttl) > 40 else ttl
            lbl = ctk.CTkLabel(row, text=short_title,
                               font=("Segoe UI",10), text_color="#1E40AF",
                               fg_color=row_bg, cursor="hand2", anchor="w")
            lbl.pack(side="left", fill="x", expand=True, padx=2)
            _url = url
            lbl.bind("<Button-1>", lambda e, u=_url: __import__('webbrowser').open(u))
            lbl.bind("<Enter>", lambda e, w=lbl: w.configure(text_color="#DC2626"))
            lbl.bind("<Leave>", lambda e, w=lbl: w.configure(text_color="#1E40AF"))
            ctk.CTkButton(row, text="↗", width=28, height=22,
                          font=("Segoe UI",11,"bold"), fg_color="#BBF7D0",
                          hover_color="#86EFAC", text_color="#065F46", corner_radius=4,
                          command=lambda u=_url: __import__('webbrowser').open(u)
                          ).pack(side="right", padx=2, pady=1)


    # Category + Tags + Status
    wp_opts = tk.Frame(wp_frame, bg="#EFF6FF")
    wp_opts.pack(fill="x", padx=8, pady=2)
    wp_opts.columnconfigure(1, weight=1)
    wp_opts.columnconfigure(3, weight=1)

    tk.Label(wp_opts, text="Category:", font=("Segoe UI",9), bg="#EFF6FF",
             fg="#374151").grid(row=0, column=0, sticky="w", pady=2, padx=(0,4))
    entry_cat = ctk.CTkEntry(wp_opts, placeholder_text="Tên danh mục (vd: SEO)",
                              height=26, font=("Segoe UI",9), corner_radius=6)
    entry_cat.grid(row=0, column=1, sticky="ew", padx=(0,8))

    tk.Label(wp_opts, text="Tags:", font=("Segoe UI",9), bg="#EFF6FF",
             fg="#374151").grid(row=0, column=2, sticky="w", pady=2, padx=(0,4))
    entry_tags = ctk.CTkEntry(wp_opts, placeholder_text="tag1, tag2, tag3",
                               height=26, font=("Segoe UI",9), corner_radius=6)
    entry_tags.grid(row=0, column=3, sticky="ew")

    wp_opts2 = tk.Frame(wp_frame, bg="#EFF6FF")
    wp_opts2.pack(fill="x", padx=8, pady=(0,4))
    wp_opts2.columnconfigure(1, weight=1)
    wp_opts2.columnconfigure(3, weight=1)

    tk.Label(wp_opts2, text="Trạng thái:", font=("Segoe UI",9), bg="#EFF6FF",
             fg="#374151").grid(row=0, column=0, sticky="w", padx=(0,4))
    post_status_var = tk.StringVar(value="publish")
    status_cb = ctk.CTkComboBox(wp_opts2,
                                 values=["publish","draft","future","pending"],
                                 variable=post_status_var,
                                 height=26, font=("Segoe UI",9),
                                 fg_color="white", corner_radius=6,
                                 width=100)
    status_cb.grid(row=0, column=1, sticky="w", padx=(0,8))

    tk.Label(wp_opts2, text="Ngày đăng:", font=("Segoe UI",9), bg="#EFF6FF",
             fg="#374151").grid(row=0, column=2, sticky="w", padx=(0,4))
    entry_schedule_date = ctk.CTkEntry(wp_opts2,
                                        placeholder_text="YYYY-MM-DDTHH:MM:SS (để trống = ngay)",
                                        height=26, font=("Segoe UI",9), corner_radius=6)
    entry_schedule_date.grid(row=0, column=3, sticky="ew")

    def _do_post_wp():
        """Đăng bài lên WordPress qua REST API."""
        if not current_result.get("content_html"):
            messagebox.showwarning("Chưa có dữ liệu", "Hãy Format bài viết trước!")
            return
        # Lấy thông tin WP từ view (controller)
        try:
            # Ưu tiên lấy từ view.controller, vì AppController lưu thông tin sau khi đăng nhập
            ctrl = getattr(view, 'controller', None)
            
            site_url = getattr(ctrl, 'site_url', "") if ctrl else ""
            username = getattr(ctrl, 'username', "") if ctrl else ""
            password = getattr(ctrl, 'password', "") if ctrl else ""
            
            # Fallback nếu ở mode dev không xài controller tiêu chuẩn
            if not site_url and hasattr(view, 'entry_site_url'):
                site_url = view.entry_site_url.get().strip()
                username = view.entry_username.get().strip()
                password = view.entry_password.get().strip()
                
        except Exception:
            site_url = username = password = ""

        if not site_url or not username or not password:
            messagebox.showwarning(
                "Chưa đăng nhập",
                "Vui lòng đăng nhập WordPress trước!\n(Tab Cài Đặt hoặc Tab Đăng Bài)"
            )
            return

        title       = current_result.get("title","")
        content     = current_result.get("content_html","")
        excerpt     = current_result.get("meta_desc","")
        cat_name    = entry_cat.get().strip()
        tags_raw    = entry_tags.get().strip()
        status      = post_status_var.get()
        sched_date  = entry_schedule_date.get().strip()

        btn_post_wp.configure(state="disabled", text="⏳ Đang đăng...")
        lbl_wp_status.configure(text="", text_color="#374151")

        def _worker():
            try:
                from model.wp_rest_api import WordPressRESTClient
                wp = WordPressRESTClient(
                    site_url=site_url.rstrip("/"),
                    username=username,
                    password=password
                )

                # ────────────────────────────────────────────────────────
                # FIX 401: Đồng bộ Cookie & Nonce từ phiên đăng nhập Selenium hiện tại
                # ────────────────────────────────────────────────────────
                ctrl = getattr(view, 'controller', None)
                if ctrl and getattr(ctrl, 'rest_client', None):
                    fast_client = ctrl.rest_client
                    if fast_client.session and fast_client.session.cookies:
                        # Copy toàn bộ cookies (chứa wordpress_logged_in_xxx)
                        for ck in fast_client.session.cookies:
                            wp.session.cookies.set(ck.name, ck.value, domain=ck.domain)
                        
                        # Copy Nonce (Bắt buộc để POST REST API khi dùng Cookie)
                        if fast_client.nonce:
                            wp.nonce = fast_client.nonce
                            
                        # Đánh dấu đã load cookies thành công để API không nhảy vào login() lại
                        wp.cookies_loaded = True
                        
                        print(f"[SEO] ✅ Đã đồng bộ Cookie & Nonce ({wp.nonce[:10] if wp.nonce else 'None'}) từ phiên Selenium!")
                # Resolve / tạo category
                cat_ids = []
                if cat_name:
                    cats = wp.get_categories()
                    matched = [c for c in (cats or []) if
                               c.get("name","").lower() == cat_name.lower() or
                               c.get("slug","").lower() == cat_name.lower()]
                    if matched:
                        cat_ids = [matched[0]["id"]]
                    else:
                        new_c = wp.create_category(cat_name)
                        if new_c and "id" in new_c:
                            cat_ids = [new_c["id"]]

                # Resolve / tạo tags
                tag_ids = []
                if tags_raw:
                    for tname in [t.strip() for t in tags_raw.split(",") if t.strip()]:
                        existing = wp.get_tags()
                        matched = [t for t in (existing or []) if
                                   t.get("name","").lower() == tname.lower()]
                        if matched:
                            tag_ids.append(matched[0]["id"])
                        else:
                            new_t = wp.create_tag(tname)
                            if new_t and "id" in new_t:
                                tag_ids.append(new_t["id"])

                # Upload featured image nếu có (local path)
                # Ưu tiên dùng fast_client (đã có Cookies/Nonce từ Selenium)
                # để tránh lỗi 401 khi upload
                featured_media = 0
                feat_path = entry_featured.get().strip()
                if feat_path and os.path.isfile(feat_path):
                    upload_result = None
                    ctrl = getattr(view, 'controller', None)
                    
                    # Thử fast_client trước (cookie-authenticated)
                    if ctrl and getattr(ctrl, 'rest_client', None):
                        try:
                            up = ctrl.rest_client.upload_image_fast(feat_path)
                            # Trả về (success, media_id, url)
                            if up and up[0] and up[1]:
                                featured_media = up[1]
                                print(f"[SEO] ✅ Upload ảnh đại diện OK, ID={featured_media}")
                        except Exception as up_err:
                            print(f"[SEO] ⚠️ fast_client upload lỗi: {up_err}")
                    
                    # Fallback: dùng wp client (có nonce)
                    if not featured_media:
                        media = wp.upload_media(feat_path)
                        if isinstance(media, dict) and "id" in media:
                            featured_media = media["id"]
                        elif isinstance(media, tuple) and len(media) >= 2 and media[1]:
                            featured_media = media[1]

                # Upload ảnh bổ sung trong nội dung (extra_entries[0..2])
                extra_img_urls = []   # url sau khi upload lên WP
                ctrl2 = getattr(view, 'controller', None)
                for extra_e in extra_entries:
                    ep = extra_e.get().strip()
                    if not ep:
                        continue
                    if ep.startswith("http"):
                        extra_img_urls.append(ep)
                    elif os.path.isfile(ep):
                        up_url = None
                        if ctrl2 and getattr(ctrl2, 'rest_client', None):
                            try:
                                res = ctrl2.rest_client.upload_image_fast(ep)
                                if res and res[0] and res[2]:
                                    up_url = res[2]
                                    print(f"[SEO] ✅ Upload ảnh bổ sung OK: {up_url}")
                            except Exception as ue:
                                print(f"[SEO] ⚠️ Upload ảnh bổ sung lỗi: {ue}")
                        if up_url:
                            extra_img_urls.append(up_url)

                # Ghép ảnh bổ sung vào cuối content (dùng biến riêng tránh UnboundLocalError)
                final_content = content
                if extra_img_urls:
                    imgs_html = "\n".join(
                        f'<figure class="wp-block-image aligncenter"><img src="{u}" alt="" loading="lazy"/></figure>'
                        for u in extra_img_urls
                    )
                    final_content = content + "\n" + imgs_html

                # Build payload
                payload = {
                    "title":    title,
                    "content":  final_content,
                    "excerpt":  excerpt,
                    "status":   status,
                }
                if cat_ids: payload["categories"] = cat_ids
                if tag_ids: payload["tags"] = tag_ids
                if featured_media: payload["featured_media"] = featured_media
                if sched_date and status == "future":
                    payload["date"] = sched_date

                result_post = wp.create_post(**payload)
                
                # create_post trả về (success, post_id, post_url) tuple
                if isinstance(result_post, tuple):
                    success_post, post_id, post_url = result_post[0], result_post[1], result_post[2] if len(result_post) > 2 else None
                elif isinstance(result_post, dict):
                    # tương thích ngược nếu có dict
                    success_post = "id" in result_post
                    post_id = result_post.get("id")
                    post_url = result_post.get("link", "")
                else:
                    success_post, post_id, post_url = False, None, None
                
                if success_post and post_id:
                    view.after(0, lambda pid=post_id: lbl_wp_status.configure(
                        text=f"✅ Đã đăng! ID #{pid}",
                        text_color="#059669"
                    ))
                    view.after(0, lambda purl=post_url, ptitle=title: _update_wp_link(purl, ptitle))
                    view.after(0, lambda pid=post_id, purl=post_url: messagebox.showinfo(
                        "Thành công!",
                        f"✅ Bài viết đã đăng lên WordPress!\n\n"
                        f"🔗 Link: {purl or '(đang xử lý...)'}\n"
                        f"📌 ID: #{pid}\n"
                        f"📊 Trạng thái: {status}"
                    ))
                    # Đánh dấu slot đã đăng
                    if current_slot[0] and current_slot[0] in slot_buttons:
                        d, s = current_slot[0]
                        view.after(0, lambda _d=d, _s=s: slot_buttons[(_d,_s)].configure(
                            fg_color="#1D4ED8", text_color="white",
                            text=f"  ✅ Bài {_s}"
                        ))
                else:
                    err_msg = str(result_post) if result_post else "Không phản hồi"
                    view.after(0, lambda: lbl_wp_status.configure(
                        text="❌ Lỗi đăng bài", text_color="#DC2626"
                    ))
                    view.after(0, lambda e=err_msg: messagebox.showerror("Lỗi", f"Không đăng được:\n{e}"))
            except Exception as ex:
                _ex_type = type(ex).__name__
                _ex_msg  = str(ex)
                view.after(0, lambda t=_ex_type: lbl_wp_status.configure(
                    text=f"❌ {t}", text_color="#DC2626"
                ))
                view.after(0, lambda m=_ex_msg: messagebox.showerror(
                    "Lỗi kết nối", f"Lỗi khi đăng bài:\n{m}"
                ))
            finally:
                view.after(0, lambda: btn_post_wp.configure(
                    state="normal", text="🚀 ĐĂNG WORDPRESS"
                ))

        threading.Thread(target=_worker, daemon=True).start()

    btn_post_wp = ctk.CTkButton(
        wp_frame, text="🚀 ĐĂNG WORDPRESS",
        height=38, font=("Segoe UI",11,"bold"),
        fg_color="#1D4ED8", hover_color="#1E40AF",
        text_color="white", corner_radius=8,
        command=_do_post_wp
    )
    btn_post_wp.pack(fill="x", padx=8, pady=(0,8))


    # =========================================================
    # STATE — lưu dữ liệu các slot
    # =========================================================
    slot_data   = {}          # key: (day,slot) -> {title, meta_desc, content_html, ...}
    current_slot = [None]     # (day, slot) đang được chọn
    current_result = {}       # kết quả format của slot đang xem

    def _update_preview(result: dict):
        current_result.clear()
        current_result.update(result)
        lbl_prev_title.configure(text=f"🏷️ {result['title']}")
        lbl_prev_meta.configure(text=f"📝 {result['meta_desc'][:100]}...")
        lbl_wc.configure(text=f"~{result['word_count']} từ")

        # Tính SEO score nhanh
        score = 0
        tips = []
        tl = len(result['title'])
        if 50 <= tl <= 60: score += 25
        elif tl > 0: score += 10
        else: tips.append("Thiếu tiêu đề!")

        ml = len(result['meta_desc'])
        if 120 <= ml <= 160: score += 25
        elif ml > 0: score += 10
        else: tips.append("Meta desc trống")

        h2c = result['content_html'].lower().count("<h2")
        if h2c >= 3: score += 25
        elif h2c > 0: score += 10
        else: tips.append("Nên có ≥3 thẻ H2")

        wc = result['word_count']
        if wc >= 1000: score += 25
        elif wc >= 500: score += 15
        else: tips.append(f"Nội dung ngắn ({wc} từ, nên ≥1000)")

        sc = _score_color(score)
        lbl_score.configure(text=f"SEO Score: {score}/100", text_color=sc)
        lbl_tips_summary.configure(text=" | ".join(tips[:2]) if tips else "✅ Chuẩn SEO!")

        prev_box.configure(state="normal")
        prev_box.delete("1.0","end")
        plain = re.sub(r"<[^>]+>", "", result['content_html'])
        plain = re.sub(r"\n{3,}", "\n\n", plain).strip()
        prev_box.insert("end", plain)
        prev_box.configure(state="disabled")

    def _load_slot(day, slot):
        """Load dữ liệu slot đã lưu vào editor."""
        current_slot[0] = (day, slot)
        lbl_slot.configure(text=f"  ✏️ Ngày {day} — Bài {slot}", text_color=C['primary'])
        if (day, slot) in slot_data:
            d = slot_data[(day, slot)]
            entry_title.delete(0,"end")
            entry_title.insert(0, d.get("title",""))
            entry_meta.delete(0,"end")
            entry_meta.insert(0, d.get("meta_desc_raw",""))
            entry_featured.delete(0,"end")
            entry_featured.insert(0, d.get("featured_img",""))
            for i, ee in enumerate(extra_entries):
                ee.delete(0,"end")
                imgs = d.get("extra_imgs",[])
                if i < len(imgs): ee.insert(0, imgs[i])
            content_box.delete("1.0","end")
            content_box.insert("end", d.get("raw_content",""))
            if d.get("content_html"):
                _update_preview(d)
        else:
            entry_title.delete(0,"end")
            entry_meta.delete(0,"end")
            entry_featured.delete(0,"end")
            for ee in extra_entries: ee.delete(0,"end")
            content_box.delete("1.0","end")

    def _do_format():
        title = entry_title.get().strip()
        if not title:
            messagebox.showwarning("Thiếu tiêu đề","Vui lòng nhập tiêu đề bài viết!")
            return
        raw = content_box.get("1.0","end").strip()
        if not raw:
            messagebox.showwarning("Thiếu nội dung","Vui lòng nhập hoặc import nội dung!")
            return
        meta = entry_meta.get().strip()
        feat = entry_featured.get().strip()
        extras = [e.get().strip() for e in extra_entries]

        btn_format.configure(state="disabled", text="⏳ Đang format...")
        def worker():
            result = _wrap_seo_html(title, raw, feat, extras, meta)
            view.after(0, lambda: _update_preview(result))
            view.after(0, lambda: btn_format.configure(state="normal", text="⚡ Format Chuẩn SEO"))
        threading.Thread(target=worker, daemon=True).start()

    def _do_save_slot():
        if not current_slot[0]:
            messagebox.showwarning("Chưa chọn slot","Hãy chọn slot từ lịch bên trái!")
            return
        if not current_result.get("content_html"):
            messagebox.showwarning("Chưa format","Hãy nhấn ⚡ Format Chuẩn SEO trước!")
            return
        day, slot = current_slot[0]
        slot_data[(day, slot)] = {
            **current_result,
            "raw_content": content_box.get("1.0","end").strip(),
            "meta_desc_raw": entry_meta.get().strip(),
            "featured_img": entry_featured.get().strip(),
            "extra_imgs": [e.get().strip() for e in extra_entries],
            "day": day, "slot": slot,
        }
        # Update button color để đánh dấu đã lưu
        if (day, slot) in slot_buttons:
            slot_buttons[(day, slot)].configure(fg_color="#10B981", text_color="white")
        lbl_stat.configure(text=f"✅ Đã lưu {len(slot_data)}/{TOTAL_POSTS} bài")
        messagebox.showinfo("Đã lưu!",f"Bài Ngày {day} – Bài {slot} đã lưu thành công!")

    btn_format.configure(command=_do_format)
    btn_save_slot.configure(command=_do_save_slot)

    # =========================================================
    # Build lịch pyramid buttons
    # =========================================================
    for day_info in PYRAMID_SCHEDULE:
        d = day_info["day"]
        cnt = day_info["count"]
        bg = day_colors[d]

        hdr = ctk.CTkFrame(sched_scroll, fg_color=bg, corner_radius=8)
        hdr.pack(fill="x", pady=(5,2))
        ctk.CTkLabel(hdr, text=f"📆 {day_info['label']}  ({day_info['desc']})",
                     font=("Segoe UI",9,"bold"), text_color="#1F2937"
                     ).pack(anchor="w", padx=8, pady=3)

        for slot in range(1, cnt + 1):
            def make_cb(dd=d, ss=slot):
                return lambda: _load_slot(dd, ss)
            btn = ctk.CTkButton(
                sched_scroll,
                text=f"  Bài {slot}",
                height=28, font=("Segoe UI",9),
                fg_color=C['bg_dark'], hover_color=C['border'],
                text_color=C['text_secondary'],
                corner_radius=6, anchor="w",
                command=make_cb()
            )
            btn.pack(fill="x", padx=4, pady=1)
            slot_buttons[(d, slot)] = btn


# ── Import hàm _build_ai_seo_tab từ file riêng ──────────────────
try:
    from view._ai_seo_tab import _build_ai_seo_tab
except Exception as _ai_tab_err:
    def _build_ai_seo_tab(view, C, parent):
        import tkinter as _tk
        _tk.Label(parent, text=f"⚠️ Không load được AI SEO tab:\n{_ai_tab_err}",
                  font=("Segoe UI",10), fg="red", bg="#FFFBEB",
                  justify="left").pack(pady=20, padx=20)
