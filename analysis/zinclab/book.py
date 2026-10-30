"""Turns the data book (data/raw/the-data-book.xlsx) into the tidy CSV files in data/tidy.

Each sheet of the book holds one iteration. Row 1 names each run ("Discharge 1", "Charge 2", ...)
above its first column, row 2 holds the column headers and the readings start in row 3. Only the
measured columns are kept (time, potential difference, current) along with the power, which the
book works out as potential difference times current. The book's other columns (hours, mA, ratios,
normalized values, running averages) can all be worked out again from these.

Every change made to the book's values is listed in FIXES and written to data/tidy/cleaning.csv.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from zinclab.runs import REPO, TIDY

BOOK = REPO / "data" / "raw" / "the-data-book.xlsx"

# Book header (row 2) -> tidy column. Anything else in a run's block of columns is left out.
COLUMNS = {
    "Time (min)": "time_min",
    "Potential(V)": "potential_v",
    "Potential (V)": "potential_v",
    "Voltage (V)": "potential_v",
    "Current(A)": "current_a",
    "Current (A)": "current_a",
    "Power (W)": "power_w",
}
ORDER = ["time_min", "potential_v", "current_a", "power_w"]


@dataclass(frozen=True)
class Run:
    id: str  # path under data/tidy without ".csv", e.g. "iteration-2/discharge-1"
    name: str  # name used in the paper
    sheet: str
    label: str  # the run's name in row 1 of the sheet
    load_ohm: int | None = None
    used: bool = True  # shown in the paper
    notes: str = ""


RUNS: list[Run] = [
    Run("iteration-1/discharge-1", "Discharge 1", "Iteration 1", "Discharge 1", used=False,
        notes="Prototype; the book notes an emf of 1.06 V"),
    Run("iteration-1/discharge-2", "Discharge 2", "Iteration 1", "Discharge 2", used=False,
        notes="Prototype; the book notes an emf of 1.28 V"),
    Run("iteration-1/discharge-3", "Discharge 3", "Iteration 1", "Discharge 3", used=False,
        notes="Prototype; the book notes an emf of 1.26 V"),
    Run("iteration-1/aa-discharge", "AA discharge", "Iteration 1", "AA Discharge", used=False,
        notes="A commercial AA cell, discharged alongside the prototype"),
    Run("iteration-1/charge-1", "Charge 1", "Iteration 1", "Charge 1", used=False,
        notes="Prototype; the book notes an emf of 0.332 V"),
    Run("iteration-1/charge-2-emf", "Charge 2 (emf)", "Iteration 1", "emf while charging 2", used=False,
        notes="Prototype; emf readings only"),
    Run("iteration-2/initial-charge", "Initial charge", "Iteration 2", "Charge 1", used=False,
        notes="Charge before the first discharge in the paper"),
    Run("iteration-2/discharge-1", "Discharge 1", "Iteration 2", "Discharge 2", 100),
    Run("iteration-2/charge-1", "Charge 1", "Iteration 2", "Charge 2",
        notes="The current at 12.5 min is the average of its neighbours in the book"),
    Run("iteration-2/discharge-2", "Discharge 2", "Iteration 2", "Discharge 3", 100),
    Run("iteration-2/charge-2", "Charge 2", "Iteration 2", "Charge 3"),
    Run("iteration-2/discharge-3", "Discharge 3", "Iteration 2", "Discharge 4", 100),
    Run("iteration-2/charge-3", "Charge 3", "Iteration 2", "Charge 4",
        notes="Logged for 120 min; the paper uses the first 60 min like the other charges"),
    Run("iteration-3/discharge-1", "Discharge 1", "Iteration 3", "Discharge 1", 10),
    Run("iteration-3/charge-1", "Charge 1", "Iteration 3", "Charge 1"),
    Run("iteration-3/discharge-2", "Discharge 2", "Iteration 3", "Discharge 2", 1000),
    Run("iteration-3/charge-2", "Charge 2", "Iteration 3", "Charge 2"),
    Run("iteration-3/discharge-3", "Discharge 3", "Iteration 3", "Discharge 3", 100),
    Run("iteration-3/modified-discharge", "Modified Iteration 3", "Iteration 3", "Iteration 3b",
        notes="Iteration 3's cathode in zinc sulfate"),
    Run("iteration-4/discharge-1", "Discharge 1", "Iteration 4", "Discharge 1", 10),
    Run("iteration-4/charge-1", "Charge 1", "Iteration 4", "Charge 1"),
    Run("iteration-4/discharge-2", "Discharge 2", "Iteration 4", "Discharge 2", 1000),
    Run("iteration-4/charge-2", "Charge 2", "Iteration 4", "Charge 2"),
    Run("iteration-4/discharge-3", "Discharge 3", "Iteration 4", "Discharge 3", 100),
    Run("iteration-4/charge-3", "Charge 3", "Iteration 4", "Charge 3"),
    Run("iteration-5/discharge-1", "Discharge 1", "Iteration 5", "Discharge 1", 1000,
        notes="Logged for 240 min; the paper uses the first 88 min to match discharge 2"),
    Run("iteration-5/charge-1", "Charge 1", "Iteration 5", "Charge 1", used=False,
        notes="Not used in the paper because chlorine gas made it unreliable"),
    Run("iteration-5/discharge-2", "Discharge 2", "Iteration 5", "Discharge 2", 10),
    Run("commercial/nimh-discharge", "NiMH discharge", "Commercial", "NiMH Discharge 1", 1000),
]
BY_ID = {r.id: r for r in RUNS}


@dataclass(frozen=True)
class Swap:
    """The book has two columns of a run the wrong way round."""

    run: str
    a: str
    b: str
    reason: str


@dataclass(frozen=True)
class Drop:
    """Readings that are removed (left blank), for samples with t_from <= time <= t_to."""

    run: str
    columns: tuple[str, ...]
    t_from: float
    t_to: float
    reason: str


FIXES: list[Swap | Drop] = [
    Swap("iteration-4/discharge-1", "potential_v", "current_a",
         "The book has the potential difference and current columns swapped for this run"),
    Drop("iteration-3/discharge-1", ("potential_v", "current_a", "power_w"), 2.53, 3.27,
         "Probe glitch: the potential drops from 0.41 V to 0.07 V and jumps to 0.65 V (struck out in Logger Pro)"),
    Drop("iteration-5/discharge-2", ("potential_v", "power_w"), 0.0, 0.1,
         "Readings before the probe settled, including a 5.087 V spike (struck out in Logger Pro)"),
]

# Cell values that Excel stores for broken formulas.
ERRORS = {"#REF!", "#VALUE!", "#DIV/0!", "#N/A", "#NAME?", "#NUM!", "#NULL!"}


def _sheets() -> dict[str, list[tuple]]:
    from openpyxl import load_workbook

    wb = load_workbook(BOOK, read_only=True, data_only=True)
    try:
        return {ws.title: list(ws.iter_rows(values_only=True)) for ws in wb.worksheets}
    finally:
        wb.close()


def _cell(rows: list[tuple], r: int, c: int):
    """The value at 0-based row r and column c (None past the edge)."""
    row = rows[r] if r < len(rows) else ()
    return row[c] if c < len(row) else None


def _number(value) -> float | None:
    return None if value is None or isinstance(value, str) else float(value)


def _columns(rows: list[tuple], run: Run) -> dict[str, int]:
    """Where each tidy column of a run is in its sheet (0-based column numbers)."""
    width = max(len(r) for r in rows[:2])
    starts = [c for c in range(width) if _cell(rows, 0, c) == run.label and _cell(rows, 1, c) == "Time (min)"]
    if not starts:
        raise ValueError(f"'{run.sheet}' has no run labelled '{run.label}'")
    # Iteration 2 labels the normalized columns of Discharge 3 with the run name again, so the
    # run itself is always the first block with that label.
    found = {}
    c = starts[0]
    while (header := _cell(rows, 1, c)) is not None:
        name = COLUMNS.get(str(header).strip())
        if name and name not in found:
            found[name] = c
        c += 1
    return found


def _fmt(x: float | None) -> str:
    return "" if x is None else repr(x)


def tidy() -> list[Path]:
    """Write every run to data/tidy/<id>.csv, plus runs.csv and cleaning.csv."""
    sheets = _sheets()
    cleaning: list[dict] = []
    index: list[dict] = []
    paths: list[Path] = []

    def log(run: str, row: int | str, column: str, value, action: str, reason: str) -> None:
        cleaning.append({"run": run, "book_row": row, "column": column, "book_value": "" if value is None else value,
                         "action": action, "reason": reason})

    for run in RUNS:
        rows = sheets[run.sheet]
        where = _columns(rows, run)
        columns = [c for c in ORDER if c in where]
        data = []
        for r in range(2, len(rows)):
            raw = {c: _cell(rows, r, where[c]) for c in columns}
            if raw["time_min"] is None:
                continue
            values = {}
            for c, v in raw.items():
                if isinstance(v, str) and v.strip() in ERRORS:
                    log(run.id, r + 1, c, v, "removed", "Broken formula in the book")
                values[c] = _number(v)
            data.append({"book_row": r + 1, **values})

        for fix in FIXES:
            if fix.run != run.id:
                continue
            if isinstance(fix, Swap):
                for d in data:
                    d[fix.a], d[fix.b] = d[fix.b], d[fix.a]
                log(run.id, f"{data[0]['book_row']}-{data[-1]['book_row']}", f"{fix.a}, {fix.b}", None, "swapped",
                    fix.reason)
            else:
                for d in data:
                    if fix.t_from <= d["time_min"] <= fix.t_to:
                        for c in fix.columns:
                            if d.get(c) is not None:
                                log(run.id, d["book_row"], c, d[c], "removed", fix.reason)
                                d[c] = None

        path = TIDY / f"{run.id}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["book_row", *columns])
            for d in data:
                w.writerow([d["book_row"], *(_fmt(d[c]) for c in columns)])
        paths.append(path)

        times = [d["time_min"] for d in data]
        index.append({
            "id": run.id,
            "name": run.name,
            "iteration": run.id.split("/")[0].removeprefix("iteration-") if run.id.startswith("iteration") else "",
            "load_ohm": "" if run.load_ohm is None else run.load_ohm,
            "book_sheet": run.sheet,
            "book_label": run.label,
            "samples": len(data),
            "duration_min": f"{max(times) - min(times):.4g}",
            "used_in_paper": "yes" if run.used else "no",
            "notes": run.notes,
        })

    for name, rows in (("runs.csv", index), ("cleaning.csv", cleaning)):
        path = TIDY / name
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        paths.append(path)
    return paths
