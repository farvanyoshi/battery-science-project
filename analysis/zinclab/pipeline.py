"""Builds data/processed (the numbers the paper reads) and the graphs in assets/figures."""

from __future__ import annotations

import csv
from functools import cache
from pathlib import Path

import numpy as np

from zinclab.runs import REPO
from zinclab.spec import BY_LABEL, CURRENT, FIGURES, POTENTIAL, POWER, SERIES, paper_column, run
from zinclab.stats import ExponentialFit, fit_exponential, fit_quality, integral, statistics

ORIGINAL = REPO / "data" / "original"
PROCESSED = REPO / "data" / "processed"
FIGURES_DIR = REPO / "assets" / "figures"

# How many discharges each iteration had (the effective capacity tables).
DISCHARGES = {2: 3, 3: 3, 4: 3, 5: 2}
USEFUL_VOLTAGE = 0.9  # V; below this a AA cell counts as empty (Energizer, 2010)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return path


def g(x: float) -> str:
    """Round-trip-safe but compact number formatting for the CSV files."""
    return f"{x:.10g}"


def readouts() -> list[dict]:
    """Statistics and integrals for every trace of every figure (one row per trace)."""
    rows = []
    for fig in FIGURES:
        for i, tr in enumerate(fig.traces):
            col = tr.data()
            s = statistics(col)
            rows.append({
                "figure": fig.label,
                "series": tr.label,
                "run": tr.run,
                "color": SERIES[i],
                "unit": col.unit,
                "n": s.n,
                "min": g(s.min),
                "min_t": g(s.min_t),
                "max": g(s.max),
                "max_t": g(s.max_t),
                "mean": g(s.mean),
                "median": g(s.median),
                "std": g(s.std),
                "delta": g(s.delta),
                "integral": g(integral(col)) if fig.integral else "",
            })
    return rows


def figure_index() -> list[dict]:
    """Which file and which readouts belong to each figure label."""
    return [
        {"figure": f.label, "file": f"{f.name}.pdf", "stats": int(f.stats), "integral": int(f.integral), "fit": int(f.fit)}
        for f in FIGURES
    ]


@cache
def fit_for(figure: str, series: str) -> tuple[ExponentialFit, ExponentialFit]:
    """The curve fit (and its uncertainties) for one series of a figure."""
    tr = next(t for t in BY_LABEL[figure].traces if t.label == series)
    return fit_exponential(tr.data())


def fits() -> list[dict]:
    """The curve fits of the charging EMF, fitted to the tidy data, in figure order."""
    # The last few digits of a least-squares fit depend on the machine's maths libraries, so the fits
    # are written to 6 significant figures (the paper shows 4) to keep the file the same everywhere.
    g6 = lambda x: f"{x:.6g}"  # noqa: E731
    rows = []
    for fig in (f for f in FIGURES if f.fit):
        for i, tr in enumerate(fig.traces):
            fit, unc = fit_for(fig.label, tr.label)
            r, rmse = fit_quality(fit, tr.data())
            rows.append({
                "figure": fig.label,
                "series": tr.label,
                "A": g6(fit.A),
                "A_unc": g6(unc.A),
                "B": g6(fit.B),
                "B_unc": g6(unc.B),
                "C": g6(fit.C),
                "C_unc": g6(unc.C),
                "correlation": g6(r),
                "rmse": g6(rmse),
                "color": SERIES[i],
            })
    return rows


def effective(it: int, k: int) -> tuple[float, float]:
    """Charge (A·min) and energy (W·min) delivered from the start of discharge k up to the
    last sample at which the terminal voltage was still above 0.9 V."""
    r = run(it, "discharge", k)
    v = paper_column(r, POTENTIAL)
    above = np.flatnonzero(v.y > USEFUL_VOLTAGE)
    if len(above) == 0:
        return 0.0, 0.0
    t_end = v.t[above[-1]]
    return integral(paper_column(r, CURRENT).between(hi=t_end)), integral(paper_column(r, POWER).between(hi=t_end))


def effective_capacity() -> list[dict]:
    rows = []
    for it, n in DISCHARGES.items():
        for k in range(1, n + 1):
            q, e = effective(it, k)
            rows.append({
                "iteration": it,
                "discharge": k,
                "capacity_amin": g(q),
                "capacity_c": g(q * 60),
                "energy_wmin": g(e),
                "energy_j": g(e * 60),
            })
    return rows


def build(figures: bool = True) -> list[Path]:
    paths = [
        write_csv(PROCESSED / "figures.csv", figure_index()),
        write_csv(PROCESSED / "readouts.csv", readouts()),
        write_csv(PROCESSED / "fits.csv", fits()),
        write_csv(PROCESSED / "effective-capacity.csv", effective_capacity()),
    ]
    if figures:
        from zinclab.plot import render_all

        paths += render_all(FIGURES_DIR)
    return paths
