"""Shared helpers for the digit-sum reachability scripts."""

from collections import deque
import numpy as np

_NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def ds(v, base=10):
    """Digit sum of |v| in the given base."""
    v = abs(v)
    s = 0
    while v:
        s += v % base
        v //= base
    return s


def bfs(N, base=10):
    """Set-based BFS from origin. Returns (points: set[(x,y)], bbox: (xmin,xmax,ymin,ymax))."""
    seen = {(0, 0)}
    q = deque([(0, 0)])
    xmin = xmax = ymin = ymax = 0
    while q:
        x, y = q.popleft()
        if x < xmin: xmin = x
        if x > xmax: xmax = x
        if y < ymin: ymin = y
        if y > ymax: ymax = y
        for dx, dy in _NEIGHBORS:
            nx, ny = x + dx, y + dy
            if (nx, ny) in seen: continue
            if ds(nx, base) + ds(ny, base) > N: continue
            seen.add((nx, ny))
            q.append((nx, ny))
    return seen, (xmin, xmax, ymin, ymax)


def bfs_distances(N, base=10):
    """BFS returning geodesic distances. Returns (dist: dict[(x,y)->int], bbox, max_d)."""
    dist = {(0, 0): 0}
    q = deque([(0, 0)])
    xmin = xmax = ymin = ymax = 0
    max_d = 0
    while q:
        x, y = q.popleft()
        d = dist[(x, y)]
        if d > max_d: max_d = d
        if x < xmin: xmin = x
        if x > xmax: xmax = x
        if y < ymin: ymin = y
        if y > ymax: ymax = y
        for dx, dy in _NEIGHBORS:
            nx, ny = x + dx, y + dy
            if (nx, ny) in dist: continue
            if ds(nx, base) + ds(ny, base) > N: continue
            dist[(nx, ny)] = d + 1
            q.append((nx, ny))
    return dist, (xmin, xmax, ymin, ymax), max_d


def axis_bound(N, base=10):
    """Smallest x > 0 with ds(x) > N — this is also the positive axis reach + 1.
    Used to size a numpy grid conservatively."""
    bound = 10
    while True:
        for x in range(bound):
            if ds(x, base) > N:
                return x
        bound *= 10
        if bound > 10_000_000:
            raise RuntimeError("axis bound exploded")


def bfs_grid(N, base=10):
    """Grid-based BFS. Returns (visited: np.ndarray[bool], G: int) where the grid is
    (2G+1)x(2G+1) and origin sits at (G, G) in array-(row, col) coords matching (y, x)."""
    G = axis_bound(N, base)
    size = 2 * G + 1
    visited = np.zeros((size, size), dtype=bool)
    ox, oy = G, G
    visited[oy, ox] = True
    q = deque([(0, 0)])
    while q:
        x, y = q.popleft()
        for dx, dy in _NEIGHBORS:
            nx, ny = x + dx, y + dy
            gx, gy = ox + nx, oy + ny
            if gx < 0 or gx >= size or gy < 0 or gy >= size: continue
            if visited[gy, gx]: continue
            if ds(nx, base) + ds(ny, base) > N: continue
            visited[gy, gx] = True
            q.append((nx, ny))
    return visited, G


def monotone_quadrant(N, base=10):
    """Directed-reachability DP in the first quadrant: R(x,y) = allowed(x,y) AND
    (R(x-1,y) OR R(x,y-1)), swept row by row with vectorized run-flooding.
    Empirically (verified vs BFS for N=1..22 base 10 and bases 2..5) this equals
    true reachability — the monotone-staircase lemma. ~100x faster than BFS.
    Returns (quadrant_count, axis_x, axis_y): cells with x,y >= 0, and the
    reachable cell counts on the y=0 row and x=0 column."""
    G = axis_bound(N, base)
    dsv = np.fromiter((ds(v, base) for v in range(G)), dtype=np.int32, count=G)
    R_prev = None
    q_count = axis_x = axis_y = 0
    for y in range(G):
        allowed = (dsv + dsv[y]) <= N
        if y == 0:
            seeds = np.zeros(G, dtype=bool)
            seeds[0] = allowed[0]
        else:
            seeds = R_prev & allowed
        # A cell is reachable iff its maximal allowed run contains a seed at or
        # left of it. Runs are identified by the count of blocked cells before x.
        run_id = np.cumsum(~allowed)
        last_seed_run = np.maximum.accumulate(np.where(seeds, run_id, -1))
        R = allowed & (last_seed_run == run_id)
        c = int(R.sum())
        q_count += c
        if y == 0:
            axis_x = c
        if R[0]:
            axis_y += 1
        R_prev = R
    return q_count, axis_x, axis_y


def monotone_reach_count(N, base=10):
    """Full-plane reachable count via the monotone DP + 4-fold symmetry."""
    q, ax, ay = monotone_quadrant(N, base)
    return 4 * q - 2 * ax - 2 * ay + 1


def constraint_in_bbox(N, bbox, base=10):
    """Count (x,y) in bbox with ds(|x|)+ds(|y|) <= N, via 1D factorization."""
    xmin, xmax, ymin, ymax = bbox
    xs = np.arange(xmin, xmax + 1)
    ys = np.arange(ymin, ymax + 1)
    dsx = np.fromiter((ds(int(v), base) for v in xs), dtype=np.int32, count=len(xs))
    dsy = np.fromiter((ds(int(v), base) for v in ys), dtype=np.int32, count=len(ys))
    ex = np.bincount(dsx[dsx <= N], minlength=N + 1)
    ey = np.bincount(dsy[dsy <= N], minlength=N + 1)
    total = 0
    for a in range(N + 1):
        for b in range(N + 1 - a):
            total += int(ex[a]) * int(ey[b])
    return total


def turbo(t):
    """Polynomial approx of the turbo colormap. t in [0,1] (array ok) -> RGB uint8."""
    t = np.clip(np.asarray(t, dtype=np.float64), 0.0, 1.0)
    r = 0.13572138 + 4.61539260*t - 42.66032258*t**2 + 132.13108234*t**3 - 152.94239396*t**4 + 59.28637943*t**5
    g = 0.09140261 + 2.19418839*t + 4.84296658*t**2 - 14.18503333*t**3 + 4.27729857*t**4 + 2.82956604*t**5
    b = 0.10667330 + 12.64194608*t - 60.58204836*t**2 + 110.36276771*t**3 - 89.90310912*t**4 + 27.34824973*t**5
    rgb = np.stack([r, g, b], axis=-1)
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def turbo_scalar(t):
    """Same as turbo but for a single float; returns (r, g, b) 0..255 tuple."""
    arr = turbo(np.array([t]))[0]
    return (int(arr[0]), int(arr[1]), int(arr[2]))


def load_font(size):
    """Menlo if available, else PIL default."""
    from PIL import ImageFont
    try:
        return ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", size)
    except Exception:
        return ImageFont.load_default()
