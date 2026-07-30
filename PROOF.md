# Proof of the reachability criterion

## Setting

Fix a base b ≥ 2 and write B = b − 1. Threshold N ≥ 1, k = ⌊N/B⌋ + 1, so that
B·k > N ≥ B·(k−1). A cell (x, y) ∈ ℤ² is *allowed* iff ds(|x|) + ds(|y|) ≤ N
(digit sums in base b). *Reachable* means joined to the origin by a 4-connected
path of allowed cells.

For 0 ≤ x, y < b^k write the digits most-significant-first, x = x₁x₂…x_k, and
let x⟨s⟩ = x₁…x_s denote the length-s prefix (as an integer). Put

  P_s = ds(x⟨s⟩) + ds(y⟨s⟩)   for s = 0, 1, …, k.

**Theorem.** For (x, y) in the quadrant, (x, y) is reachable iff

  (i) P_s ≤ N − B(k−s) + 1 for every s with 1 ≤ s < k, and
  (ii) P_k = ds(x) + ds(y) ≤ N.

(The empty prefix s = 0 is excluded: P₀ = 0 but the bound N − Bk + 1 can be
negative off the peak line. The walk DP likewise never tests the start d₀.)

In gastank language: (i) says every ancestor tank of the cell has budget
K = N − P_s ≥ B·m − 1 at its scale m = k−s; (ii) says the cell itself is
submerged.

Three elementary facts about digit sums, used repeatedly:

- (D1) ds(X) ≤ ds(X−1) + 1 for all X ≥ 1 (incrementing adds 1 to the last
  digit, or borrows, which only lowers the sum: ds(X) = ds(X−1) + 1 − B·t
  when X ends in t zeros).
- (D2) ds(X·b^m − 1) = ds(X−1) + B·m (the digits are those of X−1 followed by
  m copies of B — the trailing-nines wall).
- (D3) for m ≥ 1 and 1 ≤ a < b (a single digit):
  max { ds(t) : 0 ≤ t ≤ a·b^m } = (a−1) + B·m, attained at a·b^m − 1.
  (False without these hypotheses — e.g. m = 0 gives max = a — but the proof
  only ever applies it to leading digits with m ≥ 1.)

## Reduction to the quadrant

The folding map (x, y) ↦ (|x|, |y|) preserves allowedness and maps neighbors
to neighbors or to equal cells, so it sends any allowed path from the origin
to an allowed quadrant walk with the same endpoint image. Conversely quadrant
paths are plane paths. Hence it suffices to prove the theorem for quadrant
reachability, and the full-plane reachable set is the 4-fold reflection of the
quadrant one. Also every reachable x satisfies x < b^k: the column
x = (smallest integer with digit sum N+1) is entirely forbidden — by (D2)-type
counting its digit sum with any y is > N — and it lies below b^k, so paths
never pass it; likewise for y. Cells are therefore k-digit as assumed.

## Necessity: wall certificates

Suppose (x, y) is reachable by an allowed quadrant path π; fix s with
1 ≤ s < k and let m = k − s. Partition the quadrant into scale-m tanks: tank (A, B̂) is
[A·b^m, (A+1)·b^m) × [B̂·b^m, (B̂+1)·b^m). Let T = (X, Y) with X = x⟨s⟩,
Y = y⟨s⟩ be the ancestor tank of (x, y) at scale m.

If (X, Y) = (0, 0) then P_s = 0 and (i) holds trivially (B(k−s) ≤ B(k−1) ≤ N
< N+1). Otherwise the origin lies outside T, so π contains a first step that
enters T: two consecutive cells c ∉ T, c′ ∈ T, differing by one unit. Four
cases:

- **From the left** (c in tank (X−1, Y)): then c = (X·b^m − 1, y*) with y* in
  tank row Y, so ds(y*) ≥ ds(Y). By (D2), ds(X·b^m − 1) = ds(X−1) + B·m.
  Allowedness of c gives ds(X−1) + ds(Y) ≤ N − B·m, and by (D1)
  P_s = ds(X) + ds(Y) ≤ N − B·m + 1.
- **From below**: symmetric, using the trailing-nines wall row of tank
  (X, Y−1): P_s ≤ N − B·m + 1.
- **From the right** (c in tank (X+1, Y)): then the *entered* cell c′ lies in
  the rightmost column of T itself: c′ = ((X+1)·b^m − 1, y*). By (D2) its
  x-digit-sum is ds(X) + B·m, so allowedness gives P_s ≤ N − B·m directly.
- **From above**: symmetric: P_s ≤ N − B·m.

In every case (i) holds at s; and (ii) is just allowedness of (x, y) itself. ∎

The "+1" of slack is exactly the borrow in (D1): entering a tank from the left
or from below certifies the *neighbor's* wall, which is one digit cheaper.

## Sufficiency: the corner staircase

We prove by induction on j: *for every threshold M and every j ≥ 1 with cells
in [0, b^j)², if (x, y) satisfies (i)–(ii) (with j in place of k), then there
is a monotone staircase (steps +x and +y only) of allowed cells from (0, 0)
to (x, y).* Applying this with j = k, M = N gives the theorem, and
incidentally proves the monotone-staircase lemma.

**Base j = 1.** (ii) reads x + y ≤ M. Walk (0,0) → (x,0) → (x,y); every cell
has digit sum ≤ x + y ≤ M.

**Step j ≥ 2.** Let a = x₁, c = y₁ be the leading digits, and x′, y′ the
(j−1)-digit remainders. Condition (i) at s = 1 reads

  a + c ≤ M − B(j−1) + 1.  (★)

*Leg 1 — to the corner of tank (a, c).* Take the L-path
(0,0) → (a·b^{j−1}, 0) → (a·b^{j−1}, c·b^{j−1}).
On the axis run, by (D3) every cell (t, 0) has digit sum at most
(a−1) + B(j−1) ≤ M by (★) (using c ≥ 0); the endpoint has digit sum a. On the
column climb, every cell (a·b^{j−1}, u) with u ≤ c·b^{j−1} has digit sum at
most a + (c−1) + B(j−1) ≤ M, again exactly (★). (If a = 0 or c = 0 the
corresponding leg is shorter or empty and the bounds only improve.)

*Leg 2 — inside the tank.* The tank (a, c) at scale j−1, entered at its
bottom-left corner, is a copy of the same problem with j−1 digit positions and
threshold M′ = M − a − c: a local cell (u, v) is allowed iff
ds(u) + ds(v) ≤ M′. The original conditions (i) at 2 ≤ s ≤ j−1 and (ii)
translate verbatim: for 1 ≤ s′ = s − 1 ≤ j−2,

  P_s ≤ M − B(j−s) + 1 ⟺ P′_{s′} ≤ M′ − B((j−1) − s′) + 1,

where P′ are the prefix sums of (x′, y′); the final prefix s = j is handled
separately by (ii), which becomes ds(x′) + ds(y′) ≤ M′. So (x′, y′) satisfies the (j−1)-digit criterion at
threshold M′, and by the induction hypothesis there is a monotone allowed
staircase from the tank's corner to it; adding (a·b^{j−1}, c·b^{j−1}) to every
cell keeps it allowed globally (the leading digits contribute exactly a + c).

Concatenating the two legs gives the staircase. ∎

Note the exactness: necessity produces the bound N − B·m + 1 via the borrow in
(D1), and sufficiency *consumes* precisely the same bound in the column climb
of the L-path (worst cell a + (c−1) + B(j−1)). The two "+1"s coincide, which
is why the criterion is sharp rather than merely necessary or sufficient.

## Corollaries

1. **Monotone-staircase lemma** (previously empirical): reachable ⟹ criterion
   ⟹ staircase-reachable, so undirected reachability, directed reachability,
   and the criterion all coincide.
2. **Counting.** f(N) and Q(N) are computed exactly by the 1-D walk DP of
   `digitsum_criterion.py` (the criterion is a survival condition on the walk
   d_s = d₀ + Σ(x_t + y_t − B), d₀ = B·k − N, barrier d ≤ 1, endpoint d ≤ 0).
3. **Asymptotics.** On the peak line N ≡ B−1 (mod B) the reachable/constraint
   ratio is a classical one-boundary walk survival probability; its c/√N law
   and the constant c (= 3.84717(5) in base 10, exactly 4/√π in base 2) are
   Wiener–Hopf/kernel-method objects for the tent-step walk.
4. **Base 2.** Q(N) = C(2N+3, N) is proved. By the criterion, reachable cells
   are interleaved bit-words of length 2k (k = N+1) whose ±1 path satisfies the
   even-checkpoint condition and ends ≤ −2. Since even-time positions are even
   integers, the checkpoint condition is equivalent to the uniform barrier
   "max ≤ +1"; reflection at level 2 then gives
   #{max ≤ 1, end ≤ −2} = Σ_{m≥1} [C(2k, k−m) − C(2k, k+m+2)]
   = C(2k, k−1) + C(2k, k−2) = C(2k+1, k−1) = C(2N+3, N).
   An explicit bijection onto the allowed cells of the top two elevation layers
   (the *surfacing map*: repeatedly complement the prefix up to the first
   hitting time of level −2) is proved by a round-inversion lemma — the flipped
   word's first +2-hit occurs at the same position, so one sinking round undoes
   one surfacing round; termination and stopping match by weight parity — and
   additionally verified exhaustively in `digitsum_bijection.py`.
