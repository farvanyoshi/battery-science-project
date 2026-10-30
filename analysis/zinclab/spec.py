"""Which data each graph in the paper shows.

Every figure is named after its file in assets/figures/ and carries the label the paper
uses to reference it (`@C2-D1` etc.). The readout says which of Logger Pro's analysis
boxes the original graph had: statistics, an integral, or a curve fit.
"""

from __future__ import annotations

from dataclasses import dataclass

VC = "Voltage & Current v. Time, Iteration {}"
EMF = "emf v. time, iteration {}"
MODIFIED = "Modifed Iteration 3 graphs"  # sic, the original file name
NIMH = "NiMH Discharge"
NORMALIZED = "looks ugly"  # the file that holds every normalized run

POTENTIAL = "Potential Difference"

# Series colours, always assigned in this order (a colour-blind-safe categorical palette).
# The readout tables under each graph reuse them through data/processed/readouts.csv.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]


@dataclass(frozen=True)
class Trace:
    source: str  # Logger Pro file (folder in logger-pro/converted)
    run: str  # data set inside that file
    column: str
    label: str  # name in the legend and readout table


@dataclass(frozen=True)
class Figure:
    name: str
    label: str
    ylabel: str
    traces: tuple[Trace, ...]
    stats: bool = True
    integral: bool = False
    fit: bool = False
    sparse: bool = False  # charge readings every few minutes: draw markers, not a line


def _discharges(it: int, column: str, runs: list[str], labels: list[str] | None = None) -> tuple[Trace, ...]:
    labels = labels or runs
    return tuple(Trace(VC.format(it), r, column, l) for r, l in zip(runs, labels))


_IT3 = ["Discharge 1 (10 ohms)", "Discharge 2 (1000 ohms)", "Discharge 3 (100 ohms)"]
_IT3_LABELS = ["Discharge 1 (10 Ω)", "Discharge 2 (1000 Ω)", "Discharge 3 (100 Ω)"]
_D123 = ["Discharge 1", "Discharge 2", "Discharge 3"]
_C123 = ["Charge 1", "Charge 2", "Charge 3"]


def _iteration(it: int, runs: list[str], labels: list[str], charges: list[str], emf_column: str, fit: bool) -> list[Figure]:
    figs = [Figure(f"potential-{it}", f"Pot{it}", "Potential difference (V)", _discharges(it, POTENTIAL, runs, labels))]
    for k, (r, l) in enumerate(zip(runs, labels), start=1):
        figs.append(Figure(f"current-{it}-d{k}", f"C{it}-D{k}", "Current (A)", _discharges(it, "Current", [r], [l]), integral=True))
    if it == 3:
        figs += [
            Figure("potential-3b", "Pot3b", "Potential difference (V)", (Trace(MODIFIED, "Modified Iteration 3 Discharge", POTENTIAL, "Modified Iteration 3"),)),
            Figure("current-3b", "C3b", "Current (A)", (Trace(MODIFIED, "Modified Iteration 3 Discharge", "Current", "Modified Iteration 3"),), integral=True),
        ]
    emf = tuple(Trace(EMF.format(it), c, emf_column, c) for c in charges)
    cur = tuple(Trace(EMF.format(it), c, "Current", c) for c in charges)
    figs += [
        Figure(f"emf-{it}", f"Ch{it}", "EMF (V)", emf, stats=not fit, fit=fit, sparse=True),
        Figure(f"charge-current-{it}", f"C{it}-C", "Current (A)", cur, integral=True, sparse=True),
    ]
    return figs


FIGURES: list[Figure] = [
    *_iteration(2, _D123, _D123, _C123, "EMF", fit=True),
    *_iteration(3, _IT3, _IT3_LABELS, _C123[:2], POTENTIAL, fit=True),
    *_iteration(4, _D123, _D123, _C123, POTENTIAL, fit=False),
    Figure("potential-5", "Pot5", "Potential difference (V)", _discharges(5, POTENTIAL, _D123[:2])),
    Figure("current-5-d1", "C5-D1", "Current (A)", _discharges(5, "Current", ["Discharge 1"]), integral=True),
    Figure("current-5-d2", "C5-D2", "Current (A)", _discharges(5, "Current", ["Discharge 2"]), integral=True),
    Figure("potential-nimh", "PotS", "Potential difference (V)", (Trace(NIMH, "NiMH Discharge 1", POTENTIAL, "NiMH"),)),
    Figure("current-nimh", "CS", "Current (A)", (Trace(NIMH, "NiMH Discharge 1", "Current", "NiMH"),), integral=True),
    Figure("power-2", "P2", "Power (W)", _discharges(2, "Power", _D123), stats=False, integral=True),
    Figure("power-3", "P3", "Power (W)", _discharges(3, "Power", _IT3, _IT3_LABELS), integral=True),
    Figure("power-4", "P4", "Power (W)", _discharges(4, "Power", _D123), integral=True),
    Figure("power-5", "P5", "Power (W)", _discharges(5, "Power", _D123[:2]), integral=True),
    Figure(
        "normalized-potential",
        "Vnorm",
        "Normalized potential difference",
        tuple(
            Trace(NORMALIZED, f"Iteration {i}, Discharge 1", "Normalized Potential Difference", f"Iteration {i}")
            for i in (2, 3, 4, 5)
        ),
    ),
    Figure(
        "normalized-current",
        "Cnorm",
        "Normalized current",
        tuple(
            Trace(NORMALIZED, f"Iteration {i}, Discharge {d}", "Normalized Current", f"Iteration {i}, Discharge {d}")
            for i, d in ((3, 1), (4, 1), (5, 2))
        ),
    ),
]

BY_LABEL = {f.label: f for f in FIGURES}
