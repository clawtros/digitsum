"""Render reachable-region images for multiple bases, sized so the
bounding boxes are comparable (~300 per axis)."""

import numpy as np
from PIL import Image, ImageDraw
from digitsum_lib import bfs, load_font

# (base, N) pairs chosen so max axis reach ~ 250-500
CASES = [(2, 8), (3, 10), (4, 12), (5, 14), (10, 19)]

TILE = 320
PAD = 16
GAP = 8
tiles = []
stats = []
for base, N in CASES:
    pts, (xmin, xmax, ymin, ymax) = bfs(N, base=base)
    W = xmax - xmin + 1
    H = ymax - ymin + 1
    img = np.zeros((H, W), dtype=np.uint8)
    for x, y in pts:
        img[y - ymin, x - xmin] = 255
    img = img[::-1, :]
    scale = min(TILE / W, TILE / H)
    newW = max(1, int(W * scale))
    newH = max(1, int(H * scale))
    pil = Image.fromarray(img, mode="L").resize((newW, newH), Image.NEAREST)
    tile = Image.new("L", (TILE, TILE), color=0)
    tile.paste(pil, ((TILE - newW)//2, (TILE - newH)//2))
    tiles.append(tile)
    stats.append((base, N, len(pts), xmax))
    print(f"base {base:>2}, N={N:>2}: {len(pts):>8,} points, axis reach ±{xmax}")

font = load_font(16)
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
