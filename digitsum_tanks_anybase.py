"""Base-general gastank solver: same hash-consed flood recursion as
digitsum_tanks.py, parameterized by base b. Tanks split into b x b children,
child (i,j) has budget K-i-j, walls carry (b-1) per scale, k=1 base tank is a
b x b triangle."""


class TankSolver:
    def __init__(self, base):
        self.b = base
        self.top = 2 * (base - 1)  # max digit-sum of a cell in a scale-1 tank
        self._payload = []
        self._minpos = []
        self._intern = {}
        self._suffix = {}
        self._memo = {}
        self._memo1 = {}

    def _mk(self, k, payload):
        key = (k, payload)
        i = self._intern.get(key)
        if i is not None:
            return i
        if k == 1:
            mp = (payload & -payload).bit_length() - 1 if payload else None
        else:
            mp = None
            for c, child in enumerate(payload):
                if self._minpos[child] is not None:
                    mp = c * self.b ** (k - 1) + self._minpos[child]
                    break
        i = len(self._payload)
        self._payload.append(payload)
        self._minpos.append(mp)
        self._intern[key] = i
        return i

    def pat_empty(self, k):
        return self._mk(1, 0) if k == 1 else self._mk(k, (self.pat_empty(k - 1),) * self.b)

    def pat_point0(self, k):
        if k == 1:
            return self._mk(1, 1)
        return self._mk(k, (self.pat_point0(k - 1),) + (self.pat_empty(k - 1),) * (self.b - 1))

    def pat_suffix(self, k, lo):
        key = (k, lo)
        hit = self._suffix.get(key)
        if hit is not None:
            return hit
        b = self.b
        if k == 1:
            out = self._mk(1, ((1 << b) - (1 << lo)) if lo < b else 0)
        else:
            S1 = b ** (k - 1)
            c0 = lo // S1
            empty, full = self.pat_empty(k - 1), self.pat_suffix(k - 1, 0)
            kids = tuple(
                empty if c < c0
                else self.pat_suffix(k - 1, lo - c0 * S1) if c == c0
                else full
                for c in range(b)
            )
            out = self._mk(k, kids)
        self._suffix[key] = out
        return out

    def _flood1(self, K, elmask, ebmask):
        b = self.b
        K = min(K, self.top)
        key = (K, elmask, ebmask)
        hit = self._memo1.get(key)
        if hit is not None:
            return hit
        reach = [[False] * b for _ in range(b)]
        count = 0
        for v in range(b):
            for u in range(b):
                if u + v > K:
                    continue
                if ((u == 0 and elmask >> v & 1) or (v == 0 and ebmask >> u & 1)
                        or (u > 0 and reach[v][u - 1]) or (v > 0 and reach[v - 1][u])):
                    reach[v][u] = True
                    count += 1
        ermask = sum(1 << v for v in range(b) if reach[v][b - 1])
        etmask = sum(1 << u for u in range(b) if reach[b - 1][u])
        out = (count, self._mk(1, ermask), self._mk(1, etmask))
        self._memo1[key] = out
        return out

    def flood(self, k, K, EL, EB):
        if K < 0 or (self._minpos[EL] is None and self._minpos[EB] is None):
            e = self.pat_empty(k)
            return 0, e, e
        if k == 1:
            return self._flood1(K, self._payload[EL], self._payload[EB])
        if K >= self.top * k:
            S = self.b ** k
            h, w = self._minpos[EL], self._minpos[EB]
            count = 0
            if h is not None:
                count += S * (S - h)
            if w is not None:
                count += (S - w) * (h if h is not None else S)
            ER = self.pat_suffix(k, 0) if w is not None else self.pat_suffix(k, h)
            ET = self.pat_suffix(k, 0) if h is not None else self.pat_suffix(k, w)
            return count, ER, ET
        key = (k, K, EL, EB)
        hit = self._memo.get(key)
        if hit is not None:
            return hit
        b = self.b
        ELk, EBk = self._payload[EL], self._payload[EB]
        er, et = {}, {}
        total = 0
        for j in range(b):
            for i in range(b):
                el = ELk[j] if i == 0 else er[(i - 1, j)]
                eb = EBk[i] if j == 0 else et[(i, j - 1)]
                cnt, r, t = self.flood(k - 1, K - i - j, el, eb)
                er[(i, j)], et[(i, j)] = r, t
                total += cnt
        out = (total,
               self._mk(k, tuple(er[(b - 1, j)] for j in range(b))),
               self._mk(k, tuple(et[(i, b - 1)] for i in range(b))))
        self._memo[key] = out
        return out

    def quadrant(self, N):
        k = N // (self.b - 1) + 1
        count, _, _ = self.flood(k, N, self.pat_point0(k), self.pat_empty(k))
        return count


if __name__ == "__main__":
    from math import comb
    from digitsum_lib import monotone_reach_count, axis_bound
    import digitsum_tanks

    # validation 1: base 2 vs exact closed form
    s2 = TankSolver(2)
    for N in range(1, 26):
        assert s2.quadrant(N) == comb(2 * N + 3, N), N
    print("base 2 vs closed form C(2N+3,N), N=1..25: OK", flush=True)

    # validation 2: base 10 vs the dedicated base-10 solver
    s10 = TankSolver(10)
    for N in range(1, 101):
        assert s10.quadrant(N) == digitsum_tanks.quadrant(N), N
    print("base 10 vs digitsum_tanks, N=1..100: OK", flush=True)

    # validation 3: bases 3,4,5 vs monotone DP (full-plane comparison)
    for b in (3, 4, 5):
        s = TankSolver(b)
        for N in range(1, 13):
            f_tank = 4 * s.quadrant(N) - 4 * axis_bound(N, b) + 1
            f_dp = monotone_reach_count(N, b)
            assert f_tank == f_dp, (b, N, f_tank, f_dp)
        print(f"base {b} vs monotone DP, N=1..12: OK", flush=True)

    print("all validations passed (peak-line data lives in digitsum_peakdata.json)")
