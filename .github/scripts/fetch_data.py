#!/usr/bin/env python3
"""
fetch_data.py — Live GitHub Repository Data Ingestion

Queries GitHub API for stars, pushed_at, and exact language byte splits.
Merges live telemetry with projects.json into merged.json.
"""
import json, os, sys, urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN", "")

def gh(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "projects-panel-agent",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
        
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    src_path = os.path.join(root_dir, "projects.json")
    out_path = os.path.join(root_dir, "merged.json")
    
    with open(src_path, "r", encoding="utf-8") as f:
        projects = json.load(f)
        
    for p in projects:
        repo = p.get("repo", "").strip()
        repo = repo.replace("https://github.com/", "").replace("http://github.com/", "").rstrip("/")
        p["repo"] = repo
        try:
            info = gh(f"https://api.github.com/repos/{repo}")
            p["stars"] = info.get("stargazers_count", 0)
            p["pushed_at"] = info.get("pushed_at")
            p["languages"] = gh(f"https://api.github.com/repos/{repo}/languages")
            print(f"[OK] Fetched live data for {repo} ({len(p['languages'])} languages)")
        except Exception as e:
            print(f"[!] Warning: could not fetch live data for {repo}: {e}", file=sys.stderr)
            p.setdefault("stars", 0)
            p.setdefault("languages", {})
            p.setdefault("pushed_at", None)
            
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)
    print(f"Successfully generated {out_path} with {len(projects)} projects.")

if __name__ == "__main__":
    main()
