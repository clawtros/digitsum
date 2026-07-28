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

Base 2 specifically connects to known theory (popcount, Kummer's theorem on binomial coefficients mod 2, giving a clean Sierpiński triangle). Base 10 has no known closed form — but base 2 now does: see "The base-2 pilot" below.

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
- Both envelopes decay roughly geometrically (successive drops shrink by ~0.7); naive extrapolation puts the asymptotic ratio around **0.40–0.47**. *However*, the exact base-2 result (below) shows the base-2 ratio decays to **zero** like `4/√(πN)`, and the observed base-10 envelope is equally consistent with a slow power law `~ c/√(N/9)` (fitted exponents drift −0.30, −0.40, −0.42 toward −½ across the four cliffs). Revised conjecture: **the ratio tends to 0 in every base**, like c·√(base−1)/√N — there is no finite asymptote, just a very slow square-root decay.

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
- **Base 2 is the tractable pilot.** The monotone lemma holds there too, blocks are 2×2, and budget decrements per digit are at most 1. **This worked — see the next section**: base 2 has an exact single-binomial closed form.

## The base-2 pilot: an exact closed form

Computing the base-2 quadrant counts with the monotone DP gives Q = 5, 21, 84, 330, 1287, 5005, 19448, … — which are single binomial coefficients. For every N from 1 to 15 (the N = 15 value was *predicted first, then confirmed* by a 4.3-billion-cell DP sweep):

```
quadrant reachable    Q(N) = C(2N+3, N)
full-plane reachable  f(N) = 4·C(2N+3, N) − 2^(N+3) + 5
quadrant constraint   c(N) = (4^(N+1) − C(2N+2, N+1)) / 2
islands               c(N) − Q(N)  (closed form by subtraction)
```

(The axis term: every cell 0..2^(N+1)−2 on an axis is reachable, hence 4Q − 4(2^(N+1)−1) + 1.)

Q(N) is OEIS **A002054**, `C(2n+1, n−1)`, a ballot-type binomial with standard lattice-path interpretations ("paths that touch but do not cross the diagonal") — strong evidence that a *bijective proof* exists between reachable cells and ballot paths, presumably via interleaving the bits of x and y along the monotone staircase. That proof is the natural next step; the f(N) sequence 9, 57, 277, 1197, 4897, … is not in OEIS.

Two consequences:

1. **The program works.** Monotone lemma → directed DP → exact closed form, executed end to end in the simplest base. The base-10 analogue is now a concrete target rather than a hope: same machinery, bigger blocks (10×10 instead of 2×2, budget decrements up to 9 per digit).
2. **The asymptotic ratio is zero, not a constant.** Exactly: `Q(N)/c(N) → 4/√(πN) → 0`. The reachable set is asymptotically a vanishing fraction of the constraint set, decaying like an inverse square root. This overturns the earlier finite-asymptote reading of the base-10 staircase (see the revised conjecture in the staircase section).

## The base-10 transfer: gastanks all the way down

The working mental model — nested tanks of fluid spilling over weirs — turns out to be *exactly* the right formalism, because of one clean fact: **digit sums are carry-free inside a block**. A child tank at digit position `(i, j)` inside a tank of budget K has budget exactly `K − i − j`, at every scale. Carries never appear inside a tank; they *are* the walls between sibling tanks, and every wall separates budgets differing by exactly 1. The whole quadrant is one giant tank `T_k(N)` of 100 child tanks, recursively.

### Glossary

Two equivalent physical readings. In **coordinate space**, fluid sits in the lattice itself and only ever flows right/up (the monotone lemma). In **terrain space**, elevation at `(x, y)` is `ds(x) + ds(y)`, the waterline is N, allowed cells are the submerged ones, and the reachable set is the submerged region connected to the origin — islands are submerged basins cut off behind ridges. The tank silhouettes live in the first picture; the overflow intuition is exact in the second.

**Tank** — `T_k(K)`: a scale-k block `[0,10^k) × [0,10^k)` in local coordinates with budget K; the local cell `(u, v)` is allowed iff `ds(u) + ds(v) ≤ K`. Silhouette: at k = 1 literally the staircase triangle `u + v ≤ K`; a full square when `K ≥ 18k`; between those, a square with the far corner cut away — the classic gastank profile. Every tank is a 10×10 grid of child tanks, the child at digit position `(i, j)` being `T_{k−1}(K − i − j)`: budgets step down by 1 per digit rightward or upward, with no carry corrections inside, ever. A tank with capacity but no entries is **dry**; dry-but-roomy tanks are precisely the islands, and `(300, 0)` sits in the canonical one.

**Wall** — the seam between two adjacent sibling tanks, physically realized by the trailing-9s column (or row): the last column of the left tank, all 9s in local digits, contributing digit sum `9s` at sibling scale s. Walls are where carries live — a carry never happens inside a tank; it *is* the wall — and they grow taller by 9 with each scale. In terrain space a wall is a ridge of height `9s` running the length of the seam. The two tanks a wall separates always have budgets differing by exactly 1; the top-scale wall at `x = 299` (for N = 19) is a ridge that nowhere dips below the waterline, which is why everything past it is dry.

**Weir** — the passable opening in a wall: the set of rows at which flow can cross the seam, `{v : ds(v) ≤ K_L − 9s}` where `K_L` is the left tank's budget and s the sibling scale. In terrain space this is the notch where the ridge dips below the waterline; in coordinate space the opening sits at the *bottom* of the seam (digit sum grows with height), so fluid that has risen too high in the left tank cannot reach it — the mechanism by which new decades are entered only at low levels. Note the weir is itself a 1D digit-sum threshold set — exactly the scanline family `{v : ds(v) ≤ K}` from the scanline decomposition, one scale down. For s = 1 it is the plain interval `v ≤ K_L − 9`.

**Wetting front** — the pattern of flow across a tank edge: the set of edge cells through which fluid actually passes (entry fronts on the left/bottom edges, exit fronts on the right/top). At scale 1 a front is a single interval — a literal fluid level. At scale k it is a union of up to ~9^(k−1) intervals: weirs gate it and dry tanks punch gaps, giving fronts a Cantor-dust structure. The solver never expands a front: since fronts only ever split on child-tank boundaries, each is an interned 10-tuple of child fronts — a DAG node compared by id. The finiteness of distinct fronts per (scale, budget) is the transfer structure, and their fractal growth is why the naive interval representation died at N ≈ 100.

`digitsum_tanks.py` implements this literally. `flood()` takes a tank (scale, budget) plus entry patterns — the fluid levels on its left and bottom edges — floods the children in monotone order passing exit patterns over the weirs, and returns the flooded-cell count plus exit patterns. Two implementation facts matter:

- **The wetting fronts are fractal.** An exit pattern at scale k can have ~9^(k−1) intervals (Cantor-dust structure), so fronts are never expanded: since a front only ever splits on child-tank boundaries, it is stored *hash-consed* — an interned 10-tuple of child-front ids, a DAG node compared by id.
- **The distinct tank states are few.** Memoizing on (scale, budget, entry fronts): a few hundred distinct states per scale; total states grow only polynomially (~N^3.3). That finiteness *is* the transfer structure — but note it is budget-graded (states are indexed by K as well as scale), i.e. a layered operator, not one fixed matrix.

Results:

- Validated against BFS/DP for all N ≤ 36 and against an independent interval-based implementation for N ≤ 81.
- **Exact Q(N) to N = 630 in ~2.5 minutes** (Q(630) has 139 digits; brute force capped out at N = 36). Per-N cost is milliseconds at N ≤ 100.
- **No small recurrence.** Per residue class N mod 9 (the decade frame), Q is not C-finite (orders ≤ 13 excluded by exact Berlekamp–Massey with held-out verification) and not small-holonomic (no polynomial-coefficient recurrence with order ≤ 6, degree ≤ 8; detector validated on holonomic controls). Crucially, the *constraint* count fails the identical test, so this is not evidence that reachability is wilder than the constraint set — both are double-indexed sequences (N and the scale k = ⌊N/9⌋+1 move together). Base 2 escaped only because its constraint sum telescopes at the central binomial; base 10's cutoff sits near but not at the center of its digit-sum distribution, and no such collapse occurs.
- **The √N decay law is confirmed in base 10.** Along the peak line N ≡ 8 (mod 9), `ratio · √N` converges: 3.641 (N=35), 3.822 (N=107), 3.861 (N=251), 3.868 (N=449), 3.869 (N=629). So reachable/constraint ≈ c/√N, the base-10 sibling of the exact base-2 law 4/√(πN). See "Hunting the constant c" for the value of c (and the demise of the √15 guess).

Where this leaves the closed-form hunt: the gastank recursion gives an exact polynomial-time evaluator — the problem is now *computationally* closed. A single closed-form expression in the base-2 sense is unlikely to exist for base 10 (the layered, budget-graded operator resists collapsing to a fixed-dimensional recurrence), but the constant c and the structure of the state family are both open, well-posed targets.

## Benchmarks

Four solver generations on full-plane f(N), cross-checked wherever two overlap (`digitsum_bench.py`; tanks timed cold — module reloaded per N so memoization doesn't flatter it):

| N   | bfs (set) | bfs (grid) | monotone DP | tanks    | f(N) |
|----:|----------:|-----------:|------------:|---------:|-----:|
|  26 |    1.31 s |     1.19 s |     0.009 s |  0.002 s | 1.3 × 10⁶ |
|  28 |         — |     8.55 s |     0.053 s |  0.003 s | 9.0 × 10⁶ |
|  36 |         — |          — |     1.98 s  |  0.008 s | 3.8 × 10⁸ |
|  90 |         — |          — |           — |  0.13 s  | 2.5 × 10²⁰ |
| 360 |         — |          — |           — |  16.2 s  | ~10⁸⁹ |
| 630 |         — |          — |           — |  144 s   | ~10¹⁴⁰ |

The BFS variants and the monotone DP are all O(area) = O(10^(2N/9)) — the DP just wins a ~100× vectorization constant, which bought exactly one extra decade (N=36) before the exponential wall. The tank solver's cost tracks its state count, ~N^3.3: polynomial versus exponential, which is the whole story. At N=36 it is ~250× faster than the DP; past N≈40 it is the only game in town.

(Benchmarking exposed that `axis_bound` was a linear scan with a hard cap; it now uses the closed form — smallest x with ds(x) = N+1 is digit s followed by q nines where N+1 = 9q+s — verified against scans across bases.)

## Hunting the constant c (and the death of √15)

A serious attempt to pin the constant in `ratio ≈ c/√N`, using exact peak-line Q values to N = 989 (`digitsum_peakdata.json`, ~15M tank states, 3.6 GB) and a base-general tank solver (`digitsum_tanks_anybase.py`, validated against the base-2 closed form, the base-10 solver, and the monotone DP in bases 3–5).

**√15 is refuted.** The peak-line sequence c_N = Q/constraint·√N rises to a **crest of 3.86931 at N ≈ 650, then descends with accelerating increments** (−1.7e−4, −2.5e−4, −2.9e−4 per 90 steps of N at 719/809/899/989). √15 = 3.87298 lies above every value the sequence ever attained; reaching it would require the sequence to reverse into a rise after four accelerating descents, which no correction model supports. The seductive early agreement (pair-fits through N=629 landed within 1.3e−5 of √15) was a genuine mirage caused by two correction terms crossing over.

**What the correction structure actually is.** At least two competing terms: a geometric-per-decade rise (~ρ^q with ρ ≈ 0.91 — the signature of a subleading eigenvalue of the decade transfer map) that dominates for N ≲ 650, and a slow negative power-law tail (the CLT edge-correction family) that takes over beyond the crest. Because they fight at the 10⁻³ scale even at N ≈ 1000, extrapolation models disagree: the honest estimate is **c = 3.865 ± 0.004**. The same crest-then-descend shape appears in bases 3, 4, 5 (crests: 2.52798 at N=149, 2.74720 at N=197, 2.95829 at N=255) — the structure is universal; base 2 (exact c = 4/√π, approach from above) is the degenerate case with no visible crest.

**Methodology lesson** (the reason this section can be trusted): every extrapolation model was first calibrated on base 2, where c = 4/√π is exact. Naive polynomial-in-1/N extrapolation recovers base-2's constant with error 2×10⁻² — hopelessly wrong — because the true corrections carry 1/√N terms; the calibrated two-power model recovers it to 9×10⁻⁵. Without the base-2 control, the base-10 fits (spread 3.847–3.897) would have been reported with false confidence.

**The way to actually get c**: not extrapolation. The decade transfer map on normalized tank-state distributions should have a fixed point, with c a functional of it and ρ its subleading eigenvalue ratio — computing that spectrum directly from the flood recursion is the well-posed route, and it would deliver ρ ≈ 0.91 as a check.

## The spectral expedition

First execution of that program (`digitsum_spectral.py`): instrument the flood recursion, extract the census of tank states in the top scales normalized as `(depth, d = 9k − K, front signatures)` — d is the tank's offset from the digit-sum mean; the top tank always has d = 1 on the peak line, and children step by `(i+j) − 9`, a centered walk. Three results:

1. **The fixed point is exactly attained, not just approached.** The normalized shallow census is *identical* — exact integer equality, state by state — across every peak-line N tested (116 to 404), at every instrumented depth. The crown of the hierarchy is perfectly self-similar under the decade shift; all N-dependence lives in the deepening diffusive interior. Census sizes per depth: 1, 27, 96, 226, 435 states (55, 4180, 350317, 30748795 tank instances).
2. **The state family closes.** Transitions are well-defined functions of the truncated-signature classes (577 of 651 classes unambiguous; the 74 failures all sit at d ≤ −35 — deeply submerged near-full tanks that a truncation absorbs anyway). Classes per waterline offset max out at **24** and stop growing. Bonus: the active band is **one-sided** — no active tank ever has d > 1; everything above the waterline is dry.
3. **The spectrum trends toward ρ but is truncation-limited.** The tank-count transfer matrix on the unambiguous states gives λ₁ → 95.2 (climbing toward the trivial 100 as the d-band widens) and λ₂/λ₁ = 0.577 → 0.777 → **0.860** as truncation depth grows — rising toward the observed ρ ≈ 0.91 but saturating at the depth our SHALLOW=6 instrumentation reaches, i.e. limited by data, not by the trend.

Verdict: the spectral framework is viable and two of its three pillars are now *exact empirical facts* (fixed point, closure). The remaining work is real mathematics: instrument deeper (the band widens like √depth, so memory grows fast), and treat the diffusive d-walk properly — a Markov-additive process whose continuum spectrum is precisely the power-law correction family that fought the geometric term in the c hunt. The 24-classes-per-offset operator with a one-sided boundary at d = 1 is now a concrete, finitely-presented object; c and ρ are functionals of it.

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
| `digitsum_base2.py`         | (stdout) base-2 closed form Q(N)=C(2N+3,N) verified vs DP |
| `digitsum_tanks.py`         | (stdout) gastank solver — exact Q(N) to N=630+ via hash-consed flood recursion |
| `digitsum_bench.py`         | (stdout) four-way solver benchmark with cross-checks |
| `digitsum_tanks_anybase.py` | base-general tank solver (validations in __main__)  |
| `digitsum_c.py`             | (stdout) c-constant analysis over `digitsum_peakdata.json` |
| `digitsum_spectral.py`      | (stdout) decade-map census, closure test, transfer-matrix spectrum |

Run with `.venv-digitsum/bin/python digitsum_<name>.py`. The directed-reachability DP lives in `digitsum_lib.py` (`monotone_quadrant` / `monotone_reach_count`).
