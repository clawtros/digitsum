# Builds the two papers in paper/ with tectonic (https://tectonic-typesetting.github.io).
#
#   make            build both PDFs (only if the .tex is newer than the .pdf)
#   make criterion  build paper/criterion.pdf only
#   make findings   build paper/findings.pdf only
#   make force      rebuild both unconditionally
#   make pages      print the page count of each PDF (findings should stay at 9)
#   make clean      remove the PDFs
#
# Figures are the PNGs in the repo root (findings.tex sets \graphicspath{{../}}),
# so rebuild those with their digitsum_*.py scripts first if they changed.

TECTONIC ?= tectonic
PAPERS   := criterion findings
PDFS     := $(addprefix paper/,$(addsuffix .pdf,$(PAPERS)))

.PHONY: all force pages clean $(PAPERS)

all: $(PDFS)

$(PAPERS): %: paper/%.pdf

paper/%.pdf: paper/%.tex
	cd paper && $(TECTONIC) $(notdir $<)

paper/findings.pdf: $(wildcard *.png)

force:
	cd paper && for p in $(PAPERS); do $(TECTONIC) $$p.tex; done

pages: $(PDFS)
	@for f in $(PDFS); do printf '%s: ' $$f; pdfinfo $$f | awk '/^Pages/{print $$2}'; done

clean:
	rm -f $(PDFS)
