"""BFS the set of lattice points reachable from (0,0) via 4-connected steps
where digitSum(|x|) + digitSum(|y|) <= N. Render as PNG."""

from collections import deque
import sys
import numpy as np
from PIL import Image

N = 19

def ds(v):
    v = abs(v)
    s = 0
    while v:
        s += v % 10
        v //= 10
    return s

def ok(x, y):
    return ds(x) + ds(y) <= N

seen = set()
seen.add((0, 0))
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
        if not ok(nx, ny): continue
        seen.add((nx, ny))
        q.append((nx, ny))

print(f"N = {N}")
print(f"reachable points: {len(seen):,}")
print(f"bounding box: x in [{xmin},{xmax}], y in [{ymin},{ymax}]")

# Render
W = xmax - xmin + 1
H = ymax - ymin + 1
print(f"image size: {W} x {H}")
img = np.zeros((H, W), dtype=np.uint8)
for x, y in seen:
    img[y - ymin, x - xmin] = 255
# flip Y so +y is up
img = img[::-1, :]
Image.fromarray(img, mode="L").save("digitsum_reach.png")
print("wrote digitsum_reach.png")
