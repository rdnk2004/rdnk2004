#!/usr/bin/env python3
"""
generate_all.py — Unified Master Asset Generator for rdnk2004

Executes all telemetry ingestion and SVG generation pipelines in sequence:
  1. fetch_data.py        — Ingest GitHub API live stars & language telemetry
  2. generate_projects.py — Generate interactive project cards & composite slates
  3. generate_skills.py   — Generate Technical Arsenal 4-panel skill matrix
  4. generate_streak.py   — Generate Live Streak matrix & activity spline graph
  5. generate_divider.py  — Generate themed film section divider

Usage:
    python generate_all.py
"""

import os, sys, subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(ROOT_DIR, '.github', 'scripts')

PIPELINE_SCRIPTS = [
    ("fetch_data.py", "1/5: Ingesting Live GitHub Project Telemetry"),
    ("generate_projects.py", "2/5: Generating Project Cards & Master Slates"),
    ("generate_skills.py", "3/5: Generating Technical Arsenal & Skill Matrix"),
    ("generate_streak.py", "4/5: Generating Live Streak & Activity Matrix"),
    ("generate_divider.py", "5/5: Generating Section Divider Line"),
]

def main():
    print("=" * 60)
    print("MASTER ASSET GENERATION PIPELINE — @rdnk2004")
    print("=" * 60)
    
    for script_name, label in PIPELINE_SCRIPTS:
        script_path = os.path.join(SCRIPTS_DIR, script_name)
        if not os.path.exists(script_path):
            print(f"[!] Warning: {script_path} not found. Skipping.", file=sys.stderr)
            continue
            
        print(f"\n>> [{label}]...")
        res = subprocess.run([sys.executable, script_path], cwd=ROOT_DIR)
        if res.returncode != 0:
            print(f"[!] Error: {script_name} exited with status {res.returncode}", file=sys.stderr)
            sys.exit(res.returncode)
            
    print("\n" + "=" * 60)
    print("ALL PROFILE ASSETS SUCCESSFULLY REBUILT & SYNCHRONIZED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
