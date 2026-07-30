"""The front-class family of the 2-D flood, resolved and rendered.

Every wetting front in the flood hierarchy is a scanline set {v : ds(v) <= T}
(verified by hash-cons identity on all 142 fronts of the shallow census), the
exit fronts of any fed tank are scanline(-d) on both edges (verified on all
96,202 memoized flood states; provable from the criterion applied inside the
tank: exit rows need every prefix sum <= 1-d and total <= -d, and the prefix
condition is implied by the total), and the occurring entry thresholds form the
ladder T = 1-d-9m, m >= 0 (m = number of ancestral walls the feed has passed
through), plus empty. Class counts per d are (rungs+1)^2 - 1: 3, 8, 15, 24, ...
— the historical "24" was the 3-level signature truncation's shadow.

This script renders representative tanks (scale 3, exact flood) for the class
families at d = 1, 0, -8. Output: digitsum_classes.png.
"""

import numpy as np
from PIL import Image, ImageDraw
from digitsum_lib import ds, load_font

S = 1000          # scale-3 tank, cell resolution
PANEL = 200       # rendered panel size (S must be a multiple)
PAD, TOP = 14, 46

ds3 = np.fromiter((ds(v) for v in range(S)), dtype=np.int32, count=S)


def flood_tank(d, TL, TB):
    """Exact flood of a scale-3 tank at offset d with scanline entries.
    TL/TB are thresholds or None (empty edge). Returns reach, allowed."""
    K = 27 - d
    EL = np.zeros(S, bool) if TL is None else (ds3 <= TL)
    EB = np.zeros(S, bool) if TB is None else (ds3 <= TB)
    allowed = (ds3[None, :] + ds3[:, None]) <= K   # [v, u]
    reach = np.zeros((S, S), bool)
    R_prev = np.zeros(S, bool)
    for v in range(S):
        A = allowed[v]
        seeds = R_prev & A
        if EB[0] and v == 0:
            seeds = seeds | (EB & A)
        if EL[v] and A[0]:
            seeds = seeds.copy()
            seeds[0] = True
        bid = np.cumsum(~A)
        last = np.maximum.accumulate(np.where(seeds, bid, -1))
        R = A & (last == bid)
        reach[v] = R
        R_prev = R
    return reach, allowed


COL_BG = (16, 17, 21)
COL_FORBID = (26, 28, 34)
COL_DRY = (58, 74, 95)
COL_WET = (52, 170, 255)
COL_ENTRY = (255, 165, 40)
COL_TEXT = (225, 228, 235)


def panel(d, TL, TB):
    reach, allowed = flood_tank(d, TL, TB)
    f = S // PANEL  # downsample factor via block max
    rs = reach.reshape(PANEL, f, PANEL, f).any(axis=(1, 3))
    al = allowed.reshape(PANEL, f, PANEL, f).any(axis=(1, 3))
    img = np.empty((PANEL, PANEL, 3), np.uint8)
    img[:] = COL_FORBID
    img[al & ~rs] = COL_DRY
    img[rs] = COL_WET
    img = img[::-1]  # v upward
    im = Image.new("RGB", (PANEL + 8, PANEL + 8), COL_BG)
    im.paste(Image.fromarray(img), (8, 0))
    dr = ImageDraw.Draw(im)
    # entry fronts in orange on left/bottom margins
    for v in range(PANEL):
        blk = slice(v * f, (v + 1) * f)
        if TL is not None and np.any(ds3[blk] <= TL):
            dr.line([(0, PANEL - 1 - v), (6, PANEL - 1 - v)], fill=COL_ENTRY)
        if TB is not None and np.any(ds3[blk] <= TB):
            dr.line([(8 + v, PANEL + 1), (8 + v, PANEL + 7)], fill=COL_ENTRY)
    return im


if __name__ == "__main__":
    def label(T):
        return "∅" if T is None else str(T)

    ROWS = [
        (1, [(0, None), (None, 0), (0, 0)]),
        (0, [(1, None), (None, 1), (1, 1)]),
        (-8, [(9, None), (None, 9), (9, 9), (9, 0), (0, 9),
              (0, 0), (0, None), (None, 0)]),
    ]
    ncols = max(len(r[1]) for r in ROWS)
    W = PAD + ncols * (PANEL + 8 + PAD)
    H = TOP + len(ROWS) * (PANEL + 8 + 44)
    sheet = Image.new("RGB", (W, H), COL_BG)
    dr = ImageDraw.Draw(sheet)
    font = load_font(15)
    small = load_font(13)
    dr.text((PAD, 10), "front classes of the 2-D flood: entries (orange, scanline "
            "sets T = 1-d-9m) differ; the flood (blue) depends only on d — "
            "classes are provenance labels", fill=COL_TEXT, font=font)
    y = TOP
    for d, classes in ROWS:
        for i, (TL, TB) in enumerate(classes):
            x = PAD + i * (PANEL + 8 + PAD)
            sheet.paste(panel(d, TL, TB), (x, y))
            dr.text((x + 8, y + PANEL + 10),
                    f"d={d}  T_L={label(TL)}  T_B={label(TB)}",
                    fill=COL_TEXT, font=small)
        y += PANEL + 8 + 44
    sheet.save("digitsum_classes.png")
    print("wrote digitsum_classes.png")
