"""Spectral analysis of the decade transfer map (first expedition).

Instruments the flood recursion to extract the census of tank states in the top
SHALLOW scales, normalized as (depth, d = 9k - K, sig(EL), sig(EB)) where d is
the tank's offset from the digit-sum mean and sig is a scale-free recursive
front signature truncated at depth SIG_T. Then:
  1. censuses across peak-line N   -> exactly N-independent (fixed point ATTAINED)
  2. transition-closure test       -> classes close (<=24 per d); ambiguity only
                                      at d <= -38 (deeply submerged, truncatable)
  3. truncated transfer matrix     -> spectrum; lam2/lam1 rises with truncation
                                      depth toward the observed rho ~ 0.91

Findings (2026-07): fixed point exact at depths 0-4 for all N tested (116-404);
active band is one-sided (no active tank has d > 1); lam1 -> ~95 (toward 100),
lam2/lam1 = 0.86 at the deepest data-supported truncation, trending toward
rho ~ 0.91 but limited by SHALLOW=6 instrumentation depth. The rigorous version
needs the Markov-additive treatment of the diffusive d-band (the power-law
corrections are its continuum spectrum).
"""
import sys
sys.path.insert(0, "/Users/adam/projects/digitsum")

SHALLOW = 6   # instrument this many scales below the top
SIG_T = 3     # front-signature truncation depth

# ---- instrumented copy of the base-10 solver ----
_payload, _minpos, _intern = [], [], {}

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
    if k == 1:
        return _mk(1, 1)
    return _mk(k, (pat_point0(k - 1),) + (pat_empty(k - 1),) * 9)

_suffix = {}
def pat_suffix(k, lo):
    key = (k, lo)
    if key in _suffix:
        return _suffix[key]
    if k == 1:
        out = _mk(1, ((1 << 10) - (1 << lo)) if lo < 10 else 0)
    else:
        S1 = 10 ** (k - 1)
        c0 = lo // S1
        e, f = pat_empty(k - 1), pat_suffix(k - 1, 0)
        out = _mk(k, tuple(e if c < c0 else pat_suffix(k - 1, lo - c0 * S1) if c == c0 else f
                           for c in range(10)))
    _suffix[key] = out
    return out

_memo, _memo1 = {}, {}
CHILDREN = {}   # memo key -> list of child memo keys (shallow layers only)
K_TOP = 0

def _flood1(K, elmask, ebmask):
    K = min(K, 18)
    key = (K, elmask, ebmask)
    if key in _memo1:
        return _memo1[key]
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
    out = (count,
           _mk(1, sum(1 << v for v in range(10) if reach[v][9])),
           _mk(1, sum(1 << u for u in range(10) if reach[9][u])))
    _memo1[key] = out
    return out

def flood(k, K, EL, EB):
    if K < 0 or (_minpos[EL] is None and _minpos[EB] is None):
        e = pat_empty(k)
        return 0, e, e
    if k == 1:
        return _flood1(K, _payload[EL], _payload[EB])
    if K >= 18 * k:
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
    if key in _memo:
        return _memo[key]
    shallow = k > K_TOP - SHALLOW
    kids = [] if shallow else None
    ELk, EBk = _payload[EL], _payload[EB]
    er, et = {}, {}
    total = 0
    for j in range(10):
        for i in range(10):
            el = ELk[j] if i == 0 else er[(i - 1, j)]
            eb = EBk[i] if j == 0 else et[(i, j - 1)]
            ck, cK = k - 1, K - i - j
            cnt, r, t = flood(ck, cK, el, eb)
            if shallow and ck >= 2 and 0 <= cK < 18 * ck and (
                    _minpos[el] is not None or _minpos[eb] is not None):
                kids.append((ck, cK, el, eb))  # active memoized child
            er[(i, j)], et[(i, j)] = r, t
            total += cnt
    out = (total,
           _mk(k, tuple(er[(9, j)] for j in range(10))),
           _mk(k, tuple(et[(i, 9)] for i in range(10))))
    _memo[key] = out
    if shallow:
        CHILDREN[key] = kids
    return out


def sig(front, t=SIG_T):
    """Scale-free recursive front signature, truncated at depth t."""
    if _minpos[front] is None:
        return "0"
    k = 1
    # payload is mask (k=1) or tuple; distinguish by type
    p = _payload[front]
    if isinstance(p, int):
        return f"m{p}"
    if t == 0:
        return "*"
    return "(" + ",".join(sig(c, t - 1) for c in p) + ")"


def census(N):
    global K_TOP
    for d in (_payload, _minpos):
        d.clear()
    for d in (_intern, _suffix, _memo, _memo1, CHILDREN):
        d.clear()
    k = N // 9 + 1
    K_TOP = k
    flood(k, N, pat_point0(k), pat_empty(k))
    top = (k, N, pat_point0(k), pat_empty(k))
    mult = {top: 1}
    # top-down multiplicity over shallow layers (order by k desc)
    for key in sorted(CHILDREN, key=lambda x: -x[0]):
        m = mult.get(key, 0)
        if not m:
            continue
        for ck in CHILDREN[key]:
            if ck in CHILDREN or ck[0] > K_TOP - SHALLOW:
                mult[ck] = mult.get(ck, 0) + m
    # normalized census per depth
    out = {}
    for (kk, K, EL, EB), m in mult.items():
        depth = K_TOP - kk
        if depth >= SHALLOW - 1:
            continue
        state = (9 * kk - K, sig(EL), sig(EB))
        out.setdefault(depth, {}).setdefault(state, 0)
        out[depth][state] += m
    return out


if __name__ == "__main__":
    import numpy as np

    results = {}
    for q in (12, 20, 28):
        N = 9 * q + 8
        results[N] = census(N)
        sizes = {s: (len(v), sum(v.values())) for s, v in sorted(results[N].items())}
        print(f"N={N}: depth -> (distinct states, total tanks): {sizes}", flush=True)

    Ns = list(results)
    print("\ncensus stabilization across N (exact match of normalized census):")
    for depth in range(SHALLOW - 1):
        row = ["==" if results[a].get(depth) == results[b].get(depth) else "!="
               for a, b in zip(Ns, Ns[1:])]
        print(f"  depth {depth}: " + "  ".join(
            f"{a}vs{b}:{r}" for (a, b), r in zip(zip(Ns, Ns[1:]), row)))

    # closure test + transfer-matrix spectrum on the last N's transitions
    def norm(key):
        k, K, EL, EB = key
        return (9 * k - K, sig(EL), sig(EB))

    prof, ambiguous = {}, set()
    for key, kids in CHILDREN.items():
        s = norm(key)
        p = tuple(sorted(norm(c) for c in kids))
        if s in prof and prof[s] != p:
            ambiguous.add(s)
        prof[s] = p
    print(f"\nclosure: {len(prof)} classes, {len(ambiguous)} ambiguous "
          f"(all at d <= {max((s[0] for s in ambiguous), default='-')})")

    print("\ntruncated transfer-matrix spectrum (tank-count operator):")
    for D in (15, 25, 35, 44):
        states = sorted(s for s in prof if s not in ambiguous and s[0] >= -D)
        idx = {s: i for i, s in enumerate(states)}
        M = np.zeros((len(states), len(states)))
        for s in states:
            for c in prof[s]:
                if c in idx:
                    M[idx[c], idx[s]] += 1
        ev = sorted(np.linalg.eigvals(M), key=lambda z: -abs(z))
        print(f"  D={D:>2}: {len(states):>3} states  lam1={abs(ev[0]):8.4f}  "
              f"lam2={abs(ev[1]):8.4f}  lam2/lam1={abs(ev[1])/abs(ev[0]):.4f}")
    print("\nobserved per-decade correction ratio in c_N: rho ~ 0.91")
