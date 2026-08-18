#!/usr/bin/env python3
"""
generate_divider_svg.py — The Director's Cut: Themed Section Divider SVG

Generates a sleek, animated film-aesthetic section divider line with amber accents:
  - assets/divider.svg
  - assets/divider-light.svg
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, 'assets')

def build_divider(theme="dark"):
    W = 1180
    H = 28
    
    if theme == "dark":
        bg = "#0D0A06"
        c1 = "#C0713A"
        c2 = "#D4A353"
        c3 = "#F5E6D3"
        center_fill = "#D4A353"
        center_inner = "#0D0A06"
        dot_col = "#C0713A"
    else:
        bg = "#FAF6F0"
        c1 = "#8B5A2B"
        c2 = "#A67B3D"
        c3 = "#C89D66"
        center_fill = "#A67B3D"
        center_inner = "#FAF6F0"
        dot_col = "#8B5A2B"
        
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
    with open(os.path.join(OUT_DIR, "divider.svg"), "w", encoding="utf-8") as f:
        f.write(build_divider("dark"))
    with open(os.path.join(OUT_DIR, "divider-light.svg"), "w", encoding="utf-8") as f:
        f.write(build_divider("light"))
    print("[OK] divider.svg & divider-light.svg generated!")

if __name__ == "__main__":
    main()
