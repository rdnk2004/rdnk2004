#!/usr/bin/env python3
"""
generate_divider.py — The Director's Cut: Themed Section Divider SVG

Generates a sleek, animated film-aesthetic section divider line with amber accents:
  - assets/divider.svg
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUT_DIR    = os.path.join(ROOT_DIR, 'assets')

def build_divider(theme="dark"):
    W = 1180
    H = 28
    
    if theme == "dark":
        bg = "#09090B"
        c1 = "#27272A"
        c2 = "#71717A"
        c3 = "#E4E4E7"
        center_fill = "#E4E4E7"
        center_inner = "#09090B"
        dot_col = "#71717A"
    else:
        bg = "#FAFAFA"
        c1 = "#E4E4E7"
        c2 = "#A1A1AA"
        c3 = "#27272A"
        center_fill = "#27272A"
        center_inner = "#FAFAFA"
        dot_col = "#71717A"
        
    s = []
    a = s.append
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Section Divider">')
    a(f'<rect width="{W}" height="{H}" fill="{bg}"/>')
    
    # Animated Gradient
    gid = f"div_grad_{theme}"
    a(f'<defs>')
    a(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">')
    a(f'<stop offset="0%" stop-color="{c1}" stop-opacity="0"/>')
    a(f'<stop offset="15%" stop-color="{c1}" stop-opacity="0.6"/>')
    a(f'<stop offset="45%" stop-color="{c2}" stop-opacity="1"><animate attributeName="stop-color" values="{c2};{c3};{c1};{c2}" dur="8s" repeatCount="indefinite"/></stop>')
    a(f'<stop offset="55%" stop-color="{c3}" stop-opacity="1"><animate attributeName="stop-color" values="{c3};{c1};{c2};{c3}" dur="8s" repeatCount="indefinite"/></stop>')
    a(f'<stop offset="85%" stop-color="{c1}" stop-opacity="0.6"/>')
    a(f'<stop offset="100%" stop-color="{c1}" stop-opacity="0"/>')
    a(f'</linearGradient>')
    a(f'</defs>')
    
    # Divider Lines
    mid = H // 2
    cx = W // 2
    a(f'<line x1="40" y1="{mid}" x2="{cx - 45}" y2="{mid}" stroke="url(#{gid})" stroke-width="1.5" stroke-linecap="round"/>')
    a(f'<line x1="{cx + 45}" y1="{mid}" x2="{W - 40}" y2="{mid}" stroke="url(#{gid})" stroke-width="1.5" stroke-linecap="round"/>')
    
    # Accent Dots
    a(f'<circle cx="{cx - 28}" cy="{mid}" r="2" fill="{dot_col}"/>')
    a(f'<circle cx="{cx + 28}" cy="{mid}" r="2" fill="{dot_col}"/>')
    a(f'<circle cx="{cx - 15}" cy="{mid}" r="2.5" fill="{c2}"/>')
    a(f'<circle cx="{cx + 15}" cy="{mid}" r="2.5" fill="{c2}"/>')
    
    # Center Diamond Emblem
    a(f'<polygon points="{cx},{mid - 7} {cx + 7},{mid} {cx},{mid + 7} {cx - 7},{mid}" fill="{center_fill}"/>')
    a(f'<circle cx="{cx}" cy="{mid}" r="2" fill="{center_inner}"/>')
    
    a('</svg>')
    return "".join(s)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "divider.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(build_divider("dark"))
    print(f"[OK] {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
