// Figure builders. Graphs come from assets/figures (drawn by `make figures`), and the
// statistics, integrals and curve fits under each graph come from data/processed.
// Each function returns a `figure`, so callers can attach a label: `#graph("C2-D1", ..) <C2-D1>`.

#import "data.typ": *

#let _muted = luma(42%)

/// The small coloured line that ties a table row to its trace in the graph.
#let _swatch(color) = box(baseline: -0.32em, line(length: 1.2em, stroke: 1.4pt + rgb(color)))

#let _series(r) = [#_swatch(r.color)#h(0.45em)#r.series]

/// A value with the time at which it occurred underneath, e.g. the minimum of a run.
#let _at(value, t) = stack(dir: ttb, spacing: 0.4em, sig(value), text(0.85em, fill: _muted)[_t_ = #sig(t)])

#let _with-unit(name, unit) = if unit == "" { name } else { [#name \ (#unit)] }

/// The statistics, integrals or curve fits for one graph, as a single table.
#let _table(columns, header, cells) = {
  set text(8pt, top-edge: "cap-height", bottom-edge: "baseline")
  set par(leading: 0.5em, first-line-indent: 0em)
  table(
    columns: columns,
    align: (col, _) => if col == 0 { left + horizon } else { right + horizon },
    stroke: none,
    inset: (x: 0.5em, y: 0.45em),
    table.hline(stroke: 0.6pt),
    table.header(..header.map(h => text(weight: "bold", h))),
    table.hline(stroke: 0.4pt),
    ..cells,
    table.hline(stroke: 0.6pt),
  )
}

#let _stats-table(label, integral: true, stats: true) = {
  let rows = readouts.filter(r => r.figure == label)
  let unit = rows.first().unit
  let header = ([Series],)
  if stats {
    header += (_with-unit([Min.], unit), _with-unit([Max.], unit), [Mean], [Median], [Std. dev.], [_n_], [Δ])
  }
  if integral { header += (_with-unit([Integral], if unit == "" { "min" } else { unit + "·min" }),) }
  let cells = rows.map(r => {
    let row = (_series(r),)
    if stats {
      row += (_at(r.min, r.min_t), _at(r.max, r.max_t), sig(r.mean), sig(r.median), sig(r.std), r.n, sig(r.delta))
    }
    if integral { row += (sig(r.integral),) }
    row
  }).flatten()
  let columns = (auto,) * header.len()
  _table(columns, header, cells)
}

#let _fit-table(label) = {
  let rows = fits.filter(r => r.figure == label)
  let pm(v, u) = [#sig(v) ± #sig(u)]
  let header = ([Series], [_A_ (V)], [_B_ (V)], [_C_ (min#super[−1])], [Correlation], [RMSE (V)])
  let cells = rows.map(r => (
    _series(r), pm(r.A, r.A_unc), pm(r.B, r.B_unc), pm(r.C, r.C_unc), sig(r.correlation), sig(r.rmse),
  )).flatten()
  [
    #set text(8pt)
    #set par(first-line-indent: 0em)
    #align(left)[Curve fits of the form $"EMF" = A e^(-C t) + B$, with _t_ in minutes:]
  ]
  _table((1fr,) + (auto,) * 5, header, cells)
}

/// A graph drawn from the data book, with its statistics, integrals or curve fits as a table underneath.
#let graph(label, caption: none) = {
  let info = figure-info(label)
  figure(
    kind: image,
    block(breakable: false, width: 100%, {
      image("/assets/figures/" + info.file, width: 100%)
      v(0.3em)
      if info.fit == "1" { _fit-table(label) } else {
        _stats-table(label, integral: info.integral == "1", stats: info.stats == "1")
      }
    }),
    caption: caption,
  )
}

/// A photograph or diagram from assets/images.
#let photo(path, caption: none, ..args) = figure(image("/assets/images/" + path, ..args), caption: caption)

/// Figures placed next to each other in equal columns, each keeping its own number and label.
#let side-by-side(..figures) = grid(
  columns: (1fr,) * figures.pos().len(),
  column-gutter: 1em,
  align: bottom,
  ..figures.pos(),
)
