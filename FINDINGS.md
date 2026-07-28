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

## BFS depth (a wrong turn — later redeemed)

Colored each reached cell by geodesic distance from origin (`digitsum_depth.png`). Also computed detour := geodesic − `|x| + |y|`.

Observation: **max detour = 0** across all reached cells. Every reached cell sits on a monotone staircase from the origin.

First conclusion (wrong): interpreted this as the reachable set matching the full constraint set `{(x,y) : ds(|x|) + ds(|y|) <= N}` — i.e. no connectivity losses.

This was incorrect. Detour = 0 only describes cells that *were* reached; it says nothing about whether cells exist that satisfy the digit-sum constraint but are unreachable. The scanline analysis below exposed the error.

The measurement itself, however, turned out to be the central structural fact of the problem — see "The monotone lemma" below. Connectivity failures are always total (islands), never partial (cells reachable only via detour).

## Scanline decomposition and the correct picture

Each row `y` in the 2D picture is the 1D set `{x : ds(|x|) <= N − ds(|y|)}` — i.e. the 2D problem factors into the outer product of a 1D "digit-sum threshold" family indexed by budget K = 0…N (`digitsum_scanlines.png`, `digitsum_signal.png`).

Counting the Cartesian product over the bounding box ±298 gives **166,973 constraint-satisfying cells**, against BFS's 102,485. **Gap: 64,488 cells (38.6%) that satisfy the digit-sum constraint but are unreachable from the origin.** (An earlier revision reported 169,221 / 66,736 — that count came from `digitsum_scanlines.py`'s ±300 working box, which includes allowed cells at ±299..300 outside the reachable bounding box.)

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
| 29 | 15,961,125 | 30,255,421 | 0.5275 | ±3998 |
| 35 | 117,109,345 | 190,327,945 | 0.6153 | ±9998 |
| 36 | 377,329,873 | 761,526,445 | 0.4955 | ±19998 |

(N ≥ 23 computed with the monotone DP, `digitsum_monotone.py` — BFS is impractical at these sizes.)

The ratio curve is a **descending Cantor-like staircase** with cliffs at `N = 9, 18, 27, 36` — precisely the N values where the reachable region first crosses into a new decade on an axis:

| cliff | N  | peak before | trough after | drop  |
|------:|---:|------------:|-------------:|------:|
|   1   |  9 |       1.00  |        0.78  | 0.22  |
|   2   | 18 |       0.81  |        0.65  | 0.16  |
|   3   | 27 |       0.69  |        0.56  | 0.14  |
|   4   | 36 |       0.62  |        0.50  | 0.12  |

- Envelopes (peak and trough) are both monotonically descending.
- Drops shrink (0.22 → 0.16 → 0.14 → 0.12) — convergent.
- The ratio minimum is *not* at the cliff step: it lands two steps into each decade (N = 11: 0.7324, N = 20: 0.6098, N = 29: 0.5275) before the fill-in overtakes the bbox jump.
- Within each decade: topology fixed, holes fill in monotonically as N rises by 1.
- Predicted cliff at `N = 36` **confirmed** (0.6153 → 0.4955, bbox ±9998 → ±19998).
- Both envelopes decay roughly geometrically (successive drops shrink by ~0.7); extrapolating puts the asymptotic ratio around **0.40–0.47**, tightening the earlier 0.3–0.5 guess.

## Peak vs trough comparison

Rendered the first-of-decade (trough) and last-of-decade (peak) shapes side by side for decades 2 and 3 (`digitsum_peak_trough.png`):

- Decade 2: N = 11 (trough, 2,025 pts) vs N = 17 (peak, 14,785 pts)
- Decade 3: N = 20 (trough, 181,533 pts) vs N = 26 (peak, 1,309,537 pts)

Trough shapes are skeletal — bounding box has just jumped a decade and most of the new space is empty. Peak shapes are near-solid — 6 more units of budget have filled in almost every hole.

**N = 11 trough and N = 20 trough are the same shape at different scales.** Overlay the N = 11 image onto the central quadrant of N = 20 and they match. Same for N = 17 and N = 26. This is the recursion made visible: each new decade adds an outer scaled copy of the previous decade's pattern.

Decade 4 continues the pattern: trough at N = 29 (ratio 0.5275), peak at N = 35 (ratio 0.6153).

## The monotone lemma (the wrong turn, redeemed)

The detour = 0 observation says more than first credited: every reachable cell is reachable by a path of exactly Manhattan length, i.e. a monotone staircase that never steps back toward the origin. The strong form is a directed recurrence in the first quadrant:

```
R(x, y) = allowed(x, y) AND (R(x-1, y) OR R(x, y-1)),   R(0, 0) = allowed(0, 0)
```

**Verified: this directed DP reproduces the full undirected BFS count exactly** for every N from 1 to 22 in base 10, and for bases 2, 3, 4, 5 at all N up to their respective ±500-ish axis reaches (`digitsum_monotone.py`). Connectivity failures are always total — a cell is either an island or reachable without detours; there is no third category.

Consequences:

1. **Computation.** Reachability is one vectorized run-flood sweep per row (`monotone_quadrant` in `digitsum_lib.py`), ~100× faster than BFS. This is what made the decade-4 numbers (N up to 36, bbox ±19998, 3.8×10⁸ quadrant cells) feasible.
2. **Theory.** The problem is *directed* site percolation on a deterministic self-similar set, not undirected percolation. Directed reachability composes over blocks: what happens inside a `10^k × 10^k` digit-block depends only on (a) the digit-sum budget consumed by the block's coordinate prefixes and (b) the pattern of reachable entry cells on its left and bottom edges. If those entry patterns fall into finitely many equivalence classes, the count follows a substitution system — f(N) as an entry in a product of fixed matrices, a closed form in the same sense that the Sierpiński count is 3^k. This is the rigorous version of the "recurrence indexed by ⌊N/9⌋ with a correction term" predicted below.
3. **A provable target.** The lemma itself ("the allowed set has no reachable overhangs") is only verified empirically so far. Proving it — plausibly by induction on x + y along a row's digit-sum structure — would put the framework on solid ground.

## Why a closed form stays slippery

The natural coordinates `(⌊N / 9⌋, N mod 9)` are clearly the right frame, but the recursion isn't clean. Each new decade doesn't just *embed* the previous decade's pattern — the outer layer's reachability depends on which cells of the inner layer sit on the carry boundary. Outer and inner layers interact.

Pure self-similar fractals (Sierpiński, Cantor) avoid this because their recursions are multiplicative with no threshold. The digit-sum problem has both multiplicative self-similarity *and* an additive threshold, and the two interact. That combination is why the pencil-and-paper approach hits a wall in a way that *feels* like it shouldn't.

Likely route to a formula: a recurrence indexed by `⌊N / 9⌋` with a correction term for the carry-boundary interaction — not a single closed expression. The monotone lemma above sharpens this: the correction term is the block-edge entry-pattern bookkeeping of a transfer-matrix system.

What is *not* slippery:

- **The constraint set has an exact classical closed form.** The count of `x in [0, 10^d)` with `ds(x) ≤ K` is the partial coefficient sum of `((1−q^10)/(1−q))^d`, i.e. `Σ_j (−1)^j · C(d, j) · C(d + K − 10j, d)` (verified against brute force). The 2D constraint count is a convolution of two of these. All the difficulty lives in the island subtraction.
- **Base 2 is the tractable pilot.** The monotone lemma holds there too, blocks are 2×2, and budget decrements per digit are at most 1 — the transfer-matrix approach should carry through to an exact formula in base 2 (connecting to the Kummer/Sierpiński structure noted above) before attempting base 10.

## OEIS status

The sequence f(N) = 5, 13, 25, 41, 61, 85, 113, 145, 505, 1121, 2025, 3245, 4805, 6725, 9021, 11705, 14785, 47905, 102485, 181533, 287881, 424129, … is **not in OEIS** as of July 2026 (searched the full subsequence and the standalone value 102485). Worth submitting.

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
| `digitsum_monotone.py`      | (stdout) monotone-lemma verification vs BFS; ratio table N=23..36 |

Run with `.venv-digitsum/bin/python digitsum_<name>.py`. The directed-reachability DP lives in `digitsum_lib.py` (`monotone_quadrant` / `monotone_reach_count`).
