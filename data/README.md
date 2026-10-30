# Data

Every measurement in this project was recorded with Vernier current and voltage probes on a LabQuest 2 and saved
as a Logger Pro file (`.cmbl`). Those files and their CSV exports are in [`logger-pro/`](../logger-pro). The folders here are:

| Folder | Contents | Edited by hand? |
|---|---|---|
| `raw/the-data-book.xlsx` | The data book: the spreadsheet where we gathered all of the data for the project, one sheet per iteration | Never (only the saved OneDrive path was removed) |
| `original/` | Values typed into the submitted paper or read off its graphs, used to check the reproduction | Only to fix a transcription error |
| `processed/` | **Generated** by `python -m zinclab build` (see [`analysis/`](../analysis)) and read by Typst | Never |

`processed/` is committed, so the paper compiles without Python.

## Values from the submitted paper (`original/`)

| File | Source |
|---|---|
| `figure-readouts.csv` | The statistics, integral and curve-fit boxes on the 31 Logger Pro graphs in the submitted paper, transcribed from the screenshots |
| `curve-fits.csv` | The charging-curve fits. Iteration 3's coefficients come from `logger-pro/files/emf v. time, iteration 3.cmbl` at full precision. Iteration 2's fits were never saved in a file, so they are the four-digit values shown on the original graph |
| `effective-capacity.csv` | The effective capacity and energy tables as submitted (superseded by `processed/effective-capacity.csv`, see [`docs/VERIFICATION.md`](../docs/VERIFICATION.md)) |
| `internal-resistance.csv` | The internal resistance tables as submitted |

## Analysis conventions (matching Logger Pro)

- **Statistics** are taken over the finite samples of a run: minimum and maximum (with the time each first
  occurs), mean, median, sample standard deviation, count, and Δ = maximum − minimum.
- **Integrals** use the trapezoidal rule between consecutive finite samples, so missing readings are bridged.
- **Effective capacity and energy** are the integrals of current and power from the start of a discharge up to
  the last sample at which the potential difference was still above 0.9 V.
