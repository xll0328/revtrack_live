PDF=main.pdf
FIG1=figures/figure1_revision_tracking.pdf

.PHONY: all clean

all: $(PDF)

$(FIG1): ../outputs/day1/paper_assets/figure1_revision_tracking.svg
	python -m cairosvg $< -o $@

$(PDF): main.tex sections/*.tex tables/*.tex refs.bib acl_style/acl.sty acl_style/acl_natbib.bst $(FIG1)
	pdflatex -interaction=nonstopmode main.tex
	bibtex main
	pdflatex -interaction=nonstopmode main.tex
	pdflatex -interaction=nonstopmode main.tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.pdf *.fdb_latexmk *.fls
