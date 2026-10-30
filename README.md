# Evaluating the Potential of Zinc-ion Batteries

This was a high school science project by Nirvan Joshi and Sebastian Ruiz (2024–25), where we built our own
zinc-ion batteries out of consumer-grade materials to see how well they could actually perform. We wrote it up as
a research paper and typeset it with [Typst](https://typst.app).

## Reading the paper

I noticed while pushing this to GitHub that there were some errors in the graphs and tables, and so those have
been updated accordingly. The paper that was actually presented to the science fair can be found at
[`docs/original-paper.pdf`](docs/original-paper.pdf), while the fixed paper is available under
[Releases](https://github.com/farvanyoshi/battery-science-project/releases/latest). None of the experiments were
redone, and the text is the same apart from the corrections and some spelling and grammar fixes. Everything that
changed is listed in [What was fixed](#what-was-fixed) below.

## What we did

Each battery had a zinc foil anode and a cathode made from a paste of activated carbon and graphite powder packed
around a graphite rod, all inside a 3D-printed casing. We built five iterations of the battery, the first of which
was only a prototype. Between the other four, we changed the electrolyte (from zinc sulfate to **zinc chloride**
at higher and higher concentrations) and the cathode, and in the last iteration we added **manganese dioxide**.
The batteries were discharged across 10, 100 and 1000 Ω loads for up to 8 hours and recharged between discharges.
A Vernier LabQuest 2 logged the current and voltage, while an Arduino-timed relay opened the charging circuit
every few minutes so that the emf could be read. Lastly, an AA NiMH battery was discharged the same way for
comparison.

## Key results

| | Iteration 2 | Iteration 3 | Iteration 4 | Iteration 5 | AA NiMH |
|---|---|---|---|---|---|
| Electrolyte | 1.5 M ZnSO₄ | 1.5 M ZnCl₂ | 3 M ZnCl₂ | 6 M ZnCl₂ | KOH |
| Cathode | carbon + graphite | carbon + graphite | extra graphite | carbon + graphite + **MnO₂** | — |
| Highest terminal voltage (V) | 1.018 | 1.164 | 0.993 | **2.093** | 1.287 |
| Best effective capacity above 0.9 V (A·min) | 0.198 | 0.188 | 0.029 | **1.125** | — |
| Best effective energy above 0.9 V (W·min) | 0.186 | 0.183 | 0.027 | **1.400** | — |

All of these values are worked out from the data book, in `data/processed/`.

- Iteration 1 was used for testing whether the design was feasible and as such proper measurements were not taken
  of the data. For this reason, it is not included in data analysis.
- Iteration 5 was the only battery that showed a real battery-like discharge. It stayed above 1.8 V for about
  40 minutes across 1000 Ω before dropping off, and it gave by far the most useful charge and energy.
- Iteration 4 short-circuited on its first discharge, pushing 1.009 A through a 10 Ω load at only 0.094 V.
- Zinc chloride allowed for higher voltages than zinc sulfate. However, charging Iteration 5 at 2.2–2.4 V released
  chlorine gas.
- Even Iteration 5's second discharge (2.106 A·min, or about 35 mAh in 88 minutes) is still far from the
  ~1100 mAh of an AA NiMH battery.

## What was fixed

All of the data for this project was collected into one spreadsheet, the data book, which is now in
[`data/raw/`](data/raw). For the paper, we made the graphs in Logger Pro and pasted screenshots of them in, while
the tables were worked out in the data book. When I went back through all of it, a few things turned out to be
wrong:

- **The graphs.** All 31 graphs are now redrawn with Python straight from the data book, instead of being
  screenshots from Logger Pro. They show the same data, and the statistics, integrals and curve fits under each
  graph match the original ones. While doing this, though, I found that the data book has the voltage and current
  columns swapped for the first discharge of Iteration 4. The original normalized graphs were made from those
  columns, so the Iteration 4 curve in the normalized voltage graph was actually its current, and the other way
  around in the normalized current graph. Those two graphs are fixed. A few values under the other graphs also
  changed in the last digit, since the data book has some readings that Logger Pro had rounded.
- **The effective capacity and energy tables were wrong.** The formula in the data book added up the readings
  instead of integrating over time, so the values were 6 times (Iteration 2) or 30 times (Iterations 3 and 4) too
  large, and three of the cells read the wrong columns. The corrected values change one of our conclusions:
  Iteration 5, not Iteration 3, had the greatest effective capacity and energy.
- Four numbers in the text were wrong, such as 0.02708 A instead of 0.002708 A and the sampling rate of Iteration 2.
- The internal resistance tables could only be partly checked, since some of the emf readings they were worked out
  from were never saved. Thus, they have been left as they were.

The data itself only needed a couple of small fixes, which are explained in [`data/README.md`](data/README.md).
Every value that was checked, every change and the reason for it are in
[`docs/VERIFICATION.md`](docs/VERIFICATION.md).

## Repository layout

```
paper.typ               document entry point
paper/                  section text (abstract, intro, theory, method, results, discussion, conclusion)
lib/                    shared Typst code: package versions and layout, data access, graph and table builders
data/raw/               the data book (the raw data for the whole project)
data/tidy/              the data book split into one CSV file per run, plus a log of every fix (generated)
data/processed/         the statistics, fits and tables the paper shows (generated, read by Typst)
data/original/          values from the submitted paper, written down for checking
analysis/               zinclab: the Python code that tidies the data and draws the graphs, plus tests
logger-pro/             the original Logger Pro files and their CSV exports, kept for reference
assets/figures/         the graphs (generated)
assets/images/          photographs and diagrams
assets/code/            the Arduino sketch that timed the charging circuit
references/refs.bib     bibliography
docs/                   the paper as presented, the project logbook, the one-page abstract and VERIFICATION.md
```

## Building

Requirements: [Typst](https://github.com/typst/typst) ≥ 0.15 (tested with 0.15.1). The analysis needs
Python ≥ 3.10 with numpy, matplotlib, scipy and openpyxl (`pip install -r analysis/requirements.txt`). The tidy
data, the processed data and the graphs are all committed, so the paper builds with Typst alone.

```sh
make            # regenerate data/processed and assets/figures, then build build/paper.pdf
make paper      # only build the paper
make tidy       # split the data book into data/tidy
make test       # run the analysis tests
make verify     # regenerate docs/VERIFICATION.md
make check      # tests + fail if anything generated is out of date
make convert    # re-export logger-pro/files/*.cmbl into logger-pro/converted (slow, rarely needed)
```

You can also build without `make`:

```sh
cd analysis && python -m zinclab tidy && python -m zinclab build && cd ..
typst compile paper.typ build/paper.pdf
```

On the first compile, Typst downloads the packages pinned in `lib/style.typ` (unify and typsium). GitHub Actions
also runs the tests and builds the paper on every push, and the PDF is attached to each run.

### Changing a graph

Each graph is described in `analysis/zinclab/spec.py` (which runs and columns it shows) and drawn by
`analysis/zinclab/plot.py`. The statistics, integrals and curve fits under each graph are typeset by Typst from
`data/processed/`, so they always match the data.

## Installing Typst

- Prebuilt binary (Linux x86-64):
  ```sh
  curl -L https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz | tar -xJ -C /tmp
  install /tmp/typst-x86_64-unknown-linux-musl/typst ~/.local/bin/
  ```
- With Rust: `cargo install --locked typst-cli`
- macOS: `brew install typst`. Windows: `winget install --id Typst.Typst`
- Check the install with `typst --version`.

## License

[MIT](LICENSE)
