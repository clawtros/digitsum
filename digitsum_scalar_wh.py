"""Scalar Wiener-Hopf warm-up: the classless walk model for the constant c.

Model: descending the tank hierarchy, a cell's ancestry does a mean-zero walk
d_{s+1} = d_s + (i_s + j_s) - (b-1), starting at d_0 = 1 (the peak-line top
tank), where (i_s, j_s) are the cell's digits. The cell is ALLOWED iff the walk
ends at d <= 0 (exactly ds(x)+ds(y) <= N), and — classless approximation —
REACHABLE iff the walk also stays <= a at every scale (census: the active band
boundary is a = 1). Then

    ratio(N) ~ P(stay <= a and end <= 0) / P(end <= 0),   N = (b-1)k - 1,

and c_scalar = lim ratio * sqrt(N), computed by exact DP + extrapolation.
Base 2 (where front-classes are simplest) is the control against the exact
c = 4/sqrt(pi); the barrier offset a is varied to show model sensitivity.

The step pmf is the discrete tent on [-(b-1), b-1] (sum of two uniform digits,
centered); it is symmetric, so the end-<=0 probability is (1 - P(S_k = 0))/2
minus nothing: P(S_k <= -1) = (1 - P(S_k = 0))/2 exactly.
"""

import numpy as np
from math import sqrt, pi


def step_pmf(b):
    digit = np.full(b, 1.0 / b)
    return np.convolve(digit, digit)  # index m <-> step m - (b-1)


def c_scalar(b, a, ks):
    """c_k = ratio_k * sqrt(N) for k in ks, absorbing barrier at d > a.
    W index i <-> d = a - i; a symmetric pmf makes the step a plain convolution
    with the slice [b-1 : b-1+span] dropping d > a (absorption)."""
    pmf = step_pmf(b)
    kmax = max(ks)
    span = (b - 1) * (kmax + 2) + a + 2
    W = np.zeros(span)
    W[a - 1] = 1.0                       # start at d = 1  (requires a >= 1)
    S = np.ones(1)                       # unconstrained sum distribution
    out = {}
    for k in range(1, kmax + 1):
        W = np.convolve(W, pmf)[b - 1: b - 1 + span]
        S = np.convolve(S, pmf)
        if k in ks:
            N = (b - 1) * k - 1
            stay_end = W[a:].sum()               # survived, end d <= 0
            allowed = (1.0 - S[(len(S) - 1) // 2]) / 2  # P(S_k <= -1)
            out[k] = (stay_end / allowed) * sqrt(N)
    return out


def extrapolate(vals):
    """Fit c_k = c + p/sqrt(k) + q/k, return c."""
    ks = np.array(sorted(vals), float)
    cs = np.array([vals[int(k)] for k in ks])
    X = np.stack([np.ones_like(ks), ks ** -0.5, 1 / ks], axis=1)
    coef, *_ = np.linalg.lstsq(X, cs, rcond=None)
    return coef[0]


if __name__ == "__main__":
    KS = [250, 500, 1000, 2000, 4000]
    print(f"control: base 2 (exact c = 4/sqrt(pi) = {4 / sqrt(pi):.6f})")
    for a in (1, 2, 3):
        print(f"  barrier d<={a}:  c_scalar = {extrapolate(c_scalar(2, a, KS)):.6f}")

    print("\nbase 10 (true c = 3.865 +- 0.004):")
    for a in (1, 2, 3):
        print(f"  barrier d<={a}:  c_scalar = {extrapolate(c_scalar(10, a, KS)):.6f}")

    print("\nbases 3,4,5 at barrier d<=1 (crest upper bounds: 2.528, 2.747, 2.958):")
    for b in (3, 4, 5):
        print(f"  base {b}: c_scalar = {extrapolate(c_scalar(b, 1, KS)):.6f}")
