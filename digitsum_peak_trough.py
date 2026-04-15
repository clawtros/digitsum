"""Compare a peak-of-decade vs trough-of-decade image.
Decade 3: N=20 (trough, ratio 0.61) vs N=26 (peak, ratio 0.69).
Decade 2: N=11 (trough, 0.73) vs N=17 (peak, 0.81).
"""
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def ds(v):
    v = abs(v); s = 0
    while v: s += v % 10; v //= 10
    return s

def bfs_grid(N):
    # find axis bound
    bound = 10
    while True:
        hit = None
        for x in range(bound):
            if ds(x) > N: hit = x; break
        if hit is not None and hit < bound - 1:
            G = hit; break
        bound *= 10
    size = 2*G + 1
    visited = np.zeros((size, size), dtype=bool)
    ox, oy = G, G
    visited[oy, ox] = True
    q = deque([(0, 0)])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            gx, gy = ox+nx, oy+ny
            if gx < 0 or gx >= size or gy < 0 or gy >= size: continue
            if visited[gy, gx]: continue
            if ds(nx) + ds(ny) > N: continue
            visited[gy, gx] = True
            q.append((nx, ny))
    return visited

def render_tile(visited, target, color):
    """Render the visited grid into a target x target tile."""
    H, W = visited.shape
    # convert to RGB with given foreground color
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[visited] = color
    img = Image.fromarray(rgb, "RGB")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    # scale preserving aspect
    scale = min(target / W, target / H)
    newW = max(1, int(W * scale))
    newH = max(1, int(H * scale))
    pil = img.resize((newW, newH), Image.NEAREST)
    tile = Image.new("RGB", (target, target), (18, 18, 22))
    tile.paste(pil, ((target - newW)//2, (target - newH)//2))
    return tile

cases = [
    ("decade 2 trough", 11, (120, 200, 255)),
    ("decade 2 peak",   17, (120, 200, 255)),
    ("decade 3 trough", 20, (255, 180, 120)),
    ("decade 3 peak",   26, (255, 180, 120)),
]

TILE = 420
PAD = 16
GAP = 12
try:
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
    small = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
except Exception:
    font = small = ImageFont.load_default()

tiles = []
for label, N, color in cases:
    v = bfs_grid(N)
    tile = render_tile(v, TILE, color)
    # native axis reach
    G = (v.shape[0] - 1) // 2
    tiles.append((label, N, tile, G))
    print(f"{label} N={N}: bbox=±{G}, points={int(v.sum()):,}")

W = PAD*2 + len(tiles)*TILE + (len(tiles)-1)*GAP
H = PAD + TILE + 60
strip = Image.new("RGB", (W, H), (10, 10, 14))
d = ImageDraw.Draw(strip)
for i, (label, N, tile, G) in enumerate(tiles):
    x0 = PAD + i*(TILE + GAP)
    strip.paste(tile, (x0, PAD))
    d.text((x0 + 4, PAD + TILE + 4), f"{label}  N={N}", fill=(235,235,235), font=font)
    d.text((x0 + 4, PAD + TILE + 24), f"bbox ±{G}  (tiles rescaled to same size)", fill=(170,170,170), font=small)

strip.save("digitsum_peak_trough.png")
print("wrote digitsum_peak_trough.png")
