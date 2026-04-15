"""Scanline decomposition. The 2D reachable set factors:
  (x,y) reachable  <=>  digitSum(|x|) + digitSum(|y|) <= N
so every row y at budget K = N - digitSum(|y|) shows the SAME 1D pattern
"integers x with digitSum(|x|) <= K". Only 20 distinct rows (K=0..19).
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = 10
N = 19
MAX_X = 300  # covers the reachable axis range ±298 with slack

def ds(v, b=BASE):
    v = abs(v)
    s = 0
    while v:
        s += v % b
        v //= b
    return s

# ---- panel 1: digit-sum signal along positive x-axis, with threshold rules ----
xs = np.arange(MAX_X + 1)
signal = np.array([ds(x) for x in xs])

W1 = 1200
H1 = 340
panel1 = Image.new("RGB", (W1, H1), (20, 20, 24))
d1 = ImageDraw.Draw(panel1)
margin = 40
plot_w = W1 - 2*margin
plot_h = H1 - 2*margin
# horizontal grid at each integer digit-sum level 0..25
y_max = 27
def ymap(v): return margin + plot_h - int(v / y_max * plot_h)
def xmap(v): return margin + int(v / MAX_X * plot_w)
# threshold line at N=19
d1.line([(margin, ymap(N)), (margin+plot_w, ymap(N))], fill=(200, 60, 60), width=2)
# signal
pts = [(xmap(x), ymap(s)) for x, s in zip(xs, signal)]
d1.line(pts, fill=(200, 220, 255), width=1)
# axis labels
try:
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
except Exception:
    font = ImageFont.load_default()
d1.text((margin, 8), f"digit-sum(x) for x = 0..{MAX_X}   (red line: threshold N={N})", fill=(220,220,220), font=font)
d1.text((margin, H1-20), "x", fill=(180,180,180), font=font)
d1.text((8, margin), "ds(x)", fill=(180,180,180), font=font)
# x ticks every 50
for tx in range(0, MAX_X+1, 50):
    px = xmap(tx)
    d1.line([(px, margin+plot_h), (px, margin+plot_h+4)], fill=(120,120,120))
    d1.text((px-8, margin+plot_h+6), str(tx), fill=(150,150,150), font=font)

panel1.save("digitsum_signal.png")

# ---- panel 2: 20 stacked 1D scanlines, one per budget K = 0..19 ----
# each row shows which x in 0..MAX_X satisfy ds(x) <= K
row_h = 18
label_w = 130
rows_img_w = label_w + (MAX_X + 1)
rows_img_h = row_h * (N + 1) + 40
panel2 = Image.new("RGB", (rows_img_w, rows_img_h), (20, 20, 24))
d2 = ImageDraw.Draw(panel2)
d2.text((8, 8), f"1D scanlines: x with digitSum(x) <= K, for K=0..{N}", fill=(220,220,220), font=font)

# use turbo-ish colour per K
def turbo(t):
    t = np.clip(t, 0, 1)
    r = 0.13572138 + 4.61539260*t - 42.66032258*t**2 + 132.13108234*t**3 - 152.94239396*t**4 + 59.28637943*t**5
    g = 0.09140261 + 2.19418839*t + 4.84296658*t**2 - 14.18503333*t**3 + 4.27729857*t**4 + 2.82956604*t**5
    b = 0.10667330 + 12.64194608*t - 60.58204836*t**2 + 110.36276771*t**3 - 89.90310912*t**4 + 27.34824973*t**5
    return tuple(int(max(0,min(1,c))*255) for c in (r,g,b))

counts = []
for K in range(N, -1, -1):  # draw large K at top
    row_idx = N - K
    y0 = 36 + row_idx * row_h
    col = turbo(K / N)
    mask = signal <= K
    count = int(mask.sum())
    counts.append((K, count))
    # draw label
    d2.text((8, y0 + 2), f"K={K:>2}  ({count:>3})", fill=col, font=font)
    # draw strip
    for x in range(MAX_X + 1):
        if mask[x]:
            d2.point((label_w + x, y0 + row_h // 2), fill=col)
            d2.line([(label_w + x, y0 + 2), (label_w + x, y0 + row_h - 2)], fill=col)

panel2.save("digitsum_scanlines.png")

print("1D reach count (one-sided, x >= 0) per budget K:")
for K, c in sorted(counts):
    print(f"  K={K:>2}: {c}")

# sanity: 2D total from factorization
# full reachable count = sum over (x,y) in Z^2 of [ds(|x|)+ds(|y|) <= N]
# = sum_{a=0..N} cnt1d_all(a) * cnt1d_all(N-a) where cnt1d_all(j) = #{x in Z : ds(|x|)=j}
# but we only have <= K cumulative; use exact-j.
exact = [0]*(N+2)
for x in xs:
    s = ds(x)
    if s <= N:
        exact[s] += 1
# two-sided: for x != 0 count both signs
exact_two = [2*exact[j] for j in range(N+1)]
exact_two[0] -= 1  # x=0 counted once
from itertools import product
total = 0
for a in range(N+1):
    for b in range(N+1-a):
        total += exact_two[a] * exact_two[b]
print(f"factorized 2D total (sanity): {total:,}")
