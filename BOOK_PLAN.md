# Rule-based modeling with BioNetGen: plan for a book and course

*Working draft, October 2026. Everything here is a proposal to react to.*

**Status (2026-10-11):** Part I drafted (Chapters 1–4); Part II drafted (Chapters 5–8), including energy-based modeling in Chapter 8; Appendix B (BNGL reference) drafted. Chapters 1–7 revised after a critical review (`BOOK_REVIEW.md`). Visualization additions to core chapters and an advanced visualization chapter are planned. Chapters 1–2 revised for voice; see STYLE.md.

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
  - cooperative interactions and energy patterns (Ch. 8);
  - fitting to pSTAT time courses (Ch. 9);
  - AI-assisted construction, analysis, and calibration of the circuit (Ch. 12);
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
- **Visualize the mechanism throughout.** Introduce contact maps and rule
  diagrams with the first structured models, then use them for model review
  and interpretation. Chapter 15 develops automated visualization and
  compression for larger models.
- **Energy-based modeling is a core tool.** Introduce thermodynamic
  consistency alongside cooperative binding in Chapter 4 and develop energy
  patterns in Part II, before parameter estimation. Carry the energy
  parameterization into calibration, uncertainty analysis, and case studies.

## Proposed table of contents

**Status key:**
- **exists**: slides, models, notebooks and a worksheet exist.
- **partial**: some material exists elsewhere (named).
- **new**: written from scratch.

### Part I. Foundations

| # | Chapter | Core ideas | Running example | Status |
|---|---|---|---|---|
| 1 | Reaction networks as dynamical systems | species, reactions, mass action, ODEs, stoichiometry matrix, first BNGL model | build the STAT–SOCS loop step by step | exists (Module 1) |
| 2 | Molecules, patterns, and rules | components, states, bonds, patterns, rules, contact maps and rule diagrams, network generation, combinatorial complexity | rewrite the loop as rules, then relax assumptions | exists (Module 2); visualization expansion planned |
| 3 | Stochastic simulation and noise | SSA, when ODEs fail, intrinsic noise, bursting, ensemble statistics, PSA | one SOCS gene copy gives bursty feedback | drafted |
| 4 | A field guide to rules | binding, modification, synthesis and degradation, symmetry and multiplicity, intramolecular binding, aggregation and `max_agg`, cooperativity and thermodynamic consistency, functional rate laws | rules and diagrams for each signaling motif | drafted; thermodynamic bridge planned |

### Part II. Building realistic models

| # | Chapter | Core ideas | Running example | Status |
|---|---|---|---|---|
| 5 | Compartments and transport | cBNGL, volume scaling, membranes, transport | STAT nuclear import and export; receptor internalization | drafted |
| 6 | Network-free simulation | infinite networks, NFsim and RuleMonkey through bngsim, performance trade-offs | ligand-induced receptor aggregation (TLBR, FcεRI) | drafted |
| 7 | Analyzing models | steady states, parameter scans, bifurcation, sensitivity, timescales, conservation laws; relating structural diagrams to dynamics | generalize the pulse-shape exercise | drafted; visualization links planned |
| 8 | Energy-based rule-based modeling | free-energy and kinetic parameters, energy patterns, cooperativity and allostery, detailed balance, energy-driven signaling | cooperative receptor binding; EGFR or RAF example alongside the STAT circuit | drafted (tested binding and illustrative RAF models; companion notebook) |

### Chapter 8: Energy-based rule-based modeling

Energy-based modeling belongs in the core toolbox for building realistic
models. Rules compress the enumeration of species and reactions; energy
patterns provide a way to express how binding and modification at one site
alter interactions at another. Introduce this distinction between
combinatorial and contextual complexity using the cooperative-binding example
from Chapter 4, then build an executable energy-based version.

**Source material:** unpublished manuscripts by the author and collaborators
on energy-based modeling, to be cited once they are public, and the published
thermodynamically consistent ATP-production model of Garcia et al. (2023),
which informs the treatment of ATP-driven cycles.

**Proposed sections and learning goals:**

1. **Why independent rate constants can fail.** Construct a two-site binding
   cycle, check its equilibrium constants around the cycle, and expose an
   inconsistent parameter assignment. Distinguish equilibrium constraints
   from the kinetics that determine how quickly equilibrium is approached.
2. **Free energies and energy patterns.** Define binding free energies and
   contextual corrections for cooperativity or allostery. State energy units,
   reference states, and concentration standard states; show how pattern
   matching assigns energies across molecular configurations.
3. **From energies to rates.** Separate equilibrium free-energy differences
   from kinetic prefactors and the distribution of an energy change between
   forward and reverse barriers. Derive rate ratios with the appropriate
   standard-state factors and check symmetry and multiplicity in the
   generated reactions. Demonstrate the supported BioNetGen syntax in a
   versioned, tested model.
4. **Cooperativity and allostery.** Compare explicit context-specific rules
   with energy patterns for the same binding system. Verify matching
   predictions, count independent parameters, and perturb a contextual energy
   to explain a change in dose response. Extend to receptor or RAF dimerization
   and inhibitor binding when a verified model is available.
5. **Equilibrium and energy-driven signaling.** Explain detailed balance for
   an equilibrium subsystem and local thermodynamic constraints in a system
   driven by ATP/GTP hydrolysis or chemostatted reservoirs. Make the driving
   assumptions explicit; do not impose global equilibrium detailed balance
   on an actively driven signaling circuit. Identify the approximations in
   irreversible phosphorylation and dephosphorylation rules.
6. **Using and estimating energy parameters.** Relate affinities and
   cooperative factors to energies, distinguish measured inputs from fitted
   quantities, and explain which kinetic parameters remain undetermined by
   equilibrium data. Prepare an example for energy-parameter calibration in
   Chapter 9 and uncertainty analysis in Chapter 10.

**Chapter bundle:** matched kinetic and energy-based binding models, a
cycle-consistency check, a verified signaling example, and a notebook with
equilibrium and transient comparisons. Figures should show the binding
cycle, matched energy patterns, and the effect of a cooperative energy on
the response. Exercises should ask readers to repair an inconsistent cycle,
recover an affinity from an energy, compare rate distributions at fixed
equilibrium, and identify the energy source in a driven cycle.

### Part III. Models meet data

| # | Chapter | Core ideas | Running example | Status |
|---|---|---|---|---|
| 9 | Parameter estimation | objective functions, optimizers, multistart; fitting kinetic and energy parameters; PyBNF; pyPESTO with bngsim gradients | fit the loop to pSTAT time courses; calibrate a cooperative energy | partial (`fit_data`/`generate_data` notebooks) |
| 10 | Uncertainty and identifiability | profile likelihood, Fisher information, Bayesian inference (PyBNF MCMC, ptempest); uncertainty in kinetic and energy parameters | which STAT–SOCS parameters can the data determine? | new |
| 11 | Building, testing, and sharing models | modeling workflow, annotation, model review with contact maps and regulatory graphs, SBML import and export (Atomizer), model tests, version control, RuleHub, BNG Playground links | package the loop with model-derived diagrams and tests | new |
| 12 | AI-assisted rule-based modeling | translating biological hypotheses into rules; simulation-in-the-loop agents; mechanistic diagnostics; parameter calibration and model comparison; verification and provenance | build, diagnose, and calibrate alternative STAT–SOCS mechanisms | partial (`papers/bngp.tex`, BNG Playground preprint) |

### Chapter 12: AI-assisted rule-based modeling

This chapter draws on the BNG Playground preprint in
[`papers/bngp.tex`](papers/bngp.tex), particularly its MCP interface,
simulation-in-the-loop workflow, diagnostic pipeline, and proposed
agent-driven structure-discovery case study. It follows Chapters 7–11 so
that readers can judge the simulations, fits, uncertainty estimates, and
model changes an AI assistant produces. Earlier chapters can include short
AI-assisted exercises that point forward to this chapter.

The central example extends the STAT–SOCS circuit. Starting from a written
biological hypothesis and a defined set of measurements, an assistant
proposes BNGL rules, checks the generated reactions, analyzes the response,
and calibrates the model. Each revision must resolve to explicit rules,
parameter changes, and reproducible calculations. The reader decides whether
the assumptions and conclusions are supported by the biology and data.

**Learning goals:**

- translate a biological description into molecule types, sites, states,
  rules, observables, and explicit assumptions with an AI assistant;
- give an assistant a modeling task with specified data, units, constraints,
  outputs, and criteria for accepting the result;
- use a simulation-in-the-loop workflow to detect and repair errors in rules
  and to investigate model behavior;
- organize parameter estimation and uncertainty analysis with callable
  scientific tools, and distinguish parameter calibration from a change in
  model structure;
- test mechanistic explanations with controlled perturbations and compare
  alternative mechanisms using data reserved for validation;
- preserve the model, data, tool outputs, and revision history needed to
  reproduce and review AI-assisted work.

**Proposed sections:**

1. **From biological statements to rules.** Supply a source-supported
   mechanism, name what is known and what is assumed, and ask the assistant
   to construct a minimal model. Check site declarations, context, symmetry,
   deletion behavior, units, and observables using the methods of Chapters
   1–5. Include a plausible-looking rule that runs but expresses the wrong
   mechanism, so successful execution is distinguished from correctness.
2. **Giving an assistant access to scientific tools.** Explain the Model
   Context Protocol (MCP) as an interface for calling tools and receiving
   structured results. Use BNG Playground's shared modeling engine as the
   worked example, with a Python/BioNetGen workflow for independent checks.
   Show a task specification and an inspectable sequence of tool calls;
   document the tested versions and supported capabilities when the chapter
   is written.
3. **Simulation in the loop.** Follow the cycle: propose or edit a model,
   validate it, generate a network when feasible, simulate, inspect results,
   and revise. Use structured errors and diagnostics to guide recovery.
   State a prediction before each run and retain unsuccessful hypotheses
   when they explain why a revision was made.
4. **Analyzing a mechanism.** Ask the assistant to examine conservation,
   timescales, dose response, sensitivity, and identifiability. Trace an
   influential parameter to the rules that use it and to candidate routes
   through the molecular interaction graph. A contact-map path identifies a
   possible connection; establish its dynamical importance with matched
   perturbations, rule knockouts, and simulation results.
5. **Calibrating models against data.** Specify the measurement model,
   objective or likelihood, parameter bounds, and noise assumptions. Have
   the assistant organize multistart fitting and the uncertainty checks from
   Chapters 9–10. Inspect residuals and parameter correlations, reserve data
   for validation, and separate a good fit from an identifiable parameter
   estimate or a supported mechanism.
6. **Revising and comparing model structure.** Compare alternative SOCS
   inhibition mechanisms or a model with an omitted transport step. Fit each
   candidate under the same data and error assumptions, assess its
   predictions on reserved conditions, and propose a measurement that
   distinguishes the candidates. Include an energy-parameterized candidate
   from Chapter 8 when cooperativity is the disputed mechanism. Synthetic
   data with a known generating
   model provide a controlled first exercise; experimental data can follow
   when available and documented.
7. **Verification and reproducibility.** Review model diffs, source support
   for biological claims, invariants, reference-simulator agreement, and
   statistical uncertainty. Archive prompts, model versions, data,
   objective definitions, software versions, random seeds, and tool outputs.
   Distinguish reproducible numerical calculations from potentially variable
   AI responses. Explain which information is sent to the AI service and
   which calculations run locally or in the browser.

**Chapter bundle:**

- a verified baseline STAT–SOCS model, an intentionally flawed model, and
  alternative mechanisms in `models/ch12/`;
- synthetic calibration and validation data with a documented generating
  model and noise process;
- a notebook that reproduces the simulations, fits, and verification checks
  independently of an AI conversation;
- a recorded AI/tool interaction with model diffs and a concise evidence
  table connecting each conclusion to its calculation;
- figures showing the modeling loop, correction of an unintended rule,
  fits and residuals, uncertainty, and predictions distinguishing mechanisms;
- slides, a worksheet, and exercises asking readers to audit a generated
  model, diagnose a misleading fit, and design a discriminating experiment.

The preprint contains proposed case studies and unfinished validation
results. Treat these as starting material, and verify tool behavior and
scientific claims before using them as worked results. Its discussion also
notes that current contact-map tracing is a structural approximation; the
chapter should preserve that distinction when discussing mechanistic
explanations. Verify primary references before adding them to the book's
bibliography.

### Part IV. Advanced topics in rule-based modeling (optional; choose based on interest)

| # | Chapter | Core ideas | Status |
|---|---|---|---|
| 13 | Spatial modeling with MCell | BNGL in MCell4, diffusion, membrane geometry | new |
| 14 | Rare events and weighted ensemble | WESTPA and WEBNG for rule-based models | new |
| 15 | Visualizing rule-based models | compact rule diagrams, atom-rule graphs, regulatory interactions, graph compression, visual navigation of large models | partial (Sekar, Tapia, and Faeder, 2017) |

### Chapter 15: Visualizing rule-based models

Base the chapter on Sekar, Tapia, and Faeder (2017),
[*Automated visualization of rule-based models*](https://doi.org/10.1371/journal.pcbi.1005857),
with bibliography key `Sekar2017Visualization`. Develop compact rule
visualization, atom-rule graphs, and expert-guided graph compression into
readable diagrams of model architecture.

Use the STAT–SOCS circuit to compare contact maps, individual rule diagrams,
and regulatory views, then use a larger EGFR or FcεRI model to teach grouping,
compression, and navigation. Explain what each representation preserves or
omits and retain links from a compressed diagram to the underlying rules.
Exercises should ask readers to identify context and transformations, trace
the SOCS feedback loop, compare compression choices, and audit a diagram
against its executable model. Generate diagrams from versioned model sources
and record visualization settings with the chapter notebook.

### Visualization in the core chapters

The advanced chapter develops scalable methods; basic model visualization
should appear much earlier:

- **Chapter 2:** introduce a contact map for STAT–SOCS and show rule diagrams
  beside BNGL, distinguishing context from bonds or states changed by a rule.
- **Chapter 4:** use rule diagrams to check binding, modification, deletion,
  and intracomplex reactions; pair visual inspection with generated networks.
- **Chapter 7:** relate structural diagrams to feedback, sensitivity, and
  dynamical modes, and test structural interpretations with simulations.
- **Chapter 8:** show energy patterns on the molecular configurations and
  cycles they constrain.
- **Chapter 11:** include model-derived diagrams in the review and sharing
  workflow, with traceability to rules and regeneration after model changes.
- **Chapter 12:** use these representations to inspect AI-proposed rules and
  mechanistic explanations.

### Part V. Case studies

| # | Case study | Teaches | Status |
|---|---|---|---|
| 16 | FcεRI signaling | the classic combinatorial model; aggregation; visualization of regulatory structure | partial (old deck; published models) |
| 17 | EGFR / ErbB | large models, network-free simulation, cooperative energy parameters, visualization | partial (published models; local energy-modeling draft) |
| 18 | JAK–STAT cytokine signaling | the running example at full scale (IL-6/IL-10, SOCS1/3), fitted to data | partial (lab IL-6/IL-10 model and fitting work) |

### Appendices

- A. Installing the tools (VS Code extension, PyBioNetGen, bngsim, BNG Playground)
- B. BNGL language reference (drafted; executable syntax and semantic checks)
- C. Python interface (bngsim, PyBioNetGen) reference
- D. **Lab practices**: project layout, Git and GitHub, reproducibility, model
  review checklist. This appendix is the core of the onboarding manual.
- E. Mathematical background (ODEs, probability for stochastic kinetics)

## Reading paths

| Path | Chapters |
|---|---|
| MSCBIO two-session module | 1, 2 |
| Semester course | 1–12, plus one case study; 15 for a visualization module |
| Lab onboarding | 1–4, 7–9, 11, App. D; add 10 and 12 for AI-assisted calibration and 15 for large-model visualization, then the case study closest to the new member's project |
| Self-study introduction | 1–4 and 6, with BNG Playground |
| AI-assisted modeling | 1–4 and 7–12; add 5–6 as needed for compartments and network-free models |
| Model visualization | basics in 2 and 4, applications in 7 and 11, advanced methods in 15 |

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
  standard. The course slides for Modules 1 and 2 live in the course
  repository (decided October 12, 2026); slides derived from the chapters,
  reusing the book's figures and models, are a later step.

The alternative is Jupyter Book 2 (MyST). Its notebook-first design is good,
but its PDF output is less mature, and the PDF matters for a book.

**Continuous integration** (GitHub Actions) on every push:

- run all models;
- execute all notebooks;
- build the book.

**Answer keys** need a private home, such as a separate private repository,
because the book repository will be public.

## Repository

**This repository, `RuleWorld/bionetgen-book`**, holds the book, models,
and notebooks. The MSCBIO course repository
(`jrfaeder/RBM_Intro_BioNetGen`) remains the course page, holds the course
slides and worksheets with their private keys, and links to the book.

```
book/            Quarto chapters (.qmd) and _quarto.yml
models/          BNGL models, organized by chapter
notebooks/       executable notebooks used by chapters and exercises
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
| M4 | Chapters 5, 6, 8 (energy-based modeling), and 9 (parameter estimation). |
| M5 | Chapters 10, 11, and Appendix D, completing the lab training manual. |
| M6 | Chapter 12, AI-assisted rule-based modeling, using verified examples adapted from the BNG Playground preprint. |
| M7 | Chapter 15, visualization, extending the diagrams introduced in core chapters; case studies and other optional Part IV chapters as interest dictates. |

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
