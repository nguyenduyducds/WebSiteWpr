import tkinter as tk
import customtkinter as ctk
import threading
import re
from tkinter import messagebox

# =============================================================================
# SUB-TAB 3: AI SEO 100
# =============================================================================
def _build_ai_seo_tab(view, C, parent):
    root = tk.Frame(parent, bg="#F0F9FF")
    root.pack(fill="both", expand=True)
    root.columnconfigure(0, weight=1, minsize=280)
    root.columnconfigure(1, weight=3)
    root.rowconfigure(0, weight=1)

    # ── LEFT PANEL ─────────────────────────────────────────────────
    left = ctk.CTkFrame(root, fg_color="#E0F2FE", corner_radius=12,
                         border_width=2, border_color="#7DD3FC")
    left.grid(row=0, column=0, sticky="nsew", padx=(8,4), pady=8)

    ctk.CTkLabel(left, text="🤖 AI SEO 100",
                 font=("Segoe UI", 13, "bold"), text_color="#0369A1",
                 fg_color="#E0F2FE").pack(anchor="w", padx=12, pady=(12,4))
    ctk.CTkLabel(left, text="Nhập URL bài WordPress để AI\nphân tích và tối ưu đạt 100 điểm",
                 font=("Segoe UI", 9), text_color="#0284C7",
                 fg_color="#E0F2FE", justify="left").pack(anchor="w", padx=12, pady=(0,6))

    ctk.CTkLabel(left, text="🔗 URL bài viết:", font=("Segoe UI",10,"bold"),
                 text_color="#1E40AF", fg_color="#E0F2FE").pack(anchor="w", padx=12)
    entry_url = ctk.CTkEntry(left, placeholder_text="https://yoursite.com/post-slug",
                              height=32, font=("Segoe UI",10), corner_radius=8)
    entry_url.pack(fill="x", padx=12, pady=(2,6))

    ctk.CTkLabel(left, text="🔑 Keyword chính (tùy chọn):", font=("Segoe UI",10,"bold"),
                 text_color="#1E40AF", fg_color="#E0F2FE").pack(anchor="w", padx=12)
    entry_kw = ctk.CTkEntry(left, placeholder_text="Vd: mua xe oto cũ giá rẻ",
                             height=32, font=("Segoe UI",10), corner_radius=8)
    entry_kw.pack(fill="x", padx=12, pady=(2,6))

    ctk.CTkLabel(left, text="🧠 AI Model:", font=("Segoe UI",10,"bold"),
                 text_color="#1E40AF", fg_color="#E0F2FE").pack(anchor="w", padx=12)
    model_var = tk.StringVar(value="gemini-2.5-flash-preview")
    model_cb = ctk.CTkComboBox(left, values=[
        # ── Gemini 2.5 ──
        "gemini-2.5-flash-preview",
        "gemini-2.5-pro-preview",
        # ── Gemini 3 / 3.1 ──
        "gemini-3-pro-preview",
        "gemini-3.1-pro-low",
        "gemini-3-flash-preview",
        # ── Claude ──
        "gemini-claude-sonnet-4-5",
        "gemini-claude-sonnet-4-5-thinking",
        "gemini-claude-opus-4-5-thinking",
        # ── GPT-OSS ──
        "gpt-oss-120b-medium",
    ], variable=model_var, height=30, font=("Segoe UI",9), corner_radius=8, state="readonly")
    model_cb.pack(fill="x", padx=12, pady=(2,8))

    # ── AUTH JSON IMPORT ──────────────────────────────────────────
    import os, json, shutil
    from pathlib import Path
    AUTH_DIR = Path(__file__).resolve().parent.parent / "model" / "antigravity_auths"
    AUTH_DIR.mkdir(parents=True, exist_ok=True)

    auth_sep = tk.Frame(left, bg="#BAE6FD", height=1)
    auth_sep.pack(fill="x", padx=12, pady=(0,4))

    auth_top = tk.Frame(left, bg="#E0F2FE")
    auth_top.pack(fill="x", padx=12)
    ctk.CTkLabel(auth_top, text="🔐 Tài khoản AI:",
                 font=("Segoe UI",10,"bold"), text_color="#1E40AF",
                 fg_color="#E0F2FE").pack(side="left")
    lbl_auth_count = ctk.CTkLabel(auth_top, text="",
                                   font=("Segoe UI",9), text_color="#059669",
                                   fg_color="#E0F2FE")
    lbl_auth_count.pack(side="right")

    auth_list_frame = ctk.CTkScrollableFrame(left, fg_color="#DBEAFE", height=65, corner_radius=6)
    auth_list_frame.pack(fill="x", padx=12, pady=(2,4))

    def _refresh_auth_list():
        for w in auth_list_frame.winfo_children():
            w.destroy()
        files = sorted(AUTH_DIR.glob("*.json"))
        lbl_auth_count.configure(text=f"{len(files)} tài khoản")
        if not files:
            ctk.CTkLabel(auth_list_frame, text="Chưa có tài khoản nào. Import JSON để dùng AI.",
                         font=("Segoe UI",8), text_color="#9CA3AF",
                         fg_color="#DBEAFE", wraplength=200).pack(anchor="w", padx=4, pady=2)
            return
        for fp in files:
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                email = data.get("email", fp.stem)
                row = tk.Frame(auth_list_frame, bg="#DBEAFE")
                row.pack(fill="x", padx=2, pady=1)
                ctk.CTkLabel(row, text=f"✅ {email}",
                             font=("Segoe UI",8), text_color="#1E40AF",
                             fg_color="#DBEAFE", anchor="w").pack(side="left", fill="x", expand=True)
                def _del(p=fp):
                    p.unlink(missing_ok=True)
                    _refresh_auth_list()
                ctk.CTkButton(row, text="✕", width=20, height=18,
                              font=("Segoe UI",8), fg_color="#FEE2E2",
                              hover_color="#FECACA", text_color="#DC2626",
                              corner_radius=4, command=_del).pack(side="right", padx=2)
            except Exception:
                pass

    def _import_auth_json():
        from tkinter import filedialog
        fpath = filedialog.askopenfilename(
            title="Chọn file Auth JSON (antigravity)",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not fpath:
            return
        try:
            data = json.loads(open(fpath, encoding="utf-8").read())
            email = data.get("email", "account")
            safe_name = re.sub(r'[^\w]', '_', email) + ".json"
            dest = AUTH_DIR / safe_name
            shutil.copy2(fpath, dest)
            _refresh_auth_list()
            messagebox.showinfo("✅ Import thành công!", f"Đã thêm: {email}")
        except Exception as ex:
            messagebox.showerror("Lỗi", f"File JSON không hợp lệ:\n{ex}")

    ctk.CTkButton(left, text="📂 Import Auth JSON", height=30,
                  font=("Segoe UI",9,"bold"),
                  fg_color="#3B82F6", hover_color="#2563EB",
                  text_color="white", corner_radius=15,
                  command=_import_auth_json).pack(fill="x", padx=12, pady=(0,6))

    _refresh_auth_list()

    lbl_status = ctk.CTkLabel(left, text="", font=("Segoe UI",9),
                               text_color="#0369A1", fg_color="#E0F2FE",
                               wraplength=220, justify="left")
    lbl_status.pack(fill="x", padx=12, pady=(0,4))

    btn_run = ctk.CTkButton(left, text="🔍 PHÂN TÍCH + AI GỢI Ý", height=42,
                             font=("Segoe UI",11,"bold"),
                             fg_color="#0EA5E9", hover_color="#0284C7",
                             text_color="white", corner_radius=21)
    btn_run.pack(fill="x", padx=12, pady=4)

    btn_apply = ctk.CTkButton(left, text="✅ Apply full SEO lên WordPress", height=36,
                               font=("Segoe UI",10,"bold"),
                               fg_color="#10B981", hover_color="#059669",
                               text_color="white", corner_radius=18, state="disabled")
    btn_apply.pack(fill="x", padx=12, pady=(0,4))

    btn_clear = ctk.CTkButton(left, text="🗑️ Xóa", height=30,
                               font=("Segoe UI",9),
                               fg_color="#F1F5F9", hover_color="#E2E8F0",
                               text_color="#64748B", corner_radius=15,
                               command=lambda: [lbl_status.configure(text=""),
                                                _clear_right()])
    btn_clear.pack(fill="x", padx=12, pady=(0,8))

    # ── RIGHT PANEL ────────────────────────────────────────────────
    right = ctk.CTkFrame(root, fg_color=C['bg_card'], corner_radius=12,
                          border_width=2, border_color=C['border'])
    right.grid(row=0, column=1, sticky="nsew", padx=(4,8), pady=8)
    right.rowconfigure(1, weight=1)
    right.columnconfigure(0, weight=1)

    score_frame = tk.Frame(right, bg=C['bg_card'])
    score_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(10,4))

    lbl_score = ctk.CTkLabel(score_frame, text="Điểm: —/100",
                              font=("Segoe UI",18,"bold"), text_color="#1E293B",
                              fg_color=C['bg_card'])
    lbl_score.pack(side="left")

    lbl_score_badge = ctk.CTkLabel(score_frame, text="",
                                    font=("Segoe UI",11), text_color="white",
                                    fg_color="#94A3B8", corner_radius=10, width=80, height=26)
    lbl_score_badge.pack(side="left", padx=(10,0))

    right_sub = ctk.CTkTabview(right, corner_radius=8, height=30,
                                fg_color="transparent",
                                segmented_button_fg_color="#E2E8F0",
                                segmented_button_selected_color="#0EA5E9",
                                text_color="#374151")
    right_sub.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))

    tab_breakdown  = right_sub.add("📊 Điểm Chi Tiết")
    tab_ai_suggest = right_sub.add("🤖 Gợi Ý AI")
    tab_action     = right_sub.add("⚡ Action Items")
    tab_editor     = right_sub.add("🎨 CSS/HTML Editor")

    scrl_breakdown = ctk.CTkScrollableFrame(tab_breakdown, fg_color="transparent")
    scrl_breakdown.pack(fill="both", expand=True)

    scrl_ai = ctk.CTkScrollableFrame(tab_ai_suggest, fg_color="transparent")
    scrl_ai.pack(fill="both", expand=True)

    scrl_action = ctk.CTkScrollableFrame(tab_action, fg_color="transparent")
    scrl_action.pack(fill="both", expand=True)

    # ── CSS/HTML Editor tab ─────────────────────────────────────────
    editor_wrap = tk.Frame(tab_editor, bg="#1E1E2E")
    editor_wrap.pack(fill="both", expand=True)
    editor_wrap.columnconfigure(0, weight=1)
    editor_wrap.rowconfigure(1, weight=2)
    editor_wrap.rowconfigure(3, weight=1)

    # CSS editor
    css_header = tk.Frame(editor_wrap, bg="#2A2A3E")
    css_header.grid(row=0, column=0, sticky="ew")
    tk.Label(css_header, text="  🎨 CSS Editor  (chỉnh font/màu/layout)",
             bg="#2A2A3E", fg="#7DD3FC",
             font=("Consolas",9,"bold")).pack(side="left", pady=3)
    ctk.CTkButton(css_header, text="↺ Reset CSS mặc định", height=22, width=130,
                  font=("Segoe UI",8), fg_color="#374151", hover_color="#4B5563",
                  text_color="#D1D5DB", corner_radius=4,
                  command=lambda: [css_editor.delete("1.0", "end"),
                                   css_editor.insert("1.0", _DEFAULT_CSS)]
                  ).pack(side="right", padx=4, pady=2)

    css_editor = tk.Text(editor_wrap, bg="#0D1117", fg="#E2E8F0",
                          insertbackground="#7DD3FC", font=("Consolas",9),
                          relief="flat", wrap="none", undo=True,
                          selectbackground="#264F78")
    css_editor.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0,2))
    css_sb = tk.Scrollbar(editor_wrap, command=css_editor.yview)
    css_sb.grid(row=1, column=1, sticky="ns")
    css_editor.configure(yscrollcommand=css_sb.set)

    # HTML editor
    html_header = tk.Frame(editor_wrap, bg="#2A2A3E")
    html_header.grid(row=2, column=0, sticky="ew")
    tk.Label(html_header, text="  📄 HTML Content Preview  (chỉnh trực tiếp)",
             bg="#2A2A3E", fg="#86EFAC",
             font=("Consolas",9,"bold")).pack(side="left", pady=3)

    html_editor = tk.Text(editor_wrap, bg="#0D1117", fg="#D4D4D4",
                           insertbackground="#86EFAC", font=("Consolas",8),
                           relief="flat", wrap="none", undo=True,
                           selectbackground="#264F78", height=8)
    html_editor.grid(row=3, column=0, sticky="nsew", padx=2, pady=(0,2))
    html_sb = tk.Scrollbar(editor_wrap, command=html_editor.yview)
    html_sb.grid(row=3, column=1, sticky="ns")
    html_editor.configure(yscrollcommand=html_sb.set)

    editor_wrap.columnconfigure(1, weight=0)

    _last_result = [None]

    # ── CSS Premium Style (navy + teal — khác FPT Shop) ──
    _DEFAULT_CSS = (
        "@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');\n\n"
        "/* ===== FONT TOÀN SITE ===== */\n"
        "body,.jeg_content,.entry-content,.post-content,.article-content{\n"
        "  font-family:'Be Vietnam Pro',Inter,'Segoe UI',system-ui,sans-serif !important}\n\n"
        "/* ===== TIÊU ĐỀ H1 BÀI VIẾT ===== */\n"
        ".jeg_post_title,.jeg_post_title a,h1.entry-title,h1.post-title,\n"
        ".entry-title,.page-title,.post-title,article h1,\n"
        ".jeg_single_title,.jeg_hero_title{\n"
        "  font-family:'Be Vietnam Pro',sans-serif !important;\n"
        "  font-size:clamp(1.6rem,4vw,2.3rem) !important;\n"
        "  font-weight:800 !important;\n"
        "  color:#0C1F3F !important;\n"
        "  line-height:1.2 !important;\n"
        "  letter-spacing:-0.4px !important;\n"
        "  margin-bottom:.6em !important}\n\n"
        "/* ===== H2 — viền gradient teal, nền nhạt ===== */\n"
        ".jeg_content h2,.entry-content h2,.post-content h2,\n"
        ".seo-post h2,.article-content h2{\n"
        "  font-size:1.4rem !important;\n"
        "  font-weight:700 !important;\n"
        "  color:#0C1F3F !important;\n"
        "  margin:1.8em 0 .6em !important;\n"
        "  padding:.45em 0 .45em 18px !important;\n"
        "  border-left:5px solid #00B4D8 !important;\n"
        "  background:linear-gradient(90deg,rgba(0,180,216,.07),transparent) !important;\n"
        "  border-radius:0 8px 8px 0 !important;\n"
        "  line-height:1.28 !important}\n\n"
        "/* ===== H3 — underline teal ===== */\n"
        ".jeg_content h3,.entry-content h3,.post-content h3,\n"
        ".seo-post h3{\n"
        "  font-size:1.15rem !important;\n"
        "  font-weight:700 !important;\n"
        "  color:#023E58 !important;\n"
        "  margin:1.4em 0 .4em !important;\n"
        "  padding-bottom:.3em !important;\n"
        "  border-bottom:2.5px solid #00B4D8 !important}\n\n"
        "/* ===== PARAGRAPH ===== */\n"
        ".jeg_content p,.entry-content p,.post-content p,.seo-post p{\n"
        "  font-size:16.5px !important;\n"
        "  line-height:1.9 !important;\n"
        "  color:#1C1C2E !important;\n"
        "  margin:0 0 1.2em !important;\n"
        "  text-align:justify !important}\n\n"
        "/* ===== STRONG / BOLD ===== */\n"
        ".jeg_content strong,.entry-content strong,.seo-post strong,\n"
        ".jeg_content b,.entry-content b,.seo-post b{\n"
        "  color:#0077B6 !important; font-weight:700 !important}\n\n"
        "/* ===== ẢNH — bo tròn, shadow ===== */\n"
        ".jeg_content img,.entry-content img,.post-content img,.seo-post img{\n"
        "  max-width:100% !important;\n"
        "  height:auto !important;\n"
        "  border-radius:14px !important;\n"
        "  box-shadow:0 10px 36px rgba(0,119,182,.2),0 2px 8px rgba(0,0,0,.1) !important;\n"
        "  display:block !important;\n"
        "  margin:1.6em auto !important;\n"
        "  transition:transform .3s,box-shadow .3s !important}\n"
        ".jeg_content img:hover,.entry-content img:hover,.seo-post img:hover{\n"
        "  transform:scale(1.015) !important;\n"
        "  box-shadow:0 16px 48px rgba(0,119,182,.28) !important}\n\n"
        "/* ===== LINK ===== */\n"
        ".jeg_content a,.entry-content a,.seo-post a{\n"
        "  color:#0077B6 !important;\n"
        "  text-decoration:none !important;\n"
        "  border-bottom:1.5px solid rgba(0,119,182,.3) !important;\n"
        "  transition:color .2s,border-color .2s !important}\n"
        ".jeg_content a:hover,.entry-content a:hover,.seo-post a:hover{\n"
        "  color:#00B4D8 !important;\n"
        "  border-bottom-color:#00B4D8 !important}\n\n"
        "/* ===== BLOCKQUOTE ===== */\n"
        ".jeg_content blockquote,.entry-content blockquote,.seo-post blockquote{\n"
        "  border:none !important;\n"
        "  background:linear-gradient(135deg,#EFF9FF,#E0F2FE) !important;\n"
        "  border-left:5px solid #0077B6 !important;\n"
        "  padding:1.1em 1.6em !important;\n"
        "  margin:1.5em 0 !important;\n"
        "  border-radius:0 14px 14px 0 !important;\n"
        "  font-style:italic !important;\n"
        "  color:#0C1F3F !important;\n"
        "  font-size:.97em !important}\n\n"
        "/* ===== LIST ===== */\n"
        ".jeg_content ul,.entry-content ul,.seo-post ul{\n"
        "  list-style:none !important; padding-left:0 !important}\n"
        ".jeg_content ul li,.entry-content ul li,.seo-post ul li{\n"
        "  padding:.35em 0 .35em 1.7em !important;\n"
        "  position:relative !important; line-height:1.75 !important}\n"
        ".jeg_content ul li::before,.entry-content ul li::before,.seo-post ul li::before{\n"
        "  content:'▸' !important; color:#00B4D8 !important;\n"
        "  position:absolute !important; left:0 !important; font-size:1.1em !important}\n\n"
        "/* ===== TABLE ===== */\n"
        ".jeg_content table,.entry-content table,.seo-post table{\n"
        "  width:100% !important; border-collapse:collapse !important;\n"
        "  margin:1.5em 0 !important; font-size:.93em !important;\n"
        "  border-radius:10px !important; overflow:hidden !important;\n"
        "  box-shadow:0 2px 12px rgba(0,0,0,.08) !important}\n"
        ".jeg_content thead th,.entry-content thead th,.seo-post thead th{\n"
        "  background:#0077B6 !important; color:#fff !important;\n"
        "  padding:.65em 1em !important; text-align:left !important}\n"
        ".jeg_content tbody tr:nth-child(even),.entry-content tbody tr:nth-child(even){\n"
        "  background:#F0F9FF !important}\n"
        ".jeg_content td,.entry-content td,.seo-post td{\n"
        "  padding:.55em 1em !important; border-bottom:1px solid #BFDBFE !important}\n\n"
        "/* ===== FAQ & EXTRA CONTENT BOX ===== */\n"
        ".seo-post .faq-block,.faq-block{\n"
        "  background:#EFF9FF !important; border:1px solid #BAE6FD !important;\n"
        "  border-radius:16px !important; padding:1.5em 2em !important; margin:2em 0 !important}\n"
        ".seo-post .seo-extra-content{\n"
        "/* Responsive */\n"
        "@media(max-width:640px){\n"
        "  .seo-post{font-size:15px}\n"
        "  .seo-post h2{font-size:1.2rem}\n"
        "  .seo-post img{border-radius:8px}}\n"
    )
    css_editor.insert("1.0", _DEFAULT_CSS)


    def _clear_right():
        for w in scrl_breakdown.winfo_children(): w.destroy()
        for w in scrl_ai.winfo_children(): w.destroy()
        for w in scrl_action.winfo_children(): w.destroy()
        html_editor.delete("1.0", "end")
        lbl_score.configure(text="Điểm: —/100")
        lbl_score_badge.configure(text="", fg_color="#94A3B8")
        btn_apply.configure(state="disabled")

    def _render_breakdown(score_result):
        for w in scrl_breakdown.winfo_children(): w.destroy()
        score = score_result.get('score', 0)
        pb_bg = tk.Frame(scrl_breakdown, bg="#E2E8F0", height=12)
        pb_bg.pack(fill="x", padx=8, pady=(4,2))
        pb_color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
        tk.Frame(pb_bg, bg=pb_color, height=12).place(relwidth=score/100, relheight=1)

        for item in score_result.get('breakdown', []):
            row = tk.Frame(scrl_breakdown, bg="white")
            row.pack(fill="x", padx=6, pady=1)
            icon = "✅" if item['ok'] else "❌"
            pct = item['points'] / item['max'] if item['max'] else 0
            bar_color = "#10B981" if pct >= 0.8 else "#F59E0B" if pct >= 0.4 else "#EF4444"
            ctk.CTkLabel(row, text=f"{icon} {item['name']}", width=130,
                         font=("Segoe UI",9,"bold"), fg_color="white",
                         text_color="#1E293B", anchor="w").pack(side="left", padx=4)
            mb = tk.Frame(row, bg="#E2E8F0", height=8, width=80)
            mb.pack(side="left", padx=2)
            tk.Frame(mb, bg=bar_color, height=8, width=int(80*pct)).place(x=0, y=0)
            ctk.CTkLabel(row, text=f"{item['points']}/{item['max']}",
                         font=("Segoe UI",9), fg_color="white",
                         text_color="#6B7280", width=38).pack(side="left")
            ctk.CTkLabel(row, text=item['note'], font=("Segoe UI",8),
                         fg_color="white", text_color="#4B5563",
                         anchor="w").pack(side="left", fill="x", expand=True, padx=2)

    def _render_ai_suggestions(ai_sug):
        for w in scrl_ai.winfo_children(): w.destroy()
        if not ai_sug:
            ctk.CTkLabel(scrl_ai, text="Chưa có gợi ý AI.",
                         font=("Segoe UI",10), text_color="#6B7280").pack(pady=20)
            return
        raw = ai_sug.get('raw')
        if raw:
            tb = ctk.CTkTextbox(scrl_ai, font=("Segoe UI",9), wrap="word", height=300)
            tb.pack(fill="both", expand=True, padx=6, pady=4)
            tb.insert("end", raw)
            tb.configure(state="disabled")
            return

        fields = [
            ("🏷️ Title tối ưu",     ai_sug.get('optimized_title',''),    "#1D4ED8"),
            ("📝 Meta Description",  ai_sug.get('optimized_meta_desc',''), "#047857"),
            ("🔑 Keyword gợi ý",     ai_sug.get('suggested_keyword',''),   "#9333EA"),
            ("H1 gợi ý",             ai_sug.get('h1_suggestion',''),       "#B45309"),
            ("📊 Phân tích",         ai_sug.get('score_analysis',''),      "#374151"),
        ]
        for label, content, color in fields:
            if not content: continue
            f = tk.Frame(scrl_ai, bg="#F8FAFC", bd=1, relief="flat")
            f.pack(fill="x", padx=6, pady=3)
            ctk.CTkLabel(f, text=label, font=("Segoe UI",9,"bold"),
                         text_color=color, fg_color="#F8FAFC").pack(anchor="w", padx=8, pady=(4,0))
            ctk.CTkLabel(f, text=content, font=("Segoe UI",9), wraplength=450,
                         text_color="#1E293B", fg_color="#F8FAFC",
                         justify="left", anchor="w").pack(anchor="w", padx=8, pady=(0,4))

        h2s = ai_sug.get('h2_suggestions', [])
        if h2s:
            f = tk.Frame(scrl_ai, bg="#F8FAFC", bd=1, relief="flat")
            f.pack(fill="x", padx=6, pady=3)
            ctk.CTkLabel(f, text="📋 H2 gợi ý", font=("Segoe UI",9,"bold"),
                         text_color="#0369A1", fg_color="#F8FAFC").pack(anchor="w", padx=8, pady=(4,0))
            for i, h2 in enumerate(h2s):
                ctk.CTkLabel(f, text=f"  {i+1}. {h2}", font=("Segoe UI",9),
                             text_color="#1E293B", fg_color="#F8FAFC", anchor="w"
                             ).pack(anchor="w", padx=8)
            tk.Frame(f, height=4, bg="#F8FAFC").pack()

        add_content = ai_sug.get('content_to_add', '')
        if add_content:
            f = tk.Frame(scrl_ai, bg="#F0FDF4", bd=1, relief="flat")
            f.pack(fill="x", padx=6, pady=3)
            ctk.CTkLabel(f, text="📝 Nội dung nên thêm:", font=("Segoe UI",9,"bold"),
                         text_color="#15803D", fg_color="#F0FDF4").pack(anchor="w", padx=8, pady=(4,0))
            tb2 = ctk.CTkTextbox(f, height=80, font=("Segoe UI",9), fg_color="#F0FDF4", wrap="word")
            tb2.pack(fill="x", padx=6, pady=(0,4))
            tb2.insert("end", add_content)
            tb2.configure(state="disabled")

        # CSS preview
        css = ai_sug.get('css_style', '')
        if css and len(css) > 50:
            f = tk.Frame(scrl_ai, bg="#1E293B", bd=1, relief="flat")
            f.pack(fill="x", padx=6, pady=3)
            ctk.CTkLabel(f, text="🎨 CSS từ AI:", font=("Segoe UI",9,"bold"),
                         text_color="#7DD3FC", fg_color="#1E293B").pack(anchor="w", padx=8, pady=(4,0))
            tb3 = ctk.CTkTextbox(f, height=100, font=("Courier New",8), fg_color="#0F172A",
                                  text_color="#E2E8F0", wrap="none")
            tb3.pack(fill="x", padx=6, pady=(0,4))
            tb3.insert("end", css[:500] + ("..." if len(css) > 500 else ""))
            tb3.configure(state="disabled")

    def _render_actions(ai_sug):
        for w in scrl_action.winfo_children(): w.destroy()
        if not ai_sug:
            ctk.CTkLabel(scrl_action, text="Chưa có action items.", font=("Segoe UI",10),
                         text_color="#6B7280").pack(pady=20)
            return
        est = ai_sug.get('estimated_score_after', '?')
        ctk.CTkLabel(scrl_action, text=f"🎯 Ước tính điểm sau tối ưu: {est}/100",
                     font=("Segoe UI",11,"bold"), text_color="#0369A1").pack(pady=(8,4))
        for i, action in enumerate(ai_sug.get('action_items', [])):
            row = tk.Frame(scrl_action, bg="#F0F9FF")
            row.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row, text=f"  {i+1}.", width=28, font=("Segoe UI",10,"bold"),
                         text_color="#0284C7", fg_color="#F0F9FF").pack(side="left")
            ctk.CTkLabel(row, text=action, font=("Segoe UI",10),
                         text_color="#1E293B", fg_color="#F0F9FF",
                         anchor="w", justify="left", wraplength=420).pack(side="left", fill="x", expand=True)

    # ── FIX SEO CONTENT ────────────────────────────────────────────
    def _fix_seo_content(html_content: str, ai_sug: dict, seo_data: dict) -> str:
        """Fix HTML toàn diện: CSS đẹp, H1, alt text, content, FAQ, schema."""
        if not html_content:
            return html_content

        kw = ai_sug.get('suggested_keyword', '')

        # 1. Xóa H1 thừa (WP tự thêm H1 từ title field)
        html_content = re.sub(r'<h1[^>]*>.*?</h1>', '', html_content,
                               flags=re.DOTALL | re.IGNORECASE)

        # 2. Remove old schema nếu AI cung cấp schema mới
        schema_override = ai_sug.get('schema_override', '')
        if schema_override:
            html_content = re.sub(
                r'<script[^>]*application/ld\+json[^>]*>.*?</script>',
                '', html_content, flags=re.DOTALL | re.IGNORECASE
            )

        # 3. Fix alt text + lazy loading cho ảnh
        alt_suggestions = ai_sug.get('alt_text_suggestions', [])
        alt_idx = [0]

        def _fix_img(m):
            tag = m.group(0)
            has_good_alt = re.search(r'alt=["\']([^"\']{3,})["\']', tag, re.IGNORECASE)
            if not has_good_alt:
                alt = (alt_suggestions[alt_idx[0]]
                       if alt_idx[0] < len(alt_suggestions)
                       else (kw or 'image'))
                alt_idx[0] += 1
                alt = alt.replace('"', '&quot;')
                if re.search(r'alt=["\']["\']', tag):
                    tag = re.sub(r'alt=["\']["\']', f'alt="{alt}"', tag)
                elif 'alt=' not in tag.lower():
                    tag = re.sub(r'\s*/?>$', f' alt="{alt}">', tag.rstrip())
            if 'loading=' not in tag.lower():
                tag = re.sub(r'\s*/?>$', ' loading="lazy">', tag.rstrip())
            return tag

        html_content = re.sub(r'<img[^>]+>', _fix_img, html_content, flags=re.IGNORECASE)

        # 4. Thêm nội dung AI nếu bài ngắn
        add_content = ai_sug.get('content_to_add', '')
        word_count  = seo_data.get('word_count', 0)
        if add_content and word_count < 1200:
            html_content = html_content.rstrip() + (
                '\n<section class="seo-extra-content">'
                f'<p>{add_content}</p>'
                '</section>'
            )

        # 5. Thêm FAQ block (featured snippet + schema FAQPage)
        faq_block = ai_sug.get('faq_block', '')
        if faq_block:
            html_content = html_content.rstrip() + f'\n{faq_block}'

        # 6. CSS: đọc từ css_editor (user có thể chỉnh trực tiếp)
        css_from_ai = ai_sug.get('css_style', '')
        css_from_editor = css_editor.get("1.0", "end").strip()
        if '/* AI CSS gợi ý:' in css_from_editor:
            css_from_editor = css_from_editor.split('/* AI CSS gợi ý:')[0].strip()
        custom_css = css_from_ai if (css_from_ai and len(css_from_ai) > 100) else (css_from_editor or _DEFAULT_CSS)
        css_block = f'<style>\n{custom_css}\n</style>\n'

        # 7. Wrap trong .seo-post nếu chưa có
        if 'class="seo-post"' not in html_content and "class='seo-post'" not in html_content:
            html_content = f'<div class="seo-post">\n{html_content}\n</div>'

        # 8. Ghép: schema_override (nếu có) + CSS + content
        prefix = ''
        if schema_override:
            prefix = schema_override + '\n'
        prefix += css_block

        return (prefix + html_content).strip()


    # ── ON RUN ───────────────────────────────────────────────────────
    def _on_run():
        url = entry_url.get().strip()
        if not url or not url.startswith('http'):
            messagebox.showwarning("Thiếu URL", "Vui lòng nhập URL bài WordPress hợp lệ!")
            return

        btn_run.configure(state="disabled", text="⏳ Đang phân tích...")
        btn_apply.configure(state="disabled")
        _clear_right()

        def _worker():
            try:
                from model.ai_seo_checker import ai_analyze
                from model.modelAi import AntigravityDirectClient

                def prog(msg):
                    view.after(0, lambda m=msg: lbl_status.configure(text=m))

                ai_client = AntigravityDirectClient()
                result = ai_analyze(
                    url=url,
                    ai_client=ai_client,
                    model=model_var.get(),
                    keyword=entry_kw.get().strip(),
                    on_progress=prog
                )
                _last_result[0] = result

                if result.get('error'):
                    view.after(0, lambda e=result['error']: messagebox.showerror("Lỗi", e))
                    return

                score_result = result.get('score_result', {})
                ai_sug       = result.get('ai_suggestions', {})
                score        = score_result.get('score', 0)

                badge_color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
                badge_text  = "Tốt 🌟" if score >= 80 else "TB ⚠️" if score >= 60 else "Yếu ❌"

                view.after(0, lambda s=score, bc=badge_color, bt=badge_text: [
                    lbl_score.configure(text=f"Điểm: {s}/100"),
                    lbl_score_badge.configure(text=bt, fg_color=bc)
                ])
                view.after(0, lambda sr=score_result: _render_breakdown(sr))
                view.after(0, lambda s=ai_sug: _render_ai_suggestions(s))
                view.after(0, lambda s=ai_sug: _render_actions(s))
                view.after(0, lambda: btn_apply.configure(state="normal"))
                view.after(0, lambda: lbl_status.configure(
                    text=f"✅ Xong! Sẵn sàng Apply lên WordPress"))

                # Populate HTML editor với nội dung bài (tạm thời fetch lại)
                seo_body = result.get('seo_data', {}).get('body_text', '')[:2000]
                if ai_sug and not ai_sug.get('raw'):
                    css_hint = (f"/* AI CSS gợi ý: */\n"
                                + ai_sug.get('css_style',
                                             '/* (AI chưa tạo CSS — đang dùng CSS mặc định ở editor) */'
                                ))
                    view.after(0, lambda c=css_hint: (
                        css_editor.delete("1.0", "end"),
                        css_editor.insert("1.0", _DEFAULT_CSS + "\n\n" + c)
                    ))
                # Hiển thị HTML mẫu trong HTML editor
                view.after(0, lambda b=seo_body: (
                    html_editor.delete("1.0", "end"),
                    html_editor.insert("1.0",
                        "<!-- Nội dung sẽ được fetch từ WP khi Apply -->\n"
                        "<!-- Bạn có thể sửa CSS ở ô trên rồi nhấn Apply -->\n\n"
                        f"<!-- Preview nội dung (700 từ đầu): -->\n{b}")
                ))


            except Exception as ex:
                _ex = str(ex)
                view.after(0, lambda m=_ex: lbl_status.configure(text=f"❌ {m}"))
                view.after(0, lambda m=_ex: messagebox.showerror("Lỗi", m))
            finally:
                view.after(0, lambda: btn_run.configure(state="normal",
                                                         text="🔍 PHÂN TÍCH + AI GỢI Ý"))

        threading.Thread(target=_worker, daemon=True).start()

    # ── ON APPLY (Full SEO Fix) ──────────────────────────────────────
    def _on_apply():
        result = _last_result[0]
        if not result or not result.get('ai_suggestions'):
            messagebox.showwarning("Chưa có dữ liệu", "Hãy phân tích bài trước!")
            return
        ai_sug   = result['ai_suggestions']
        seo_data = result.get('seo_data', {})
        if ai_sug.get('raw'):
            messagebox.showwarning("AI text mode", "AI trả lời dạng text, không thể auto-apply!")
            return

        ctrl = getattr(view, 'controller', None)
        wp   = getattr(ctrl, 'rest_client', None) if ctrl else None
        if not wp:
            messagebox.showwarning("Chưa đăng nhập", "Hãy đăng nhập WordPress trước!")
            return

        page_url = entry_url.get().strip()

        def _get_post_id(purl, wpc):
            m = re.search(r'[?&]p=(\d+)', purl)
            if m: return int(m.group(1))
            try:
                api_base = wpc.posts_endpoint.replace('/posts', '')
                r = wpc.session.get(f"{api_base}/posts",
                    params={'link': purl, 'per_page': 1}, timeout=10, verify=False)
                if r.status_code == 200:
                    d = r.json()
                    if d and isinstance(d, list): return d[0].get('id')
            except Exception: pass
            from urllib.parse import urlparse
            path = urlparse(purl).path
            nums = [int(x) for x in re.findall(r'(\d+)', path) if int(x) > 100]
            return max(nums) if nums else None

        post_id = _get_post_id(page_url, wp)
        if not post_id:
            messagebox.showwarning("Không lấy được Post ID",
                "Không tìm được Post ID.\nThêm ?p=ID vào URL hoặc dùng: site.com/?p=1234")
            return

        btn_apply.configure(state="disabled", text="⏳ Đang fix SEO (CSS + content)...")
        lbl_status.configure(text=f"⏳ Lấy nội dung Post #{post_id}...")

        def _apply_worker():
            try:
                import base64
                import urllib3 as _urllib3
                _urllib3.disable_warnings()

                headers = {'Content-Type': 'application/json'}
                nonce = getattr(wp, 'nonce', None)
                if nonce:
                    headers['X-WP-Nonce'] = nonce
                else:
                    creds = f"{wp.username}:{wp.password}"
                    headers['Authorization'] = 'Basic ' + base64.b64encode(creds.encode()).decode()

                # Bước 1: Lấy nội dung hiện tại
                view.after(0, lambda: lbl_status.configure(text="📥 Lấy nội dung bài..."))
                get_r = wp.session.get(
                    f"{wp.posts_endpoint}/{post_id}",
                    headers=headers, timeout=15, verify=False
                )
                if get_r.status_code != 200:
                    view.after(0, lambda c=get_r.status_code: messagebox.showerror(
                        "Lỗi", f"Không lấy được bài ({c})"))
                    return

                post_data   = get_r.json()
                raw_content = (post_data.get('content', {}).get('raw') or
                               post_data.get('content', {}).get('rendered', ''))

                # Bước 2: Fix nội dung toàn diện
                view.after(0, lambda: lbl_status.configure(
                    text="🔧 Fix H1 + Alt + CSS + FAQ + Schema..."))
                fixed_content = _fix_seo_content(raw_content, ai_sug, seo_data)

                # ── Bước 3: Build patch toàn diện ─────────────────────────
                patch = {'content': fixed_content}
                yoast = {}
                items_auto = []

                # (A) Meta Description — tự sinh nếu AI không cung cấp hoặc bài đang trống
                new_desc = ai_sug.get('optimized_meta_desc', '').strip()
                cur_meta = seo_data.get('meta_desc', '')
                if not new_desc or len(new_desc) < 80:
                    # Fallback: lấy từ body text
                    body = seo_data.get('body_text', '')
                    # Cắt ở khoảng trắng gần 155 ký tự
                    if len(body) > 80:
                        cut = body[:158].rsplit(' ', 1)[0]
                        new_desc = cut + '…' if len(cut) > 50 else ''
                if new_desc and (not cur_meta or len(cur_meta) < 80):
                    patch['excerpt'] = new_desc
                    yoast['_yoast_wpseo_metadesc'] = new_desc
                    items_auto.append("✅ Meta Description (tự tạo từ content)")
                elif new_desc:
                    patch['excerpt'] = new_desc
                    yoast['_yoast_wpseo_metadesc'] = new_desc
                    items_auto.append("✅ Meta Description (AI gợi ý)")

                # (B) Yoast SEO Title — rút ngắn cho <title> tag (KHÔNG thay H1 visible)
                # Nếu title hiện tại > 60 ký tự → dùng AI optimized hoặc tự cắt
                cur_title = post_data.get('title', {}).get('rendered', '') or \
                            post_data.get('title', {}).get('raw', '')
                ai_title  = ai_sug.get('optimized_title', '').strip()
                if len(cur_title) > 60 or not ai_title:
                    if ai_title and 30 <= len(ai_title) <= 70:
                        yoast['_yoast_wpseo_title'] = ai_title
                        items_auto.append(f"✅ Yoast SEO Title ({len(ai_title)} ký tự, không thay H1)")
                    elif len(cur_title) > 60:
                        # Tự cắt tại từ gần nhất trước 57 ký tự
                        short = cur_title[:57].rsplit(' ', 1)[0] + '...'
                        yoast['_yoast_wpseo_title'] = short
                        items_auto.append(f"✅ Yoast SEO Title (rút ngắn → {len(short)} ký tự)")

                # (C) Focus Keyword
                kw = ai_sug.get('suggested_keyword', entry_kw.get().strip())
                if kw:
                    yoast['_yoast_wpseo_focuskw'] = kw
                    items_auto.append(f"✅ Focus Keyword: \"{kw}\"")

                # (D) Open Graph (nếu OG chưa đủ)
                if not seo_data.get('og_title'):
                    yoast['_yoast_wpseo_opengraph-title'] = ai_title or cur_title
                if not seo_data.get('og_desc') and new_desc:
                    yoast['_yoast_wpseo_opengraph-description'] = new_desc

                if yoast:
                    patch['meta'] = yoast

                # (E) Tổng kết items visual
                items_auto.append("✅ CSS đẹp (font/màu/size tiêu đề + nội dung)")
                items_auto.append("✅ Alt text ảnh (tự điền nếu thiếu)")
                if ai_sug.get('faq_block'):       items_auto.append("✅ FAQ block + Schema FAQPage")
                if ai_sug.get('schema_override'): items_auto.append("✅ Schema JSON-LD thay thế")
                if ai_sug.get('content_to_add'):  items_auto.append("✅ Nội dung thêm")
                items_auto.append("ℹ️ H1 tiêu đề: GIỮ NGUYÊN chữ người dùng viết")


                # ── Bước 4: INJECT CSS qua WordPress Additional CSS ────────
                # WP sẽ strip <style> khỏi post content → phải dùng Additional CSS API
                view.after(0, lambda: lbl_status.configure(text="🎨 Đang inject CSS vào WordPress..."))
                css_for_wp = css_editor.get("1.0", "end").strip()
                if '/* AI CSS gợi ý:' in css_for_wp:
                    css_for_wp = css_for_wp.split('/* AI CSS gợi ý:')[0].strip()
                if not css_for_wp:
                    css_for_wp = _DEFAULT_CSS
                css_ok = False
                api_base = wp.posts_endpoint.replace('/posts', '')

                # Method A: /wp/v2/custom_css (WP 4.7+)
                try:
                    # Lấy active theme slug
                    theme_r = wp.session.get(f"{api_base}/themes?status=active",
                                              headers=headers, timeout=8, verify=False)
                    theme_slug = 'default'
                    if theme_r.status_code == 200:
                        themes = theme_r.json()
                        if themes:
                            theme_slug = themes[0].get('stylesheet', 'default')

                    # Check existing custom CSS post
                    css_r = wp.session.get(f"{api_base}/custom_css/{theme_slug}",
                                            headers=headers, timeout=8, verify=False)
                    if css_r.status_code == 200:
                        existing = css_r.json().get('content', {})
                        existing_raw = existing.get('raw', '') if isinstance(existing, dict) else str(existing)
                        # Thêm block CSS của chúng ta (không xóa CSS cũ)
                        marker_start = '/* === SEO-FIXER CSS START === */'
                        marker_end   = '/* === SEO-FIXER CSS END === */'
                        new_block = f"{marker_start}\n{css_for_wp}\n{marker_end}"
                        if marker_start in existing_raw:
                            import re as _re
                            new_css = _re.sub(
                                r'/\* === SEO-FIXER CSS START === \*/.*?/\* === SEO-FIXER CSS END === \*/',
                                new_block, existing_raw, flags=_re.DOTALL
                            )
                        else:
                            new_css = existing_raw + '\n\n' + new_block
                        upd_r = wp.session.put(
                            f"{api_base}/custom_css/{theme_slug}",
                            json={'content': new_css}, headers=headers, timeout=15, verify=False
                        )
                        if upd_r.status_code in [200, 201]:
                            css_ok = True
                            items_auto.append("✅ CSS injected vào WordPress Additional CSS ✨")
                    elif css_r.status_code == 404:
                        # Tạo mới
                        new_block = f"/* === SEO-FIXER CSS START === */\n{css_for_wp}\n/* === SEO-FIXER CSS END === */"
                        cr_r = wp.session.post(f"{api_base}/custom_css",
                            json={'title': f'SEO CSS - {theme_slug}',
                                  'content': new_block, 'slug': theme_slug},
                            headers=headers, timeout=15, verify=False)
                        if cr_r.status_code in [200, 201]:
                            css_ok = True
                            items_auto.append("✅ CSS injected vào WordPress Additional CSS ✨")
                except Exception as _ce:
                    pass  # Thử method B

                # Method B: /wp/v2/settings (fallback)
                if not css_ok:
                    try:
                        set_r = wp.session.get(f"{api_base}/settings",
                                                headers=headers, timeout=8, verify=False)
                        if set_r.status_code == 200:
                            css_post_id = set_r.json().get('custom_css_post_id', 0)
                            if css_post_id:
                                new_block = f"/* === SEO-FIXER CSS START === */\n{css_for_wp}\n/* === SEO-FIXER CSS END === */"
                                wp.session.post(f"{api_base}/custom_css/{css_post_id}",
                                    json={'content': new_block},
                                    headers=headers, timeout=15, verify=False)
                                css_ok = True
                                items_auto.append("✅ CSS injected via Settings API ✨")
                    except Exception:
                        pass

                if not css_ok:
                    # Method C: Nhét CSS html vào content thô (WP admin thường có unfiltered_html)
                    items_auto.append("⚠️ CSS injected vào content (WP có thể lọc)")

                # ── Bước 5: POST content + meta lên WP ─────────────────────
                view.after(0, lambda: lbl_status.configure(text="📤 Đang cập nhật bài viết..."))
                resp = wp.session.post(
                    f"{wp.posts_endpoint}/{post_id}",
                    json=patch, headers=headers, timeout=40, verify=False
                )
                if resp.status_code in [200, 201]:
                    updated = resp.json()
                    new_url = updated.get('link', page_url)
                    msg = (f"🎉 ĐÃ FIX FULL SEO Post #{post_id}!\n\n"
                           + "\n".join(items_auto)
                           + f"\n\n🔗 {new_url}")
                    view.after(0, lambda m=msg: messagebox.showinfo("✅ Apply Thành Công!", m))
                    view.after(0, lambda: lbl_status.configure(
                        text=f"🎉 Full SEO applied! Post #{post_id}"))
                else:
                    err = f"Lỗi {resp.status_code}:\n{resp.text[:300]}"
                    view.after(0, lambda e=err: messagebox.showerror("Lỗi", e))
                    view.after(0, lambda c=resp.status_code: lbl_status.configure(
                        text=f"❌ Lỗi {c}"))

            except Exception as ex:
                _ex = str(ex)
                view.after(0, lambda m=_ex: messagebox.showerror("Lỗi apply", m))
                view.after(0, lambda m=_ex: lbl_status.configure(text=f"❌ {m}"))
            finally:
                view.after(0, lambda: btn_apply.configure(
                    state="normal", text="✅ Apply full SEO lên WordPress"))

        threading.Thread(target=_apply_worker, daemon=True).start()

    btn_run.configure(command=_on_run)
    btn_apply.configure(command=_on_apply)
