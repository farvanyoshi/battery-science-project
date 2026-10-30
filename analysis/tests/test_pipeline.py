"""Checks the analysis against the numbers on the original graphs."""

import csv
import math
import unittest

import numpy as np

from zinclab.pipeline import ORIGINAL, effective, fit_for
from zinclab.runs import Column, column
from zinclab.stats import integral, statistics
from zinclab.verify import READOUT_CHANGES, readout_comparison


def close(a, b, digits=4):
    """True when a and b agree to `digits` significant figures (how Logger Pro displays values)."""
    if b == 0:
        return abs(a) < 1e-12
    return abs(a - b) <= 0.5 * 10 ** (math.floor(math.log10(abs(b))) - digits + 1) * 1.0001


class StatsTest(unittest.TestCase):
    def test_integral_bridges_missing_samples(self):
        t = np.array([0.0, 1.0, 2.0, 3.0])
        y = np.array([1.0, np.nan, 1.0, 1.0])
        self.assertAlmostEqual(integral(Column("y", "", t, y)), 3.0)

    def test_statistics_of_a_known_run(self):
        s = statistics(column("iteration-2/discharge-1", "potential_v"))
        self.assertEqual(s.n, 2881)
        self.assertTrue(close(s.min, 0.3506) and close(s.min_t, 460.8))
        self.assertTrue(close(s.max, 0.6031) and close(s.max_t, 2.000))
        self.assertTrue(close(s.std, 0.05657))

    def test_integral_of_a_known_run(self):
        # "Integral: 3.079 A*min" on the original Current v. Time graph for Discharge 2 of Iteration 2.
        self.assertTrue(close(integral(column("iteration-2/discharge-2", "current_a")), 3.079))


class ReadoutTest(unittest.TestCase):
    def test_every_original_readout_is_reproduced_or_explained(self):
        rows, checked, differences = readout_comparison()
        self.assertEqual(len(rows), 55)
        self.assertGreater(checked, 400)
        for figure, series, bad in differences:
            with self.subTest(figure=figure, series=series):
                self.assertIn((figure, series), READOUT_CHANGES, bad)


class FitTest(unittest.TestCase):
    def test_fits_match_the_original_graphs(self):
        with (ORIGINAL / "curve-fits.csv").open(newline="") as f:
            for o in csv.DictReader(f):
                fit, unc = fit_for(o["figure"], o["series"])
                for k in "ABC":
                    with self.subTest(figure=o["figure"], series=o["series"], coefficient=k):
                        self.assertTrue(close(getattr(fit, k), float(o[k])), (getattr(fit, k), o[k]))
                        self.assertTrue(close(getattr(unc, k), float(o[k + "_unc"]), digits=3),
                                        (getattr(unc, k), o[k + "_unc"]))


class EffectiveCapacityTest(unittest.TestCase):
    def test_no_charge_below_the_useful_voltage(self):
        # Iteration 4's first discharge short-circuited and never reached 0.9 V.
        self.assertEqual(effective(4, 1), (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
