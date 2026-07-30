"""The rho ~ 0.91 'subleading structure', resolved: it was never a geometric.

With the criterion + Sparre Andersen machinery, c_k = sqrt(N) P_k / A_k follows
an exact recursion (evaluated here in double precision, without certified error
bounds), and its correction structure is modeled by the power family
    c_k = c (1 + alpha k^{-1/2} + beta/k + gamma k^{-3/2} + ...),
where alpha is DERIVED — forced by the denominator A_k = (1-p_k)/2 alone:
alpha = lim p_k sqrt(k) = 1/(sigma sqrt(2 pi))  (= 1/sqrt(pi) in base 2) —
and the higher coefficients are NUMERICALLY FITTED. A genuine geometric would
need a second singularity of the generating function; the next one comes from
the first SIDE LOBE of the tent kernel phi(theta), at phi ~ 0.05 — a true
ratio of ~0.05/step, utterly negligible at any relevant k.

This script: (1) computes c_k to k=1500; (2) fits the power family with
alpha PINNED to theory; (3) predicts the crest location k* = (2|beta|/alpha)^2
and compares with the observed crest; (4) replays the historical single-
geometric fit on the old data window and recovers rho ~ 0.91 from the pure
power family — the masquerade, demonstrated; (5) evaluates the true subleading
singularity (side-lobe ratio).
"""

import numpy as np
from math import sqrt, pi, exp

B = 9
SIGMA2 = (10 * 10 - 1) / 6.0


def tent_pmf():
    d = np.full(10, 0.1)
    return np.convolve(d, d)


def exact_ck(kmax):
    """c_k = sqrt(9k-1) * P(stay>=0, end>=1) / P(end>=1). The recursion is
    exact; the evaluation is double-precision (no certified error bounds)."""
    pmf = tent_pmf()
    span = B * (kmax + 2) + 2
    W = np.zeros(span)
    W[0] = 1.0                    # constrained walk, index = e >= 0
    S = np.ones(1)                # free walk
    out = np.empty(kmax + 1)
    out[0] = np.nan
    for k in range(1, kmax + 1):
        W = np.convolve(W, pmf)[B: B + span]
        S = np.convolve(S, pmf)
        pk = S[(len(S) - 1) // 2]
        out[k] = sqrt(9 * k - 1) * W[1:].sum() / ((1 - pk) / 2)
    return out


def wh_constant(M=4000):
    pmf = tent_pmf()
    dist = np.ones(1)
    p = np.empty(M + 1)
    for n in range(1, M + 1):
        dist = np.convolve(dist, pmf)
        p[n] = dist[n * B]
    head = sum(p[n] / n for n in range(1, M + 1))
    A = 1.0 / sqrt(SIGMA2 * 2 * pi)
    ns = np.arange(M - 400, M + 1)
    y = p[ns] / (A * ns ** -0.5) - 1.0
    X = np.stack([1 / ns, 1 / ns ** 2], axis=1)
    (a1, a2), *_ = np.linalg.lstsq(X, y, rcond=None)

    def zt(s, M):
        return (M ** (1 - s) / (s - 1) - 0.5 * M ** -s + s / 12 * M ** (-s - 1)
                - s * (s + 1) * (s + 2) / 720 * M ** (-s - 3))

    g = head + A * (zt(1.5, M) + a1 * zt(2.5, M) + a2 * zt(3.5, M))
    return 6 / sqrt(pi) * exp(g / 2)


if __name__ == "__main__":
    KMAX = 1500
    ck = exact_ck(KMAX)
    c = wh_constant()
    alpha = 1.0 / sqrt(SIGMA2 * 2 * pi)
    print(f"c = {c:.9f},  theoretical alpha = 1/(sigma sqrt(2pi)) = {alpha:.6f}")

    # fit beta, gamma, delta with alpha pinned, on k in [300, 1500]
    ks = np.arange(300, KMAX + 1, dtype=float)
    r = ck[300:] / c - 1.0 - alpha / np.sqrt(ks)
    X = np.stack([1 / ks, ks ** -1.5, ks ** -2.0], axis=1)
    (beta, gamma, delta), *_ = np.linalg.lstsq(X, r, rcond=None)
    resid = X @ np.array([beta, gamma, delta]) - r
    print(f"power fit (alpha pinned): beta = {beta:.4f}, gamma = {gamma:.3f}, "
          f"delta = {delta:.2f}; rms = {np.sqrt(np.mean(resid**2)):.1e}")

    # out-of-window test: predict c_k on k in [30, 300) from the fitted family
    ks2 = np.arange(30, 300, dtype=float)
    pred = c * (1 + alpha / np.sqrt(ks2) + beta / ks2 + gamma * ks2 ** -1.5
                + delta * ks2 ** -2.0)
    err = np.max(np.abs(pred - ck[30:300]))
    print(f"out-of-window (k in [30,300)): max |pred - exact| = {err:.1e}")

    # crest: predicted k* = (2|beta|/alpha)^2 vs observed argmax
    kstar_pred = (2 * abs(beta) / alpha) ** 2
    kstar_obs = int(np.nanargmax(ck))
    print(f"crest: predicted k* = {kstar_pred:.0f}, observed argmax = "
          f"{kstar_obs} (N = {9*kstar_obs-1}), c_crest = {ck[kstar_obs]:.6f}")

    # the masquerade: single-geometric fit on the historical window q in [28,69]
    qs = np.arange(28, 70, dtype=float)
    cs = ck[(qs + 1).astype(int)]  # k = q + 1
    best = None
    for rho in np.linspace(0.80, 0.99, 2000):
        Xg = np.stack([np.ones_like(qs), rho ** qs], axis=1)
        coef, *_ = np.linalg.lstsq(Xg, cs, rcond=None)
        rms = float(np.sqrt(np.mean((Xg @ coef - cs) ** 2)))
        if best is None or rms < best[0]:
            best = (rms, rho, coef[0])
    print(f"masquerade: best single-geometric fit on q in [28,69]: "
          f"rho = {best[1]:.4f} (historical fit gave 0.913-0.915), "
          f"apparent limit {best[2]:.5f}, rms {best[0]:.1e}")

    # the TRUE subleading singularity: first side lobe of the tent kernel
    th = np.linspace(np.pi / 5 + 1e-6, 2 * np.pi / 5 - 1e-6, 200001)
    phi = (np.sin(5 * th) / (10 * np.sin(th / 2))) ** 2
    print(f"true geometric component: side-lobe ratio phi* = {phi.max():.5f} "
          f"per step (z1 = {1/phi.max():.2f}) — invisible at all relevant k")
