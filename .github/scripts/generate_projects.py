#!/usr/bin/env python3
"""
generate_projects.py — Large-Scale High-Visibility Projects Slate

Generates an enlarged, extra-visible, zero-overlap 6-card master SVG:
  - CARD_H = 256 (Enlarged)
  - Title = 20px bold
  - Description = 13.5px
  - Skills = 11px bold
  - Donut = r:28, stroke:9.5, 13px bold center %
  - Icons = 52px bespoke vectors
"""

import json, os, sys, math, html
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PROJECTS_JSON = os.path.join(ROOT_DIR, 'merged.json' if os.path.exists(os.path.join(ROOT_DIR, 'merged.json')) else 'projects.json')
OUT_DIR = os.path.join(ROOT_DIR, 'assets')

THEMES = {
    "dark": {
        "BG": "#0D0A06",            # Burnt celluloid black
        "PANEL": "#140F09",         # Warm dark chocolate
        "PANEL_BAR": "#110B06",     # Header bar
        "ACCENT_1": "#C0713A",      # Burnt Sienna
        "ACCENT_2": "#D4A353",      # Warm Amber
        "ACCENT_3": "#F5E6D3",      # Cream
        "TEXT": "#F5E6D3",          # Title text
        "MUTED": "#D0BFAD",         # High-contrast readable description
        "DIM": "#8C7B6B",           # Dim metadata
        "STROKE": "rgba(212,163,83,0.40)",
        "STROKE_HI": "rgba(212,163,83,0.88)",
        "STROKE_LO": "rgba(192,113,58,0.28)",
        "BARLINE": "rgba(255,255,255,0.08)",
        "RING_BG": "rgba(156,139,120,0.22)",
        "PILL_BG": "rgba(58,35,18,0.95)",
        "PILL_STROKE": "rgba(212,163,83,0.60)",
        "CAT_BG": "rgba(192,113,58,0.32)",
        "CAT_STROKE": "rgba(192,113,58,0.80)",
        "MONO_TX": "#0D0A06",
        "ICON_BG": "#C0713A",
        "EMERALD": "#5B8C5A",
        "DONUT_COLORS": ["#D4A353", "#C0713A", "#5B8C5A", "#B85C38", "#9C8B78"],
    },
    "light": {
        "BG": "#FAF6F0",            # Vintage warm parchment
        "PANEL": "#FFFFFF",         # Crisp white
        "PANEL_BAR": "#F3ECE2",     # Header bar
        "ACCENT_1": "#8B5A2B",      # Deep sienna
        "ACCENT_2": "#A67B3D",      # Antique gold
        "ACCENT_3": "#C89D66",      # Muted amber
        "TEXT": "#1A1207",          # Deep ink
        "MUTED": "#5A4C3E",         # High-contrast readable bronze
        "DIM": "#9C8B78",           # Dim metadata
        "STROKE": "rgba(166,123,61,0.42)",
        "STROKE_HI": "rgba(166,123,61,0.85)",
        "STROKE_LO": "rgba(139,90,43,0.25)",
        "BARLINE": "rgba(0,0,0,0.08)",
        "RING_BG": "rgba(107,93,79,0.20)",
        "PILL_BG": "rgba(234,219,202,0.85)",
        "PILL_STROKE": "rgba(166,123,61,0.65)",
        "CAT_BG": "rgba(139,90,43,0.20)",
        "CAT_STROKE": "rgba(139,90,43,0.55)",
        "MONO_TX": "#FAF6F0",
        "ICON_BG": "#8B5A2B",
        "EMERALD": "#3D6B3C",
        "DONUT_COLORS": ["#A67B3D", "#8B5A2B", "#3D6B3C", "#B85C38", "#6B5D4F"],
    },
}

W        = 1180
CARD_W   = 576
CARD_H   = 256
GAP      = 16
MARGIN   = 6
FONT     = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

PROJECT_SKILLS = {
    "rdnk2004/NyayaSetu-Multi-Agent": ["Python", "Multi-Agent", "LangChain", "ChromaDB", "Pydantic", "RAG"],
    "rdnk2004/screenwriting-software": ["React", "JavaScript", "Django REST", "Fountain", "PDFKit", "Story Systems"],
    "rdnk2004/cpi-mpc": ["Python", "XGBoost", "Prophet", "SHAP", "Pandas", "Statsmodels", "FastAPI"],
    "rdnk2004/NPA-RBI": ["Python", "Econometrics", "XGBoost", "SHAP", "Scikit-Learn", "Streamlit"],
    "rdnk2004/automated-career": ["Python", "TypeScript", "n8n", "Job APIs", "ATS Parser", "Telemetry"],
    "rdnk2004/nexus-tasktrack": ["Python", "FastAPI", "PostgreSQL", "Docker", "JWT Auth", "SQLAlchemy"]
}

def esc(s):
    return html.escape(str(s), quote=True)

def clean_lang_name(name):
    aliases = {
        "Jupyter Notebook": "Jupyter",
        "JavaScript": "JS",
        "TypeScript": "TS",
        "Dockerfile": "Docker",
    }
    return aliases.get(name, name)

def wrap_text(s, max_chars, max_lines=2):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and words and " ".join(lines).count(" ") + 1 < len(words):
        lines[-1] = lines[-1][:max_chars-1].rstrip() + "…"
    return lines

def render_vector_icon(icon_type, x, y, size=52, bg_col="#C0713A", fg_col="#0D0A06"):
    u = size / 24.0
    parts = []
    a = parts.append
    
    a(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="12" fill="{bg_col}" opacity="0.95"/>')
    
    if icon_type == "justice":
        a(f'<path d="M {x+12*u} {y+4.5*u} L {x+12*u} {y+19.5*u} M {x+8.5*u} {y+19.5*u} L {x+15.5*u} {y+19.5*u} '
          f'M {x+4.5*u} {y+7.5*u} L {x+19.5*u} {y+7.5*u} '
          f'M {x+5.5*u} {y+7.5*u} L {x+3.5*u} {y+12.5*u} M {x+7.5*u} {y+7.5*u} L {x+9.5*u} {y+12.5*u} '
          f'M {x+2.5*u} {y+12.5*u} Q {x+6.5*u} {y+15.5*u} {x+10.5*u} {y+12.5*u} Z '
          f'M {x+16.5*u} {y+7.5*u} L {x+14.5*u} {y+12.5*u} M {x+18.5*u} {y+7.5*u} L {x+20.5*u} {y+12.5*u} '
          f'M {x+13.5*u} {y+12.5*u} Q {x+17.5*u} {y+15.5*u} {x+21.5*u} {y+12.5*u} Z" '
          f'fill="none" stroke="{fg_col}" stroke-width="{1.7*u}" stroke-linecap="round" stroke-linejoin="round"/>')
        a(f'<circle cx="{x+12*u}" cy="{y+4.5*u}" r="{1.5*u}" fill="{fg_col}"/>')

    elif icon_type == "clapper":
        a(f'<rect x="{x+3.5*u}" y="{y+10*u}" width="{17*u}" height="{10*u}" rx="{1.5*u}" fill="{fg_col}"/>')
        a(f'<path d="M {x+3.5*u} {y+5*u} L {x+20.5*u} {y+5*u} L {x+20.5*u} {y+9*u} L {x+3.5*u} {y+9*u} Z" fill="{fg_col}"/>')
        a(f'<line x1="{x+7.5*u}" y1="{y+5*u}" x2="{x+5.5*u}" y2="{y+9*u}" stroke="{bg_col}" stroke-width="{1.6*u}"/>')
        a(f'<line x1="{x+12.5*u}" y1="{y+5*u}" x2="{x+10.5*u}" y2="{y+9*u}" stroke="{bg_col}" stroke-width="{1.6*u}"/>')
        a(f'<line x1="{x+17.5*u}" y1="{y+5*u}" x2="{x+15.5*u}" y2="{y+9*u}" stroke="{bg_col}" stroke-width="{1.6*u}"/>')
        a(f'<line x1="{x+6.5*u}" y1="{y+13*u}" x2="{x+17.5*u}" y2="{y+13*u}" stroke="{bg_col}" stroke-width="{1.4*u}" stroke-linecap="round"/>')
        a(f'<line x1="{x+6.5*u}" y1="{y+16.5*u}" x2="{x+13.5*u}" y2="{y+16.5*u}" stroke="{bg_col}" stroke-width="{1.4*u}" stroke-linecap="round"/>')

    elif icon_type == "chart":
        a(f'<path d="M {x+4*u} {y+19*u} L {x+20*u} {y+19*u} M {x+4*u} {y+5*u} L {x+4*u} {y+19*u}" '
          f'fill="none" stroke="{fg_col}" stroke-width="{2.2*u}" stroke-linecap="round"/>')
        a(f'<path d="M {x+5*u} {y+16*u} L {x+9*u} {y+12*u} L {x+13*u} {y+14*u} L {x+19*u} {y+7*u}" '
          f'fill="none" stroke="{fg_col}" stroke-width="{2.2*u}" stroke-linecap="round" stroke-linejoin="round"/>')
        a(f'<polygon points="{x+19*u},{y+7*u} {x+15*u},{y+7*u} {x+19*u},{y+11*u}" fill="{fg_col}"/>')
        a(f'<circle cx="{x+9*u}" cy="{y+12*u}" r="{1.5*u}" fill="{fg_col}"/>')
        a(f'<circle cx="{x+13*u}" cy="{y+14*u}" r="{1.5*u}" fill="{fg_col}"/>')

    elif icon_type == "bank":
        a(f'<polygon points="{x+12*u},{y+4*u} {x+3*u},{y+8.5*u} {x+21*u},{y+8.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+3*u}" y="{y+8.5*u}" width="{18*u}" height="{1.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+4.5*u}" y="{y+10*u}" width="{2.2*u}" height="{7*u}" rx="{0.4*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+8.8*u}" y="{y+10*u}" width="{2.2*u}" height="{7*u}" rx="{0.4*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+13*u}" y="{y+10*u}" width="{2.2*u}" height="{7*u}" rx="{0.4*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+17.3*u}" y="{y+10*u}" width="{2.2*u}" height="{7*u}" rx="{0.4*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+3*u}" y="{y+17*u}" width="{18*u}" height="{1.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+2*u}" y="{y+18.5*u}" width="{20*u}" height="{2*u}" rx="{0.5*u}" fill="{fg_col}"/>')

    elif icon_type == "career":
        a(f'<rect x="{x+3.5*u}" y="{y+8*u}" width="{17*u}" height="{12*u}" rx="{2*u}" fill="{fg_col}"/>')
        a(f'<path d="M {x+8.5*u} {y+8*u} L {x+8.5*u} {y+5.5*u} Q {x+8.5*u} {y+4*u} {x+10*u} {y+4*u} L {x+14*u} {y+4*u} Q {x+15.5*u} {y+4*u} {x+15.5*u} {y+5.5*u} L {x+15.5*u} {y+8*u}" '
          f'fill="none" stroke="{fg_col}" stroke-width="{2.0*u}"/>')
        a(f'<line x1="{x+3.5*u}" y1="{y+13*u}" x2="{x+20.5*u}" y2="{y+13*u}" stroke="{bg_col}" stroke-width="{1.5*u}"/>')
        a(f'<rect x="{x+10.5*u}" y="{y+11.5*u}" width="{3*u}" height="{3*u}" rx="{0.6*u}" fill="{bg_col}"/>')

    elif icon_type == "kanban":
        a(f'<rect x="{x+3.5*u}" y="{y+4*u}" width="{17*u}" height="{16*u}" rx="{2*u}" '
          f'fill="none" stroke="{fg_col}" stroke-width="{2.2*u}"/>')
        a(f'<line x1="{x+9.5*u}" y1="{y+4*u}" x2="{x+9.5*u}" y2="{y+20*u}" stroke="{fg_col}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+15*u}" y1="{y+4*u}" x2="{x+15*u}" y2="{y+20*u}" stroke="{fg_col}" stroke-width="{1.8*u}"/>')
        a(f'<rect x="{x+5.2*u}" y="{y+7*u}" width="{2.8*u}" height="{4*u}" rx="{0.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+5.2*u}" y="{y+13*u}" width="{2.8*u}" height="{4*u}" rx="{0.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+11*u}" y="{y+7*u}" width="{2.8*u}" height="{6*u}" rx="{0.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+16.5*u}" y="{y+7*u}" width="{2.8*u}" height="{3*u}" rx="{0.5*u}" fill="{fg_col}"/>')

    return "".join(parts)

def donut_segments(languages, cx, cy, r, begin, donut_colors, ring_bg, text_col, muted_col):
    total = sum(languages.values()) or 1
    entries = sorted(languages.items(), key=lambda kv: -kv[1])[:3]
    other = total - sum(v for _, v in entries)
    if other > 0 and len(entries) < 3:
        entries.append(("Other", other))
        
    C = 2 * math.pi * r
    out, legend = [], []
    offset = 0.0
    t = begin
    for i, (lang, v) in enumerate(entries):
        frac = v / total
        seg = frac * C
        col = donut_colors[i % len(donut_colors)]
        out.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="9.5" '
            f'stroke-dasharray="{seg:.2f} {C - seg:.2f}" stroke-dashoffset="{-offset:.2f}" '
            f'transform="rotate(-90 {cx} {cy})" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.01s" begin="{t:.2f}s" fill="freeze"/>'
            f'<animate attributeName="stroke-dasharray" from="0 {C:.2f}" to="{seg:.2f} {C - seg:.2f}" '
            f'dur="0.6s" begin="{t:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.3 0 0.2 1"/>'
            f'</circle>'
        )
        legend.append((clean_lang_name(lang), frac, col))
        offset += seg
        t += 0.16
    return "".join(out), legend

def card(p, x, y, idx, t):
    b = 0.25 + idx * 0.12
    e = []
    a = e.append
    
    repo = p.get("repo", "").strip().replace("https://github.com/", "").rstrip("/")
    href = f"https://github.com/{esc(repo)}"
    
    a(f'<a href="{href}" target="_blank">')
    a(f'<g opacity="0" transform="translate({x},{y})">')
    a(f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{b:.2f}s" fill="freeze"/>')

    # Card Shell
    a(f'<rect width="{CARD_W}" height="{CARD_H}" rx="14" fill="{t["PANEL"]}" stroke="{t["STROKE"]}">'
      f'<animate attributeName="stroke" values="{t["STROKE_LO"]};{t["STROKE_HI"]};{t["STROKE_LO"]}" '
      f'dur="4.5s" begin="{b+idx*0.7:.2f}s" repeatCount="indefinite"/></rect>')
    a(f'<rect width="{CARD_W}" height="36" rx="14" fill="{t["PANEL_BAR"]}"/>')
    a(f'<rect y="22" width="{CARD_W}" height="14" fill="{t["PANEL_BAR"]}"/>')
    a(f'<line x1="0" y1="36" x2="{CARD_W}" y2="36" stroke="{t["BARLINE"]}"/>')
    a(f'<text x="18" y="23" font-size="12" font-weight="600" fill="{t["MUTED"]}"><tspan fill="{t["ACCENT_2"]}">&#8226;</tspan> {esc(repo)}</text>')

    # Top right category pill
    cat = esc(p.get("category", "Project"))
    cat_w = len(cat) * 7.0 + 18
    cat_x = CARD_W - cat_w - 26
    a(f'<rect x="{cat_x}" y="8" width="{cat_w}" height="20" rx="10" fill="{t["CAT_BG"]}" stroke="{t["CAT_STROKE"]}"/>')
    a(f'<text x="{cat_x + cat_w/2:.0f}" y="21.5" text-anchor="middle" font-size="10" font-weight="700" fill="{t["ACCENT_2"]}">{cat}</text>')
    
    # Live pulse dot
    a(f'<circle cx="{CARD_W-14}" cy="18" r="4.5" fill="{t["EMERALD"]}">'
      f'<animate attributeName="opacity" values="1;0.25;1" dur="1.8s" repeatCount="indefinite"/></circle>')

    # Bespoke Domain Vector Icon (Enlarged 52px)
    icon_type = p.get("icon", "justice")
    float_anim = (f'<animateTransform attributeName="transform" type="translate" '
                  f'values="0 0; 0 -3; 0 0" dur="5s" begin="{b+idx*0.5:.2f}s" '
                  f'repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
                  f'keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>')
    a(f'<g>{float_anim}{render_vector_icon(icon_type, 18, 52, 52, t["ICON_BG"], t["MONO_TX"])}</g>')

    # Name + Blinking cursor (Extra-Large 20px font)
    name = esc(p.get("name", "unnamed"))
    a(f'<text x="80" y="74" font-size="20" font-weight="700" fill="{t["TEXT"]}">{name}'
      f'<tspan fill="{t["ACCENT_2"]}">_<animate attributeName="opacity" values="1;0;1" dur="1.2s" '
      f'begin="{b+0.4:.2f}s" repeatCount="indefinite"/></tspan></text>')

    # Description (High contrast 13.5px font wrapped to 32 chars)
    for i, line in enumerate(wrap_text(p.get("description", ""), 32)):
        a(f'<text x="80" y="{98 + i * 20}" font-size="13.5" font-weight="500" fill="{t["MUTED"]}">{esc(line)}</text>')

    # Complete Production Skills (Enlarged pills with 11px font)
    skills = PROJECT_SKILLS.get(repo, p.get("tags", []))
    
    # Row 1 of Skills (max 3 pills)
    tx1 = 80
    row1_skills = skills[:3]
    for tag in row1_skills:
        tw = len(tag) * 7.5 + 16
        a(f'<rect x="{tx1}" y="146" width="{tw:.0f}" height="23" rx="11.5" fill="{t["PILL_BG"]}" stroke="{t["PILL_STROKE"]}"/>')
        a(f'<text x="{tx1 + tw/2:.0f}" y="161" text-anchor="middle" font-size="11" font-weight="700" fill="{t["ACCENT_2"]}">{esc(tag)}</text>')
        tx1 += tw + 8

    # Row 2 of Skills (max 3 pills)
    tx2 = 80
    row2_skills = skills[3:6]
    if row2_skills:
        for tag in row2_skills:
            tw = len(tag) * 7.5 + 16
            a(f'<rect x="{tx2}" y="177" width="{tw:.0f}" height="23" rx="11.5" fill="{t["PILL_BG"]}" stroke="{t["PILL_STROKE"]}"/>')
            a(f'<text x="{tx2 + tw/2:.0f}" y="192" text-anchor="middle" font-size="11" font-weight="700" fill="{t["ACCENT_2"]}">{esc(tag)}</text>')
            tx2 += tw + 8

    # Bottom Row: Quick Action Indicator
    a(f'<text x="80" y="234" font-size="12" font-weight="600" fill="{t["MUTED"]}">'
      f'<tspan fill="{t["ACCENT_2"]}">&#9656;</tspan> Applied Production Stack'
      f'<tspan fill="{t["ACCENT_1"]}" dx="16" font-weight="700">&#8599; View Repository</tspan></text>')

    # Right-Hand Telemetry: Enlarged 28px Radius Donut + Legend Layout
    langs = p.get("languages") or {}
    if langs:
        cx, cy, r = CARD_W - 52, 102, 28
        segs, legend = donut_segments(langs, cx, cy, r, b + 0.3, t["DONUT_COLORS"], t["RING_BG"], t["TEXT"], t["MUTED"])
        a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["RING_BG"]}" stroke-width="9.5"/>')
        a(segs)
        top = legend[0]
        a(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="13" font-weight="800" fill="{t["TEXT"]}">{top[1]*100:.0f}%</text>')
        
        dot_x = cx - r - 100
        text_x = dot_x + 11
        n_items = len(legend[:3])
        start_ly = cy - (n_items - 1) * 11
        for i_l, (lang, frac, col) in enumerate(legend[:3]):
            curr_ly = start_ly + i_l * 22
            a(f'<circle cx="{dot_x}" cy="{curr_ly}" r="4" fill="{col}"/>')
            a(f'<text x="{text_x}" y="{curr_ly+4.5}" font-size="11.5" font-weight="600" fill="{t["MUTED"]}">'
              f'{esc(lang)} <tspan fill="{t["TEXT"]}" font-weight="700">{frac*100:.0f}%</tspan></text>')

    a('</g>')
    a('</a>')
    return "".join(e)

def build_single_slate_svg(projects, theme="dark"):
    t = THEMES[theme]
    rows = math.ceil(len(projects) / 2)
    H = 58 + rows * (CARD_H + GAP) + MARGIN
    gid = f"proj_acc_single_{theme}"
    s = []
    a = s.append
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="{FONT}" role="img" aria-label="Nikhil Krishna R D — Featured Projects &amp; Applied Skills">')
    a(f'<rect width="{W}" height="{H}" fill="{t["BG"]}"/>')
    
    a(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{t["ACCENT_1"]}"><animate attributeName="stop-color" values="{t["ACCENT_1"]};{t["ACCENT_2"]};{t["ACCENT_3"]};{t["ACCENT_1"]}" dur="10s" repeatCount="indefinite"/></stop>'
      f'<stop offset="1" stop-color="{t["ACCENT_2"]}"><animate attributeName="stop-color" values="{t["ACCENT_2"]};{t["ACCENT_3"]};{t["ACCENT_1"]};{t["ACCENT_2"]}" dur="10s" repeatCount="indefinite"/></stop>'
      f'</linearGradient></defs>')
      
    # Single Clean Header with zero collision
    a(f'<text x="{MARGIN+2}" y="20" font-size="12.5" font-weight="700" letter-spacing="2" fill="{t["ACCENT_2"]}">PROJECTS.SLATE // APPLIED.SKILLS</text>')
    a(f'<text x="{W-MARGIN-10}" y="20" text-anchor="end" font-size="11" fill="{t["DIM"]}">./projects.sh --live --traceable</text>')
    a(f'<line x1="{MARGIN}" y1="30" x2="{W-MARGIN}" y2="30" stroke="url(#{gid})" stroke-width="1.8" opacity="0.85"/>')
    
    for i, p in enumerate(projects):
        x = MARGIN + (i % 2) * (CARD_W + GAP)
        y = 46 + (i // 2) * (CARD_H + GAP)
        a(card(p, x, y, i, t))
        
    a('</svg>')
    return "".join(s)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(PROJECTS_JSON, 'r', encoding='utf-8') as f:
        projects = json.load(f)
        
    for theme, fname in [("dark", "projects-dark.svg"), ("light", "projects-light.svg")]:
        svg = build_single_slate_svg(projects, theme)
        out_path = os.path.join(OUT_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f"[OK] {fname} ({os.path.getsize(out_path)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
