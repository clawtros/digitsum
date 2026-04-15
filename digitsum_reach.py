"""BFS the set of lattice points reachable from (0,0) via 4-connected steps
where digitSum(|x|) + digitSum(|y|) <= N. Render as PNG."""

import numpy as np
from PIL import Image
from digitsum_lib import bfs

N = 19

seen, (xmin, xmax, ymin, ymax) = bfs(N)

print(f"N = {N}")
print(f"reachable points: {len(seen):,}")
print(f"bounding box: x in [{xmin},{xmax}], y in [{ymin},{ymax}]")

W = xmax - xmin + 1
H = ymax - ymin + 1
print(f"image size: {W} x {H}")
img = np.zeros((H, W), dtype=np.uint8)
for x, y in seen:
    img[y - ymin, x - xmin] = 255
img = img[::-1, :]  # +y up
Image.fromarray(img, mode="L").save("digitsum_reach.png")
print("wrote digitsum_reach.png")
