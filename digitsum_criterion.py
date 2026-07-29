"""THE REACHABILITY CRITERION — the master theorem of this project.

In base b with threshold N, write x and y with k = N//(b-1) + 1 digits and set
    d_s = d_0 + sum_{t<=s} (x_t + y_t - (b-1)),   d_0 = (b-1)k - N.
Then (x,y) in the quadrant is reachable from the origin iff
    d_s <= 1 for every s < k   AND   d_k <= 0.
(The final condition is exactly ds(x)+ds(y) <= N; the prefix condition says
every prefix pair leaves at least (b-1)*(digits remaining) - 1 of budget — the
weir slack is the "+1".)

PROVED in PROOF.md (wall-certificate necessity + corner-staircase sufficiency),
and verified exhaustively against monotone-DP reachability for base 10
(N=9..29), base 3 (N=3..15), base 5 (N=5..19), and against exact tank-solver
counts to N=989 (integer equality; see __main__). Subsumes the monotone lemma and the
gastank recursion for counting purposes: Q(N) follows from a 1-D walk DP in
O(k^2 b) time — microseconds where the tank solver needed minutes.

Consequence for the constant c: Q(N)/10^(2k) is the survival probability of a
tent-walk below a wall — classical one-boundary lattice-path asymptotics
(Wiener-Hopf / kernel method) — computed here by DP to k=16000:
c(base 10, peak line) = 3.84717(5), retracting the earlier 3.865 +- 0.004.
"""

import json
import numpy as np
from math import sqrt, pi
from digitsum_lib import axis_bound


def step_weights(b):
    """Integer counts of (i+j) - (b-1) for digit pairs: tent on [-(b-1), b-1]."""
    w = [0] * (2 * b - 1)
    for i in range(b):
        for j in range(b):
            w[i + j] += 1
    return w  # index m <-> step m - (b-1)


def quadrant_exact(N, b=10):
    """Exact Q(N) via the criterion: integer 1-D walk DP."""
    k = N // (b - 1) + 1
    d0 = (b - 1) * k - N
    w = step_weights(b)
    W = {d0: 1}  # keyed by d; barrier d <= 1 enforced on transitions
    for s in range(k):
        nxt = {}
        for d, cnt in W.items():
            for m, wm in enumerate(w):
                d2 = d + m - (b - 1)
                if d2 <= (1 if s < k - 1 else 0):
                    nxt[d2] = nxt.get(d2, 0) + cnt * wm
        W = nxt
    return sum(W.values())


def full_plane_exact(N, b=10):
    return 4 * quadrant_exact(N, b) - 4 * axis_bound(N, b) + 1


def c_constant(b, kmax=16000, ks=None):
    """Peak-line c via float DP + extrapolation in [1, 1/sqrt k, 1/k, k^-1.5]."""
    ks = ks or [kmax // 8, kmax // 4, kmax // 2, 3 * kmax // 4, kmax]
    pmf = np.array(step_weights(b), float) / b ** 2
    span = (b - 1) * (kmax + 2) + 3
    W = np.zeros(span)
    W[0] = 1.0  # index i <-> d = 1 - i, start at d = 1
    S = np.ones(1)
    vals = {}
    for k in range(1, kmax + 1):
        W = np.convolve(W, pmf)[b - 1: b - 1 + span]
        S = np.convolve(S, pmf)
        if k in ks:
            N = (b - 1) * k - 1
            allowed = (1.0 - S[(len(S) - 1) // 2]) / 2
            vals[k] = (W[1:].sum() / allowed) * sqrt(N)
    kk = np.array(sorted(vals), float)
    cs = np.array([vals[int(t)] for t in kk])
    X = np.stack([np.ones_like(kk), kk ** -0.5, 1 / kk, kk ** -1.5], axis=1)
    coef, *_ = np.linalg.lstsq(X, cs, rcond=None)
    return coef[0], vals


if __name__ == "__main__":
    from digitsum_tanks import KNOWN_F

    # integer validation vs BFS-era values and the exact tank data
    for N in range(1, 37):
        assert full_plane_exact(N) == KNOWN_F[N - 1], N
    print("criterion DP vs BFS f(N), N=1..36: OK", flush=True)

    peaks = {int(N): int(q) for N, q in json.load(
        open(__file__.rsplit("/", 1)[0] + "/digitsum_peakdata.json"))["10"].items()}
    for N in (269, 449, 629, 809, 989):
        assert quadrant_exact(N) == peaks[N], N
    print("criterion DP vs tank solver Q(N) at N=269..989: EXACT integer match", flush=True)

    c2, _ = c_constant(2, 16000)
    print(f"\nbase 2:  c = {c2:.6f}   (exact 4/sqrt(pi) = {4 / sqrt(pi):.6f})", flush=True)
    c10, vals = c_constant(10, 16000)
    for k, v in sorted(vals.items()):
        print(f"  c_k(10) at k={k}: {v:.7f}")
    print(f"base 10: c = {c10:.6f}")
