# Data

Every measurement in this project was recorded with Vernier current and voltage probes on a LabQuest 2 and saved
as a Logger Pro file (`.cmbl`). The folders are:

| Folder | Contents | Edited by hand? |
|---|---|---|
| `raw/` | The 35 battery-related Logger Pro files, byte-for-byte as saved (unrelated class labs are left out) | Never |
| `converted/` | One folder per `.cmbl` with a CSV per data set and `metadata.json`, exported by [`tools/cmbl-export`](../tools/cmbl-export) | Never (regenerate with `make convert`) |
| `original/` | Values typed into the submitted paper or read off its graphs, used to check the reproduction | Only to fix a transcription error |
| `processed/` | **Generated** by `python -m zinclab build` (see [`analysis/`](../analysis)) and read by Typst | Never |

`processed/` is committed, so the paper compiles without Python.

## The runs used in the paper

Discharges were logged for 8 hours (480 min) and charges for 1 hour. The figure labels are the ones used in the paper.

| Logger Pro file | Runs | Sampling | Figures |
|---|---|---|---|
| `Voltage & Current v. Time, Iteration 2` | Discharge 1–3 (100 Ω) | every 10 s | Pot2, C2-D1–D3, P2 |
| `Voltage & Current v. Time, Iteration 3` | Discharge 1 (10 Ω), 2 (1000 Ω), 3 (100 Ω) | every 2 s | Pot3, C3-D1–D3, P3 |
| `Voltage & Current v. Time, Iteration 4` | Discharge 1–3 (10, 1000, 100 Ω) | every 2 s | Pot4, C4-D1–D3, P4 |
| `Voltage & Current v. Time, Iteration 5` | Discharge 1 (1000 Ω), 2 (10 Ω), both cut off at 88 min | every 1 s / 2 s | Pot5, C5-D1, C5-D2, P5 |
| `emf v. time, iteration 2` | Charge 1–3 | every 2.5 min (EMF and current on alternate readings) | Ch2, C2-C |
| `emf v. time, iteration 3` | Charge 1–2 | every 1 min (EMF every 5 min) | Ch3, C3-C |
| `emf v. time, iteration 4` | Charge 1–3 | every 1 min (EMF every 5 min) | Ch4, C4-C |
| `Modifed Iteration 3 graphs` | Modified Iteration 3 discharge (Iteration 3 cathode in zinc sulfate) | every 2 s | Pot3b, C3b |
| `NiMH Discharge` | AA NiMH discharge (1000 Ω) | every 2 s | PotS, CS |
| `looks ugly` | Normalized potential, current and power of every discharge | as above | Vnorm, Cnorm |

The other files are earlier tests, single runs saved straight from the LabQuest (`it 3 discharge 2 (1k ohm)` etc.)
before they were combined into the files above, and the first prototype (`battery science project`,
`expo tester`, `normalized curves science project`). They are kept for completeness.

Units are as saved: time in minutes, potential difference and EMF in volts, current in amperes. Power is the
calculated column `"Potential Difference" * "Current"` from Logger Pro, recomputed from its saved formula. The
normalized columns are each value divided by the first value of its run.

## Converted files

`converted/<file>/dataset_<id>.csv` has one column per Logger Pro column, headed `Name [unit] (id N)`. Rows keep
their original positions, and blank cells are missing values. `metadata.json` lists the data sets and columns, the
saved graphs, Logger Pro's analysis boxes (statistics, integrals, curve fits) as XML, and the SHA-256 of the source
file. `verification.json` is the converter's own cell-by-cell check against the `.cmbl` files.

About 700 cells in the source files hold special `Z…` strings instead of numbers. They are exported as missing
values. Logger Pro treats them the same way: the statistics recomputed here (which skip them) match the sample
counts on the original graphs exactly.

## Values from the submitted paper (`original/`)

| File | Source |
|---|---|
| `figure-readouts.csv` | The statistics, integral and curve-fit boxes on the 31 Logger Pro graphs in the submitted paper, transcribed from the screenshots |
| `curve-fits.csv` | The charging-curve fits. Iteration 3's coefficients come from `raw/emf v. time, iteration 3.cmbl` at full precision. Iteration 2's fits were never saved in a file, so they are the four-digit values shown on the original graph |
| `effective-capacity.csv` | The effective capacity and energy tables as submitted (superseded by `processed/effective-capacity.csv`, see [`docs/VERIFICATION.md`](../docs/VERIFICATION.md)) |
| `internal-resistance.csv` | The internal resistance tables as submitted |

## Analysis conventions (matching Logger Pro)

- **Statistics** are taken over the finite samples of a run: minimum and maximum (with the time each first
  occurs), mean, median, sample standard deviation, count, and Δ = maximum − minimum.
- **Integrals** use the trapezoidal rule between consecutive finite samples, so missing readings are bridged.
- **Effective capacity and energy** are the integrals of current and power from the start of a discharge up to
  the last sample at which the potential difference was still above 0.9 V.
