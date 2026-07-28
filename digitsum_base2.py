"""Base-2 pilot: exact closed form for the reachable count.

Computes base-2 reachability via the monotone DP and verifies, for every N:

  quadrant reachable   Q(N) = C(2N+3, N)                    (OEIS A002054 shifted)
  full-plane reachable f(N) = 4*C(2N+3, N) - 2^(N+3) + 5
  quadrant constraint  c(N) = (4^(N+1) - C(2N+2, N+1)) / 2

so islands(N) = c(N) - Q(N) is closed-form too, and the reachable/constraint
ratio decays to ZERO like 4/sqrt(pi*N) — there is no finite asymptotic ratio
in base 2.

Usage: digitsum_base2.py [MAXN]   (default 12; N=15 sweeps 4.3e9 cells, ~1-2 min)
"""

import sys
from math import comb, pi, sqrt
import numpy as np


def quadrant_base2(N):
    """Monotone DP specialized to base 2 (popcount)."""
    G = 2 ** (N + 1) - 1  # smallest x with popcount > N
    dsv = np.fromiter((v.bit_count() for v in range(G)), dtype=np.int32, count=G)
    R_prev = None
    q = 0
    for y in range(G):
        allowed = (dsv + int(dsv[y])) <= N
        if y == 0:
            seeds = np.zeros(G, dtype=bool)
            seeds[0] = True
        else:
            seeds = R_prev & allowed
        run_id = np.cumsum(~allowed)
        last_seed = np.maximum.accumulate(np.where(seeds, run_id, -1))
        R = allowed & (last_seed == run_id)
        q += int(R.sum())
        R_prev = R
    return q


MAXN = int(sys.argv[1]) if len(sys.argv) > 1 else 12

print(f"{'N':>2} {'Q (DP)':>14} {'C(2N+3,N)':>14} {'f (formula)':>14} {'ratio':>7} {'4/sqrt(piN)':>11}")
for N in range(1, MAXN + 1):
    q = quadrant_base2(N)
    q_formula = comb(2 * N + 3, N)
    f_formula = 4 * q_formula - 2 ** (N + 3) + 5
    con = (4 ** (N + 1) - comb(2 * N + 2, N + 1)) // 2
    tag = "" if q == q_formula else "  *** MISMATCH ***"
    print(f"{N:>2} {q:>14,} {q_formula:>14,} {f_formula:>14,}"
          f" {q/con:>7.4f} {4/sqrt(pi*N):>11.4f}{tag}", flush=True)
    assert q == q_formula
print("\nall N verified: Q(N) = C(2N+3, N) exactly")
