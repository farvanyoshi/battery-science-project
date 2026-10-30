// Package versions and the page layout of the paper.
// Every other file imports packages through here, so versions are pinned in one place.

#import "@preview/typsium:0.3.1": ce
#import "@preview/unify:0.7.1": num, qty, unit, numrange, qtyrange

/// The paper layout: a title page, an abstract page, then the body with numbered
/// equations, indented paragraphs and page numbers.
#let project(title: "", abstract: [], authors: (), body) = {
  set document(author: authors, title: title)
  set page(paper: "us-letter", numbering: "1")
  set text(font: "New Computer Modern", lang: "en")
  show math.equation: set text(weight: 400)
  set math.equation(numbering: "(1)")

  set text(top-edge: 0.5em, bottom-edge: -.9em)
  set par(leading: 1em, spacing: 1em, first-line-indent: (amount: 0.5in, all: true))
  show heading: set text(top-edge: 0.8em, bottom-edge: -0.5em)

  show figure: set par(leading: 0em)
  show figure.where(kind: table): set figure.caption(position: top)

  // Title page.
  v(10.2fr)
  text(2em, weight: 700, title)
  v(2.4fr)
  pagebreak()

  // Abstract page.
  align(center)[
    #set par(first-line-indent: 0em)
    #heading(
      outlined: false,
      numbering: none,
      text(.85em, smallcaps[Abstract]),
    )
    #abstract
  ]
  v(1.618fr)
  pagebreak()

  // Main body.
  set text(size: 10pt)
  body
}
