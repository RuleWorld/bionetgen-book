"""Scientific checks for Chapter 8; run directly with the book's Python."""
from pathlib import Path
import unittest

import bngsim
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return bngsim.Model.from_bngl(ROOT / "models" / "ch08" / f"{name}.bngl")


def simulate(model, **params):
    for name, value in params.items():
        model.set_param(name, value)
    model.reset()
    return bngsim.Simulator(model, "ode").run(t_span=(0, 3000), n_points=301)


class EnergyModels(unittest.TestCase):
    def test_energy_and_explicit_rates_in_multiple_contexts(self):
        energy, explicit = load("two_site_energy"), load("two_site_rates")
        for phi, omega in ((0, 10), (0.5, 0.2), (1, 4)):
            params = dict(phi=phi, omega=omega, KD_A=0.07, KD_B=0.3, L0=2)
            a, b = simulate(energy, **params), simulate(explicit, **params)
            for name in energy.observable_names:
                np.testing.assert_allclose(a.observables[name], b.observables[name],
                                           rtol=2e-6, atol=2e-8)
            o = a.observables
            np.testing.assert_allclose(o["Rtotal"], energy.get_param("R0"), atol=1e-8)
            np.testing.assert_allclose(o["Ltotal"], params["L0"], atol=1e-8)
            ell = o["Lfree"][-1]
            xa, xb = ell/params["KD_A"], ell/params["KD_B"]
            weights = np.array([1, xa, xb, omega*xa*xb])
            actual = np.array([o[n][-1] for n in ("R00", "R10", "R01", "R11")])
            np.testing.assert_allclose(actual/energy.get_param("R0"),
                                       weights/weights.sum(), atol=2e-7)

    def test_stationary_circulation_and_repaired_cycle(self):
        model = load("two_site_inconsistent")
        for boost in (10, 1):
            o = simulate(model, boost=boost).observables
            kon, koff = model.get_param("kon"), model.get_param("koff")
            ell = o["Lfree"][-1]
            r00, r10, r01, r11 = (o[n][-1] for n in ("R00", "R10", "R01", "R11"))
            j = np.array([kon*ell*r00-koff*r10,
                          boost*kon*ell*r10-koff*r11,
                          koff*r11-kon*ell*r01,
                          koff*r01-kon*ell*r00])
            np.testing.assert_allclose(j, j[0], atol=1e-8)
            if boost == 10:
                self.assertGreater(j[0], 0.01)
            else:
                np.testing.assert_allclose(j, 0, atol=1e-8)

    def test_raf_symmetry_and_reciprocal_coupling(self):
        model = load("raf_inhibitor_energy")
        for total in (0.03, 0.1, 0.3):
            o = simulate(model, RAF0=total, I0=0).observables
            monomer = total-o["DimerRAF"][-1]
            macro_kd = monomer**2/o["D00"][-1]
            self.assertAlmostEqual(macro_kd, 2*model.get_param("KD_dim"), places=6)
        o = simulate(model, RAF0=0.1, I0=0.03, omega=100).observables
        ell = o["Ifree"][-1]
        x = ell/model.get_param("KD_drug")*model.get_param("omega")
        self.assertAlmostEqual(o["D10"][-1]/o["D00"][-1], 2*x, places=5)
        self.assertAlmostEqual(o["D11"][-1]/o["D10"][-1], x/2, places=5)
        np.testing.assert_allclose(o["RAFtotal"], 0.1, atol=1e-8)
        np.testing.assert_allclose(o["Itotal"], 0.03, atol=1e-8)
        np.testing.assert_allclose(o["Active"], 2*o["D00"]+o["D10"], atol=1e-8)


if __name__ == "__main__":
    unittest.main()
