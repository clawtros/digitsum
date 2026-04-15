"""BFS with distance tracking. Color each cell by geodesic distance from
origin and by (geodesic - Manhattan) detour."""

import numpy as np
from PIL import Image
from digitsum_lib import bfs_distances, turbo

N = 19

dist, (xmin, xmax, ymin, ymax), max_d = bfs_distances(N)
print(f"N={N}: {len(dist):,} points, max BFS depth = {max_d}")

W = xmax - xmin + 1
H = ymax - ymin + 1
depth_img  = np.full((H, W), -1, dtype=np.int32)
detour_img = np.full((H, W), -1, dtype=np.int32)
for (x, y), d in dist.items():
    depth_img[y - ymin, x - xmin]  = d
    detour_img[y - ymin, x - xmin] = d - (abs(x) + abs(y))

depth_img  = depth_img[::-1, :]
detour_img = detour_img[::-1, :]

def render(data, max_val, outfile, bg=(0, 0, 0)):
    mask = data >= 0
    t = np.where(mask, data / max(1, max_val), 0.0).astype(np.float32)
    rgb = turbo(t)
    rgb[~mask] = bg
    Image.fromarray(rgb, mode="RGB").save(outfile)

render(depth_img, max_d, "digitsum_depth.png")
detour_max = int(detour_img.max())
print(f"max detour (geodesic - L1): {detour_max}")
render(detour_img, detour_max, "digitsum_detour.png")
print("wrote digitsum_depth.png and digitsum_detour.png")
