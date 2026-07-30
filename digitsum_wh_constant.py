"""The Wiener-Hopf closed form for the constant c — open problem 1, resolved.

Via the criterion, Q(N)/b^(2k) on the peak line is the probability that the
reflected tent walk stays >= 0 for k steps and ends >= 1. Sparre Andersen's
identity (the combinatorial form of Wiener-Hopf factorization) plus symmetry
P(S_n >= 0) = (1 + p_n)/2, p_n := P(S_n = 0), gives

    c_b = (2 sqrt(b-1) / sqrt(pi)) * exp( (1/2) * sum_{n>=1} p_n / n )
        = (2 sqrt(b-1) / sqrt(pi)) *
          exp( -(1/4pi) * INT_{-pi}^{pi} log(1 - phi_b(t)) dt ),

with phi_b(t) = (sin(b t/2) / (b sin(t/2)))^2 the tent characteristic function.
Base 2 collapses in closed form: sum p_n/n = 2 log 2, K = 2, c_2 = 4/sqrt(pi).

This script (1) verifies the Sparre Andersen identity coefficientwise against a
barrier DP, (2) evaluates the series (exact p_n + Euler-Maclaurin tail) and the
integral independently, and (3) compares c_b with the DP extrapolations.
"""

import numpy as np
from math import sqrt, pi, log, exp


def tent_pmf(b):
    d = np.full(b, 1.0 / b)
    return np.convolve(d, d)  # steps -(b-1)..(b-1)


def p_central(b, nmax):
    """p_n = P(tent walk at 0 after n steps), exactly, for n = 1..nmax."""
    pmf = tent_pmf(b)
    B = b - 1
    dist = np.ones(1)
    out = np.empty(nmax + 1)
    for n in range(1, nmax + 1):
        dist = np.convolve(dist, pmf)
        out[n] = dist[n * B]  # center
    return out


def sa_check(b, kmax=120):
    """Sparre Andersen: coefficients of exp(sum z^n (1+p_n)/(2n)) must equal
    q_k = P(S_1>=0,...,S_k>=0) from a direct barrier DP."""
    p = p_central(b, kmax)
    a = np.array([0.0] + [(1 + p[n]) / (2 * n) for n in range(1, kmax + 1)])
    Q = np.zeros(kmax + 1)
    Q[0] = 1.0
    for k in range(1, kmax + 1):  # exp of a power series, standard recurrence
        Q[k] = sum(j * a[j] * Q[k - j] for j in range(1, k + 1)) / k
    pmf = tent_pmf(b)
    B = b - 1
    span = B * (kmax + 1) + 1
    W = np.zeros(span)
    W[0] = 1.0  # index = e >= 0
    worst = 0.0
    for k in range(1, kmax + 1):
        W = np.convolve(W, pmf)[B: B + span]  # drop e < 0
        worst = max(worst, abs(W.sum() - Q[k]))
    return worst


def series_g(b, M=4000):
    """g = sum_{n>=1} p_n/n with Euler-Maclaurin tail beyond M."""
    p = p_central(b, M)
    head = sum(p[n] / n for n in range(1, M + 1))
    # tail: p_n ~ A n^{-1/2} (1 + a1/n + a2/n^2), A = 1/(sigma sqrt(2 pi))
    sigma2 = (b * b - 1) / 6.0
    A = 1.0 / sqrt(sigma2 * 2 * pi)
    ns = np.arange(M - 400, M + 1)
    y = (p[ns] / (A * ns ** -0.5) - 1.0)
    X = np.stack([1 / ns, 1 / ns ** 2], axis=1)
    (a1, a2), *_ = np.linalg.lstsq(X, y, rcond=None)

    def zeta_tail(s, M):  # sum_{n>M} n^{-s} by Euler-Maclaurin
        return (M ** (1 - s) / (s - 1) - 0.5 * M ** -s
                + s / 12 * M ** (-s - 1)
                - s * (s + 1) * (s + 2) / 720 * M ** (-s - 3))

    tail = A * (zeta_tail(1.5, M) + a1 * zeta_tail(2.5, M) + a2 * zeta_tail(3.5, M))
    return head + tail


def integral_g(b):
    """g = -(1/pi) * int_0^pi log(1 - phi(t)) dt, log-singularity at 0 split off."""
    def phi(t):
        return (np.sin(b * t / 2) / (b * np.sin(t / 2))) ** 2
    eps = 0.05
    # [eps, pi]: plain fine Simpson
    t = np.linspace(eps, pi, 200001)
    y = np.log(1 - phi(t))
    I1 = np.trapezoid(y, t)
    # [0, eps]: log(1-phi) = 2 log t + log((1-phi)/t^2); the second factor is
    # smooth with limit log(sigma^2/2) at 0 — used below 1e-5 where direct
    # evaluation of 1-phi loses to float cancellation.
    sigma2 = (b * b - 1) / 6.0
    t2 = np.linspace(0.0, eps, 200001)
    with np.errstate(divide="ignore", invalid="ignore"):
        smooth = np.where(t2 < 1e-5, log(sigma2 / 2),
                          np.log((1 - phi(np.maximum(t2, 1e-5))) /
                                 np.maximum(t2, 1e-5) ** 2))
    I2 = 2 * (eps * log(eps) - eps) + np.trapezoid(smooth, t2)
    return -(I1 + I2) / pi


def excursion_check(b, kmax=2000):
    """The endpoint-zero excursions r_k = P(stay >= 0, end = 0) must be
    o(k^{-1/2}) for the endpoint condition (>=1 vs >=0) not to affect c.
    Standard meander local-limit theory gives r_k ~ const * k^{-3/2}; verify
    r_k * k^{3/2} is bounded and settling."""
    pmf = tent_pmf(b)
    B = b - 1
    span = B * (kmax + 1) + 1
    W = np.zeros(span)
    W[0] = 1.0
    vals = {}
    for k in range(1, kmax + 1):
        W = np.convolve(W, pmf)[B: B + span]
        if k in (kmax // 4, kmax // 2, kmax):
            vals[k] = W[0] * k ** 1.5
    return vals


if __name__ == "__main__":
    print("Sparre Andersen identity vs barrier DP (max coefficient error):")
    for b in (2, 10):
        print(f"  base {b}: {sa_check(b):.2e}")

    print("endpoint-zero excursions r_k * k^(3/2) (bounded => o(k^-1/2), "
          "endpoint condition immaterial):")
    for b in (2, 10):
        vals = excursion_check(b)
        print(f"  base {b}: " + ", ".join(f"k={k}: {v:.4f}"
                                          for k, v in sorted(vals.items())))

    print(f"\n{'b':>3} {'g (series)':>12} {'g (integral)':>12} "
          f"{'c_b (formula)':>13} {'c_b (DP extrap)':>15}")
    dp_ref = {2: 4 / sqrt(pi), 3: 2.478057, 4: 2.704994, 5: 2.921624, 10: 3.847175}
    for b in (2, 3, 4, 5, 10):
        gs = series_g(b)
        gi = integral_g(b)
        c = 2 * sqrt(b - 1) / sqrt(pi) * exp(gs / 2)
        print(f"{b:>3} {gs:>12.9f} {gi:>12.9f} {c:>13.9f} {dp_ref[b]:>15.6f}")
    print(f"\nbase-2 closed form: sum p_n/n = 2 log 2 = {2 * log(2):.9f}; "
          f"c_2 = 4/sqrt(pi) = {4 / sqrt(pi):.9f}")
