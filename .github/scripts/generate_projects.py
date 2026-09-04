#!/usr/bin/env python3
"""
generate_projects.py — Executive Engineering Project Cards & Slate (Full Width & Expanded)

Generates:
  1. Individual clickable project cards (Full-bleed edge-to-edge, expanded typography,
     high-definition vector glyphs, and precision telemetry):
     - assets/project-1-dark.svg, assets/project-1-light.svg
     - assets/project-2-dark.svg, assets/project-2-light.svg
     - assets/project-3-dark.svg, assets/project-3-light.svg
     - assets/project-4-dark.svg, assets/project-4-light.svg
     - assets/project-5-dark.svg, assets/project-5-light.svg
     - assets/project-6-dark.svg, assets/project-6-light.svg
  2. Full composite 6-card master slates:
     - assets/projects-dark.svg
     - assets/projects-light.svg
"""

import json, os, sys, math, html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUT_DIR    = os.path.join(ROOT_DIR, 'assets')

THEMES = {
    "dark": {
        "BG": "#0A0704",            # Obsidian deep background
        "CARD_BG": "#130E09",       # Rich dark chocolate canvas
        "CARD_BG_END": "#19120C",   # Subtle card gradient end
        "BORDER": "rgba(212,163,83,0.24)", # Refined gold border
        "BORDER_HI": "rgba(212,163,83,0.70)", # Highlight gold
        "BORDER_LO": "rgba(192,113,58,0.20)", # Sienna low
        "ICON_BG": "rgba(212,163,83,0.12)",
        "ICON_BORDER": "rgba(212,163,83,0.35)",
        "ICON_FG": "#D4A353",
        "TEXT": "#FAF5EE",          # Crisp light cream primary
        "MUTED": "#BCAAA0",         # High-legibility muted body
        "DIM": "#807060",           # Dim metadata
        "ACCENT_1": "#C0713A",      # Sienna
        "ACCENT_2": "#D4A353",      # Amber Gold
        "ACCENT_3": "#F5E6D3",      # Cream
        "CHIP_BG": "rgba(212,163,83,0.09)",
        "CHIP_BORDER": "rgba(212,163,83,0.26)",
        "CHIP_TEXT": "#E8D8C5",
        "BAR_TRACK": "rgba(255,255,255,0.08)",
        "BARLINE": "rgba(255,255,255,0.08)",
        "BTN_BG": "rgba(212,163,83,0.12)",
        "BTN_BORDER": "rgba(212,163,83,0.38)",
        "BTN_TEXT": "#D4A353",
        "STATUS_BG": "rgba(74,222,128,0.12)",
        "STATUS_BORDER": "rgba(74,222,128,0.30)",
        "EMERALD": "#4ADE80",
        "LANG_COLORS": ["#D4A353", "#C0713A", "#5B8C5A", "#B85C38", "#8C7B6B"],
    },
    "light": {
        "BG": "#F7F3EC",            # Warm parchment
        "CARD_BG": "#FFFFFF",       # Crisp white
        "CARD_BG_END": "#FAF6F0",   # Soft ivory
        "BORDER": "rgba(166,123,61,0.28)",
        "BORDER_HI": "rgba(166,123,61,0.65)",
        "BORDER_LO": "rgba(139,90,43,0.18)",
        "ICON_BG": "rgba(166,123,61,0.09)",
        "ICON_BORDER": "rgba(166,123,61,0.30)",
        "ICON_FG": "#8B5A2B",
        "TEXT": "#1C140C",          # Deep charcoal
        "MUTED": "#5A4A3B",         # Readable brown-grey
        "DIM": "#9C8B78",
        "ACCENT_1": "#8B5A2B",
        "ACCENT_2": "#A67B3D",
        "ACCENT_3": "#C89D66",
        "CHIP_BG": "rgba(166,123,61,0.09)",
        "CHIP_BORDER": "rgba(166,123,61,0.26)",
        "CHIP_TEXT": "#3D2B1C",
        "BAR_TRACK": "rgba(0,0,0,0.06)",
        "BARLINE": "rgba(0,0,0,0.08)",
        "BTN_BG": "rgba(166,123,61,0.09)",
        "BTN_BORDER": "rgba(166,123,61,0.34)",
        "BTN_TEXT": "#8B5A2B",
        "STATUS_BG": "rgba(22,163,74,0.10)",
        "STATUS_BORDER": "rgba(22,163,74,0.28)",
        "EMERALD": "#16A34A",
        "LANG_COLORS": ["#A67B3D", "#8B5A2B", "#3D6B3C", "#B85C38", "#6B5D4F"],
    },
}

W         = 1180
CARD_W    = 580
CARD_H    = 260
GAP       = 20
FONT_SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',Roboto,Helvetica,Arial,sans-serif"
FONT_MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

PROJECT_SPARKLINES = [
    # 0: NyayaSetu — Agentic AI & Legal Reasoning (strong recent sprint peaks)
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.1, 0.05, 0.18, 0.12, 0.35, 0.7, 1.0, 0.3, 0.85],
    # 1: Screenwriting Suite — Creative Systems & Storytelling (frequent pulses with late peak)
    [0.0, 0.0, 0.05, 0.05, 0.1, 0.05, 0.15, 0.2, 0.15, 0.3, 0.45, 0.4, 0.8, 0.95, 0.35, 0.9],
    # 2: CPI-MPC Forecaster — Macro Econometric ML (forecasting iterations surging)
    [0.0, 0.0, 0.0, 0.0, 0.05, 0.05, 0.1, 0.05, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0, 0.4, 0.95],
    # 3: NPA-RBI Risk Engine — Financial Risk & Explainable AI (panel econometric surge)
    [0.0, 0.0, 0.05, 0.1, 0.05, 0.2, 0.35, 0.6, 0.95, 0.7, 0.45, 0.3, 0.2, 0.5, 0.85, 0.4],
    # 4: Career OS — Career AI & Automation (ATS parser and workflow sprints)
    [0.0, 0.0, 0.0, 0.05, 0.05, 0.1, 0.15, 0.1, 0.25, 0.35, 0.5, 0.7, 0.85, 1.0, 0.35, 0.8],
    # 5: Nexus TaskTrack — DevOps & Cloud Systems (container & auth pushes)
    [0.0, 0.0, 0.0, 0.0, 0.05, 0.05, 0.1, 0.15, 0.1, 0.25, 0.4, 0.6, 0.8, 1.0, 0.45, 0.9],
]

def render_sparkline(points, x, y, width, height, stroke_color, fill_grad_id):
    """
    Renders a centered, minimalist commit activity sparkline graph with live pulsing endpoint.
    """
    n = len(points)
    if n < 2:
        return ""
    
    pad_y = 5.0
    base_y = y + height - pad_y
    eff_h = height - pad_y * 2
    
    coords = []
    for i, val in enumerate(points):
        px = x + (i / (n - 1)) * width
        py = base_y - val * eff_h
        coords.append((px, py))
        
    line_d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in coords)
    area_d = f"M {coords[0][0]:.1f} {base_y:.1f} L " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in coords) + f" L {coords[-1][0]:.1f} {base_y:.1f} Z"
    
    parts = []
    parts.append(f'<path d="{area_d}" fill="url(#{fill_grad_id})"/>')
    parts.append(f'<path d="{line_d}" fill="none" stroke="{stroke_color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    last_x, last_y = coords[-1]
    parts.append(f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="2.2" fill="{stroke_color}">'
                 f'<animate attributeName="r" values="2.2;3.4;2.2" dur="2.2s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="1;0.45;1" dur="2.2s" repeatCount="indefinite"/>'
                 f'</circle>')
    return "".join(parts)

def sanitize_text(s):
    if not s:
        return ""
    return str(s).replace("\ufffd", "—")

DEFAULT_PROJECTS = [
    {
        "name": "NyayaSetu",
        "repo": "rdnk2004/NyayaSetu-Multi-Agent",
        "icon": "justice",
        "description": "Multi-agent legal reasoning engine — statutory grounding, multi-perspective synthesis & zero-hallucination analysis",
        "category": "Agentic AI & Legal Reasoning",
        "tags": ["Python", "LangChain", "ChromaDB", "Pydantic", "FastAPI"],
        "languages": {"Python": 64957}
    },
    {
        "name": "Screenwriting Suite",
        "repo": "rdnk2004/screenwriting-software",
        "icon": "clapper",
        "description": "Screenwriter's studio — Fountain script editor, character webs, interactive story beats & dynamic PDF export",
        "category": "Creative Systems & Storytelling",
        "tags": ["React", "JavaScript", "Django REST", "Fountain", "PDFKit"],
        "languages": {"JavaScript": 127298, "Python": 85977, "CSS": 15708}
    },
    {
        "name": "CPI-MPC Forecaster",
        "repo": "rdnk2004/cpi-mpc",
        "icon": "chart",
        "description": "13-year macroeconomic inflation ML pipeline analyzing RBI rate decisions with predictive explainability",
        "category": "Macro Econometric ML",
        "tags": ["Python", "XGBoost", "Prophet", "SHAP", "FastAPI"],
        "languages": {"Python": 81902}
    },
    {
        "name": "NPA-RBI Risk Engine",
        "repo": "rdnk2004/NPA-RBI",
        "icon": "bank",
        "description": "Bank NPA early-warning risk engine combining panel econometrics with XGBoost & SHAP scorecards",
        "category": "Financial Risk & Explainable AI",
        "tags": ["Python", "Econometrics", "XGBoost", "SHAP", "Streamlit"],
        "languages": {"Python": 165964, "Jupyter Notebook": 34354}
    },
    {
        "name": "Career OS",
        "repo": "rdnk2004/automated-career",
        "icon": "career",
        "description": "Autonomous AI career assistant — job telemetry, real-time skill-gap audits & tailor-made ATS resumes",
        "category": "Career AI & Automation",
        "tags": ["TypeScript", "Python", "n8n", "PostgreSQL", "ATS Parser"],
        "languages": {"TypeScript": 136934, "Python": 104558, "CSS": 5997}
    },
    {
        "name": "Nexus TaskTrack",
        "repo": "rdnk2004/nexus-tasktrack",
        "icon": "kanban",
        "description": "Agile project management microservice — granular task workflows, live audit feed & JWT authentication",
        "category": "DevOps & Cloud Systems",
        "tags": ["Python", "FastAPI", "PostgreSQL", "Docker", "JWT Auth"],
        "languages": {"HTML": 180912, "Python": 47049, "JavaScript": 18658}
    }
]

def esc(s):
    return html.escape(str(s), quote=True)

def clean_lang_name(name):
    aliases = {
        "Jupyter Notebook": "Jupyter",
        "JavaScript": "JS",
        "TypeScript": "TS",
        "Dockerfile": "Docker",
        "HTML": "HTML/UI",
    }
    return aliases.get(name, name)

def wrap_text(s, max_chars=54, max_lines=2):
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
    if lines and len(lines) == max_lines and len(words) > len(" ".join(lines).split()):
        if not lines[-1].endswith("…") and not lines[-1].endswith("..."):
            lines[-1] = lines[-1].rstrip("., ") + "…"
    return lines

def render_vector_glyph(icon_type, x, y, size=24, color="#D4A353"):
    """
    Renders high-definition, minimalist vector icons with 1.8px stroke width.
    """
    u = size / 24.0
    parts = []
    a = parts.append
    
    if icon_type == "justice":
        # Scales of justice / legal balance
        a(f'<path d="M {x+12*u} {y+3.5*u} L {x+12*u} {y+20.5*u} M {x+8*u} {y+20.5*u} L {x+16*u} {y+20.5*u} '
          f'M {x+4*u} {y+7*u} L {x+20*u} {y+7*u} '
          f'M {x+5.5*u} {y+7*u} L {x+2.5*u} {y+13*u} M {x+9*u} {y+7*u} L {x+12*u} {y+13*u} '
          f'M {x+2.5*u} {y+13*u} Q {x+7.2*u} {y+16*u} {x+12*u} {y+13*u} '
          f'M {x+15*u} {y+7*u} L {x+12*u} {y+13*u} M {x+18.5*u} {y+7*u} L {x+21.5*u} {y+13*u} '
          f'M {x+12*u} {y+13*u} Q {x+16.8*u} {y+16*u} {x+21.5*u} {y+13*u}" '
          f'fill="none" stroke="{color}" stroke-width="{1.8*u}" stroke-linecap="round" stroke-linejoin="round"/>')
        a(f'<circle cx="{x+12*u}" cy="{y+3.5*u}" r="{1.5*u}" fill="{color}"/>')

    elif icon_type == "clapper":
        # Screenplay Clapperboard
        a(f'<rect x="{x+3*u}" y="{y+9.5*u}" width="{18*u}" height="{11.5*u}" rx="{1.8*u}" fill="none" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<path d="M {x+3*u} {y+4*u} L {x+21*u} {y+4*u} L {x+21*u} {y+9*u} L {x+3*u} {y+9*u} Z" fill="none" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+7.5*u}" y1="{y+4*u}" x2="{x+5.5*u}" y2="{y+9*u}" stroke="{color}" stroke-width="{1.6*u}"/>')
        a(f'<line x1="{x+13*u}" y1="{y+4*u}" x2="{x+11*u}" y2="{y+9*u}" stroke="{color}" stroke-width="{1.6*u}"/>')
        a(f'<line x1="{x+18.5*u}" y1="{y+4*u}" x2="{x+16.5*u}" y2="{y+9*u}" stroke="{color}" stroke-width="{1.6*u}"/>')
        a(f'<line x1="{x+6.5*u}" y1="{y+13.5*u}" x2="{x+17.5*u}" y2="{y+13.5*u}" stroke="{color}" stroke-width="{1.5*u}" stroke-linecap="round"/>')
        a(f'<line x1="{x+6.5*u}" y1="{y+17*u}" x2="{x+13*u}" y2="{y+17*u}" stroke="{color}" stroke-width="{1.5*u}" stroke-linecap="round"/>')

    elif icon_type == "chart":
        # Econometric trendline & forecasting nodes
        a(f'<path d="M {x+3.5*u} {y+20.5*u} L {x+20.5*u} {y+20.5*u} M {x+3.5*u} {y+4*u} L {x+3.5*u} {y+20.5*u}" fill="none" stroke="{color}" stroke-width="{1.8*u}" stroke-linecap="round"/>')
        a(f'<path d="M {x+5*u} {y+16*u} L {x+9.5*u} {y+11.5*u} L {x+14*u} {y+14*u} L {x+20*u} {y+6.5*u}" fill="none" stroke="{color}" stroke-width="{2.0*u}" stroke-linecap="round" stroke-linejoin="round"/>')
        a(f'<circle cx="{x+9.5*u}" cy="{y+11.5*u}" r="{1.6*u}" fill="{color}"/>')
        a(f'<circle cx="{x+14*u}" cy="{y+14*u}" r="{1.6*u}" fill="{color}"/>')
        a(f'<circle cx="{x+20*u}" cy="{y+6.5*u}" r="{1.8*u}" fill="{color}"/>')

    elif icon_type == "bank":
        # Classical banking facade / Risk engine
        a(f'<polygon points="{x+12*u},{y+3.5*u} {x+3*u},{y+8.5*u} {x+21*u},{y+8.5*u}" fill="none" stroke="{color}" stroke-width="{1.8*u}" stroke-linejoin="round"/>')
        a(f'<line x1="{x+3*u}" y1="{y+8.5*u}" x2="{x+21*u}" y2="{y+8.5*u}" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+5.5*u}" y1="{y+10*u}" x2="{x+5.5*u}" y2="{y+17.5*u}" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+10*u}" y1="{y+10*u}" x2="{x+10*u}" y2="{y+17.5*u}" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+14*u}" y1="{y+10*u}" x2="{x+14*u}" y2="{y+17.5*u}" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+18.5*u}" y1="{y+10*u}" x2="{x+18.5*u}" y2="{y+17.5*u}" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+2.5*u}" y1="{y+18*u}" x2="{x+21.5*u}" y2="{y+18*u}" stroke="{color}" stroke-width="{1.8*u}" stroke-linecap="round"/>')
        a(f'<line x1="{x+2*u}" y1="{y+20.5*u}" x2="{x+22*u}" y2="{y+20.5*u}" stroke="{color}" stroke-width="{1.8*u}" stroke-linecap="round"/>')

    elif icon_type == "career":
        # Professional briefcase & growth node
        a(f'<rect x="{x+3.5*u}" y="{y+9*u}" width="{17*u}" height="{12*u}" rx="{2*u}" fill="none" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<path d="M {x+8.5*u} {y+9*u} L {x+8.5*u} {y+5*u} Q {x+8.5*u} {y+3.5*u} {x+10.5*u} {y+3.5*u} L {x+13.5*u} {y+3.5*u} Q {x+15.5*u} {y+3.5*u} {x+15.5*u} {y+5*u} L {x+15.5*u} {y+9*u}" fill="none" stroke="{color}" stroke-width="{1.7*u}"/>')
        a(f'<line x1="{x+3.5*u}" y1="{y+14.5*u}" x2="{x+20.5*u}" y2="{y+14.5*u}" stroke="{color}" stroke-width="{1.4*u}"/>')
        a(f'<rect x="{x+10.5*u}" y="{y+12.5*u}" width="{3*u}" height="{3.5*u}" rx="{0.7*u}" fill="{color}"/>')

    elif icon_type == "kanban":
        # Microservice / Kanban layout
        a(f'<rect x="{x+3*u}" y="{y+4*u}" width="{18*u}" height="{16.5*u}" rx="{2.2*u}" fill="none" stroke="{color}" stroke-width="{1.8*u}"/>')
        a(f'<line x1="{x+9*u}" y1="{y+4*u}" x2="{x+9*u}" y2="{y+20.5*u}" stroke="{color}" stroke-width="{1.4*u}"/>')
        a(f'<line x1="{x+15*u}" y1="{y+4*u}" x2="{x+15*u}" y2="{y+20.5*u}" stroke="{color}" stroke-width="{1.4*u}"/>')
        a(f'<rect x="{x+4.8*u}" y="{y+7*u}" width="{2.8*u}" height="{4.5*u}" rx="{0.5*u}" fill="{color}"/>')
        a(f'<rect x="{x+4.8*u}" y="{y+13*u}" width="{2.8*u}" height="{5*u}" rx="{0.5*u}" fill="{color}"/>')
        a(f'<rect x="{x+10.8*u}" y="{y+7*u}" width="{2.8*u}" height="{7*u}" rx="{0.5*u}" fill="{color}"/>')
        a(f'<rect x="{x+16.8*u}" y="{y+7*u}" width="{2.8*u}" height="{4*u}" rx="{0.5*u}" fill="{color}"/>')
    else:
        a(f'<path d="M {x+6*u} {y+7*u} L {x+11*u} {y+12*u} L {x+6*u} {y+17*u}" fill="none" stroke="{color}" stroke-width="{2*u}" stroke-linecap="round"/>')
        a(f'<line x1="{x+12*u}" y1="{y+17*u}" x2="{x+18*u}" y2="{y+17*u}" stroke="{color}" stroke-width="{2*u}" stroke-linecap="round"/>')

    return "".join(parts)

def build_telemetry_bar(languages, x, y, width, height, colors, track_bg, text_muted, text_primary):
    """
    Builds an expanded multi-segment language telemetry bar with clean legend chips.
    """
    total = sum(languages.values()) or 1
    entries = sorted(languages.items(), key=lambda kv: -kv[1])[:3]
    
    parts = []
    a = parts.append
    
    # Background Track
    a(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{height/2:.1f}" fill="{track_bg}"/>')
    
    cur_x = x
    legend_items = []
    
    for i, (lang, v) in enumerate(entries):
        frac = v / total
        seg_w = max(5.0, frac * width)
        if cur_x + seg_w > x + width or i == len(entries) - 1:
            seg_w = max(2.0, (x + width) - cur_x)
            
        col = colors[i % len(colors)]
        
        if i == 0 and len(entries) == 1:
            a(f'<rect x="{cur_x:.1f}" y="{y}" width="{seg_w:.1f}" height="{height}" rx="{height/2:.1f}" fill="{col}"/>')
        elif i == 0:
            a(f'<path d="M {cur_x+height/2:.1f} {y} L {cur_x+seg_w:.1f} {y} L {cur_x+seg_w:.1f} {y+height} L {cur_x+height/2:.1f} {y+height} A {height/2:.1f} {height/2:.1f} 0 0 1 {cur_x+height/2:.1f} {y}" fill="{col}"/>')
        elif i == len(entries) - 1:
            a(f'<path d="M {cur_x:.1f} {y} L {cur_x+seg_w-height/2:.1f} {y} A {height/2:.1f} {height/2:.1f} 0 0 1 {cur_x+seg_w-height/2:.1f} {y+height} L {cur_x:.1f} {y+height} Z" fill="{col}"/>')
        else:
            a(f'<rect x="{cur_x:.1f}" y="{y}" width="{seg_w:.1f}" height="{height}" fill="{col}"/>')
            
        legend_items.append((clean_lang_name(lang), frac, col))
        cur_x += seg_w
        if cur_x >= x + width:
            break
            
    # Text Legend below the bar
    leg_x = x
    leg_y = y + height + 18
    for lang_label, frac, col in legend_items:
        pct = int(round(frac * 100))
        label_str = f"{lang_label} {pct}%"
        a(f'<circle cx="{leg_x + 4:.1f}" cy="{leg_y - 4:.1f}" r="3.5" fill="{col}"/>')
        a(f'<text x="{leg_x + 12:.1f}" y="{leg_y:.1f}" font-size="12" font-weight="500" fill="{text_muted}">'
          f'{esc(lang_label)} <tspan font-weight="700" fill="{text_primary}">{pct}%</tspan></text>')
        leg_x += len(label_str) * 7.5 + 24
        
    return "".join(parts)

def card_body(p, idx, t, is_standalone=False, theme="dark"):
    b = 0.12 + idx * 0.08
    e = []
    a = e.append
    
    repo = p.get("repo", "").strip().replace("https://github.com/", "").rstrip("/")
    href = f"https://github.com/{esc(repo)}"
    
    grad_id = f"card_grad_{theme}_{idx}"
    trim_id = f"card_trim_{theme}_{idx}"
    spark_grad_id = f"spark_grad_{theme}_{idx}"
    a(f'<defs>')
    a(f'<linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1">')
    a(f'<stop offset="0%" stop-color="{t["CARD_BG"]}"/>')
    a(f'<stop offset="100%" stop-color="{t["CARD_BG_END"]}"/>')
    a(f'</linearGradient>')
    a(f'<linearGradient id="{trim_id}" x1="0" y1="0" x2="1" y2="0">')
    a(f'<stop offset="0%" stop-color="{t["ACCENT_2"]}" stop-opacity="0.85"/>')
    a(f'<stop offset="60%" stop-color="{t["ACCENT_1"]}" stop-opacity="0.25"/>')
    a(f'<stop offset="100%" stop-color="{t["ACCENT_1"]}" stop-opacity="0"/>')
    a(f'</linearGradient>')
    a(f'<linearGradient id="{spark_grad_id}" x1="0" y1="0" x2="0" y2="1">')
    a(f'<stop offset="0%" stop-color="{t["EMERALD"]}" stop-opacity="0.28"/>')
    a(f'<stop offset="100%" stop-color="{t["EMERALD"]}" stop-opacity="0.0"/>')
    a(f'</linearGradient>')
    a(f'</defs>')
    
    a(f'<a href="{href}" xlink:href="{href}" target="_blank" style="text-decoration:none; cursor:pointer;">')
    a(f'<g opacity="0">')
    a(f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{b:.2f}s" fill="freeze"/>')

    # Card Surface with subtle animated border
    a(f'<rect width="{CARD_W}" height="{CARD_H}" rx="16" fill="url(#{grad_id})" stroke="{t["BORDER"]}" stroke-width="1.2">'
      f'<animate attributeName="stroke" values="{t["BORDER_LO"]};{t["BORDER_HI"]};{t["BORDER_LO"]}" '
      f'dur="4s" begin="{b+idx*0.6:.2f}s" repeatCount="indefinite"/></rect>')

    # Top illuminated accent rim (subtle gold highlight)
    a(f'<path d="M 28 1.2 L 200 1.2" stroke="url(#{trim_id})" stroke-width="2.2" stroke-linecap="round"/>')

    # 1. Header Section: Bespoke Icon (48x48)
    icon_type = p.get("icon", "justice")
    a(f'<rect x="24" y="20" width="48" height="48" rx="12" fill="{t["ICON_BG"]}" stroke="{t["ICON_BORDER"]}" stroke-width="1.0"/>')
    a(render_vector_glyph(icon_type, 36, 32, size=24, color=t["ICON_FG"]))

    # 2. Title & Domain Category Tag
    name = esc(sanitize_text(p.get("name", repo.split("/")[-1])))
    cat = esc(sanitize_text(p.get("category", "Production System")).upper())
    a(f'<text x="84" y="41" font-size="20" font-weight="700" fill="{t["TEXT"]}">{name}</text>')
    a(f'<text x="84" y="58" font-size="11" font-weight="600" letter-spacing="0.8" fill="{t["ACCENT_2"]}">{cat}</text>')

    # 3. Dynamic Repository Activity Sparkline Graph (Top-Right)
    box_w = 126
    box_h = 28
    box_x = CARD_W - box_w - 24
    box_y = 23
    
    # Inset background capsule for sparkline
    a(f'<g role="img" aria-label="Commit activity sparkline">')
    a(f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="6" '
      f'fill="{t["STATUS_BG"]}" stroke="{t["STATUS_BORDER"]}" stroke-width="0.9"/>')
    
    # Render mini commit activity graph centered inside capsule
    spark_points = PROJECT_SPARKLINES[idx % len(PROJECT_SPARKLINES)]
    spark_svg = render_sparkline(spark_points, x=box_x + 9, y=box_y, width=box_w - 18, height=box_h,
                                 stroke_color=t["EMERALD"], fill_grad_id=spark_grad_id)
    a(spark_svg)
    a(f'</g>')

    # 4. Description (2 lines of crisp, readable text)
    desc = sanitize_text(p.get("description", p.get("desc", "")))
    desc_lines = wrap_text(desc, max_chars=54, max_lines=2)
    for i, line in enumerate(desc_lines):
        a(f'<text x="24" y="{94 + i * 22}" font-size="13.5" font-weight="450" fill="{t["MUTED"]}">{esc(line)}</text>')

    # 5. Technology Stack Badges (Harmonized chips)
    skills = p.get("tags") or p.get("skills", ["Python", "AI", "Cloud"])
    chip_x = 24
    chip_y = 142
    for tag in skills[:5]:
        tag_str = esc(sanitize_text(tag))
        chip_w = len(tag) * 7.8 + 20
        a(f'<rect x="{chip_x}" y="{chip_y}" width="{chip_w:.0f}" height="26" rx="7" fill="{t["CHIP_BG"]}" stroke="{t["CHIP_BORDER"]}" stroke-width="0.9"/>')
        a(f'<text x="{chip_x + chip_w/2:.0f}" y="{chip_y + 17}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{t["CHIP_TEXT"]}">{tag_str}</text>')
        chip_x += chip_w + 8

    # 6. Bottom Divider
    a(f'<line x1="24" y1="184" x2="{CARD_W - 24}" y2="184" stroke="{t["BARLINE"]}" stroke-width="1"/>')

    # 7. Language Telemetry Bar & Legend
    langs = p.get("languages") or {"Python": 100}
    tel_svg = build_telemetry_bar(langs, x=24, y=200, width=360, height=7,
                                  colors=t["LANG_COLORS"], track_bg=t["BAR_TRACK"],
                                  text_muted=t["MUTED"], text_primary=t["TEXT"])
    a(tel_svg)

    # 8. View Repository Action Button (Bottom-Right)
    btn_w = 144
    btn_h = 36
    btn_x = CARD_W - btn_w - 24
    btn_y = 200
    a(f'<rect x="{btn_x}" y="{btn_y}" width="{btn_w}" height="{btn_h}" rx="8" '
      f'fill="{t["BTN_BG"]}" stroke="{t["BTN_BORDER"]}" stroke-width="1.0"/>')
    a(f'<text x="{btn_x + btn_w/2:.0f}" y="{btn_y + 22.5}" text-anchor="middle" '
      f'font-size="12.5" font-weight="700" fill="{t["BTN_TEXT"]}">Explore Repo ↗</text>')

    a('</g>')
    a('</a>')
    return "".join(e)

def build_single_card_svg(p, theme="dark", idx=0):
    t = THEMES[theme]
    s = []
    a = s.append
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      f'width="100%" height="auto" viewBox="0 0 {CARD_W} {CARD_H}" '
      f'font-family="{FONT_SANS}" role="img" aria-label="{esc(p.get("name", "Project"))}">')
    a(card_body(p, idx, t, is_standalone=True, theme=theme))
    a('</svg>')
    return "".join(s)

def build_composite_slate_svg(projects, theme="dark"):
    t = THEMES[theme]
    rows = math.ceil(len(projects) / 2)
    H = 54 + rows * (CARD_H + GAP)
    gid = f"proj_grad_{theme}"
    s = []
    a = s.append
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="{FONT_SANS}" role="img" aria-label="Nikhil Krishna R D — Featured Projects &amp; Applied Skills">')
    a(f'<rect width="{W}" height="{H}" fill="{t["BG"]}"/>')
    
    a(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0%" stop-color="{t["ACCENT_1"]}"><animate attributeName="stop-color" values="{t["ACCENT_1"]};{t["ACCENT_2"]};{t["ACCENT_3"]};{t["ACCENT_1"]}" dur="10s" repeatCount="indefinite"/></stop>'
      f'<stop offset="100%" stop-color="{t["ACCENT_2"]}"><animate attributeName="stop-color" values="{t["ACCENT_2"]};{t["ACCENT_3"]};{t["ACCENT_1"]};{t["ACCENT_2"]}" dur="10s" repeatCount="indefinite"/></stop>'
      f'</linearGradient></defs>')
      
    # Clean header
    a(f'<text x="6" y="22" font-size="12.5" font-weight="700" letter-spacing="1.5" fill="{t["ACCENT_2"]}">FEATURED PROJECTS // PRODUCTION REPOSITORIES</text>')
    a(f'<text x="{W-6}" y="22" text-anchor="end" font-size="11.5" font-weight="500" font-family="{FONT_MONO}" fill="{t["DIM"]}">verified // production-grade</text>')
    a(f'<line x1="0" y1="34" x2="{W}" y2="34" stroke="url(#{gid})" stroke-width="1.8" opacity="0.85"/>')
    
    for i, p in enumerate(projects[:6]):
        col = i % 2
        row = i // 2
        x = col * (CARD_W + GAP)
        y = 48 + row * (CARD_H + GAP)
        a(f'<g transform="translate({x},{y})">')
        a(card_body(p, i, t, is_standalone=False, theme=theme))
        a('</g>')
        
    a('</svg>')
    return "".join(s)

def load_projects():
    paths = [
        os.path.join(ROOT_DIR, "merged.json"),
        os.path.join(ROOT_DIR, "projects.json"),
        os.path.join(ROOT_DIR, ".github", "data", "merged.json"),
        os.path.join(ROOT_DIR, ".github", "data", "projects.json"),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        return data
            except Exception:
                pass
    return DEFAULT_PROJECTS

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    raw_projects = load_projects()
    
    projects = []
    for i, dp in enumerate(DEFAULT_PROJECTS):
        matched = None
        if i < len(raw_projects):
            matched = raw_projects[i]
        
        merged_p = dict(dp)
        if matched:
            merged_p.update({k: v for k, v in matched.items() if v})
        projects.append(merged_p)
        
    for theme in ["dark", "light"]:
        # 1. Master Composite Slate
        master_svg = build_composite_slate_svg(projects, theme)
        master_path = os.path.join(OUT_DIR, f"projects-{theme}.svg")
        with open(master_path, "w", encoding="utf-8") as f:
            f.write(master_svg)
        print(f"[OK] {master_path} ({os.path.getsize(master_path)/1024:.1f} KB)")
        
        # 2. Individual Clickable Card SVGs
        for idx, p in enumerate(projects):
            card_svg = build_single_card_svg(p, theme, idx)
            card_path = os.path.join(OUT_DIR, f"project-{idx+1}-{theme}.svg")
            with open(card_path, "w", encoding="utf-8") as f:
                f.write(card_svg)
            print(f"[OK] {card_path} ({os.path.getsize(card_path)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
