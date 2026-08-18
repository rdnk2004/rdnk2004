#!/usr/bin/env python3
"""
generate_projects.py — The Director's Cut Projects Grid Generator

Generates theme-aware, animated SVG project showcases from live GitHub data:
  assets/projects-dark.svg
  assets/projects-light.svg
"""

import json, os, sys, math, html
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PROJECTS_JSON = os.path.join(ROOT_DIR, 'merged.json' if os.path.exists(os.path.join(ROOT_DIR, 'merged.json')) else 'projects.json')
OUT_DIR = os.path.join(ROOT_DIR, 'assets')

# ---------------- Theme Configurations ----------------
THEMES = {
    "dark": {
        "BG": "#0D0A06",            # Burnt celluloid black
        "PANEL": "#140F09",         # Warm dark chocolate
        "PANEL_BAR": "#100B06",     # Header bar
        "ACCENT_1": "#C0713A",      # Burnt Sienna
        "ACCENT_2": "#D4A353",      # Warm Amber
        "ACCENT_3": "#F5E6D3",      # Cream
        "TEXT": "#F5E6D3",          # Title text
        "MUTED": "#9C8B78",         # Muted description
        "DIM": "#6B5D4F",           # Dim metadata
        "STROKE": "rgba(212,163,83,0.30)",
        "STROKE_HI": "rgba(212,163,83,0.65)",
        "STROKE_LO": "rgba(192,113,58,0.25)",
        "BARLINE": "rgba(255,255,255,0.08)",
        "RING_BG": "rgba(156,139,120,0.18)",
        "PILL_BG": "rgba(58,35,18,0.75)",
        "PILL_STROKE": "rgba(212,163,83,0.45)",
        "CAT_BG": "rgba(192,113,58,0.25)",
        "CAT_STROKE": "rgba(192,113,58,0.60)",
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
        "MUTED": "#6B5D4F",         # Muted bronze
        "DIM": "#9C8B78",           # Dim metadata
        "STROKE": "rgba(166,123,61,0.35)",
        "STROKE_HI": "rgba(166,123,61,0.70)",
        "STROKE_LO": "rgba(139,90,43,0.25)",
        "BARLINE": "rgba(0,0,0,0.08)",
        "RING_BG": "rgba(107,93,79,0.18)",
        "PILL_BG": "rgba(234,219,202,0.60)",
        "PILL_STROKE": "rgba(166,123,61,0.50)",
        "CAT_BG": "rgba(139,90,43,0.15)",
        "CAT_STROKE": "rgba(139,90,43,0.40)",
        "MONO_TX": "#FAF6F0",
        "ICON_BG": "#8B5A2B",
        "EMERALD": "#3D6B3C",
        "DONUT_COLORS": ["#A67B3D", "#8B5A2B", "#3D6B3C", "#B85C38", "#6B5D4F"],
    },
}

W        = 1180
CARD_W   = 578
CARD_H   = 174
GAP      = 14
MARGIN   = 5
FONT     = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

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

def render_vector_icon(icon_type, x, y, size=40, bg_col="#C0713A", fg_col="#0D0A06"):
    u = size / 24.0
    parts = []
    a = parts.append
    
    # Outer rounded container
    a(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="9" fill="{bg_col}" opacity="0.95"/>')
    
    if icon_type == "justice":
        # Scales of Justice
        a(f'<path d="M {x+12*u} {y+4.5*u} L {x+12*u} {y+19.5*u} M {x+8.5*u} {y+19.5*u} L {x+15.5*u} {y+19.5*u} '
          f'M {x+4.5*u} {y+7.5*u} L {x+19.5*u} {y+7.5*u} '
          f'M {x+5.5*u} {y+7.5*u} L {x+3.5*u} {y+12.5*u} M {x+7.5*u} {y+7.5*u} L {x+9.5*u} {y+12.5*u} '
          f'M {x+2.5*u} {y+12.5*u} Q {x+6.5*u} {y+15.5*u} {x+10.5*u} {y+12.5*u} Z '
          f'M {x+16.5*u} {y+7.5*u} L {x+14.5*u} {y+12.5*u} M {x+18.5*u} {y+7.5*u} L {x+20.5*u} {y+12.5*u} '
          f'M {x+13.5*u} {y+12.5*u} Q {x+17.5*u} {y+15.5*u} {x+21.5*u} {y+12.5*u} Z" '
          f'fill="none" stroke="{fg_col}" stroke-width="{1.5*u}" stroke-linecap="round" stroke-linejoin="round"/>')
        a(f'<circle cx="{x+12*u}" cy="{y+4.5*u}" r="{1.3*u}" fill="{fg_col}"/>')

    elif icon_type == "clapper":
        # Director's Clapperboard
        a(f'<rect x="{x+3.5*u}" y="{y+10*u}" width="{17*u}" height="{10*u}" rx="{1.5*u}" fill="{fg_col}"/>')
        a(f'<path d="M {x+3.5*u} {y+5*u} L {x+20.5*u} {y+5*u} L {x+20.5*u} {y+9*u} L {x+3.5*u} {y+9*u} Z" fill="{fg_col}"/>')
        a(f'<line x1="{x+7.5*u}" y1="{y+5*u}" x2="{x+5.5*u}" y2="{y+9*u}" stroke="{bg_col}" stroke-width="{1.4*u}"/>')
        a(f'<line x1="{x+12.5*u}" y1="{y+5*u}" x2="{x+10.5*u}" y2="{y+9*u}" stroke="{bg_col}" stroke-width="{1.4*u}"/>')
        a(f'<line x1="{x+17.5*u}" y1="{y+5*u}" x2="{x+15.5*u}" y2="{y+9*u}" stroke="{bg_col}" stroke-width="{1.4*u}"/>')
        a(f'<line x1="{x+6.5*u}" y1="{y+13*u}" x2="{x+17.5*u}" y2="{y+13*u}" stroke="{bg_col}" stroke-width="{1.2*u}" stroke-linecap="round"/>')
        a(f'<line x1="{x+6.5*u}" y1="{y+16.5*u}" x2="{x+13.5*u}" y2="{y+16.5*u}" stroke="{bg_col}" stroke-width="{1.2*u}" stroke-linecap="round"/>')

    elif icon_type == "chart":
        # Trend Chart & Forecaster
        a(f'<path d="M {x+4*u} {y+19*u} L {x+20*u} {y+19*u} M {x+4*u} {y+5*u} L {x+4*u} {y+19*u}" '
          f'fill="none" stroke="{fg_col}" stroke-width="{1.8*u}" stroke-linecap="round"/>')
        a(f'<path d="M {x+5*u} {y+16*u} L {x+9*u} {y+12*u} L {x+13*u} {y+14*u} L {x+19*u} {y+7*u}" '
          f'fill="none" stroke="{fg_col}" stroke-width="{1.8*u}" stroke-linecap="round" stroke-linejoin="round"/>')
        a(f'<polygon points="{x+19*u},{y+7*u} {x+15.5*u},{y+7*u} {x+19*u},{y+10.5*u}" fill="{fg_col}"/>')
        a(f'<circle cx="{x+9*u}" cy="{y+12*u}" r="{1.2*u}" fill="{fg_col}"/>')
        a(f'<circle cx="{x+13*u}" cy="{y+14*u}" r="{1.2*u}" fill="{fg_col}"/>')

    elif icon_type == "bank":
        # Bank Pediment & Classical Columns
        a(f'<polygon points="{x+12*u},{y+4*u} {x+3*u},{y+8.5*u} {x+21*u},{y+8.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+3*u}" y="{y+8.5*u}" width="{18*u}" height="{1.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+4.5*u}" y="{y+10*u}" width="{2.2*u}" height="{7*u}" rx="{0.4*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+8.8*u}" y="{y+10*u}" width="{2.2*u}" height="{7*u}" rx="{0.4*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+13*u}" y="{y+10*u}" width="{2.2*u}" height="{7*u}" rx="{0.4*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+17.3*u}" y="{y+10*u}" width="{2.2*u}" height="{7*u}" rx="{0.4*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+3*u}" y="{y+17*u}" width="{18*u}" height="{1.5*u}" fill="{fg_col}"/>')
        a(f'<rect x="{x+2*u}" y="{y+18.5*u}" width="{20*u}" height="{2*u}" rx="{0.5*u}" fill="{fg_col}"/>')

    elif icon_type == "career":
        # Career OS / Briefcase
        a(f'<rect x="{x+3.5*u}" y="{y+8*u}" width="{17*u}" height="{12*u}" rx="{2*u}" fill="{fg_col}"/>')
        a(f'<path d="M {x+8.5*u} {y+8*u} L {x+8.5*u} {y+5.5*u} Q {x+8.5*u} {y+4*u} {x+10*u} {y+4*u} L {x+14*u} {y+4*u} Q {x+15.5*u} {y+4*u} {x+15.5*u} {y+5.5*u} L {x+15.5*u} {y+8*u}" '
          f'fill="none" stroke="{fg_col}" stroke-width="{1.6*u}"/>')
        a(f'<line x1="{x+3.5*u}" y1="{y+13*u}" x2="{x+20.5*u}" y2="{y+13*u}" stroke="{bg_col}" stroke-width="{1.2*u}"/>')
        a(f'<rect x="{x+10.5*u}" y="{y+11.5*u}" width="{3*u}" height="{3*u}" rx="{0.6*u}" fill="{bg_col}"/>')

    elif icon_type == "kanban":
        # Agile Kanban / TaskTrack
        a(f'<rect x="{x+3.5*u}" y="{y+4*u}" width="{17*u}" height="{16*u}" rx="{2*u}" '
          f'fill="none" stroke="{fg_col}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+9.5*u}" y1="{y+4*u}" x2="{x+9.5*u}" y2="{y+20*u}" stroke="{fg_col}" stroke-width="{1.5*u}"/>')
        a(f'<line x1="{x+15*u}" y1="{y+4*u}" x2="{x+15*u}" y2="{y+20*u}" stroke="{fg_col}" stroke-width="{1.5*u}"/>')
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
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="7.5" '
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
    a(f'<rect width="{CARD_W}" height="{CARD_H}" rx="12" fill="{t["PANEL"]}" stroke="{t["STROKE"]}">'
      f'<animate attributeName="stroke" values="{t["STROKE_LO"]};{t["STROKE_HI"]};{t["STROKE_LO"]}" '
      f'dur="4.5s" begin="{b+idx*0.7:.2f}s" repeatCount="indefinite"/></rect>')
    a(f'<rect width="{CARD_W}" height="30" rx="12" fill="{t["PANEL_BAR"]}"/>')
    a(f'<rect y="18" width="{CARD_W}" height="12" fill="{t["PANEL_BAR"]}"/>')
    a(f'<line x1="0" y1="30" x2="{CARD_W}" y2="30" stroke="{t["BARLINE"]}"/>')
    a(f'<text x="16" y="19" font-size="10.5" fill="{t["MUTED"]}"><tspan fill="{t["ACCENT_2"]}">&#8226;</tspan> {esc(repo)}</text>')

    # Top right category pill
    cat = esc(p.get("category", "Project"))
    cat_w = len(cat) * 5.8 + 14
    cat_x = CARD_W - cat_w - 24
    a(f'<rect x="{cat_x}" y="7" width="{cat_w}" height="16" rx="8" fill="{t["CAT_BG"]}" stroke="{t["CAT_STROKE"]}"/>')
    a(f'<text x="{cat_x + cat_w/2:.0f}" y="18.5" text-anchor="middle" font-size="9" font-weight="600" fill="{t["ACCENT_2"]}">{cat}</text>')
    
    # Live pulse dot
    a(f'<circle cx="{CARD_W-12}" cy="15" r="3.5" fill="{t["EMERALD"]}">'
      f'<animate attributeName="opacity" values="1;0.25;1" dur="1.8s" repeatCount="indefinite"/></circle>')

    # Bespoke Domain Vector Icon with float animation
    icon_type = p.get("icon", "justice")
    float_anim = (f'<animateTransform attributeName="transform" type="translate" '
                  f'values="0 0; 0 -2.5; 0 0" dur="5s" begin="{b+idx*0.5:.2f}s" '
                  f'repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
                  f'keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>')
    a(f'<g>{float_anim}{render_vector_icon(icon_type, 16, 44, 40, t["ICON_BG"], t["MONO_TX"])}</g>')

    # Name + Blinking cursor
    name = esc(p.get("name", "unnamed"))
    a(f'<text x="68" y="61" font-size="16.5" font-weight="700" fill="{t["TEXT"]}">{name}'
      f'<tspan fill="{t["ACCENT_2"]}">_<animate attributeName="opacity" values="1;0;1" dur="1.2s" '
      f'begin="{b+0.4:.2f}s" repeatCount="indefinite"/></tspan></text>')

    # Description (wrapped cleanly to 40 characters to avoid any overlap)
    for i, line in enumerate(wrap_text(p.get("description", ""), 40)):
        a(f'<text x="68" y="{80 + i * 16}" font-size="11" fill="{t["MUTED"]}">{esc(line)}</text>')

    # Tag pills
    tx = 68
    for tag in (p.get("tags") or [])[:3]:
        tw = len(tag) * 6.5 + 14
        a(f'<rect x="{tx}" y="118" width="{tw:.0f}" height="18" rx="9" fill="{t["PILL_BG"]}" stroke="{t["PILL_STROKE"]}"/>')
        a(f'<text x="{tx + tw/2:.0f}" y="130.5" text-anchor="middle" font-size="9.5" font-weight="600" fill="{t["ACCENT_2"]}">{esc(tag)}</text>')
        tx += tw + 6

    # Bottom Row: Quick Action Indicator
    a(f'<text x="68" y="156" font-size="10.5" fill="{t["MUTED"]}">'
      f'<tspan fill="{t["ACCENT_2"]}">&#9656;</tspan> Production Stack'
      f'<tspan fill="{t["ACCENT_1"]}" dx="14" font-weight="600">&#8599; View Repository</tspan></text>')

    # Right-Hand Telemetry: Zero-Overlap Donut + Legend Layout
    langs = p.get("languages") or {}
    if langs:
        cx, cy, r = CARD_W - 40, 78, 20
        segs, legend = donut_segments(langs, cx, cy, r, b + 0.3, t["DONUT_COLORS"], t["RING_BG"], t["TEXT"], t["MUTED"])
        a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["RING_BG"]}" stroke-width="7.5"/>')
        a(segs)
        top = legend[0]
        a(f'<text x="{cx}" y="{cy+3.5}" text-anchor="middle" font-size="10" font-weight="700" fill="{t["TEXT"]}">{top[1]*100:.0f}%</text>')
        
        dot_x = cx - r - 82
        text_x = dot_x + 8
        n_items = len(legend[:3])
        start_ly = cy - (n_items - 1) * 8.5
        for i_l, (lang, frac, col) in enumerate(legend[:3]):
            curr_ly = start_ly + i_l * 17
            a(f'<circle cx="{dot_x}" cy="{curr_ly}" r="3" fill="{col}"/>')
            a(f'<text x="{text_x}" y="{curr_ly+3.5}" font-size="9" fill="{t["MUTED"]}">'
              f'{esc(lang)} <tspan fill="{t["TEXT"]}" font-weight="600">{frac*100:.0f}%</tspan></text>')

    a('</g>')
    a('</a>')
    return "".join(e)

def build_projects_svg(projects, theme="dark"):
    t = THEMES[theme]
    rows = math.ceil(len(projects) / 2)
    H = 56 + rows * (CARD_H + GAP) + MARGIN
    gid = f"proj_acc_{theme}"
    s = []
    a = s.append
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="{FONT}" role="img" aria-label="Nikhil Krishna R D — Featured Projects">')
    a(f'<rect width="{W}" height="{H}" fill="{t["BG"]}"/>')
    
    # Animated accent gradient
    a(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{t["ACCENT_1"]}"><animate attributeName="stop-color" values="{t["ACCENT_1"]};{t["ACCENT_2"]};{t["ACCENT_3"]};{t["ACCENT_1"]}" dur="10s" repeatCount="indefinite"/></stop>'
      f'<stop offset="1" stop-color="{t["ACCENT_2"]}"><animate attributeName="stop-color" values="{t["ACCENT_2"]};{t["ACCENT_3"]};{t["ACCENT_1"]};{t["ACCENT_2"]}" dur="10s" repeatCount="indefinite"/></stop>'
      f'</linearGradient></defs>')
      
    # Header: matches SYSTEM.INFO styling
    a(f'<text x="{MARGIN+2}" y="18" font-size="11" letter-spacing="2" fill="{t["ACCENT_2"]}">PROJECTS.SLATE</text>')
    a(f'<text x="{MARGIN+145}" y="18" font-size="10" fill="{t["DIM"]}">./projects.sh --live</text>')
    a(f'<line x1="{MARGIN}" y1="28" x2="{W-MARGIN}" y2="28" stroke="url(#{gid})" stroke-width="1.5" opacity="0.75"/>')
    
    for i, p in enumerate(projects):
        x = MARGIN + (i % 2) * (CARD_W + GAP + 4)
        y = 42 + (i // 2) * (CARD_H + GAP)
        a(card(p, x, y, i, t))
        
    a('</svg>')
    return "".join(s)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(PROJECTS_JSON, 'r', encoding='utf-8') as f:
        projects = json.load(f)
        
    for theme, fname in [("dark", "projects-dark.svg"), ("light", "projects-light.svg")]:
        svg = build_projects_svg(projects, theme)
        out_path = os.path.join(OUT_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(svg)
        size_kb = os.path.getsize(out_path) / 1024.0
        print(f"[OK] {fname} written ({size_kb:.1f} KB) -> {out_path}")

if __name__ == "__main__":
    main()
