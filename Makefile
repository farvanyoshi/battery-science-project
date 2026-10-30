# Build everything with `make`. Requires Python >= 3.10 (numpy, matplotlib, scipy) and Typst >= 0.15.
PYTHON ?= python3
TYPST  ?= typst

.PHONY: all data test verify paper check convert clean

all: data paper

data:                        ## regenerate data/processed and the graphs in assets/figures
	cd analysis && $(PYTHON) -m zinclab build

test:                        ## run the analysis tests
	cd analysis && $(PYTHON) -m unittest discover -s tests

verify:                      ## regenerate docs/VERIFICATION.md
	cd analysis && $(PYTHON) -m zinclab verify

paper: build/paper.pdf

build/paper.pdf: paper.typ lib/*.typ paper/*.typ data/processed/*.csv data/original/*.csv assets/figures/*.pdf references/refs.bib | build
	$(TYPST) compile $< $@

build:
	mkdir -p build

check: test                  ## tests + fail if the committed processed data or report is stale
	cd analysis && $(PYTHON) -m zinclab build --no-figures && $(PYTHON) -m zinclab verify
	git diff --exit-code -- data/processed docs

convert:                     ## re-export logger-pro/files/*.cmbl into logger-pro/converted (slow)
	rm -rf build/cmbl && mkdir -p build/cmbl
	cp logger-pro/files/*.cmbl build/cmbl/
	cd build/cmbl && MPLCONFIGDIR="$(CURDIR)/build/mpl-cache" $(PYTHON) "$(CURDIR)/logger-pro/export/convert.py"
	$(PYTHON) logger-pro/export/collect.py build/cmbl/converted logger-pro/converted

clean:
	rm -rf build
