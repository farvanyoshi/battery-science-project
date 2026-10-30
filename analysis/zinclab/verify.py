"""Compares the submitted paper with the data book and writes docs/VERIFICATION.md."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from zinclab.book import BY_ID
from zinclab.pipeline import DISCHARGES, ORIGINAL, USEFUL_VOLTAGE, effective, fit_for, read_csv, readouts
from zinclab.runs import REPO, TIDY
from zinclab.spec import BY_LABEL, CURRENT, POTENTIAL, POWER, paper_column, run
from zinclab.stats import fit_quality

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


def table(header: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def _finite(col):
    ok = np.isfinite(col.t) & np.isfinite(col.y)
    return col.t[ok], col.y[ok]


# --- Data book vs. Logger Pro -----------------------------------------------------------

def cleaning_section() -> str:
    with (TIDY / "cleaning.csv").open(newline="", encoding="utf-8") as f:
        entries = list(csv.DictReader(f))
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for e in entries:
        groups[(e["run"], e["action"], e["reason"])].append(e)
    rows = []
    for (r, action, reason), es in groups.items():
        book_rows = sorted({e["book_row"] for e in es}, key=lambda x: int(x.split("-")[0]))
        span = book_rows[0] if len(book_rows) == 1 else f"{book_rows[0]}–{book_rows[-1]}"
        columns = sorted({c.strip() for e in es for c in e["column"].split(",")})
        rows.append([
            f"`{r}`", "yes" if BY_ID[r].used else "no", span.replace("-", "–"), ", ".join(columns),
            f"{action} ({len(es)} cells)" if action == "removed" else action, reason,
        ])
    return table(["Run", "In the paper", "Book rows", "Columns", "Change", "Reason"], rows)


# --- Graph readouts --------------------------------------------------------------------

STAT_KEYS = ("n", "min", "min_at", "max", "max_at", "mean", "median", "std", "integral")

# Boxes that come out differently from the data book, and why. Keyed by (figure, series on the
# original graph).
READOUT_CHANGES = {
    ("Vnorm", "Iteration 4, Discharge 1"): "the original graph showed Iteration 4's normalized current here, "
    "because it was made from the data book's swapped columns (now fixed)",
    ("Cnorm", "Iteration 4, Discharge 1"): "the original graph showed Iteration 4's normalized potential here, "
    "because it was made from the data book's swapped columns (now fixed)",
    ("C2-C", "Charge 1"): "the current at 12.5 min is an average the data book keeps unrounded "
    "(0.0425911 A) where Logger Pro rounded it (0.042591 A)",
    ("C3-D2", "Discharge 2 (1000 ohms)"): "Logger Pro rounded the smallest current step to −9.54e-05 A; "
    "the data book has it in full",
    ("P3", "Discharge 2 (1000 ohms)"): "the same unrounded current step as C3-D2",
}


def readout_comparison() -> tuple[list[list], int, list[tuple[str, str, list[str]]]]:
    """Original boxes next to the recomputed ones, matched by their order on each graph."""
    new = defaultdict(list)
    for r in readouts():
        new[r["figure"]].append(r)
    original = defaultdict(list)
    for o in read_csv(ORIGINAL / "figure-readouts.csv"):
        if o["kind"] != "fit":
            original[o["figure"]].append(o)
    key_map = {"min_at": "min_t", "max_at": "max_t"}
    rows, checked, differences = [], 0, []
    for figure, boxes in original.items():
        assert len(boxes) == len(new[figure]), figure
        for o, n in zip(boxes, new[figure]):
            bad = []
            for k in STAT_KEYS:
                if o[k] == "":
                    continue
                checked += 1
                if not agrees(float(n[key_map.get(k, k)]), o[k]):
                    bad.append(f"{k}: {o[k]} → {sig(float(n[key_map.get(k, k)]))}")
            if bad:
                differences.append((figure, o["series"], bad))
            rows.append([
                figure, o["series"], o["n"] or "—",
                o["mean"] or "—", sig(float(n["mean"])) if o["mean"] else "—",
                o["integral"] or "—", sig(float(n["integral"])) if o["integral"] else "—",
                "matches" if not bad else "**changed** (see above)",
            ])
    return rows, checked, differences


def readout_changes_text(differences) -> str:
    rows = []
    for figure, series, bad in differences:
        why = READOUT_CHANGES.get((figure, series), "**not explained**")
        rows.append([figure, series, "; ".join(bad), why])
    return table(["Figure", "Series", "Original → now", "Why"], rows)


# --- Curve fits ------------------------------------------------------------------------

def fit_section() -> str:
    rows = []
    for o in read_csv(ORIGINAL / "curve-fits.csv"):
        tr = next(t for t in BY_LABEL[o["figure"]].traces if t.label == o["series"])
        fit, unc = fit_for(o["figure"], o["series"])
        r, rmse = fit_quality(fit, tr.data())
        rows.append([
            o["figure"], o["series"],
            ", ".join(f"{sig(float(o[k]))} ± {sig(float(o[k + '_unc']))}" for k in "ABC"),
            ", ".join(f"{sig(getattr(fit, k))} ± {sig(getattr(unc, k))}" for k in "ABC"),
            f"{sig(float(o['correlation']))} / {sig(float(o['rmse']))}",
            f"{sig(r)} / {sig(rmse)}",
        ])
    return table(["Figure", "Series", "A, B, C (original)", "A, B, C (fitted to the data book)",
                  "Correlation / RMSE (original)", "Correlation / RMSE (now)"], rows)


# --- Effective capacity ----------------------------------------------------------------

def spreadsheet_sum(it: int, k: int, name: str) -> float:
    """What the data book formula computed: SUM of the samples from the first row down to the
    last row whose potential difference is above 0.9 V (no time step, so not an integral)."""
    v = paper_column(run(it, "discharge", k), POTENTIAL)
    above = np.flatnonzero(v.y > USEFUL_VOLTAGE)
    if len(above) == 0:
        return 0.0
    return float(np.nansum(paper_column(run(it, "discharge", k), name).y[: above[-1] + 1]))


# Cells whose data book formula pointed at the wrong columns (see the notes under the table).
SWAPPED = {(4, 1): (CURRENT, POWER), (5, 1): (POTENTIAL, POWER), (5, 2): (POTENTIAL, POWER)}
NAMES = {POTENTIAL: "potential difference", CURRENT: "current", POWER: "power"}


def effective_section() -> str:
    paper = {(int(r["iteration"]), int(r["discharge"])): r for r in read_csv(ORIGINAL / "effective-capacity.csv")}
    rows = []
    for it, n in DISCHARGES.items():
        for k in range(1, n + 1):
            p = paper[(it, k)]
            if (it, k) == (5, 2):
                sheet = "— (see explanation)"
                why = ("formula read the wrong columns: the first potential difference and power samples, which are "
                       "readings that were struck out in Logger Pro and are removed from the tidy data")
            elif (it, k) in SWAPPED:
                a, b = SWAPPED[(it, k)]
                first = lambda name: float(_finite(paper_column(run(it, "discharge", k), name))[1][0])  # noqa: E731
                sheet = f"{sig(first(a))} / {sig(first(b))}"
                why = f"formula read the wrong columns: first {NAMES[a]} and first power sample"
            else:
                sheet = f"{sig(spreadsheet_sum(it, k, CURRENT))} / {sig(spreadsheet_sum(it, k, POWER))}"
                why = "sum of samples, not an integral"
            q, e = effective(it, k)
            if (it, k) == (3, 2):
                why += "; the paper's energy (2.316) was also mistyped from the data book (2.778)"
            if q == 0 and float(p["capacity_amin"]) == 0:
                why = "never above 0.9 V (unchanged)"
            rows.append([it, k, f"{p['capacity_amin']} / {p['energy_wmin']}", sheet, f"**{sig(q)} / {sig(e)}**", why])
    return table(["Iteration", "Discharge", "Paper (A·min / W·min)", "Data book formula, recomputed",
                  "Corrected integral", "Explanation"], rows)


# --- Internal resistance ---------------------------------------------------------------

def resistance_section() -> str:
    readings = {}
    for it in (2, 3, 4):
        values = []
        for c in (1, 2, 3):
            if run(it, "charge", c) in BY_ID:
                values += [float(v) for v in _finite(paper_column(run(it, "charge", c), POTENTIAL))[1]]
        readings[it] = np.array(values)
    rows = []
    for r in read_csv(ORIGINAL / "internal-resistance.csv"):
        it, k = int(r["iteration"]), int(r["discharge"])
        _, v = _finite(paper_column(run(it, "discharge", k), POTENTIAL))
        _, i = _finite(paper_column(run(it, "discharge", k), CURRENT))
        for at, idx in (("start", 0), ("end", -1)):
            ohm = float(r[f"{at}_ohm"])
            emf = v[idx] + ohm * i[idx]
            near = readings.get(it)
            if near is not None and len(near):
                best = near[np.argmin(np.abs(near - emf))]
                found = f"{best:.4f} V" + (" ✓" if abs(best - emf) <= 0.005 * emf else "")
            else:
                found = "no charge readings used"
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


def _r(label: str, series: str) -> dict:
    return next(r for r in readouts() if r["figure"] == label and r["series"] == series)


def quotes() -> list[Quote]:
    c2d2 = float(_r("C2-D2", "Discharge 2")["integral"])
    c4d1 = _r("C4-D1", "Discharge 1")
    c5d2 = float(_r("C5-D2", "Discharge 2")["integral"])
    p2d2 = float(_r("P2", "Discharge 2")["integral"])
    p5d2 = float(_r("P5", "Discharge 2")["integral"])
    t2, _ = _finite(paper_column(run(2, "discharge", 1), POTENTIAL))
    t4c, i4c = _finite(paper_column(run(4, "charge", 2), CURRENT))
    v5 = paper_column(run(5, "discharge", 1), POTENTIAL)
    below = v5.t[np.flatnonzero(v5.y < 1.8)[0]]
    b = lambda figure, series: fit_for(figure, series)[0].B  # noqa: E731
    return [
        Quote("Method", "samples per minute recorded for Iteration 2", "30", 1 / float(np.median(np.diff(t2))), "6 (one every 10 s)"),
        Quote("Discussion, @C2-D3", "maximum current of Iteration 2 (A)", "0.01049", float(_r("C2-D3", "Discharge 3")["max"])),
        Quote("Discussion, @C2-D2", "charge of Discharge 2 (A·min)", "3.079", c2d2),
        Quote("Discussion, @C2-D2", "the same in coulombs", "184.7", c2d2 * 60),
        Quote("Discussion, @C2-D2", "the same in mAh", "51.32", c2d2 / 60 * 1000),
        Quote("Discussion, @C2-D2", "how many times less than a 1100 mAh AA cell", "21.43", 1100 / (c2d2 / 60 * 1000)),
        Quote("Discussion, @Ch2", "predicted maximum EMF, charge 1 (V)", "0.9885", b("Ch2", "Charge 1")),
        Quote("Discussion, @Ch2", "predicted maximum EMF, charge 2 (V)", "1.056", b("Ch2", "Charge 2")),
        Quote("Discussion, @Ch2", "predicted maximum EMF, charge 3 (V)", "1.018", b("Ch2", "Charge 3")),
        Quote("Discussion, @Ch2", "measured maximum EMF, charge 2 (V)", "1.061", float(_r("Ch2", "Charge 2")["max"])),
        Quote("Discussion, @C3-D1", "maximum current (A)", "0.05", float(_r("C3-D1", "Discharge 1 (10 Ω)")["max"])),
        Quote("Discussion, @Pot3b", "average voltage of the modified Iteration 3 (V)", "0.08890",
              float(_r("Pot3b", "Modified Iteration 3")["mean"]), "0.08880"),
        Quote("Discussion, @C3b", "average current of the modified Iteration 3 (mA)", "1.617",
              float(_r("C3b", "Modified Iteration 3")["mean"]) * 1000),
        Quote("Discussion, @Ch3", "predicted maximum EMF, charge 1 (V)", "1.338", b("Ch3", "Charge 1")),
        Quote("Discussion, @Ch3", "predicted maximum EMF, charge 2 (V)", "1.466", b("Ch3", "Charge 2")),
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
        Quote("Discussion, @CS", "charge of the NiMH cell (A·min)", "0.4568", float(_r("CS", "NiMH")["integral"])),
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
    rows, checked, differences = readout_comparison()
    unexplained = [d for d in differences if (d[0], d[1]) not in READOUT_CHANGES]
    quote_text, corrected = quote_section()
    return f"""# Verification against the submitted paper

Generated by `python -m zinclab verify` (or `make verify`). Every graph, table and number in the submitted paper
(January 2025) was compared with the data book ([`data/raw/the-data-book.xlsx`](../data/raw/the-data-book.xlsx),
through the tidy files in [`data/tidy/`](../data/tidy)). Values are compared at the precision they were printed
with. Do not edit this file by hand.

## Summary

- **Data.** The data book holds the same readings as the Logger Pro files the original graphs were made from,
  except for the few cells listed below. The tests in `analysis/tests/test_book.py` check this reading by reading.
- **Graphs.** The 31 graphs are redrawn from the data book. Of the {checked} values in the statistics and integral
  boxes of the original graphs, all are reproduced except in {len(differences)} boxes, and each of those is
  explained below{"" if not unexplained else f" (**{len(unexplained)} are not explained**)"}.
- **Curve fits.** The fits are now done on the data book's readings. They give the same coefficients,
  uncertainties, correlations and RMSEs as the original graphs.
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

## Data book vs. Logger Pro

Every change made while splitting the data book into [`data/tidy/`](../data/tidy) is logged in
[`data/tidy/cleaning.csv`](../data/tidy/cleaning.csv). Grouped by run:

{cleaning_section()}

The readings that were removed from runs in the paper are exactly the ones that were struck out in Logger Pro, so
the original graphs did not include them either. Apart from these, the data book and Logger Pro agree to within
Logger Pro's rounding (about 10⁻⁷).

The data book also has the full length of two runs that the paper cut short: Iteration 5's first discharge ran for
240 minutes, but the paper cut both of its discharges off at 88 minutes, and the last charge of Iteration 2 ran for
120 minutes, but the paper only used the first 60. The graphs and tables keep the paper's cutoffs
(`CUTOFF` in `analysis/zinclab/spec.py`). The normalized potential graph (Vnorm) showed the whole of each run in
the original, so it still does.

## Graph readouts

The original graphs were Logger Pro screenshots with statistics boxes (minimum and maximum with their times, mean,
median, standard deviation, sample count, Δ) and integral boxes. Their values were transcribed into
[`data/original/figure-readouts.csv`](../data/original/figure-readouts.csv) and compared with the values
recomputed from the data book.

These boxes come out differently:

{readout_changes_text(differences)}

The table lists the mean and integral of each box. The last column covers every value in the box.

{table(["Figure", "Series", "n", "Mean (original)", "Mean (now)", "Integral (original)", "Integral (now)",
        "All values in the box"], rows)}

## Curve fits (EMF while charging)

The model is EMF = A·e^(−Ct) + B, fitted by least squares. The uncertainties are one standard error. Iteration 2's
original fits were never saved in a Logger Pro file, so their coefficients are the four-digit values on the
original graph. Iteration 3's come from `logger-pro/files/emf v. time, iteration 3.cmbl`.

{fit_section()}

## Effective capacity and energy

The paper defines the effective capacity (energy) as the area under the current (power) curve while the
potential difference is above 0.9 V. The data book used
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
