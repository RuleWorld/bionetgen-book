#!/usr/bin/env bash
# Compile the standalone TikZ figures in figures/tikz/ to PDF (print book)
# and SVG (web book). Needs pdflatex (TeX Live / MacTeX) and pdftocairo (poppler).
set -euo pipefail
cd "$(dirname "$0")/../figures/tikz"
for tex in *.tex; do
  [[ $tex == common.tex ]] && continue
  name=${tex%.tex}
  pdflatex -interaction=nonstopmode -halt-on-error "$tex" > "/tmp/tikz-$name.log" 2>&1 \
    || { tail -20 "/tmp/tikz-$name.log"; exit 1; }
  pdftocairo -svg "$name.pdf" "../$name.svg"
  mv "$name.pdf" "../$name.pdf"
  rm -f "$name.aux" "$name.log"
  echo "figures/$name.{pdf,svg}"
done
