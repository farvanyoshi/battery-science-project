"""Checks the analysis against the numbers Logger Pro showed on the original graphs."""

import csv
import math
import unittest

import numpy as np

from zinclab.pipeline import ORIGINAL, effective, readouts
from zinclab.loggerpro import column
from zinclab.runs import Column
from zinclab.stats import integral, statistics


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
        s = statistics(column("Voltage & Current v. Time, Iteration 2", "Discharge 1", "Potential Difference"))
        self.assertEqual(s.n, 2881)
        self.assertTrue(close(s.min, 0.3506) and close(s.min_t, 460.8))
        self.assertTrue(close(s.max, 0.6031) and close(s.max_t, 2.000))
        self.assertTrue(close(s.std, 0.05657))

    def test_integral_of_a_known_run(self):
        # "Integral: 3.079 A*min" on the original Current v. Time graph for Discharge 2 of Iteration 2.
        q = integral(column("Voltage & Current v. Time, Iteration 2", "Discharge 2", "Current"))
        self.assertTrue(close(q, 3.079))


class ReadoutTest(unittest.TestCase):
    def test_every_original_readout_is_reproduced(self):
        new = {(r["figure"], r["run"]): r for r in readouts()}
        with (ORIGINAL / "figure-readouts.csv").open(newline="") as f:
            original = [r for r in csv.DictReader(f) if r["kind"] != "fit"]
        self.assertEqual(len(original), 55)
        for o in original:
            n = new[(o["figure"], o["series"])]
            for key in ("min", "max", "mean", "median", "std", "integral"):
                if o[key]:
                    with self.subTest(figure=o["figure"], series=o["series"], quantity=key):
                        self.assertTrue(close(float(n[key]), float(o[key])), (n[key], o[key]))


class EffectiveCapacityTest(unittest.TestCase):
    def test_no_charge_below_the_useful_voltage(self):
        # Iteration 4's first discharge short-circuited and never reached 0.9 V.
        self.assertEqual(effective(4, "Discharge 1"), (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
