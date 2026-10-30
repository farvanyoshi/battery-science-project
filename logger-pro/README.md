# Logger Pro files

All of the measurements in this project were recorded with Vernier current and voltage probes on a LabQuest 2,
and they were saved as Logger Pro files (`.cmbl`). The original paper used screenshots of the graphs from these
files. However, all of the same data was also copied into the data book (see [`data/`](../data)), and that is now
what the paper is built from. These files are kept here for reference and as a way to double-check the data book.
Nothing in the paper reads from this folder.

| Folder | Contents |
|---|---|
| `files/` | The 35 battery-related Logger Pro files, exactly as they were saved (the unrelated class labs are left out) |
| `converted/` | One folder per `.cmbl`, with a CSV per data set and a `metadata.json`, exported by `export/` |
| `export/` | The scripts I wrote to get the data out of the `.cmbl` format (see [`export/README.md`](export/README.md)) |

## The files the paper used

Discharges were logged for 8 hours (480 min) and charges for 1 hour.

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

The other files are earlier tests, single runs that were saved straight from the LabQuest (such as
`it 3 discharge 2 (1k ohm)`) before they were combined into the files above, and the first prototype
(`battery science project`, `expo tester` and `normalized curves science project`).

## Converted files

`converted/<file>/dataset_<id>.csv` has one column per Logger Pro column, headed `Name [unit] (id N)`. The rows keep
their original positions, and blank cells are missing values. `metadata.json` lists the data sets and columns, the
saved graphs, Logger Pro's analysis boxes (statistics, integrals and curve fits) as XML, and the SHA-256 of the
source file. `verification.json` is the converter's own cell-by-cell check against the `.cmbl` files.

About 700 cells in these files hold special `Z…` strings instead of numbers, and they are exported as missing
values. As far as I can tell, these are readings that were struck out in Logger Pro, since Logger Pro skips them
in its statistics too. In the runs the paper uses, the data book still has two of these stretches, and they are
removed in the same way when the data book is cleaned up (see [`data/README.md`](../data/README.md)).

To export everything again, run `make convert` from the top of the repository. It takes a while, and it only ever
writes to `build/cmbl` and `converted/`.
