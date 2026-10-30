"""Access to the runs in data/tidy, the cleaned-up data book (see data/README.md)."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
TIDY = REPO / "data" / "tidy"

# Tidy column -> unit.
UNITS = {"time_min": "min", "potential_v": "V", "current_a": "A", "power_w": "W"}


class DataError(ValueError):
    """Raised when a requested run or column does not exist."""


@dataclass(frozen=True)
class Column:
    """One column of a run: the time base and the matching values, both as float arrays.

    Missing cells (blank in the CSV) are NaN. `t` and `y` always have the same length.
    """

    name: str
    unit: str
    t: np.ndarray
    y: np.ndarray

    def between(self, lo: float = -math.inf, hi: float = math.inf) -> Column:
        """The part of the column with lo <= t <= hi."""
        keep = (self.t >= lo) & (self.t <= hi)
        return Column(self.name, self.unit, self.t[keep], self.y[keep])

    def normalized(self) -> Column:
        """Every value divided by the first reading of the run."""
        first = self.y[np.isfinite(self.y)][0]
        return Column(f"normalized {self.name}", "", self.t, self.y / first)


@cache
def _table(run: str) -> tuple[list[str], np.ndarray]:
    path = TIDY / f"{run}.csv"
    if not path.exists():
        raise DataError(f"no tidy run '{run}' in {TIDY}")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    values = np.array([[float(x) if x else np.nan for x in row] for row in rows[1:]], dtype=float)
    return rows[0], values.reshape(len(rows) - 1, len(rows[0]))


def column(run: str, name: str) -> Column:
    """A column of one run, e.g. `column("commercial/nimh-discharge", "current_a")`.

    The time base is the run's time_min column.
    """
    header, values = _table(run)
    if name not in header:
        raise DataError(f"run '{run}' has no column '{name}' (has {header})")
    return Column(name, UNITS[name], values[:, header.index("time_min")], values[:, header.index(name)])
