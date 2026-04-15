"""For N = 1..22, compare:
  - BFS-reachable count from origin under 4-connected moves with ds(|x|)+ds(|y|) <= N
  - constraint-set count inside the reachable bounding box (upper bound)
Plot counts and ratio vs N.
"""
from collections import deque
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def ds(v):
    v = abs(v); s = 0
    while v: s += v % 10; v //= 10
    return s

def bfs(N):
    seen = {(0, 0)}
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
            if (nx,ny) in seen: continue
            if ds(nx) + ds(ny) > N: continue
            seen.add((nx, ny))
            q.append((nx, ny))
    return len(seen), (xmin, xmax, ymin, ymax)

def constraint_in_bbox(N, bbox):
    xmin, xmax, ymin, ymax = bbox
    # count (x,y) in bbox with ds(|x|)+ds(|y|) <= N
    xs = np.arange(xmin, xmax + 1)
    ys = np.arange(ymin, ymax + 1)
    dsx = np.array([ds(int(v)) for v in xs])
    dsy = np.array([ds(int(v)) for v in ys])
    # For each budget level K = 0..N, count x-values with ds<=K, same for y
    # constraint count = sum over (a,b) with a+b<=N of exact_x(a)*exact_y(b)
    max_level = N
    ex = np.zeros(max_level + 1, dtype=np.int64)
    ey = np.zeros(max_level + 1, dtype=np.int64)
    for v in dsx:
        if v <= max_level: ex[v] += 1
    for v in dsy:
        if v <= max_level: ey[v] += 1
    total = 0
    for a in range(N + 1):
        for b in range(N + 1 - a):
            total += int(ex[a]) * int(ey[b])
    return total

results = []
for N in range(1, 23):
    bfs_count, bbox = bfs(N)
    cs_count = constraint_in_bbox(N, bbox)
    ratio = bfs_count / cs_count if cs_count else 1.0
    print(f"N={N:>2}: bfs={bfs_count:>10,}  constraint_bbox={cs_count:>10,}  ratio={ratio:.4f}  bbox=±{bbox[1]}")
    results.append((N, bfs_count, cs_count, ratio))

Ns  = [r[0] for r in results]
bfs_counts = [r[1] for r in results]
cs_counts  = [r[2] for r in results]
ratios     = [r[3] for r in results]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(Ns, bfs_counts, "o-", label="BFS-reachable", color="#3aa0ff")
ax1.plot(Ns, cs_counts,  "s--", label="constraint set (in bbox)", color="#ff6060")
ax1.set_yscale("log")
ax1.set_xlabel("N")
ax1.set_ylabel("count (log scale)")
ax1.set_title("reachable vs constraint-in-bbox")
ax1.legend()
ax1.grid(True, which="both", alpha=0.3)
ax1.set_xticks(Ns)

ax2.plot(Ns, ratios, "o-", color="#60c060")
ax2.set_xlabel("N")
ax2.set_ylabel("reachable / constraint")
ax2.set_title("fraction of bbox constraint-set actually reachable")
ax2.set_ylim(0, 1.05)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(Ns)
for N, r in zip(Ns, ratios):
    ax2.annotate(f"{r:.2f}", (N, r), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8)

plt.tight_layout()
plt.savefig("digitsum_ratio.png", dpi=130)
print("wrote digitsum_ratio.png")
