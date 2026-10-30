"""Command-line entry point: `python -m zinclab tidy`, `python -m zinclab build` or `python -m zinclab verify`."""

from __future__ import annotations

import argparse
import sys

from zinclab.runs import REPO, DataError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="zinclab", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("tidy", help="split the data book into the CSV files in data/tidy")
    b = sub.add_parser("build", help="regenerate data/processed and the graphs in assets/figures")
    b.add_argument("--no-figures", action="store_true", help="only write data/processed")
    sub.add_parser("verify", help="compare the original paper with the data -> docs/VERIFICATION.md")
    args = parser.parse_args(argv)

    try:
        if args.command == "tidy":
            from zinclab.book import tidy

            paths = tidy()
        elif args.command == "build":
            from zinclab.pipeline import build

            paths = build(figures=not args.no_figures)
        else:
            from zinclab.verify import write_report

            paths = [write_report()]
    except DataError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for p in paths:
        print(f"wrote {p.relative_to(REPO)}")
    return 0
