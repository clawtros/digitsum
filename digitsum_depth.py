"""BFS with distance tracking. Color each cell by geodesic (shortest-path)
distance from origin, revealing the isthmuses the path had to squeeze through."""

from collections import deque
import numpy as np
from PIL import Image

BASE = 10
N = 19

def ds(v, b=BASE):
    v = abs(v)
    s = 0
    while v:
        s += v % b
        v //= b
    return s

dist = {(0, 0): 0}
q = deque([(0, 0)])
xmin = xmax = ymin = ymax = 0
max_d = 0
while q:
    x, y = q.popleft()
    d = dist[(x, y)]
    if d > max_d: max_d = d
    if x < xmin: xmin = x
    if x > xmax: xmax = x
    if y < ymin: ymin = y
    if y > ymax: ymax = y
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if (nx, ny) in dist: continue
        if ds(nx) + ds(ny) > N: continue
        dist[(nx, ny)] = d + 1
        q.append((nx, ny))

print(f"base {BASE}, N={N}: {len(dist):,} points, max BFS depth = {max_d}")

# L1 (Manhattan) distance from origin for comparison:
# if reachability were pure taxicab the geodesic would equal |x|+|y|.
# plot (geodesic - L1) to highlight detours too.

W = xmax - xmin + 1
H = ymax - ymin + 1
depth_img = np.full((H, W), -1, dtype=np.int32)
detour_img = np.full((H, W), -1, dtype=np.int32)
for (x, y), d in dist.items():
    row = y - ymin
    col = x - xmin
    depth_img[row, col] = d
    detour_img[row, col] = d - (abs(x) + abs(y))  # >=0 always

depth_img = depth_img[::-1, :]
detour_img = detour_img[::-1, :]

def colormap_turbo(t):
    """t in [0,1] -> RGB uint8. Cheap polynomial approx of turbo."""
    t = np.clip(t, 0.0, 1.0)
    r = 0.13572138 + 4.61539260*t - 42.66032258*t**2 + 132.13108234*t**3 - 152.94239396*t**4 + 59.28637943*t**5
    g = 0.09140261 + 2.19418839*t + 4.84296658*t**2 - 14.18503333*t**3 + 4.27729857*t**4 + 2.82956604*t**5
    b = 0.10667330 + 12.64194608*t - 60.58204836*t**2 + 110.36276771*t**3 - 89.90310912*t**4 + 27.34824973*t**5
    rgb = np.stack([r, g, b], axis=-1)
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)

def render(data, max_val, outfile, bg=(0,0,0)):
    mask = data >= 0
    t = np.where(mask, data / max(1, max_val), 0.0).astype(np.float32)
    rgb = colormap_turbo(t)
    rgb[~mask] = bg
    Image.fromarray(rgb, mode="RGB").save(outfile)

render(depth_img, max_d, "digitsum_depth.png")
detour_max = int(detour_img.max())
print(f"max detour (geodesic - L1): {detour_max}")
render(detour_img, detour_max, "digitsum_detour.png")
print("wrote digitsum_depth.png and digitsum_detour.png")
