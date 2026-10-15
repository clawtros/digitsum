"""The 1/k coefficient beta of the correction family, derived — the last loose
thread of the constant c, closed.

On the peak line, c_k = sqrt((b-1)k - 1) * (q_k - r_k) / ((1 - p_k)/2) with
    q_k = P(S_1,...,S_k >= 0)              (Sparre Andersen: GF = (1-z)^{-1/2} e^{G(z)})
    r_k = P(S_1,...,S_{k-1} >= 0, S_k = 0) (Spitzer-Baxter at the origin: GF = e^{2G(z)})
    p_k = P(S_k = 0),  G(z) = (1/2) sum_n p_n z^n / n.
Expanding G at z = 1 (w = 1 - z) through order w, with alpha = 1/(sigma sqrt(2 pi)),
K = e^{G(1)} (so c_b = 2 sqrt(b-1) K / sqrt(pi)) and
rho_1 = sum_n (p_n - alpha n^{-1/2}):
    G = log K - alpha sqrt(pi) w^{1/2} - (1/2)(alpha zeta(1/2) + rho_1) w + O(w^{3/2}),
singularity analysis gives
    q_k = K/sqrt(pi k) (1 + u_1/k + ...),  u_1 = -1/8 + (alpha zeta(1/2) + rho_1)/4 - pi alpha^2/4,
    r_k ~ K^2 alpha k^{-3/2}
(the w^0 term of the SA generating function is analytic, so the numerator has no
k^{-1/2} correction: alpha comes from the denominator alone), and therefore
    c_k = c_b (1 + alpha/sqrt(k) + beta/k + ...),
    beta = (1 - pi/4) alpha^2 - K/(sigma sqrt 2) - 1/8 - 1/(2(b-1))
           + (alpha zeta(1/2) + rho_1)/4.
Base 2 is fully explicit (K = 2, G = log(2/(1+sqrt w)), alpha zeta(1/2) + rho_1 = -1):
    beta_2 = 1/pi - 25/8 = -2.80669...

This script: (1) verifies the Spitzer-Baxter identity for r_k coefficientwise
against a barrier DP; (2) evaluates beta from the closed form; (3) compares with
the power-family fit to the exact c_k with alpha pinned (as in digitsum_rho.py),
and with alpha AND beta pinned.  Double precision throughout (exact recursions,
uncertified floating-point evaluation).
"""

import numpy as np
from math import sqrt, pi, exp

ZETA_HALF = -1.4603545088095868  # zeta(1/2)


def tent_pmf(b):
    d = np.full(b, 1.0 / b)
    return np.convolve(d, d)  # steps -(b-1)..(b-1)


def exact_ck(b, kmax):
    """c_k and p_k for k <= kmax."""
    B = b - 1
    pmf = tent_pmf(b)
    span = B * (kmax + 2) + 2
    W = np.zeros(span)
    W[0] = 1.0  # constrained walk, index = e >= 0
    S = np.ones(1)  # free walk
    ck = np.full(kmax + 1, np.nan)
    p = np.ones(kmax + 1)
    for k in range(1, kmax + 1):
        W = np.convolve(W, pmf)[B: B + span]
        S = np.convolve(S, pmf)
        p[k] = S[(len(S) - 1) // 2]
        ck[k] = sqrt(B * k - 1) * W[1:].sum() / ((1 - p[k]) / 2)
    return ck, p


def spitzer_baxter_check(b, kmax=120):
    """r_k = P(S_1..S_{k-1} >= 0, S_k = 0) must equal [z^k] exp(sum p_n z^n / n)."""
    B = b - 1
    pmf = tent_pmf(b)
    dist = np.ones(1)
    a = np.zeros(kmax + 1)
    for n in range(1, kmax + 1):
        dist = np.convolve(dist, pmf)
        a[n] = dist[n * B] / n
    R = np.zeros(kmax + 1)
    R[0] = 1.0
    for k in range(1, kmax + 1):
        R[k] = sum(j * a[j] * R[k - j] for j in range(1, k + 1)) / k
    span = B * (kmax + 1) + 1
    W = np.zeros(span)
    W[0] = 1.0
    worst = 0.0
    for k in range(1, kmax + 1):
        W = np.convolve(W, pmf)[B: B + span]
        worst = max(worst, abs(W[0] - R[k]))
    return worst


def zeta_tail(s, M):
    """sum_{n>M} n^-s by Euler-Maclaurin."""
    return (M ** (1 - s) / (s - 1) - 0.5 * M ** -s + s / 12 * M ** (-s - 1)
            - s * (s + 1) * (s + 2) / 720 * M ** (-s - 3))


def beta_closed_form(b, p, M):
    B = b - 1
    sigma2 = (b * b - 1) / 6.0
    alpha = 1.0 / sqrt(sigma2 * 2 * pi)
    # tail model p_n = alpha n^-1/2 (1 + a1/n + a2/n^2), fitted on the last 400 points
    ns = np.arange(M - 400, M + 1)
    y = p[ns] / (alpha * ns ** -0.5) - 1.0
    X = np.stack([1 / ns, 1 / ns ** 2], axis=1)
    (a1, a2), *_ = np.linalg.lstsq(X, y, rcond=None)
    n = np.arange(1, M + 1)
    g = (p[1:M + 1] / n).sum() + alpha * (
        zeta_tail(1.5, M) + a1 * zeta_tail(2.5, M) + a2 * zeta_tail(3.5, M))
    K = exp(g / 2)
    rho1 = (p[1:M + 1] - alpha * n ** -0.5).sum() + alpha * (
        a1 * zeta_tail(1.5, M) + a2 * zeta_tail(2.5, M))
    beta = ((1 - pi / 4) * alpha ** 2 - K / sqrt(2 * sigma2) - 1 / 8
            - 1 / (2 * B) + (alpha * ZETA_HALF + rho1) / 4)
    c_b = 2 * sqrt(B) / sqrt(pi) * K
    return dict(alpha=alpha, K=K, c_b=c_b, rho1=rho1, beta=beta)


def fits(ck, c, alpha, beta, kmin, kmax):
    ks = np.arange(kmin, kmax + 1, dtype=float)
    r = ck[kmin:kmax + 1] / c - 1.0 - alpha / np.sqrt(ks)
    # alpha pinned: fit beta, gamma, delta
    X = np.stack([1 / ks, ks ** -1.5, ks ** -2.0], axis=1)
    (bf, gf, df), *_ = np.linalg.lstsq(X, r, rcond=None)
    # alpha and beta pinned: fit gamma, delta
    X2 = np.stack([ks ** -1.5, ks ** -2.0], axis=1)
    (g2, d2), *_ = np.linalg.lstsq(X2, r - beta / ks, rcond=None)
    resid = X2 @ np.array([g2, d2]) - (r - beta / ks)
    rms = float(np.sqrt(np.mean(resid ** 2)))
    ks2 = np.arange(30, kmin, dtype=float)
    pred = c * (1 + alpha / np.sqrt(ks2) + beta / ks2 + g2 * ks2 ** -1.5 + d2 * ks2 ** -2.0)
    oow = float(np.max(np.abs(pred - ck[30:kmin])))
    return bf, (g2, d2, rms, oow)


if __name__ == "__main__":
    for b in (2, 3, 4, 5, 10):
        KMAX = 1500
        ck, p = exact_ck(b, KMAX)
        r = beta_closed_form(b, p, KMAX)
        print(f"base {b}: Spitzer-Baxter r_k check, max coefficient error "
              f"{spitzer_baxter_check(b):.1e}")
        print(f"   c_b = {r['c_b']:.9f}, alpha = {r['alpha']:.6f}, K = {r['K']:.6f}, "
              f"rho_1 = {r['rho1']:.6f}")
        bf, (g2, d2, rms, oow) = fits(ck, r['c_b'], r['alpha'], r['beta'], 300, KMAX)
        print(f"   beta: closed form {r['beta']:.6f}   fitted (alpha pinned) {bf:.6f}")
        if b == 2:
            print(f"   base-2 exact: 1/pi - 25/8 = {1 / pi - 25 / 8:.6f}")
        print(f"   with alpha, beta pinned: gamma = {g2:.4f}, delta = {d2:.3f}, "
              f"rms {rms:.1e} on k in [300,1500], out-of-window (k in [30,300)) "
              f"max err {oow:.1e}")
