// The research paper. Build with `typst compile paper.typ` (or `make paper`).
#import "/lib/style.typ": *

#show: project.with(
  title: [Evaluating the Potential\ of Zinc-ion Batteries],
  authors: (
    "Nirvan Joshi",
    "Sebastian Ruiz",
  ),
  abstract: include "paper/abstract.typ",
)

#include "paper/intro.typ"
#include "paper/theory.typ"
#include "paper/method.typ"
#include "paper/results.typ"
#include "paper/discussion.typ"
#include "paper/conclusion.typ"

#pagebreak()
#bibliography("/references/refs.bib", full: true, style: "american-psychological-association", title: [Works Cited])
