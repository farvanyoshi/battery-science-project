# cmbl-export

Converts Logger Pro `.cmbl` files into CSV files. It was written to recover the raw data behind the paper's
graphs, since Logger Pro only saved it inside its own file format.

- `convert.py` reads every `.cmbl` in the current folder (gzip-compressed or plain XML) and writes
  `converted/<file>/`: a CSV per data set, the original cell text, `metadata.json`, an XML working copy, and every
  saved graph redrawn in two styles. Calculated columns (such as Power) are recomputed from their saved formulas.
- `render_graphs.py` redraws the saved graphs and recomputes Logger Pro's integral and statistics boxes.
- `validate_archive.py` checks every exported cell against the source XML and writes `verification.json`.
- `collect.py` copies the CSV files and metadata that this repository keeps into `data/converted`.

Run it with `make convert` from the repository root. It works in `build/cmbl` and never touches `data/raw`.
