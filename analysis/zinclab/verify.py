"""Compares the submitted paper with the Logger Pro data and writes docs/VERIFICATION.md."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from zinclab.pipeline import DISCHARGES, ORIGINAL, USEFUL_VOLTAGE, effective, fit_for, read_csv, readouts
from zinclab.loggerpro import column
from zinclab.runs import REPO
from zinclab.spec import BY_LABEL, EMF, VC
from zinclab.stats import fit_quality, refit, statistics

REPORT = REPO / "docs" / "VERIFICATION.md"


def sig(x: float, n: int = 4) -> str:
    """x to n significant figures, the way Logger Pro and the paper show values."""
    if x == 0:
        return "0"
    digits = n - 1 - math.floor(math.log10(abs(x)))
    return f"{x:.{max(digits, 0)}f}" if abs(x) >= 1e-4 else f"{x:.{n - 1}e}"


def agrees(new: float, original: str) -> bool:
    """True when `new` rounds to the digits written in `original`."""
    o = float(original)
    mantissa = original.lower().split("e")[0]
    decimals = len(mantissa.split(".")[1]) if "." in mantissa else 0
    exp = int(original.lower().split("e")[1]) if "e" in original.lower() else 0
    return abs(new - o) <= 0.5 * 10 ** (exp - decimals) * 1.0001


def pct(new: float, original: float) -> str:
    return "—" if original == 0 else f"{(new - original) / abs(original):+.1%}"


def table(header: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


# --- Graph readouts --------------------------------------------------------------------

STAT_KEYS = ("n", "min", "min_at", "max", "max_at", "mean", "median", "std", "integral")


def readout_section() -> tuple[str, int, int]:
    new = {(r["figure"], r["run"]): r for r in readouts()}
    key_map = {"min_at": "min_t", "max_at": "max_t"}
    rows, checked, failed = [], 0, 0
    for o in read_csv(ORIGINAL / "figure-readouts.csv"):
        if o["kind"] == "fit":
            continue
        n = new[(o["figure"], o["series"])]
        bad = []
        for k in STAT_KEYS:
            if o[k] == "":
                continue
            checked += 1
            if not agrees(float(n[key_map.get(k, k)]), o[k]):
                bad.append(f"{k}: {o[k]} → {sig(float(n[key_map.get(k, k)]))}")
        failed += bool(bad)
        rows.append([
            o["figure"], o["series"], o["n"] or "—",
            o["mean"] or "—", sig(float(n["mean"])) if o["mean"] else "—",
            o["integral"] or "—", sig(float(n["integral"])) if o["integral"] else "—",
            "matches" if not bad else "; ".join(bad),
        ])
    text = table(["Figure", "Series", "n", "Mean (original)", "Mean (recomputed)", "Integral (original)",
                  "Integral (recomputed)", "All values in the box"], rows)
    return text, checked, failed


# --- Curve fits ------------------------------------------------------------------------

def fit_section() -> str:
    rows = []
    for o in read_csv(ORIGINAL / "curve-fits.csv"):
        fig = BY_LABEL[o["figure"]]
        tr = next(t for t in fig.traces if t.label == o["series"])
        col = column(tr.source, tr.run, tr.column)
        fit = fit_for(o["figure"], o["series"])
        r, rmse = fit_quality(fit, col)
        best = refit(col, fit)
        rows.append([
            o["figure"], o["series"],
            f"{sig(fit.A)}, {sig(fit.B)}, {sig(fit.C)}",
            f"{sig(best.A)}, {sig(best.B)}, {sig(best.C)}",
            f"{sig(float(o['correlation']))} / {sig(float(o['rmse']))}",
            f"{sig(r)} / {sig(rmse)}",
        ])
    return table(["Figure", "Series", "A, B, C (original)", "A, B, C (least-squares refit)",
                  "Correlation / RMSE (original)", "Correlation / RMSE (recomputed)"], rows)


# --- Effective capacity ----------------------------------------------------------------

def spreadsheet_sum(it: int, run: str, name: str) -> float:
    """What the data book formula computed: SUM of the samples from the first row down to the
    last row whose potential difference is above 0.9 V (no time step, so not an integral)."""
    v = column(VC.format(it), run, "Potential Difference")
    above = np.flatnonzero(v.y > USEFUL_VOLTAGE)
    if len(above) == 0:
        return 0.0
    return float(np.nansum(column(VC.format(it), run, name).y[: above[-1] + 1]))


# Cells whose data book formula pointed at the wrong columns (see the notes under the table).
SWAPPED = {(4, 1): ("Current", "Power"), (5, 1): ("Potential Difference", "Power"), (5, 2): ("Potential Difference", "Power")}


def effective_section() -> str:
    paper = {(int(r["iteration"]), int(r["discharge"])): r for r in read_csv(ORIGINAL / "effective-capacity.csv")}
    rows = []
    for it, runs in DISCHARGES.items():
        for k, run in enumerate(runs, start=1):
            p = paper[(it, k)]
            if (it, k) == (5, 2):
                sheet = "— (see explanation)"
                why = ("formula read the wrong columns: first potential difference and first power sample of the "
                       "data book's copy, which has four stray rows above the recorded data")
            elif (it, k) in SWAPPED:
                a, b = SWAPPED[(it, k)]
                first = lambda name: float(_finite(column(VC.format(it), run, name))[1][0])  # noqa: E731
                sheet = f"{sig(first(a))} / {sig(first(b))}"
                why = f"formula read the wrong columns: first {a.lower()} and first power sample"
            else:
                sheet = f"{sig(spreadsheet_sum(it, run, 'Current'))} / {sig(spreadsheet_sum(it, run, 'Power'))}"
                why = "sum of samples, not an integral"
            q, e = effective(it, run)
            if (it, k) == (3, 2):
                why += "; the paper's energy (2.316) was also mistyped from the data book (2.778)"
            if q == 0 and float(p["capacity_amin"]) == 0:
                why = "never above 0.9 V (unchanged)"
            rows.append([
                it, k,
                f"{p['capacity_amin']} / {p['energy_wmin']}",
                sheet,
                f"**{sig(q)} / {sig(e)}**",
                why,
            ])
    return table(["Iteration", "Discharge", "Paper (A·min / W·min)", "Data book formula, recomputed",
                  "Corrected integral", "Explanation"], rows)


# --- Internal resistance ---------------------------------------------------------------

def _finite(col):
    ok = np.isfinite(col.t) & np.isfinite(col.y)
    return col.t[ok], col.y[ok]


def resistance_section() -> str:
    readings = {}
    for it in (2, 3, 4):
        name = "EMF" if it == 2 else "Potential Difference"
        values = []
        for c in ("Charge 1", "Charge 2", "Charge 3"):
            try:
                values += [float(v) for v in _finite(column(EMF.format(it), c, name))[1]]
            except Exception:
                pass
        readings[it] = np.array(values)
    rows = []
    for r in read_csv(ORIGINAL / "internal-resistance.csv"):
        it, k = int(r["iteration"]), int(r["discharge"])
        run = DISCHARGES[it][k - 1]
        _, v = _finite(column(VC.format(it), run, "Potential Difference"))
        _, i = _finite(column(VC.format(it), run, "Current"))
        for at, idx in (("start", 0), ("end", -1)):
            ohm = float(r[f"{at}_ohm"])
            emf = v[idx] + ohm * i[idx]
            near = readings.get(it)
            if near is not None and len(near):
                best = near[np.argmin(np.abs(near - emf))]
                found = f"{best:.4f} V" + (" ✓" if abs(best - emf) <= 0.005 * emf else "")
            else:
                found = "no charge readings saved"
            rows.append([it, k, at, r[f"{at}_ohm"], f"{v[idx]:.4f} V, {i[idx]:.5f} A", f"{emf:.4f} V", found])
    return table(["Iteration", "Discharge", "At", "Paper r (Ω)", "Measured V, I", "EMF implied by r = (ε − V)/I",
                  "Closest EMF reading in the charge data"], rows)


# --- Values quoted in the text ---------------------------------------------------------

@dataclass
class Quote:
    where: str
    text: str
    paper: str
    value: float
    corrected: str = ""  # new text in the paper, when the original was wrong


def _r(label: str, run: str) -> dict:
    return next(r for r in readouts() if r["figure"] == label and r["run"] == run)


def quotes() -> list[Quote]:
    c2d2 = float(_r("C2-D2", "Discharge 2")["integral"])
    c4d1 = _r("C4-D1", "Discharge 1")
    c5d2 = float(_r("C5-D2", "Discharge 2")["integral"])
    p2d2 = float(_r("P2", "Discharge 2")["integral"])
    p5d2 = float(_r("P5", "Discharge 2")["integral"])
    t2, _ = _finite(column(VC.format(2), "Discharge 1", "Potential Difference"))
    t4c, i4c = _finite(column(EMF.format(4), "Charge 2", "Current"))
    v5 = column(VC.format(5), "Discharge 1", "Potential Difference")
    below = v5.t[np.flatnonzero(v5.y < 1.8)[0]]
    return [
        Quote("Method", "samples per minute recorded for Iteration 2", "30", 1 / float(np.median(np.diff(t2))), "6 (one every 10 s)"),
        Quote("Discussion, @C2-D3", "maximum current of Iteration 2 (A)", "0.01049", float(_r("C2-D3", "Discharge 3")["max"])),
        Quote("Discussion, @C2-D2", "charge of Discharge 2 (A·min)", "3.079", c2d2),
        Quote("Discussion, @C2-D2", "the same in coulombs", "184.7", c2d2 * 60),
        Quote("Discussion, @C2-D2", "the same in mAh", "51.32", c2d2 / 60 * 1000),
        Quote("Discussion, @C2-D2", "how many times less than a 1100 mAh AA cell", "21.43", 1100 / (c2d2 / 60 * 1000)),
        Quote("Discussion, @Ch2", "predicted maximum EMF, charge 1 (V)", "0.9885", fit_for("Ch2", "Charge 1").B),
        Quote("Discussion, @Ch2", "predicted maximum EMF, charge 2 (V)", "1.056", fit_for("Ch2", "Charge 2").B),
        Quote("Discussion, @Ch2", "predicted maximum EMF, charge 3 (V)", "1.018", fit_for("Ch2", "Charge 3").B),
        Quote("Discussion, @Ch2", "measured maximum EMF, charge 2 (V)", "1.061", float(_r("Ch2", "Charge 2")["max"])),
        Quote("Discussion, @C3-D1", "maximum current (A)", "0.05", float(_r("C3-D1", "Discharge 1 (10 ohms)")["max"])),
        Quote("Discussion, @Pot3b", "average voltage of the modified Iteration 3 (V)", "0.08890",
              float(_r("Pot3b", "Modified Iteration 3 Discharge")["mean"]), "0.08880"),
        Quote("Discussion, @C3b", "average current of the modified Iteration 3 (mA)", "1.617",
              float(_r("C3b", "Modified Iteration 3 Discharge")["mean"]) * 1000),
        Quote("Discussion, @Ch3", "predicted maximum EMF, charge 1 (V)", "1.338", fit_for("Ch3", "Charge 1").B),
        Quote("Discussion, @Ch3", "predicted maximum EMF, charge 2 (V)", "1.466", fit_for("Ch3", "Charge 2").B),
        Quote("Discussion, @C4-D1", "total charge (A·h)", "2.818", float(c4d1["integral"]) / 60),
        Quote("Discussion, @C4-D1", "times the best discharge of Iteration 2", "55", float(c4d1["integral"]) / c2d2),
        Quote("Discussion, @C4-D1", "maximum current (A)", "1.009", float(c4d1["max"])),
        Quote("Discussion, Eq. 4-1-res", "maximum terminal voltage (V)", "0.09371", float(_r("Pot4", "Discharge 1")["max"])),
        Quote("Discussion, Eq. 4-1-res", "external resistance V/I (Ω)", "0.09287",
              float(_r("Pot4", "Discharge 1")["max"]) / float(c4d1["max"])),
        Quote("Discussion, Eq. short-r", "internal resistance for ε = 1.5 V (Ω)", "1.394",
              (1.5 - float(_r("Pot4", "Discharge 1")["max"])) / float(c4d1["max"])),
        Quote("Discussion, @C4-C", "first current of charge 2 (A)", "0.1062", float(i4c[0])),
        Quote("Discussion, @C4-C", "typical current after the first reading (A, median)", "0.02708",
              float(_r("C4-C", "Charge 2")["median"]), "0.002708"),
        Quote("Discussion, @C4-C", "minutes between the first two readings", "2.5", float(t4c[1] - t4c[0]), "1"),
        Quote("Discussion, @Pot5", "minutes above 1.8 V in discharge 1", "40", float(below)),
        Quote("Discussion, @C5-D2", "charge of discharge 2 (A·min)", "2.106", c5d2),
        Quote("Discussion, @C5-D2", "the same in coulombs", "126.36", c5d2 * 60),
        Quote("Discussion, @C5-D2", "the same in mAh", "35.1", c5d2 / 60 * 1000),
        Quote("Discussion, @CS", "charge of the NiMH cell (A·min)", "0.4568", float(_r("CS", "NiMH Discharge 1")["integral"])),
        Quote("Discussion, @C4-D2", "charge of Iteration 4, discharge 2 (A·min)", "0.4180", float(_r("C4-D2", "Discharge 2")["integral"])),
        Quote("Discussion, @P2", "energy of Iteration 2, discharge 2 (W·min)", "2.055", p2d2),
        Quote("Discussion, @P2", "the same in mWh", "34.25", p2d2 / 60 * 1000),
        Quote("Discussion, @P4", "average power of Iteration 4, discharge 3 (mW)", "4.822", float(_r("P4", "Discharge 3")["mean"]) * 1000),
        Quote("Discussion, @P5", "energy of Iteration 5, discharge 2 (W·min)", "1.710", p5d2),
        Quote("Discussion, @P5", "the same in joules", "102.6", p5d2 * 60),
    ]


def quote_section() -> tuple[str, int]:
    rows, corrected = [], 0
    for q in quotes():
        if q.corrected:
            corrected += 1
            status = f"**corrected to {q.corrected}**"
        elif agrees(q.value, q.paper):
            status = "matches"
        elif abs(q.value - float(q.paper)) <= 0.001 * abs(float(q.paper)):
            status = "matches (worked out from rounded values)"
        elif q.paper in ("40", "55"):
            status = "matches (rounded in the text)"
        else:
            status = "**differs**"
        rows.append([q.where, q.text, q.paper, sig(q.value), status])
    return table(["Where", "Quantity", "Paper", "From the data", "Status"], rows), corrected


# --- Report ----------------------------------------------------------------------------

TEXT_CHANGES = [
    ("Method", "“set to measure 30 samples per minute … 1 sample every 2 seconds” (Iteration 2)",
     "6 samples per minute, 1 sample every 10 seconds; Iterations 3 and 4 used 30 samples per minute"),
    ("Discussion, @Pot3b", "average voltage 0.08890 V", "0.08880 V (value on the graph)"),
    ("Discussion, @C4-C", "“down to around 0.02708 A … recorded 2.5 minutes after the first”",
     "0.002708 A (the median) and 1 minute"),
    ("Discussion, @cap3", "Iteration 3's effective values were “about 5 times larger” than Iteration 2's",
     "about the same; the factor of 5 came from the different sampling rates"),
    ("Discussion, @cap4", "Iteration 4's first discharge had a “very high” effective capacity",
     "it had none, because the short circuit kept the voltage below 0.9 V"),
    ("Discussion, @cap5", "Iteration 5's values “were not impressive”",
     "they were the largest of any iteration"),
    ("Conclusion", "“The zinc chloride-based iteration 3 had by far the greatest effective capacity and effective energy.”",
     "Iteration 5, with manganese dioxide, had the greatest"),
]


def report() -> str:
    readout_text, checked, failed = readout_section()
    quote_text, corrected = quote_section()
    return f"""# Verification against the submitted paper

Generated by `python -m zinclab verify` (or `make verify`). Every graph, table and number in the submitted paper
(January 2025) was compared with the Logger Pro data in [`data/`](../data). Values are compared at the precision
they were printed with. Do not edit this file by hand.

## Summary

- **Graphs.** The 31 graphs are redrawn from the raw data. All {checked} values in the statistics and integral
  boxes of the original graphs are reproduced{"" if not failed else f", except in {failed} boxes"} (below).
- **Curve fits.** The fit coefficients are the original ones (never refitted). A least-squares refit of the same
  model gives the same coefficients.
- **Effective capacity and energy (Tables 1–4).** The submitted values were wrong. The data book formula added
  up the samples instead of integrating over time, so every value was too large by the number of samples per
  minute (6 for Iteration 2, 30 for Iterations 3 and 4). In three cells, the formula pointed at the wrong columns.
  The tables in the paper now use the integrals, and the sentences that compared these values were updated.
- **Internal resistance (Tables 5–6).** These were worked out by hand from EMF readings that are not all in the
  saved data, so they could only be partly checked. They are unchanged in the paper. See the notes below.
- **Numbers in the text.** {len(quotes())} quoted values were checked. {corrected} were wrong and are corrected in
  the paper. The rest match.

## Changes made to the paper

| Where | Submitted | Now |
|---|---|---|
""" + "\n".join(f"| {a} | {b} | {c} |" for a, b, c in TEXT_CHANGES) + f"""

The effective capacity and energy tables were replaced as a whole (see below). Spelling and grammar fixes are not
listed here (see the git history).

## Graph readouts

The original graphs were Logger Pro screenshots with statistics boxes (minimum and maximum with their times, mean,
median, standard deviation, sample count, Δ) and integral boxes. Their values were transcribed into
[`data/original/figure-readouts.csv`](../data/original/figure-readouts.csv) and compared with the values
recomputed from the raw data. The table lists the mean and integral of each box. The last column covers every
value in the box.

{readout_text}

## Curve fits (EMF while charging)

The model is EMF = A·e^(−Ct) + B. Iteration 2's fits were never saved in a Logger Pro file, so their four-digit
coefficients come from the original graph. Iteration 3's come from `emf v. time, iteration 3.cmbl`.

{fit_section()}

## Effective capacity and energy

The paper defines the effective capacity (energy) as the area under the current (power) curve while the
potential difference is above 0.9 V. The data book (`Drafting/the data book.xlsx`, not in this repository) used
`SUM(C3:INDEX(C:C, MAX(IF(B1:B10000>0.9, ROW(B1:B10000)))))`. This is the sum of every sample from the start
of the discharge to the last sample above 0.9 V. The sum leaves out the time step, so it is not an integral. For
Iteration 4, discharge 1, and both discharges of Iteration 5, the formula referenced the potential and current
columns the wrong way round. It returned the first sample instead. The corrected integrals use the same range
(start of the discharge to the last sample above 0.9 V) with the trapezoidal rule.

{effective_section()}

## Internal resistance

Each table value r was turned back into the EMF it implies, ε = V + I·r, using the first (start) or last (end)
sample of the discharge. That EMF was then compared with the open-circuit readings in the charge data. A ✓ means
a saved reading within 0.5 % was found. The other EMF values were probably read from the meters by hand and not
saved. For Iteration 4, discharge 1 (the short circuit), the implied EMF of about 5–7 V is impossible for this
cell, so those two values are almost certainly wrong. No correct value can be computed without the missing EMF
readings, so the tables are left as submitted.

{resistance_section()}

## Values quoted in the text

{quote_text}
"""


def write_report(path: Path = REPORT) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report(), encoding="utf-8")
    return path
