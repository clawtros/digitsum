"""Benchmark the four solver generations on full-plane f(N).

  bfs    set-based BFS over the plane          (digitsum_lib.bfs)
  grid   numpy-grid BFS                        (digitsum_lib.bfs_grid)
  mono   monotone DP, vectorized row sweep     (digitsum_lib.monotone_reach_count)
  tanks  gastank flood recursion, hash-consed  (digitsum_tanks.quadrant)

Each approach runs only up to the N where it stays practical (time/memory).
tanks is timed cold: its module is reloaded per N so memoization from earlier
rows doesn't flatter it. All results computed at the same N are cross-checked.
"""

import importlib
import time
import numpy as np
from digitsum_lib import bfs, bfs_grid, monotone_reach_count, axis_bound
import digitsum_tanks

NS = [8, 17, 19, 26, 28, 36, 45, 90, 180, 360, 630]
CAPS = {"bfs": 26, "grid": 28, "mono": 36, "tanks": 630}


def run_bfs(N):
    return len(bfs(N)[0])


def run_grid(N):
    visited, _ = bfs_grid(N)
    return int(np.count_nonzero(visited))


def run_mono(N):
    return monotone_reach_count(N)


def run_tanks(N):
    importlib.reload(digitsum_tanks)  # cold start: drop memo + interned fronts
    return 4 * digitsum_tanks.quadrant(N) - 4 * axis_bound(N) + 1


RUNNERS = {"bfs": run_bfs, "grid": run_grid, "mono": run_mono, "tanks": run_tanks}

print(f"{'N':>4} " + "".join(f"{m:>12} " for m in RUNNERS) + " f(N)")
for N in NS:
    cells, times = {}, {}
    for m, fn in RUNNERS.items():
        if N > CAPS[m]:
            continue
        t0 = time.time()
        cells[m] = fn(N)
        times[m] = time.time() - t0
    assert len(set(cells.values())) == 1, (N, cells)
    row = "".join(
        f"{times[m]:>11.3f}s " if m in times else f"{'—':>12} " for m in RUNNERS
    )
    print(f"{N:>4} {row} {next(iter(cells.values())):,}", flush=True)
