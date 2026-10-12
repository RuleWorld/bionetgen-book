# Chapter 8 model bundle

Concentrations are in micromolar units and time is in minutes. The energy
models use dimensionless free energies, a concentration reference of
1 micromolar, and a kinetic reference of 1 per minute. Keep `Cref` at 1;
changing it alone does not convert the model's units.

- `two_site_inconsistent.bngl`: intentionally violates passive-binding cycle
  consistency when `boost != 1`; illustrates a stationary circulating flux.
- `two_site_energy.bngl`: cooperative binding using energy patterns.
- `two_site_rates.bngl`: the same system using explicit context-dependent rates.
- `raf_inhibitor_energy.bngl`: illustrative reciprocal coupling between RAF
  dimerization and inhibitor binding. It is not fitted to cellular data.
  `KD_dim` is the intrinsic scale; the inhibitor-free macroscopic dimer
  dissociation constant is `2*KD_dim` because of identical-reactant symmetry.

The chapter and notebook generate the figures from these files. Models were
checked with BioNetGen 2.9.3. Run scientific checks with the book environment:

```sh
python tests/test_ch08_energy.py
python tests/test_models.py
```

## Sources

The thermodynamics discussion cites Garcia et al. (J. Gen. Physiol. 155,
e202213263, 2023). The RAF model is an illustrative assembly model motivated
by Poulikakos et al. (Nature 464, 427, 2010) and is not fitted to data.
