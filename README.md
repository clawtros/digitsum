# digitsum

Reachability on the integer lattice when the digit sums are the budget.

Start at the origin. A cell `(x, y)` is *allowed* when
`digitsum(|x|) + digitsum(|y|) <= N`, and *reachable* when a 4-connected path
of allowed cells joins it to the origin. The classic puzzle instance is base 10
with `N = 19`, where the answer is **102,485** reachable cells. This repository
is the record of working out why, and of what happens for every `N` and every
base.

## The result

**An exact reachability criterion.** Write `|x|` and `|y|` with
`k = floor(N/(b-1)) + 1` base-`b` digits. The cell is reachable if and only if
the cell itself is allowed and every proper digit-prefix pair stays within an
explicit budget, with exactly one unit of slack. The slack is the whole story:
a path can enter a block of cells only by crossing a wall of trailing
`(b-1)`-digits, and entering from the neighbouring block is one digit cheaper.

Consequences, all proved in `paper/criterion.pdf`:

- **Reachability is monotone.** Every reachable cell lies on a staircase path
  from the origin. Islands exist, but detours never help.
- **Counting is a one-dimensional walk.** The reachable count is a dynamic
  program over the `k` digit positions, polynomial in `N`. Brute-force BFS gives
  out around `N = 36`; the DP handles `N` in the hundreds of thousands.
- **The density has a closed form.** On the peak line `N = (b-1)k - 1`, the
  fraction of allowed cells in the `k`-digit box that is reachable decays like
  `c_b / sqrt(N)`, with

  ```
  c_b = (2 sqrt(b-1) / sqrt(pi)) * exp( -(1/4pi) * integral_{-pi}^{pi} ln(1 - phi_b(t)) dt ),
  phi_b(t) = ( sin(b t/2) / (b sin(t/2)) )^2
  ```

  This is a Wiener–Hopf constant via Sparre Andersen's identity. Base 2 gives
  `c_2 = 4/sqrt(pi)` exactly and base 10 gives `c_10 = 3.847174895...`. The
  next coefficient in the expansion is also closed-form (`digitsum_beta.py`).
- **Base 2 is binomial.** The quadrant count is `C(2N+3, N)`, which is
  [A002054](https://oeis.org/A002054).

## OEIS

The base-10 sequences were submitted on 2026-10-15 and are under editor review:

- [A401129](https://oeis.org/A401129): reachable cells in the full plane
  (5, 13, 25, 41, 61, 85, 113, 145, 505, ..., a(19) = 102485).
- [A401130](https://oeis.org/A401130): reachable cells in the closed first
  quadrant. The full-plane count is `4*A401130(n) - 4*A051885(n+1) + 1`.

`oeis_export.py` regenerates `oeis/submission.txt` and the b-files from
`OEIS_SUBMISSION.md`.

## Papers

Both are in `paper/` as source and PDF.

- **`criterion.pdf`** (5 pages): the proof paper. Statement and proof of the
  criterion, the monotone corollary, the counting recursion, and the
  asymptotic constant.
- **`findings.pdf`** (9 pages): the expedition report. The same material in the
  order it was discovered, wrong turns included, with figures.

Build with `make` (wraps [tectonic](https://tectonic-typesetting.github.io);
`make pages` prints page counts). The findings paper pulls its figures from
PNGs in the repo root, most of which are gitignored, so on a fresh clone run
the figure scripts first:

```
for s in reach scanlines ratio_extended peak_trough depth strip; do python3 digitsum_$s.py; done
```

## Documents

- `FINDINGS.md`: the working log, in chronological order. The source for
  `findings.tex`.
- `PROOF.md`: the proof in markdown. The source for `criterion.tex`.
- `CURRICULUM.md`: a teaching guide to the techniques the project used, aimed
  at whoever walks through it next.
- `OEIS_SUBMISSION.md`: the OEIS draft, field by field.

## Code

Python 3.10+ with `numpy`, `pillow` and `matplotlib`. Shared helpers are in
`digitsum_lib.py`; everything else is a standalone script that prints to stdout
or writes a PNG into the current directory. The full table is in `FINDINGS.md`
under "Scripts". The ones that matter most:

| script | what it does |
|---|---|
| `digitsum_criterion.py` | The criterion: cell-by-cell validation against BFS in bases 3, 5, 10, then the exact walk-DP counts and the constant `c`. |
| `digitsum_tanks.py` | The "gastank" solver: exact quadrant counts to `N = 630+` by hash-consed flood recursion. The explanatory model that preceded the criterion. |
| `digitsum_wh_constant.py` | `c_b` in closed form, checked five ways. |
| `digitsum_beta.py` | The `1/k` correction coefficient in closed form. |
| `digitsum_base2.py` | The base-2 closed form `C(2N+3, N)` verified against the DP. |
| `digitsum_bench.py` | Four solvers (BFS, monotone DP, tanks, criterion DP) cross-checked and timed. |
| `digitsum_reach.py` | Renders the reachable set at `N = 19`. |

## Authorship

Adam Benzan, in joint exploration with Claude (Anthropic). Every result was
verified computationally against exhaustive search where that was feasible,
and the three independent counting programs agree to integer equality.
