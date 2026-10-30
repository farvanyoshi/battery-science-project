"""Draws the graphs in assets/figures with Matplotlib.

The graphs only show data. Titles, statistics, integrals and fit coefficients are typeset
by Typst under each graph (lib/figures.typ), so they use the paper's fonts.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / "build" / "mpl-cache"))

import matplotlib

matplotlib.use("Agg")
logging.getLogger("fontTools").setLevel(logging.ERROR)  # cmr10's header dates trigger harmless warnings
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator, ScalarFormatter

from zinclab.runs import column
from zinclab.spec import FIGURES, SERIES, Figure

INK = "#0b0b0b"
INK_2 = "#52514e"
RULE = "#8a8984"
GRID = "#e6e5e1"

WIDTH, HEIGHT = 6.3, 2.9  # inches; the paper's text block is 6.5 in wide

STYLE = {
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.labelcolor": INK,
    "axes.edgecolor": RULE,
    "axes.linewidth": 0.6,
    "xtick.color": RULE,
    "ytick.color": RULE,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.minor.width": 0.4,
    "ytick.minor.width": 0.4,
    "legend.fontsize": 8.5,
    "legend.frameon": False,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.dpi": 300,
}


def _formatter() -> ScalarFormatter:
    f = ScalarFormatter(useMathText=True)
    f.set_useOffset(False)
    f.set_powerlimits((-6, 6))  # plain decimals, no "×10⁻³" offset label
    return f


def _tex(label: str) -> str:
    """cmr10 has no Ω glyph, so draw it with mathtext."""
    return label.replace("Ω", r"$\Omega$")


def render(fig_spec: Figure, out: Path) -> Path:
    """Render one figure to `out` (PDF)."""
    from zinclab.pipeline import fit_for

    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT), layout="constrained")
        t_max, y_min = 0.0, 0.0
        for i, tr in enumerate(fig_spec.traces):
            color = SERIES[i]
            col = column(tr.source, tr.run, tr.column)
            ok = np.isfinite(col.t) & np.isfinite(col.y)
            t, y = col.t[ok], col.y[ok]
            t_max, y_min = max(t_max, float(t.max())), min(y_min, float(y.min()))
            if fig_spec.sparse:
                ax.plot(t, y, ls="none" if fig_spec.fit else "-", lw=0.7, marker="o", ms=3.4,
                        mfc=color, mec="white", mew=0.5, color=color, label=_tex(tr.label), zorder=3)
                if fig_spec.fit:
                    tt = np.linspace(t.min(), t.max(), 400)
                    ax.plot(tt, fit_for(fig_spec.label, tr.label)(tt), lw=1.0, color=color, zorder=2)
            else:
                ax.plot(t, y, lw=0.6, color=color, label=_tex(tr.label), solid_joinstyle="round", zorder=2)
                if fig_spec.integral and len(fig_spec.traces) == 1:
                    ax.fill_between(t, y, color=color, alpha=0.12, lw=0, zorder=1)

        ax.set_xlim(0, t_max)
        ax.set_ylim(bottom=y_min if y_min < 0 else 0)
        ax.margins(y=0.06)
        ax.set_xlabel("Time (min)")
        ax.set_ylabel(fig_spec.ylabel)
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_major_formatter(_formatter())
            axis.set_minor_locator(AutoMinorLocator())
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(True, which="major", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        if y_min < 0:
            ax.axhline(0, color=RULE, lw=0.6, zorder=1)
        if len(fig_spec.traces) > 1:
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc="outside upper center", ncols=len(labels),
                       handlelength=1.6, columnspacing=1.6, borderaxespad=0.2)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, metadata={"CreationDate": None, "Creator": None, "Producer": None})
        plt.close(fig)
    return out


def render_all(directory: Path) -> list[Path]:
    return [render(f, directory / f"{f.name}.pdf") for f in FIGURES]
