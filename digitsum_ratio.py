"""For N = 1..22, compare BFS-reachable count against the constraint-set
count inside the reachable bounding box. Plot counts and ratio vs N."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from digitsum_lib import bfs, constraint_in_bbox

results = []
for N in range(1, 23):
    seen, bbox = bfs(N)
    bfs_count = len(seen)
    cs_count = constraint_in_bbox(N, bbox)
    ratio = bfs_count / cs_count if cs_count else 1.0
    print(f"N={N:>2}: bfs={bfs_count:>10,}  constraint_bbox={cs_count:>10,}  ratio={ratio:.4f}  bbox=±{bbox[1]}")
    results.append((N, bfs_count, cs_count, ratio))

Ns = [r[0] for r in results]
bfs_counts = [r[1] for r in results]
cs_counts = [r[2] for r in results]
ratios = [r[3] for r in results]

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
