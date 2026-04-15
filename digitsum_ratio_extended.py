"""Extend the ratio analysis through N=28 to catch the predicted cliff at N=27.
Uses numpy array BFS for speed at larger N.
"""
from collections import deque
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import time

def ds(v):
    v = abs(v); s = 0
    while v: s += v % 10; v //= 10
    return s

def bfs_fast(N):
    """BFS using a numpy bool grid. Grid size bounded by conservative axis reach."""
    # Conservative axis bound: first x with ds(x) > N. We can overshoot safely.
    # For N, axis reach stops at first x with ds(x)=N+1. Grow bound to find it.
    bound = 10
    while True:
        # find the first x with ds(x) > N within [0, bound]
        hit = None
        for x in range(bound):
            if ds(x) > N:
                hit = x; break
        if hit is not None and hit < bound - 1:
            axis_bound = hit
            break
        bound *= 10
        if bound > 100_000:
            raise RuntimeError("bound exploded")
    # grid spans [-axis_bound, axis_bound] on each axis
    G = axis_bound
    size = 2*G + 1
    visited = np.zeros((size, size), dtype=bool)
    # center (G,G) is origin
    ox, oy = G, G
    visited[oy, ox] = True
    q = deque([(0, 0)])
    count = 1
    xmin = xmax = ymin = ymax = 0
    while q:
        x, y = q.popleft()
        if x < xmin: xmin = x
        if x > xmax: xmax = x
        if y < ymin: ymin = y
        if y > ymax: ymax = y
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            gx, gy = ox+nx, oy+ny
            if gx < 0 or gx >= size or gy < 0 or gy >= size: continue
            if visited[gy, gx]: continue
            if ds(nx) + ds(ny) > N: continue
            visited[gy, gx] = True
            count += 1
            q.append((nx, ny))
    return count, (xmin, xmax, ymin, ymax)

def constraint_in_bbox(N, bbox):
    xmin, xmax, ymin, ymax = bbox
    xs = np.arange(xmin, xmax + 1)
    ys = np.arange(ymin, ymax + 1)
    dsx = np.fromiter((ds(int(v)) for v in xs), dtype=np.int32, count=len(xs))
    dsy = np.fromiter((ds(int(v)) for v in ys), dtype=np.int32, count=len(ys))
    ex = np.bincount(dsx[dsx <= N], minlength=N+1)
    ey = np.bincount(dsy[dsy <= N], minlength=N+1)
    total = 0
    for a in range(N + 1):
        for b in range(N + 1 - a):
            total += int(ex[a]) * int(ey[b])
    return total

results = []
for N in range(1, 29):
    t0 = time.time()
    bfs_count, bbox = bfs_fast(N)
    cs_count = constraint_in_bbox(N, bbox)
    ratio = bfs_count / cs_count if cs_count else 1.0
    dt = time.time() - t0
    print(f"N={N:>2}: bfs={bfs_count:>12,}  constraint={cs_count:>12,}  ratio={ratio:.4f}  bbox=±{bbox[1]}  ({dt:.1f}s)")
    results.append((N, bfs_count, cs_count, ratio, bbox[1]))

Ns  = [r[0] for r in results]
bfs_counts = [r[1] for r in results]
cs_counts  = [r[2] for r in results]
ratios     = [r[3] for r in results]
bboxes     = [r[4] for r in results]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))

ax1.plot(Ns, bfs_counts, "o-", label="BFS-reachable", color="#3aa0ff")
ax1.plot(Ns, cs_counts,  "s--", label="constraint set (in bbox)", color="#ff6060")
ax1.set_yscale("log")
ax1.set_xlabel("N")
ax1.set_ylabel("count (log scale)")
ax1.set_title("reachable vs constraint-in-bbox")
ax1.legend()
ax1.grid(True, which="both", alpha=0.3)
ax1.set_xticks(Ns)
# vertical dashed lines at predicted cliffs N = 9, 18, 27
for c in (9, 18, 27):
    ax1.axvline(c, color="#999999", linestyle=":", alpha=0.6)

ax2.plot(Ns, ratios, "o-", color="#60c060")
ax2.set_xlabel("N")
ax2.set_ylabel("reachable / constraint")
ax2.set_title("fraction of bbox constraint-set actually reachable")
ax2.set_ylim(0, 1.05)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(Ns)
for c in (9, 18, 27):
    ax2.axvline(c, color="#999999", linestyle=":", alpha=0.6)
for N, r in zip(Ns, ratios):
    ax2.annotate(f"{r:.2f}", (N, r), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=7.5)

plt.tight_layout()
plt.savefig("digitsum_ratio_extended.png", dpi=130)
print("wrote digitsum_ratio_extended.png")
