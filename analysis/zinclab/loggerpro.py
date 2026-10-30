"""Access to the Logger Pro runs exported to logger-pro/converted (see logger-pro/README.md).

The paper is built from the data book instead. This is only used to check the data book against Logger Pro.
"""

from __future__ import annotations

import csv
import json
import re
from functools import cache

import numpy as np

from zinclab.runs import REPO, Column, DataError

CONVERTED = REPO / "logger-pro" / "converted"

# CSV headers look like "Potential Difference [V] (id 104)".
_HEADER = re.compile(r"^(?P<name>.*?) \[(?P<unit>.*)\] \(id (?P<id>\d+)\)$")


@cache
def _metadata(source: str) -> dict:
    path = CONVERTED / source / "metadata.json"
    if not path.exists():
        raise DataError(f"no converted Logger Pro file named '{source}' in {CONVERTED}")
    return json.loads(path.read_text(encoding="utf-8"))


@cache
def _table(source: str, run: str) -> tuple[list[tuple[str, str]], np.ndarray]:
    datasets = [d for d in _metadata(source)["datasets"] if d["name"] == run]
    if len(datasets) != 1:
        raise DataError(f"'{source}' has {len(datasets)} runs named '{run}'")
    with (CONVERTED / source / datasets[0]["csv"]).open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = []
    for cell in rows[0]:
        m = _HEADER.match(cell)
        if not m:
            raise DataError(f"unexpected column header '{cell}' in '{source}'")
        header.append((m["name"], m["unit"]))
    values = np.array([[float(x) if x else np.nan for x in row] for row in rows[1:]], dtype=float)
    return header, values.reshape(len(rows) - 1, len(header))


def column(source: str, run: str, name: str) -> Column:
    """A column of one run, e.g. `column("NiMH Discharge", "NiMH Discharge 1", "Current")`.

    The time base is the run's "Time" column (minutes).
    """
    header, values = _table(source, run)
    names = [n for n, _ in header]
    if name not in names:
        raise DataError(f"run '{run}' in '{source}' has no column '{name}' (has {names})")
    t = values[:, names.index("Time")]
    i = names.index(name)
    return Column(name, header[i][1], t, values[:, i])
