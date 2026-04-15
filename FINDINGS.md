# Digit-sum reachability — findings

## The problem

Starting from `(0, 0)` on the integer lattice, 4-connected moves (up/down/left/right). A cell `(x, y)` is permitted iff

```
digitSum(|x|) + digitSum(|y|) <= N
```

Count all cells reachable from the origin via a path of permitted cells. Canonical instance: `N = 19`, base 10.

## Answer for N = 19

- **Reachable points: 102,485**
- Bounding box: `x, y in [-298, 298]` — stops exactly at the first axis-cliff (ds(299) = 20).
- By symmetry in the sign of each coordinate, the shape is 4-fold symmetric about the origin.

See `digitsum_reach.png`.

## The shape

- Outer boundary is a diamond from the `ds(x) + ds(y) <= N` constraint (digit sum is roughly linear in `|x| + |y|` for small values).
- Large rectangular "death zones" where digit-sum configurations exceed N (e.g. around `(±150, ±150)`, `(±200, 0)`, `(0, ±200)`).
- Internal "tri-force" nested-triangle pattern in each quadrant from the self-similar structure of digit sums at powers of ten.

## Base sensitivity

Rendered comparable reachable regions for bases 2, 3, 4, 5, 10, with N chosen so each has axis reach ~±250–500 (see `digitsum_strip.png`):

| base | N  | points   | axis reach |
|-----:|---:|---------:|-----------:|
|   2  |  8 |  300,285 |       ±510 |
|   3  | 10 |  262,941 |       ±484 |
|   4  | 12 |  288,685 |       ±510 |
|   5  | 14 |  294,765 |       ±498 |
|  10  | 19 |  102,485 |       ±298 |

Base 2 is densest and closest to a solid diamond — carries happen every step, so cliffs are finely woven. As base grows, carry events become rarer but more violent, punching bigger holes. Base 10 is the noisiest member of this family.

Base 2 specifically connects to known theory (popcount, Kummer's theorem on binomial coefficients mod 2, giving a clean Sierpiński triangle). Base 10 has no known closed form.

## BFS depth (a wrong turn, kept for the record)

Colored each reached cell by geodesic distance from origin (`digitsum_depth.png`). Also computed detour := geodesic − `|x| + |y|`.

Observation: **max detour = 0** across all reached cells. Every reached cell sits on a monotone staircase from the origin.

First conclusion (wrong): interpreted this as the reachable set matching the full constraint set `{(x,y) : ds(|x|) + ds(|y|) <= N}` — i.e. no connectivity losses.

This was incorrect. Detour = 0 only describes cells that *were* reached; it says nothing about whether cells exist that satisfy the digit-sum constraint but are unreachable. The scanline analysis below exposed the error.

## Scanline decomposition and the correct picture

Each row `y` in the 2D picture is the 1D set `{x : ds(|x|) <= N − ds(|y|)}` — i.e. the 2D problem factors into the outer product of a 1D "digit-sum threshold" family indexed by budget K = 0…N (`digitsum_scanlines.png`, `digitsum_signal.png`).

Counting the Cartesian product over the bounding box gave **169,221 constraint-satisfying cells**, against BFS's 102,485. **Gap: 66,736 cells (~39%) that satisfy the digit-sum constraint but are unreachable from the origin.**

These are genuine islands. Example: `(300, 0)` has ds = 3 ≤ 19 but the only way to it along the x-axis passes through `(299, 0)` with ds = 20, which is forbidden. Reachability = constraint set *minus* all cells cut off past a carry-cliff.

Two tangled structures:

1. **The constraint set** — clean Cartesian product, plausibly admits a generating-function description.
2. **The reachable subset** — the constraint set minus island cells cut off by carry-cliffs. This is the hard part.

## The staircase in N

For each N from 1 through 28, computed BFS reach and constraint-in-bbox count (`digitsum_ratio.png`, `digitsum_ratio_extended.png`):

| N  | BFS        | constraint | ratio  | bbox  |
|---:|-----------:|-----------:|-------:|------:|
|  8 |        145 |        145 | 1.0000 |    ±8 |
|  9 |        505 |        649 | 0.7781 |   ±18 |
| 11 |      2,025 |      2,765 | 0.7324 |   ±38 |
| 17 |     14,785 |     18,265 | 0.8095 |   ±98 |
| 18 |     47,905 |     73,885 | 0.6484 |  ±198 |
| 19 |    102,485 |    166,973 | 0.6138 |  ±298 |
| 20 |    181,533 |    297,693 | 0.6098 |  ±398 |
| 26 |  1,309,537 |  1,885,501 | 0.6945 |  ±998 |
| 27 |  4,216,357 |  7,552,009 | 0.5583 | ±1998 |
| 28 |  9,006,221 | 17,005,469 | 0.5296 | ±2998 |

The ratio curve is a **descending Cantor-like staircase** with cliffs at `N = 9, 18, 27` — precisely the N values where the reachable region first crosses into a new decade on an axis:

| cliff | N  | peak before | trough after | drop  |
|------:|---:|------------:|-------------:|------:|
|   1   |  9 |       1.00  |        0.73  | 0.27  |
|   2   | 18 |       0.81  |        0.61  | 0.20  |
|   3   | 27 |       0.69  |        0.53  | 0.16  |

- Envelopes (peak and trough) are both monotonically descending.
- Drops shrink (0.27 → 0.20 → 0.16, ratios ~0.74, 0.80) — convergent.
- Within each decade: topology fixed, holes fill in monotonically as N rises by 1.
- Predicted next cliff at `N = 36` (first budget reaching past x = 9999, ds = 36).
- Suggests an asymptotic ratio as N → ∞, likely in 0.3–0.5.

## Peak vs trough comparison

Rendered the first-of-decade (trough) and last-of-decade (peak) shapes side by side for decades 2 and 3 (`digitsum_peak_trough.png`):

- Decade 2: N = 11 (trough, 2,025 pts) vs N = 17 (peak, 14,785 pts)
- Decade 3: N = 20 (trough, 181,533 pts) vs N = 26 (peak, 1,309,537 pts)

Trough shapes are skeletal — bounding box has just jumped a decade and most of the new space is empty. Peak shapes are near-solid — 6 more units of budget have filled in almost every hole.

**N = 11 trough and N = 20 trough are the same shape at different scales.** Overlay the N = 11 image onto the central quadrant of N = 20 and they match. Same for N = 17 and N = 26. This is the recursion made visible: each new decade adds an outer scaled copy of the previous decade's pattern.

## Why a closed form stays slippery

The natural coordinates `(⌊N / 9⌋, N mod 9)` are clearly the right frame, but the recursion isn't clean. Each new decade doesn't just *embed* the previous decade's pattern — the outer layer's reachability depends on which cells of the inner layer sit on the carry boundary. Outer and inner layers interact.

Pure self-similar fractals (Sierpiński, Cantor) avoid this because their recursions are multiplicative with no threshold. The digit-sum problem has both multiplicative self-similarity *and* an additive threshold, and the two interact. That combination is why the pencil-and-paper approach hits a wall in a way that *feels* like it shouldn't.

Likely route to a formula: a recurrence indexed by `⌊N / 9⌋` with a correction term for the carry-boundary interaction — not a single closed expression.

## Scripts

All in this directory. Each writes its output PNG(s) into cwd.

| script                      | produces                                                 |
|-----------------------------|----------------------------------------------------------|
| `digitsum_reach.py`         | `digitsum_reach.png` — 2D reachable set at N=19          |
| `digitsum_strip.py`         | `digitsum_strip.png` — bases 2,3,4,5,10 side by side     |
| `digitsum_depth.py`         | `digitsum_depth.png`, `digitsum_detour.png` — BFS distance + detour |
| `digitsum_scanlines.py`     | `digitsum_signal.png`, `digitsum_scanlines.png` — 1D decomposition |
| `digitsum_ratio.py`         | `digitsum_ratio.png` — ratio analysis N=1..22            |
| `digitsum_ratio_extended.py`| `digitsum_ratio_extended.png` — extended to N=28         |
| `digitsum_peak_trough.py`   | `digitsum_peak_trough.png` — per-decade peak vs trough   |

Run with `.venv-digitsum/bin/python digitsum_<name>.py`.
