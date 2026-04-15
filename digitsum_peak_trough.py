"""Compare a peak-of-decade vs trough-of-decade image.
Decade 2: N=11 (trough, ratio 0.73) vs N=17 (peak, 0.81).
Decade 3: N=20 (trough, 0.61) vs N=26 (peak, 0.69)."""

import numpy as np
from PIL import Image, ImageDraw
from digitsum_lib import bfs_grid, load_font


def render_tile(visited, target, color):
    H, W = visited.shape
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[visited] = color
    img = Image.fromarray(rgb, "RGB").transpose(Image.FLIP_TOP_BOTTOM)
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
font = load_font(16)
small = load_font(13)

tiles = []
for label, N, color in cases:
    v, G = bfs_grid(N)
    tile = render_tile(v, TILE, color)
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
