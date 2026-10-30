"""Which data each graph in the paper shows.

Every figure is named after its file in assets/figures/ and carries the label the paper
uses to reference it (`@C2-D1` etc.). The readout says which analysis boxes the original
graph had: statistics, an integral, or a curve fit.
"""

from __future__ import annotations

from dataclasses import dataclass

from zinclab.runs import Column, column

POTENTIAL = "potential_v"
CURRENT = "current_a"
POWER = "power_w"

# Series colours, always assigned in this order (a colour-blind-safe categorical palette).
# The readout tables under each graph reuse them through data/processed/readouts.csv.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]

# The paper only used the start of two runs that the data book has in full. Iteration 5's discharges
# were cut off at the end of discharge 2 "to ensure the data would be comparable" (discussion of
# @Pot5), and every charge was 60 minutes long, even though the last one of Iteration 2 was logged
# for 120 minutes.
CUTOFF = {
    "iteration-5/discharge-1": 88.37,
    "iteration-2/charge-3": 60.0,
}


def paper_column(run: str, name: str) -> Column:
    """A column of a run, cut off where the paper cut it off."""
    col = column(run, name)
    return col.between(hi=CUTOFF[run]) if run in CUTOFF else col


@dataclass(frozen=True)
class Trace:
    run: str  # tidy run id (data/tidy/<run>.csv)
    column: str
    label: str  # name in the legend and readout table
    normalized: bool = False  # divide by the first reading
    full: bool = False  # ignore CUTOFF (the original normalized graph showed all of each run)

    def data(self) -> Column:
        col = column(self.run, self.column) if self.full else paper_column(self.run, self.column)
        return col.normalized() if self.normalized else col


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


def run(it: int, kind: str, k: int) -> str:
    return f"iteration-{it}/{kind}-{k}"


# Loads of each discharge, used in the legends of Iteration 3's graphs.
_IT3_LABELS = ["Discharge 1 (10 Ω)", "Discharge 2 (1000 Ω)", "Discharge 3 (100 Ω)"]


def _discharges(it: int, column: str, labels: list[str]) -> tuple[Trace, ...]:
    return tuple(Trace(run(it, "discharge", k), column, l) for k, l in enumerate(labels, start=1))


def _iteration(it: int, labels: list[str], charges: int, fit: bool) -> list[Figure]:
    figs = [Figure(f"potential-{it}", f"Pot{it}", "Potential difference (V)", _discharges(it, POTENTIAL, labels))]
    for k, l in enumerate(labels, start=1):
        figs.append(Figure(f"current-{it}-d{k}", f"C{it}-D{k}", "Current (A)",
                           (Trace(run(it, "discharge", k), CURRENT, l),), integral=True))
    if it == 3:
        modified = "iteration-3/modified-discharge"
        figs += [
            Figure("potential-3b", "Pot3b", "Potential difference (V)", (Trace(modified, POTENTIAL, "Modified Iteration 3"),)),
            Figure("current-3b", "C3b", "Current (A)", (Trace(modified, CURRENT, "Modified Iteration 3"),), integral=True),
        ]
    emf = tuple(Trace(run(it, "charge", c), POTENTIAL, f"Charge {c}") for c in range(1, charges + 1))
    cur = tuple(Trace(run(it, "charge", c), CURRENT, f"Charge {c}") for c in range(1, charges + 1))
    figs += [
        Figure(f"emf-{it}", f"Ch{it}", "EMF (V)", emf, stats=not fit, fit=fit, sparse=True),
        Figure(f"charge-current-{it}", f"C{it}-C", "Current (A)", cur, integral=True, sparse=True),
    ]
    return figs


_D123 = ["Discharge 1", "Discharge 2", "Discharge 3"]
NIMH = "commercial/nimh-discharge"

FIGURES: list[Figure] = [
    *_iteration(2, _D123, 3, fit=True),
    *_iteration(3, _IT3_LABELS, 2, fit=True),
    *_iteration(4, _D123, 3, fit=False),
    Figure("potential-5", "Pot5", "Potential difference (V)", _discharges(5, POTENTIAL, _D123[:2])),
    Figure("current-5-d1", "C5-D1", "Current (A)", (Trace(run(5, "discharge", 1), CURRENT, "Discharge 1"),), integral=True),
    Figure("current-5-d2", "C5-D2", "Current (A)", (Trace(run(5, "discharge", 2), CURRENT, "Discharge 2"),), integral=True),
    Figure("potential-nimh", "PotS", "Potential difference (V)", (Trace(NIMH, POTENTIAL, "NiMH"),)),
    Figure("current-nimh", "CS", "Current (A)", (Trace(NIMH, CURRENT, "NiMH"),), integral=True),
    Figure("power-2", "P2", "Power (W)", _discharges(2, POWER, _D123), stats=False, integral=True),
    Figure("power-3", "P3", "Power (W)", _discharges(3, POWER, _IT3_LABELS), integral=True),
    Figure("power-4", "P4", "Power (W)", _discharges(4, POWER, _D123), integral=True),
    Figure("power-5", "P5", "Power (W)", _discharges(5, POWER, _D123[:2]), integral=True),
    Figure(
        "normalized-potential",
        "Vnorm",
        "Normalized potential difference",
        tuple(Trace(run(i, "discharge", 1), POTENTIAL, f"Iteration {i}", normalized=True, full=True) for i in (2, 3, 4, 5)),
    ),
    Figure(
        "normalized-current",
        "Cnorm",
        "Normalized current",
        tuple(
            Trace(run(i, "discharge", d), CURRENT, f"Iteration {i}, Discharge {d}", normalized=True, full=True)
            for i, d in ((3, 1), (4, 1), (5, 2))
        ),
    ),
]

BY_LABEL = {f.label: f for f in FIGURES}
