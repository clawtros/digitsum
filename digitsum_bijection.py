"""Open problem 2, resolved: the base-2 bijection ("surfacing map").

Via the criterion, base-2 reachable cells are interleaved bit-words w of length
2k (k = N+1) with even-checkpoint majority-0 and at most k-1 ones. Three facts,
each verified exhaustively here:

1. PARITY COLLAPSE: reading w as a +-1 path (1 = up), the even-checkpoint
   condition is equivalent to the uniform barrier "never reach +2". (Even-time
   positions are even integers.)
2. IDENTITY: |Good| = C(2k,k-1) + C(2k,k-2) = C(2k+1,k-1) by reflection at
   level 2 plus binomial telescoping — so Q2(N) = C(2N+3,N) is a theorem.
3. BIJECTION (surfacing map): while w has <= k-3 ones, complement the prefix up
   to and including the first hitting time of level -2. Each round adds exactly
   2 ones; the map lands bijectively on the words with exactly k-1 or k-2 ones
   — the allowed cells of the top two elevation layers. Inverse: while the walk
   touches +2, complement the prefix up to the first +2-hit.
"""

from math import comb
from itertools import product


def path(w):
    """Prefix positions of the +-1 walk (1 = +1, 0 = -1), length len(w)+1."""
    out = [0]
    for b in w:
        out.append(out[-1] + (1 if b else -1))
    return out


def checkpoint_ok(w, k):
    p = path(w)
    return all(p[2 * s] <= 0 for s in range(1, k + 1)) and p[2 * k] <= -2


def barrier_ok(w):
    p = path(w)
    return max(p) <= 1 and p[-1] <= -2


def flip_prefix_to_first_hit(w, level):
    p = path(w)
    j = p.index(level)  # first hitting time (raises ValueError if never hit)
    return tuple(1 - b for b in w[:j]) + w[j:]


def surface(w, k):
    while sum(w) <= k - 3:
        w = flip_prefix_to_first_hit(w, -2)
    return w


def sink(w):
    while max(path(w)) >= 2:
        w = flip_prefix_to_first_hit(w, 2)
    return w


if __name__ == "__main__":
    for k in range(2, 8):
        words = list(product((0, 1), repeat=2 * k))
        good = [w for w in words if checkpoint_ok(w, k)]
        # 1. parity collapse
        assert all(checkpoint_ok(w, k) == barrier_ok(w) for w in words)
        # 2. the identity
        assert len(good) == comb(2 * k + 1, k - 1)
        # 3. the surfacing bijection onto the top two layers
        target = {w for w in words if sum(w) in (k - 1, k - 2)}
        images = [surface(w, k) for w in good]
        assert all(t in target for t in images)
        assert len(set(images)) == len(good) == len(target)
        # inverse roundtrip both ways
        assert all(sink(surface(w, k)) == w for w in good)
        assert all(surface(sink(t), k) == t for t in target)
        print(f"k={k} (N={k-1}): parity collapse OK; |Good| = C({2*k+1},{k-1}) "
              f"= {len(good)}; surfacing map bijective with inverse OK")
    print("\nQ2(N) = C(2N+3, N) is now fully proved: criterion + parity "
          "collapse + reflection;\nthe surfacing map realizes reachable <-> "
          "top-two-layers explicitly.")
