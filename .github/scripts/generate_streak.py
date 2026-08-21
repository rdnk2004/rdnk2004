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

    # 30-Day micro telemetry
    last_30_days = active_days[-30:] if len(active_days) >= 30 else active_days
    last_30_total = sum(d["count"] for d in last_30_days)
    last_30_active = sum(1 for d in last_30_days if d["count"] > 0)
    last_30_avg = last_30_total / max(1, len(last_30_days))
    peak_30_val = max([d["count"] for d in last_30_days] + [1])
    peak_30_idx = 0
    for idx, d in enumerate(last_30_days):
        if d["count"] == peak_30_val:
            peak_30_idx = idx

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
        "last_30_days": last_30_days,
        "last_30_total": last_30_total,
        "last_30_active": last_30_active,
        "last_30_avg": last_30_avg,
        "peak_30_val": peak_30_val,
        "peak_30_idx": peak_30_idx,
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
    W, H = 1180, 296
    
    s = []
    a = s.append
    
    curr = data["current_streak"]
    curr_range = data["current_range"]
    is_active = data["is_active"]
    username = data["username"]
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT_SANS}" role="img" aria-label="GitHub Streak and Stats Matrix">')
    
    a(f'''<defs>
      <style>
        .pulse {{ animation: stkPulse 2.8s infinite ease-in-out; }}
        @keyframes stkPulse {{
          0%, 100% {{ opacity: 1; transform: scale(1); }}
          50% {{ opacity: 0.4; transform: scale(0.92); }}
        }}
        .hero-banner {{
          transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), filter 0.25s ease;
        }}
        .hero-banner:hover {{
          filter: drop-shadow(0 6px 20px rgba(212, 163, 83, 0.25));
        }}
        .metric-cell {{
          transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), filter 0.25s ease;
          cursor: pointer;
        }}
        .metric-cell:hover {{
          transform: translateY(-4px);
          filter: drop-shadow(0 10px 22px rgba(0, 0, 0, 0.65)) drop-shadow(0 0 10px rgba(212, 163, 83, 0.35));
        }}
        .metric-cell:hover .cell-bg {{
          stroke: rgba(212, 163, 83, 0.85);
          fill: rgba(38, 25, 14, 0.95);
        }}
        .metric-cell:hover .cell-title {{
          fill: #FAF5EE;
        }}
        .metric-cell:hover .cell-val {{
          fill: #D4A353;
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
    banner_h = 96
    a(f'<g transform="translate(14, {banner_y})" class="hero-banner">')
    a(f'<rect width="{banner_w}" height="{banner_h}" rx="8" ry="8" fill="url(#stk_card)" stroke="{t["BORDER_HI"]}" stroke-width="1.2"/>')
    a(f'<path d="M 0 8 Q 0 0 8 0 L 28 0 L 0 28 Z" fill="{t["ACCENT_2"]}" opacity="0.25"/>')
    
    # Flame icon box
    a(f'<rect x="16" y="14" width="68" height="68" rx="8" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="1"/>')
    a(f'<g transform="translate(26, 23)">')
    a(f'''<path d="M 22 42 C 10 42 2 34 2 23 C 2 15 8 9 14 3 C 14.5 2.5 15.5 2.8 15.6 3.5 C 16.2 8.5 18.5 12 21 14 C 21.3 10.5 22.5 7 25 4 C 25.4 3.5 26.2 3.8 26.3 4.4 C 27.5 11 31 15 35 20 C 40 26 42 31 42 36 C 42 40 33 42 22 42 Z M 22 38 C 29 38 34 35 34 31 C 34 27 31 24 28 20 C 27.5 19.3 26.5 19.8 26.5 20.6 C 26.5 23 25 25 23 26 C 22.4 26.3 21.6 25.8 21.6 25.1 C 21.6 22 19 19 17 16 C 13.5 21 10 26 10 31 C 10 35 15 38 22 38 Z" fill="url(#flameGrad)"/>''')
    a(f'</g>')
    
    a(f'<text x="102" y="29" font-size="14.5" font-weight="550" letter-spacing="0.8" fill="{t["TEXT_MUTED"]}">CURRENT ACTIVE STREAK</text>')
    
    a(f'<text x="102" y="75" font-size="44" font-weight="600" fill="{t["TEXT_PRIMARY"]}">{curr}</text>')
    num_len = len(str(curr))
    num_offset = 102 + num_len * 27
    
    a(f'<rect x="{num_offset + 12}" y="50" width="70" height="28" rx="6" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="1"/>')
    a(f'<text x="{num_offset + 47}" y="69" font-size="13" font-weight="600" fill="{t["ACCENT_2"]}" text-anchor="middle" letter-spacing="0.8">DAYS</text>')
    
    # Right telemetry indicators (Prominent, non-duplicate, larger font)
    live_col = t["ACTIVE_GREEN"] if is_active else t["ACCENT_2"]
    live_bg = t["ACTIVE_BG"] if is_active else t["PILL_BG"]
    live_bdr = t["ACTIVE_BORDER"] if is_active else t["PILL_BORDER"]
    chip_w = 160
    chip_h = 28
    chip_x = banner_w - chip_w - 18
    a(f'<rect x="{chip_x}" y="13" width="{chip_w}" height="{chip_h}" rx="6" fill="{live_bg}" stroke="{live_bdr}" stroke-width="1"/>')
    a(f'<circle cx="{chip_x + 16}" cy="27" r="4.5" fill="{live_col}" class="pulse"/>')
    a(f'<text x="{chip_x + 82}" y="32" font-size="13" font-weight="600" fill="{live_col}" text-anchor="middle" letter-spacing="0.5">{"STREAK ACTIVE" if is_active else "CADENCE PAUSED"}</text>')
    
    a(f'<text x="{banner_w - 18}" y="63" font-size="18.5" font-weight="600" fill="{t["ACCENT_2"]}" text-anchor="end">Longest Run: {data["longest_streak"]} Days</text>')
    a(f'<text x="{banner_w - 18}" y="85" font-size="14.5" font-weight="500" fill="{t["TEXT_MUTED"]}" text-anchor="end">{data["longest_range"]}</text>')
    
    a(f'</g>')
    
    # ── 6-Metric Horizontal Telemetry Grid (Interactive Hover & Links) ──
    grid_y = 124
    cell_h = 158
    gap_x = 12
    cell_w = (banner_w - 5 * gap_x) / 6  # 182.4px each
    
    stats_config = [
        {
            "title": "Longest Streak",
            "val": f"{data['longest_streak']}",
            "unit": "Days",
            "sub": "Personal Record",
            "icon": "trophy",
            "accent": t["ACCENT_1"],
            "url": f"https://github.com/{username}?tab=overview"
        },
        {
            "title": "Total Contribs",
            "val": f"{data['total_all']:,}",
            "unit": "Total",
            "sub": f"{data['total_year']:,} in {datetime.now().year}",
            "icon": "git",
            "accent": t["ACCENT_2"],
            "url": f"https://github.com/{username}?tab=overview"
        },
        {
            "title": "Active Days",
            "val": f"{data['active_days_count']}",
            "unit": "Days",
            "sub": f"{data['cadence_pct']:.1f}% Annual Ratio",
            "icon": "calendar",
            "accent": t["ACCENT_3"],
            "url": f"https://github.com/{username}?tab=overview"
        },
        {
            "title": "Public Repos",
            "val": f"{data['public_repos']}",
            "unit": "Repos",
            "sub": f"{data['followers']} Followers",
            "icon": "box",
            "accent": t["ACCENT_2"],
            "url": f"https://github.com/{username}?tab=repositories"
        },
        {
            "title": "Pull Requests",
            "val": f"{data['pull_requests']}",
            "unit": "Merged",
            "sub": f"{data['issues']} Issues Opened",
            "icon": "pr",
            "accent": t["ACCENT_1"],
            "url": f"https://github.com/{username}?tab=overview&from=2026-01-01"
        },
        {
            "title": "Daily Cadence",
            "val": f"{data['daily_velocity']:.1f}",
            "unit": "Avg",
            "sub": "Contribs / Active Day",
            "icon": "speed",
            "accent": t["ACCENT_2"],
            "url": f"https://github.com/{username}?tab=overview"
        },
    ]
    
    for idx, sc in enumerate(stats_config):
        cx = 14 + idx * (cell_w + gap_x)
        cy = grid_y
        
        a(f'<a href="{sc["url"]}" target="_blank" rel="noopener noreferrer">')
        a(f'<g transform="translate({cx:.1f}, {cy})" class="metric-cell">')
        a(f'<rect width="{cell_w:.1f}" height="{cell_h}" rx="8" ry="8" fill="url(#stk_card)" stroke="{t["CARD_STROKE"]}" stroke-width="1" class="cell-bg"/>')
        a(f'<path d="M 0 6 Q 0 0 6 0 L 18 0 L 0 18 Z" fill="{sc["accent"]}" opacity="0.25"/>')
        
        # Icon box (30x30)
        a(f'<rect x="12" y="12" width="30" height="30" rx="6" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="0.8"/>')
        
        if sc["icon"] == "trophy":
            a(f'<path d="M 20 20 L 34 20 L 34 26 C 34 29.5 30.5 32 27 32 C 23.5 32 20 29.5 20 26 Z M 19 21 L 16 21 C 16 25.5 19 27 20 27 Z M 35 21 L 38 21 C 38 25.5 35 27 34 27 Z M 25 32 L 29 32 L 30 36 L 24 36 Z" fill="{sc["accent"]}"/>')
        elif sc["icon"] == "git":
            a(f'<circle cx="27" cy="27" r="5" fill="none" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="17" y1="27" x2="22" y2="27" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="32" y1="27" x2="37" y2="27" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="27" y1="17" x2="27" y2="22" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="27" y1="32" x2="27" y2="37" stroke="{sc["accent"]}" stroke-width="1.8"/>')
        elif sc["icon"] == "calendar":
            a(f'<rect x="18" y="19" width="18" height="15" rx="2" fill="none" stroke="{sc["accent"]}" stroke-width="1.6"/>')
            a(f'<line x1="18" y1="24.5" x2="36" y2="24.5" stroke="{sc["accent"]}" stroke-width="1.2"/>')
            a(f'<circle cx="23" cy="29.5" r="1.3" fill="{sc["accent"]}"/>')
            a(f'<circle cx="31" cy="29.5" r="1.3" fill="{sc["accent"]}"/>')
            a(f'<line x1="22" y1="17" x2="22" y2="20" stroke="{sc["accent"]}" stroke-width="1.6"/>')
            a(f'<line x1="32" y1="17" x2="32" y2="20" stroke="{sc["accent"]}" stroke-width="1.6"/>')
        elif sc["icon"] == "box":
            a(f'<rect x="18" y="20" width="18" height="14" rx="2" fill="none" stroke="{sc["accent"]}" stroke-width="1.6"/>')
            a(f'<line x1="18" y1="24.5" x2="36" y2="24.5" stroke="{sc["accent"]}" stroke-width="1.2"/>')
            a(f'<rect x="24" y="27" width="6" height="4.5" fill="{sc["accent"]}"/>')
        elif sc["icon"] == "pr":
            a(f'<circle cx="22" cy="21" r="3.2" fill="none" stroke="{sc["accent"]}" stroke-width="1.6"/>')
            a(f'<circle cx="22" cy="32" r="3.2" fill="none" stroke="{sc["accent"]}" stroke-width="1.6"/>')
            a(f'<circle cx="32" cy="25" r="3.2" fill="none" stroke="{sc["accent"]}" stroke-width="1.6"/>')
            a(f'<line x1="22" y1="24.2" x2="22" y2="28.8" stroke="{sc["accent"]}" stroke-width="1.6"/>')
            a(f'<path d="M 32 28.2 C 32 31.5 26 32 22 32" fill="none" stroke="{sc["accent"]}" stroke-width="1.6"/>')
        else:
            a(f'<path d="M 19 33 A 9.5 9.5 0 0 1 35 33" fill="none" stroke="{sc["accent"]}" stroke-width="1.8"/>')
            a(f'<line x1="27" y1="33" x2="31" y2="25" stroke="{sc["accent"]}" stroke-width="1.8" stroke-linecap="round"/>')
            a(f'<circle cx="27" cy="33" r="2.2" fill="{sc["accent"]}"/>')
            
        a(f'<text x="50" y="32.5" font-size="14.5" font-weight="600" fill="{t["TEXT_PRIMARY"]}" class="cell-title">{sc["title"]}</text>')
        
        a(f'<text x="12" y="82" font-size="36" font-weight="600" fill="{t["TEXT_PRIMARY"]}" class="cell-val">{sc["val"]}</text>')
        val_w = len(sc["val"]) * 21
        a(f'<text x="{16 + val_w}" y="77" font-size="14.5" font-weight="550" fill="{sc["accent"]}">{sc["unit"]}</text>')
        
        a(f'<line x1="12" y1="101" x2="{cell_w - 12:.1f}" y2="101" stroke="{t["BORDER"]}" stroke-width="1.0"/>')
        a(f'<text x="12" y="132" font-size="14" font-weight="500" fill="{t["TEXT_MUTED"]}">{sc["sub"]}</text>')
        
        a(f'</g>')
        a(f'</a>')
        
    a(f'</svg>')
    return "".join(s)

def render_activity_card(data):
    t = THEME
    W, H = 1180, 376
    
    s = []
    a = s.append
    
    monthly = data["monthly_data"]
    peak_lbl = data["peak_month_label"]
    peak_val = data["peak_month_val"]
    past_yr_total = data["past_year_contribs"]
    avg_per_mo = past_yr_total / max(1, len(monthly))
    
    last_30 = data.get("last_30_days", [])
    last_30_tot = data.get("last_30_total", 0)
    last_30_act = data.get("last_30_active", 0)
    last_30_avg = data.get("last_30_avg", 0.0)
    peak_30_val = data.get("peak_30_val", 1)
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT_SANS}" role="img" aria-label="Commit Activity Flow: 12-Month Macro and 30-Day Cadence">')
    
    a(f'''<defs>
      <style>
        .pulse {{ animation: actPulse 2.5s infinite ease-in-out; }}
        @keyframes actPulse {{
          0%, 100% {{ opacity: 1; }}
          50% {{ opacity: 0.4; }}
        }}
        .act-panel {{
          transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), filter 0.25s ease;
        }}
        .act-panel:hover {{
          filter: drop-shadow(0 6px 18px rgba(0, 0, 0, 0.5));
        }}
        .node-interactive {{
          cursor: pointer;
        }}
        .node-interactive .tooltip-pop {{
          opacity: 0;
          transform: translateY(6px);
          transition: opacity 0.18s ease, transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
          pointer-events: none;
        }}
        .node-interactive:hover .tooltip-pop {{
          opacity: 1;
          transform: translateY(0px);
        }}
        .node-interactive .node-glow-ring {{
          opacity: 0;
          transform: scale(0.8);
          transition: all 0.2s ease;
          transform-origin: center;
        }}
        .node-interactive:hover .node-glow-ring {{
          opacity: 1;
          transform: scale(1.6);
        }}
        .node-interactive:hover .node-core {{
          transform: scale(1.35);
          filter: drop-shadow(0 0 6px rgba(212, 163, 83, 0.9));
        }}
        .node-interactive:hover .tick-label {{
          fill: #FAF5EE;
          font-weight: 700;
        }}
      </style>
      <linearGradient id="act_bg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{t['BG']}"/>
        <stop offset="100%" stop-color="{t['PANEL_BG']}"/>
      </linearGradient>
      <linearGradient id="act_area_m" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="{t['AREA_TOP']}"/>
        <stop offset="60%" stop-color="{t['AREA_MID']}"/>
        <stop offset="100%" stop-color="{t['AREA_BOT']}"/>
      </linearGradient>
      <linearGradient id="act_area_d" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="rgba(74,222,128,0.38)"/>
        <stop offset="60%" stop-color="rgba(212,163,83,0.18)"/>
        <stop offset="100%" stop-color="rgba(15,11,7,0.0)"/>
      </linearGradient>
      <linearGradient id="act_stroke_m" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="{t['ACCENT_1']}"/>
        <stop offset="50%" stop-color="{t['ACCENT_2']}"/>
        <stop offset="100%" stop-color="{t['ACCENT_3']}"/>
      </linearGradient>
      <linearGradient id="act_stroke_d" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="{t['ACCENT_2']}"/>
        <stop offset="60%" stop-color="{t['ACTIVE_GREEN']}"/>
        <stop offset="100%" stop-color="#86EFAC"/>
      </linearGradient>
      <filter id="act_glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3.5" result="blur"/>
        <feComposite in="SourceGraphic" in2="blur" operator="over"/>
      </filter>
    </defs>''')
    
    a(f'<rect width="{W}" height="{H}" rx="12" ry="12" fill="url(#act_bg)" stroke="{t["BORDER"]}" stroke-width="1.5"/>')
    
    panel_w = 569
    panel_h = 348
    
    # ═══════════════════════════════════════════════════════════════════
    #  LEFT HALF: 12-MONTH MACRO COMMIT SOUNDWAVE
    # ═══════════════════════════════════════════════════════════════════
    a(f'<g transform="translate(14, 14)" class="act-panel">')
    a(f'<rect width="{panel_w}" height="{panel_h}" rx="10" ry="10" fill="{t["CANVAS_BG"]}" stroke="{t["BORDER"]}" stroke-width="1.2"/>')
    
    # Header bar
    a(f'<rect width="{panel_w}" height="46" rx="10" fill="{t["PANEL_BG"]}" stroke="{t["BORDER_LO"]}" stroke-width="0.8"/>')
    a(f'<rect y="36" width="{panel_w}" height="10" fill="{t["PANEL_BG"]}"/>')
    a(f'<line x1="0" y1="46" x2="{panel_w}" y2="46" stroke="{t["BORDER_LO"]}" stroke-width="0.8"/>')
    
    a(f'<circle cx="18" cy="23" r="4" fill="{t["ACCENT_2"]}"/>')
    a(f'<text x="29" y="28" font-size="14.5" font-weight="600" letter-spacing="0.5" fill="{t["TEXT_PRIMARY"]}">12-Month Commit Flow</text>')
    
    a(f'<rect x="{panel_w - 216}" y="9" width="114" height="28" rx="6" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="0.8"/>')
    a(f'<text x="{panel_w - 159}" y="27.5" font-size="12.5" font-weight="550" fill="{t["ACCENT_2"]}" text-anchor="middle">Peak: {peak_lbl}</text>')
    
    a(f'<rect x="{panel_w - 94}" y="9" width="80" height="28" rx="6" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="0.8"/>')
    a(f'<text x="{panel_w - 54}" y="27.5" font-size="12.5" font-weight="550" fill="{t["TEXT_PRIMARY"]}" text-anchor="middle">{avg_per_mo:.1f} / Mo</text>')
    
    # Plot canvas
    pad_l = 44
    pad_r = 20
    pad_t = 66
    pad_b = 40
    plot_w = panel_w - pad_l - pad_r
    plot_h = panel_h - pad_t - pad_b - 36
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
        a(f'<text x="{pad_l - 8}" y="{y_pos + 4.5:.1f}" font-size="12.5" font-weight="500" fill="{t["TEXT_MUTED"]}" text-anchor="end">{int(val)}</text>')
        
    pts_m = []
    n_pts_m = len(monthly)
    step_m = plot_w / max(1, n_pts_m - 1)
    for i, m in enumerate(monthly):
        px = pad_l + i * step_m
        cnt = m["count"]
        py = base_y - (cnt / y_max_nice) * plot_h
        py = min(base_y, max(pad_t, py))
        pts_m.append((px, py))
        
    line_m, area_m = generate_smooth_spline(pts_m, base_y)
    a(f'<path d="{area_m}" fill="url(#act_area_m)"/>')
    a(f'<path d="{line_m}" fill="none" stroke="{t["ACCENT_2"]}" stroke-width="4.5" opacity="0.4" filter="url(#act_glow)"/>')
    a(f'<path d="{line_m}" fill="none" stroke="url(#act_stroke_m)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    
    for i, (px, py) in enumerate(pts_m):
        m = monthly[i]
        is_peak = (m["count"] == peak_val and peak_val > 0)
        is_latest = (i == len(pts_m) - 1)
        
        node_r = 4.5 if (is_peak or is_latest) else 2.8
        node_fill = t["ACCENT_3"] if is_peak else (t["ACTIVE_GREEN"] if is_latest else t["ACCENT_2"])
        
        a(f'<g class="node-interactive">')
        # Invisible hit target
        a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="16" fill="transparent"/>')
        
        # Month X label
        a(f'<text x="{px:.1f}" y="{base_y + 24}" font-size="13.5" font-weight="550" fill="{t["ACCENT_2"] if is_latest or is_peak else t["TEXT_MUTED"]}" text-anchor="middle" class="tick-label">{m["label"]}</text>')
        
        if is_peak or is_latest:
            a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{node_r + 4}" fill="none" stroke="{node_fill}" stroke-width="1.2" opacity="0.6" class="pulse"/>')
            
        a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{node_r}" fill="{node_fill}" stroke="{t["PANEL_BG"]}" stroke-width="1.8" class="node-core"/>')
        
        # Interactive Tooltip on hover
        tt_y = py - 12 if py > 100 else py + 34
        a(f'<g class="tooltip-pop" transform="translate({px:.1f}, {tt_y:.1f})">')
        a(f'<rect x="-44" y="-28" width="88" height="26" rx="6" fill="#18120B" stroke="{node_fill}" stroke-width="1.2"/>')
        a(f'<text x="0" y="-15" font-size="10.5" font-weight="600" fill="#E2D5C5" text-anchor="middle">{m["label"]} {m.get("year", "")}</text>')
        a(f'<text x="0" y="-3" font-size="11.5" font-weight="700" fill="{node_fill}" text-anchor="middle">{m["count"]} commits</text>')
        a(f'</g>')
        
        a(f'</g>')
            
    # Bottom footer inside left panel
    a(f'<line x1="14" y1="{panel_h - 36}" x2="{panel_w - 14}" y2="{panel_h - 36}" stroke="{t["CARD_STROKE"]}" stroke-width="0.8"/>')
    a(f'<text x="18" y="{panel_h - 14}" font-size="13.5" font-weight="500" fill="{t["TEXT_MUTED"]}">Macro 12-Month Soundwave</text>')
    a(f'<text x="{panel_w - 18}" y="{panel_h - 14}" font-size="14.5" font-weight="600" fill="{t["ACCENT_2"]}" text-anchor="end">{past_yr_total:,} Total Commits</text>')
    
    a(f'</g>')
    
    # ═══════════════════════════════════════════════════════════════════
    #  RIGHT HALF: LAST 30 DAYS DAILY CADENCE & VELOCITY
    # ═══════════════════════════════════════════════════════════════════
    a(f'<g transform="translate(597, 14)" class="act-panel">')
    a(f'<rect width="{panel_w}" height="{panel_h}" rx="10" ry="10" fill="{t["CANVAS_BG"]}" stroke="{t["BORDER"]}" stroke-width="1.2"/>')
    
    # Header bar
    a(f'<rect width="{panel_w}" height="46" rx="10" fill="{t["PANEL_BG"]}" stroke="{t["BORDER_LO"]}" stroke-width="0.8"/>')
    a(f'<rect y="36" width="{panel_w}" height="10" fill="{t["PANEL_BG"]}"/>')
    a(f'<line x1="0" y1="46" x2="{panel_w}" y2="46" stroke="{t["BORDER_LO"]}" stroke-width="0.8"/>')
    
    a(f'<circle cx="18" cy="23" r="4" fill="{t["ACTIVE_GREEN"]}"/>')
    a(f'<text x="29" y="28" font-size="14.5" font-weight="600" letter-spacing="0.5" fill="{t["TEXT_PRIMARY"]}">Last 30 Days Cadence</text>')
    
    a(f'<rect x="{panel_w - 246}" y="9" width="124" height="28" rx="6" fill="{t["PILL_BG"]}" stroke="{t["BORDER"]}" stroke-width="0.8"/>')
    a(f'<text x="{panel_w - 184}" y="27.5" font-size="12.5" font-weight="550" fill="{t["ACCENT_2"]}" text-anchor="middle">Daily Avg: {last_30_avg:.1f}</text>')
    
    a(f'<rect x="{panel_w - 114}" y="9" width="100" height="28" rx="6" fill="{t["ACTIVE_BG"]}" stroke="{t["ACTIVE_BORDER"]}" stroke-width="0.8"/>')
    a(f'<circle cx="{panel_w - 101}" cy="23" r="3.5" fill="{t["ACTIVE_GREEN"]}" class="pulse"/>')
    a(f'<text x="{panel_w - 58}" y="27.5" font-size="12.5" font-weight="550" fill="{t["ACTIVE_GREEN"]}" text-anchor="middle">{last_30_act}/30 Active</text>')
    
    # Plot canvas
    max_d_cnt = max([d["count"] for d in last_30] + [5])
    if max_d_cnt <= 10:
        y_max_30 = 10
    elif max_d_cnt <= 20:
        y_max_30 = 20
    elif max_d_cnt <= 40:
        y_max_30 = 40
    else:
        y_max_30 = math.ceil(max_d_cnt / 10) * 10
        
    y_steps_30 = [0, y_max_30 * 0.33, y_max_30 * 0.66, y_max_30]
    for val in y_steps_30:
        y_pos = base_y - (val / y_max_30) * plot_h
        a(f'<line x1="{pad_l}" y1="{y_pos:.1f}" x2="{pad_l + plot_w}" y2="{y_pos:.1f}" stroke="{t["GRID_LINE"]}" stroke-width="0.8" stroke-dasharray="3,3"/>')
        a(f'<text x="{pad_l - 8}" y="{y_pos + 4.5:.1f}" font-size="12.5" font-weight="500" fill="{t["TEXT_MUTED"]}" text-anchor="end">{int(val)}</text>')
        
    pts_d = []
    n_pts_d = len(last_30)
    step_d = plot_w / max(1, n_pts_d - 1)
    
    tick_indices = [0, 6, 12, 18, 24, n_pts_d - 1] if n_pts_d >= 25 else list(range(0, n_pts_d, max(1, n_pts_d // 5)))
    
    for i, d in enumerate(last_30):
        px = pad_l + i * step_d
        cnt = d["count"]
        py = base_y - (cnt / y_max_30) * plot_h
        py = min(base_y, max(pad_t, py))
        pts_d.append((px, py))
        
    line_d, area_d = generate_smooth_spline(pts_d, base_y)
    a(f'<path d="{area_d}" fill="url(#act_area_d)"/>')
    a(f'<path d="{line_d}" fill="none" stroke="{t["ACTIVE_GREEN"]}" stroke-width="4.5" opacity="0.4" filter="url(#act_glow)"/>')
    a(f'<path d="{line_d}" fill="none" stroke="url(#act_stroke_d)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    
    for i, (px, py) in enumerate(pts_d):
        d = last_30[i]
        is_peak = (d["count"] == peak_30_val and peak_30_val > 0)
        is_latest = (i == n_pts_d - 1)
        
        tick_lbl = ""
        if i in tick_indices:
            try:
                dt_obj = datetime.strptime(d["date"], "%Y-%m-%d")
                tick_lbl = "Today" if is_latest else dt_obj.strftime("%b %d")
            except Exception:
                tick_lbl = d["date"][-5:]
                
        node_r = 4.2 if (is_peak or is_latest) else (2.6 if d["count"] > 0 else 1.8)
        node_fill = t["ACCENT_3"] if is_peak else (t["ACTIVE_GREEN"] if d["count"] > 0 else t["TEXT_DIM"])
        
        a(f'<g class="node-interactive">')
        # Invisible hit target
        a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="14" fill="transparent"/>')
        
        if tick_lbl:
            a(f'<text x="{px:.1f}" y="{base_y + 24}" font-size="13.5" font-weight="550" fill="{t["ACTIVE_GREEN"] if is_latest else t["TEXT_MUTED"]}" text-anchor="middle" class="tick-label">{tick_lbl}</text>')
            
        if is_peak or is_latest:
            a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{node_r + 3.5}" fill="none" stroke="{node_fill}" stroke-width="1.2" opacity="0.6" class="pulse"/>')
            
        a(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{node_r}" fill="{node_fill}" stroke="{t["PANEL_BG"]}" stroke-width="1.5" class="node-core"/>')
        
        # Interactive Tooltip on hover
        tt_y = py - 12 if py > 100 else py + 34
        d_date_str = d.get("date", "")
        try:
            d_date_fmt = datetime.strptime(d_date_str, "%Y-%m-%d").strftime("%b %d, %Y")
        except Exception:
            d_date_fmt = d_date_str
            
        a(f'<g class="tooltip-pop" transform="translate({px:.1f}, {tt_y:.1f})">')
        a(f'<rect x="-44" y="-28" width="88" height="26" rx="6" fill="#18120B" stroke="{node_fill}" stroke-width="1.2"/>')
        a(f'<text x="0" y="-15" font-size="10.5" font-weight="600" fill="#E2D5C5" text-anchor="middle">{d_date_fmt}</text>')
        a(f'<text x="0" y="-3" font-size="11.5" font-weight="700" fill="{node_fill}" text-anchor="middle">{d["count"]} commits</text>')
        a(f'</g>')
        
        a(f'</g>')
            
    # Bottom footer inside right panel
    a(f'<line x1="14" y1="{panel_h - 36}" x2="{panel_w - 14}" y2="{panel_h - 36}" stroke="{t["CARD_STROKE"]}" stroke-width="0.8"/>')
    a(f'<text x="18" y="{panel_h - 14}" font-size="13.5" font-weight="500" fill="{t["TEXT_MUTED"]}">Recent 30-Day Activity Flow</text>')
    a(f'<text x="{panel_w - 18}" y="{panel_h - 14}" font-size="14.5" font-weight="600" fill="{t["ACTIVE_GREEN"]}" text-anchor="end">{last_30_tot:,} Commits</text>')
    
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
