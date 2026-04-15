"""Render reachable-region images for multiple bases, sized so the
bounding boxes are comparable (~300 per axis)."""

from collections import deque
import numpy as np
from PIL import Image

# (base, N) pairs chosen so max axis reach ~ 250-300
CASES = [(2, 8), (3, 10), (4, 12), (5, 14), (10, 19)]

def ds(v, b):
    v = abs(v)
    s = 0
    while v:
        s += v % b
        v //= b
    return s

def bfs(base, N):
    seen = {(0, 0)}
    q = deque([(0, 0)])
    xmin = xmax = ymin = ymax = 0
    while q:
        x, y = q.popleft()
        if x < xmin: xmin = x
        if x > xmax: xmax = x
        if y < ymin: ymin = y
        if y > ymax: ymax = y
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if (nx, ny) in seen: continue
            if ds(nx, base) + ds(ny, base) > N: continue
            seen.add((nx, ny))
            q.append((nx, ny))
    return seen, (xmin, xmax, ymin, ymax)

# render each into a tile of common size
TILE = 320  # per-tile square side
PAD = 16
GAP = 8
tiles = []
stats = []
for base, N in CASES:
    pts, (xmin, xmax, ymin, ymax) = bfs(base, N)
    W = xmax - xmin + 1
    H = ymax - ymin + 1
    img = np.zeros((H, W), dtype=np.uint8)
    for x, y in pts:
        img[y - ymin, x - xmin] = 255
    img = img[::-1, :]
    # scale to fit TILE x TILE preserving aspect
    scale = min(TILE / W, TILE / H)
    newW = max(1, int(W * scale))
    newH = max(1, int(H * scale))
    pil = Image.fromarray(img, mode="L").resize((newW, newH), Image.NEAREST)
    tile = Image.new("L", (TILE, TILE), color=0)
    tile.paste(pil, ((TILE - newW)//2, (TILE - newH)//2))
    tiles.append(tile)
    stats.append((base, N, len(pts), xmax))
    print(f"base {base:>2}, N={N:>2}: {len(pts):>8,} points, axis reach ±{xmax}")

# compose horizontal strip with labels
from PIL import ImageDraw, ImageFont
try:
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
except Exception:
    font = ImageFont.load_default()

strip_W = PAD*2 + len(tiles)*TILE + (len(tiles)-1)*GAP
strip_H = PAD*2 + TILE + 40
strip = Image.new("L", (strip_W, strip_H), color=30)
draw = ImageDraw.Draw(strip)
for i, (tile, (base, N, count, reach)) in enumerate(zip(tiles, stats)):
    x0 = PAD + i*(TILE + GAP)
    strip.paste(tile, (x0, PAD))
    label = f"base {base}, N={N}\n{count:,} pts, ±{reach}"
    draw.multiline_text((x0, PAD + TILE + 4), label, fill=220, font=font)

strip.save("digitsum_strip.png")
print("wrote digitsum_strip.png")
