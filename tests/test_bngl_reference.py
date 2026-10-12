"""Semantic regression checks for the BNGL language reference.

Run with the book environment: python tests/test_bngl_reference.py
"""
from pathlib import Path
import re
import sys
import tempfile
import unittest
import warnings

import bngsim
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bngl_reference import native_model


def load(name):
    return bngsim.Model.from_bngl(ROOT / "models" / "appendix_b" / f"{name}.bngl")


class BNGLReference(unittest.TestCase):
    def test_pattern_counts_and_symmetry(self):
        source = (ROOT / "models/appendix_b/syntax_demo.bngl").read_text()
        extra = """  Molecules Free R(l)
  Molecules Any R(l!?)
  Molecules UnboundP R(l,Y~p)
  Molecules Embeddings R(d!1).R(d!1)
  Species Dimers R(d!1).R(d!1)
  Molecules Once {MatchOnce}R()
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "patterns.bngl"
            path.write_text(source.replace("end observables", extra+"end observables"))
            model = bngsim.Model.from_bngl(path)
            result = bngsim.Simulator(model, "ode").run(t_span=(0, 0.01), n_points=2)
        expected = dict(Rtotal=6, Rcomplexes=5, Rphos=2, Rbound=1,
                        Roverlap=3, Rpair=1, Free=5, Any=6, UnboundP=1,
                        Embeddings=2, Dimers=1, Once=5)
        for name, value in expected.items():
            self.assertEqual(result.observables[name][0], value, name)

    def test_local_function_scope(self):
        # Whole-complex scope gives both receptors rate 2; molecule scope
        # gives the bound receptor rate 2 and the free receptor rate 1.
        t = 0.5
        for name, expected in [("local_complex", 2*(1-np.exp(-2*t))),
                               ("local_molecule", 2-np.exp(-2*t)-np.exp(-t))]:
            model = load(name)
            result = bngsim.Simulator(model, "ode").run(t_span=(0,t), n_points=2)
            self.assertAlmostEqual(result.observables["Rp"][-1], expected, places=6)

    def test_native_deletion_products(self):
        result = native_model("deletion")
        data = result["data"]["deletion.gdat"]
        time = data["time"]
        np.testing.assert_allclose(data["Rtotal"], np.exp(-2*time), atol=2e-7)
        np.testing.assert_allclose(data["Ltotal"], (1+np.exp(-2*time))/2, atol=2e-7)
        np.testing.assert_allclose(data["Lfree"], (1-np.exp(-2*time))/2, atol=2e-7)

    def test_total_rate_backend_difference_and_source_alternative(self):
        result = native_model("functional_rates")
        ode = result["data"]["functional_rates.gdat"]
        for name, value in [("Btotal",4.5), ("Ctotal",4.5), ("Dtotal",1.5)]:
            self.assertAlmostEqual(ode[name][-1], value, places=6)
        xml = result["texts"]["functional_rates_nf.xml"]
        self.assertIn('totalrate="1"', xml)
        nf = result["data"]["functional_rates_nf.gdat"]
        duration = nf["time"][-1]
        # Broad statistical bounds distinguish per-molecule and total fluxes.
        self.assertLess(abs(nf["Btotal"][-1]/duration-4.5), 0.4)
        self.assertLess(abs(nf["Ctotal"][-1]/duration-1.5), 0.25)
        self.assertLess(abs(nf["Dtotal"][-1]/duration-1.5), 0.25)

    def test_native_actions_and_exports(self):
        result = native_model("actions")
        data, texts = result["data"], result["texts"]
        np.testing.assert_allclose(data["actions_sample.gdat"]["time"], [0,0.25,1])
        self.assertEqual(data["actions_ode.gdat"]["time"][-1], 2)
        self.assertEqual(data["actions_nf.gdat"]["time"][-1], 1)
        for name in ["actions_network.net", "actions_xml.xml", "actions_sbml.xml",
                     "actions_model.bngl", "actions_mfile.m"]:
            self.assertIn(name, texts)
        self.assertTrue(any(name.endswith(('.gml', '.graphml')) for name in texts))
        scan = np.loadtxt(texts["actions_scan.scan"].splitlines(), comments="#", ndmin=2)
        np.testing.assert_allclose(scan[:,0], [0.1,0.2,0.3])

    def test_expressions_filters_and_legacy_rate_laws(self):
        source = (ROOT / "models/appendix_b/syntax_demo.bngl").read_text()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expressions.bngl"
            expr = ("kp*if(time()<1 && Rphos>=0,1,0)+0*("
                    "_pi()+_e()+min(1,2)+max(1,2)+sum(1,2)+avg(1,2)+rint(1.5)+"
                    "log2(2)+log10(10)+ln(1)+exp(0)+sqrt(4)+abs(-1)+"
                    "sin(0)+cos(0)+tan(0)+asin(0)+acos(1)+atan(0)+"
                    "sinh(0)+cosh(0)+tanh(0)+asinh(0)+acosh(1)+atanh(0))")
            path.write_text(source.replace("kp/(1+Rphos/K)", expr))
            model = bngsim.Model.from_bngl(path)
            bngsim.Simulator(model, "ode").run(t_span=(0,.01), n_points=2)
            for modifier in ["include_reactants", "exclude_reactants",
                             "include_products", "exclude_products"]:
                path = Path(directory) / f"{modifier}.bngl"
                path.write_text(source.replace("phos_rate()\n", f"phos_rate() {modifier}(1,R(l!+))\n"))
                model = bngsim.Model.from_bngl(path)
                bngsim.Simulator(model, "ode").run(t_span=(0,.01), n_points=2)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            model = load("specialized_rates")
        result = bngsim.Simulator(model, "ode").run(t_span=(0,1e-5), n_points=2)
        sfree = (3-1-1+np.sqrt((3-1-1)**2+4*1*3))/2
        expected = dict(Ptotal=2*3/(1+3), Qtotal=2*3**2/(1+3**2),
                        Ttotal=0.5*sfree/(1+sfree))
        for name, value in expected.items():
            self.assertAlmostEqual(result.observables[name][-1]/1e-5, value, places=4)

    def test_incomplete_seeds_are_rejected(self):
        source = (ROOT / "models/appendix_b/syntax_demo.bngl").read_text()
        seed = "R(l,d,Y~u)                              R0"
        with tempfile.TemporaryDirectory() as directory:
            for pattern, error in [("R()", "missing from molecule"),
                                   ("R(l,d,Y)", "must be set"),
                                   ("R(l!+,d,Y~u)", "illegal bond wildcard")]:
                path = Path(directory) / "invalid_seed.bngl"
                path.write_text(source.replace(seed, pattern+" R0"))
                with self.assertRaisesRegex(bngsim.ModelError, error):
                    bngsim.Model.from_bngl(path)


if __name__ == "__main__":
    unittest.main()
