"""The gastank solver: exact hierarchical computation of the base-10 reachable count.

The quadrant is one giant tank T_k(N): a [0,10^k)^2 block where a cell is allowed
iff its two k-digit digit-sums total <= budget. Every tank splits into a 10x10
grid of child tanks, the child at digit position (i,j) having budget K-i-j —
digit sums are carry-free inside a block, so the structure is exactly
self-similar. Carries are the walls between sibling tanks (budgets always differ
by 1 across a seam), and flow passes tank-to-tank over weirs on shared edges,
rightward and upward only (the monotone lemma).

flood() floods one tank from entry patterns ("fluid levels") on its left/bottom
edges and returns (cell count, exit patterns on right/top edges). The wetting
fronts are fractal — their interval count grows ~9x per scale — but a front is
only ever split on child-tank boundaries, so patterns are hash-consed: a scale-k
front is an interned 10-tuple of scale-(k-1) front ids, stored once in a DAG and
compared by id. The number of DISTINCT tank states (scale, budget, entries) stays
in the hundreds per scale — that finiteness is the transfer matrix.

Usage: digitsum_tanks.py [MAXN]   (default 60; validates N<=36 against DP/BFS)
"""

import sys
import time
from digitsum_lib import axis_bound

# ---- hash-consed edge patterns -------------------------------------------
# A pattern is a subset of [0, 10^k) rows, stored as an interned node id.
# k=1 payload: 10-bit mask. k>=2 payload: tuple of 10 child (k-1) pattern ids.

_payload = []
_minpos = []  # minimum set position, or None if the pattern is empty
_intern = {}


def _mk(k, payload):
    key = (k, payload)
    i = _intern.get(key)
    if i is not None:
        return i
    if k == 1:
        mp = (payload & -payload).bit_length() - 1 if payload else None
    else:
        mp = None
        for c, child in enumerate(payload):
            if _minpos[child] is not None:
                mp = c * 10 ** (k - 1) + _minpos[child]
                break
    i = len(_payload)
    _payload.append(payload)
    _minpos.append(mp)
    _intern[key] = i
    return i


def pat_empty(k):
    return _mk(1, 0) if k == 1 else _mk(k, (pat_empty(k - 1),) * 10)


def pat_point0(k):
    """Just row 0 — the origin seed."""
    if k == 1:
        return _mk(1, 1)
    return _mk(k, (pat_point0(k - 1),) + (pat_empty(k - 1),) * 9)


_suffix_memo = {}


def pat_suffix(k, lo):
    """Rows [lo, 10^k) — a wedge front."""
    key = (k, lo)
    hit = _suffix_memo.get(key)
    if hit is not None:
        return hit
    if k == 1:
        out = _mk(1, ((1 << 10) - (1 << lo)) if lo < 10 else 0)
    else:
        S1 = 10 ** (k - 1)
        c0 = lo // S1
        empty, full = pat_empty(k - 1), pat_suffix(k - 1, 0)
        kids = tuple(
            empty if c < c0
            else pat_suffix(k - 1, lo - c0 * S1) if c == c0
            else full
            for c in range(10)
        )
        out = _mk(k, kids)
    _suffix_memo[key] = out
    return out


# ---- the solver -----------------------------------------------------------

_memo = {}
_memo1 = {}


def _flood1(K, elmask, ebmask):
    """Base tank: 10x10 triangle u+v <= K, entry masks on left/bottom edges."""
    K = min(K, 18)
    key = (K, elmask, ebmask)
    hit = _memo1.get(key)
    if hit is not None:
        return hit
    reach = [[False] * 10 for _ in range(10)]
    count = 0
    for v in range(10):
        for u in range(10):
            if u + v > K:
                continue
            if ((u == 0 and elmask >> v & 1) or (v == 0 and ebmask >> u & 1)
                    or (u > 0 and reach[v][u - 1]) or (v > 0 and reach[v - 1][u])):
                reach[v][u] = True
                count += 1
    ermask = sum(1 << v for v in range(10) if reach[v][9])
    etmask = sum(1 << u for u in range(10) if reach[9][u])
    out = (count, _mk(1, ermask), _mk(1, etmask))
    _memo1[key] = out
    return out


def flood(k, K, EL, EB):
    """Flood tank of size 10^k, budget K, from left/bottom entry patterns.
    Returns (flooded cell count, right-edge exits, top-edge exits)."""
    if K < 0 or (_minpos[EL] is None and _minpos[EB] is None):
        e = pat_empty(k)
        return 0, e, e
    if k == 1:
        return _flood1(K, _payload[EL], _payload[EB])
    if K >= 18 * k:
        # Tank fully allowed: flood is the union of two wedges above/right of
        # the lowest entries.
        S = 10 ** k
        h, w = _minpos[EL], _minpos[EB]
        count = 0
        if h is not None:
            count += S * (S - h)
        if w is not None:
            count += (S - w) * (h if h is not None else S)
        ER = pat_suffix(k, 0) if w is not None else pat_suffix(k, h)
        ET = pat_suffix(k, 0) if h is not None else pat_suffix(k, w)
        return count, ER, ET
    key = (k, K, EL, EB)
    hit = _memo.get(key)
    if hit is not None:
        return hit
    ELk, EBk = _payload[EL], _payload[EB]
    er = {}  # child right-edge exits
    et = {}  # child top-edge exits
    total = 0
    for j in range(10):
        for i in range(10):
            el = ELk[j] if i == 0 else er[(i - 1, j)]
            eb = EBk[i] if j == 0 else et[(i, j - 1)]
            cnt, r, t = flood(k - 1, K - i - j, el, eb)
            er[(i, j)], et[(i, j)] = r, t
            total += cnt
    out = (total,
           _mk(k, tuple(er[(9, j)] for j in range(10))),
           _mk(k, tuple(et[(i, 9)] for i in range(10))))
    _memo[key] = out
    return out


def quadrant(N):
    """Quadrant reachable count: flood the top-level tank from the origin."""
    k = N // 9 + 1  # 10^k covers the axis bound
    count, _, _ = flood(k, N, pat_point0(k), pat_empty(k))
    return count


# f(N) for N=1..36 from BFS (digitsum_monotone.py) to validate against.
KNOWN_F = [5, 13, 25, 41, 61, 85, 113, 145, 505, 1121, 2025, 3245, 4805, 6725,
           9021, 11705, 14785, 47905, 102485, 181533, 287881, 424129, 592597,
           795285, 1033841, 1309537, 4216357, 9006221, 15961125, 25353625,
           37441397, 52462177, 70629201, 92127245, 117109345, 377329873]

if __name__ == "__main__":
    MAXN = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    print(f"{'N':>4} {'digits(Q)':>9} {'Q(N)':>24} {'states':>8} {'sec':>7}")
    for N in range(1, MAXN + 1):
        t0 = time.time()
        q = quadrant(N)
        f = 4 * q - 4 * axis_bound(N) + 1
        if N <= len(KNOWN_F):
            assert f == KNOWN_F[N - 1], (N, f, KNOWN_F[N - 1])
            tag = " ok"
        else:
            tag = ""
        qs = f"{q:,}" if q < 10 ** 24 else f"...{q % 10**18:018d}"
        print(f"{N:>4} {len(str(q)):>9} {qs:>24} {len(_memo):>8,}"
              f" {time.time()-t0:>7.3f}{tag}", flush=True)
