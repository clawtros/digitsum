# A curriculum from the digitsum expedition

*A guide for a future instructor — human or AI instance — walking Adam (or
anyone) through the techniques this project used, roughly in the order they
earned their keep. Each module: the idea, where it lives in this repo, and how
to teach it. The project's own wrong turns are teaching instruments; do not
route around them.*

**About the student, from the instance that worked alongside him:** learns by
staring at structures — render early, render often. Prefers metaphors he builds
himself (the gastank picture predated and ultimately became the formalism;
"weir," "wall," "wetting front" are load-bearing vocabulary, see the FINDINGS
glossary). Comfortable with code as the primary instrument and math arriving
second. Let discoveries be his: set up the computation, let him look at the
output first. Keep the commit-as-you-go rhythm; every claim should trace to a
re-runnable script.

---

## Module 1 — Computation as microscope

**Idea:** before theory, exhaustively compute a small instance and *look* at it.
**Artifacts:** `digitsum_lib.py` (BFS), `digitsum_reach.png`, `digitsum_strip.png`.
**Teach:** brute force is not the opposite of insight; it is how the tri-force,
death zones, and islands were first seen. Render everything.
**Exercise:** pick any constrained-lattice problem, BFS it, render it, list
three visual anomalies before proving anything.

## Module 2 — Measurements outlive interpretations

**Idea:** the project's central theorem came from a measurement filed under
"a wrong turn": detour ≡ 0 was correctly measured, wrongly interpreted, and
shelved — the *measurement* was the monotone lemma waiting to be noticed.
**Artifacts:** FINDINGS "BFS depth (a wrong turn — later redeemed)."
**Teach:** keep a record that separates what was observed from what was
concluded. Revisit discarded observations when new frames appear.
**Exercise:** find a "failed" experiment in any old project and re-read only
its raw observations, ignoring its conclusions.

## Module 3 — Directed structure and cheap exactness

**Idea:** verifying a structural lemma (undirected reachability = directed
staircase reachability) can convert an expensive computation into a cheap one
— here a ~100× vectorized row sweep (`monotone_quadrant`, the run-flood trick
with `cumsum`/`maximum.accumulate`).
**Artifacts:** `digitsum_monotone.py`, `digitsum_lib.py`.
**Teach:** every verified structural fact is also an algorithm. The speedup is
what made every later module affordable.

## Module 4 — The predict-then-verify protocol

**Idea:** when a pattern appears (Q₂ = C(2N+3,N) from 14 data points), commit
to a prediction for the *next* value before computing it. OEIS lookup is part
of this module (the sequence f(N) was absent; A002054 anchored base 2).
**Artifacts:** `digitsum_base2.py` (N=15 predicted, then confirmed by a
4.3×10⁹-cell sweep).
**Teach:** held-out confirmation is the difference between numerology and
discovery. It failed us exactly once — see Module 8 — which is the point.

## Module 5 — Renormalization by hand: the gastank decomposition

**Idea:** find the coordinates in which the problem is exactly self-similar.
Here: digit sums are carry-free inside blocks, so tanks decompose into tanks
with budgets K−i−j; carries *are* the walls. Then build the exact recursive
solver, with hash-consing when interface objects (wetting fronts) are fractal.
**Artifacts:** `digitsum_tanks.py`, `digitsum_tanks_anybase.py`, the FINDINGS
glossary + `digitsum_glossary.png`, `digitsum_bench.py`.
**Teach:** (a) hunting for the carry-free/self-similar frame; (b) interning
recursive objects as DAG nodes so equality is id-comparison; (c) benchmarking
honestly (cold starts, cross-checked outputs) to show the complexity-class
jump. The naive interval representation dying at N≈100 is a feature — let it
die first.

## Module 6 — Sequence forensics, with controls

**Idea:** test for C-finite (Berlekamp–Massey, exact rationals, held-out
verification) and holonomic (nullspace mod several primes) recurrences — and
**always validate the detector on a known instance first**. Our first
holonomic guesser silently failed its control; only the control exposed it.
**Artifacts:** scratch scripts described in FINDINGS ("no small recurrence"
bullets); the RREF-nullspace fix.
**Teach:** a negative result from an unvalidated detector is worthless. State
negative results as tested bounds, never as nonexistence (review round 2's
lesson).

## Module 7 — The special case as pilot plant

**Idea:** run the whole intended program on the smallest special case first
(base 2), where answers are checkable in closed form. Base 2's exact constant
4/√π later calibrated every extrapolation model, and its binomial later
validated the general solver.
**Artifacts:** `digitsum_base2.py`, base-2 checks inside nearly every later
script.
**Teach:** a solved special case is not a trophy — it is permanent test
infrastructure.

## Module 8 — Asymptotic extrapolation and its traps (the best module)

**Idea:** extracting limits from finite data is model-dependent and the models
lie. Walk the student through, in order: the √15 mirage (pair-fits landing
within 1.3×10⁻⁵ of a wrong constant), the crest that killed it, the 3.865
horizon artifact, and the ρ≈0.91 "eigenvalue" that was a power family in
disguise (`digitsum_rho.py`: refitting the historical window reproduces the
historical wrong number exactly).
**Artifacts:** `digitsum_c.py`, `digitsum_peakdata.json`, `digitsum_rho.py`,
FINDINGS "two false summits" + "masquerade" sections.
**Teach:** (a) calibrate every extrapolation pipeline on a case with a known
answer; (b) local increment ratios discriminate tail classes; (c) a fitted
constant is not a discovered constant; (d) when the exact answer arrived, the
"degenerate" fits everyone dismissed had been right. Let the student be
seduced by √15 before showing the crest.

## Module 9 — Spectral/transfer-operator thinking

**Idea:** self-similar systems have decade maps; censuses of normalized states
can attain fixed points *exactly*; truncated transfer matrices give spectra.
Also: how this frame can mislead (the λ₂/λ₁ reading was withdrawn) and how it
can win late (the census's d ≤ 1 boundary became the criterion's barrier).
**Artifacts:** `digitsum_spectral.py`, `digitsum_classes.py --verify`.
**Teach:** instrument, normalize (the offset d = 9k − K), census, compare
across scale. Emphasize the end of the story: the "24 classes" dissolved into
a scanline-threshold ladder with dynamically inert labels — structure hunting
sometimes ends by proving the structure carries no information.

## Module 10 — Fluctuation theory as applied toolkit

**Idea:** one-boundary walk problems have a classical machine: reflection
principle (base-2 proof), Sparre Andersen identity (the constant), Wiener–Hopf
factorization (its integral form), meander local-limit estimates (endpoint
condition), Garsia–Milne / round-inversion (the surfacing bijection).
**Artifacts:** `digitsum_wh_constant.py`, `digitsum_bijection.py`,
`digitsum_criterion.py`, paper/criterion.tex corollaries.
**Teach:** each tool with its project instance; verify identities
coefficientwise against DPs before trusting conventions (the SA identity was
checked to 10⁻¹⁶ precisely because textbook conventions vary).

## Module 11 — Proof craft

**Idea:** the criterion's proof is elementary and worth internalizing as a
pattern: necessity by *crossing certificates* (any path entering a region
pays at a wall; the +1 slack is a borrow), sufficiency by *explicit
construction* (the corner L-path consumes exactly the certified slack), glued
by induction in self-similar coordinates. Sharpness = the two slacks coincide.
**Artifacts:** PROOF.md, paper/criterion.tex.
**Teach:** also the hygiene layer: statement ranges matter (the s=0 exclusion,
D3's hypotheses — both caught in review), and writing LaTeX rigorously *finds*
bugs (D3's m=0 failure surfaced while typesetting).

## Module 12 — Claim hygiene and adversarial review

**Idea:** the final polish came from four rounds of external review that moved
every claim onto one of three shelves: proved, bounded, or labeled numerical.
**Artifacts:** the last five commits; every `--verify` mode.
**Teach:** distinctions that matter: exact recursion vs double-precision
evaluation; verified-exhaustively vs proved; "no recurrence found below
bounds" vs "no recurrence"; a documented claim should name the script that
re-checks it. Invite an adversarial review and treat every finding as either
a fix or a proof opportunity (the bijection got *proved* because a reviewer
called it only-verified).

---

## Suggested arc for a guided replay

1–2 sessions per module; the natural spine is the project's own chronology
(FINDINGS.md is ordered that way deliberately, false summits included). For a
fresh problem instead of a replay, the checklist is: compute and render →
separate observations from conclusions → find the self-similar frame → pilot
the smallest special case → predict-then-verify → forensics with controls →
suspect every extrapolation → let the structure dissolve if it wants to →
prove with certificates and constructions → subject it all to review.

The one-sentence version of the whole project: **the criterion was hiding in
the first session's discarded measurement, and every technique above was, in
hindsight, a way of learning to look at it.**
