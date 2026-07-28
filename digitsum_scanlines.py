"""Scanline decomposition. The 2D reachable set factors:
  (x,y) reachable  <=>  digitSum(|x|) + digitSum(|y|) <= N
so every row y at budget K = N - digitSum(|y|) shows the SAME 1D pattern
"integers x with digitSum(|x|) <= K". Only N+1 distinct rows (K=0..N)."""

import numpy as np
from PIL import Image, ImageDraw
from digitsum_lib import ds, turbo_scalar, load_font

N = 19
MAX_X = 300  # covers the reachable axis range ±298 with slack

xs = np.arange(MAX_X + 1)
signal = np.array([ds(x) for x in xs])

# ---- panel 1: digit-sum signal along positive x-axis ----
W1, H1 = 1200, 340
panel1 = Image.new("RGB", (W1, H1), (20, 20, 24))
d1 = ImageDraw.Draw(panel1)
font = load_font(14)

margin = 40
plot_w = W1 - 2*margin
plot_h = H1 - 2*margin
y_max = 27
def ymap(v): return margin + plot_h - int(v / y_max * plot_h)
def xmap(v): return margin + int(v / MAX_X * plot_w)

d1.line([(margin, ymap(N)), (margin+plot_w, ymap(N))], fill=(200, 60, 60), width=2)
pts = [(xmap(x), ymap(s)) for x, s in zip(xs, signal)]
d1.line(pts, fill=(200, 220, 255), width=1)
d1.text((margin, 8), f"digit-sum(x) for x = 0..{MAX_X}   (red line: threshold N={N})", fill=(220,220,220), font=font)
d1.text((margin, H1-20), "x", fill=(180,180,180), font=font)
d1.text((8, margin), "ds(x)", fill=(180,180,180), font=font)
for tx in range(0, MAX_X+1, 50):
    px = xmap(tx)
    d1.line([(px, margin+plot_h), (px, margin+plot_h+4)], fill=(120,120,120))
    d1.text((px-8, margin+plot_h+6), str(tx), fill=(150,150,150), font=font)

panel1.save("digitsum_signal.png")

# ---- panel 2: stacked 1D scanlines, one per budget K = 0..N ----
row_h = 18
label_w = 130
rows_img_w = label_w + (MAX_X + 1)
rows_img_h = row_h * (N + 1) + 40
panel2 = Image.new("RGB", (rows_img_w, rows_img_h), (20, 20, 24))
d2 = ImageDraw.Draw(panel2)
d2.text((8, 8), f"1D scanlines: x with digitSum(x) <= K, for K=0..{N}", fill=(220,220,220), font=font)

counts = []
for K in range(N, -1, -1):
    row_idx = N - K
    y0 = 36 + row_idx * row_h
    col = turbo_scalar(K / N)
    mask = signal <= K
    count = int(mask.sum())
    counts.append((K, count))
    d2.text((8, y0 + 2), f"K={K:>2}  ({count:>3})", fill=col, font=font)
    for x in range(MAX_X + 1):
        if mask[x]:
            d2.line([(label_w + x, y0 + 2), (label_w + x, y0 + row_h - 2)], fill=col)

panel2.save("digitsum_scanlines.png")

print("1D reach count (one-sided, x >= 0) per budget K:")
for K, c in sorted(counts):
    print(f"  K={K:>2}: {c}")

# sanity: 2D total from factorization over Z^2 within the true BFS bbox ±298.
# (Using ±MAX_X here would overcount: columns/rows at ±300 are allowed but sit
# outside the reachable bounding box — this discrepancy caused a wrong gap
# figure, 66,736 vs the correct 64,488, in an earlier FINDINGS revision.)
BBOX = 298
exact = [0] * (N + 2)
for x in range(BBOX + 1):
    s = ds(x)
    if s <= N:
        exact[s] += 1
exact_two = [2 * exact[j] for j in range(N + 1)]
exact_two[0] -= 1  # x=0 counted once
total = 0
for a in range(N + 1):
    for b in range(N + 1 - a):
        total += exact_two[a] * exact_two[b]
print(f"factorized 2D total (sanity): {total:,}")
