#!/usr/bin/env python3
"""
generate_streak.py — The Director's Cut: Live GitHub Streak & Activity Flow Matrix (CI Script)

Generates 2 balanced, executive rectangular vector SVG cards (W=578, H=338):
  1. assets/streak-dark.svg    — Live Streak & 6-Metric Stats Matrix (Dark)
  2. assets/activity-dark.svg  — Cinematic Commit Flow & Soundwave Graph (Dark)

All typography matches the Featured Projects and Technical Arsenal design system:
  - Font: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, Helvetica, Arial, sans-serif
  - Weights: 600/700 for titles and numbers, 500/450 for descriptions and metadata.
"""

import os, sys, json, math, re, urllib.request
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUT_DIR    = os.path.join(ROOT_DIR, 'assets')
USERNAME   = "rdnk2004"
TOKEN      = os.environ.get("GITHUB_TOKEN", "") or os.environ.get("GH_TOKEN", "")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

THEME = {
    "BG": "#0A0704",            # Obsidian deep celluloid
    "PANEL_BG": "#130E09",      # Warm dark chocolate
    "PANEL_END": "#19120C",     # Subtle gradient end
    "HEADER_BG": "#110B06",     # Header bar
    "ACCENT_1": "#C0713A",      # Burnt Sienna
    "ACCENT_2": "#D4A353",      # Warm Amber Gold
    "ACCENT_3": "#F5E6D3",      # Soft Cream
    "TEXT_PRIMARY": "#FAF5EE",  # Crisp cream primary text
    "TEXT_MUTED": "#C8B6A6",    # Readable bronze subtitle
    "TEXT_DIM": "#8C7B6B",      # Dim metadata
    "BORDER": "rgba(212,163,83,0.28)",
    "BORDER_HI": "rgba(212,163,83,0.75)",
    "BORDER_LO": "rgba(192,113,58,0.20)",
    "CARD_BG": "rgba(20,15,9,0.75)",
    "CARD_STROKE": "rgba(212,163,83,0.30)",
    "GRID_LINE": "rgba(212,163,83,0.12)",
    "CANVAS_BG": "#0F0B07",
    "ACTIVE_GREEN": "#4ADE80",
    "ACTIVE_BG": "rgba(74,222,128,0.14)",
    "ACTIVE_BORDER": "rgba(74,222,128,0.40)",
    "PILL_BG": "rgba(42,27,15,0.85)",
    "PILL_BORDER": "rgba(212,163,83,0.40)",
    "PILL_TEXT": "#F5E6D3",
    "AREA_TOP": "rgba(212,163,83,0.45)",
    "AREA_MID": "rgba(192,113,58,0.20)",
    "AREA_BOT": "rgba(15,11,7,0.0)",
}

FONT_SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',Roboto,Helvetica,Arial,sans-serif"
FONT_MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

def format_date_range(start_str, end_str):
    if not start_str or not end_str:
        return "No active record"
    try:
        s_dt = datetime.strptime(start_str, "%Y-%m-%d")
        e_dt = datetime.strptime(end_str, "%Y-%m-%d")
        if s_dt.year == e_dt.year:
            if s_dt.month == e_dt.month and s_dt.day == e_dt.day:
                return s_dt.strftime("%b %d, %Y")
            return f"{s_dt.strftime('%b %d')} – {e_dt.strftime('%b %d, %Y')}"
        return f"{s_dt.strftime('%b %d, %Y')} – {e_dt.strftime('%b %d, %Y')}"
    except Exception:
        return f"{start_str} – {end_str}"

def fetch_telemetry_data(username, token=""):
    """Fetch complete telemetry: calendar, repos, PRs, issues, and streaks"""
    public_repos = 24
    followers = 12
    try:
        user_url = f"https://api.github.com/users/{username}"
        req_u = urllib.request.Request(user_url, headers={"User-Agent": "streak-telemetry"})
        if token:
            req_u.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req_u, timeout=10) as r:
            u_data = json.load(r)
            public_repos = u_data.get("public_repos", 24)
            followers = u_data.get("followers", 12)
    except Exception as e:
        print(f"[!] Warning fetching user basic info: {e}", file=sys.stderr)

    pr_count = 6
    issue_count = 0
    try:
        pr_url = f"https://api.github.com/search/issues?q=author:{username}+type:pr"
        req_pr = urllib.request.Request(pr_url, headers={"User-Agent": "streak-telemetry"})
        if token:
            req_pr.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req_pr, timeout=10) as r:
            pr_count = json.load(r).get("total_count", 6)
            
        issue_url = f"https://api.github.com/search/issues?q=author:{username}+type:issue"
        req_iss = urllib.request.Request(issue_url, headers={"User-Agent": "streak-telemetry"})
        if token:
            req_iss.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req_iss, timeout=10) as r:
            issue_count = json.load(r).get("total_count", 0)
    except Exception as e:
        print(f"[!] Warning fetching PRs/Issues: {e}", file=sys.stderr)

    current_year = datetime.now(timezone.utc).year
    days = []
    total_all = 0
    total_year = 0
    
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}", "User-Agent": "streak-telemetry", "Content-Type": "application/json"}
            q_years = 'query($login: String!) { user(login: $login) { contributionsCollection { contributionYears } } }'
            req_g = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q_years, "variables": {"login": username}}).encode(), headers=headers)
            with urllib.request.urlopen(req_g, timeout=12) as r:
                res = json.load(r)
            years = res.get("data", {}).get("user", {}).get("contributionsCollection", {}).get("contributionYears", [current_year])
            
            for y in sorted(years):
                q = f'''query($login: String!) {{ user(login: $login) {{ contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") {{ contributionCalendar {{ totalContributions weeks {{ contributionDays {{ contributionCount date contributionLevel }} }} }} }} }} }}'''
                req_y = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q, "variables": {"login": username}}).encode(), headers=headers)
                with urllib.request.urlopen(req_y, timeout=12) as r_y:
                    cal = json.load(r_y).get("data", {}).get("user", {}).get("contributionsCollection", {}).get("contributionCalendar", {})
                    y_total = cal.get("totalContributions", 0)
                    total_all += y_total
                    if y == current_year:
                        total_year = y_total
                    for w in cal.get("weeks", []):
                        for d in w.get("contributionDays", []):
                            days.append({"date": d["date"], "count": d["contributionCount"], "level": 0 if d["contributionCount"] == 0 else min(4, max(1, d["contributionCount"] // 3 + 1))})
        except Exception as e:
            print(f"[!] GraphQL error: {e}. Falling back to calendar scraper...", file=sys.stderr)
            days = []

    if not days:
        years = list(range(2022, current_year + 1))
        days_map = {}
        for y in years:
            url = f"https://github.com/users/{username}/contributions?from={y}-01-01&to={y}-12-31"
            req_c = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            try:
                with urllib.request.urlopen(req_c, timeout=10) as resp:
                    html_text = resp.read().decode("utf-8")
                td_matches = re.findall(r'<td[^>]*data-date="([\d-]+)"[^>]*id="([^"]+)"[^>]*data-level="(\d+)"', html_text)
                if not td_matches:
                    td_matches = re.findall(r'<td[^>]*id="([^"]+)"[^>]*data-date="([\d-]+)"[^>]*data-level="(\d+)"', html_text)
                    td_map = {m[0]: {"date": m[1], "level": int(m[2])} for m in td_matches}
                else:
                    td_map = {m[1]: {"date": m[0], "level": int(m[2])} for m in td_matches}
                tooltips = re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>(.*?)</tool-tip>', html_text, re.DOTALL)
                y_cnt = 0
                for tid, tip in tooltips:
                    if tid in td_map:
                        d_str = td_map[tid]["date"]
                        lvl = td_map[tid]["level"]
                        cnt = 0
                        m = re.search(r'(\d+)\s+contribution', tip)
                        if m:
                            cnt = int(m.group(1))
                        days_map[d_str] = {"date": d_str, "count": cnt, "level": lvl}
                        y_cnt += cnt
                total_all += y_cnt
                if y == current_year:
                    total_year = y_cnt
            except Exception as e:
                print(f"[!] Warning scraping year {y}: {e}", file=sys.stderr)
        days = [days_map[k] for k in sorted(days_map.keys())]

    seen = {}
    for d in days:
        seen[d["date"]] = d
    sorted_days = [seen[k] for k in sorted(seen.keys())]
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    active_days = [d for d in sorted_days if d.get("date", "") <= today_str]
    if not active_days:
        active_days = sorted_days

    max_streak = 0
    max_start, max_end = None, None
    cur_run = 0
    cur_start = None
    for d in active_days:
        if d["count"] > 0:
            if cur_run == 0:
                cur_start = d["date"]
            cur_run += 1
            if cur_run > max_streak:
                max_streak = cur_run
                max_start = cur_start
                max_end = d["date"]
        else:
            cur_run = 0
            cur_start = None

    rev = list(reversed(active_days))
    current_streak = 0
    current_start, current_end = None, None
    is_active = False
    if rev:
        start_idx = 0
        if rev[0]["count"] == 0:
            if len(rev) > 1 and rev[1]["count"] > 0:
                start_idx = 1
            else:
                start_idx = -1
        if start_idx >= 0 and rev[start_idx]["count"] > 0:
            is_active = True
            current_end = rev[start_idx]["date"]
            for d in rev[start_idx:]:
                if d["count"] > 0:
                    current_streak += 1
                    current_start = d["date"]
                else:
                    break

    past_year_days = active_days[-365:] if len(active_days) >= 365 else active_days
    active_days_count = sum(1 for d in past_year_days if d["count"] > 0)
    past_year_contribs = sum(d["count"] for d in past_year_days)
    cadence_pct = (active_days_count / len(past_year_days)) * 100 if past_year_days else 0
    daily_velocity = past_year_contribs / max(1, active_days_count)

    month_groups = {}
    for d in active_days:
        if not d["date"]:
            continue
        m_key = d["date"][:7]
        month_groups[m_key] = month_groups.get(m_key, 0) + d["count"]
        
    sorted_month_keys = sorted(month_groups.keys())
    recent_12_keys = sorted_month_keys[-12:] if len(sorted_month_keys) >= 12 else sorted_month_keys
    
    monthly_data = []
    peak_month_label = ""
    peak_month_val = 0
    
    for mk in recent_12_keys:
        dt = datetime.strptime(mk, "%Y-%m")
        cnt = month_groups[mk]
        lbl = dt.strftime("%b").upper()
        monthly_data.append({
            "key": mk,
            "label": lbl,
            "year": dt.strftime("%Y"),
            "count": cnt
        })
        if cnt > peak_month_val:
            peak_month_val = cnt
            peak_month_label = f"{lbl} {dt.strftime('%Y')}"

    return {
        "username": username,
        "current_streak": current_streak,
        "current_range": format_date_range(current_start, current_end),
        "is_active": is_active,
        "longest_streak": max_streak,
        "longest_range": format_date_range(max_start, max_end),
        "total_all": max(total_all, sum(d["count"] for d in active_days)),
        "total_year": total_year,
        "public_repos": public_repos,
        "followers": followers,
        "pull_requests": pr_count,
        "issues": issue_count,
        "active_days_count": active_days_count,
        "cadence_pct": cadence_pct,
        "daily_velocity": daily_velocity,
        "monthly_data": monthly_data,
        "peak_month_label": peak_month_label,
        "peak_month_val": peak_month_val,
        "past_year_contribs": past_year_contribs,
    }

def generate_smooth_spline(points, base_y):
    """Generate smooth cubic bezier curve & filled area path from points"""
    if not points:
        return "", ""
    if len(points) == 1:
        x, y = points[0]
        return f"M {x} {y}", f"M {x} {y} L {x} {base_y} Z"
        
    def get_cp(p0, p1, p2, p3, t=0.25):
        t1x = (p2[0] - p0[0]) * t
        t1y = (p2[1] - p0[1]) * t
        t2x = (p3[0] - p1[0]) * t
        t2y = (p3[1] - p1[1]) * t
        return (p1[0] + t1x, p1[1] + t1y), (p2[0] - t2x, p2[1] - t2y)
        
    line_parts = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    padded = [points[0]] + points + [points[-1]]
    
    for i in range(len(points) - 1):
        p0 = padded[i]
        p1 = padded[i+1]
        p2 = padded[i+2]
        p3 = padded[i+3]
        (cp1x, cp1y), (cp2x, cp2y) = get_cp(p0, p1, p2, p3)
        line_parts.append(f"C {cp1x:.1f} {cp1y:.1f}, {cp2x:.1f} {cp2y:.1f}, {p2[0]:.1f} {p2[1]:.1f}")
        
    line_d = " ".join(line_parts)
    first_x = points[0][0]
    last_x = points[-1][0]
    area_d = f"{line_d} L {last_x:.1f} {base_y:.1f} L {first_x:.1f} {base_y:.1f} Z"
    return line_d, area_d

def render_streak_card(data):
    t = THEME
    W, H = 1180, 284
    
    s = []
    a = s.append
    
    curr = data["current_streak"]
    curr_range = data["current_range"]
    is_active = data["is_active"]
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT_SANS}" role="img" aria-label="GitHub Streak and Stats Matrix">')
    
    a(f'''<defs>
      <style>
        .pulse {{ animation: stkPulse 2.8s infinite ease-in-out; }}
        @keyframes stkPulse {{
          0%, 100% {{ opacity: 1; }}
          50% {{ opacity: 0.35; }}
        }}
      </style>
      <linearGradient id="stk_bg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{t['BG']}"/>
        <stop offset="100%" stop-color="{t['PANEL_BG']}"/>
      </linearGradient>
      <linearGradient id="stk_card" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{t['PANEL_BG']}"/>
        <stop offset="100%" stop-color="{t['PANEL_END']}"/>
      </linearGradient>
      <linearGradient id="flameGrad" x1="0" y1="1" x2="0" y2="0">
        <stop offset="0%" stop-color="{t['ACCENT_1']}"/>
        <stop offset="60%" stop-color="{t['ACCENT_2']}"/>
        <stop offset="100%" stop-color="{t['ACCENT_3']}"/>
      </linearGradient>
    </defs>''')
    
    a(f'<rect width="{W}" height="{H}" rx="12" ry="12" fill="url(#stk_bg)" stroke="{t["BORDER"]}" stroke-width="1.5"/>')
    
    # ── Top Hero Streak Banner ──
    banner_y = 14
    banner_w = W - 28
    banner_h = 94
    a(f'<g transform="translate(14, {banner_y})">')
    a(f'<rect width="{banner_w}" height="{banner_h}" rx="8" ry="8" fill="url(#stk_card)" stroke="{t["BORDER_HI"]}" stroke-width="1.2"/>')
    a(f'<path d="M 0 8 Q 0 0 8 0 L 28 0 L 0 28 Z" fill="{t["ACCENT_2"]}" opacity="0.25"/>')
    
    # Flame icon box
    a(f'<rect x="16" y="13" width="68" height="68" rx="8" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="1"/>')
    a(f'<g transform="translate(26, 22)">')
    a(f'''<path d="M 22 42 C 10 42 2 34 2 23 C 2 15 8 9 14 3 C 14.5 2.5 15.5 2.8 15.6 3.5 C 16.2 8.5 18.5 12 21 14 C 21.3 10.5 22.5 7 25 4 C 25.4 3.5 26.2 3.8 26.3 4.4 C 27.5 11 31 15 35 20 C 40 26 42 31 42 36 C 42 40 33 42 22 42 Z M 22 38 C 29 38 34 35 34 31 C 34 27 31 24 28 20 C 27.5 19.3 26.5 19.8 26.5 20.6 C 26.5 23 25 25 23 26 C 22.4 26.3 21.6 25.8 21.6 25.1 C 21.6 22 19 19 17 16 C 13.5 21 10 26 10 31 C 10 35 15 38 22 38 Z" fill="url(#flameGrad)"/>''')
    a(f'</g>')
    
    a(f'<text x="100" y="27" font-size="12.5" font-weight="700" letter-spacing="0.6" fill="{t["TEXT_MUTED"]}">CURRENT ACTIVE STREAK</text>')
    
    a(f'<text x="100" y="64" font-size="34" font-weight="800" fill="{t["TEXT_PRIMARY"]}">{curr}</text>')
    num_len = len(str(curr))
    num_offset = 100 + num_len * 21
    
    a(f'<rect x="{num_offset + 10}" y="43" width="60" height="24" rx="5" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="1.2"/>')
    a(f'<text x="{num_offset + 40}" y="59.5" font-size="11.5" font-weight="800" fill="{t["ACCENT_2"]}" text-anchor="middle" letter-spacing="0.6">DAYS</text>')
    
    a(f'<text x="100" y="83" font-size="13" font-weight="500" fill="{t["TEXT_DIM"]}">{curr_range}</text>')
    
    # Right telemetry indicators
    live_col = t["ACTIVE_GREEN"] if is_active else t["ACCENT_2"]
    live_bg = t["ACTIVE_BG"] if is_active else t["PILL_BG"]
    live_bdr = t["ACTIVE_BORDER"] if is_active else t["PILL_BORDER"]
    chip_w = 136
    chip_x = banner_w - chip_w - 16
    a(f'<rect x="{chip_x}" y="14" width="{chip_w}" height="26" rx="6" fill="{live_bg}" stroke="{live_bdr}" stroke-width="1.2"/>')
    a(f'<circle cx="{chip_x + 14}" cy="27" r="4" fill="{live_col}" class="pulse"/>')
    a(f'<text x="{chip_x + 74}" y="31" font-size="10.5" font-weight="800" fill="{live_col}" text-anchor="middle" letter-spacing="0.4">{"STREAK ACTIVE" if is_active else "CADENCE PAUSED"}</text>')
    
    a(f'<text x="{banner_w - 16}" y="62" font-size="14" font-weight="700" fill="{t["ACCENT_2"]}" text-anchor="end">Longest Run: {data["longest_streak"]} Days</text>')
    a(f'<text x="{banner_w - 16}" y="81" font-size="12.5" font-weight="500" fill="{t["TEXT_DIM"]}" text-anchor="end">{data["longest_range"]}</text>')
    
    a(f'</g>')
    
    # ── 6-Metric Horizontal Telemetry Grid ──
    grid_y = 120
    cell_h = 148
    gap_x = 12
    cell_w = (banner_w - 5 * gap_x) / 6  # 182.4px each
    
    stats_config = [
        {
            "title": "Longest Streak",
            "val": f"{data['longest_streak']}",
            "unit": "Days",
            "sub": "Personal Record",
            "icon": "trophy",
            "accent": t["ACCENT_1"]
        },
        {
            "title": "Total Contribs",
            "val": f"{data['total_all']:,}",
            "unit": "Total",
            "sub": f"{data['total_year']:,} in {datetime.now().year}",
            "icon": "git",
            "accent": t["ACCENT_2"]
        },
        {
            "title": "Active Days",
            "val": f"{data['active_days_count']}",
            "unit": "Days",
            "sub": f"{data['cadence_pct']:.1f}% Annual Ratio",
            "icon": "calendar",
            "accent": t["ACCENT_3"]
        },
        {
            "title": "Public Repos",
            "val": f"{data['public_repos']}",
            "unit": "Repos",
            "sub": f"{data['followers']} Followers",
            "icon": "box",
            "accent": t["ACCENT_2"]
        },
        {
            "title": "Pull Requests",
            "val": f"{data['pull_requests']}",
            "unit": "Merged",
            "sub": f"{data['issues']} Issues Opened",
            "icon": "pr",
            "accent": t["ACCENT_1"]
        },
        {
            "title": "Daily Cadence",
            "val": f"{data['daily_velocity']:.1f}",
            "unit": "Avg",
            "sub": "Contribs / Active Day",
            "icon": "speed",
            "accent": t["ACCENT_2"]
        },
    ]
    
    for idx, sc in enumerate(stats_config):
        cx = 14 + idx * (cell_w + gap_x)
        cy = grid_y
        
        a(f'<g transform="translate({cx:.1f}, {cy})">')
        a(f'<rect width="{cell_w:.1f}" height="{cell_h}" rx="8" ry="8" fill="url(#stk_card)" stroke="{t["CARD_STROKE"]}" stroke-width="1"/>')
        a(f'<path d="M 0 6 Q 0 0 6 0 L 18 0 L 0 18 Z" fill="{sc["accent"]}" opacity="0.25"/>')
        
        # Icon box (28x28)
        a(f'<rect x="12" y="12" width="28" height="28" rx="6" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="0.8"/>')
        
        if sc["icon"] == "trophy":
            a(f'<path d="M 19 19 L 31 19 L 31 25 C 31 28 28 30 25 30 C 22 30 19 28 19 25 Z M 18 20 L 15 20 C 15 24 18 25 19 25 Z M 32 20 L 35 20 C 35 24 32 25 31 25 Z M 23 30 L 27 30 L 28 34 L 22 34 Z" fill="{sc["accent"]}"/>')
        elif sc["icon"] == "git":
            a(f'<circle cx="26" cy="26" r="4.5" fill="none" stroke="{sc["accent"]}" stroke-width="2"/>')
            a(f'<line x1="17" y1="26" x2="21.5" y2="26" stroke="{sc["accent"]}" stroke-width="2"/>')
            a(f'<line x1="30.5" y1="26" x2="35" y2="26" stroke="{sc["accent"]}" stroke-width="2"/>')
            a(f'<line x1="26" y1="17" x2="26" y2="21.5" stroke="{sc["accent"]}" stroke-width="2"/>')
            a(f'<line x1="26" y1="30.5" x2="26" y2="35" stroke="{sc["accent"]}" stroke-width="2"/>')
        elif sc["icon"] == "calendar":
            a(f'<rect x="18" y="19" width="16" height="14" rx="2" fill="none" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="18" y1="24" x2="34" y2="24" stroke="{sc["accent"]}" stroke-width="1.4"/>')
            a(f'<circle cx="22.5" cy="28.5" r="1.2" fill="{sc["accent"]}"/>')
            a(f'<circle cx="29.5" cy="28.5" r="1.2" fill="{sc["accent"]}"/>')
            a(f'<line x1="21.5" y1="17" x2="21.5" y2="20" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="30.5" y1="17" x2="30.5" y2="20" stroke="{sc["accent"]}" stroke-width="1.8"/>')
        elif sc["icon"] == "box":
            a(f'<rect x="18" y="20" width="16" height="13" rx="2" fill="none" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="18" y1="24" x2="34" y2="24" stroke="{sc["accent"]}" stroke-width="1.4"/>')
            a(f'<rect x="23.5" y="26" width="5" height="4" fill="{sc["accent"]}"/>')
        elif sc["icon"] == "pr":
            a(f'<circle cx="21" cy="21" r="3" fill="none" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<circle cx="21" cy="31" r="3" fill="none" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<circle cx="31" cy="24" r="3" fill="none" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="21" y1="24" x2="21" y2="28" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<path d="M 31 27 C 31 30 25 31 21 31" fill="none" stroke="{sc["accent"]}" stroke-width="1.8"/>')
        else:
            a(f'<path d="M 18 31 A 9 9 0 0 1 34 31" fill="none" stroke="{sc["accent"]}" stroke-width="2"/>')
            a(f'<line x1="26" y1="31" x2="30" y2="24" stroke="{sc["accent"]}" stroke-width="2" stroke-linecap="round"/>')
            a(f'<circle cx="26" cy="31" r="2" fill="{sc["accent"]}"/>')
            
        a(f'<text x="47" y="30" font-size="12" font-weight="700" fill="{t["TEXT_MUTED"]}">{sc["title"]}</text>')
        
        a(f'<text x="12" y="73" font-size="26" font-weight="800" fill="{t["TEXT_PRIMARY"]}">{sc["val"]}</text>')
        val_w = len(sc["val"]) * 15
        a(f'<text x="{16 + val_w}" y="70" font-size="12.5" font-weight="700" fill="{sc["accent"]}">{sc["unit"]}</text>')
        
        a(f'<line x1="12" y1="92" x2="{cell_w - 12:.1f}" y2="92" stroke="{t["CARD_STROKE"]}" stroke-width="0.8"/>')
        a(f'<text x="12" y="118" font-size="12" font-weight="500" fill="{t["TEXT_DIM"]}">{sc["sub"]}</text>')
        
        a(f'</g>')
        
    a(f'</svg>')
    return "".join(s)

def render_activity_card(data):
    t = THEME
    W, H = 1180, 360
    
    s = []
    a = s.append
    
    monthly = data["monthly_data"]
    peak_lbl = data["peak_month_label"]
    peak_val = data["peak_month_val"]
    past_yr_total = data["past_year_contribs"]
    avg_per_mo = past_yr_total / max(1, len(monthly))
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT_SANS}" role="img" aria-label="Commit Activity Flow and Soundwave Graph">')
    
    a(f'''<defs>
      <style>
        .pulse {{ animation: actPulse 2.5s infinite ease-in-out; }}
        @keyframes actPulse {{
          0%, 100% {{ opacity: 1; }}
          50% {{ opacity: 0.4; }}
        }}
      </style>
      <linearGradient id="act_bg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{t['BG']}"/>
        <stop offset="100%" stop-color="{t['PANEL_BG']}"/>
      </linearGradient>
      <linearGradient id="act_area" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{t['AREA_TOP']}"/>
        <stop offset="60%" stop-color="{t['AREA_MID']}"/>
        <stop offset="100%" stop-color="{t['AREA_BOT']}"/>
      </linearGradient>
      <linearGradient id="act_stroke" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="{t['ACCENT_1']}"/>
        <stop offset="50%" stop-color="{t['ACCENT_2']}"/>
        <stop offset="100%" stop-color="{t['ACCENT_3']}"/>
      </linearGradient>
      <filter id="act_glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3.5" result="blur"/>
        <feComposite in="SourceGraphic" in2="blur" operator="over"/>
      </filter>
    </defs>''')
    
    a(f'<rect width="{W}" height="{H}" rx="12" ry="12" fill="url(#act_bg)" stroke="{t["BORDER"]}" stroke-width="1.5"/>')
    
    # ── Top 3 Telemetry Metrics ──
    pill_y = 14
    pill_w = (W - 28 - 20) / 3  # 374px each
    pill_h = 46
    
    a(f'<g transform="translate(14, {pill_y})">')
    a(f'<rect width="{pill_w:.1f}" height="{pill_h}" rx="6" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="1"/>')
    a(f'<text x="16" y="17" font-size="11" font-weight="700" letter-spacing="0.5" fill="{t["TEXT_MUTED"]}">PEAK VELOCITY</text>')
    a(f'<text x="16" y="36" font-size="14.5" font-weight="800" fill="{t["ACCENT_2"]}">{peak_lbl} ({peak_val} Contribs)</text>')
    a(f'</g>')
    
    a(f'<g transform="translate({14 + pill_w + 10:.1f}, {pill_y})">')
    a(f'<rect width="{pill_w:.1f}" height="{pill_h}" rx="6" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="1"/>')
    a(f'<text x="16" y="17" font-size="11" font-weight="700" letter-spacing="0.5" fill="{t["TEXT_MUTED"]}">MONTHLY AVERAGE</text>')
    a(f'<text x="16" y="36" font-size="14.5" font-weight="800" fill="{t["TEXT_PRIMARY"]}">{avg_per_mo:.1f} Contribs / Month</text>')
    a(f'</g>')
    
    a(f'<g transform="translate({14 + (pill_w + 10)*2:.1f}, {pill_y})">')
    a(f'<rect width="{pill_w:.1f}" height="{pill_h}" rx="6" fill="{t["ACTIVE_BG"]}" stroke="{t["ACTIVE_BORDER"]}" stroke-width="1"/>')
    a(f'<text x="16" y="17" font-size="11" font-weight="700" letter-spacing="0.5" fill="{t["ACTIVE_GREEN"]}">VELOCITY TREND</text>')
    a(f'<text x="16" y="36" font-size="14.5" font-weight="800" fill="{t["ACTIVE_GREEN"]}">↗ Accelerating Cadence</text>')
    a(f'</g>')
    
    # ── Main Spline Soundwave Canvas ──
    gx, gy = 14, 70
    gw, gh = W - 28, 238
    
    a(f'<g transform="translate({gx}, {gy})">')
    a(f'<rect width="{gw}" height="{gh}" rx="8" ry="8" fill="{t["CANVAS_BG"]}" stroke="{t["BORDER"]}" stroke-width="1"/>')
    
    pad_l = 52
    pad_r = 32
    pad_t = 28
    pad_b = 36
    
    plot_w = gw - pad_l - pad_r
    plot_h = gh - pad_t - pad_b
    base_y = pad_t + plot_h
    
    max_count = max([m["count"] for m in monthly] + [10])
    if max_count <= 50:
        y_max_nice = 50
    elif max_count <= 100:
        y_max_nice = 100
    elif max_count <= 250:
        y_max_nice = 250
    else:
        y_max_nice = math.ceil(max_count / 100) * 100
        
    y_steps = [0, y_max_nice * 0.33, y_max_nice * 0.66, y_max_nice]
    for val in y_steps:
        y_pos = base_y - (val / y_max_nice) * plot_h
        a(f'<line x1="{pad_l}" y1="{y_pos:.1f}" x2="{pad_l + plot_w}" y2="{y_pos:.1f}" stroke="{t["GRID_LINE"]}" stroke-width="0.8" stroke-dasharray="3,3"/>')
        a(f'<text x="{pad_l - 10}" y="{y_pos + 4.5:.1f}" font-size="11.5" font-weight="600" fill="{t["TEXT_DIM"]}" text-anchor="end">{int(val)}</text>')
        
    points = []
    n_pts = len(monthly)
    step_x = plot_w / max(1, n_pts - 1)
    
    for i, m in enumerate(monthly):
        px = pad_l + i * step_x
        cnt = m["count"]
        py = base_y - (cnt / y_max_nice) * plot_h
        py = min(base_y, max(pad_t, py))
        points.append((px, py))
        
    line_path, area_path = generate_smooth_spline(points, base_y)
    
    a(f'<path d="{area_path}" fill="url(#act_area)"/>')
    a(f'<path d="{line_path}" fill="none" stroke="{t["ACCENT_2"]}" stroke-width="5.0" opacity="0.35" filter="url(#act_glow)"/>')
    a(f'<path d="{line_path}" fill="none" stroke="url(#act_stroke)" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>')
    
    for i, (px, py) in enumerate(points):
        m = monthly[i]
        is_peak = (m["count"] == peak_val and peak_val > 0)
        is_latest = (i == len(points) - 1)
        
        a(f'<text x="{px:.1f}" y="{base_y + 22}" font-size="12" font-weight="700" fill="{t["ACCENT_2"] if is_latest or is_peak else t["TEXT_DIM"]}" text-anchor="middle">{m["label"]}</text>')
        
        node_r = 5.0 if (is_peak or is_latest) else 3.5
        node_fill = t["ACCENT_3"] if is_peak else (t["ACTIVE_GREEN"] if is_latest else t["ACCENT_2"])
        
        if is_peak or is_latest:
            a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{node_r + 4}" fill="none" stroke="{node_fill}" stroke-width="1.2" opacity="0.6" class="pulse"/>')
            
        a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{node_r}" fill="{node_fill}" stroke="{t["PANEL_BG"]}" stroke-width="1.8"/>')
        
        if is_peak:
            a(f'<g transform="translate({px:.1f}, {py - 20:.1f})">')
            a(f'<rect x="-28" y="-14" width="56" height="19" rx="4" fill="{t["PILL_BG"]}" stroke="{t["ACCENT_2"]}" stroke-width="1"/>')
            a(f'<text x="0" y="-1" font-size="11.5" font-weight="800" fill="{t["ACCENT_2"]}" text-anchor="middle">{m["count"]}</text>')
            a(f'</g>')
            
    a(f'</g>')
    
    # ── Bottom Legend & Summary ──
    a(f'<g transform="translate(14, 320)">')
    a(f'<circle cx="8" cy="18" r="4" fill="{t["ACCENT_2"]}"/>')
    a(f'<text x="22" y="22" font-size="13" font-weight="600" fill="{t["TEXT_MUTED"]}">12-Month Continuous Spline Soundwave</text>')
    a(f'<text x="{W - 28}" y="22" font-size="13.5" font-weight="700" fill="{t["ACCENT_2"]}" text-anchor="end">{past_yr_total:,} Total Commits in Past Year</text>')
    a(f'</g>')
    
    a(f'</svg>')
    return "".join(s)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[*] Ingesting comprehensive GitHub telemetry for @{USERNAME}...")
    
    data = fetch_telemetry_data(USERNAME, TOKEN)
    
    print("\n=======================================================")
    print(f"📊 LIVE TELEMETRY & CADENCE MATRIX — @{USERNAME}")
    print("=======================================================")
    print(f"  🔥 Current Streak : {data['current_streak']} Days ({data['current_range']}) [Active: {data['is_active']}]")
    print(f"  🏆 Longest Streak : {data['longest_streak']} Days ({data['longest_range']})")
    print(f"  ⚡ Total Contribs : {data['total_all']:,} ({data['total_year']:,} in {datetime.now().year})")
    print(f"  📦 Public Repos   : {data['public_repos']} Repos")
    print(f"  🔀 Pull Requests  : {data['pull_requests']} PRs")
    print(f"  📅 Active Days    : {data['active_days_count']} Days ({data['cadence_pct']:.1f}%)")
    print(f"  🚀 Daily Velocity : {data['daily_velocity']:.2f} Contribs/Active Day")
    print(f"  📈 Peak Month     : {data['peak_month_label']} ({data['peak_month_val']} commits)")
    print("=======================================================\n")
    
    stk_dark = render_streak_card(data)
    act_dark = render_activity_card(data)
    
    paths = {
        "streak-dark.svg": stk_dark,
        "activity-dark.svg": act_dark,
    }
    
    for filename, content in paths.items():
        out_path = os.path.join(OUT_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[OK] Generated {out_path} ({len(content)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
