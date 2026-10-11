"""Check that the book's models show the behavior the text claims.

test_models.py checks only that every model runs. The checks here compare
simulations with results derived in the text, so that a change to a model or
to the simulator that alters a lesson is caught.

Run with:  python tests/test_science.py
"""
import os
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import bngsim

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bookutils import model_path, generated_network   # noqa: E402


def load(chapter, name, replace=None):
    """Load a model, optionally after replacing text in its file."""
    if replace is None:
        return bngsim.Model.from_bngl(model_path(chapter, name))
    src = model_path(chapter, name).read_text()
    for old, new in replace.items():
        assert old in src, f"{old!r} not in {name}"
        src = src.replace(old, new)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, f"{name}.bngl")
        open(path, "w").write(src)
        return bngsim.Model.from_bngl(path, cache=False)


def ode(model, t_end, n=201):
    model.reset()
    return bngsim.Simulator(model, method="ode").run(t_span=(0, t_end), n_points=n)


def test_binding_equilibrium():
    """Ch 1: [LR] approaches the root of the quadratic, and totals are conserved."""
    m = load("ch01", "stat_step1_binding")
    L0, R0 = m.get_param("L0"), m.get_param("R0")
    KD = m.get_param("koff") / m.get_param("kon")
    r = ode(m, 200)
    b = L0 + R0 + KD
    assert np.isclose(r.observables["LR"][-1], (b - np.sqrt(b * b - 4 * L0 * R0)) / 2, rtol=1e-4)
    for law, total in zip(np.array(m.conservation_laws["coefficients"]), m.conservation_laws["constants"]):
        assert total > 0 and np.all(law >= 0)


def test_rules_reproduce_network():
    """Ch 2: the rule-based rewrite gives the same pSTAT as the Chapter 1 model."""
    a = ode(load("ch01", "stat_step6_feedback"), 120).observables["pSTAT"]
    b = ode(load("ch02", "stat_rbm1_rules"), 120).observables["pSTAT"]
    assert np.allclose(a, b, rtol=1e-4, atol=1e-6)


def test_symmetry_factor():
    """Ch 4: binding of identical molecules generates a reaction with 0.5*kf."""
    _, reactions = generated_network("ch04", "homodimer")
    forward = [rate for lhs, rhs, rate, rule in reactions if rule == "Dimerize"]
    assert forward == ["0.5*kf"], forward


def test_deletion():
    """Ch 4: deleting A removes B; DeleteMolecules and explicit products release D and F."""
    r = ode(load("ch04", "degradation"), 200)
    assert r.observables["Btot"][-1] < 1e-6
    assert np.isclose(r.observables["Dtot"][-1], 1, rtol=1e-6)
    assert np.isclose(r.observables["Ftot"][-1], 1, rtol=1e-6)


def test_mm_is_total_qssa():
    """Ch 4: the MM rate law uses the free substrate from the quadratic, not the classical form."""
    m = load("ch04", "enzyme")
    kcat, Km, S0, E0 = 1.0, m.get_param("Km"), m.get_param("S0"), 0.5
    m.set_param("E0", E0)
    r = ode(m, 5, n=5001)
    sp = 0.0                                  # integrate the total QSSA by RK4
    t = r.time
    def f(sp):
        S = S0 - sp
        b = S - Km - E0
        Sf = 0.5 * (b + np.sqrt(b * b + 4 * Km * S))
        return kcat * E0 * Sf / (Km + Sf)
    for i in range(1, len(t)):
        h = t[i] - t[i - 1]
        k1 = f(sp); k2 = f(sp + h / 2 * k1); k3 = f(sp + h / 2 * k2); k4 = f(sp + h * k3)
        sp += h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    assert np.isclose(r.observables["Sp_MM"][-1], sp, rtol=1e-4)


def test_rings_close_and_open():
    """Ch 4: one ring per even complex size, and every ring can open."""
    m = load("ch04", "aggregation", {"max_agg=>4": "max_agg=>8"})
    rings = [s for s in m.species_names if not re.search(r"[rl][,)]", s)]
    assert len(rings) == 4, rings
    _, reactions = generated_network("ch04", "aggregation")
    opened = {lhs[0] for lhs, rhs, rate, rule in reactions if rule == "_reverse_Close"}
    closed = {rhs[0] for lhs, rhs, rate, rule in reactions if rule == "Close"}
    assert closed and closed == opened


def test_compartment_scaling():
    """Ch 5: one rule, two compartments; each reaches the equilibrium set by its own concentration."""
    m = load("ch05", "two_volumes")
    r = ode(m, 50)
    KD = m.get_param("koff") / m.get_param("kon")
    for V, obs in [(m.get_param("V_CP"), "AB_CP"), (m.get_param("V_NU"), "AB_NU")]:
        nav = V * m.get_param("NA_pL")
        c0 = m.get_param("N0") / nav               # initial A and B (uM)
        b = 2 * c0 + KD
        expected = (b - np.sqrt(b * b - 4 * c0 * c0)) / 2 * nav
        assert np.isclose(r.observables[obs][-1], expected, rtol=1e-4), obs


def test_bistable_folds():
    """Ch 7: the autoloop model is bistable between kact = 0.125 and 0.5."""
    m = load("ch07", "stat_autoloop")
    sim = bngsim.Simulator(m, method="ode")
    for kact, low_stays_low in [(0.3, True), (0.6, False)]:
        m.set_param("kact", kact)
        m.reset()
        S = sim.run(t_span=(0, 5000), n_points=3).observables["STAT"][-1]
        assert (S < 2) == low_stays_low, (kact, S)
    m.set_param("kact", 0.3)                       # the upper state also persists
    m.reset()
    m.set_state(np.array([1.0, 9.0]))
    assert sim.run(t_span=(0, 5000), n_points=3).observables["STAT"][-1] > 2


if __name__ == "__main__":
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok    {name}")
            except Exception as exc:
                failures += 1
                print(f"FAIL  {name}: {exc!r}")
    sys.exit(1 if failures else 0)
