"""Copy the parts of a convert.py export that this repository keeps into logger-pro/converted.

Usage: python collect.py <export>/converted <repo>/logger-pro/converted

Kept: dataset_<id>.csv, metadata.json and verification.json. Left out: the rendered
Logger Pro graphs, the XML working copies and the *_raw_cells.csv companions, which
can all be regenerated from logger-pro/files.
"""

import shutil
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
for folder in sorted(p for p in src.iterdir() if p.is_dir()):
    out = dst / folder.name
    out.mkdir(parents=True, exist_ok=True)
    for f in folder.iterdir():
        if f.name == "metadata.json" or (f.name.startswith("dataset_") and f.suffix == ".csv" and "_raw_cells" not in f.name):
            shutil.copy2(f, out / f.name)
shutil.copy2(src / "verification.json", dst / "verification.json")
print(f"copied {src} -> {dst}")
