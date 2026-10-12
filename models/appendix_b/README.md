# BNGL reference examples

These models accompany `appendices/b-bngl-reference.qmd`.

| File | Purpose |
|---|---|
| `syntax_demo.bngl` | Core blocks, states, binding, dimers, observables, and a global function |
| `deletion.bngl` | Contrast complex deletion with `DeleteMolecules` |
| `functional_rates.bngl` | Compare coefficients, `TotalRate`, and explicit sources |
| `local_complex.bngl` | A whole-complex local-function reference |
| `local_molecule.bngl` | A local-function reference rooted at one receptor |
| `compartments.bngl` | Compartment topology, locations, and transport |
| `energy_binding.bngl` | An energy pattern and reversible `Arrhenius` rule |
| `specialized_rates.bngl` | Native `Sat`, `Hill`, and `MM` forms |
| `actions.bngl` | Simulation protocol, parameter scan, SSA/NFsim, exports, and visualization |

`functional_rates.bngl` deliberately demonstrates a backend difference.
In the tested distribution, `TotalRate` affects NFsim, while the generated
network supplies a coefficient multiplied by reactant amounts. Its explicit
source rule supplies the intended source flux in both representations.
The stochastic trajectories are illustrative, not fitted biological results.

The reference was audited against the clean OneDrive clone at commit
`9601746f8884ed19ab2acea49fe87fc4660ace46` (2026-09-22), which tracked
`origin/master`. Executable checks used the book environment's BioNetGen
2.9.3 distribution, bngsim, and NFsim. The regression tests document the
observed semantics so that a later backend change can prompt a corresponding
reference update. Older source snapshots and packaged simulators can differ
in graph-attribute syntax, output format, and action support.

Run from the book root:

```sh
python tests/test_bngl_reference.py
python tests/test_models.py
```

The semantic suite checks pattern counts and symmetry, local-function scope,
deletion products, the network/NFsim `TotalRate` difference, actions and
exports, expression syntax, filters, and specialized rate laws. The native
runner in `scripts/bngl_reference.py` writes all outputs to temporary
directories. A bngsim smoke test alone does not execute every action in a
BNGL file.

## Integration

`drafts/b-bngl-integration.patch` adds the appendix after installation in
`_quarto.yml` and marks it drafted in `BOOK_PLAN.md`. Shared book files were
left for integration after the concurrent corrections. The patch passed
`git apply --check` at draft completion; recheck it against subsequent edits.

The appendix has its own section identifiers and no unresolved dependencies
on future chapters. No bibliography entries or third-party figures were added.
