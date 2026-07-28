"""The constant c in reachable/constraint ~ c/sqrt(N): analysis on the peak line.

Loads digitsum_peakdata.json (exact peak-line Q values: base 10 to N=989, bases
3/4/5 to N~320-455; regenerate with digitsum_tanks.py / digitsum_tanks_anybase.py),
computes c_N = Q/constraint * sqrt(N), and prints the convergence picture.

Findings (2026-07): base-10 c_N rises to a crest of 3.86931 at N~650 then
descends with accelerating increments — at least two competing correction terms
(a fading geometric-per-decade rise ~rho^q, rho~0.91, and a slow negative
power-law tail). Extrapolation models disagree at the 1e-3 level, so
c = 3.865 +- 0.004 is the honest estimate; sqrt(15) = 3.87298 lies above the
crest of the entire sequence and is REFUTED. Base 2 is exact: c = 4/sqrt(pi).
"""

import json
from math import sqrt, pi

DATA = json.load(open(__file__.rsplit("/", 1)[0] + "/digitsum_peakdata.json"))


def dist(b, k):
    """Digit-sum distribution over [0, b^k)."""
    h = [1] * b
    for _ in range(k - 1):
        cur = [0] * (len(h) + b - 1)
        for a, va in enumerate(h):
            for d in range(b):
                cur[a + d] += va
        h = cur
    return h


def constraint(b, N):
    k = N // (b - 1) + 1
    h = dist(b, k)
    pref = [0]
    for v in h:
        pref.append(pref[-1] + v)
    top = (b - 1) * k
    return sum(h[a] * pref[min(N - a, top) + 1] for a in range(0, min(N, top) + 1))


print("base 2 (exact): c = 4/sqrt(pi) =", f"{4 / sqrt(pi):.7f}\n")
for b_str in sorted(DATA, key=int):
    b = int(b_str)
    pts = sorted((int(N), int(q)) for N, q in DATA[b_str].items())
    cs = [(N, qv / constraint(b, N) * sqrt(N)) for N, qv in pts]
    crest = max(cs, key=lambda t: t[1])
    print(f"base {b}: {len(pts)} peak points, N up to {pts[-1][0]}")
    for N, c in cs[-4:]:
        print(f"    c_{N} = {c:.7f}")
    print(f"    crest: c_{crest[0]} = {crest[1]:.7f}\n")

print("sqrt(15) =", f"{sqrt(15):.7f}", "(refuted: above the base-10 crest)")
