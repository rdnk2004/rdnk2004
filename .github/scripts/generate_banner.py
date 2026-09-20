#!/usr/bin/env python3
"""
generate_banner.py — The Director's Cut

Vintage-film-styled animated SVG visual map hero banner for rdnk2004.
Features:
  - 1-bit Floyd-Steinberg dithered dot-art portrait with 100% clean background isolation.
  - Animated 60-group random shimmer-in intro (0.2s - 3.2s) where dots form the user's face.
  - Seamless Face-to-Logo Morphing: Dots physically lift off the facial features
    (eyes, nose, cheeks, forehead) and fly across to assemble into:
      RDNK Emblem -> 35mm Cinema Camera -> Docker -> TensorFlow -> Reconstituting Face!
  - Ultra-precision contour arc-length + medial-axis skeleton sampling.
  - Fully responsive SYSTEM.INFO readout with textLength dotted leaders and vintage live pulse.
  - Celluloid 35mm film perforation accents & breathing warm amber perimeter glow.

Usage:
    python generate_banner.py

Outputs:
    assets/dark.svg, assets/light.svg
"""

import os, sys, math, html, random
import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance
import cv2
from scipy import ndimage
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR      = os.path.dirname(os.path.dirname(SCRIPT_DIR)) if os.path.basename(SCRIPT_DIR) == 'scripts' else SCRIPT_DIR
OUT_DIR       = os.path.join(ROOT_DIR, 'assets')

def _find_file(name):
    for candidate in [
        os.path.join(OUT_DIR, name),
        os.path.join(ROOT_DIR, name),
        os.path.join(ROOT_DIR, '..', name),
        os.path.join(SCRIPT_DIR, name),
    ]:
        if os.path.exists(candidate):
            return candidate
    return os.path.join(OUT_DIR, name)

PORTRAIT_PATH = _find_file('portrait.png')
ICON_PATH     = _find_file('icon.png')

W, H          = 1180, 610
FONT          = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# Layout
TITLE_H       = 46
MAP_X, MAP_Y  = 36, 84
MAP_W, MAP_H  = 400, 492

GRID_W        = 280                    # Portrait dot grid width (~280x300)
N_SHIMMER     = 60                     # Shimmer intro groups
N_TRAVELLER   = 850                    # Swarm traveller dots for logo morphing

INTRO_END     = 3.2                    # Shimmer intro finishes at 3.2s
LOOP_DUR      = 18.0                   # Morphing loop duration in seconds

# ═══════════════════════════════════════════════════════════════════
#  Vintage Film Color Themes
# ═══════════════════════════════════════════════════════════════════

THEMES = {
    "dark": dict(
        BG="#0D0A06",            # Burnt celluloid black
        PANEL_BG="#140F09",      # Deep warm dark chocolate
        PANEL_BAR="#100B06",     # Header bar
        PORT_DOT="#D4A353",      # Warm glowing gold/amber for lit subject
        TRAV_DOT="#F5E6D3",      # Cream white for morphing logo dots
        ACCENT_1="#C0713A",      # Burnt Sienna
        ACCENT_2="#D4A353",      # Warm Amber
        ACCENT_3="#F5E6D3",      # Warm Cream
        TITLE_TXT="#9C8B78",     # Muted parchment
        SECTION_TXT="#D4A353",   # Amber label
        PILL_BG="#3A2312",       # Deep amber-brown handle pill
        PILL_TXT="#F5E6D3",      # Cream handle text
        LABEL_COL="#D4A353",     # Amber row labels
        DOT_LEADER="rgba(212,163,83,0.30)", # Amber dotted leader
        VAL_COL="#F5E6D3",       # Cream white values
        SUB_TXT="#9C8B78",       # Muted subtitle
        LIVE_COL="#5B8C5A",      # Muted vintage emerald
        BORDER_STROKE="#C0713A", # Warm amber-sienna border
        BORDER_GLOW="rgba(212,163,83,0.45)",
        BARLINE="rgba(255,255,255,0.08)",
        WIN_C="#B85C38", WIN_M="#D4A353", WIN_X="#5B8C5A",
    ),
    "light": dict(
        BG="#FAF6F0",            # Vintage warm parchment
        PANEL_BG="#FFFFFF",      # Crisp parchment white
        PANEL_BAR="#F3ECE2",     # Header bar
        PORT_DOT="#5A3A1E",      # Deep sepia dark bronze for shadows
        TRAV_DOT="#3A2210",      # Rich dark sepia for logo dots
        ACCENT_1="#8B5A2B",      # Deep warm sienna
        ACCENT_2="#A67B3D",      # Antique gold
        ACCENT_3="#C89D66",      # Muted cream amber
        TITLE_TXT="#6B5D4F",     # Muted bronze
        SECTION_TXT="#8B5A2B",   # Deep sienna label
        PILL_BG="#EADBCA",       # Warm parchment handle pill
        PILL_TXT="#2C1810",      # Dark sepia handle text
        LABEL_COL="#8B5A2B",     # Sienna row labels
        DOT_LEADER="rgba(139,90,43,0.32)",  # Sienna dotted leader
        VAL_COL="#1A1207",       # Deep ink values
        SUB_TXT="#6B5D4F",       # Muted subtitle
        LIVE_COL="#3D6B3C",      # Vintage green
        BORDER_STROKE="#A67B3D", # Antique gold border
        BORDER_GLOW="rgba(166,123,61,0.35)",
        BARLINE="rgba(0,0,0,0.08)",
        WIN_C="#B85C38", WIN_M="#D4A353", WIN_X="#5B8C5A",
    ),
}

# ═══════════════════════════════════════════════════════════════════
#  Info Panel Content (Email strictly once, Core.Data has Chroma)
# ═══════════════════════════════════════════════════════════════════

INFO_ROWS = [
    ("Subject",          "Nikhil Krishna R D"),
    ("Role",             "ML/AI Engineer"),
    ("Origin",           "Coimbatore, Tamil Nadu"),
    ("Education",        "M.Sc. CS (Data Analytics)"),
    ("Status",           "Dev + Screenwriter + Mentor"),
    ("ToolChain",        "VS Code, Git, Docker, MLflow"),
    ("Core.Lang",        "Python, SQL, R"),
    ("Core.ML",          "sklearn, PyTorch, TF, XGBoost"),
    ("Core.Data",        "Postgres, Mongo, Chroma"),
    ("Core.Infra",       "Docker, GH Actions, MLflow"),
    None,                # Section divider: - Contact -----------------
    ("Grid.Mail",        "rdnikhilkrishna2004@gmail.com"),
    ("Grid.Portfolio",   "rdnkportfolio.vercel.app"),
    ("Grid.LinkedIn",    "nikhil-krishna-r-d-773b84259"),
    ("Grid.GitHub",      "rdnk2004"),
    ("Grid.HuggingFace", "rdnk-2004"),
]

def esc(s):
    return html.escape(str(s), quote=True)

# ═══════════════════════════════════════════════════════════════════
#  1. Portrait Processing & Background Isolation
# ═══════════════════════════════════════════════════════════════════

def get_clean_subject_mask(img_rgba):
    """Segment subject using alpha channel with morphological closing and hole filling."""
    if img_rgba.mode == 'RGBA':
        alpha = np.array(img_rgba.split()[3])
        mask = alpha > 40
    else:
        arr = np.array(img_rgba.convert('RGB'))
        mask = ~np.all(arr > 230, axis=2)
        
    mask = ndimage.binary_closing(mask, structure=np.ones((5, 5)))
    mask = ndimage.binary_fill_holes(mask)
    
    labeled, num_features = ndimage.label(mask)
    if num_features > 0:
        sizes = ndimage.sum(mask, labeled, range(num_features + 1))
        largest_label = np.argmax(sizes[1:]) + 1
        mask = (labeled == largest_label)
    return mask


def process_portrait(path, grid_w):
    """Load portrait, crop head-and-shoulders, enhance, and segment subject."""
    img = Image.open(path)
    w, h = img.size
    
    crop_box = (int(w * 0.04), int(h * 0.06), int(w * 0.96), int(h * 0.80))
    cropped = img.crop(crop_box)
    
    cw, ch = cropped.size
    grid_h = int(grid_w * ch / cw)
    resized = cropped.resize((grid_w, grid_h), Image.LANCZOS)
    
    clean_mask = get_clean_subject_mask(resized)
    
    rgb = resized.convert('RGB')
    gray = ImageOps.grayscale(rgb)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=140))
    enhancer = ImageEnhance.Contrast(gray)
    gray_enhanced = enhancer.enhance(1.35)
    
    gray_arr = np.array(gray_enhanced, dtype=np.float64)
    return gray_arr, clean_mask, grid_w, grid_h


def serpentine_dither(gray_arr, mask, dark_mode=True):
    """Serpentine Floyd-Steinberg 1-bit error-diffusion dithering with zero background bleed."""
    h, w = gray_arr.shape
    if dark_mode:
        buf = gray_arr.copy()
        buf[~mask] = 0.0
    else:
        m_vals = gray_arr[mask]
        min_v, max_v = m_vals.min(), m_vals.max()
        scaled = (gray_arr - min_v) / (max_v - min_v + 1e-5) * 255.0
        buf = (255.0 - scaled).copy()
        buf[~mask] = 0.0
        
    dots = []
    for y in range(h):
        is_even = (y % 2 == 0)
        x_range = range(w) if is_even else range(w - 1, -1, -1)
        for x in x_range:
            if not mask[y, x]:
                buf[y, x] = 0.0
                continue
            old = max(0.0, min(255.0, buf[y, x]))
            new = 255.0 if old > 128.0 else 0.0
            if new > 0:
                dots.append((x, y))
            err = old - new
            if is_even:
                if x + 1 < w and mask[y, x + 1]:
                    buf[y, x + 1] += err * 7 / 16
                if y + 1 < h:
                    if x > 0 and mask[y + 1, x - 1]:
                        buf[y + 1, x - 1] += err * 3 / 16
                    if mask[y + 1, x]:
                        buf[y + 1, x] += err * 5 / 16
                    if x + 1 < w and mask[y + 1, x + 1]:
                        buf[y + 1, x + 1] += err * 1 / 16
            else:
                if x > 0 and mask[y, x - 1]:
                    buf[y, x - 1] += err * 7 / 16
                if y + 1 < h:
                    if x + 1 < w and mask[y + 1, x + 1]:
                        buf[y + 1, x + 1] += err * 3 / 16
                    if mask[y + 1, x]:
                        buf[y + 1, x] += err * 5 / 16
                    if x > 0 and mask[y + 1, x - 1]:
                        buf[y + 1, x - 1] += err * 1 / 16
    return dots


def dots_to_rle_paths(dots, n_groups=N_SHIMMER, seed=42):
    """Split dots randomly into n_groups interleaved groups across the portrait for shimmer intro."""
    rng = random.Random(seed)
    shuffled = dots[:]
    rng.shuffle(shuffled)
    
    groups = [[] for _ in range(n_groups)]
    for i, pt in enumerate(shuffled):
        groups[i % n_groups].append(pt)
        
    path_strings = []
    for g in groups:
        g.sort(key=lambda p: (p[1], p[0]))
        d_chunks = []
        i = 0
        while i < len(g):
            x0, y0 = g[i]
            run = 1
            while (i + run < len(g) and g[i + run][1] == y0 and g[i + run][0] == x0 + run):
                run += 1
            d_chunks.append(f"M{x0} {y0}h{run}v1h-{run}z")
            i += run
        path_strings.append("".join(d_chunks))
        
    # Full portrait path for static duplicate layer
    full_sorted = sorted(dots, key=lambda p: (p[1], p[0]))
    full_chunks = []
    i = 0
    while i < len(full_sorted):
        x0, y0 = full_sorted[i]
        run = 1
        while (i + run < len(full_sorted) and full_sorted[i + run][1] == y0 and full_sorted[i + run][0] == x0 + run):
            run += 1
        full_chunks.append(f"M{x0} {y0}h{run}v1h-{run}z")
        i += run
    full_path = "".join(full_chunks)
    
    return path_strings, full_path

# ═══════════════════════════════════════════════════════════════════
#  2. Multi-Tier Contour + Medial-Axis Skeleton Logo Sampler
# ═══════════════════════════════════════════════════════════════════

def sample_bitmap_ultra_crisp(binary_img, n_dots=N_TRAVELLER, res=1024, seed=42):
    """
    Sample dots using 3 synergistic tiers:
      1. Contour Arc-Length Allocation: Crisp connected boundary lines
      2. Medial-Axis Skeleton Thinning: Centerline spine along strokes/curves
      3. Distance Transform Core Fill: Uniform inner body density
    """
    # 1. Contours
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    total_len = sum(cv2.arcLength(cnt, True) for cnt in contours)
    
    n_contour_dots = int(n_dots * 0.58)
    contour_pts = []
    for cnt in contours:
        cnt_len = cv2.arcLength(cnt, True)
        if cnt_len < 10:
            continue
        n_p = max(4, int(n_contour_dots * (cnt_len / total_len)))
        pts = cnt.reshape(-1, 2)
        dists = np.sqrt(np.sum(np.diff(pts, axis=0, prepend=[pts[-1]])**2, axis=1))
        cum = np.cumsum(dists)
        tot = cum[-1]
        if tot <= 0:
            continue
        targets = np.linspace(0, tot, n_p, endpoint=False)
        for t in targets:
            idx = min(np.searchsorted(cum, t), len(pts)-1)
            contour_pts.append(pts[idx])
            
    # 2. Skeleton Thinning
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    thin = binary_img.copy()
    skel = np.zeros(binary_img.shape, np.uint8)
    while True:
        eroded = cv2.erode(thin, kernel)
        temp = cv2.dilate(eroded, kernel)
        temp = cv2.subtract(thin, temp)
        skel = cv2.bitwise_or(skel, temp)
        thin = eroded.copy()
        if cv2.countNonZero(thin) == 0:
            break
            
    sy, sx = np.where(skel > 0)
    n_skel = int(n_dots * 0.28)
    skel_pts = []
    if len(sx) > 0:
        rng = np.random.default_rng(seed)
        idx_skel = rng.choice(len(sx), size=min(n_skel, len(sx)), replace=False)
        for idx in idx_skel:
            skel_pts.append([sx[idx], sy[idx]])
            
    # 3. Core Fill
    dt = cv2.distanceTransform(binary_img, cv2.DIST_L2, 5)
    dy, dx = np.where(dt > 4)
    n_fill = n_dots - len(contour_pts) - len(skel_pts)
    fill_pts = []
    if n_fill > 0 and len(dx) > 0:
        w = dt[dy, dx]
        w = w / w.sum()
        rng = np.random.default_rng(seed + 1)
        idx_fill = rng.choice(len(dx), size=n_fill, replace=False, p=w)
        for idx in idx_fill:
            fill_pts.append([dx[idx], dy[idx]])
            
    all_pts = contour_pts + skel_pts + fill_pts
    return np.array(all_pts[:n_dots]) / res


def draw_cinema_camera(res=1000):
    """Draw classic 35mm cinema camera with dual top reels, body, lens cone, and tripod."""
    img = Image.new('L', (res, res), 0)
    d = ImageDraw.Draw(img)
    u = res / 24.0
    
    # Dual Top Reels
    d.ellipse([5.5*u, 2.5*u, 11.5*u, 8.5*u], fill=255)
    d.ellipse([10.5*u, 2.5*u, 16.5*u, 8.5*u], fill=255)
    d.ellipse([7.5*u, 4.5*u, 9.5*u, 6.5*u], fill=0)
    d.ellipse([12.5*u, 4.5*u, 14.5*u, 6.5*u], fill=0)
    
    # Camera Body
    d.rounded_rectangle([4.5*u, 8.0*u, 15.5*u, 17.5*u], radius=int(1.2*u), fill=255)
    d.ellipse([8.5*u, 11.0*u, 11.5*u, 14.0*u], fill=0)
    d.ellipse([9.2*u, 11.7*u, 10.8*u, 13.3*u], fill=255)
    
    # Eyepiece Viewfinder (Left)
    d.rounded_rectangle([2.0*u, 8.8*u, 4.5*u, 11.2*u], radius=int(0.6*u), fill=255)
    d.polygon([(2.0*u, 8.8*u), (0.8*u, 7.8*u), (0.8*u, 12.2*u), (2.0*u, 11.2*u)], fill=255)
    
    # Lens & Matte Box (Right)
    d.rectangle([15.5*u, 10.5*u, 17.5*u, 15.0*u], fill=255)
    d.polygon([(17.5*u, 10.0*u), (22.5*u, 6.8*u), (22.5*u, 18.2*u), (17.5*u, 15.5*u)], fill=255)
    d.ellipse([21.8*u, 10.2*u, 23.0*u, 14.8*u], fill=0)
    
    # Tripod Base
    d.rectangle([9.0*u, 17.5*u, 11.0*u, 19.5*u], fill=255)
    d.polygon([(8.5*u, 19.5*u), (4.5*u, 23.5*u), (6.0*u, 23.5*u), (9.5*u, 19.5*u)], fill=255)
    d.polygon([(10.5*u, 19.5*u), (14.0*u, 23.5*u), (15.5*u, 23.5*u), (11.5*u, 19.5*u)], fill=255)
    d.polygon([(9.3*u, 19.5*u), (9.3*u, 23.5*u), (10.7*u, 23.5*u), (10.7*u, 19.5*u)], fill=255)
    
    return np.array(img)


def get_perfect_logo_dots(n_dots=N_TRAVELLER, grid_w=GRID_W, grid_h=300):
    """Generate high-precision dot clouds for the 4 morphing shapes: RDNK, Cinema Camera, Docker, TensorFlow."""
    logos = {}
    cx, cy = grid_w / 2.0, grid_h / 2.0 - 2.0
    r_target = 95.0
    res = 1000
    u = res / 24.0

    # 1. RDNK ICON
    try:
        icon = Image.open(ICON_PATH).convert('RGBA')
        bbox = icon.getbbox()
        cropped = icon.crop(bbox)
        resized_icon = cropped.resize((res, res), Image.LANCZOS)
        alpha = np.array(resized_icon.split()[3])
        _, rdnk_bin = cv2.threshold(alpha, 80, 255, cv2.THRESH_BINARY)
        raw_pts = sample_bitmap_ultra_crisp(rdnk_bin, n_dots, res, 42)
        logos['rdnk'] = [(cx + (x - 0.5) * r_target * 2.15, cy + (y - 0.5) * r_target * 2.15) for x, y in raw_pts]
    except Exception as e:
        print(f"  [!] Fallback for icon: {e}")
        rng = random.Random(42)
        logos['rdnk'] = [(cx + rng.uniform(-60, 60), cy + rng.uniform(-60, 60)) for _ in range(n_dots)]

    # 2. 35MM CINEMA CAMERA LOGO
    cam_bin = draw_cinema_camera(res)
    raw_cam = sample_bitmap_ultra_crisp(cam_bin, n_dots, res, 77)
    logos['camera'] = [(cx + (x - 0.5) * r_target * 2.10, cy + (y - 0.5) * r_target * 2.10) for x, y in raw_cam]

    # 3. DOCKER LOGO (Whale + Container Grid + Spout)
    dk_img = Image.new('L', (res, res), 0)
    d = ImageDraw.Draw(dk_img)
    box_w = 1.75 * u
    box_gap = 0.45 * u
    start_x = 5.0 * u
    start_y = 12.0 * u
    for c in range(4):
        bx = start_x + c * (box_w + box_gap)
        by = start_y - box_w
        d.rectangle([bx, by, bx + box_w, by + box_w], fill=255)
    for c in range(3):
        bx = start_x + (c + 1) * (box_w + box_gap)
        by = start_y - 2 * (box_w + box_gap)
        d.rectangle([bx, by, bx + box_w, by + box_w], fill=255)
    for c in range(2):
        bx = start_x + (c + 1) * (box_w + box_gap)
        by = start_y - 3 * (box_w + box_gap)
        d.rectangle([bx, by, bx + box_w, by + box_w], fill=255)
    d.pieslice([0.5*u, 8.0*u, 20.5*u, 21.0*u], 0, 180, fill=255)
    d.rectangle([0.5*u, 12.0*u, 18.5*u, 14.5*u], fill=255)
    d.pieslice([0.0*u, 11.5*u, 5.5*u, 17.0*u], 90, 270, fill=255)
    d.polygon([(18.0*u, 12.5*u), (23.0*u, 7.5*u), (21.2*u, 14.5*u)], fill=255)
    d.polygon([(23.0*u, 7.5*u), (23.5*u, 10.5*u), (21.2*u, 14.5*u)], fill=255)
    d.ellipse([2.6*u, 13.0*u, 3.8*u, 14.2*u], fill=0)
    d.ellipse([20.0*u, 4.0*u, 21.4*u, 5.4*u], fill=255)
    d.ellipse([21.8*u, 2.6*u, 23.2*u, 4.0*u], fill=255)
    dk_bin = np.array(dk_img)
    raw_dk = sample_bitmap_ultra_crisp(dk_bin, n_dots, res, 44)
    logos['docker'] = [(cx + (x - 0.5) * r_target * 2.05, cy + (y - 0.5) * r_target * 2.05) for x, y in raw_dk]

    # 4. TENSORFLOW LOGO (Official 3D isometric faceted T)
    tf_img = Image.new('L', (res, res), 0)
    d = ImageDraw.Draw(tf_img)
    p_l = [
        (1.292*u, 5.856*u), (11.54*u, 0.0*u), (11.54*u, 24.0*u),
        ((11.54 - 4.095)*u, (24.0 - 2.378)*u), (7.445*u, 7.603*u),
        ((7.445 - 6.168)*u, (7.603 + 3.564)*u)
    ]
    d.polygon(p_l, fill=255)
    p_r = [
        (22.708*u, 5.857*u), (12.46*u, 0.0*u), (12.46*u, 24.0*u),
        ((12.46 + 4.095)*u, (24.0 - 2.378)*u), (16.555*u, 7.603*u),
        ((16.555 + 6.168)*u, (7.603 + 3.564)*u)
    ]
    d.polygon(p_r, fill=255)
    d.line([(7.445*u, 7.603*u), (11.54*u, 0.0*u)], fill=0, width=int(0.6*u))
    d.line([(16.555*u, 7.603*u), (12.46*u, 0.0*u)], fill=0, width=int(0.6*u))
    d.line([(7.445*u, 7.603*u), (7.445*u, (24.0 - 2.378)*u)], fill=0, width=int(0.6*u))
    d.line([(16.555*u, 7.603*u), (16.555*u, (24.0 - 2.378)*u)], fill=0, width=int(0.6*u))
    tf_bin = np.array(tf_img)
    raw_tf = sample_bitmap_ultra_crisp(tf_bin, n_dots, res, 45)
    logos['tensorflow'] = [(cx + (x - 0.5) * r_target * 1.95, cy + (y - 0.5) * r_target * 1.95) for x, y in raw_tf]

    return logos


def sample_face_dots(portrait_dots, n_target, seed=777):
    """Sample N_TRAVELLER dots directly from the user's face/portrait dot distribution."""
    rng = random.Random(seed)
    shuffled = portrait_dots[:]
    rng.shuffle(shuffled)
    if len(shuffled) >= n_target:
        return [(float(x), float(y)) for x, y in shuffled[:n_target]]
    else:
        res = [(float(x), float(y)) for x, y in shuffled]
        while len(res) < n_target:
            p = res[rng.randint(0, len(res) - 1)]
            res.append((p[0] + rng.gauss(0, 0.4), p[1] + rng.gauss(0, 0.4)))
        return res


def solve_optimal_transport(pts_from, pts_to):
    """Compute optimal transport assignment via linear sum assignment on Euclidean distance."""
    cost_matrix = cdist(pts_from, pts_to)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    reordered_to = [pts_to[j] for j in col_ind]
    return reordered_to


def generate_face_to_logo_trajectories(portrait_dots, grid_w, grid_h):
    """
    Generate seamless morphing trajectory:
    Face -> RDNK -> Cinema Camera -> Docker -> TensorFlow -> Back to Face!
    """
    logo_dots = get_perfect_logo_dots(N_TRAVELLER, grid_w, grid_h)
    
    # Start directly on the user's facial dots
    pts_face = sample_face_dots(portrait_dots, N_TRAVELLER)
    
    matched = {'face': pts_face}
    matched['rdnk']       = solve_optimal_transport(matched['face'], logo_dots['rdnk'])
    matched['camera']     = solve_optimal_transport(matched['rdnk'], logo_dots['camera'])
    matched['docker']     = solve_optimal_transport(matched['camera'], logo_dots['docker'])
    matched['tensorflow'] = solve_optimal_transport(matched['docker'], logo_dots['tensorflow'])
    
    return matched

# ═══════════════════════════════════════════════════════════════════
#  3. SVG Generation Pipeline
# ═══════════════════════════════════════════════════════════════════

def build_defs(t, theme_id):
    return f"""<defs>
<linearGradient id="{theme_id}_acc" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t['ACCENT_1']}"><animate attributeName="stop-color" values="{t['ACCENT_1']};{t['ACCENT_2']};{t['ACCENT_3']};{t['ACCENT_1']}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="0.5" stop-color="{t['ACCENT_2']}"><animate attributeName="stop-color" values="{t['ACCENT_2']};{t['ACCENT_3']};{t['ACCENT_1']};{t['ACCENT_2']}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="1" stop-color="{t['ACCENT_3']}"><animate attributeName="stop-color" values="{t['ACCENT_3']};{t['ACCENT_1']};{t['ACCENT_2']}" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="{theme_id}_panelGrad" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{t['BG']}"/>
  <stop offset="1" stop-color="{t['PANEL_BG']}"/>
</linearGradient>
<filter id="{theme_id}_glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="{theme_id}_glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="{theme_id}_txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="{theme_id}_winClip"><rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18"/></clipPath>
<path id="tv_{theme_id}" d="M0 0h2.2v2.2h-2.2z" fill="{t['TRAV_DOT']}"/>
</defs>"""


def build_chrome(t, theme_id):
    lines = []
    a = lines.append
    
    # Outer frame
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="{t["BG"]}"/>')
    a(f'<g clip-path="url(#{theme_id}_winClip)">')
    a(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" fill="url(#{theme_id}_panelGrad)"/>')
    
    # Title bar
    a(f'<rect x="2" y="2" width="{W-4}" height="{TITLE_H}" fill="{t["PANEL_BAR"]}"/>')
    a(f'<line x1="2" y1="{TITLE_H+2}" x2="{W-2}" y2="{TITLE_H+2}" stroke="{t["BARLINE"]}"/>')
    
    # Traffic lights themed to vintage tones
    cy = TITLE_H // 2 + 2
    a(f'<circle cx="30" cy="{cy}" r="5.5" fill="{t["WIN_C"]}"/>')
    a(f'<circle cx="50" cy="{cy}" r="5.5" fill="{t["WIN_M"]}"/>')
    a(f'<circle cx="70" cy="{cy}" r="5.5" fill="{t["WIN_X"]}"/>')
    
    # Header title
    a(f'<text x="{W//2}" y="{cy+4}" text-anchor="middle" font-size="12" fill="{t["TITLE_TXT"]}">'
      f'rdnk2004 — % ./director.sh --live</text>')
    
    # VISUAL.MAP Frame & Accents
    a(f'<text x="{MAP_X+2}" y="{MAP_Y-10}" font-size="10" letter-spacing="3" fill="{t["TITLE_TXT"]}">VISUAL.MAP</text>')
    a(f'<rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" rx="10" '
      f'fill="none" stroke="{t["BORDER_STROKE"]}" stroke-width="2" opacity="0.45" filter="url(#{theme_id}_glow3)"/>')
    a(f'<rect x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" rx="10" '
      f'fill="{t["BG"]}" stroke="{t["BORDER_GLOW"]}"/>')
    
    # Corner brackets on portrait panel
    a(f'<path d="M 50 {MAP_Y} L {MAP_X} {MAP_Y} L {MAP_X} {MAP_Y+14}" fill="none" stroke="{t["ACCENT_2"]}" stroke-width="2" opacity="0.85"/>')
    a(f'<path d="M {MAP_X+MAP_W-14} {MAP_Y} L {MAP_X+MAP_W} {MAP_Y} L {MAP_X+MAP_W} {MAP_Y+14}" fill="none" stroke="{t["ACCENT_2"]}" stroke-width="2" opacity="0.85"/>')
    a(f'<path d="M 50 {MAP_Y+MAP_H} L {MAP_X} {MAP_Y+MAP_H} L {MAP_X} {MAP_Y+MAP_H-14}" fill="none" stroke="{t["ACCENT_2"]}" stroke-width="2" opacity="0.85"/>')
    a(f'<path d="M {MAP_X+MAP_W-14} {MAP_Y+MAP_H} L {MAP_X+MAP_W} {MAP_Y+MAP_H} L {MAP_X+MAP_W} {MAP_Y+MAP_H-14}" fill="none" stroke="{t["ACCENT_2"]}" stroke-width="2" opacity="0.85"/>')
    
    # Film-strip perforation accents along the bottom edge
    for x in range(26, W - 26, 28):
        a(f'<rect x="{x}" y="{H-18}" width="8" height="8" rx="2" '
          f'fill="none" stroke="{t["ACCENT_2"]}" stroke-width="0.7" opacity="0.22"/>')
          
    return "\n".join(lines)


def build_portrait_svg(shimmer_paths, full_path, gw, gh, t, theme_id):
    """Build the two-layer portrait: 60-group shimmer intro + loop-faded static duplicate layer."""
    lines = []
    a = lines.append
    
    pad_x, pad_y = 12, 12
    avail_w = MAP_W - 2 * pad_x
    avail_h = MAP_H - 2 * pad_y
    sc = min(avail_w / gw, avail_h / gh)
    trans_x = MAP_X + pad_x + (avail_w - gw * sc) / 2
    trans_y = MAP_Y + pad_y + (avail_h - gh * sc) / 2
    
    # Layer 1: Shimmer-in intro (0.2s - 3.2s, once)
    a(f'<g transform="translate({trans_x:.1f},{trans_y:.1f}) scale({sc:.4f})" '
      f'fill="{t["PORT_DOT"]}" shape-rendering="crispEdges">')
    a(f'<set attributeName="opacity" to="0" begin="{INTRO_END}s"/>')
    
    for i, pth in enumerate(shimmer_paths):
        begin_t = 0.20 + i * (1.90 / N_SHIMMER)
        a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.9s" '
          f'begin="{begin_t:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>'
          f'<path d="{pth}"/></g>')
    a('</g>')
    
    # Layer 2: Static duplicate layer (active after 3.2s)
    # Timing matches 4-logo cycle: Face -> RDNK -> Cinema Camera -> Docker -> TensorFlow -> Face
    port_kt = "0.000;0.139;0.206;0.344;0.411;0.550;0.617;0.756;0.822;0.944;0.989;1.000"
    port_op = "1;1;0;0;0;0;0;0;0;0;0;1"
    
    a(f'<g transform="translate({trans_x:.1f},{trans_y:.1f}) scale({sc:.4f})" '
      f'fill="{t["PORT_DOT"]}" shape-rendering="crispEdges" opacity="0">')
    a(f'<set attributeName="opacity" to="1" begin="{INTRO_END}s"/>')
    a(f'<g opacity="1">'
      f'<animate attributeName="opacity" values="{port_op}" keyTimes="{port_kt}" '
      f'dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite"/>'
      f'<path d="{full_path}"/>'
      f'</g>')
    a('</g>')
    
    return "\n".join(lines), sc, trans_x, trans_y


def build_travellers_svg(matched, sc, trans_x, trans_y, t, theme_id):
    """
    Build the 850 traveller dots morphing:
    Face -> RDNK -> Cinema Camera -> Docker -> TensorFlow -> Reconstitute Face!
    """
    lines = []
    a = lines.append
    
    key_times = "0.000;0.139;0.206;0.344;0.411;0.550;0.617;0.756;0.822;0.944;0.989;1.000"
    op_values = "0;0;1;1;1;1;1;1;1;1;1;0"
    
    a(f'<g transform="translate({trans_x:.1f},{trans_y:.1f}) scale({sc:.4f})">')
    
    for i in range(N_TRAVELLER):
        fc  = matched['face'][i]
        rk  = matched['rdnk'][i]
        cam = matched['camera'][i]
        dk  = matched['docker'][i]
        tf  = matched['tensorflow'][i]
        
        trans_vals = (f"{fc[0]:.1f} {fc[1]:.1f};"
                      f"{fc[0]:.1f} {fc[1]:.1f};"
                      f"{rk[0]:.1f} {rk[1]:.1f};"
                      f"{rk[0]:.1f} {rk[1]:.1f};"
                      f"{cam[0]:.1f} {cam[1]:.1f};"
                      f"{cam[0]:.1f} {cam[1]:.1f};"
                      f"{dk[0]:.1f} {dk[1]:.1f};"
                      f"{dk[0]:.1f} {dk[1]:.1f};"
                      f"{tf[0]:.1f} {tf[1]:.1f};"
                      f"{tf[0]:.1f} {tf[1]:.1f};"
                      f"{fc[0]:.1f} {fc[1]:.1f};"
                      f"{fc[0]:.1f} {fc[1]:.1f}")
        
        a(f'<use href="#tv_{theme_id}" opacity="0">'
          f'<animate attributeName="opacity" values="{op_values}" keyTimes="{key_times}" '
          f'dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite"/>'
          f'<animateTransform attributeName="transform" type="translate" values="{trans_vals}" '
          f'keyTimes="{key_times}" dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite"/>'
          f'</use>')
          
    a('</g>')
    return "\n".join(lines)


def build_info_panel(t, theme_id):
    """Build right-side SYSTEM.INFO readout with animated slide-in, handle pill, and textLength dotted leaders."""
    lines = []
    a = lines.append
    
    x0 = 470
    rw = 655
    
    # SYSTEM.INFO Header + Divider + LIVE Badge
    a(f'<text x="{x0}" y="106" font-size="13" letter-spacing="2" fill="{t["SECTION_TXT"]}" filter="url(#{theme_id}_txtGlow)">SYSTEM.INFO</text>')
    a(f'<line x1="575" y1="102" x2="1061" y2="102" stroke="{t["BARLINE"]}"/>')
    a(f'<text x="1125" y="106" text-anchor="end" font-size="12" fill="{t["LIVE_COL"]}" font-weight="700">'
      f'<tspan>&#9679;</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>')
    
    # Handle pill
    a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>'
      f'<rect x="{x0}" y="122" width="130" height="20" rx="4" fill="{t["PILL_BG"]}"/>'
      f'<text x="{x0+12}" y="136" font-size="13" font-weight="700" fill="{t["PILL_TXT"]}">@rdnk2004</text>'
      f'<line x1="{x0+145}" y1="130" x2="1125" y2="130" stroke="{t["BARLINE"]}"/>'
      f'</g>')
    
    # Info Rows
    y = 162
    stagger = 0.90
    cw = 8.5
    max_chars = int(rw / cw)
    
    for row in INFO_ROWS:
        if row is None:
            a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{stagger:.2f}s" fill="freeze"/>'
              f'<text x="{x0}" y="{y}" font-size="14" textLength="{rw}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
              f'<tspan fill="{t["SUB_TXT"]}">- Contact </tspan>'
              f'<tspan fill="{t["DOT_LEADER"]}">---------------------------------------------------------------------</tspan>'
              f'</text></g>')
            y += 23
            stagger += 0.10
            continue
            
        label, value = row
        dots_count = max(4, max_chars - len(label) - len(value) - 2)
        dots_str = "." * dots_count
        
        a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{stagger:.2f}s" fill="freeze"/>'
          f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{stagger:.2f}s" fill="freeze"/>'
          f'<text x="{x0}" y="{y}" font-size="14" textLength="{rw}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
          f'<tspan fill="{t["LABEL_COL"]}">{esc(label)} </tspan>'
          f'<tspan fill="{t["DOT_LEADER"]}">{dots_str}</tspan>'
          f'<tspan fill="{t["VAL_COL"]}" font-weight="600"> {esc(value)}</tspan>'
          f'</text></g>')
        
        y += 23
        stagger += 0.10
        
    # Footer prompt
    a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{stagger+0.2:.2f}s" fill="freeze"/>'
      f'<text x="{x0}" y="572" font-size="14" fill="{t["SUB_TXT"]}">'
      f'&#9656; More about me &amp; projects below in README &#8595; '
      f'<tspan fill="{t["LABEL_COL"]}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan>'
      f'</text></g>')
      
    return "\n".join(lines)


def assemble_svg(shimmer_paths, full_path, gw, gh, matched, theme):
    """Assemble the complete animated SVG for a specific color theme."""
    t = THEMES[theme]
    tid = theme
    parts = []
    a = parts.append
    
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="{FONT}" role="img" aria-label="Nikhil Krishna R D — Director Cut Visual Map">')
    
    a(build_defs(t, tid))
    a(build_chrome(t, tid))
    
    port_svg, sc, tx, ty = build_portrait_svg(shimmer_paths, full_path, gw, gh, t, tid)
    a(port_svg)
    
    trav_svg = build_travellers_svg(matched, sc, tx, ty, t, tid)
    a(trav_svg)
    
    a(build_info_panel(t, tid))
    
    a('</g>')
    
    # Glowing animated perimeter frame
    a(f'<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="17" '
      f'fill="none" stroke="url(#{tid}_acc)" stroke-width="3" opacity="0.55" filter="url(#{tid}_glow8)"/>')
    a(f'<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="17" '
      f'fill="none" stroke="url(#{tid}_acc)" stroke-width="1.6"/>')
    
    a('</svg>')
    return "\n".join(parts)

# ═══════════════════════════════════════════════════════════════════
#  Main Pipeline
# ═══════════════════════════════════════════════════════════════════

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=" * 60)
    print("  The Director's Cut  —  Vintage Film Visual Map Generator")
    print("=" * 60, "\n")
    
    if not os.path.isfile(PORTRAIT_PATH):
        print(f"[!] ERROR: Portrait file not found at: {PORTRAIT_PATH}")
        sys.exit(1)
        
    print("[1/4] Processing portrait image & subject segmentation (zero background bleed)...")
    gray_arr, mask, gw, gh = process_portrait(PORTRAIT_PATH, GRID_W)
    print(f"      Grid resolution: {gw} x {gh}")
    
    print("[2/4] Dithering portrait (serpentine Floyd-Steinberg)...")
    dark_dots = serpentine_dither(gray_arr, mask, dark_mode=True)
    light_dots = serpentine_dither(gray_arr, mask, dark_mode=False)
    print(f"      Dark mode dot count : {len(dark_dots)}")
    print(f"      Light mode dot count: {len(light_dots)}")
    
    dark_shimmer, dark_full = dots_to_rle_paths(dark_dots, N_SHIMMER)
    light_shimmer, light_full = dots_to_rle_paths(light_dots, N_SHIMMER)
    
    print("[3/4] Generating Face-to-Logo morphing trajectories (RDNK -> Camera -> Docker -> TensorFlow -> Face)...")
    matched_dark = generate_face_to_logo_trajectories(dark_dots, gw, gh)
    matched_light = generate_face_to_logo_trajectories(light_dots, gw, gh)
    print(f"      Mapped {N_TRAVELLER} facial dots -> RDNK -> Cinema Camera -> Docker -> TensorFlow -> Face!")
    
    print("[4/4] Assembling animated SVGs with vintage film palette...")
    for theme, shimmer_paths, full_path, matched in [
        ("dark", dark_shimmer, dark_full, matched_dark)
    ]:
        svg_content = assemble_svg(shimmer_paths, full_path, gw, gh, matched, theme)
        out_file = os.path.join(OUT_DIR, f"{theme}.svg")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        size_kb = os.path.getsize(out_file) / 1024.0
        print(f"      [OK] {theme}.svg generated ({size_kb:.1f} KB) -> {out_file}")
        
    print("\n" + "=" * 60)
    print("  Generation complete! dark.svg and light.svg are ready.")
    print("=" * 60)

if __name__ == '__main__':
    main()
