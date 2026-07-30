"""Glossary figure: tank, wall, weir, wetting front in one real strip.

Renders x in [250,320), y in [0,20) at N=19 — scale-1 tanks (25,0)..(31,1).
Along the bottom row the budgets K = 19 - ds(a) shrink 12,11,10,9,8 then jump
to 16 at a=30: weirs narrow (v <= K-9 gives 3,2,1,0 open rows), the wall at
x=299 never dips below the waterline, and tank (30,0) sits dry with K=16 —
the canonical island. Output: digitsum_glossary.png.
"""

import numpy as np
from PIL import Image, ImageDraw
from digitsum_lib import ds, load_font

N = 19
X0, X1, Y0, Y1 = 250, 320, 0, 20
CS = 13                       # cell size in px
MARG, TOP = 30, 128           # margins; TOP holds the labels

W = X1 - X0
H = Y1 - Y0

# reachability over [0, X1) x [0, Y1) via the monotone row sweep
dsx = np.fromiter((ds(v) for v in range(X1)), dtype=np.int32, count=X1)
rows = []
R_prev = None
for y in range(Y1):
    A = (dsx + ds(y)) <= N
    if y == 0:
        S = np.zeros(X1, bool)
        S[0] = True
    else:
        S = R_prev & A
    bid = np.cumsum(~A)
    last = np.maximum.accumulate(np.where(S, bid, -1))
    R = A & (last == bid)
    rows.append(R)
    R_prev = R
reach = np.array(rows)                      # [y, x]
allowed = (dsx[None, :] + np.fromiter((ds(y) for y in range(Y1)),
                                      dtype=np.int32, count=Y1)[:, None]) <= N

COL_BG = (16, 17, 21)
COL_FORBID = (26, 28, 34)
COL_WALL = (96, 26, 30)       # the x=299 all-forbidden wall column
COL_DRY = (58, 74, 95)        # allowed but unreached (dry)
COL_WET = (52, 170, 255)      # flooded
COL_WEIR = (52, 220, 120)     # weir crossings (green ticks on seams)
COL_FRONT = (255, 165, 40)    # wetting front (right-edge flooded cells)
COL_GRID = (80, 84, 94)
COL_TEXT = (225, 228, 235)

img = Image.new("RGB", (2 * MARG + W * CS, TOP + H * CS + MARG + 26), COL_BG)
d = ImageDraw.Draw(img)
font = load_font(15)
small = load_font(12)


def px(x, y):
    """Top-left pixel of cell (x, y); y increases upward."""
    return (MARG + (x - X0) * CS, TOP + (Y1 - 1 - y) * CS)


for y in range(Y0, Y1):
    for x in range(X0, X1):
        if reach[y, x]:
            c = COL_WET
        elif allowed[y, x]:
            c = COL_DRY
        elif x == 299:
            c = COL_WALL
        else:
            c = COL_FORBID
        x0, y0 = px(x, y)
        d.rectangle([x0, y0, x0 + CS - 1, y0 + CS - 1], fill=c)

# tank grid lines every 10 cells
for x in range(X0, X1 + 1, 10):
    x0, _ = px(x, 0)
    d.line([(x0, TOP), (x0, TOP + H * CS)], fill=COL_GRID, width=1)
for y in range(Y0, Y1 + 1, 10):
    _, y0 = px(X0, y - 1)
    d.line([(MARG, y0), (MARG + W * CS, y0)], fill=COL_GRID, width=1)

# wetting front: orange marks inside each tank's rightmost flooded column
for y in range(Y0, Y1):
    for x in range(X0, X1):
        if x % 10 == 9 and reach[y, x]:
            x0, y0 = px(x, y)
            d.line([(x0 + CS - 4, y0 + 1), (x0 + CS - 4, y0 + CS - 2)],
                   fill=COL_FRONT, width=2)

# weirs (drawn last so the green stays clean): tick on any seam whose two
# cells are both flooded
for y in range(Y0, Y1):
    for x in range(X0, X1 - 1):
        if x % 10 == 9 and reach[y, x] and reach[y, x + 1]:
            x0, y0 = px(x + 1, y)
            d.line([(x0 - 1, y0 + 1), (x0 - 1, y0 + CS - 2)], fill=COL_WEIR, width=4)
for y in range(Y0, Y1 - 1):
    for x in range(X0, X1):
        if y % 10 == 9 and reach[y, x] and reach[y + 1, x]:
            x0, y0 = px(x, y)
            d.line([(x0 + 1, y0 - 1), (x0 + CS - 2, y0 - 1)], fill=COL_WEIR, width=4)

# call-outs, ordered left to right so leader lines never cross
def callout(text, tip_xy, text_xy, color):
    d.text(text_xy, text, fill=color, font=font)
    tx, ty = text_xy
    d.line([(tx + 8, ty + 20), tip_xy], fill=color, width=1)

cx = lambda x: MARG + (x - X0) * CS  # noqa: E731
callout("wetting front", (cx(260) - 4, TOP + 17 * CS),
        (cx(251), 96), COL_FRONT)
callout("tank (27,0), K=10: the silhouette", (cx(277), TOP + 12 * CS),
        (cx(258), 8), (150, 176, 205))
callout("weirs narrow toward the wall: 4, 3, 2, 1, closed",
        (cx(280), TOP + 18 * CS), (cx(263), 38), COL_WEIR)
callout("wall x=299: never below waterline", (cx(299) + 7, TOP + 6 * CS),
        (cx(287), 68), (222, 96, 102))
callout("dry tank (30,0), K=16: the island", (cx(304), TOP + 12 * CS),
        (cx(296), 96), (140, 160, 190))

d.text((MARG, TOP + H * CS + 8),
       f"N={N}, cells x in [{X0},{X1}), y in [{Y0},{Y1})   "
       "blue=flooded  slate=allowed but dry  dark=forbidden  "
       "green=weir  orange=front", fill=COL_TEXT, font=small)

img.save("digitsum_glossary.png")
print(f"flooded in strip: {int(reach[:, X0:].sum())}, "
      f"allowed-but-dry: {int((allowed[:, X0:] & ~reach[:, X0:]).sum())}")
print("wrote digitsum_glossary.png")
