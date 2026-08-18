#!/usr/bin/env python3
"""
generate_skills.py — The Director's Cut: Technical Arsenal & Applied Skill Matrix SVG

Generates a stunning, ultra-premium 4-panel interactive vector SVG matching
the exact theme of the Hero Banner and Projects Slate:
  - assets/skills-dark.svg
  - assets/skills-light.svg
"""

import os, math, html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(os.path.dirname(SCRIPT_DIR))
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
        "STROKE": "rgba(212,163,83,0.38)",
        "STROKE_HI": "rgba(212,163,83,0.85)",
        "STROKE_LO": "rgba(192,113,58,0.28)",
        "BARLINE": "rgba(255,255,255,0.08)",
        "PILL_BG": "rgba(42,27,15,0.85)",
        "PILL_STROKE": "rgba(212,163,83,0.45)",
        "PILL_TEXT": "#F5E6D3",
        "PILL_SUB": "#D4A353",
        "CAT_BG": "rgba(192,113,58,0.28)",
        "CAT_STROKE": "rgba(192,113,58,0.75)",
        "EMERALD": "#5B8C5A",
        "CYAN": "#4E9F9F",
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
        "STROKE": "rgba(166,123,61,0.40)",
        "STROKE_HI": "rgba(166,123,61,0.80)",
        "STROKE_LO": "rgba(139,90,43,0.25)",
        "BARLINE": "rgba(0,0,0,0.08)",
        "PILL_BG": "rgba(240,230,218,0.80)",
        "PILL_STROKE": "rgba(166,123,61,0.50)",
        "PILL_TEXT": "#1A1207",
        "PILL_SUB": "#8B5A2B",
        "CAT_BG": "rgba(139,90,43,0.18)",
        "CAT_STROKE": "rgba(139,90,43,0.50)",
        "EMERALD": "#3D6B3C",
        "CYAN": "#2A6E6E",
    },
}

W       = 1180
CARD_W  = 578
CARD_H  = 230
GAP     = 14
MARGIN  = 5
FONT    = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

CATEGORIES = [
    {
        "id": "STACK.01",
        "title": "CORE LANGUAGES & DATA SCHEMAS",
        "tag": "FOUNDATION",
        "icon": "code",
        "skills": [
            ("Python", "Production Core", "#3776AB"),
            ("SQL / PostgreSQL", "Relational", "#336791"),
            ("TypeScript", "Type-Safe", "#3178C6"),
            ("JavaScript", "Modern ES6+", "#F7DF1E"),
            ("R", "Econometrics", "#276DC3"),
            ("Pydantic", "Data Validation", "#E92063"),
            ("Pandera", "Schema Testing", "#3776AB"),
            ("Bash / Shell", "Automation", "#4EAA25"),
        ]
    },
    {
        "id": "STACK.02",
        "title": "AI, MACHINE LEARNING & AGENTS",
        "tag": "INTELLIGENCE",
        "icon": "brain",
        "skills": [
            ("PyTorch", "Deep Learning", "#EE4C2C"),
            ("TensorFlow", "Neural Nets", "#FF6F00"),
            ("scikit-learn", "Statistical ML", "#F7931E"),
            ("XGBoost", "Gradient Boost", "#0E7C7B"),
            ("SHAP", "Model Explainability", "#8A2BE2"),
            ("Prophet", "Time-Series", "#0668E1"),
            ("ChromaDB", "Vector RAG", "#E67E22"),
            ("LangChain", "Multi-Agent", "#1ABC9C"),
            ("n8n", "Workflow Orchestration", "#EA4B71"),
            ("Hugging Face", "Transformers", "#FFD21E"),
        ]
    },
    {
        "id": "STACK.03",
        "title": "DATA PROCESSING & ANALYTICS",
        "tag": "PIPELINES",
        "icon": "chart",
        "skills": [
            ("Pandas", "High-Perf Data", "#150458"),
            ("NumPy", "Vector Math", "#013243"),
            ("SciPy", "Scientific Compute", "#0C55A5"),
            ("Matplotlib", "Visualizations", "#11557C"),
            ("Seaborn", "Statistical Plots", "#388E3C"),
            ("Statsmodels", "Econometric Inference", "#455A64"),
            ("SHAP Analysis", "Feature Attribution", "#8A2BE2"),
            ("Macro Analytics", "RBI / CPI Modeling", "#D4A353"),
        ]
    },
    {
        "id": "STACK.04",
        "title": "BACKEND, CLOUD & FULL STACK DEVOPS",
        "tag": "DEPLOYMENT",
        "icon": "server",
        "skills": [
            ("FastAPI", "Async Microservices", "#009688"),
            ("Django REST", "Production Web", "#092E20"),
            ("React", "Frontend Interfaces", "#61DAFB"),
            ("Streamlit", "ML Dashboards", "#FF4B4B"),
            ("Docker", "Containerization", "#2496ED"),
            ("PostgreSQL", "ACID Database", "#336791"),
            ("MongoDB", "Document Store", "#47A248"),
            ("GitHub Actions", "CI/CD Pipelines", "#2088FF"),
            ("MLflow", "Experiment Tracking", "#0194E2"),
            ("Vercel / Render", "Cloud Hosting", "#000000"),
        ]
    }
]

def esc(s):
    return html.escape(str(s), quote=True)

def render_category_icon(icon_type, x, y, size=16, color="#D4A353"):
    u = size / 16.0
    if icon_type == "code":
        return f'<path d="M {x+5*u} {y+4*u} L {x+2*u} {y+8*u} L {x+5*u} {y+12*u} M {x+11*u} {y+4*u} L {x+14*u} {y+8*u} L {x+11*u} {y+12*u} M {x+9*u} {y+3*u} L {x+7*u} {y+13*u}" fill="none" stroke="{color}" stroke-width="{1.6*u}" stroke-linecap="round" stroke-linejoin="round"/>'
    elif icon_type == "brain":
        return f'<path d="M {x+8*u} {y+3*u} C {x+5*u} {y+3*u} {x+3*u} {y+5.5*u} {x+3*u} {y+8*u} C {x+3*u} {y+10*u} {x+4.5*u} {y+11.5*u} {x+5*u} {y+13*u} L {x+11*u} {y+13*u} C {x+11.5*u} {y+11.5*u} {x+13*u} {y+10*u} {x+13*u} {y+8*u} C {x+13*u} {y+5.5*u} {x+11*u} {y+3*u} {x+8*u} {y+3*u} Z M {x+6*u} {y+13*u} L {x+6*u} {y+14.5*u} M {x+10*u} {y+13*u} L {x+10*u} {y+14.5*u}" fill="none" stroke="{color}" stroke-width="{1.5*u}" stroke-linecap="round"/>'
    elif icon_type == "chart":
        return f'<path d="M {x+3*u} {y+13*u} L {x+13*u} {y+13*u} M {x+3*u} {y+3*u} L {x+3*u} {y+13*u} M {x+4.5*u} {y+11*u} L {x+7.5*u} {y+7*u} L {x+10*u} {y+9*u} L {x+13*u} {y+4.5*u}" fill="none" stroke="{color}" stroke-width="{1.6*u}" stroke-linecap="round" stroke-linejoin="round"/>'
    else:
        return f'<rect x="{x+2.5*u}" y="{y+3*u}" width="{11*u}" height="{4*u}" rx="1" fill="none" stroke="{color}" stroke-width="{1.5*u}"/><rect x="{x+2.5*u}" y="{y+9*u}" width="{11*u}" height="{4*u}" rx="1" fill="none" stroke="{color}" stroke-width="{1.5*u}"/><circle cx="{x+5*u}" cy="{y+5*u}" r="{0.9*u}" fill="{color}"/><circle cx="{x+5*u}" cy="{y+11*u}" r="{0.9*u}" fill="{color}"/>'

def render_panel(cat, x, y, idx, t):
    b = 0.2 + idx * 0.12
    e = []
    a = e.append
    
    a(f'<g opacity="0" transform="translate({x},{y})">')
    a(f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{b:.2f}s" fill="freeze"/>')
    
    # Panel Background & Animated Breathing Border
    a(f'<rect width="{CARD_W}" height="{CARD_H}" rx="12" fill="{t["PANEL"]}" stroke="{t["STROKE"]}">'
      f'<animate attributeName="stroke" values="{t["STROKE_LO"]};{t["STROKE_HI"]};{t["STROKE_LO"]}" '
      f'dur="4.8s" begin="{b+idx*0.6:.2f}s" repeatCount="indefinite"/></rect>')
    
    # Panel Header Bar
    a(f'<rect width="{CARD_W}" height="32" rx="12" fill="{t["PANEL_BAR"]}"/>')
    a(f'<rect y="20" width="{CARD_W}" height="12" fill="{t["PANEL_BAR"]}"/>')
    a(f'<line x1="0" y1="32" x2="{CARD_W}" y2="32" stroke="{t["BARLINE"]}"/>')
    
    # Header Icon + Title
    a(render_category_icon(cat["icon"], 16, 8, 16, t["ACCENT_2"]))
    a(f'<text x="40" y="20.5" font-size="11" font-weight="700" letter-spacing="1" fill="{t["TEXT"]}">'
      f'<tspan fill="{t["ACCENT_1"]}">{cat["id"]} //</tspan> {esc(cat["title"])}</text>')
    
    # Category Tag Pill
    tag_w = len(cat["tag"]) * 6.5 + 14
    tag_x = CARD_W - tag_w - 22
    a(f'<rect x="{tag_x}" y="7.5" width="{tag_w}" height="17" rx="8.5" fill="{t["CAT_BG"]}" stroke="{t["CAT_STROKE"]}"/>')
    a(f'<text x="{tag_x + tag_w/2:.0f}" y="19.5" text-anchor="middle" font-size="9" font-weight="700" letter-spacing="0.5" fill="{t["ACCENT_2"]}">{cat["tag"]}</text>')
    
    # Emerald pulse dot
    a(f'<circle cx="{CARD_W-12}" cy="16" r="4" fill="{t["EMERALD"]}">'
      f'<animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/></circle>')

    # Skill Badges Layout
    skills = cat["skills"]
    col_w = (CARD_W - 32 - 10) / 2 # 268px each
    for s_idx, (name, role, accent_col) in enumerate(skills[:8]):
        col = s_idx % 2
        row = s_idx // 2
        
        bx = 16 + col * (col_w + 10)
        by = 44 + row * 43
        
        a(f'<g transform="translate({bx:.0f},{by:.0f})">')
        a(f'<rect width="{col_w:.0f}" height="35" rx="8" fill="{t["PILL_BG"]}" stroke="{t["PILL_STROKE"]}"/>')
        
        # Left Accent Indicator Line
        a(f'<line x1="1" y1="8" x2="1" y2="27" stroke="{accent_col}" stroke-width="3" stroke-linecap="round"/>')
        
        # Bullet Dot
        a(f'<circle cx="12" cy="17.5" r="3" fill="{accent_col}"/>')
        
        # Skill Name
        a(f'<text x="22" y="16.5" font-size="11.5" font-weight="700" fill="{t["PILL_TEXT"]}">{esc(name)}</text>')
        
        # Skill Subtitle / Domain Role
        a(f'<text x="22" y="28" font-size="9" font-weight="500" fill="{t["PILL_SUB"]}">{esc(role)}</text>')
        
        # Status Pill / Verified Check
        a(f'<text x="{col_w-8:.0f}" y="22" text-anchor="end" font-size="10" fill="{t["EMERALD"]}">&#10003;</text>')
        
        a('</g>')

    a('</g>')
    return "".join(e)

def build_skills_svg(theme="dark"):
    t = THEMES[theme]
    rows = 2
    H = 56 + rows * (CARD_H + GAP) + MARGIN
    gid = f"skills_acc_{theme}"
    s = []
    a = s.append
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="{FONT}" role="img" aria-label="Nikhil Krishna R D — Technical Arsenal &amp; Applied Skill Matrix">')
    a(f'<rect width="{W}" height="{H}" fill="{t["BG"]}"/>')
    
    a(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{t["ACCENT_1"]}"><animate attributeName="stop-color" values="{t["ACCENT_1"]};{t["ACCENT_2"]};{t["ACCENT_3"]};{t["ACCENT_1"]}" dur="10s" repeatCount="indefinite"/></stop>'
      f'<stop offset="1" stop-color="{t["ACCENT_2"]}"><animate attributeName="stop-color" values="{t["ACCENT_2"]};{t["ACCENT_3"]};{t["ACCENT_1"]};{t["ACCENT_2"]}" dur="10s" repeatCount="indefinite"/></stop>'
      f'</linearGradient></defs>')
      
    # Slate Header
    a(f'<text x="{MARGIN+2}" y="18" font-size="11.5" font-weight="700" letter-spacing="2" fill="{t["ACCENT_2"]}">TECHNICAL.ARSENAL // PRODUCTION.STACK</text>')
    a(f'<text x="{W-MARGIN-10}" y="18" text-anchor="end" font-size="10.5" fill="{t["DIM"]}">./arsenal.sh --verified --all</text>')
    a(f'<line x1="{MARGIN}" y1="28" x2="{W-MARGIN}" y2="28" stroke="url(#{gid})" stroke-width="1.5" opacity="0.75"/>')
    
    for i, cat in enumerate(CATEGORIES):
        x = MARGIN + (i % 2) * (CARD_W + GAP + 4)
        y = 42 + (i // 2) * (CARD_H + GAP)
        a(render_panel(cat, x, y, i, t))
        
    a('</svg>')
    return "".join(s)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for theme, fname in [("dark", "skills-dark.svg"), ("light", "skills-light.svg")]:
        svg = build_skills_svg(theme)
        out_path = os.path.join(OUT_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f"[OK] {fname} ({os.path.getsize(out_path)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
