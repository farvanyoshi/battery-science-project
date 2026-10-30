// The results tables, generated from the data in /data.

#import "data.typ": *

#let _table(columns, header, rows) = {
  set par(first-line-indent: 0em)
  table(
    columns: columns,
    align: (col, _) => if col == 0 { left } else { right },
    stroke: none,
    inset: (x: 0.7em, y: 0.5em),
    table.hline(stroke: 0.6pt),
    table.header(..header.map(h => text(weight: "bold", h))),
    table.hline(stroke: 0.4pt),
    ..rows,
    table.hline(stroke: 0.6pt),
  )
}

/// Effective charge capacity and energy (the part of each discharge above 0.9 V) for one iteration.
#let effective-table(iteration, caption: none) = {
  let rows = effective-capacity.filter(r => r.iteration == str(iteration))
  let quantities = (
    ([Effective Capacity (A min)], "capacity_amin"),
    ([Effective Capacity (C)], "capacity_c"),
    ([Effective Energy (W min)], "energy_wmin"),
    ([Effective Energy (J)], "energy_j"),
  )
  figure(
    _table(
      (auto,) + (auto,) * rows.len(),
      ([],) + rows.map(r => [Discharge #r.discharge]),
      quantities.map(((name, key)) => (name, ..rows.map(r => sig(r.at(key))))).flatten(),
    ),
    caption: caption,
  )
}

/// Internal resistance at the start or end (`at: "start_ohm"` / `"end_ohm"`) of every discharge.
#let resistance-table(at, caption: none) = {
  let iterations = (2, 3, 4, 5)
  let value(it, d) = {
    let r = internal-resistance.filter(r => r.iteration == str(it) and r.discharge == str(d))
    if r.len() == 0 { [N/A] } else { r.first().at(at) }
  }
  figure(
    _table(
      (auto,) * 5,
      ([Resistance ($Omega$)],) + iterations.map(it => [Iteration #it]),
      range(1, 4).map(d => (strong[Discharge #d], ..iterations.map(it => value(it, d)))).flatten(),
    ),
    caption: caption,
  )
}
