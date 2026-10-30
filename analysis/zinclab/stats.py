"""The statistics, integrals and curve fits shown under each graph (the same ones Logger Pro showed on the original graphs)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from zinclab.runs import Column


@dataclass(frozen=True)
class Statistics:
    """Logger Pro's "Statistics" box: extremes (with the time they first occur), mean,
    median, sample standard deviation, sample count and range (Δ = max − min)."""

    n: int
    min: float
    min_t: float
    max: float
    max_t: float
    mean: float
    median: float
    std: float

    @property
    def delta(self) -> float:
        return self.max - self.min


def statistics(col: Column) -> Statistics:
    """Statistics over the finite samples of a column."""
    ok = np.isfinite(col.t) & np.isfinite(col.y)
    t, y = col.t[ok], col.y[ok]
    if len(y) < 2:
        raise ValueError(f"'{col.name}' has fewer than two samples")
    i, j = int(np.argmin(y)), int(np.argmax(y))
    return Statistics(
        n=len(y),
        min=float(y[i]),
        min_t=float(t[i]),
        max=float(y[j]),
        max_t=float(t[j]),
        mean=float(y.mean()),
        median=float(np.median(y)),
        std=float(y.std(ddof=1)),
    )


def integral(col: Column) -> float:
    """Trapezoidal integral of y over t (Logger Pro's "Integral" box).

    Like Logger Pro, missing samples are skipped and the trapezoid joins the finite samples
    on either side. This matters for the charging currents, which were only recorded every
    other reading.
    """
    ok = np.isfinite(col.t) & np.isfinite(col.y)
    t, y = col.t[ok], col.y[ok]
    return float(np.sum(np.diff(t) * (y[:-1] + y[1:]) / 2))


@dataclass(frozen=True)
class ExponentialFit:
    """The model V = A·exp(−C·t) + B used for the charging curves."""

    A: float
    B: float
    C: float

    def __call__(self, t: np.ndarray) -> np.ndarray:
        return self.A * np.exp(-self.C * t) + self.B


def fit_quality(fit: ExponentialFit, col: Column) -> tuple[float, float]:
    """Correlation and RMSE of a fit against a column, as Logger Pro reports them.

    The correlation is r = √(1 − SS_res / SS_tot); the RMSE uses n − 3 degrees of freedom.
    """
    ok = np.isfinite(col.t) & np.isfinite(col.y)
    t, y = col.t[ok], col.y[ok]
    resid = y - fit(t)
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return float(np.sqrt(max(0.0, 1 - ss_res / ss_tot))), float(np.sqrt(ss_res / (len(y) - 3)))


def fit_exponential(col: Column) -> tuple[ExponentialFit, ExponentialFit]:
    """Least-squares fit of V = A·exp(−C·t) + B, like Logger Pro's curve fit.

    Returns the coefficients and their uncertainties (one standard error each, from the
    covariance of the fit). The tolerances are tight so the result does not depend on the
    starting guess, which comes from the first and last readings.
    """
    from scipy.optimize import curve_fit

    ok = np.isfinite(col.t) & np.isfinite(col.y)
    t, y = col.t[ok], col.y[ok]
    (a, c, b), cov = curve_fit(
        lambda t, a, c, b: a * np.exp(-c * t) + b,
        t,
        y,
        p0=(y[0] - y[-1], 0.05, y[-1]),
        maxfev=100000,
        ftol=1e-15,
        xtol=1e-15,
        gtol=1e-15,
    )
    ea, ec, eb = np.sqrt(np.diag(cov))
    return ExponentialFit(A=float(a), B=float(b), C=float(c)), ExponentialFit(A=float(ea), B=float(eb), C=float(ec))
