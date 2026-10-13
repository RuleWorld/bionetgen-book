# Rule-Based Modeling of Biological Systems

*Theory and practice with BioNetGen*

An open book, course, and lab training manual on rule-based modeling of
biological systems with the [BioNetGen](https://bionetgen.org) tools.

**Read the book:** <https://ruleworld.github.io/bionetgen-book/> (web and PDF)

The book is in progress. Chapters 1-8 are drafted. The plan for the rest is
in [BOOK_PLAN.md](BOOK_PLAN.md).

## What's here

| Folder | Contents |
|---|---|
| `chapters/`, `index.qmd`, `appendices/` | Book chapters ([Quarto](https://quarto.org) Markdown with executable Python) |
| `models/` | BNGL models, by chapter |
| `notebooks/` | Jupyter notebooks for exercises |
| `figures/` | Diagrams; `figures/tikz/` holds their sources |
| `scripts/` | Build helpers |
| `tests/` | Model checks run on every change |

Every figure and number in the book is produced by running the models, using
[bngsim](https://bngsim.readthedocs.io). A GitHub Actions workflow tests all
models and rebuilds the book on every push to `main`.

Lecture slides and worksheets for the course built on Chapters 1 and 2 live
in the course repository, [jrfaeder/RBM_Intro_BioNetGen](https://github.com/jrfaeder/RBM_Intro_BioNetGen).
Slides derived from the chapters are planned.

## Building locally

```bash
conda env create -f environment.yml
conda activate bionetgen-book
python tests/test_models.py          # check the models
quarto render                        # build the book into _book/
quarto preview                       # live preview while editing
```

Other builds:

- Diagrams: `scripts/make_tikz_figures.sh` (needs a TeX installation and poppler)

## License

Text and figures: [CC BY 4.0](LICENSE-TEXT.txt). Code and models:
[MIT](LICENSE-CODE.txt). See [LICENSE.md](LICENSE.md).
