"""Check that every BNGL model in models/ generates a network and simulates.

Run with:  python tests/test_models.py
"""
import sys
from pathlib import Path

import bngsim

ROOT = Path(__file__).resolve().parents[1]
failures = 0
for path in sorted((ROOT / "models").rglob("*.bngl")):
    try:
        model = bngsim.Model.from_bngl(path)
        sim = bngsim.Simulator(model, method="ode")
        model.reset()
        result = sim.run(t_span=(0, 10), n_points=11)
        assert result.observables is not None
        print(f"ok    {path.relative_to(ROOT)}  ({model.n_species} species, {model.n_reactions} reactions)")
    except Exception as exc:          # report every failure, then exit nonzero
        failures += 1
        print(f"FAIL  {path.relative_to(ROOT)}: {exc}")
sys.exit(1 if failures else 0)
