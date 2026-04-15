"""Extend the ratio analysis through N=28 using numpy-grid BFS for speed."""

import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from digitsum_lib import bfs_grid, constraint_in_bbox

results = []
for N in range(1, 29):
    t0 = time.time()
    visited, G = bfs_grid(N)
    bfs_count = int(visited.sum())
    # reachable bbox from the visited array
    rows = visited.any(axis=1); cols = visited.any(axis=0)
    ry = [i for i, b in enumerate(rows) if b]
    cx = [i for i, b in enumerate(cols) if b]
    ymin, ymax = ry[0] - G, ry[-1] - G
    xmin, xmax = cx[0] - G, cx[-1] - G
    bbox = (xmin, xmax, ymin, ymax)
    cs_count = constraint_in_bbox(N, bbox)
    ratio = bfs_count / cs_count if cs_count else 1.0
    dt = time.time() - t0
    print(f"N={N:>2}: bfs={bfs_count:>12,}  constraint={cs_count:>12,}  ratio={ratio:.4f}  bbox=±{xmax}  ({dt:.1f}s)")
    results.append((N, bfs_count, cs_count, ratio, xmax))

Ns  = [r[0] for r in results]
bfs_counts = [r[1] for r in results]
cs_counts  = [r[2] for r in results]
ratios     = [r[3] for r in results]

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
