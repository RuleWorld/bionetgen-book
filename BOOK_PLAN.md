# Rule-based modeling with BioNetGen: plan for a book and course

*Working draft, October 2026. Everything here is a proposal to react to.*

**Status:** M1 in progress. Repository created, Chapters 1–2 drafted, CI set up.

## What we are building

One set of source material that serves three uses:

1. **A book** (web and PDF): a general introduction to rule-based modeling of
   biological systems with the BioNetGen tools.
2. **A course**: lecture slides, exercises, and worksheets for teaching. This
   can be a two-session module, as in MSCBIO 2025, or a full semester.
3. **A lab training manual**: a self-paced path for new lab members, ending with
   them building, fitting, and sharing their own models the way the lab does.

Modules 1 and 2 (`Slides/module1-kinetics`, `Slides/module2-rules`) become
Chapters 1 and 2.

## Design principles

- **One running example.** The cytokine–STAT–SOCS circuit from Modules 1–2
  grows through the book, so readers keep extending a model they already
  understand:
  - stochastic SOCS expression from a single gene copy (Ch. 3);
  - nuclear shuttling of STAT (Ch. 5);
  - fitting to pSTAT time courses (Ch. 8);
  - the full IL-6/IL-10 JAK-STAT model from the lab (case study).

  Other systems (FcεRI, EGFR, MAPK) appear where they teach something the
  running example cannot, such as aggregation.
- **Every chapter is a bundle.** Each one has:
  - text;
  - BNGL models;
  - a notebook;
  - slides;
  - a worksheet with a private key;
  - exercises.

  They share models and figures, so they cannot drift apart.
- **Everything is executable and tested.** Every figure and number in the book
  is produced by running the models. A continuous-integration job rebuilds the
  book and runs all models and notebooks on every change, so a BioNetGen or
  bngsim update cannot break the text silently.
- **Current tools throughout:**
  - BNGL;
  - VS Code with the BioNetGen extension;
  - bngsim for Python simulation;
  - BNG Playground for zero-install use.

  Older interfaces (RuleBender, `run_network`) appear only in a historical
  note.
- **Learn by predicting.** Keep the pattern from the Module 1 worksheet:
  predict, simulate, explain.

## Proposed table of contents

**Status key:**
- **exists**: slides, models, notebooks and a worksheet exist.
- **partial**: some material exists elsewhere (named).
- **new**: written from scratch.

### Part I. Foundations

| # | Chapter | Core ideas | Running example | Status |
|---|---|---|---|---|
| 1 | Reaction networks as dynamical systems | species, reactions, mass action, ODEs, stoichiometry matrix, first BNGL model | build the STAT–SOCS loop step by step | exists (Module 1) |
| 2 | Molecules, patterns, and rules | components, states, bonds, patterns, rules, network generation, combinatorial complexity | rewrite the loop as rules, then relax assumptions | exists (Module 2) |
| 3 | Stochastic simulation and noise | SSA, when ODEs fail, intrinsic noise, bursting, ensemble statistics, PSA | one SOCS gene copy gives bursty feedback | partial (old deck SSA slides; `run_lr` notebook) |
| 4 | A field guide to rules | binding, modification, synthesis and degradation, symmetry and multiplicity, intramolecular binding, aggregation and `max_agg`, cooperativity, functional rate laws | rules for each signaling motif | partial (`RuleWorld/BNGTutorial`; Sekar & Faeder 2012 rule library) |

### Part II. Building realistic models

| # | Chapter | Core ideas | Running example | Status |
|---|---|---|---|---|
| 5 | Compartments and transport | cBNGL, volume scaling, membranes, transport | STAT nuclear import and export; receptor internalization | partial (BNGTutorial `CBNGL`) |
| 6 | Network-free simulation | infinite networks, NFsim and RuleMonkey through bngsim, performance trade-offs | ligand-induced receptor aggregation (TLBR, FcεRI) | partial (Module 2 scaling slides) |
| 7 | Analyzing models | steady states, parameter scans, bifurcation, sensitivity, timescales, conservation laws | generalize the pulse-shape exercise | partial (Module 1 worksheet, part B) |

### Part III. Models meet data

| # | Chapter | Core ideas | Running example | Status |
|---|---|---|---|---|
| 8 | Parameter estimation | objective functions, optimizers, multistart; PyBNF; pyPESTO with bngsim gradients | fit the loop to pSTAT time courses | partial (`fit_data`/`generate_data` notebooks) |
| 9 | Uncertainty and identifiability | profile likelihood, Fisher information, Bayesian inference (PyBNF MCMC, ptempest) | which STAT–SOCS parameters can the data determine? | new |
| 10 | Building, testing, and sharing models | modeling workflow, annotation, contact maps and regulatory graphs, SBML import and export (Atomizer), model tests, version control, RuleHub, BNG Playground links | package the loop as a shareable, tested model | new |

### Part IV. Beyond the well-mixed cell (optional; choose based on interest)

| # | Chapter | Core ideas | Status |
|---|---|---|---|
| 11 | Spatial modeling with MCell | BNGL in MCell4, diffusion, membrane geometry | new |
| 12 | Rare events and weighted ensemble | WESTPA and WEBNG for rule-based models | new |
| 13 | Energy-based rule-based modeling | thermodynamic consistency, energy patterns | new |

### Part V. Case studies

| # | Case study | Teaches | Status |
|---|---|---|---|
| 14 | FcεRI signaling | the classic combinatorial model; aggregation | partial (old deck; published models) |
| 15 | EGFR / ErbB | large models, network-free simulation | partial (published models) |
| 16 | JAK–STAT cytokine signaling | the running example at full scale (IL-6/IL-10, SOCS1/3), fitted to data | partial (lab IL-6/IL-10 model and fitting work) |

### Appendices

- A. Installing the tools (VS Code extension, PyBioNetGen, bngsim, BNG Playground)
- B. BNGL language reference
- C. Python interface (bngsim, PyBioNetGen) reference
- D. **Lab practices**: project layout, Git and GitHub, reproducibility, model
  review checklist. This appendix is the core of the onboarding manual.
- E. Mathematical background (ODEs, probability for stochastic kinetics)

## Reading paths

| Path | Chapters |
|---|---|
| MSCBIO two-session module | 1, 2 |
| Semester course | 1–10, plus one case study |
| Lab onboarding | 1–4, 7, 8, 10, App. D; then the case study closest to the new member's project |
| Self-study introduction | 1–4 and 6, with BNG Playground |

## Format and tools

**Recommendation: a [Quarto](https://quarto.org) book**, built from Markdown
and Jupyter notebooks:

- **One source, two outputs:** an HTML book on GitHub Pages and a typeset PDF
  through LaTeX.
- **Executable chapters:** each chapter runs Python with bngsim, so every
  figure is regenerated from the models.
- **Citations** from a BibTeX file, which can be exported from Zotero, and
  numbered cross-references.
- **BNGL syntax highlighting** through a small custom syntax file.
- **Slides stay in beamer** with the existing theme, because that is your
  standard. They reuse the book's figures and models.

The alternative is Jupyter Book 2 (MyST). Its notebook-first design is good,
but its PDF output is less mature, and the PDF matters for a book.

**Continuous integration** (GitHub Actions) on every push:

- run all models;
- execute all notebooks;
- build the book and the slides.

**Answer keys** need a private home, such as a separate private repository,
because the book repository will be public.

## Repository

**This repository, `RuleWorld/bionetgen-book`**, holds the book, models,
notebooks, slides, and worksheets. The MSCBIO course repository (`jrfaeder/RBM_Intro_BioNetGen`) remains the
course page and links to the book.

```
book/            Quarto chapters (.qmd) and _quarto.yml
models/          BNGL models, organized by chapter
notebooks/       executable notebooks used by chapters and exercises
slides/          beamer theme and one deck per chapter
worksheets/      printable worksheets (keys live in a private repo)
references.bib   bibliography
tests/           model and notebook checks run in CI
```

## How each chapter gets made

1. **Outline.** Learning goals, key figures, models, and exercises. You approve.
2. **Models and notebook.** Each model is tested, and the figures are generated
   from it.
3. **Text.** Prose draft, written from the slides and models, with figures and
   code embedded.
4. **Slides and worksheet.** Derived from the chapter.
5. **Review.** You review the science and framing. Ideally a new lab member
   reads it as a test reader and reports where they got stuck.

Claude can draft steps 1–4. Scientific judgment and final framing stay with
you.

## Roadmap

| Milestone | Contents |
|---|---|
| M0 | Decide format, repository, title, license, and chapter list. |
| M1 | Scaffold the book, CI, and BNGL highlighting. Convert Modules 1 and 2 into Chapters 1 and 2 (prose plus executable figures). Publish to GitHub Pages. |
| M2 | Chapter 3, stochastic simulation. This completes the core of the onboarding path and the semester course's first unit. |
| M3 | Chapters 4 and 7, which build on existing material. |
| M4 | Chapters 5, 6, and 8. |
| M5 | Chapters 9, 10, and Appendix D, completing the lab training manual. |
| M6 | Case studies and optional Part IV chapters as interest dictates. |

## Decisions

**Made (October 9, 2026):**

- **Format:** Quarto book (HTML on GitHub Pages and a PDF); slides stay in beamer.
- **Repository:** a new public repository under RuleWorld. This repository
  stays as the MSCBIO course page and links to the book.
- **Publication:** open online book. Text under CC BY 4.0, code and models
  under MIT.

- **Title:** *Rule-Based Modeling of Biological Systems: Theory and practice
  with BioNetGen*.
- **Repository:** `RuleWorld/bionetgen-book`, at
  `OneDrive/Code/bionetgen-book` locally.

**Still open:**

1. Chapter list: anything to add, cut, or reorder? In particular, which Part IV
   chapters and case studies matter most to the lab?
