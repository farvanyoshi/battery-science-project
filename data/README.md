# Data

Every measurement in this project was recorded with Vernier current and voltage probes on a LabQuest 2. All of
the runs were then copied into one spreadsheet, the data book, which is the raw data for everything in the paper.
The Logger Pro files that the readings first came from are kept separately in [`logger-pro/`](../logger-pro).

| Folder | Contents | Edited by hand? |
|---|---|---|
| `raw/the-data-book.xlsx` | The data book, with one sheet per iteration and one for the NiMH battery | Never (only the saved OneDrive path was removed) |
| `tidy/` | **Generated** by `python -m zinclab tidy`: the data book split into one CSV file per run | Never |
| `processed/` | **Generated** by `python -m zinclab build`: the statistics, fits and tables that Typst reads | Never |
| `original/` | Values typed into the submitted paper or read off its graphs, used to check everything | Only to fix a transcription error |

`tidy/` and `processed/` are committed, so the paper compiles without Python.

## The data book

Each sheet holds one iteration. Row 1 names each run (such as "Discharge 1" or "Charge 2") above its first column,
row 2 has the column headers, and the readings start in row 3. Along with the measured time, potential difference
and current, the book has columns that were worked out from those, such as power, hours, milliamps, normalized
values and running averages, as well as the formulas we used for the effective capacity tables (which turned out
to be wrong, see [`docs/VERIFICATION.md`](../docs/VERIFICATION.md)).

The only change made to the file itself was removing the OneDrive folder path that Excel saves inside it, since it
has a school account ID in it. Every sheet is exactly as it was.

## Tidy files (`tidy/`)

`tidy/<iteration>/<run>.csv` has one row per reading:

| Column | Meaning |
|---|---|
| `book_row` | The row in the data book that the reading came from |
| `time_min` | Time since the start of the run (min) |
| `potential_v` | Potential difference across the battery (V). During the charges of Iterations 2–4, the circuit was opened for these readings, so they are the emf |
| `current_a` | Current (A) |
| `power_w` | Power (W), worked out by the data book as potential difference × current (discharges only) |

Blank cells are missing readings. During the charges of Iterations 2–4, the potential and current were recorded
on alternating readings, so each row only has one of them.

`tidy/runs.csv` lists every run with its load, where it is in the data book, how long it lasted and whether the
paper used it. The runs are numbered the same way as in the paper. The data book numbers Iteration 2 one higher
(its "Discharge 2" is the paper's discharge 1), because it also has a charge before the first discharge, which
is in `iteration-2/initial-charge.csv`. Iteration 1 (the prototype) and the charge of Iteration 5 are also
included, even though the paper did not use them.

## Fixes (`tidy/cleaning.csv`)

Only the measured columns are kept, and a few cells had to be fixed along the way. Every cell that was changed is
listed in `tidy/cleaning.csv` with its row in the data book, its old value and the reason. These are the fixes
(they are written out in `FIXES` in [`analysis/zinclab/book.py`](../analysis/zinclab/book.py)):

- **Iteration 4, discharge 1:** the data book has the potential difference and current columns the wrong way
  round (the "potential" column starts at 1.009, which is the current). They are swapped back.
- **Iteration 3, discharge 1:** 23 readings between 2.53 and 3.27 minutes are removed. The potential drops from
  0.41 V to 0.07 V and then jumps up to 0.65 V, which looks like the probe lost contact for a moment. These
  readings were also struck out in Logger Pro, so they were never in the original graphs.
- **Iteration 5, discharge 2:** the first 4 potential readings are removed, since they were taken before the
  probe settled, and one of them is a 5.087 V spike. These were struck out in Logger Pro as well.
- **Iteration 1, discharge 2:** 27 cells hold broken formulas (`#REF!`) in the data book, so they are left blank.

Apart from these, the tidy data matches the Logger Pro files reading for reading (the tests in
[`analysis/tests/test_book.py`](../analysis/tests/test_book.py) check this). The only differences are in the
last digits of a few readings, which Logger Pro had rounded.

The data book also has the full length of two runs that the paper cut short. Iteration 5's first discharge ran
for 240 minutes, but both of its discharges were cut off at 88 minutes in the paper so they could be compared,
and the last charge of Iteration 2 was logged for 120 minutes, even though every other charge was 60 minutes.
The tidy files keep all of it, while the graphs use the same cutoffs as the paper (`CUTOFF` in
[`analysis/zinclab/spec.py`](../analysis/zinclab/spec.py)).

## Values from the submitted paper (`original/`)

| File | Source |
|---|---|
| `figure-readouts.csv` | The statistics, integral and curve-fit boxes on the 31 Logger Pro graphs in the submitted paper, transcribed from the screenshots |
| `curve-fits.csv` | The charging-curve fits. Iteration 3's coefficients come from `logger-pro/files/emf v. time, iteration 3.cmbl` at full precision. Iteration 2's fits were never saved in a file, so they are the four-digit values shown on the original graph |
| `effective-capacity.csv` | The effective capacity and energy tables as submitted (replaced by `processed/effective-capacity.csv`, see [`docs/VERIFICATION.md`](../docs/VERIFICATION.md)) |
| `internal-resistance.csv` | The internal resistance tables as submitted (the paper still uses these) |

## How the numbers are worked out

These follow the same conventions as Logger Pro, so they can be compared with the original graphs.

- **Statistics** are taken over the readings of a run that are not blank: minimum and maximum (with the time each
  first occurs), mean, median, sample standard deviation, count, and Δ = maximum − minimum.
- **Integrals** use the trapezoidal rule between neighbouring readings, so missing readings are bridged.
- **Curve fits** of the charging emf use the model emf = A·e^(−Ct) + B, fitted by least squares.
- **Effective capacity and energy** are the integrals of current and power from the start of a discharge up to
  the last reading at which the potential difference was still above 0.9 V.
