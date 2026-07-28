"""The monotone-staircase lemma and the decade-4 data it unlocks.

Part 1 verifies the lemma: full-plane BFS reachability equals directed
(right/up only) reachability, for N=1..22 in base 10 and small N in bases 2..5.
Part 2 uses the fast DP to extend the reach/constraint ratio table through the
N=36 cliff (bbox ±19998; the N=36 row alone takes a couple of minutes).
"""

import numpy as np
from digitsum_lib import ds, bfs, axis_bound, monotone_reach_count

# ---- part 1: lemma verification against BFS ----
print("monotone lemma vs BFS, base 10:")
for N in range(1, 23):
    full_bfs = len(bfs(N)[0])
    full_mono = monotone_reach_count(N)
    tag = "OK" if full_bfs == full_mono else "*** MISMATCH ***"
    print(f"  N={N:>2}  BFS={full_bfs:>9,}  monoDP={full_mono:>9,}  {tag}")

print("monotone lemma vs BFS, other bases:")
for base, n_max in [(2, 10), (3, 11), (4, 12), (5, 14)]:
    bad = [N for N in range(1, n_max + 1)
           if len(bfs(N, base)[0]) != monotone_reach_count(N, base)]
    print(f"  base {base}, N=1..{n_max}: {'OK' if not bad else f'MISMATCH at {bad}'}")

# ---- part 2: extended ratio table via the DP ----
print("\nreach/constraint through the N=36 cliff:")
for N in range(23, 37):
    reach = monotone_reach_count(N)
    G = axis_bound(N)
    dsv = np.fromiter((ds(v) for v in range(G)), dtype=np.int64, count=G)
    hist = np.bincount(dsv, minlength=N + 1)[: N + 1].astype(object)
    two = 2 * hist
    two[0] -= 1  # x=0 counted once
    constraint = sum(int(two[a]) * int(sum(two[: N + 1 - a])) for a in range(N + 1))
    print(f"  N={N:>2}  reach={reach:>12,}  constraint={constraint:>12,}"
          f"  ratio={reach/constraint:.4f}  bbox=±{G-1}", flush=True)
