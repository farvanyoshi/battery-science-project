"""Builds data/processed (the numbers the paper reads) and the graphs in assets/figures."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from zinclab.runs import REPO, column
from zinclab.spec import FIGURES, SERIES, VC
from zinclab.stats import ExponentialFit, integral, statistics

ORIGINAL = REPO / "data" / "original"
PROCESSED = REPO / "data" / "processed"
FIGURES_DIR = REPO / "assets" / "figures"

# The runs behind the effective capacity tables, in paper order.
DISCHARGES = {
    2: ["Discharge 1", "Discharge 2", "Discharge 3"],
    3: ["Discharge 1 (10 ohms)", "Discharge 2 (1000 ohms)", "Discharge 3 (100 ohms)"],
    4: ["Discharge 1", "Discharge 2", "Discharge 3"],
    5: ["Discharge 1", "Discharge 2"],
}
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
            col = column(tr.source, tr.run, tr.column)
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


def original_fits() -> dict[tuple[str, str], dict]:
    return {(r["figure"], r["series"]): r for r in read_csv(ORIGINAL / "curve-fits.csv")}


def fit_for(figure: str, series: str) -> ExponentialFit:
    r = original_fits()[(figure, series)]
    return ExponentialFit(A=float(r["A"]), B=float(r["B"]), C=float(r["C"]))


def fits() -> list[dict]:
    """The curve fits from the original graphs (never refitted), in figure order.

    docs/VERIFICATION.md checks their correlation and RMSE against the data.
    """
    rows = []
    for fig in (f for f in FIGURES if f.fit):
        for i, tr in enumerate(fig.traces):
            o = original_fits()[(fig.label, tr.label)]
            keys = ("figure", "series", "A", "A_unc", "B", "B_unc", "C", "C_unc", "correlation", "rmse")
            rows.append({k: o[k] for k in keys} | {"color": SERIES[i]})
    return rows


def effective(it: int, run: str) -> tuple[float, float]:
    """Charge (A·min) and energy (W·min) delivered from the start of a discharge up to the
    last sample at which the terminal voltage was still above 0.9 V."""
    v = column(VC.format(it), run, "Potential Difference")
    above = np.flatnonzero(v.y > USEFUL_VOLTAGE)
    if len(above) == 0:
        return 0.0, 0.0
    t_end = v.t[above[-1]]
    cur = column(VC.format(it), run, "Current").between(hi=t_end)
    pwr = column(VC.format(it), run, "Power").between(hi=t_end)
    return integral(cur), integral(pwr)


def effective_capacity() -> list[dict]:
    rows = []
    for it, runs in DISCHARGES.items():
        for k, run in enumerate(runs, start=1):
            q, e = effective(it, run)
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
