"""Checks the tidy data book against the Logger Pro files the original graphs were made from."""

import csv
import unittest

import numpy as np

from zinclab.book import RUNS
from zinclab.loggerpro import CONVERTED
from zinclab.loggerpro import column as logger_pro
from zinclab.runs import TIDY, column

VC = "Voltage & Current v. Time, Iteration {}"
EMF = "emf v. time, iteration {}"
MEASURED = {"potential_v": "Potential Difference", "current_a": "Current"}
DISCHARGE = MEASURED | {"power_w": "Power"}

# Tidy run -> (Logger Pro file, data set, {tidy column: Logger Pro column}). Logger Pro only had a power
# column for the runs that had a power graph.
LOGGER_PRO = {
    **{f"iteration-2/discharge-{d}": (VC.format(2), f"Discharge {d}", DISCHARGE) for d in (1, 2, 3)},
    **{f"iteration-2/charge-{c}": (EMF.format(2), f"Charge {c}", {"potential_v": "EMF", "current_a": "Current"})
       for c in (1, 2, 3)},
    "iteration-3/discharge-1": (VC.format(3), "Discharge 1 (10 ohms)", DISCHARGE),
    "iteration-3/discharge-2": (VC.format(3), "Discharge 2 (1000 ohms)", DISCHARGE),
    "iteration-3/discharge-3": (VC.format(3), "Discharge 3 (100 ohms)", DISCHARGE),
    "iteration-3/modified-discharge": ("Modifed Iteration 3 graphs", "Modified Iteration 3 Discharge", MEASURED),
    **{f"iteration-3/charge-{c}": (EMF.format(3), f"Charge {c}", MEASURED) for c in (1, 2)},
    **{f"iteration-4/discharge-{d}": (VC.format(4), f"Discharge {d}", DISCHARGE) for d in (1, 2, 3)},
    **{f"iteration-4/charge-{c}": (EMF.format(4), f"Charge {c}", MEASURED) for c in (1, 2, 3)},
    **{f"iteration-5/discharge-{d}": (VC.format(5), f"Discharge {d}", DISCHARGE) for d in (1, 2)},
    "commercial/nimh-discharge": ("NiMH Discharge", "NiMH Discharge 1", MEASURED),
}


@unittest.skipUnless(CONVERTED.exists(), "the Logger Pro exports are not available")
class MatchesLoggerProTest(unittest.TestCase):
    def test_every_run_in_the_paper_has_a_logger_pro_counterpart(self):
        self.assertEqual({r.id for r in RUNS if r.used}, set(LOGGER_PRO))

    def test_tidy_data_equals_logger_pro(self):
        """Every Logger Pro reading is in the tidy data (to within Logger Pro's rounding), and every reading
        that Logger Pro had struck out has been removed, so the only differences are listed in cleaning.csv."""
        for run, (source, dataset, columns) in LOGGER_PRO.items():
            for name, lp_name in columns.items():
                with self.subTest(run=run, column=name):
                    ours = column(run, name)
                    theirs = logger_pro(source, dataset, lp_name)
                    index = {round(t, 6): i for i, t in enumerate(ours.t)}
                    for t, y in zip(theirs.t, theirs.y):
                        i = index.get(round(float(t), 6))
                        if i is None:
                            # Iteration 3's first discharge has a blank first row in the book, which Logger Pro
                            # had struck out too.
                            self.assertTrue(np.isnan(y), f"t = {t} is missing from the data book")
                            continue
                        if np.isnan(y):
                            self.assertTrue(np.isnan(ours.y[i]), f"t = {t}: {ours.y[i]} was struck out in Logger Pro")
                        else:
                            self.assertAlmostEqual(ours.y[i], y, delta=1e-6, msg=f"t = {t}")

    def test_cleaning_log_only_touches_what_it_says(self):
        with (TIDY / "cleaning.csv").open(newline="") as f:
            removed = [r for r in csv.DictReader(f) if r["action"] == "removed"]
        for r in removed:
            with self.subTest(run=r["run"], row=r["book_row"], column=r["column"]):
                with (TIDY / f"{r['run']}.csv").open(newline="") as f:
                    row = next(x for x in csv.DictReader(f) if x["book_row"] == r["book_row"])
                self.assertEqual(row[r["column"]], "")


class BookFixesTest(unittest.TestCase):
    def test_iteration_4_discharge_1_columns_are_the_right_way_round(self):
        # The short circuit: 1.009 A through the 10 ohm load at only 0.094 V.
        v = column("iteration-4/discharge-1", "potential_v")
        i = column("iteration-4/discharge-1", "current_a")
        self.assertAlmostEqual(v.y[0], 0.0937, places=4)
        self.assertAlmostEqual(i.y[0], 1.009, places=3)

    def test_no_spike_left_in_iteration_5(self):
        self.assertLess(np.nanmax(column("iteration-5/discharge-2", "potential_v").y), 2.0)


if __name__ == "__main__":
    unittest.main()
